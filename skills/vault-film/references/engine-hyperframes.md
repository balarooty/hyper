# Engine: HyperFrames

For chapters built on the person's stills (sagas, devotional pieces, archival documents): slow camera moves and parallax over images, overlays in the look's fonts. A chapter is its own small HyperFrames project at `build/<id>/`.

`new_film.py chapters` runs `npx hyperframes init` there and writes a starter: a root `index.html` that only mounts scenes, and one scene file per shot in `compositions/s<shot>.html` with its own timeline. Shot times are baked in from `chapter.json`; each still gets a slow push; fonts come from `assets/fonts/`, art from `assets/art/`. The starter passes `hyperframes check` with no errors or warnings.

## Commands

```bash
npx hyperframes check build/<id> --json                 # fix every error; weigh every warning
npx hyperframes snapshot build/<id> --at <t,…>          # stills at chapter-local seconds
npx hyperframes render build/<id> -o build/out/<id>.mp4 --fps 30 --crf 16
npx hyperframes preview build/<id>                      # live preview for the person
```

## Contract (the parts that bite)

1. Every timed element has `class="clip"`, `data-start` and `data-duration` in seconds; the chapter's length is the root's `data-duration`.
2. One paused GSAP timeline, registered after its tweens: `window.__timelines["main"] = tl`.
3. No `Date.now()`, unseeded `Math.random()`, network fetches, timers or `repeat: -1`. That is why the times are baked into the HTML and not read from `chapter.json` at run time.
4. Never tween `display`, `visibility` or `autoAlpha` on a `.clip`; animate a child. No CSS `transform` on an element GSAP transforms.
5. Fonts only through `@font-face` to a file in `assets/fonts/`; asset paths are `assets/...` with no leading `/`.
6. No `<audio>` in a chapter: `mix.py` owns the sound. The check's "no sound" note is expected.

## Keeping the frame count exact

The root's `data-duration` is set a hair under `frames / fps`, because the renderer rounds the length up; `assemble.py --check` confirms the count. After a re-voice, `timeline.py` rewrites `chapter.json` but not your HTML: copy each shot's new `start` and `dur` into its host's `data-start` / `data-duration` in `index.html`, stretch the durations inside that shot's scene to match, set the root (and the last host's end) to `frames / fps − 0.0005`, and re-render.

## Building the chapter

- Each shot is already its own scene file. Times inside a scene are local to it (0 is the shot's start); the host in `index.html` carries the shot's place in the chapter. Give the host, the scene root and the timeline key the same id, and prefix every id inside a scene with it (`s07-title`).
- Add layers to a shot (parallax planes, an overlay, a verse card) as more `.clip` elements inside its scene.
- Parallax: cut a still into 2–3 planes (background, subject, foreground) and move them at different speeds; a single plane gets a slow push or drift. No still sits frozen.
- Overlays (names, dates, maps, verses) are HTML in the look's fonts, never text inside an image. The anchor verse holds still at its cue frame.
- Grades, grain, blur and vignettes on images go through `npx hyperframes media-treatment`, not CSS filters; film-wide grain is added once at assembly instead.
- Frame 0 of the film's first chapter already shows the key image; nothing enters from black.
- A missing still shows a red `PLACEHOLDER` tile; list them for the person and never render past one.

If the `hyperframes`, `hyperframes-cli` and `hyperframes-registry` skills are installed they hold the full format, motion and registry references; this file is enough for a stills chapter without them.
