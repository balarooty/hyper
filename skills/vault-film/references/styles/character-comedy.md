# Style pack: character-comedy

A recurring cartoon cast makes dense facts land as jokes. Vault sources: folders `05 Educational Comedy & Character Animation` and `07 Meme Storytelling & Digital Philosophy`, and `10 Channel Inspiration` notes 03 (CasiCreativo), 04 (monke) and 07 (Hundred Days In). Take the grammar; design a cast of your own and never reuse theirs.

- **Default engine**: canvas (`engine-canvas.md`): rigs with mouth shapes timed to the voice lines. Diagram or data chapters may go to Remotion.
- **Format**: dialogue cartoon or mascot explainer (`formats.md`, `dialogue.md`), 2–8 min, 16:9. **Persona**: a Kokoro voice per character (`cast` in `audio/voice.json`), or one narrator.

## Three shapes

| | Ensemble sitcom | Mascot essay | Second-person serial |
|---|---|---|---|
| Idea | an abstract system is a workplace or a flat-share: each part is a character with one flaw, one goal that clashes with the others, and one voice | one disarming mascot or stock figure explains hard science in plain, slightly odd grammar | "you" are a stick figure in a slow disaster; the story is fiction, the survival facts are real |
| Length | 2:20–5:30 | 4–8 min | 5–6 min parts of a longer run |
| Spine | a ticking clock (hour 4, hour 12; day 1, day 10, day 30): a new stage, and a micro-hook, every ~25 s; ends on a comic button and freeze | 4–6 numbered protocols, each a wild-versus-modern comparison, no filler between them | exact-minute catastrophe → resource rules → strangers → the mystery; each part ends before the door opens |
| Facts | every fact is the punchline of an argument between characters | humour lowers the guard, then exact numbers and cause-and-effect | each rule arrives inside the suspense ("a closed fridge keeps food safe for four hours"), sourced from public safety guidance |
| Voice | a voice per character, 150–165 WPM | one deadpan narrator | one calm, tense narrator, 135–145 WPM, short present-tense sentences, a spoken time or day marker on each beat |
| Picture | bold outlines, bright flats, rubber-hose slapstick | crude, endearing mascot beside crisp diagrams | dark, near-static room or floor plan, torch beams and screen glow; one locked camera for long stretches |

## Cast rules

- The voice comes first and the animation follows it: voice every line, then pose and lip-sync to the measured timings.
- Write a voice sheet per character in `brief.md` (`dialogue.md`): want, flaw, verbal habit, what they never say.
- Jargon becomes an everyday prop (a janitor with a vacuum, furniture broken up for firewood); the real term appears once, on screen, after the joke.
- The cast is the channel's property: keep each rig, palette and voice in the project so the next episode reuses them. Three to five characters; more than that and voices blur.
- No real people, no brand mascots, nothing that resembles the references' characters.

## Performance

Anticipation, action, follow-through on every meaningful move; poses blend, never switch inside an `if`. Check every expression at final size: worried and angry are one eyebrow flip apart. Gags get time to be understood.

## Sound

Layer 1 a light room tone; Layer 2 playful pizzicato or cartoon jazz well under the dialogue, stopping dead for a punchline; a foley hit on every slapstick action (boing, squeak, siren). A serial swaps this for wind, radio static, an alert tone and a low heartbeat. One dry turn still applies: the one sincere line.

## Review flags

`checks.py export/final.mp4 --project .`. Listen to the cast once at full speed: two characters must never sound alike.
