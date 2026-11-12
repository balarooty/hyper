#!/usr/bin/env python3
"""Scaffold a vault-film project, then its chapter build folders (stdlib only).

usage:
  python3 ~/.claude/skills/vault-film/scripts/new_film.py init <slug> [--root <videos dir>] [--title "..."]
          [--pack code-explainer|silent-film|character-comedy|saga] [--aspect 16:9|9:16]
  python3 ~/.claude/skills/vault-film/scripts/new_film.py chapters --project <film dir>

init      the project folder: brief.md, sources.md, script.md, shots.json, film.json, look.json, cues.md,
          audio/voice.json, audio/events.json, with the pack's default engine, palette, fonts and persona.
chapters  after plan.py and timeline.py: for every chapter in timeline.json that has no build/<id>/ yet, a starter
          on its engine (it never overwrites a chapter that exists):
            remotion     build/<id> -> <motion>/src/films/<slug>/<id>/ (Chapter.tsx), plus the film's index.tsx
            canvas       build/<id>/index.html + main.js on the Lemo-Opuscar page contract
            hyperframes  build/<id>/index.html + compositions/s<shot>.html, one scene per shot, timings baked in
          Every run also refreshes the look's fonts and the art images in each chapter, re-writes chapter.json
          (timeline.py) and prints each chapter's still and render commands.
The Remotion workspace is $VAULT_FILM_MOTION, else <the folder that holds skills/>/motion (made by setup.sh).
"""
import argparse, html, json, os, shutil, subprocess, sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
TPL = SKILL / "templates"
MOTION = Path(os.environ.get("VAULT_FILM_MOTION") or SKILL.parents[1] / "motion")
LEMO = Path(os.environ.get("LEMO_OPUSCAR_HOME") or Path.home() / "lemo-opuscar")

PACKS = {
    "code-explainer": {
        "engine": "remotion", "persona": "explainer", "format": "explainer",
        "look": {"palette": {"bg": "#0B0F17", "ink": "#E6EDF3", "accent": "#38BDF8", "accent2": "#F59E0B", "alert": "#EF4444", "muted": "#8B98A9"},
                 "fonts": {"display": {"family": "Anton", "weights": [400]}, "body": {"family": "Inter", "weights": [400, 700]},
                           "mono": {"family": "JetBrains Mono", "weights": [400, 700]}},
                 "caption": {"style": "sentence", "size": 46, "position": "lower", "uppercase": False}, "grain": 0}},
    "silent-film": {
        "engine": "canvas", "persona": None, "format": "silent short film",
        "look": {"palette": {"bg": "#1E2126", "ink": "#ECE7DF", "accent": "#E3A857", "accent2": "#6C8EBF", "alert": "#C0392B", "muted": "#7C8088"},
                 "fonts": {"display": {"family": "Cormorant Garamond", "weights": [500, 700]}, "body": {"family": "Inter", "weights": [400, 700]}},
                 "caption": {"style": "none"}, "grain": 4}},
    "character-comedy": {
        "engine": "canvas", "persona": "storybook", "format": "dialogue cartoon",
        "look": {"palette": {"bg": "#FFF4DC", "ink": "#2A1B2E", "accent": "#FF6B4A", "accent2": "#2EC4B6", "alert": "#E63946", "muted": "#9A8C98"},
                 "fonts": {"display": {"family": "Fredoka", "weights": [500, 700]}, "body": {"family": "Inter", "weights": [400, 700]}},
                 "caption": {"style": "sentence", "size": 46, "position": "lower", "uppercase": False}, "grain": 0}},
    "saga": {
        "engine": "hyperframes", "persona": "chronicler", "format": "long-form saga",
        "look": {"palette": {"bg": "#0F0C0A", "ink": "#F1E6D0", "accent": "#D4AF37", "accent2": "#8C2F1B", "alert": "#B03A2E", "muted": "#8A7F70"},
                 "fonts": {"display": {"family": "Cormorant Garamond", "weights": [500, 700]}, "body": {"family": "Inter", "weights": [400, 700]}},
                 "caption": {"style": "none"}, "grain": 6}},
}

