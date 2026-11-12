
# Free voiceover (Kokoro, local)

Kokoro-82M is an open-weight TTS model (Apache 2.0, commercial use OK, safe for monetized YouTube). It runs on this Mac on CPU, no account, no per-minute cost. It is flatter than ElevenLabs and cannot clone voices or act; pacing, pauses and level carry the performance instead, which is what personas and delivery cues control.

## Setup (already done on this machine)

- Python venv with the runtime: `~/.venvs/hyperframes-tts` (`kokoro-onnx`, `soundfile`). All 54 Kokoro voices are in `~/.cache/hyperframes/tts/voices/voices-v1.0.bin`; `tts --list` shows only 12, but any id works (`am_onyx`, `am_puck`, `bm_fable`, `af_bella`…).
- Always prefix commands with `HYPERFRAMES_PYTHON=~/.venvs/hyperframes-tts/bin/python` (voice.py does it for you).
- If the venv is missing: `python3 -m venv ~/.venvs/hyperframes-tts && ~/.venvs/hyperframes-tts/bin/pip install kokoro-onnx soundfile`

One line by hand: `HYPERFRAMES_PYTHON=~/.venvs/hyperframes-tts/bin/python npx -y hyperframes tts "Text" -v am_michael -s 1.0 -o out.wav --json` (`durationSeconds` in the JSON is the timing; never guess).

## Personas (`personas.json`)

A persona is a voice performance: audition voices, speed, pauses and the mic/processing chain. Pick one per video (the brief names it), set it in `<project>/audio/voice.json`, audition, then voice.

| Persona | For | Audition voices (first = default) | Speed | Beat | Gaps (line / scene) | Processing (in the build) |
|---|---|---|---|---|---|---|
| `explainer` | explainers, brisk history/science (channel default) | am_michael, bm_george, af_heart | 1.0 | 0.9 s | 0.35 / 0.8 | none |
| `confessor` | human-first faith/drama Shorts: tired, close, unpolished | am_michael, am_puck, af_heart | 0.82 | 1.2 s | 0.45 / 0.9 | high-pass 80 Hz, +2 dB low shelf (close mic), dry |
| `historian` | lore investigations, myth vs truth, essays: warm, wry | bm_george, bm_fable, am_fenrir | 0.95 | 1.0 s | 0.35 / 0.9 | high-pass 60 Hz, +2.5 dB at 120 Hz |
| `chronicler` | apocrypha sagas, royal tragedies: deep, solemn | am_onyx, bm_lewis, am_fenrir | 0.82 | 1.2 s | 0.45 / 1.0 | +3 dB chest at 110 Hz, stone-chamber reverb (off at the dry turn) |
| `storybook` | illustrated parables: gentle, unhurried | af_bella, bm_fable, bf_emma | 0.8 | 1.2 s | 0.45 / 1.5 | +1.5 dB at 160 Hz, −3 dB above 6.5 kHz |

A silent film (no narration) has no persona: skip this skill. Paid voices (ElevenLabs, HeyGen, fish.audio) only when the person asks; `paid_reference` in personas.json says what to ask for.

The persona's processing chain (reverb, EQ) is recorded in `audio/voice_timing.json` but not baked into the wav, and `scripts/mix.py` mixes the voice dry. A chronicler's chamber reverb is added by hand in the mix only when the person asks for it.

`audio/voice.json` (per project; anything here overrides the persona):

```json
{"persona": "confessor", "voice": "am_michael", "lead_in": 2.0,
 "cast": {"VOICE": {"voice": "bm_george", "speed": 0.9}}}
```

`lead_in` is the silence before the first word (2.0 s for a micro-drama Short whose first 2 s are the hand on the prop). `cast` voices lines tagged `sNN_lNN [NAME]: …`.

## Audition first

```bash
python3 ~/.claude/skills/vault-film/scripts/voice.py --project <episode dir> --audition [--persona confessor] [--voices a,b,c] [--lines 3]
```

Voices the first 3 narrator lines with each audition voice into `audio/audition/<voice>.wav` and prints each voice's measured words per second (rates differ a lot between voices: 2.4–3.3 at the same speed). Send the person the files; they pick; write the voice into `audio/voice.json`.

## Voice the script

