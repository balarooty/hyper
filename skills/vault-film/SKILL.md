---
name: vault-film
description: Make a 1-8 minute video in one of the styles studied in the Obsidian "youtube inspration" vault - code-built explainer (Segment Zero, Ricks Clips, Celyxi), silent emotional film (Last Soul, Monk Mode), character comedy or mascot essay (CasiCreativo, monke), long-form saga on stills (untold lore, myth and history) - from a vault note or a topic to an uploaded file. One self-contained pipeline that can mix three engines inside one film, chapter by chapter (Remotion, the Lemo-Opuscar canvas engine, HyperFrames), with one timeline, one look and one sound mix. Use when the person says "make a vault film", "a video like <vault note or channel>", "make this inspiration note into a video", "1-8 minute video in the style of", "mix Remotion and HyperFrames", or names one of the four style packs.
---

# Vault film

One vault note or topic in, one finished 1–8 minute film out. Everything this skill needs is in this folder; the engines themselves are found or installed by `setup.sh`. Work the stages in order, stop for approval at each ★, and keep the person informed with a task list.

For the person: `prompt-guide/README.md` shows how to ask for a film, and `prompt-guide/names.md` lists every animation style name with a file of ready prompts. When they name one of those styles, read its file and the pack it maps to.

Scripts are run as `python3 ~/.claude/skills/vault-film/scripts/<name>.py --project <film dir>`.

## 0. Once per machine

```bash
sh ~/.claude/skills/vault-film/setup.sh          # `check` to report only
```

It checks Node, ffmpeg, the Kokoro venv, HyperFrames, the Lemo-Opuscar library (`~/lemo-opuscar`) and the shared Remotion workspace (`motion/` next to `skills/`), and creates what is missing. Before trusting any path below, confirm it exists.

## Style packs and engines

| Pack | For | Default engine | Picture | Voice |
|---|---|---|---|---|
| `code-explainer` | mechanisms, paradoxes, bizarre history, every frame in code | Remotion | code | explainer / historian |
| `silent-film` | wordless habit and emotion films | canvas | code | none |
| `character-comedy` | a recurring cartoon cast or mascot teaching real science | canvas | code | a voice per character |
| `saga` | long narrated story on illustrated stills | HyperFrames | the person's stills | chronicler / historian |

Read the pack's file in `references/styles/` before writing anything. Any chapter may use another engine when the content calls for it (`references/mixing-engines.md`).

## Project folder

```
brief.md  sources.md  script.md  cues.md
shots.json    every shot: voice lines or sec, camera, overlay, `draw` (code) or `prompt` (a still)
film.json     the chapters: id, engine, shots, join
look.json     one palette, font set, caption style and grain for every engine
timeline.json, shotlist.md, art/prompts.*        generated; never hand-edit
art/          the person's stills, named by shot id
audio/        voice.json, voice/, voice_timing.json, narration_norm.wav, music/, sfx/, events.json, mix.wav
build/<id>/   one chapter's source on its engine;  build/out/<id>.mp4 its silent render;  build/public/ fonts and art
review/       stills, contact sheets, checks/, notes.md
export/       final.mp4, captions.srt, publish.md
```

The folder is the template for the next episode.

## 1. Intake ★

Settle, asking only what is not already clear:

- **Start point**: a vault note or recreation script (`references/vault.md` maps a note to a pack and a brief), a topic, or a finished script.
- **Pack, length (1–8 min), aspect** (16:9; 9:16 only for a Short), **persona** (`references/voice.md`).
- **Effort**: for anything over 3 min or fully code-drawn, say what it costs before they choose (`references/long-form.md` § Honest effort).

Then `new_film.py init <slug> --pack <pack> [--aspect 9:16] [--title "…"]` and fill `brief.md`.

## 2. Ideas and story ★

- Topic only → `references/ideas.md`: exactly 10 numbered ideas, facts checked first; the person picks.
- `references/story-and-script.md` and the pack file: premise, controlling idea, the ending first; for story formats the Four Decisions. Offer 3 storylines (hook + 3-line spine + ending line); the person picks. ★
- Research into `sources.md`; flag anything unverified. A claim taken from a vault note is the original creator's claim until a source confirms it.

## 3. Script ★

Write `script.md` as `sNN_lNN:` lines with delivery cues (every scene at least one; exactly one `*(dry — cut music)*`, on the turn). Characters who speak: `references/dialogue.md` and a voice sheet each. Then lint until clean:

```bash
python3 -I ~/.claude/skills/vault-film/scripts/lint_script.py script.md --seconds <target> [--persona <name>]
```

