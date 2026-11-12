#!/usr/bin/env python3
"""Final export checks for a rendered video (stdlib + ffmpeg/ffprobe).

usage: python3 -I ~/.claude/skills/vault-film/scripts/checks.py <video.mp4> [--project <episode dir>]
         [--short] [--warm-ending] [--warm-min 6] [--out <dir>]

  format    H.264 + AAC, 1920x1080 (1080x1920 with --short), fps, duration; with --project the video must not be
            shorter than the narration (audio/voice_timing.json)
  loudness  integrated -16.5..-13.5 LUFS (YouTube plays at about -14), true peak <= -1 dBTP
  frame 0   sound in the first 0.5 s: room tone or foley from frame 0 (Layer 1), never dead air
  loop      --short: SSIM of the first vs the last frame; >= 0.5 means the end returns to the opening composition
  warm end  --warm-ending: Cr-Cb (warmth) of the last second vs the first; the ending must be warmer by --warm-min
  cues      --project: a 5-frame strip (cue-0.2 s ... +0.6 s) at every beat action, dry turn and anchor in
            audio/voice_timing.json, plus a waveform around the dry turn -> <out>/cues/
Prints PASS / WARN / FAIL per check and exits 1 if anything FAILs.
"""
import argparse, json, re, subprocess, sys
from pathlib import Path

def run(args): return subprocess.run(args, capture_output=True, text=True)