```bash
python3 ~/.claude/skills/vault-film/scripts/voice.py --project <episode dir>                      # changed lines only
python3 ~/.claude/skills/vault-film/scripts/voice.py --project <episode dir> --only s02_l01,s04_l03 # redo some lines
python3 ~/.claude/skills/vault-film/scripts/voice.py --project <episode dir> --force               # everything
```

- Reads `script.md` lines `s01_l01: text` and `s01_l02 [NAME]: text`; unchanged lines are reused (cache on text + voice + speed).
- Writes `audio/voice/<id>.wav` (each line levelled to the same loudness, so voices and lines match), `audio/voice_timing.json` (settings, measured words/s, every line's start/end, every cue's time), `audio/narration.wav` and `audio/narration_norm.wav`.
- `narration_norm.wav` is stereo at −16 LUFS by one static gain plus a −1.5 dBFS limiter. No dynamic levelling, so a quiet line stays quiet; stereo because a mono file reads about 3 LU louder once the render plays it on both channels.
- `audio/pronounce.json` maps words to TTS respellings (`{"Enzo": "Ennzo", "Le Mans": "Luh Mahn"}`); it changes only what Kokoro hears. Lowercase respellings work best. Check phonemes before voicing:
  `~/.venvs/hyperframes-tts/bin/python -c "from kokoro_onnx.tokenizer import Tokenizer as T; print(T().phonemize('Ennzo','en-us'))"`
- Verify names by transcribing the result (`npx hyperframes transcribe audio/narration_norm.wav`) and searching for each proper noun.

## Delivery cues (in script.md, never spoken)

| Cue | What voice.py does | Logged in voice_timing.json |
|---|---|---|
| `*(beat)*` | silence of the persona's beat (0.9–1.2 s) instead of the normal gap | `beat` with time and length |
| `*(beat — the fist opens)*` | same, and the action is logged for the picture to land on | `beat` + `action` |
| `*(inhale)*` | 0.45 s pause before the line (Kokoro cannot breathe; breath foley goes here) | `breath` |
| `*(drop register)*` / `*(almost a whisper)*` / `*(whisper)*` | that line at 0.95× speed and −4.4 dB | `drop` |
| `*(dry — cut music)*` / `*(dry)*` | nothing in the wav; the build pulls the music ≥ 1.5 s and the reverb | `dry` with start/end |
| `*(anchor)*` | nothing; marks the verse/moral line | `anchor` |

Placement: a cue on its own line acts on the gap after the previous line (beat) or on the next line (the others); at the start or end of a line it acts on that line; mid-line is an error (split the line). Any other cue is an error. The full writing rules are in `video-studio/references/story-and-script.md`.

## Fixing bad lines

- Mispronounced word → respell in `pronounce.json` (all lines) or in that line only ("Kubernetes" → "koo-ber-net-eez").
- Rushed delivery → split into two lines, add a `*(beat)*`, or drop the speed in `voice.json`.
- Robotic sentence ending → end the line with a full stop, not a comma.

## Captions

`npx hyperframes transcribe audio/narration_norm.wav --to srt -o export/captions.srt` writes captions from the final narration (fix names against script.md before upload); never reuse an old SRT.

## When to suggest something else

- Needs a specific/cloned voice or acted emotion → paid (ElevenLabs, fish.audio, HeyGen), only when the person asks.
- Multi-character drama at quality → Fish Audio Drama 3 (open weights, 35B, needs an NVIDIA GPU; rent one or use fish.audio).

## Using a voice you already have

When the narration was already recorded (a past project, ElevenLabs takes with timestamps), import it instead of re-voicing. The words and timing stay exactly as recorded:

```bash
python3 ~/.claude/skills/vault-film/scripts/import_voice.py --project . --takes <dir with takes.json> \
  --cues audio/cues_in.json [--script <the person's script, to prove no word changed>] [--tail 2.8]
```

- It writes `script.md` (lines verbatim as `sNN_lNN:`, one scene per take section), `audio/voice_timing.json`, `audio/narration.wav` and `audio/narration_norm.wav`, the same files `voice.py` writes, so every later stage works unchanged.
- Delivery cues live in `audio/cues_in.json`, matched to lines by exact text, so a script the person asked you not to edit stays clean. The lint will still report "no delivery cue" for such a script; say so instead of adding cue marks.
- `--tail` sets the hold after the last line; make it long enough for any silent end card (`sec` shot) to sit after the last word.
- Spoken by a synthetic voice: disclose it at upload like any other.
