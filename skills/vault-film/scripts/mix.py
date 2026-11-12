#!/usr/bin/env python3
"""One sound mix for the whole film, whatever engines drew it -> audio/mix.wav (48 kHz stereo).

usage: python3 ~/.claude/skills/vault-film/scripts/mix.py --project <film dir>
         [--music audio/music/<track or score.wav>] [--ambience audio/sfx/<room tone or foley loop>]
         [--events audio/events.json] [--music-in SEC] [--music-level 0.25] [--duck 0.35] [--ambience-level 0.5]
         [--music-under DB] [--after-dry fade|none] [--music-end backtime|fade] [--stems]

No engine mixes audio: every chapter is rendered silent and this is the only place sound is put together, so
music and ambience run across chapter and engine changes. Length = timeline.json (the picture), never the voice.
  voice     audio/narration_norm.wav (scripts/voice.py), untouched and always on top
  Layer 1   --ambience looped from frame 0 to the end, 80 ms in, 1 s out (no dead air at 0:00)
  Layer 2   --music ducked to --duck under speech, 0 through the dry turn (>= 1.5 s), then back (--after-dry fade)
            or out for good (none); back-timed so the track's real ending lands on the last frame, or looped and
            faded over the last 2 s when it is too short
            --music-under 18 sets the music gain itself, so the voice sits that many dB over the music under speech
            (use it for a synthesized score, whose level is unknown; it replaces --music-level)
  events    audio/events.json: [{"t": 12.4, "file": "audio/sfx/thunk.wav", "gain_db": -6, "pan": 0}]
            `t` is film seconds; or {"chapter": "c03", "t": 2.1} for chapter-local seconds, or "frame": film frame.
            A canvas chapter's window.EV exported with lemo's events.mjs can be converted to this list.
The final loudness (-14 LUFS, true peak) is set by assemble.py; this file only keeps the sum below clipping.
Needs numpy: re-runs itself with the Kokoro venv's Python when the current one has none.
"""
import argparse, json, os, subprocess, sys
from pathlib import Path

try:
    import numpy as np
except ImportError:
    alt = Path.home() / ".venvs/hyperframes-tts/bin/python"
    if alt.exists() and Path(sys.executable).resolve() != alt.resolve():
        os.execv(str(alt), [str(alt), *sys.argv])
    sys.exit("mix.py needs numpy (pip install numpy, or create ~/.venvs/hyperframes-tts)")

SR = 48000

def probe(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)], capture_output=True, text=True)
    return float(r.stdout.strip())

def decode(f, dur=None, start=0.0, loop=False):
    cmd = ["ffmpeg", "-v", "error"] + (["-stream_loop", "-1"] if loop else []) + (["-ss", f"{start:.3f}"] if start else []) + ["-i", str(f)]
    cmd += (["-t", f"{dur:.3f}"] if dur else []) + ["-f", "f32le", "-ac", "2", "-ar", str(SR), "-"]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode: sys.exit(f"ffmpeg could not read {f}: {r.stderr.decode()[-300:]}")
    return np.frombuffer(r.stdout, dtype=np.float32).reshape(-1, 2).astype(np.float64)

def fit(x, n):
    return x[:n] if len(x) >= n else np.vstack([x, np.zeros((n - len(x), 2))])

def envelope(points, n):
    pts = sorted((max(0.0, t), v) for t, v in points)
    return np.interp(np.arange(n) / SR, [p[0] for p in pts], [p[1] for p in pts])[:, None]

def write(path, x):
    path.parent.mkdir(parents=True, exist_ok=True)
    p = subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_s24le", str(path)],
                       input=x.astype(np.float32).tobytes(), capture_output=True)
    if p.returncode: sys.exit(f"could not write {path}: {p.stderr.decode()[-300:]}")

