# Kazchart production

Use this route for Kazchart episodes after the narration is ready. Resolve the local [Kazchart skill](../../kazchart-skill/SKILL.md) and its references before authoring scenes. Run its renderer with Node, Playwright Chromium, and ffmpeg. Use paths rooted in the workspace even when video-studio was loaded through an installed symlink.

## Time and build

- Use the recorded narration or the `free-voiceover` output at `audio/narration_norm.wav`. Run the Kazchart `scripts/timestamps.py` against the narration to write `audio/words.json`. Check the transcribed timing against the approved script, especially names and stressed words. If transcription is unavailable, time against the recording manually. Estimates are suitable for previews only.
- Write the editable scene as `build/scene.json` using Kazchart's schema. Use the chosen preset, 30 fps, and 1920×1080 by default (1080×1920 for a vertical brief). Begin at 0, keep shots contiguous, and cover the full narration, including any planned tail. Shots use absolute seconds and element cues use seconds relative to the shot. Keep `shotlist.md` with shot IDs, frame ranges, beats, and the studio's delivery-cue table for shared review.
- For Kazchart, skip `shots.json`, the still-image art board, and HyperFrames composition checks. Use the renderer's contact sheet and inspect risky beats with short range renders. Use `--from` and `--to` for picture-only previews. Review framing and captions in the target aspect.

## Render and review

From the episode directory, set `KAZCHART` to the absolute path of the project's `skills/kazchart-skill` directory, then run:

```bash
mkdir -p review export
node "$KAZCHART/scripts/render.mjs" build/scene.json review/contact.png --contact
node "$KAZCHART/scripts/render.mjs" build/scene.json review/sample.mp4 --from 0 --to 3 --scale 0.5
```

For timed silence, ducking, ambience, or effects, prepare the full mix as `audio/mix.wav`. Match the audio to the scene duration, padding the tail when needed. Pass the mix as the only audio input and omit audio/music fields in the scene JSON. For narration alone use the narration file, padded when needed. Kazchart's constant-volume music option does not apply timed cues.

```bash
node "$KAZCHART/scripts/render.mjs" build/scene.json export/final.mp4 --audio audio/mix.wav
```

Resume [shared review](../../video-review-loop/SKILL.md) at §1. Use Kazchart for fixes and range previews. Verify the export's duration against the narration, check audio and captions, and carry `build/scene.json` alongside the final MP4. Continue with the existing captions and publish kit steps.
