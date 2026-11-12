---
name: youtube-inspiration
description: Study YouTube reference videos and keep the Obsidian "youtube inspration" vault - break a video down (hook archetype, story architecture and beat map, voice persona and pace, light arc, sound bed, measured cuts and words per minute) into a genre note linked in the YouTube Inspiration Hub, and write or file recreation scripts (original stories in the reference's grammar). Use when the person pastes a YouTube link to analyse, says "break this down", "add this to my vault / Obsidian", "youtube inspration", "inspiration note", "write a recreation script for the vault", or says yes to filing an approved video-studio script. A script meant to become a HyperFrames video starts in video-studio.
---

# YouTube inspiration (Obsidian vault)

The writers' room for the channel: study what works, file it by genre, write original stories in the same grammar. The production line is `video-studio`; this skill never builds or renders.

Vault, taxonomy, note and script templates, hub entry formats: `references/vault.md`. Craft rules come from video-studio (`references/story-and-script.md`: laws, hook archetypes, delivery cues; `references/formats.md`: architectures and beat maps) and free-voiceover (`personas.json`).

## 1. Break down a reference video

1. **Get the facts.**
   - Metadata (title, channel, length, description, chapters): WebFetch the URL.
   - Transcript, in this order: a file the person provides → `npx hyperframes transcribe <file> --json` (local, free); the text they paste from YouTube's "Show transcript" panel; or, if the person has installed yt-dlp and wants it, its captions only (`yt-dlp --skip-download --write-auto-subs --sub-format vtt <url>`, then `npx hyperframes transcribe <file>.vtt` imports them).
   - Measured grammar, when there is a file:

     ```bash
     python3 -I ~/.claude/skills/youtube-inspiration/scripts/ref_metrics.py ref.mp4 --transcript <transcribe json>
     ```

     It prints cuts, shot lengths, cuts/min, the first cut, WPM, speech onset, loudness, sound at 0:00 and the warmth arc, and writes `shots.png` (one frame per shot). Read the sheet. Optional sound map: `npx hyperframes audio ref.mp4 --only moments,loudness,silence --json` (local). `--read --quality best` separates voice, music and SFX but uploads to HeyGen's services and may bill; use it only when asked.
2. **Analyse through the lenses** (the note's sections 3–6):
   - the hook archetype and what happens at 0:00–0:02
   - the architecture and its beat map with timestamps, where the turn and any silence fall
   - the voice (persona match, its Kokoro equivalent, measured WPM, delivery)
   - the picture (shot sizes, cut rate, camera, light arc, palette hex)
   - the sound (foley, the instrument, silences)
   - why it works, and whether the CTA is an invitation or guilt
   - what to take (grammar) and what never to copy (characters, lines, shots, music, art)
3. **File it.** Classify into one of the nine genre folders (propose a new numbered folder and ask if none fits), write the note from the template, and append the hub bullet under that genre's heading. Show the person the note's path and the hub line.

## 2. Write a recreation script (vault only)

- A recreation is an original story in the reference's grammar: a new human (name, age, job, the lie they believe), a new prop, new lines, new shots. The vault's names stay (`Recreated Scripts/`, status "Recreation Script").
- Use Template A (Short) or B (saga) from `references/vault.md`. Write the voiceover as `script.md` lines with delivery cues inside the note, so it moves into an episode unchanged.
- Lint the note before showing it (only its id lines are checked), and set `runtime` from the estimate, not a wish:

  ```bash
  python3 -I ~/.claude/skills/video-studio/scripts/lint_script.py "<note>.md" --seconds <target> --persona <name>
  ```

- Where a series bible exists (08: "Faith Is a Hand That Opens"), follow it: the camera belongs to the human, one verse after the turn, one prop, no guilt CTA, the last frame loops to the first.
- File it in the genre's `Recreated Scripts/`, add a README slate row if that folder has one, and link it in the hub's TIP callout for the genre.

## 3. File an approved video-studio script

When video-studio offers it and the person says yes: a short Template A/B note with the logline, the Four Decisions, the final `script.md` lines, the persona and voice, the runtime from `audio/voice_timing.json`, the episode folder path and status "In production" (or "Published" with the video link). File and link it as in §2.

## 4. Hand-off

"Make this a video" → `video-studio`, start point "a vault script or inspiration note".

## Rules

- Vault edits are additive: new notes, new hub lines, new slate rows. Never reorganise, rename or rewrite existing notes or entries unless asked.
- Claims taken from a reference video are the creator's claims until checked; scripts carry sources like any episode (`sources.md` rules).
- Quote at most a hook line or two from another creator; summarise the rest. Never paste their full transcript into the vault.
