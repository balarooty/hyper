#!/usr/bin/env python3
"""Measure a reference video's grammar for a breakdown note (stdlib + ffmpeg/ffprobe).

usage: python3 -I ~/.claude/skills/youtube-inspiration/scripts/ref_metrics.py <video> [--transcript <json>]
         [--out <dir>] [--threshold 0.3]

Prints a markdown block to paste into the note's "Measured grammar" section:
  duration, size, fps · cuts by ffmpeg scene detection (--threshold), shots, average and median shot length,
  cuts per minute, first cut (hook pace) · words, words per minute and speech onset from the word list written by
  `npx hyperframes transcribe <video> --json` (pass that JSON or its transcriptPath) · loudness and sound at 0:00 ·
  warmth (Cr-Cb) of the first and last second.
Writes <out>/shots.png: one frame from the middle of each shot (up to 48), to read the shot grammar at a glance.
"""
import argparse, json, re, statistics, subprocess
from pathlib import Path

def run(a): return subprocess.run(a, capture_output=True, text=True)

def warmth(video, first):
    src = ["-i", video, "-t", "1"] if first else ["-sseof", "-1", "-i", video]
    e = run(["ffmpeg", "-hide_banner", "-nostats", *src, "-vf", "scale=320:-2,signalstats,metadata=mode=print", "-f", "null", "-"]).stderr
    u = [float(x) for x in re.findall(r"signalstats\.UAVG=([\d.]+)", e)]; v = [float(x) for x in re.findall(r"signalstats\.VAVG=([\d.]+)", e)]
    return sum(v) / len(v) - sum(u) / len(u) if u and v else None

def mmss(t): return f"{int(t // 60)}:{t % 60:04.1f}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("--transcript"); ap.add_argument("--out"); ap.add_argument("--threshold", type=float, default=0.3)
    a = ap.parse_args()
    video = str(Path(a.video).resolve())
    out = Path(a.out).resolve() if a.out else Path(video).with_suffix("").parent / (Path(video).stem + "_metrics")
    (out / "frames").mkdir(parents=True, exist_ok=True)

    pj = json.loads(run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate:format=duration", "-of", "json", video]).stdout)
    vs = next(s for s in pj["streams"] if s["codec_type"] == "video")
    has_audio = any(s["codec_type"] == "audio" for s in pj["streams"])
    dur = float(pj["format"]["duration"]); num, den = (int(x) for x in vs["r_frame_rate"].split("/"))

    e = run(["ffmpeg", "-hide_banner", "-nostats", "-i", video, "-an", "-vf", f"scale=320:-2,select='gt(scene,{a.threshold})',showinfo", "-f", "null", "-"]).stderr
    cuts = [float(x) for x in re.findall(r"pts_time:([\d.]+)", e)]
    edges = [0.0] + cuts + [dur]
    lens = [b - a_ for a_, b in zip(edges, edges[1:]) if b - a_ > 0.04]
    rows = [("Duration / format", f"{mmss(dur)} · {vs['width']}×{vs['height']} · {num / den:.3g} fps"),
            ("Shots / cuts", f"{len(lens)} shots · {len(cuts)} cuts · {len(cuts) / (dur / 60):.1f} cuts/min"),
            ("Shot length", f"average {statistics.mean(lens):.1f} s · median {statistics.median(lens):.1f} s · longest {max(lens):.1f} s"
                            + (f" · first cut at {cuts[0]:.1f} s" if cuts else " · no cuts"))]

    if a.transcript:
        tj = json.loads(Path(a.transcript).read_text())
        if isinstance(tj, dict) and tj.get("transcriptPath"): tj = json.loads(Path(tj["transcriptPath"]).read_text())
        words = tj if isinstance(tj, list) else tj.get("words", [])
        if words:
            span = max(words[-1]["end"] - words[0]["start"], 1e-6)
            rows += [("Words / pace", f"{len(words)} words · {len(words) / (span / 60):.0f} WPM over the speech · speech starts at {words[0]['start']:.1f} s"),
                     ("First words", "\"" + " ".join(w["text"] for w in words[:18]).strip() + ("…\"" if len(words) > 18 else "\""))]

    if has_audio:
        e = run(["ffmpeg", "-hide_banner", "-nostats", "-i", video, "-vn", "-af", "loudnorm=print_format=json", "-f", "null", "-"]).stderr
        lj = json.loads(e[e.rindex("{"):e.rindex("}") + 1])
        e = run(["ffmpeg", "-hide_banner", "-nostats", "-t", "0.5", "-i", video, "-vn", "-af", "astats=metadata=0", "-f", "null", "-"]).stderr
        r0 = re.findall(r"RMS level dB: (-?[\d.]+|-inf)", e)
        r0 = float(r0[-1]) if r0 and r0[-1] != "-inf" else float("-inf")
        rows.append(("Loudness", f"{float(lj['input_i']):.1f} LUFS · true peak {float(lj['input_tp']):.1f} dBTP · sound at 0:00: "
                                 + (f"yes ({r0:.0f} dB RMS)" if r0 > -60 else "no (silent first 0.5 s)")))
    w0, w1 = warmth(video, True), warmth(video, False)
    if w0 is not None and w1 is not None:
        rows.append(("Warmth (Cr−Cb)", f"first second {w0:+.1f} → last second {w1:+.1f} ({'warmer' if w1 - w0 >= 6 else 'cooler' if w0 - w1 >= 6 else 'about the same'} ending)"))

    mids = [(a_ + b) / 2 for a_, b in zip(edges, edges[1:]) if b - a_ > 0.04]
    if len(mids) > 48: mids = [mids[round(i * (len(mids) - 1) / 47)] for i in range(48)]
    for f in (out / "frames").glob("*.png"): f.unlink()
    for i, t in enumerate(mids, 1):
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", video, "-frames:v", "1", "-vf", "scale=320:-2", str(out / "frames" / f"shot_{i:02d}.png")])
    cols = min(8 if vs["width"] >= vs["height"] else 10, max(1, len(mids)))
    rws = max(1, -(-len(mids) // cols))
    run(["ffmpeg", "-v", "error", "-y", "-framerate", "1", "-i", str(out / "frames" / "shot_%02d.png"), "-vf",
         f"tile={cols}x{rws}:padding=4:color=gray", "-frames:v", "1", str(out / "shots.png")])

    print("## Measured grammar (ref_metrics.py)\n\n| Measure | Value |\n|---|---|")
    for k, v in rows: print(f"| {k} | {v} |")
    print(f"\nCuts at: {', '.join(f'{c:.1f}' for c in cuts[:40])}{' …' if len(cuts) > 40 else ''}")
    print(f"Shot sheet: {out / 'shots.png'} (one frame from the middle of each shot, in order)")

if __name__ == "__main__":
    main()
