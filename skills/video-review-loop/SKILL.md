---
name: video-review-loop
description: Review a rendered video without watching it ten times - pre-render HyperFrames checks, contact sheets, delivery-cue strips, an Opus critic pass with scoped four-field fixes, partial re-renders, and a final export check (format, loudness, sound at frame 0, Shorts loop, warm ending) before upload. Use when the person says "review the video", "check the render", "is it ready", "what's wrong with this cut", or after any full or partial render.
---

# Video review loop

Never review by re-watching full exports. Make the frames come to you, critique as a critic (not the author), fix with scoped edits, re-check only what changed.

## 0. Before any render

```bash
npx hyperframes check build --json          # lint + runtime, layout, motion, WCAG contrast; fix every error
npx hyperframes snapshot build --at <t,…>   # the cue times printed under shotlist.md, plus each shot's middle
```

While a lint error remains, the layout and contrast audits don't run ("0 samples" means nothing was checked). If a render fails, keep the first exact error and run `npx hyperframes doctor`.

## 1. Make the sheets

```bash
bash ~/.claude/skills/video-review-loop/scripts/sheets.sh <video.mp4> <out_dir> [fps=1] [cols=8]
python3 -I ~/.claude/skills/video-review-loop/scripts/checks.py <video.mp4> --project <episode dir> [--short] [--warm-ending]
```

`sheets.sh` writes `sheet_01.png …` (one tile per second; timestamps burned in when ffmpeg has drawtext, otherwise tile n on sheet k is second ((k−1)·48 + n)/fps), `audio_wave.png` and `probe.txt`. `checks.py` prints the export checks (§5) and, with `--project`, writes `review/checks/cues/`: a 5-frame strip (0.2 s apart, from 0.2 s before) at every beat action, the dry turn and the anchor, plus `dry_wave.png` around the turn. For a dense beat, re-run on a clip at a higher fps:

```bash
ffmpeg -ss 41.5 -t 2 -i video.mp4 -vf "fps=15,scale=360:-1,tile=6x5" -frames:v 1 beat.png
```

## 2. Critic pass

Read every sheet image and cue strip. Compare against `script.md`, `shotlist.md` (with its delivery-cue table) and `brief.md` if the project has them. Look for:

- **Wrong or missing**: a fact on screen that contradicts the script, a shot the shotlist promised that isn't there, wrong spelling, a placeholder left in.
- **Frame 0**: the hook image is on screen at 0:00; no logo, title card or greeting in the first 2 s. A Short's last frame returns to its first.
- **Readability**: text too small at phone size (under ~4% of frame height), low contrast, text over busy areas, captions covering faces or the hand on the prop, anything key in a Short's bottom fifth.
- **Timing**: shot changes not landing on narration beats; a `beat — action` whose action misses its strip (it should land on frames 2–3); holds over 6 s with nothing changing; a payoff before its setup; the last frame ending before the music resolves.
- **Light arc** (story formats): cold practical light until the turn, warm after, the ending warmer than the opening (`checks.py --warm-ending`).
- **Mute test** (silent films, and every Short): the sheets alone tell the story.
- **AI-slop and slideshow tells**: everything bouncing/floating the same way, centred fade-in/fade-out clusters, static slides, characters that never pause before acting, generic gradients/glows, the same layout in every scene, empty corners.
- **Audio** (from the waveform, `dry_wave.png` and a listen of key spots): voice clipped; music fighting the voice; the dry turn not actually dry (the bed should vanish, voice and foley stay); more than one solo instrument or a stock orchestra; silence gaps; dead air at 0:00; an SFX hit off its picture event; music ending because the file ran out; words or breaths cut at a scene change. Say in the notes that audio was measured, not heard, until the person listens.

## 3. Write fixes as four fields

Every correction goes into `review/notes.md` as:

```
- where: 01:12–01:15 (frames 2160–2250), scene s05
  wrong: label "Harness" overlaps the stove icon
  change: move label 40px up, fade in 6 frames after the stove lands
  keep: stove position, narration timing, colours
```

Order: wrong/missing → readability → timing → visual detail. Do not wander outside the "where".

## 4. Fix and re-render only the range

```bash
npx hyperframes render build --start <S> --end <E> --quality delivery -o review/fix_01.mp4   # MP4, whole fps (24/25/30/60), SDR
ffmpeg -i v1.mp4 -i review/fix_01.mp4 -filter_complex \
 "[0:v]trim=end=<S>,setpts=PTS-STARTPTS[v0];[0:a]atrim=end=<S>,asetpts=PTS-STARTPTS[a0];[1:v]setpts=PTS-STARTPTS[v1];[1:a]asetpts=PTS-STARTPTS[a1];[0:v]trim=start=<E>,setpts=PTS-STARTPTS[v2];[0:a]atrim=start=<E>,asetpts=PTS-STARTPTS[a2];[v0][a0][v1][a1][v2][a2]concat=n=3:v=1:a=1[v][a]" \
 -map "[v]" -map "[a]" -c:v libx264 -crf 16 -preset slow -pix_fmt yuv420p -c:a aac -b:a 320k v2.mp4
```

Pick `S` and `E` on frame boundaries (multiples of 1/30 s) at cuts or quiet moments. Re-run the sheets on that range only (`ffmpeg -ss S -to E …`) and the checks on the new file. Mark the note done. Blender: `blender -b file.blend -s START -e END -a`.

## 5. Final export check (before upload)

```bash
python3 -I ~/.claude/skills/video-review-loop/scripts/checks.py export/final.mp4 --project . [--short] [--warm-ending]
```

| Check | Pass |
|---|---|
| format | H.264 + AAC; 1920×1080 (long-form) or 1080×1920 (`--short`); the planned fps; not shorter than the narration |
| loudness | −16.5 to −13.5 LUFS integrated, true peak ≤ −1 dBTP (fix with group volumes, not the voice file) |
| frame 0 | sound in the first 0.5 s (room tone or foley, never dead air) |
| loop (`--short`) | first and last frames match: SSIM ≥ 0.5 and close in colour |
| warm end (`--warm-ending`) | the last second is warmer than the first (Cr−Cb rises by ≥ 6) |

It exits 1 on any FAIL. By hand, if needed: `ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate:format=duration -of default=nw=1 final.mp4` and `ffmpeg -i final.mp4 -af loudnorm=I=-14:TP=-1:print_format=summary -f null - 2>&1 | tail -12`.

Last step for the person: watch once at normal speed on a phone with sound on.