Show the script in a copyable block with word count and estimated length, a one-paragraph visual plan and the beat list. After approval, offer once to file it in the vault. A `silent-film` has no script: the beat sheet in `brief.md` is approved instead, and the music comes first.

## 4. Voice

`references/voice.md`. Audition (`voice.py --project . --audition`), the person picks, then `voice.py --project .` voices every line and writes `audio/voice_timing.json` and `audio/narration_norm.wav`. Kokoro only, unless the person asks for a paid voice. Never edit or re-time a recorded voice; the picture is timed to it. A narration that already exists (past ElevenLabs takes, the person's recording) is imported with `import_voice.py` instead (`references/voice.md` § Using a voice you already have).

## 5. Chapter and shot plan ★

`references/shots-and-sound.md`, `references/mixing-engines.md`, `references/long-form.md`.

1. `shots.json`: one shot per phrase; `draw` for a code-drawn shot, `prompt` for a still.
2. `film.json`: chapters of 20–90 s, each on one engine, changing engine only at a scene change. Write the split and the one-line reason per non-default chapter in `brief.md`.
3. `look.json`: adjust the pack's palette and fonts to this film.
4. `plan.py --project .` then `new_film.py chapters --project .`: the timeline, a starter per chapter, and each chapter's still and render commands.
5. `cues.md` and `audio/events.json` for the sound hits.

Show the chapter table (id, engine, seconds, what happens, why that engine) and the shot list. Stills needed from the person: start `art_server.py --project .` in the background and give them `http://127.0.0.1:8765`; wait until they say the images are in, then re-run `new_film.py chapters`.

## 6. Look proof ★

Before building: a character model sheet where there is a cast, and one style frame from every engine the film uses, rendered with the real drawing code and tiled on one sheet. If the frames do not read as one film, fix `look.json` or drop an engine. The person approves the sheet.

## 7. Build, chapter by chapter

| Engine | Read |
|---|---|
| Remotion | `references/engine-remotion.md` |
| canvas | `references/engine-canvas.md` |
| HyperFrames | `references/engine-hyperframes.md` |

Build in story order; finish one chapter (stills at every cue, contact sheet, render to `build/out/<id>.mp4`) before starting the next, and send its sheet with a one-line summary. Every action lands on its cue frame from `chapter.json`. No chapter carries audio, and no `PLACEHOLDER` tile reaches a render.

## 8. Sound, assembly, review ★

```bash
mix.py --project . --music <track or score.wav> --ambience <loop>     # the only mix
assemble.py --project . --check && assemble.py --project .           # export/final.mp4
sheets.sh export/final.mp4 review/sheets
python3 -I ~/.claude/skills/vault-film/scripts/checks.py export/final.mp4 --project . [--warm-ending] [--short]
```

Music is a track the person holds a licence for, or an original score synthesized with the Lemo library (`references/engine-canvas.md` § Score and foley). Then the review loop in `references/review.md`: read every sheet and cue strip as a critic, write each fix as where / wrong / change / keep, re-render only the chapter it belongs to, re-join. Fix order: wrong or missing → readability → timing → visual detail. Look hard at both sides of every chapter join.

## 9. Package

- Captions from the final narration only: `npx hyperframes transcribe audio/narration_norm.wav --to srt -o export/captions.srt`; fix names against `script.md`.
- Offer 1–3 vertical Shorts (`references/shorts.md`): rewritten and re-laid for 9:16, never centre-cropped.
- `references/publish.md` → `export/publish.md`: title and thumbnail matrix, description with chapters and sources, tags, thumbnail prompt, pinned comment, settings.

A film is not done until the review has passed and `export/publish.md` exists.

## Rules

- Grammar only. From a vault note or channel take the hook type, structure, pacing, light and sound; never its story, characters, lines, shots, music or art. New story, new sets, real sources every film.
- Free and local tools: Kokoro for voice, code or the person's own stills for pictures, licensed or synthesized music. No paid generation unless the person asks.
- No real living people as characters or jokes, no brand mascots or logos, nothing graphic or political. Maps follow `references/engine-remotion.md`.
- Every fact, number and asset has a row in `sources.md`; disputed or legendary material is said as such.
- Disclose realistic synthetic voice or visuals when YouTube asks (`references/publish.md`).
- Vault edits are additive: new notes and lines, never a rename or rewrite.
- Breaking down a new reference video is `youtube-inspiration`'s job, not this skill's.
- `motion/src/lib` began from components in a repository with no licence file (`NOTICE.md` there): fine for the person's own films, not for publishing this skill.
