#!/usr/bin/env python3
"""Write the 3-layer audio bed for a HyperFrames build from the measured voice (stdlib only).

usage: python3 ~/.claude/skills/video-studio/scripts/audio_bed.py [--project <episode dir>] [--build build]
         [--music audio/music/<track>] [--ambience audio/sfx/<room tone or foley loop>] [--breath audio/sfx/<breath>]
         [--music-in SEC] [--music-level 0.25] [--duck 0.35] [--ambience-level 0.5] [--after-dry fade|none]
         [--music-end backtime|fade] [--track-base 90] [--inject]

Reads audio/voice_timing.json (lines, cues, persona fx_chain) and writes <build>/audio-bed.html:
  - voiceover group: the narration with the persona's data-fx-chain; reverb wet goes to 0 during the dry turn
  - Layer 1 ambience: room tone / foley loop from frame 0 to the end (no dead air at 0:00)
  - Layer 2 music: ducked to --duck under speech, 0 through the dry turn (>= 1.5 s), then back (--after-dry fade)
    or out for good (none); back-timed with data-media-start so the track's real ending lands on the last frame
    (or looped and faded over the last 2 s when it is too short); data-fx-carve set to make room for the voice
  - breath SFX at every *(inhale)* cue when --breath is given
Copies the audio files into <build>/assets/. JSON attributes are double-quoted with &quot; (the carve tool needs it).
--inject replaces the block between <!-- audio-bed:start --> and <!-- audio-bed:end --> in <build>/index.html;
the first time, paste the file's content inside the root composition yourself.
Then: npx hyperframes lint <build>; optional carve: node ~/.claude/skills/media-use/audio/scripts/carve.mjs --comp <build>/index.html
"""
import argparse, html, json, re, shutil, subprocess
from pathlib import Path

START, END = "<!-- audio-bed:start -->", "<!-- audio-bed:end -->"

def attr(obj):
    return html.escape(json.dumps(obj, separators=(",", ":")), quote=True)

def probe(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)], capture_output=True, text=True)
    return float(r.stdout.strip())

def copy_in(src, build, sub):
    src = Path(src).resolve()
    if not src.exists(): raise SystemExit(f"missing file: {src}")
    dst = build / "assets" / sub / src.name
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime: shutil.copy2(src, dst)
    return f"assets/{sub}/{src.name}"

