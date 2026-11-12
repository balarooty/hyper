
# YouTube publish kit

Write everything into `export/publish.md` in the project folder and show the person a short version in chat.

## Inputs to read first

`brief.md` (format, persona, hook, Four Decisions, palette), `script.md`, `sources.md`, the final video's duration, `audio/voice_timing.json` (scene/line timings for chapters) and the `checks.py` result. If there is no project folder, ask for the script or transcribe the video.

## 1. Packaging matrix (title + thumbnail, three options, one recommended)

The title and the thumbnail are one package: together they open a curiosity gap the first 30 seconds close.

| Option | Title (≤ 60 chars) | Thumbnail concept | Thumbnail text (2–3 words) |
|---|---|---|---|
| A ← recommended | | | |
| B | | | |
| C | | | |

- Title: ≤ 60 characters so it isn't cut off; the curiosity gap or payoff in the first 40; plain words the viewer would search; no clickbait the video doesn't deliver.
- Thumbnail text: 2–3 words, one in the accent colour; it never repeats the title (they work together).
- Concept: one focal subject, big; for story videos, the hand on the prop or the human's face at the breaking point; for explainers, the hero object mid-change.

## 2. Description

```
<2-line hook that repeats the promise, with the main search phrase>

<3–5 line summary of what they'll learn or feel>

Chapters
00:00 <hook>
0:xx  <section> ...      (first chapter at 00:00, at least 3 chapters, each ≥ 10 s)

Sources
- <from sources.md; scripture with book, chapter:verse and translation>

Credits
- Voice: <Kokoro voice id + persona, e.g. "am_onyx (Kokoro-82M, open-weight AI voice)"> · Music/SFX: <source + licence> · Made with HyperFrames

#tag1 #tag2 #tag3        (max 3 hashtags)
```

- Chapters come from the measured scene start times (`voice_timing.json`), never guessed. Shorts have no chapters.
- Scripture and quotes name their translation. Public-domain translations (KJV, WEB) can be quoted freely; for others (NIV, ESV…) keep quotes short and add the publisher's required attribution line.

## 3. Tags

10–15 tags, most specific first, under 500 characters in all.

## 4. Thumbnail prompt (for ChatGPT / an image model)

One prompt per option A and B in a code block, built from:

- The video's own visual style and palette (pull hex colours from `brief.md` / the build); story videos use the warm turn light (#E3A857) against the cold opening palette.
- The concept from the matrix: one focal subject, big; the 2–3 words of bold text, one word in the accent colour.
- 16:9, 1280×720, readable at phone size, high contrast, no logos or real brands, no faces of real people.
- Tip line: if the model garbles the text, generate without text and add it in Canva.

Offer the second variant for A/B testing (YouTube "Test & compare").

## 5. Upload settings

- **Captions:** upload `export/captions.srt` made from the final narration (`npx hyperframes transcribe audio/narration_norm.wav --to srt -o export/captions.srt`, names fixed against `script.md`).
- **Category:** usually Education or Science & Technology for explainers and lore; Film & Animation for story films and Shorts. **Audience:** "No, it's not made for kids" unless it is.
- **Altered or synthetic content:** answer yes if it has a realistic AI voice or realistic AI-generated people/places/events (photorealistic story stills always count). A plain AI narrator over clearly animated visuals should still be disclosed when YouTube's question applies; when unsure, disclose.
- **End screen:** last 5–20 s; one subscribe element and one video/playlist. Make sure the last 20 s of the edit leave room for it (Shorts have none; they loop).
- **Pinned comment:** a one-line recap and a question that invites replies. For story videos, an ethical CTA that echoes the film's motif (the hand, the prop): an invitation ("Open your hand. Type AMEN if you're still learning to trust."), never guilt or a threat.
- **Playlist** and **Shorts** links (see `shorts.md`).

## 6. Second version

If the person publishes a second visual version of the same video, give it a different title suffix and its own thumbnail. Space the uploads apart, and don't use the same description word for word.
