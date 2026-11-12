#!/usr/bin/env python3
"""shots.json + audio/voice_timing.json -> shotlist.md, art/prompts.md, art/prompts.json (frames @30fps).

usage: python3 ~/.claude/skills/video-studio/scripts/plan.py [--project <episode dir>] [--beats <beats.json>]

- A shot with `lines` ("s01_l02" or "s01_l02-s01_l04") starts 3 frames before its first line and runs until the
  next shot starts (the first shot starts at frame 0).
- A shot without `lines` needs `sec` (or `beats`). Before the first voiced shot it fills from frame 0 (the pre-roll
  hook of a Short: the hand on the prop, no voice yet); anywhere else it sits just before the next shot or the end
  (the loop shot of a Short).
- Silent film (no audio/voice_timing.json): every shot needs `sec` or `beats`. With --beats (the JSON printed by
  `npx hyperframes beats <music> --json`) cuts snap to the music's beat grid.
- shots.json "aspect": "16:9" (default) or "9:16" sets the image orientation and the art board.
- Delivery cues from voice.py (beat actions, dry, anchor, breath) are listed in frames in shotlist.md, copied to
  art/prompts.json, and turned into a `npx hyperframes snapshot --at ...` line for the pre-render look check.
"""
import argparse, json, re, statistics
from pathlib import Path

ap = argparse.ArgumentParser(); ap.add_argument("--project", default="."); ap.add_argument("--beats")
A = ap.parse_args()
ROOT = Path(A.project).resolve()
FPS, LEAD = 30, 3
S = json.loads((ROOT / "shots.json").read_text())
VT = ROOT / "audio/voice_timing.json"
T = json.loads(VT.read_text()) if VT.exists() else None
L = {l["id"]: l for l in T["lines"]} if T else {}
ASPECT = S.get("aspect", "16:9")
SHOTS = S["shots"]
GRID = None
if A.beats:
    bj = json.loads(Path(A.beats).read_text())
    GRID = bj if isinstance(bj, list) else (bj.get("beatTimes") or bj.get("beats") or [])
    GRID = sorted(float(x["time"] if isinstance(x, dict) else x) for x in GRID)
    if len(GRID) < 2: raise SystemExit(f"{A.beats}: no beat times found")
    STEP = statistics.median(b - a for a, b in zip(GRID, GRID[1:]))

def beat_t(k):  # time of beat index k, extrapolated past the end of the track
    return GRID[k] if k < len(GRID) else GRID[-1] + (k - len(GRID) + 1) * STEP

def snap(t):
    return min(GRID, key=lambda b: abs(b - t)) if t <= GRID[-1] else GRID[-1] + round((t - GRID[-1]) / STEP) * STEP

def length_f(sh):
    if sh.get("beats"):
        if not GRID: raise SystemExit(f"shot {sh['id']}: `beats` needs --beats <beats.json>")
        return round(sh["beats"] * STEP * FPS)
    if sh.get("sec"): return round(sh["sec"] * FPS)
    raise SystemExit(f"shot {sh['id']}: no `lines`, so it needs `sec` (or `beats`)")

def full_prompt(sh):
    body, chars, cdesc = sh["prompt"], [], []
    m = re.search(r"\s*\(([A-Z_][^)]*)\)\s*$", body)
    if m:
        body = body[:m.start()]
        for part in m.group(1).split(","):
            mm = re.match(r"\s*([A-Z_]+)\s*(.*)", part)
            if mm and mm.group(1) in S.get("characters", {}):
                chars.append(mm.group(1))
                d = S["characters"][mm.group(1)].replace(" (age noted in prompt)", "")
                note = mm.group(2).strip()
                cdesc.append(f"Character: {d}" + (f", shown at {note}" if note else "") + ".")
    style = S["style"]
    if ASPECT == "9:16" and not re.search(r"9:16|vertical|portrait", style, re.I):
        style += " Vertical 9:16 portrait composition, subject in the centre third with margin above and below."
    era = S.get("eras", {}).get(sh.get("era", ""), "")
    return re.sub(r"\s+", " ", f"{style} {era} Scene: {body} {' '.join(cdesc)}").strip(), chars

# ---- timing -------------------------------------------------------------------------------------------
n = len(SHOTS)
start = [None] * n
if T:
    total_f = round(T["total"] * FPS)
    voiced = [i for i, sh in enumerate(SHOTS) if sh.get("lines")]
    if not voiced: raise SystemExit("voice timing exists but no shot has `lines`")
    rng = {}
    for i in voiced:
        a, _, b = SHOTS[i]["lines"].partition("-"); b = b or a
        for x in (a, b):
            if x not in L: raise SystemExit(f"shot {SHOTS[i]['id']}: line {x} is not in audio/voice_timing.json")
        rng[i] = (a, b)
        start[i] = 0 if i == 0 else round(L[a]["start"] * FPS) - LEAD
    first_v = voiced[0]
    for i in range(first_v):  # pre-roll shots pack forward from frame 0
        start[i] = 0 if i == 0 else start[i - 1] + length_f(SHOTS[i - 1])
    for i in range(n - 1, first_v, -1):  # other shots without lines sit just before the next shot / the end
        if start[i] is None:
            nxt = start[i + 1] if i + 1 < n else total_f
            start[i] = nxt - length_f(SHOTS[i])
else:
    if any(sh.get("lines") for sh in SHOTS):
        raise SystemExit("shots have `lines` but audio/voice_timing.json is missing: run free-voiceover voice.py first")
    t = 0.0
    for i, sh in enumerate(SHOTS):
        start[i] = round(t * FPS)
        if sh.get("beats"):
            if not GRID: raise SystemExit(f"shot {sh['id']}: `beats` needs --beats <beats.json>")
            if i == 0: k = 0
            elif t <= GRID[-1]: k = min(range(len(GRID)), key=lambda j: abs(GRID[j] - t))
            else: k = len(GRID) - 1 + round((t - GRID[-1]) / STEP)
            t = beat_t(k + int(sh["beats"]))
        else:
            t = t + length_f(sh) / FPS
            if GRID: t = snap(t)
    total_f = round(t * FPS)
    rng = {}