def frame_stats(video, first):
    """Mean Cr-Cb over the first (or last) second."""
    src = ["-i", video, "-t", "1"] if first else ["-sseof", "-1", "-i", video]
    r = run(["ffmpeg", "-hide_banner", "-nostats", *src, "-vf", "scale=320:-2,signalstats,metadata=mode=print", "-f", "null", "-"])
    u = [float(x) for x in re.findall(r"signalstats\.UAVG=([\d.]+)", r.stderr)]
    v = [float(x) for x in re.findall(r"signalstats\.VAVG=([\d.]+)", r.stderr)]
    return (sum(v) / len(v) - sum(u) / len(u)) if u and v else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("--project"); ap.add_argument("--short", action="store_true")
    ap.add_argument("--warm-ending", action="store_true"); ap.add_argument("--warm-min", type=float, default=6.0)
    ap.add_argument("--out")
    a = ap.parse_args()
    video = str(Path(a.video).resolve())
    proj = Path(a.project).resolve() if a.project else None
    out = Path(a.out).resolve() if a.out else ((proj / "review/checks") if proj else Path(video).parent / "checks")
    out.mkdir(parents=True, exist_ok=True)
    res = []
    def report(level, name, msg): res.append(level); print(f"{level:4s} {name:10s} {msg}")

    # format
    pj = json.loads(run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,codec_name,width,height,r_frame_rate:format=duration",
                         "-of", "json", video]).stdout or "{}")
    vs = next((s for s in pj.get("streams", []) if s["codec_type"] == "video"), None)
    au = next((s for s in pj.get("streams", []) if s["codec_type"] == "audio"), None)
    dur = float(pj.get("format", {}).get("duration", 0))
    if not vs or not au:
        report("FAIL", "format", f"missing {'video' if not vs else 'audio'} stream"); vs = vs or {}; au = au or {}
    else:
        want = (1080, 1920) if a.short else (1920, 1080)
        size = (vs.get("width"), vs.get("height"))
        bad = [x for x, ok in (("video not H.264", vs.get("codec_name") == "h264"), ("audio not AAC", au.get("codec_name") == "aac"),
                               (f"size {size[0]}x{size[1]}, expected {want[0]}x{want[1]}", size == want)) if not ok]
        msg = f"{vs.get('codec_name')} {size[0]}x{size[1]} {vs.get('r_frame_rate')} · {au.get('codec_name')} · {dur:.2f}s"
        report("WARN" if bad else "PASS", "format", msg + (" — " + "; ".join(bad) if bad else ""))
    if a.short and dur > 60.5: report("WARN", "length", f"{dur:.1f}s — a Short is 60 s or less unless the person asked for longer")
    if proj and (proj / "audio/voice_timing.json").exists():
        total = json.loads((proj / "audio/voice_timing.json").read_text())["total"]
        if dur + 0.1 < total: report("FAIL", "length", f"video {dur:.2f}s is shorter than the narration {total:.2f}s — the ending is cut")
        else: report("PASS", "length", f"video {dur:.2f}s covers the narration {total:.2f}s" + (f" (+{dur - total:.1f}s after)" if dur - total > 0.5 else ""))

    # loudness
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", video, "-vn", "-af", "loudnorm=I=-14:TP=-1:print_format=json", "-f", "null", "-"])
    try:
        lj = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1]); li, tp = float(lj["input_i"]), float(lj["input_tp"])
        lvl = "PASS" if -16.5 <= li <= -13.5 else ("WARN" if -18 <= li <= -12 else "FAIL")
        if tp > -1.0: lvl = "FAIL"
        report(lvl, "loudness", f"{li:.1f} LUFS integrated (target -14 to -16), true peak {tp:.1f} dBTP (max -1)")
    except Exception:
        report("FAIL", "loudness", "could not measure (no audio?)")

    # frame 0: sound present
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-t", "0.5", "-i", video, "-vn", "-af", "astats=metadata=0", "-f", "null", "-"])
    m = re.findall(r"RMS level dB: (-?[\d.]+|-inf)", r.stderr)
    first = float(m[-1]) if m and m[-1] != "-inf" else float("-inf")
    report("PASS" if first > -60 else "WARN", "frame 0", f"first 0.5 s at {first:.1f} dB RMS" +
           ("" if first > -60 else " — dead air; start on room tone or foley (Layer 1, mix.py --ambience)"))

    # loop: first vs last frame
    if a.short:
        f0, f1 = out / "loop_first.png", out / "loop_last.png"
        run(["ffmpeg", "-v", "error", "-y", "-i", video, "-vf", "scale=270:-2", "-frames:v", "1", str(f0)])
        run(["ffmpeg", "-v", "error", "-y", "-sseof", "-0.3", "-i", video, "-vf", "scale=270:-2", "-update", "1", str(f1)])
        r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(f0), "-i", str(f1), "-lavfi", "ssim", "-f", "null", "-"])
        m = re.search(r"All:([\d.]+)", r.stderr)
        def yuv(f):
            st = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(f), "-vf", "signalstats,metadata=mode=print", "-f", "null", "-"]).stderr
            return [float(re.findall(rf"signalstats\.{k}=([\d.]+)", st)[-1]) for k in ("YAVG", "UAVG", "VAVG")]
        if m:
            s = float(m.group(1))
            dc = sum((x - y) ** 2 for x, y in zip(yuv(f0), yuv(f1))) ** 0.5  # same layout can still be a different colour/grade
            ok = s >= 0.5 and dc <= 20
            report("PASS" if ok else "WARN", "loop", f"SSIM {s:.2f}, colour distance {dc:.0f} (first vs last frame)" +
                   ("" if ok else " — the last frame does not return to the opening (match-cut the end to 0:00: same framing, same grade)"))
        else: report("WARN", "loop", "could not compare first and last frames")

    # warm ending
    if a.warm_ending:
        w0, w1 = frame_stats(video, True), frame_stats(video, False)
        if w0 is None or w1 is None: report("WARN", "warm end", "could not measure colour")
        else:
            d = w1 - w0
            report("PASS" if d >= a.warm_min else "WARN", "warm end", f"warmth (Cr-Cb) {w0:+.1f} at the start -> {w1:+.1f} at the end (Δ {d:+.1f}, need ≥ {a.warm_min:+.0f})" +
                   ("" if d >= a.warm_min else " — grade the turn and ending warmer than frame 0"))

    # cue strips
    if proj and (proj / "audio/voice_timing.json").exists():
        cues = [c for c in json.loads((proj / "audio/voice_timing.json").read_text()).get("cues", [])
                if (c["type"] == "beat" and c.get("action")) or c["type"] in ("dry", "anchor")]
        cd = out / "cues"; cd.mkdir(exist_ok=True)
        for k, c in enumerate(cues, 1):
            ss = max(0.0, c["t"] - 0.2)
            f = cd / f"{k:02d}_{c['type']}_{c['t']:.2f}s.png"
            run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ss:.3f}", "-t", "1.0", "-i", video, "-vf", "fps=5,scale=-2:360,tile=5x1:padding=4:color=gray",
                 "-frames:v", "1", str(f)])
            label = c.get("action") or c.get("line", "")
            print(f"     cue {k:02d} {c['type']:6s} {c['t']:6.2f}s  {label}  -> {f.relative_to(out.parent) if f.exists() else 'no frame'}")
        dry = next((c for c in cues if c["type"] == "dry"), None)
        if dry:
            ss = max(0.0, dry["t"] - 1.5)
            run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ss:.3f}", "-t", f"{dry['end'] - ss + 1.5:.3f}", "-i", video,
                 "-filter_complex", "showwavespic=s=1600x240:split_channels=0:colors=0x3D6B59", "-frames:v", "1", str(cd / "dry_wave.png")])
            print(f"     dry-turn waveform {ss:.2f}–{dry['end'] + 1.5:.2f}s -> {(cd / 'dry_wave.png').relative_to(out.parent)} (the bed should vanish, voice and foley stay)")
        if cues: print(f"     strips are 5 frames 0.2 s apart starting 0.2 s before each cue: the action lands on frame 2–3")
    sys.exit(1 if "FAIL" in res else 0)

if __name__ == "__main__":
    main()
