# Style pack: silent-film

No voice, no dialogue: a film that reads the same in Tokyo, São Paulo and Berlin. Vault sources: folder `01 Animated Short Films` (the Last Soul channel breakdown and four film notes) and `10 Channel Inspiration` notes 01 (Last Soul) and 02 (Monk Mode Films). Take the grammar; never their characters, props, shots or music.

- **Default engine**: canvas (`engine-canvas.md`): a code rig acts, the score is synthesized on the film's own clock.
- **Format**: B. silent short film (`formats.md`), 2:30–6:20 in the references, 16:9. **Persona**: none. No script lint; the beat sheet in `brief.md` is the script. At most one spoken sentence in the whole film, at the turn, and only if the picture cannot carry it.
- **Themes**: a silent shame millions share: the habit never started, the phone at 2 a.m., feeling behind one's peers, the lone-wolf myth, the thing left unsaid.

## Hook: the guilt mirror (first 5 s)

A private failure the viewer committed today, shown without comment: blue screen light at 2:14 a.m., running shoes with the price tag still on, a half-painted canvas behind a sofa. Find a new one; the famous ones are taken.

## Three acts

| Act | Share | What happens | Colour |
|---|---|---|---|
| 1. The guilt loop | first third | who they want to be (one anchor prop) against the cheap trap; the loop repeats, slightly worse | grey, desaturated |
| 2. The valley | middle third | a big effort, no visible result, the breaking point | coldest here |
| 3. The micro-step | last third | no heroic montage: a ridiculously small rule from a child, a stranger or a realisation; momentum compounds | colour bleeds back; the last frame is warmer than the first |

Give the failure room: about 40% of the film is the struggle, so the viewer feels the exhaustion before the payoff. Relapse is allowed and builds trust: the hero may fail once more in act 3 before the step holds.

The turn is never a heroic speech. It is a reframe small enough to be impossible to refuse, or a silent presence. End on a quiet physical action: curtains opened, shoes laced, headphones taken off, a one-word text sent.

A second shape from the vault: an object with a soul (a candle, a watch, a blank notebook) whose physical nature is the metaphor, seen from its own small scale.

## Grammar

- Something changes every 4–6 s: an object, a reaction, a chord.
- Limited animation: poses held on twos or threes (8–12 fps stepping) with long holds on a face, while the camera and the light stay smooth every frame.
- Text only inside the world (a calendar, a fridge note, a phone screen), and little of it: show the message on the screen, then cut to the room it lands in. A title of 1–4 words; one object alone in a dim room for the thumbnail.
- Light: cold slate blue (`#1B2A4A`) in isolation; warm amber (`#E3A857`) enters only with action or connection. Colour may drain from the world step by step and return drop by drop, not all at once.
- Pace by feeling: the trap is fast and hypnotic, the withdrawal lingers and is painfully quiet, time stops for the reframe.
- Series option (Monk Mode): the same rig across numbered parts, each ending on an unresolved choice. Write the arc in `brief.md` and keep the rig's code for the next part.

## Sound

Write the cue map before animating and time shots to it (`shots.json` shots take `beats` or `sec`). The measured shape in the vault: the first 60% is dry room tone and amplified foley only (a clock, rain on glass, a phone buzz breaking the quiet, breath, a pencil snapping); a single piano motif enters for the last 40% and a second voice (cello, acoustic guitar) joins as the hero acts. The sacred silence is everything out for ≥ 1.5 s at the turn, and the first sound after it is the most important sound in the film.

## Review flags

`checks.py export/final.mp4 --project . --warm-ending`, plus the mute test: the contact sheets alone tell the story.
