# Shot plan, light, motion and sound timing (HyperFrames)

Read when writing `shots.json`, `shotlist.md` and `cues.md`, after the voice exists (a silent film is timed to its music instead).

## Timing is locked to the voice

- Never edit or re-time the voice. The picture is timed to it.
- Times come from `audio/voice_timing.json` (free-voiceover: per-line start/end and every delivery cue) or `npx hyperframes transcribe` word timestamps. Total frames = round(duration × 30).
- Every visual reaction lands 0–3 frames **before** its word; a sound effect peaks one frame after its picture (light arrives before sound).
- `plan.py` lists the delivery cues in frames under the shot list: each `beat — action` is where that action lands (the fist closes on the beat, not before); the `dry` frame is where the music and reverb go out; the `anchor` frame is where the verse/moral holds still.
- Lock picture timing before final sound. Any timing change means redoing the cue sheet and mix (`audio_bed.py` regenerates from the voice).

## Shot plan (one row per shot, in frames)

`frames | words | setting | light | camera move | characters / pose / expression | effects | SFX cue`

- Frame 0 is already the hook image. No title card, logo or greeting first. In a story Short, frame 0 is a MACRO of the hand on the prop, voice-free for 2 s (a shot with no `lines` and `sec: 2`, plus `lead_in: 2.0` in `audio/voice.json`).
- A Short's last shot matches frame 0 (same framing, same grade) so the loop is seamless: a shot with no `lines` and `sec: 1` at the end.
- Usually one shot per phrase; merge tiny phrases into the next shot.
- Illustrate every sentence literally; props carry the jokes and the emotion. The hero prop is always rich and detailed, and it persists across the film, changing state only through a character's action.
- Vary shot sizes: close hook → wide reveal → two-shot → insert close-up on the key object → reaction close-up → environment move for the payoff.
- The twist/turn line (the `dry` cue) gets the sting: music out, a low hit or nothing, a push-in with a slight roll. The last shot's payoff lands on the final word.

## Light and grade

- **Explainers**: day/neutral for normal, warm golden for drama or decline, night-blue for explanation. A time jump gets a 6-frame white flash.
- **Story formats (the light rule)**:
  - Until the turn, light the struggle with harsh, lonely practical sources: a blue phone screen at 2 a.m., a hospital monitor, cold rain through a windshield. Use cold #1B2A4A / #2F4F4F.
  - At the turn, when grace, revelation or breakthrough enters, bring in warm amber light with no visible source: #E3A857 / #D4AF37.
  - The final frame is graded warmer than the opening frame. `checks.py --warm-ending` measures it.
- **Building it**:
  - Use `shots.json` eras named `cold` and `warm` with those hex notes, so the images arrive in the right light.
  - In the build, put a warm grade on the turn and ending media (`npx hyperframes media-use resolve --type grade --intent "warm amber candlelight" --project build --json`, or a params LUT with `"temperature": 0.3`) and ramp `--hf-color-grading-intensity` from 0 to 1 across the turn.
  - A silent film goes from desaturated grey to colour the same way. Syntax: media-use `references/grading.md`.

## Art board (person-made images)

Scripts: `scripts/plan.py` (shots.json + voice timing → shotlist.md, art/prompts.md, art/prompts.json) and `scripts/art_server.py` (local page on 127.0.0.1 for copying prompts and uploading images). Both take `--project <episode dir>`.

**shots.json** is the single source of truth for art direction:

```json
{
 "title": "The Ferrari Story",
 "aspect": "16:9",
 "style": "Anime cel-shaded illustration … No text, no letters, no numbers, no logos, no badges, no brand marks, no watermark.",
 "eras": {"early": "Early 1900s palette: warm sepia …", "modern": "…"},
 "characters": {"ENZO_OLD": "a tall Italian man in his sixties with swept-back silver-white hair, large dark sunglasses …"},
 "shots": [{"id": "01", "lines": "s01_l01", "era": "modern", "move": "slow push-in",
            "overlay": "counter 0 → 13,663 cars", "prompt": "… scene description … (ENZO_OLD)"},
           {"id": "02", "sec": 2.0, "era": "modern", "move": "macro hold", "prompt": "… a shot with no narration …"}]
}
```

`plan.py` builds each full prompt as style + era + scene + character sheets, and times each shot from 3 frames before its first line to the start of the next shot. A shot with no `lines` takes `sec` (or `beats` with `--beats`): before the first voiced shot it fills from frame 0; elsewhere it sits just before the next shot or the end. `"aspect": "9:16"` makes the prompts and the art board portrait.

**Prompt rules**
- One shot ≈ one image per 1–3 lines (about 5–12 s). Shorter beats reuse an earlier image or use a code-built card.
- No text, numbers, logos, badges or wordmarks in any image: labels, numbers, maps, charts and the anchor verse are HyperFrames overlays (`overlay` field), so they stay sharp, correct and editable.
- People are described by appearance, never by name, and brand names never appear in prompts. Image models refuse or distort real names and draw real logos when a brand is named. Real emblems are drawn as original shapes (e.g. "an original rearing horse silhouette on a plain yellow rectangle, no shield, no lettering").
- One shared style sentence and fixed character sheets on every prompt; the subject in the centre third with margin, so camera moves and a 16:9 crop of a 3:2 image never cut it (9:16: margin above and below, and keep the bottom fifth clear of key detail; captions and Shorts UI sit there).
- Tell the person: make every image in one ChatGPT conversation, in the project's orientation; lock the look on 2–3 key shots (the hero prop, each main character) first, then say "keep this exact style and character designs"; regenerate any image that came back with text.
- Era palettes change with time jumps and with the light arc (cold → warm); the style sentence never changes.
- Realistic AI people or places must be disclosed at upload (`youtube-publish-kit`).