def lane(points):
    """Sort, drop non-increasing times, round."""
    out = []
    for t, v in sorted(points):
        t = round(max(0.0, t), 3)
        if out and t <= out[-1]["t"]:
            out[-1]["v"] = round(v, 4); continue
        out.append({"t": t, "v": round(v, 4)})
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default="."); ap.add_argument("--build", default="build")
    ap.add_argument("--music"); ap.add_argument("--ambience"); ap.add_argument("--breath")
    ap.add_argument("--music-in", type=float, default=0.0); ap.add_argument("--music-level", type=float, default=0.25)
    ap.add_argument("--duck", type=float, default=0.35); ap.add_argument("--ambience-level", type=float, default=0.5)
    ap.add_argument("--after-dry", choices=["fade", "none"], default="fade")
    ap.add_argument("--music-end", choices=["backtime", "fade"], default="backtime")
    ap.add_argument("--track-base", type=int, default=90); ap.add_argument("--inject", action="store_true")
    a = ap.parse_args()
    root = Path(a.project).resolve(); build = (root / a.build).resolve()
    T = json.loads((root / "audio/voice_timing.json").read_text())
    total = T["total"]; cues = T.get("cues", [])
    dry = next((c for c in cues if c["type"] == "dry"), None)
    d0, d1 = (dry["t"] - 0.15, max(dry["end"], dry["t"] + 1.5)) if dry else (None, None)
    track = a.track_base
    els, groups, notes = [], [], []

    # voiceover group: persona processing, reverb off through the dry turn
    chain = T.get("fx_chain") or []
    vo_attrs = f' data-fx-chain="{attr({"version": 1, "nodes": chain})}"' if chain else ""
    rev = next((nd for nd in chain if nd.get("type") == "reverb"), None)
    if rev and dry:
        wet = rev.get("params", {}).get("wet", 0.35)
        vo_attrs += f' data-automation="{attr({"version": 1, "lanes": [{"target": f"fx.{rev["id"]}.wet", "points": lane([(0, wet), (d0 - 0.05, wet), (d0, 0), (dry["end"], 0), (dry["end"] + 0.3, wet)])}]})}"'
    groups.append(f'<hf-audio-group id="voiceover" data-label="Voiceover" data-volume="1"{vo_attrs}></hf-audio-group>')
    nsrc = copy_in(root / "audio/narration_norm.wav", build, "audio")
    els.append(f'<audio id="narration" class="clip" data-audio-group="voiceover" src="{nsrc}" data-start="0" data-duration="{total}" data-track-index="{track}" data-volume="1"></audio>')
    track += 1

    # Layer 1: ambience from frame 0
    if a.ambience:
        src = copy_in(root / a.ambience, build, "sfx")
        fade = {"version": 1, "lanes": [{"target": "volume", "points": lane([(0, 0), (0.08, 1), (total - 1.0, 1), (total, 0)])}]}
        groups.append('<hf-audio-group id="ambience" data-label="Ambience" data-volume="1"></hf-audio-group>')
        els.append(f'<audio id="ambience-bed" class="clip" data-audio-group="ambience" src="{src}" data-start="0" data-duration="{total}" data-track-index="{track}" data-volume="{a.ambience_level}" loop data-automation="{attr(fade)}"></audio>')
        track += 1
    else:
        notes.append("no --ambience: Layer 1 is empty, so 0:00 is silent unless foley starts there (checks.py will warn)")

    # Layer 2: music, ducked under speech, out for the dry turn, ending on the last frame
    if a.music:
        src = copy_in(root / a.music, build, "music")
        mlen = probe(root / a.music); span = total - a.music_in
        media_start, loop = 0.0, False
        if a.music_end == "backtime" and mlen >= span:
            media_start = round(mlen - span, 3)
        else:
            loop = mlen < span
        regions = []
        for l in T["lines"]:
            if regions and l["start"] - regions[-1][1] < 1.2: regions[-1][1] = l["end"]
            else: regions.append([l["start"], l["end"]])
        def level(t):
            if dry and (d0 <= t < d1 or (a.after_dry == "none" and t >= d0)): return 0.0
            return a.duck if any(s <= t < e for s, e in regions) else 1.0
        marks = sorted({x for r in regions for x in r} | ({d0, d1} if dry else set()))
        pts = [(0, level(0))]
        for m in marks:
            before, after = level(m - 1e-3), level(m + 1e-3)
            if before == after: continue
            if after < before: pts += [(m - (0.12 if after == 0 else 0.25), before), (m, after)]
            else: pts += [(m, before), (m + (0.8 if before == 0 else 0.5), after)]
        if loop or a.music_end == "fade":
            pts += [(total - 2.0, level(total - 2.0)), (total, 0)]
        groups.append(f'<hf-audio-group id="music" data-label="Music" data-volume="1" data-automation="{attr({"version": 1, "lanes": [{"target": "volume", "points": lane(pts)}]})}"></hf-audio-group>')
        carve = {"enabled": True, "sources": ["voiceover"], "strength": 0.25}
        els.append(f'<audio id="music-bed" class="clip" data-timeline-role="music" data-audio-group="music" src="{src}" data-start="{a.music_in}" data-duration="{round(span, 3)}"'
                   + (f' data-media-start="{media_start}"' if media_start else "") + (" loop" if loop else "")
                   + f' data-track-index="{track}" data-volume="{a.music_level}" data-fx-carve="{attr(carve)}"></audio>')
        track += 1
        notes.append(f"music {Path(a.music).name}: {mlen:.1f}s, " + (f"back-timed from {media_start:.2f}s so it ends on the last frame" if media_start
                     else ("looped, faded over the last 2 s" if loop else "starts at its top")) + f"; {len(regions)} speech regions ducked to {a.duck}")
        if dry: notes.append(f"dry turn: music out {d0:.2f}–{d1:.2f}s" + (", then back" if a.after_dry == "fade" else ", and stays out"))
    else:
        notes.append("no --music: Layer 2 is empty (get a solo-instrument track with media-use, then re-run)")

    # breath foley at inhale cues
    if a.breath:
        src = copy_in(root / a.breath, build, "sfx"); blen = probe(root / a.breath)
        if not any(g.startswith('<hf-audio-group id="sfx"') for g in groups):
            groups.append('<hf-audio-group id="sfx" data-label="SFX" data-volume="1"></hf-audio-group>')
        for k, c in enumerate([c for c in cues if c["type"] == "breath"], 1):
            els.append(f'<audio id="breath-{k}" class="clip" data-audio-group="sfx" src="{src}" data-start="{c["t"]}" data-duration="{round(min(blen, c["dur"] + 0.25), 3)}" data-track-index="{track}" data-volume="0.5"></audio>')

    block = "\n".join([START, f"<!-- generated by video-studio/scripts/audio_bed.py from audio/voice_timing.json ({T.get('persona', '?')}, {total:.2f}s); re-run after re-voicing -->",
                       "<style>hf-audio-group { display: none !important; }</style>", *groups, *els, END])
    (build / "audio-bed.html").write_text(block + "\n")
    idx = build / "index.html"
    if a.inject:
        s = idx.read_text()
        if START not in s or END not in s:
            raise SystemExit(f"--inject: paste {build/'audio-bed.html'} inside the root composition of {idx} once (it carries the markers)")
        idx.write_text(s[:s.index(START)] + block + s[s.index(END) + len(END):])
        notes.append(f"injected into {idx}")
    if idx.exists():
        m = re.search(r'data-composition-id="[^"]+"[^>]*?data-duration="([\d.]+)"', idx.read_text())
        if m and float(m.group(1)) + 1e-3 < total: notes.append(f"WARNING: root data-duration {m.group(1)} is shorter than the narration ({total:.2f}s)")
    print(f"wrote {build/'audio-bed.html'} · {len(els)} audio clips, {len(groups)} groups")
    for n in notes: print("  - " + n)

if __name__ == "__main__":
    main()
