#!/usr/bin/env python3
"""film.json + art/prompts.json (+ look.json) -> timeline.json and build/<chapter>/chapter.json.

usage: python3 ~/.claude/skills/vault-film/scripts/timeline.py --project <film dir>

Run after plan.py (which times every shot from the measured voice, or from sec/beats for a silent film).
film.json chapters name the shots they hold ("shots": "01-06", or "07" for one shot); together they must cover
every shot once, in order. Each chapter gets:
  - its span in film frames (start_f, end_f) and its own frame count: the engine must render exactly that many
  - its shots, voice lines and delivery cues re-timed to chapter-local frames and seconds
  - the film's size, fps and look.json, so every engine draws from the same numbers
timeline.json is the whole film: the chapters in order with their engine, span and join.
Re-run after any change to the voice, shots.json or film.json; it never touches a chapter's own source files.
"""
import argparse, json
from pathlib import Path

SIZES = {"16:9": (1920, 1080), "9:16": (1080, 1920), "1:1": (1080, 1080)}
ENGINES = ("remotion", "canvas", "hyperframes")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--project", default=".")
    root = Path(ap.parse_args().project).resolve()
    film = json.loads((root / "film.json").read_text())
    pj = root / "art/prompts.json"
    if not pj.exists(): raise SystemExit("art/prompts.json is missing: run scripts/plan.py first")
    plan = json.loads(pj.read_text())
    look = json.loads((root / "look.json").read_text()) if (root / "look.json").exists() else {}
    fps = plan["fps"]
    if film.get("fps", fps) != fps: raise SystemExit(f"film.json fps {film['fps']} != plan fps {fps}")
    aspect = plan.get("aspect", film.get("aspect", "16:9"))
    if aspect not in SIZES: raise SystemExit(f"aspect {aspect}: use one of {', '.join(SIZES)}")
    w, h = SIZES[aspect]
    shots = plan["shots"]; ids = [s["id"] for s in shots]
    vt = root / "audio/voice_timing.json"
    lines = json.loads(vt.read_text())["lines"] if vt.exists() else []
    cues = plan.get("cues", [])

    chapters, nxt = [], 0
    for ch in film["chapters"]:
        if ch.get("engine") not in ENGINES:
            raise SystemExit(f"chapter {ch.get('id')}: engine must be one of {', '.join(ENGINES)}")
        a, _, b = str(ch["shots"]).partition("-"); b = b or a
        for x in (a, b):
            if x not in ids: raise SystemExit(f"chapter {ch['id']}: shot {x} is not in shots.json")
        i, j = ids.index(a), ids.index(b)
        if i != nxt or j < i:
            raise SystemExit(f"chapter {ch['id']}: shots {ch['shots']} must start at shot {ids[nxt]} (chapters cover every shot once, in order)")
        nxt = j + 1
        s0, s1 = shots[i]["start_f"], shots[j]["end_f"]
        loc = lambda f: f - s0
        c = {"film": film.get("title", root.name), "slug": film.get("slug", root.name), "id": ch["id"],
             "title": ch.get("title", ""), "engine": ch["engine"], "join": ch.get("join", "cut"),
             "fps": fps, "width": w, "height": h, "aspect": aspect,
             "start_f": s0, "end_f": s1, "frames": s1 - s0, "dur": round((s1 - s0) / fps, 4), "look": look,
             "shots": [{**{k: s[k] for k in ("id", "file", "move", "overlay", "era", "draw", "words", "lines", "art") if k in s},
                        "start_f": loc(s["start_f"]), "end_f": loc(s["end_f"]),
                        "start": round(loc(s["start_f"]) / fps, 4), "dur": round((s["end_f"] - s["start_f"]) / fps, 4)}
                       for s in shots[i:j + 1]],
             "lines": [{**l, "start": round(l["start"] - s0 / fps, 4), "end": round(l["end"] - s0 / fps, 4),
                        "start_f": round(l["start"] * fps) - s0, "end_f": round(l["end"] * fps) - s0}
                       for l in lines if s0 <= round(l["start"] * fps) < s1],
             "cues": [{**{k: v for k, v in q.items() if k not in ("frame", "t", "end")}, "frame": q["frame"] - s0,
                       "t": round(q["t"] - s0 / fps, 4), **({"end": round(q["end"] - s0 / fps, 4)} if "end" in q else {})}
                      for q in cues if s0 <= q["frame"] < s1]}
        chapters.append(c)
    if nxt != len(ids): raise SystemExit(f"shots from {ids[nxt]} on belong to no chapter in film.json")

    for c in chapters:
        d = root / "build" / c["id"]
        if d.exists():  # scaffolded by new_film.py chapters (a Remotion chapter is a link into the workspace)
            (d / "chapter.json").write_text(json.dumps(c, indent=1, ensure_ascii=False) + "\n")
    tl = {"title": film.get("title", root.name), "slug": film.get("slug", root.name), "fps": fps, "width": w, "height": h,
          "aspect": aspect, "total_f": plan["total_f"], "dur": round(plan["total_f"] / fps, 4),
          "chapters": [{k: c[k] for k in ("id", "title", "engine", "join", "start_f", "end_f", "frames", "dur")} | {"shots": [s["id"] for s in c["shots"]]}
                       for c in chapters]}
    (root / "timeline.json").write_text(json.dumps(tl, indent=1, ensure_ascii=False) + "\n")
    print(f"timeline.json: {len(chapters)} chapters, {tl['total_f']} frames ({tl['dur']:.1f}s) @ {fps} fps, {w}x{h}")
    for c in chapters:
        have = "chapter.json written" if (root / "build" / c["id"]).exists() else "no build folder yet: run new_film.py chapters"
        print(f"  {c['id']} {c['engine']:<11} frames {c['start_f']}-{c['end_f']} ({c['frames']} f, {c['dur']:.1f}s), {len(c['shots'])} shots, {len(c['lines'])} lines · {have}")
    by = {}
    for c in chapters: by[c["engine"]] = by.get(c["engine"], 0) + c["frames"]
    print("  engines: " + ", ".join(f"{e} {f / fps:.0f}s" for e, f in by.items()))

if __name__ == "__main__":
    main()