def slug(f): return f.lower().replace(" ", "-")

def font_files(look):
    """[(source in @fontsource, published name)] for every family/weight the look names."""
    out = []
    for role in look.get("fonts", {}).values():
        s = slug(role["family"])
        for w in role["weights"]:
            out.append((MOTION / "node_modules/@fontsource" / s / "files" / f"{s}-latin-{w}-normal.woff2", f"{s}-{w}.woff2"))
    return out

def sync_fonts(look, dst):
    dst.mkdir(parents=True, exist_ok=True); missing = []
    for src, name in font_files(look):
        if src.exists(): shutil.copy2(src, dst / name)
        elif not (dst / name).exists(): missing.append(f"{name} (npm i @fontsource/{src.parents[1].name} in {MOTION}, or put the .woff2 in {dst})")
    return missing

def sync_art(root, shots, dst):
    n = 0
    for s in shots:
        if not s.get("art"): continue
        for ext in (".png", ".jpg", ".webp"):
            src = root / "art" / f"{s['id']}{ext}"
            if src.exists():
                dst.mkdir(parents=True, exist_ok=True)
                t = dst / src.name
                if not t.exists() or t.stat().st_mtime < src.stat().st_mtime: shutil.copy2(src, t)
                n += 1; break
    return n

def init(a):
    pack = PACKS[a.pack]
    root = Path(a.root).resolve() / a.slug
    if root.exists() and any(root.iterdir()): sys.exit(f"{root} already exists and is not empty")
    for d in ("art", "audio/voice", "audio/music", "audio/sfx", "audio/audition", "build/out", "build/public", "review", "export"):
        (root / d).mkdir(parents=True, exist_ok=True)
    title = a.title or a.slug.replace("-", " ").title()
    brief = (TPL / "brief.md").read_text().replace("<Title>", title).replace("<slug>", a.slug)
    (root / "brief.md").write_text(brief)
    (root / "sources.md").write_text(f"# Sources — {title}\n\n## Facts\n\n| Claim (as scripted) | Source | Quoted wording | Status (true / disputed / legend) |\n|---|---|---|---|\n\n## Assets\n\n| Asset | Source | Licence |\n|---|---|---|\n")
    if pack["persona"]:
        (root / "script.md").write_text(f"# {title}\n\n## s01 <scene>\ns01_l01: <first line: the hook>\n*(beat)*\ns01_l02: <line>\n")
        (root / "audio/voice.json").write_text(json.dumps({"persona": pack["persona"]}, indent=1) + "\n")
    shots = {"title": title, "aspect": a.aspect,
             "style": "<one shared art style sentence for image prompts. No text, no letters, no numbers, no logos, no watermark.>",
             "eras": {}, "characters": {},
             "shots": [{"id": "01", "lines": "s01_l01", "move": "slow push-in", "overlay": "",
                        "draw": "<what the engine draws in code>  (use \"prompt\" instead for a shot made from a still)"}]
             if pack["persona"] else [{"id": "01", "sec": 4, "move": "macro hold", "draw": "<what the engine draws>"}]}
    (root / "shots.json").write_text(json.dumps(shots, indent=1, ensure_ascii=False) + "\n")
    film = {"title": title, "slug": a.slug, "aspect": a.aspect, "fps": 30, "pack": a.pack,
            "chapters": [{"id": "c01", "title": "<chapter>", "engine": pack["engine"], "shots": "01", "join": "cut"}]}
    (root / "film.json").write_text(json.dumps(film, indent=1, ensure_ascii=False) + "\n")
    (root / "look.json").write_text(json.dumps(pack["look"], indent=1) + "\n")
    (root / "cues.md").write_text(f"# Sound cues — {title}\n\nFilm frames @ 30 fps. Every hit here is also a row in `audio/events.json`.\n\n| frame | sec | chapter | sound | file | level |\n|---|---|---|---|---|---|\n")
    (root / "audio/events.json").write_text("[]\n")
    print(f"created {root}\n  pack {a.pack}: default engine {pack['engine']}, persona {pack['persona'] or 'none (silent)'}, {a.aspect}")
    print("  next: fill brief.md, then the script (lint), the voice, shots.json + film.json, plan.py, timeline.py, new_film.py chapters")

