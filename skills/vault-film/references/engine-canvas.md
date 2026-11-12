# Engine: canvas (the Lemo-Opuscar library)

For chapters where a character acts: silent films, cartoon casts, hand-drawn and painterly looks. The picture is one page whose frame is a function of time, rendered by the library at `~/lemo-opuscar` (MIT; `setup.sh` clones it when missing). The same library synthesizes scores and foley.

A chapter folder (`build/<id>/`): `index.html`, `main.js`, `chapter.json` (from `timeline.py`), `fonts/`, `art/`.

## The page contract

```js
window.DUR = CH.frames / CH.fps;   // seconds: exactly the chapter's frame count
window.render = (t) => { ... };    // draw the frame at second t; deterministic
window.READY = true;               // set once fonts and images are loaded
window.EV = [{t, type}];           // optional: sound moments, in chapter seconds
window.TEXTS = (t) => [{id, text, x0, y0, x1, y1}];   // every text visible at t, for readcheck
```

- Deterministic: no `Date.now()`, no unseeded `Math.random()` (`mulberry`, `hash` from `/core/lib.js`), no state carried from the previous frame. Any frame renders alone, in any order, on any worker.
- Library files by absolute URL (`/core/lib.js`, `/node_modules/three/build/three.module.js`); the chapter's own files by relative path. Never `../..`.
- Lay out from `innerWidth` × `innerHeight`; one world → screen function for anything that follows a subject.
- Voice timing from `CH.shots`, `CH.lines`, `cue("beat" | "dry" | "anchor")`; colours and fonts from `CH.look`.
- Animate on twos where the style wants it (hold a pose for 2–3 frames), but keep the camera and light smooth every frame: a stepped camera reads as lag.
- No grain in the page (it makes every frame incompressible); `look.json` `grain` adds it at assembly.

## Commands (run from the library; `new_film.py chapters` prints them filled in)

```bash
cd ~/lemo-opuscar
node core/render/still.mjs  <film>/build/<id> 1.5 3 --range 0:20:2 --size 1920x1080 --out <film>/review --prefix <id>_t
node core/render/video.mjs  <film>/build/<id> --fps 30 --size 1920x1080 --out <film>/build/out/<id>.mp4
node core/render/readcheck.mjs <film>/build/<id> --size 1920x1080      # every on-screen text stays long enough to read
node core/render/events.mjs <film>/build/<id> --out <film>/build/<id>/events.json   # DUR + EV
.venv/bin/python core/render/sheet.py <out.jpg> <stills…> --cols 4
```

Always pass `--fps 30` (the library's default is 24) and the film's `--size`. Stills and renders stop on any page error.

## Characters

- A 2.5D rig (torso, head, limbs solved per frame) is enough for pantomime. Prove it on a model sheet first: turnaround, 3–4 expressions, 2–3 key poses, palette.
- Anticipation, action, follow-through on every meaningful move. Blend poses with keyframes and easing; never switch a pose inside an `if`, except one deliberate comic pop.
- Shoulders: rotate abduction first, then flexion (the reverse crosses raised arms into an X); let the shoulder rise as the arm lifts; do not outline the part of the arm that overlaps the torso.
- A held prop sits between the palms; a hand-over interpolates palm to palm; a rolling object turns by distance ÷ radius.
- Lip sync: open the mouth on each word of the character's line (`CH.lines` gives the line's span; split it by word share), closed in the gaps.
- At key moments the subject fills at least a third of the frame height. Check every expression at final size.
- Step through key actions at 0.2 s intervals, enlarged, before the full render.

## Techniques to read in the library

Each style has a `STYLE.md` (what it looks and sounds like) and a `DEMO.md` (how its demo was built); demo source comes with `sh ~/lemo-opuscar/plugin/skills/lemo-opuscar/scripts/setup.sh demo <slug>`. Read a demo for a technique, never to rebuild that film.

| Need | Look at `~/lemo-opuscar/styles/…` |
|---|---|
| 2D character animation and lip sync | `scifi-toon`, `cel-anime-80s`, `rubber-hose`, `midcentury-toon` |
| silent pantomime, a score on a cue grid | `silent-film`, `pictogram-motion`, `one-line` |
| brush and stroke engines | `watercolor`, `ink-wash`, `impasto`, `crayon-book` |
| paper, shadow and cut-out looks | `shadow-puppet`, `paper-lantern`, `papercut-red` |
| 3D with depth of field | `brick-toy`, `paper-popup` (`core/three/post.js`) |

A chapter may take a library style's look whole; the film's `look.json` palette and fonts still win where text and flat colour appear, so the join with other chapters holds.

## Score and foley (for any film, whatever engine drew it)

Write a `score.py` in the film folder and run it with the library's Python. This form needs no download: plucked and struck instruments are physically modelled (`guqin`, `pipa`, `shamisen`, `koto`, `banjo`, `acoustic_guitar`, `nylon_guitar`, `upright_bass_pizz`, `harp`, `kalimba`, `music_box`), and beds and hits come from `sfx.py`.

```python
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / 'lemo-opuscar'))
import numpy as np, soundfile as sf
from core.audio import pluck as P
from core.audio.sfx import SR, add, limit, rumble, lp

root = Path(__file__).resolve().parent
tl = json.loads((root / 'timeline.json').read_text()); total = tl['dur']
cues = json.loads((root / 'audio/voice_timing.json').read_text()).get('cues', [])
dry = next((c for c in cues if c['type'] == 'dry'), None)
buf = np.zeros((int(total * SR) + SR, 2))
add(buf, lp(rumble(total, .5), 90), 0, gain=.25)                               # low bed from frame 0
add(buf, P.pluck('nylon_guitar', 'D3', 2.2, vel=.6), 0.3, gain=.5, pan=-.2)    # add(buffer, sound, at seconds, gain, pan)
add(buf, P.strum('nylon_guitar', ['D3', 'A3', 'D4', 'F4'], 3.0, vel=.6), total - 2.6, gain=.6)
b = buf[:int(total * SR)]
sf.write(root / 'audio/music/score.wav', np.stack([limit(b[:, 0]), limit(b[:, 1])], axis=1), SR)   # limit() is per channel
```

```bash
~/lemo-opuscar/.venv/bin/python score.py
python3 ~/.claude/skills/vault-film/scripts/mix.py --project . --music audio/music/score.wav --music-end fade --music-under 18
```

- Take every time from `timeline.json` and `audio/voice_timing.json` (chapter starts, each cue, the last frame), so the music lands on the picture. Write the silence at the dry turn into the score, and land the final chord after `max(dry end, dry t + 1.5)`: `mix.py` mutes the music through that window whatever the score holds.
- A synthesized score has no known level: pass `--music-under 18` (explainers 18–20, story Shorts down to 6) and `mix.py` sets the gain so the voice sits that far over the music under speech.
- Bowed strings, piano, winds and percussion come from `core/audio/sampler.py`, which plays real recordings and needs a sample library first: none is installed by default, and the error names the `sh tools/fetch.sh instruments <lib>` command (70–400 MB each; tell the person before downloading). Details and the instrument list: `core/audio/INSTRUMENTS.md`; `sampler.credits(names)` gives the credit lines for `sources.md`.
- Foley: `core/audio/sfx.py` has `click`, `clack`, `crash`, `whoosh`, `creak`, `thump`, `step`, `ding`, `pop`, `rumble`, `heartbeat` and filters. Write each to `audio/sfx/<name>.wav` and place it with a row in `audio/events.json`.
- Score in the instruments of the film's world, one solo voice leading. Keep 20–120 Hz about 3 dB under the rest.
