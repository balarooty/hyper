
# Shorts from long-form

A Short is not a crop of the long video. It is a self-contained 30–60 s story built from it, in its own episode folder (`<slug>-short-1/`, same layout as any vault-film; `new_film.py init <slug>-short-1 --aspect 9:16`), reusing the long-form's art, voice persona and sources.

## 1. Pick moments

Read `script.md` (or transcribe the video with `npx hyperframes transcribe`). Score candidate segments on:

- One complete idea that makes sense with zero context.
- A "wait, really?" fact, a clean visual payoff, or a human moment with a prop (a hand that opens, a door slammed).
- A summary/cheat-sheet moment (recaps are strong Shorts).

Propose 1–3 candidates with timestamps, a hook archetype (`story-and-script.md` §2) and a one-line hook each. ★ Person picks.

## 2. Rewrite the narration

- Size it by the persona, not a fixed rate: about 140–160 words for 60 s at explainer pace, about 100 at confessor pace with a 2 s hook. `lint_script.py script.md --seconds 55` sizes it exactly. Hard ceiling 60 s unless asked.
- The hook lands in the first 2 s: the first spoken line, or (story Shorts) a voice-free 2 s macro of the hand on the prop with `lead_in: 2.0` in `audio/voice.json`. No "in this video", no greeting.
- Story channels use the micro-drama beat map (`formats.md` § A): the hand → the wound → the breaking → the turn (the one `*(dry — cut music)*` line) → the anchor → echo and loop.
- Delivery cues as in the long-form; the lint must be clean.
- End on the payoff, then loop back to the first image; never end on "subscribe". The CTA, if any, is an on-screen invitation at the loop point that echoes the motif, never guilt.
- Re-voice the new lines with the same voice and persona (`voice.md`), so timing is fresh.

## 3. Re-lay for 9:16

Do not centre-crop 16:9 scenes. Rebuild the layout:

- Canvas 1080×1920, 30 fps: `new_film.py init <slug>-short-1 --aspect 9:16`, and `"aspect": "9:16"` in `shots.json`; every engine template lays out from the frame size.
- Safe zone: keep text and key visuals between y≈260 and y≈1500 and x 60–1020 (the bottom ~420 px is covered by the caption/UI, the right edge by buttons).
- Stack instead of side-by-side; stage characters in depth; one idea per screen; type at least ~56 px.
- Big burned-in captions, 1–3 words at a time, word-timed from the new narration, at most two lines, 2–3 key words in the accent colour, off faces and off the hand on the prop.
- Reuse the long-form's assets/scenes in HyperFrames with a vertical composition; new person-made stills come from the portrait art board (`plan.py` + `art_server.py`).
- The last shot matches frame 0 (same framing, same grade): a shot with no `lines` and `sec: 1`, a match-cut, so the Short replays seamlessly.
- Sound: the same 3-layer bed (`mix.py`), foley from frame 0.

## 4. Export and check

Run the review (`review.md`) on the Short (sheets at 2 fps) and:

```bash
python3 -I ~/.claude/skills/vault-film/scripts/checks.py export/final.mp4 --project . --short [--warm-ending]
```

Expect 1080×1920, ≤ 60 s, about −14 LUFS, sound at frame 0, and a loop that matches (SSIM ≥ 0.5, close in colour).

## 5. Publish notes

Title ≤ 40 chars, with the hook; description first line links the full video. Add the full video as the Short's "related video" in YouTube Studio. Full kit: `publish.md`.