def remotion_entry(tl):
    ids = [c["id"] for c in tl["chapters"] if c["engine"] == "remotion"]
    L = ['// Generated by vault-film new_film.py: one composition per Remotion chapter of this film. Do not hand-edit.',
         'import { Composition, registerRoot } from "remotion";']
    for i in ids:
        L += [f'import {i}Data from "./{i}/chapter.json";', f'import {{ Chapter as {i.upper()} }} from "./{i}/Chapter";']
    L += ["", "const Root = () => (", "  <>"]
    L += [f'    <Composition id="{i}" component={{{i.upper()}}} durationInFrames={{{i}Data.frames}} fps={{{i}Data.fps}} width={{{i}Data.width}} height={{{i}Data.height}} />' for i in ids]
    L += ["  </>", ");", "", "registerRoot(Root);", ""]
    return "\n".join(L)

def hf_page(c):
    """(index.html, {"compositions/s<id>.html": scene}) for a HyperFrames chapter: the root holds only scene hosts,
    each shot is its own scene file with its own timeline (times inside a scene are local to it)."""
    P = {"bg": "#0F0C0A", "ink": "#F1E6D0", "accent": "#D4AF37", "muted": "#8A7F70", **c["look"].get("palette", {})}
    fonts = c["look"].get("fonts", {})
    faces = "\n".join(f"      @font-face {{ font-family: \"{r['family']}\"; src: url(assets/fonts/{slug(r['family'])}-{w}.woff2) format(\"woff2\"); font-weight: {w}; }}"
                      for r in fonts.values() for w in r["weights"])
    disp = fonts.get("display", {}).get("family", "serif"); body = fonts.get("body", {}).get("family", "sans-serif")
    W, H = c["width"], c["height"]; hosts, scenes = [], {}
    # a hair under frames / fps: the renderer rounds the length up, and the chapter must be exactly c["frames"] long
    total = c["frames"] / c["fps"] - 0.0005
    for k, s in enumerate(c["shots"]):
        if k == len(c["shots"]) - 1: s = {**s, "dur": round(total - s["start"], 6)}
        cid, d = f"s{s['id']}", s["dur"]
        art = next((f"{s['id']}{e}" for e in (".png", ".jpg", ".webp") if (ARTDIR / f"{s['id']}{e}").exists()), None) if s.get("art") else None
        if art:
            inner = f'<img id="{cid}-art" class="clip art" data-start="0" data-duration="{d:.6f}" data-track-index="1" src="assets/art/{art}" alt="">'
            tween = f'tl.fromTo("#{cid}-art", {{ scale: 1.05 }}, {{ scale: 1.16, duration: {d:.6f}, ease: "sine.inOut" }}, 0);'
            css = f"#{cid}-art {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}"
        else:
            note = html.escape(s.get("draw") or s.get("overlay") or s.get("words") or "")
            miss = f" · art/{s['id']}.png is missing" if s.get("art") else ""
            inner = (f'<div id="{cid}-stub" class="clip" data-start="0" data-duration="{d:.6f}" data-track-index="1"><p class="tag">PLACEHOLDER · shot {s["id"]} · '
                     f'{s["end_f"] - s["start_f"]} f{miss}</p><p class="note">{note}</p><p class="move">{html.escape(s.get("move", ""))}</p></div>')
            tween = f'tl.fromTo("#{cid}-stub", {{ scale: 1 }}, {{ scale: 1.03, duration: {d:.6f}, ease: "none" }}, 0);'
            css = (f"#{cid}-stub {{ position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 24px; padding: 10%; text-align: center; }}\n"
                   f"    #{cid}-stub .tag {{ color: #e5534b; font-size: 34px; font-weight: 700; }}\n"
                   f"    #{cid}-stub .note {{ font-family: var(--font-display); font-size: 56px; line-height: 1.15; }}\n"
                   f"    #{cid}-stub .move {{ color: var(--muted); font-size: 28px; }}")
        scenes[f"compositions/{cid}.html"] = f"""<!-- shot {s['id']} of chapter {c['id']}: {d:.3f} s. Times here are local to this scene. Add layers (parallax planes, overlays) as more .clip elements. -->
<template>
  <style>
    #root {{ position: absolute; inset: 0; overflow: hidden; background: var(--ground); color: var(--ink); font-family: var(--font-body); }}
    {css}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="{W}" data-height="{H}">
    {inner}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {tween}
    window.__timelines["{cid}"] = tl;
  </script>
</template>
"""
        hosts.append(f'      <div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" data-start="{s["start"]:.6f}" data-duration="{d:.6f}" '
                     f'data-track-index="1" data-track-kind="graphics" data-width="{W}" data-height="{H}"></div>')
    index = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <!-- vault-film HyperFrames chapter {c['id']} of "{html.escape(c['film'])}": {c['frames']} frames @ {c['fps']} fps. One scene file per shot in
         compositions/. Shot times are baked in from chapter.json; after a re-voice, copy each shot's new start/dur into its host's
         data-start / data-duration here (and the durations inside its scene). No <audio>: scripts/mix.py owns the sound. -->
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
{faces}
      :root {{ --ground: {P['bg']}; --ink: {P['ink']}; --accent: {P['accent']}; --muted: {P['muted']}; --font-display: "{disp}", serif; --font-body: "{body}", sans-serif; }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: var(--ground); }}
      #root {{ position: relative; width: {W}px; height: {H}px; background: var(--ground); }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total:.6f}" data-width="{W}" data-height="{H}" data-fps="{c['fps']}">
{chr(10).join(hosts)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""
    return index, scenes

def chapters(a):
    global ARTDIR
    root = Path(a.project).resolve(); ARTDIR = root / "art"
    here = Path(__file__).resolve().parent
    r = subprocess.run([sys.executable, str(here / "timeline.py"), "--project", str(root)], capture_output=True, text=True)
    if r.returncode: sys.exit(r.stdout + r.stderr)
    tl = json.loads((root / "timeline.json").read_text())
    film = json.loads((root / "film.json").read_text())
    look = json.loads((root / "look.json").read_text())
    plan = {s["id"]: s for s in json.loads((root / "art/prompts.json").read_text())["shots"]}
    slg, size = tl["slug"], f"{tl['width']}x{tl['height']}"
    (root / "build/out").mkdir(parents=True, exist_ok=True)
    notes, made = [], []
    fdir = MOTION / "src/films" / slg
    for c in tl["chapters"]:
        d = root / "build" / c["id"]; shots = [plan[i] for i in c["shots"]]
        if c["engine"] == "remotion":
            if not (MOTION / "package.json").exists(): sys.exit(f"no Remotion workspace at {MOTION}: run the skill's setup.sh first")
            src = fdir / c["id"]
            if not src.exists():
                src.mkdir(parents=True); shutil.copy2(TPL / "remotion/chapter/Chapter.tsx", src / "Chapter.tsx"); made.append(c["id"])
            if not d.exists(): d.symlink_to(src, target_is_directory=True)
        elif not d.exists():
            if c["engine"] == "canvas":
                shutil.copytree(TPL / "canvas", d)
            else:
                rr = subprocess.run(["npx", "hyperframes", "init", str(d), "--skip-skills", "--skill=hyperframes"], capture_output=True, text=True, cwd=root)
                if rr.returncode or not d.exists():
                    d.mkdir(parents=True, exist_ok=True); notes.append(f"{c['id']}: `npx hyperframes init` did not run; wrote index.html only")
            made.append(c["id"])
    # chapter.json now that every folder exists, then the engine files that are generated from it
    r = subprocess.run([sys.executable, str(here / "timeline.py"), "--project", str(root)], capture_output=True, text=True)
    if r.returncode: sys.exit(r.stdout + r.stderr)
    if any(c["engine"] == "remotion" for c in tl["chapters"]):
        (fdir / "index.tsx").write_text(remotion_entry(tl))
        notes += [f"missing font: {m}" for m in sync_fonts(look, root / "build/public/fonts")]
    for c in tl["chapters"]:
        d = root / "build" / c["id"]; shots = [plan[i] for i in c["shots"]]
        if c["engine"] == "remotion":
            sync_art(root, shots, root / "build/public/art")
        elif c["engine"] == "canvas":
            notes += [f"{c['id']} missing font: {m}" for m in sync_fonts(look, d / "fonts")]
            sync_art(root, shots, d / "art")
        else:
            notes += [f"{c['id']} missing font: {m}" for m in sync_fonts(look, d / "assets/fonts")]
            sync_art(root, shots, d / "assets/art")
            if c["id"] in made:
                index, scenes = hf_page(json.loads((d / "chapter.json").read_text()))
                (d / "index.html").write_text(index); (d / "compositions").mkdir(exist_ok=True)
                for name, body in scenes.items(): (d / name).write_text(body)
    print(r.stdout.strip())
    print(f"scaffolded: {', '.join(made) if made else 'nothing new (existing chapters are never overwritten)'}")
    q = lambda p: f'"{p}"'
    for c in tl["chapters"]:
        d, out = root / "build" / c["id"], root / "build/out" / f"{c['id']}.mp4"; mid = c["frames"] // 2
        print(f"\n{c['id']} · {c['engine']} · {c['frames']} frames")
        if c["engine"] == "remotion":
            pub = f"--public-dir {q(root / 'build/public')}"
            print(f"  still : cd {q(MOTION)} && npx remotion still src/films/{slg}/index.tsx {c['id']} {q(root / 'review' / (c['id'] + '_f' + str(mid) + '.jpg'))} --frame {mid} {pub}")
            print(f"  render: cd {q(MOTION)} && npx remotion render src/films/{slg}/index.tsx {c['id']} {q(out)} --codec h264 --crf 16 {pub}")
        elif c["engine"] == "canvas":
            print(f"  still : cd {q(LEMO)} && node core/render/still.mjs {q(d)} {c['dur'] / 2:.2f} --size {size} --out {q(root / 'review')} --prefix {c['id']}_t")
            print(f"  render: cd {q(LEMO)} && node core/render/video.mjs {q(d)} --fps {tl['fps']} --size {size} --out {q(out)}")
        else:
            print(f"  check : npx hyperframes check {q(d)} --json")
            print(f"  still : npx hyperframes snapshot {q(d)} --at {c['dur'] / 2:.2f}")
            print(f"  render: npx hyperframes render {q(d)} -o {q(out)} --fps {tl['fps']} --crf 16")
    for n in notes: print("  - " + n)

def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("init"); i.add_argument("slug"); i.add_argument("--root", default="."); i.add_argument("--title")
    i.add_argument("--pack", choices=list(PACKS), default="code-explainer"); i.add_argument("--aspect", choices=["16:9", "9:16"], default="16:9")
    c = sub.add_parser("chapters"); c.add_argument("--project", default=".")
    a = ap.parse_args()
    init(a) if a.cmd == "init" else chapters(a)

if __name__ == "__main__":
    main()
