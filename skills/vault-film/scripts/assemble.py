#!/usr/bin/env python3
"""Check every chapter render, join them, add the one mix, master -> export/final.mp4 (stdlib + ffmpeg).

usage: python3 ~/.claude/skills/vault-film/scripts/assemble.py --project <film dir> [--mix audio/mix.wav | --silent]
         [--fit] [--dip-frames 8] [--grain N] [--crf 18] [--lufs -14] [--out export/final.mp4] [--check]

The chapter contract (timeline.json): build/out/<chapter id>.mp4, silent, the film's width x height and fps, and
exactly the chapter's frame count. A chapter that differs is refused; --fit trims or holds up to 3 frames instead.
  joins    film.json "join": "cut" (default) or "dip" (fade through black over --dip-frames on each side)
  colour   every chapter is converted to limited-range BT.709 yuv420p and tagged, so engines match on YouTube;
           an untagged canvas render is read as BT.601 full range (JPEG frames), anything else as BT.709
  grain    look.json "grain" (0-20, ffmpeg noise strength) or --grain, added once over the whole film. Grain is
           incompressible: grain 3 turned a 6.5 min film into 720 MB. Use 0 unless the look needs it, and raise --crf with it
  sound    the mix is padded or cut to the picture, then two-pass loudnorm to --lufs with true peak -1.5 dBTP
--check only verifies the chapters and prints the table. The output is written whole or not at all.
"""
import argparse, json, re, subprocess, sys
from pathlib import Path

def run(args, **k): return subprocess.run(args, capture_output=True, text=True, **k)

