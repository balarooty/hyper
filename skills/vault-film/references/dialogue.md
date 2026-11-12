# Dialogue (characters who speak)

Read when any character speaks on screen or in voiceover besides the narrator, including the single "voice at the turn" in a micro-drama Short.

## Dialogue is action

Every line does something to the other person. Before writing a line, know the speaker's **want** in this exchange and their **tactic** as a verb-ing (pressing, deflecting, testing, charming, dodging, conceding, pleading). A line with no tactic gets cut.

Three layers: the **said** (words), the **unsaid** (what they're hiding, the audience decodes it), the **unsayable** (the misbelief that only breaks under pressure, at the climax).

## The 9 rules

1. **Every line is a move.** Never open on a greeting. Start mid-action.
2. **Subtext, not therapy.** No "I feel…", no naming emotions, no self-diagnosis ("my trust issues"). Fixate on a prop or detail instead. ✗ "I'm scared Gran can't see." ✓ "When did you last thread a needle, Gran?"
3. **Asymmetry beats ping-pong.** Break Q→A→Q→A. Answer with another subject, a one-word parry, an interruption. Vary line lengths.
4. **Cover-up-names test.** Hide the names: you should still know who's talking from rhythm and sentence shape (clipped commands vs. winding observations).
5. **Spoken economy.** ≤ 2.5 words per second of shot. Contractions and fragments. ✗ "Please return that to me, it is my turn." ✓ "Give it back! My turn!"
6. **Concrete words.** Argue about props, places, bodies, not "respect". Turn a two-person stand-off into a three-way by putting an object between them.
7. **Silence is direction.** After every 2–3 lines, an action that shifts status (slams the ledger, pockets the key). Never more than 4 speeches without one. No filler fidgets ("rubs neck", "shifts weight"). A `*(beat — action)*` cue is such an action.
8. **The one sentence that could reach them.** At the climax, a character says only the single sentence that speaker could say in that exact second: no small talk, no theology lecture, no recap. ✗ "Tamar, I realise now that I broke my promise to give you my third son, and you were right to trick me." ✓ "She is more righteous than I." That line usually carries the `*(dry — cut music)*` cue.
9. **No template leaks.** Never reuse example lines from skill docs or movie clichés. When an authority figure arrives, the squabble stops and pivots.

**Exposition:** never "As you know…". Use facts as ammunition in an argument. The line after a spoken fact is a visceral reaction, not "I see."

## Voice sheet (in `brief.md`, one per speaking character)

```
char_01 <Name>
  look lock: <one fixed line: silhouette + palette + one distinctive feature — reuse verbatim everywhere>
  voice: <Kokoro voice id + speed (goes into `cast` in audio/voice.json), or other provider>, pitch/pace/accent notes
  speech pattern: <sentence skeleton, e.g. two-to-five-word commands, no questions>
  owns: <2–5 signature words>
  never says: <taboos>
  want vs. say: <the gap between what they want and what they say>
  tactics: <2–4 moves>
  toward <other>: <how they change with this listener>
  samples: <5 fresh lines>
```

Two characters must not share most of their speech pattern or sample words; if they blur in the cover-up test, fix the voice sheet first, then the lines. Give each character a different Kokoro voice (e.g. `bm_george` vs `af_heart`); audition with `voice.py --audition --voices a,b`.

## Script format with dialogue

`script.md` uses the same id lines as narration, so `voice.py` can voice it and the lint can check it:

```
## s01 The square
EXT. TOWN SQUARE - DAY
CORVIN (40s, soot-black apron, one brass goggle) kneels by the cart. CLANG!
s01_l01 [CORVIN]: Forty seconds. Hand me the spare.
s01_l02 [MIRA]: You sold the spare.
Mira drops the SPANNER into the well. SPLASH.
*(beat — Corvin stares at the well)*
s01_l03 [CORVIN]: *(dry — cut music)* Then we walk.
```

- `audio/voice.json`: `{"persona": "explainer", "cast": {"CORVIN": {"voice": "bm_george", "speed": 0.95}, "MIRA": {"voice": "af_heart"}}}`. Untagged lines are the narrator.
- Action lines (present tense, max 3 lines per paragraph) sit between speech lines and are never voiced; sounds in CAPS become the SFX cue list in `cues.md`.
- First appearance of a character in CAPS with age and the look lock.
- Hero props in CAPS on first appearance and on each change of state; every state change must be caused by a character's action, and stays changed afterwards.
- Two characters never share one bowl or tool in frame; give each their own.

## Before showing dialogue

1. Run `scripts/lint_script.py script.md`: zero warnings (it checks fidgets, ping-pong, speeches without an action, rhythm, echoes and the cues).
2. Do the cover-up-names read.
3. Check each line fits its shot at ≤ 2.5 words/s.
