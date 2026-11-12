# Formats

Pick one at intake. The format sets the aspect, length, persona, spine, beat map, how the voice is set up and which review flags run. Word counts are estimates; `scripts/lint_script.py` sizes the real script and the voice measures it.

| Format | Aspect | Length | Persona (`free-voiceover`) | Spine | `checks.py` flags |
|---|---|---|---|---|---|
| Explainer | 16:9, or 9:16 Short | ~45 s – 12 min | explainer, historian | narration formula + hook loop | (`--short`) |
| A. Micro-drama Short | 9:16 | 20–60 s | confessor + one cast voice | Life → Breaking → Turn | `--short --warm-ending` |
| B. Silent short film | 16:9 or 9:16 | 1–4 min | none | Guilt loop → Valley → Micro-step | `--warm-ending` + mute test |
| C. Long-form saga | 16:9 | ~7 min (10–30 scaled) | chronicler, historian | six scenes, Disruption → Echo | `--warm-ending` |
| Dialogue cartoon | either | 30 s – 3 min | a Kokoro voice per character | `dialogue.md` | (`--short`) |

## Explainer

The narration formula and hook loop in `story-and-script.md`. Pick one storyline angle:

- **Understand one idea**: open with a useful question, then reveal the mechanism one layer at a time.
- **Follow a process**: one visual stage; show each step in the order the viewer needs it.
- **Remember three points**: parallel, concrete, visually distinct points.
- **Learn through a story**: one case moves from setup and tension to a general lesson.

Scenes: the opening creates a question, tension or surprise; the main idea is clear by the second scene; each body scene advances one mechanism, step, example or implication (one idea per scene); the ending lands the sentence the viewer should remember. Diagrams reveal mechanisms, charts prove claims, motion shows what changes. Long-form sections run 45–90 s and end on a rehook. The dry turn is the twist line; an anchor is optional (the "so that's why" line).

## A. Micro-drama Short (human first, 20–60 s, 9:16)

Write the Four Decisions in `brief.md` first (Human, Prop, Value turn, Anchor word; see `story-and-script.md` §1). Beat map for 25 s (stretch the middle for longer):

| Time | Beat | Picture | Sound | In the script |
|---|---|---|---|---|
| 0:00–0:02 | The hand | MACRO: the hand doing something unexplained with the loaded prop | dry foley only (rain on glass, engine tick) | no voice: `lead_in: 2.0`; a shot with no `lines`, `sec: 2` |
| 0:02–0:07 | The wound | the human in their place, cold practical light | one sentence naming the unspoken pain | `*(beat)*` after it |
| 0:07–0:15 | The breaking | the failed attempt to fix it alone (fogged windshield, stopped pen, closed door) | the solo instrument enters | `*(beat — <the hand's action>)*` |
| 0:15–0:21 | The turn | light shifts cold → warm; the hand opens, releases or grips | music out: the one sentence lands dry | `*(dry — cut music)*` on that line, often `[VOICE]` |
| 0:21–0:24 | The anchor | the anchor word holds still on screen | one resolving chord, or silence | `*(anchor)*` if spoken, else an overlay |
| 0:24–0:25 | Echo and loop | ethical invitation as on-screen text; match-cut back to 0:00 | foley | a shot with no `lines`, `sec: 1` |

- Words at confessor pace with the 2 s lead-in and beats: 25 s ≈ 35–45, 45 s ≈ 70–85, 60 s ≈ 95–115.
- `audio/voice.json`: `{"persona": "confessor", "lead_in": 2.0, "cast": {"VOICE": {"voice": "bm_george", "speed": 0.9}}}`.
- `shots.json`: `"aspect": "9:16"`; the pre-roll hand shot and the loop shot have `sec` and no `lines`.
- Sound: `audio_bed.py --ambience <foley loop> --music <solo instrument> --music-in <first line start> --after-dry none` (one chord or silence after the turn; `fade` if the anchor needs a bed).
- Grade: cold until the turn, warm after; the last frame warmer than the first (`checks.py --short --warm-ending`).

## B. Silent short film (1–4 min, zero voice)

Every beat must read for a viewer in Tokyo, São Paulo or Berlin with the sound off.

- **Act 1 (0:00–1:00), the guilt loop**: who they want to be (an anchor prop: running shoes, a canvas, a textbook) against the cheap dopamine trap (a glowing phone, red calendar crosses, a grey, desaturated room).
- **Act 2 (1:00–2:00), the valley of disappointment**: a big effort, no visible result, the breaking point. Find an original image for the plateau; don't reuse the famous ones.
- **Act 3 (2:00–end), the frictionless micro-step**: no heroic montage. A mentor, a child or a realisation offers a ridiculously small rule ("Can you do it for one minute?"); colour bleeds back as momentum compounds.

- No narration, so no persona, no voice stage and no lint; write the beat sheet in `brief.md` instead (beat, picture, sound, seconds).
- Choose the music first. `npx hyperframes beats audio/music/<track> --json > audio/beats.json`; give each shot `beats` (a count) or `sec`, then `python3 ~/.claude/skills/video-studio/scripts/plan.py --project . --beats audio/beats.json` cuts on the beat grid.
- Sound: amplified tactile foley (breathing, a pencil snapping, shoe squeaks) plus one solo instrument. The sacred silence is the music dropping out for ≥ 1.5 s at the turn: put it in `cues.md` and as a `volume` lane on the music (media-use `mixing.md`).
- Light: desaturated grey that turns to colour; review with the mute test (the contact sheets alone tell the story) and `checks.py --warm-ending`.

## C. Long-form saga (~7 min, 16:9)

The hook (the disruption) lands inside the first 45 s; every scene ends on a rehook; one `sNN` per scene.

| Time | Scene | Words | Job |
|---|---|---|---|
| 0:00–1:15 | s01 The disruption and the oath | ~160 | shatter the sanitised version; the transgression or secret pact |
| 1:15–2:30 | s02 The escalation, the forbidden gift | ~170 | the immediate consequence |
| 2:30–3:45 | s03 The point of no return | ~160 | the trap closes |
| 3:45–5:15 | s04 The confrontation | ~190 | peak drama: the tokens held up, the throne approached |
| 5:15–6:15 | s05 The verdict, the catharsis | ~150 | the reversal; the dry turn is here |
| 6:15–7:00 | s06 The existential echo | ~120 | ancient dust to modern human nature; one ethical subscribe line |

- About 900–950 words at chronicler or historian pace including beats; the lint's per-scene table checks each window. Longer films keep the six movements and still have one dry turn.
- Write every word: a 7-minute script is ~950 spoken words in six timestamped scenes, never an outline.
- Sources: every claim in `sources.md`; disputed or legendary material said plainly. Scripture and apocrypha name their translation (public domain: KJV, WEB, R. H. Charles' 1 Enoch).
- Sound: the chronicler's chamber reverb (off at the dry turn), sub-bass and foley, one solo instrument (cello, duduk).

## Dialogue cartoon

`dialogue.md`. Voice it with `voice.py`: speech lines are `sNN_lNN [NAME]: line`, a `cast` in `audio/voice.json` gives each character a different Kokoro voice, and action lines sit between them unvoiced.
