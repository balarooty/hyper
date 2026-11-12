# One film from several engines

A film is a list of chapters. Each chapter is built on the engine that suits it, rendered silent, and joined; the sound is mixed once over the whole film.

## The four files that hold it together

| File | Written by | Holds |
|---|---|---|
| `shots.json` | you | every shot: its voice lines (or `sec` / `beats`), camera move, overlay, and `draw` (code-drawn) or `prompt` (a still) |
| `film.json` | you | the chapters: `id`, `title`, `engine` (`remotion` / `canvas` / `hyperframes`), `shots` (`"05-09"`), `join` (`cut` / `dip`) |
| `look.json` | you | one palette, font set, caption style and grain value for every engine |
| `timeline.json`, `build/<id>/chapter.json` | `timeline.py` | each chapter's span in film frames, and its shots, lines and cues in chapter-local frames |

```bash
python3 ~/.claude/skills/vault-film/scripts/plan.py --project .        # shots timed from the measured voice
python3 ~/.claude/skills/vault-film/scripts/new_film.py chapters --project .   # timeline + a starter per new chapter + commands
```

Re-run both after any change to the voice, `shots.json` or `film.json`. Existing chapter sources are never overwritten.

## Choosing the engine for a chapter

Start from the pack's default and move a chapter only for a reason you can say in one line:

| The chapter is mostly… | Engine |
|---|---|
| a mechanism, diagram, chart, map, numbers, type, code on screen | Remotion |
| a character acting, a wordless scene, a hand-drawn or painterly look | canvas |
| the person's stills with camera moves and overlays | HyperFrames |

- Chapters cover every shot once, in order. A chapter is 20–90 s; shorter and the joins get busy, longer and a fix costs a long re-render.
- Change engine at a scene change, never mid-sentence, and prefer a place the story already changes place, time or register.
- Fewer engines is better. Two is normal for a mixed film; three needs a reason for each.
- Write the split and the reasons in `brief.md` ("Engines"); the person approves it with the shot plan.

## The chapter contract

Every chapter renders to `build/out/<id>.mp4`:

- silent, the film's width × height, 30 fps;
- exactly the frame count in `timeline.json` (`assemble.py` refuses a chapter that differs; `--fit` trims or holds up to 3 frames);
- any colour tagging: assembly converts every chapter to limited-range BT.709 and tags the result, so a canvas chapter (full-range JPEG frames) and a Remotion chapter show the same colour.

## Making chapters look like one film

- Palette, fonts and captions only from `look.json`. The fonts are the same `.woff2` files in every engine (`new_film.py chapters` copies them from the workspace's `@fontsource` packages).
- One caption style for the whole film, or none; never captions in some chapters only.
- Agree the camera's feel: if one engine's holds creep at 0.06% per frame, the others do too.
- Grain is added once, at assembly (`look.json` `grain`), never inside a chapter.
- At a join, the two frames either differ clearly (new place, new register: a `cut`) or the story pauses (a `dip`, 8 frames each side). For a matched cut, export the last frame of the outgoing chapter and build the incoming chapter's first frame over it:

  ```bash
  ffmpeg -sseof -0.05 -i build/out/c02.mp4 -frames:v 1 -update 1 review/c02_last.png
  ```

- Look proof before building: one sheet with a style frame from every engine the film uses, side by side. If they do not read as one film, fix `look.json` or drop an engine.

## Sound and assembly

```bash
python3 ~/.claude/skills/vault-film/scripts/mix.py --project . --music <file> --ambience <file>   # audio/mix.wav
python3 ~/.claude/skills/vault-film/scripts/assemble.py --project . --check                       # chapters vs timeline
python3 ~/.claude/skills/vault-film/scripts/assemble.py --project .                               # export/final.mp4
```

`mix.py` takes its length from the picture and places events by film second, film frame or chapter-local second. `assemble.py` joins, adds the grain, pads or cuts the mix to the picture and masters to −14 LUFS with true peak −1.5 dBTP.

## Lessons from the first mixed film

- **Room tone level**: `--ambience-level 0.35` put a brown-noise room tone only 2 dB under the voice and clipped the sum. Use about 0.07 (around −36 dB RMS against a −20 dB voice) and read the printed stem levels.
- **Grain costs size**: grain 3 turned a 6.5 min film into 720 MB; with grain 0 and `--crf 20` it is 59 MB. Keep grain at 0 unless the look needs it.
- **Warm-up for 3D chapters, shared rigs for canvas chapters**: a character used across several canvas chapters lives once in `build/shared/rig.js` and is copied into each chapter by a sync script, because the renderer serves one folder.
