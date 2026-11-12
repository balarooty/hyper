# Engine: Remotion

For chapters drawn in code with React: schematic cutaways, kinetic type, charts, maps, terminal overlays, and (optionally) a three.js cartoon world. One shared workspace holds every film: `<hyper>/motion/` (or `$VAULT_FILM_MOTION`), made by `setup.sh`.

```
motion/src/lib/                 shared components (below)
motion/src/films/<slug>/index.tsx        generated: one <Composition id="<chapter id>"> per Remotion chapter
motion/src/films/<slug>/<id>/Chapter.tsx the chapter you write      (the film's build/<id> links here)
motion/src/films/<slug>/<id>/chapter.json timing from timeline.py   (never hand-edit)
<film>/build/public/            fonts/ and art/ for this film, passed with --public-dir
```

## Commands (`new_film.py chapters` prints them with the paths filled in)

```bash
cd <motion> && npx tsc --noEmit
npx remotion still  src/films/<slug>/index.tsx <id> <film>/review/<id>_f<frame>.jpg --frame <f> --public-dir <film>/build/public
npx remotion render src/films/<slug>/index.tsx <id> <film>/build/out/<id>.mp4 --codec h264 --crf 16 --public-dir <film>/build/public
npx remotion studio src/films/<slug>/index.tsx --public-dir <film>/build/public     # live preview for the person
```

`remotion.config.ts` already sets silent output, BT.709, JPEG frames at quality 95 and Chrome for Testing. Add `--frames=a-b` for a quick range; the file for the join is always the whole chapter.

## Rules

- Everything visible is a function of `useCurrentFrame()`: `interpolate`, `spring`, `Easing`. No CSS transitions or animations, no `Math.random()` (use `random(seed)`), no `Date`, no timers.
- Frames that belong to the voice come from `chapter.json`: `chapter.shots[i].start_f`, `chapter.lines`, `cueFrame(chapter, "beat" | "dry" | "anchor")`. A visual reaction lands 0–3 frames before its word.
- No `<Audio>` in a chapter: `mix.py` owns the sound.
- Colours and fonts come from `useColors()` / `useFonts()` (the film's `look.json`), sizes from `useScale()` so 16:9 and 9:16 share code. Text stays inside `useSafe()`.
- No SVG filters (`feTurbulence`, `feDisplacementMap`, blur) on large or moving layers: frame capture drops whole frames and the video blinks. Put wobble and texture in geometry with seeded `random()`, or bake it into an image.
- Assets through `staticFile("art/03.png")` / `staticFile("fonts/…")`; never an absolute path or a URL.
- Every hold creeps (`HoldPush`): a flat hold of 12 frames or more reads as a freeze.
- One file per shot in `<id>/shots/` once a chapter grows; move a component into `src/lib/` only when a second film needs it.

## Components in `src/lib`

| Component | Use |
|---|---|
| `LookProvider`, `useLook`, `useColors`, `useFonts`, `useScale`, `useSafe` | the film's look; wrap the chapter once |
| `Shots`, `ShotStub`, `cueFrame`, `LineCaptions` | one `<Sequence>` per shot on the voice's frames; placeholder; sentence captions in the look's style |
| `GridStage`, `HoldPush`, `DrawPath`, `PopIn`, `Callout` | the schematic stage: grid ground, creeping hold, self-drawing SVG path, sprung part, label with leader line |
| `KineticText`, `Counter`, `BarChart` | words landing one by one; a number counting up; ranked bars |
| `MapReveal` | world map that zooms to a country and lights others up (names from `COUNTRY_NAMES`) |
| `KenBurns`, `LowerThird`, `SourceCard` | a still with a slow move; name strip; source credit |

Maps: no national borders unless the film is about them; prefer a regional view and keep disputed areas out of frame.

The deep API reference is the `remotion-dev/skills` set (`remotion-best-practices`, `remotion-markup`, `remotion-maps`, `remotion-render`…) when it is installed; this file is enough to build without it. Remotion is free for individuals and companies of up to 3 people.

## Cartoon world template (optional)

`templates/remotion/cartoon3d/` holds the source of a finished 67 s short in the "flat 2D characters in a painted 3D world" look (MIT, see its `LICENSE`): `bridge/` (world, characters, ink outline pass, lens blur, grade, the camera and shot table in `story.ts`), `reports/` (seven measured look reports) and `STYLE_BIBLE.md`.

- It needs extra packages, installed on demand: `cd <motion> && npm i three@0.170.0 @types/three@0.170.0 @remotion/three@<the workspace's remotion version> @react-three/fiber @react-three/postprocessing postprocessing`. Its CC0 Kenney prop models are not included (`public/bridge/kenney/*.glb`); without them the trees, stalls and lanterns are simply left out.
- To use it, copy `bridge/` to `motion/src/films/<slug>/<id>/world/`, export its root component as `Chapter`, and replace `TOTAL` and the `SHOTS` frames in `story.ts` with values read from `chapter.json`.
- It was written for 1080×1920 at 30 fps; every pixel-sized post value scales with output height / 1920.
- The look lives in `lights.ts`, `ink.ts`, `lensblur.ts`, `grade.ts`; the story lives in `story.ts`, the `build.ts` layout and the `cast.ts` roles. Keep the look, write a new story.
- Rendered in this workspace with the full post chain (ink, lens blur, bloom, grade) on three 0.170, Remotion 4.0.542: stills take about 10–13 s each, and 30 frames on 3 workers took 17 s with no blank frames. Render with `--gl angle`.
- `WarmUp` in `Bridge.tsx` must stay: the effect composer builds its passes after the first draw, so without it the first frame of every browser tab (every still, and one frame per render worker) comes out as empty sky. Any other three.js chapter that uses `EffectComposer` needs the same warm-up.
- Half-size stills (`--scale 0.5`) work and are quicker for look checks.

## Traps

- Every bundle copies the public dir into the temp folder and leaves it there. Keep `build/public` small (fonts and this film's art only), and clear old `remotion-webpack-bundle-*` folders from the temp dir after a long session (ask first).
- A font that is not in `build/public/fonts` stops the render with its file name: add the `@fontsource/<family>` package to the workspace and re-run `new_film.py chapters`.
- 3D: ink in the same pass as depth of field gets overwritten; ink is its own pass before the blur. Film grain multiplies file size; add grain at assembly instead (`look.json` `grain`).
