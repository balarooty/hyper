# Style pack: code-explainer

Every frame built in code. A mechanism, a paradox or an order that made no sense, told with exact names, dates and numbers. Vault sources: `10 Channel Inspiration` notes 05 (dark nature framework), 06 (MRAKOPYS), 08 (Celyxi), 09 (Ricks Clips), 10 (Knackery), 11 (Segment Zero), the measured numbers in note 12, and folder `06 Science & History Video Essays` (an 8-minute ink-line essay). Take the grammar; never their stories, lines, characters or drawings.

- **Default engine**: Remotion (`engine-remotion.md`). A chapter with acting characters may go to canvas; a chapter built on stills to HyperFrames.
- **Format**: explainer (`formats.md`), 16:9, 1–8 min. **Persona**: explainer or historian, 145–160 WPM.

## Picking the story

A topic works when it carries a built-in contradiction and a physical cause the viewer can watch:

- a cruel-looking act that is merciful; a criminal who wants the punishment; a survival trick that looks stupid; a fake thing built on purpose (a bus stop to nowhere);
- an everyday object hiding a law of physics (a track curve, a wheel's taper, oil on waves);
- a paradox, a parable with a refrain, or an invention its maker never profited from;
- a flaw that became a strength; an order nobody cancelled; the danger nobody thought of.

Verify it first: these stories travel because they sound too good, and some are not true.

## Voice (pick one register and hold it)

| Register | Delivery |
|---|---|
| Deadpan documentary | icy calm, exact names, dates and numbers; the calm is what makes the stakes feel high |
| Friend at a bar | warm and casual, stress on the contrast words, small bridges ("Here's why.", "Turns out,") |
| Wry storyteller | amused, quick, almost no gaps between sentences; slows just before the reveal so the twist lands |
| Fable and riddle | a refrain repeated in the same calm tone each time; half a second of silence after a riddle's rule |

Kokoro cannot act these by itself: write them in (short sentences, the bridges, a `*(beat)*` before the reveal).

## Hook (first 4 s)

Pick one and put its picture on frame 0:

- **False assumption**: "If you build a railroad with a perfect curve, the train derails the second it turns."
- **Two-sentence question + mechanism**: the question, then the surprising part named at once.
- **Institutional absurdity**: an order nobody cancelled, a job nobody wants.
- **The hidden danger**: everyone fears X; the people there feared Y.
- **A/B dilemma**: the rules of a deal with one hidden catch; two players, two choices, the gap between them grows on screen.

## Beat map, scaled from the 60 s template

The references are 40–65 s. A 1–8 min film is that shape repeated as chapters, each ending on a rehook (`long-form.md`).

| Share of the film | Beat | Picture |
|---|---|---|
| first 4 s | hook | the object and its contradiction, already on screen |
| 5–25% | the obvious solution fails | what happened when people did the obvious thing; a force arrow hitting the thing |
| 25–70% | the mechanism, one layer per chapter | cutaway: the outer wall fades to 20% and the inside moves with the words |
| 70–90% | the consequence / the rule it created | the same object, now seen correctly; a number counts up |
| last 10% | the everyday proof, then the callback | "next time you see a highway ramp, look closely"; the opening image, changed by what the viewer now knows; the dry turn sits here or just before |

A dilemma film runs differently: the rules (5 s) → the fool and the strategist side by side → a crisis that tempts the strategist at about two-thirds → the final tally with a twist, and one open question to the viewer.

A nature or anatomy film is a descent: open in sensory isolation (pressure, dark, cold), then each discovery stranger than the last, with an X-ray reveal (skin → muscle → the organ that explains it) and every size set beside a familiar object.

## Measured grammar (vault note 12)

| | Fast cut (Segment Zero, Celyxi) | One continuous canvas (Ricks Clips, Knackery) |
|---|---|---|
| Hard cuts | 38–43 per min, shot 0.4–5.9 s | 2–6 per min |
| Something new on screen | every 0.75–1.35 s | every ~4 s |
| Motion | static hold ≤ 3% of frames; pan 9–17%, push 10–20%, the rest is the drawing itself animating | static ≤ 8%; a pan/morph carries the whole film |

Choose one column per film and write it in `brief.md`. Whichever it is: no frame is ever frozen (every hold creeps), and something changes at least every 2.5 s.

## Look

- Starting palette (in `look.json`): blueprint `#0B0F17`, strokes cyan `#38BDF8`, amber `#F59E0B`, alert red `#EF4444`. The measured references are warmer and mid-key (mean luminance 112–143 of 255, 13% dark pixels at most); for a warm film swap the ground for an olive or brick tone and keep three accents.
- Other grounds the vault measured or describes: neon vector characters on near-black for a dilemma film (`#1D1425`, 43% dark pixels, long static holds); black, white and sepia ink line for a science-history essay; abyssal black with bioluminescent teal for deep-sea films.
- Bold fact captions: 2–4 words in the display font (`16,000 LBS OF BITE FORCE`) landing with a short hammer sentence.
- Always show the cross-section. Springs are critically damped (`damping 20, stiffness 180`): schematics do not bounce.
- Terminal and code overlays are real text in the mono font, never an image of text.
- Every number on screen has a row in `sources.md` and, where it helps trust, a `SourceCard`.

## Sound

Layer 1 a low room tone or machine hum from frame 0; Layer 2 a light plucked or marimba groove (wry stories), a synth pulse that tightens as stakes rise (dilemmas) or ambient pads (essays); hits on every reveal (tick, thunk, ting, a cash-register ding), 3–6 dB over the bed. The voice sits 18–20 dB over the music.

## Review flags

`checks.py export/final.mp4 --project .`. Mute test on the mechanism chapters: the cutaway alone should explain it.