def db(x):
    r = float(np.sqrt(np.mean(x ** 2))) if len(x) else 0.0
    return f"{20 * np.log10(r):.1f} dB RMS" if r > 0 else "silent"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default="."); ap.add_argument("--music"); ap.add_argument("--ambience"); ap.add_argument("--events")
    ap.add_argument("--music-in", type=float, default=0.0); ap.add_argument("--music-level", type=float, default=0.25)
    ap.add_argument("--duck", type=float, default=0.35); ap.add_argument("--ambience-level", type=float, default=0.5)
    ap.add_argument("--after-dry", choices=["fade", "none"], default="fade"); ap.add_argument("--music-under", type=float)
    ap.add_argument("--music-end", choices=["backtime", "fade"], default="backtime")
    ap.add_argument("--stems", action="store_true"); ap.add_argument("--out", default="audio/mix.wav")
    a = ap.parse_args()
    root = Path(a.project).resolve()
    tl = json.loads((root / "timeline.json").read_text())
    fps, total = tl["fps"], tl["dur"]; n = round(total * SR)
    chap = {c["id"]: c for c in tl["chapters"]}
    vt = root / "audio/voice_timing.json"
    T = json.loads(vt.read_text()) if vt.exists() else {"lines": [], "cues": []}
    dry = next((c for c in T.get("cues", []) if c["type"] == "dry"), None)
    d0, d1 = (dry["t"] - 0.15, max(dry["end"], dry["t"] + 1.5)) if dry else (None, None)
    stems, notes = {}, []

    nv = root / "audio/narration_norm.wav"
    if nv.exists():
        v = decode(nv)
        if len(v) > n + SR // 10: notes.append(f"WARNING: the narration ({len(v) / SR:.2f}s) is longer than the picture ({total:.2f}s): re-run plan.py and timeline.py")
        stems["voice"] = fit(v, n)
    elif T["lines"]:
        sys.exit("audio/voice_timing.json exists but audio/narration_norm.wav is missing: run scripts/voice.py")

    if a.ambience:
        x = fit(decode(root / a.ambience, dur=total, loop=True), n)
        stems["ambience"] = x * a.ambience_level * envelope([(0, 0), (0.08, 1), (total - 1.0, 1), (total, 0)], n)

    if a.music:
        f = root / a.music; mlen = probe(f); span = total - a.music_in
        start, loop = 0.0, False
        if a.music_end == "backtime" and mlen >= span: start = mlen - span
        else: loop = mlen < span
        x = decode(f, dur=span, start=start, loop=loop)
        x = fit(np.vstack([np.zeros((round(a.music_in * SR), 2)), x]), n)
        regions = []
        for l in T["lines"]:
            if regions and l["start"] - regions[-1][1] < 1.2: regions[-1][1] = l["end"]
            else: regions.append([l["start"], l["end"]])
        def level(t):
            if dry and (d0 <= t < d1 or (a.after_dry == "none" and t >= d0)): return 0.0
            return a.duck if any(s <= t < e for s, e in regions) else 1.0
        marks = sorted({m for r in regions for m in r} | ({d0, d1} if dry else set()))
        pts = [(0, level(0))]
        for m in marks:
            before, after = level(m - 1e-3), level(m + 1e-3)
            if before == after: continue
            if after < before: pts += [(m - (0.12 if after == 0 else 0.25), before), (m, after)]
            else: pts += [(m, before), (m + (0.8 if before == 0 else 0.5), after)]
        pts.append((total, level(total - 1e-3)))
        env = envelope(pts, n)
        if loop or a.music_end == "fade": env = env * envelope([(0, 1), (total - 2.0, 1), (total, 0)], n)
        gain = a.music_level
        if a.music_under is not None and "voice" in stems and T["lines"]:
            sp = np.zeros(n, bool)
            for l in T["lines"]: sp[round(l["start"] * SR):round(l["end"] * SR)] = True
            vr, mr = np.sqrt(np.mean(stems["voice"][sp] ** 2)), np.sqrt(np.mean((x * env)[sp] ** 2))
            if mr > 0:
                gain = float(vr / mr / 10 ** (a.music_under / 20))
                notes.append(f"--music-under {a.music_under:g}: music gain set to {gain:.2f}")
        stems["music"] = x * gain * env
        notes.append(f"music {f.name}: {mlen:.1f}s, " + (f"back-timed from {start:.2f}s so it ends on the last frame" if start else
                     ("looped, faded over the last 2 s" if loop else "starts at its top")) + f"; {len(regions)} speech regions ducked to {a.duck}")
        if dry: notes.append(f"dry turn: music out {d0:.2f}-{d1:.2f}s" + (", then back" if a.after_dry == "fade" else ", and stays out"))

    ev = Path(root / a.events) if a.events else root / "audio/events.json"
    first = None
    if ev.exists():
        sfx = np.zeros((n, 2)); cache = {}; k = 0
        for e in json.loads(ev.read_text()):
            if "frame" in e: t = e["frame"] / fps
            elif "chapter" in e:
                if e["chapter"] not in chap: sys.exit(f"{ev.name}: chapter {e['chapter']} is not in timeline.json")
                t = chap[e["chapter"]]["start_f"] / fps + e["t"]
            else: t = e["t"]
            if not 0 <= t < total: notes.append(f"WARNING: event at {t:.2f}s ({e['file']}) is outside the film"); continue
            if e["file"] not in cache: cache[e["file"]] = decode(root / e["file"])
            s = cache[e["file"]] * 10 ** (e.get("gain_db", 0) / 20)
            pan = max(-1.0, min(1.0, e.get("pan", 0)))
            s = s * np.array([min(1.0, 1 - pan), min(1.0, 1 + pan)])
            i = round(t * SR); s = s[:n - i]; sfx[i:i + len(s)] += s; k += 1
            first = t if first is None else min(first, t)
        stems["sfx"] = sfx; notes.append(f"{k} sound events from {ev.name}")

    if not stems: sys.exit("nothing to mix: no narration, --music, --ambience or audio/events.json")
    mix = sum(stems.values()); peak = float(np.abs(mix).max())
    if peak > 0.89: mix *= 0.89 / peak; notes.append(f"sum peaked at {20 * np.log10(peak):.1f} dBFS: scaled to -1 dBFS (lower a layer if the voice now sits too low)")
    out = root / a.out; write(out, mix)
    if a.stems:
        for k, x in stems.items(): write(root / "audio/stems" / f"{k}.wav", x)
    print(f"wrote {out} · {total:.2f}s · " + " · ".join(f"{k} {db(x)}" for k, x in stems.items()))
    if "voice" in stems and "music" in stems:
        sp = np.zeros(n, bool)
        for l in T["lines"]: sp[round(l["start"] * SR):round(l["end"] * SR)] = True
        if sp.any():
            vr, mr = np.sqrt(np.mean(stems["voice"][sp] ** 2)), np.sqrt(np.mean(stems["music"][sp] ** 2))
            if mr > 0: notes.append(f"under speech the voice sits {20 * np.log10(vr / mr):.1f} dB over the music (explainers: 18-20; story Shorts: down to 6)")
    if "ambience" not in stems and (first is None or first > 0.5) and float(np.abs(mix[:SR // 2]).max()) < 0.003:
        notes.append("WARNING: the first 0.5 s is silent: give --ambience or an event at frame 0 (checks.py fails dead air at 0:00)")
    for s in notes: print("  - " + s)

if __name__ == "__main__":
    main()