for i in range(1, n):
    if start[i] <= start[i - 1]:
        raise SystemExit(f"shot {SHOTS[i]['id']} starts at frame {start[i]}, not after shot {SHOTS[i-1]['id']} "
                         f"(frame {start[i-1]}): shorten `sec` or regroup the lines")

out = []
for i, sh in enumerate(SHOTS):
    end_f = start[i + 1] if i + 1 < n else total_f
    if i in rng:
        a, b = rng[i]
        ids = [k for k in L if L[a]["start"] <= L[k]["start"] <= L[b]["start"]]
    else:
        ids = []
    prompt, chars = full_prompt(sh)
    out.append({"id": sh["id"], "file": f"{sh['id']}.png", "start_f": start[i], "end_f": end_f,
                "start": round(start[i] / FPS, 3), "dur": round((end_f - start[i]) / FPS, 3),
                "lines": ids, "words": " ".join(L[k]["text"] for k in ids), "move": sh.get("move", ""),
                "overlay": sh.get("overlay", ""), "era": sh.get("era", ""), "characters": chars, "prompt": prompt})

# ---- delivery cues ------------------------------------------------------------------------------------
def shot_at(f):
    return next((s["id"] for s in out if s["start_f"] <= f < s["end_f"]), out[-1]["id"])

cues, snaps = [], []
for c in (T or {}).get("cues", []):
    f = round(c["t"] * FPS)
    if c["type"] == "beat":
        note = (f"ACTION on this beat: {c['action']}" if c.get("action") else "pause: let the picture hold or move, no busy transition")
        note += f" ({c['dur']:.2f}s, after {c['after']})"
        if c.get("action"): snaps.append(c["t"] + min(0.4, c["dur"] / 2))
    elif c["type"] == "dry":
        out_to = max(c["end"], c["t"] + 1.5)
        note = f"DRY TURN ({c['line']}): music out {c['t']:.2f}–{out_to:.2f}s, narration reverb off, foley stays"
        snaps.append(c["t"] + 0.3)
    elif c["type"] == "anchor":
        note = f"ANCHOR lands ({c['line']}): the verse/moral holds still on screen"
        snaps.append(c["t"] + 0.5)
    elif c["type"] == "breath":
        note = f"breath before {c['line']} ({c['dur']:.2f}s): optional breath foley"
    elif c["type"] == "drop":
        note = f"quiet line ({c['line']}): drop register, keep the picture intimate"
    else:
        note = c["type"]
    cues.append({**c, "frame": f, "shot": shot_at(f), "note": note})

ART = ROOT / "art"; ART.mkdir(exist_ok=True)
(ART / "prompts.json").write_text(json.dumps({"fps": FPS, "total_f": total_f, "aspect": ASPECT, "shots": out,
                                               "cues": cues}, indent=1, ensure_ascii=False))

md = [f"# Shot list — {len(out)} shots · {total_f} frames ({total_f/FPS:.1f}s) @ {FPS} fps · {ASPECT}",
      "", "Generated by `scripts/plan.py` from `shots.json` + measured voice. Do not hand-edit; edit shots.json and re-run.", "",
      "| shot | frames | sec | lines | camera | overlay | art |", "|---|---|---|---|---|---|---|"]
for s in out:
    lines = f"{s['lines'][0]}…{s['lines'][-1]}" if s["lines"] else "— (no voice)"
    md.append(f"| {s['id']} | {s['start_f']}–{s['end_f']} | {s['dur']:.1f} | {lines} | {s['move']} | {s['overlay']} | art/{s['file']} |")
if cues:
    md += ["", "## Delivery cues (from voice.py)", "",
           "Land each action on its beat (0–3 frames early). The dry turn pulls the music and the narration reverb.", "",
           "| frame | sec | shot | cue | note |", "|---|---|---|---|---|"]
    md += [f"| {c['frame']} | {c['t']:.2f} | {c['shot']} | {c['type']} | {c['note']} |" for c in cues]
if snaps:
    md += ["", "Look check at the cues before rendering (run from the episode folder):", "",
           "```bash", f"npx hyperframes snapshot build --at {','.join(f'{t:.2f}' for t in sorted(set(round(x, 2) for x in snaps)))}", "```"]
(ROOT / "shotlist.md").write_text("\n".join(md) + "\n")

orient = ("Portrait 9:16 (1080×1920)" if ASPECT == "9:16" else "Landscape 16:9 (or 3:2)")
pm = [f"# Image prompts for ChatGPT — {S.get('title', ROOT.name)}", "",
      f"{orient}. Generate in ONE ChatGPT conversation so the style and faces stay consistent.",
      "Save each image as `art/<id>.png` (e.g. `art/01.png`), or drop it onto the art board (`python3 ~/.claude/skills/video-studio/scripts/art_server.py --project .`).", ""]
for s in out:
    said = f"\"{s['words'][:90]}{'…' if len(s['words']) > 90 else ''}\"" if s["words"] else "(no narration)"
    pm += [f"## {s['id']} · {s['dur']:.0f}s · {said}", "", "```", s["prompt"], "```", ""]
(ART / "prompts.md").write_text("\n".join(pm))
print(f"{len(out)} shots, {total_f} frames ({ASPECT}); shortest {min(s['dur'] for s in out):.1f}s, "
      f"longest {max(s['dur'] for s in out):.1f}s; {len(cues)} delivery cues")