def probe(f):
    r = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries",
             "stream=width,height,r_frame_rate,pix_fmt,nb_read_packets,color_space,color_range", "-of", "json", str(f)])
    s = json.loads(r.stdout)["streams"][0]
    a, b = s["r_frame_rate"].split("/")
    return {"w": s["width"], "h": s["height"], "fps": int(a) / int(b), "frames": int(s["nb_read_packets"]),
            "pix": s.get("pix_fmt"), "matrix": s.get("color_space", "unknown"), "range": s.get("color_range", "unknown")}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default="."); ap.add_argument("--mix", default="audio/mix.wav"); ap.add_argument("--silent", action="store_true")
    ap.add_argument("--fit", action="store_true"); ap.add_argument("--dip-frames", type=int, default=8); ap.add_argument("--grain", type=int)
    ap.add_argument("--lufs", type=float, default=-14.0); ap.add_argument("--out", default="export/final.mp4"); ap.add_argument("--check", action="store_true"); ap.add_argument("--crf", type=int, default=18)
    a = ap.parse_args()
    root = Path(a.project).resolve()
    tl = json.loads((root / "timeline.json").read_text())
    W, H, FPS = tl["width"], tl["height"], tl["fps"]
    look = json.loads((root / "look.json").read_text()) if (root / "look.json").exists() else {}
    grain = a.grain if a.grain is not None else int(look.get("grain", 0))
    bad, rows, ins, filt = [], [], [], []
    ch = tl["chapters"]
    for i, c in enumerate(ch):
        f = root / "build/out" / f"{c['id']}.mp4"
        if not f.exists(): bad.append(f"{c['id']}: {f} is missing (render the chapter)"); continue
        p = probe(f); d = p["frames"] - c["frames"]; why = []
        if (p["w"], p["h"]) != (W, H): why.append(f"size {p['w']}x{p['h']}, film is {W}x{H}")
        if abs(p["fps"] - FPS) > 0.01: why.append(f"{p['fps']:g} fps, film is {FPS}")
        if d and not (a.fit and abs(d) <= 3): why.append(f"{p['frames']} frames, timeline says {c['frames']}" + (" (--fit fixes up to 3)" if abs(d) <= 3 else ""))
        if why: bad.append(f"{c['id']} ({c['engine']}): " + "; ".join(why))
        rows.append(f"  {c['id']} {c['engine']:<11} {p['frames']:>6} f  {p['pix']}  matrix {p['matrix']}  range {p['range']}" + (f"  fit {d:+d} f" if d else ""))
        tagged = p["matrix"] not in ("unknown", None)
        m = {"smpte170m": "bt601", "bt470bg": "bt601"}.get(p["matrix"], p["matrix"]) if tagged else ("bt601" if c["engine"] == "canvas" else "bt709")
        rng = "full" if (p["range"] in ("pc", "full") or str(p["pix"]).startswith("yuvj") or (not tagged and c["engine"] == "canvas" and p["range"] == "unknown" and str(p["pix"]).startswith("yuvj"))) else "tv"
        v = f"[{len(ins)}:v]fps={FPS},scale={W}:{H}:in_color_matrix={m}:in_range={rng}:out_color_matrix=bt709:out_range=tv,format=yuv420p,setsar=1"
        if d > 0: v += f",trim=end_frame={c['frames']}"
        if d < 0: v += f",tpad=stop_mode=clone:stop={-d}"
        v += ",setpts=PTS-STARTPTS"
        n = a.dip_frames
        if c.get("join") == "dip" and i > 0: v += f",fade=t=in:s=0:n={n}"
        if i + 1 < len(ch) and ch[i + 1].get("join") == "dip": v += f",fade=t=out:s={c['frames'] - n}:n={n}"
        filt.append(v + f"[v{len(ins)}]"); ins.append(str(f))
    print(f"{tl['title']}: {len(ch)} chapters, {tl['total_f']} frames ({tl['dur']:.1f}s) @ {FPS} fps, {W}x{H}")
    print("\n".join(rows))
    if bad:
        print("REFUSED:\n  " + "\n  ".join(bad)); sys.exit(1)
    if a.check: print("chapters match the timeline"); return

    mix = root / a.mix
    if not a.silent and not mix.exists(): sys.exit(f"{mix} is missing: run scripts/mix.py (or pass --silent for a picture-only join)")
    out = root / a.out; out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_name("." + out.stem + ".part.mp4")
    graph = ";".join(filt) + ";" + "".join(f"[v{i}]" for i in range(len(ins))) + f"concat=n={len(ins)}:v=1:a=0" + (f",noise=alls={grain}:allf=t" if grain else "") + "[v]"
    cmd = ["ffmpeg", "-v", "error", "-y"]
    for f in ins: cmd += ["-i", f]
    amap = []
    if not a.silent:
        ln = f"loudnorm=I={a.lufs}:TP=-1.5:LRA=11"
        r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(mix), "-af", f"apad=whole_dur={tl['dur']},atrim=end={tl['dur']},{ln}:print_format=json", "-f", "null", "-"])
        mj = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr)
        if not mj: sys.exit("loudnorm could not measure the mix:\n" + r.stderr[-400:])
        m = json.loads(mj.group(0))
        if float(m["input_i"]) < -60: sys.exit("the mix is silent")
        af = (f"apad=whole_dur={tl['dur']},atrim=end={tl['dur']},{ln}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
              f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,aresample=48000")
        cmd += ["-i", str(mix)]; graph += f";[{len(ins)}:a]{af}[a]"; amap = ["-map", "[a]", "-c:a", "aac", "-b:a", "320k"]
    cmd += ["-filter_complex", graph, "-map", "[v]", *amap, "-c:v", "libx264", "-preset", "medium", "-crf", str(a.crf), "-pix_fmt", "yuv420p",
            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv", "-r", str(FPS),
            "-movflags", "+faststart", str(tmp)]
    r = run(cmd)
    if r.returncode:
        tmp.unlink(missing_ok=True); sys.exit("ffmpeg failed:\n" + r.stderr[-800:])
    got = probe(tmp)["frames"]
    if got != tl["total_f"]:
        tmp.unlink(missing_ok=True); sys.exit(f"joined film has {got} frames, timeline says {tl['total_f']}")
    tmp.replace(out)
    msg = f"wrote {out} · {got} frames"
    if not a.silent:
        r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(out), "-af", "ebur128=peak=true", "-f", "null", "-"])
        i = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr); p = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r.stderr)
        msg += f" · {i[-1] if i else '?'} LUFS, true peak {p[-1] if p else '?'} dBTP"
    print(msg + (f" · grain {grain}" if grain else ""))

if __name__ == "__main__":
    main()