## Motion

- Nothing static for 4+ frames: holds creep, characters idle and blink, something secondary always moves (cloth, dust, leaves, steam, rain, water).
- **Dwell and sweep**: the camera rests 1.5–2.5 s on each hero moment (the world still moving), then sweeps to the next. A plain `*(beat)*` is a dwell; a `beat — action` is the action.
- **Arrive, don't cut**: the next region enters from the frame edge and the last one exits by parallax; prefer continuous moves (pull back from a close-up to wide, push into an object, rack focus ~14 frames). Hard cut only on place/time jumps and the Short's loop match-cut.
- Camera glides use smootherstep over 18–45 frames; reveals and whips ease out; 3–5° rolls on drama; a 7-frame shake on impacts.
- Actions: anticipation → overshoot → spring settle. Impacts: 2-frame dip + dust puff + kick. Physical motion obeys physics (a 30 cm drop ≈ 7–8 frames at 30 fps).
- No slideshow tells: centred fade-in/fade-out clusters, static slides, the same layout every scene, everything bouncing the same way.
- Vertical 9:16 frames are narrow: stage characters in depth, not side by side.
- Diegetic text (signs, carved words) must read correctly, never mirrored.

## Captions

- No captions unless asked or the format needs them (Shorts usually do). Burned-in captions: at most two lines, broken at meaning points, 1–3 words at a time on Shorts, 2–3 key words in the accent colour; keep them off faces, hands on props and the bottom UI zone.
- Read the transcript before using it: names, terms and numbers are the usual recognition errors.

## Look check before the long render

1. `npx hyperframes check build --json`: fix every error (lint, layout, motion, contrast).
2. `npx hyperframes snapshot build --at <times>`: the cue times are printed under the shot list (every beat action, the dry turn, the anchor), plus each shot's middle and the transitions; or `--review` for each scene's start and middle.
3. Make a contact sheet (`video-review-loop/scripts/sheets.sh`) and send it to the person with a one-line shot summary, then start the full render.

## Sound: the 3-layer bed

1. **Layer 1, dry reality from frame 0**: room tone, foley and sub-bass under everything (rain on glass, an engine tick, parchment unrolling, a hammer on iron, sandals on gravel, a 35 Hz rumble). Never dead air at 0:00.
2. **Layer 2, one solo instrument** per video (C-minor solo piano, a mournful cello, a duduk, a nylon-string guitar; a light electronic bed for explainers); not a cluttered stock orchestra. Source it with `media-use` (HeyGen catalog after a free sign-in, local MusicGen, or the person's own licensed track; log the licence in `sources.md`).
3. **Layer 3, the sacred silence**: at the `dry` cue the music drops out completely for ≥ 1.5 s; foley and the unguarded line stand alone. After it, the music comes back, resolves on one chord, or stays out.

Write the bed with:

```bash
python3 ~/.claude/skills/video-studio/scripts/audio_bed.py --project . --music audio/music/<track> --ambience audio/sfx/<loop> \
  [--breath audio/sfx/<breath>] [--music-in <s>] [--after-dry fade|none] --inject
```

It writes the narration with the persona's `data-fx-chain` (reverb off through the dry turn), ambience from frame 0, the music ducked to 0.35 under speech, out through the dry turn, and back-timed (`data-media-start`) so the track's real ending lands on the last frame (looped and faded only if it's too short), plus breath foley at `*(inhale)*` cues. Paste `build/audio-bed.html` inside the root composition once (it carries the markers); later runs with `--inject` replace it. Optional carve: `node ~/.claude/skills/media-use/audio/scripts/carve.mjs --comp build/index.html`. Syntax for anything hand-made: media-use `references/mixing.md`.

- Cue sheet in `cues.md` in the same frame numbers as the picture: whooshes on big moves, thunks on stamps, rumble+crash on collapses, ting on reveals, the sting (or the silence) at the dry turn. Each hit sits 3–6 dB over the bed; rotate 2–3 takes of a repeated sound.
- Levels: the voice is always on top. Music under the voice: about −18 to −20 dB below for explainers (`--music-level 0.25 --duck 0.35`); closer (up to −6 dB) only for punchy story Shorts when the person wants that style. SFX peaks never poke out over the narration. No pumping compression.
- Music ends on purpose (back-timed to the last frame or resolved on a chord), never when the file runs out; no words or breaths cut at scene changes.
- Final: about −14 LUFS, true peak ≤ −1 dBTP, checked by `video-review-loop/scripts/checks.py`. If the mix is off, change the group volumes (or `npx hyperframes normalize-audio`), not the voice file.
