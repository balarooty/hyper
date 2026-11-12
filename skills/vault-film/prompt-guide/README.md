# Prompt guide: how to ask for a vault film

Type these in Claude Code, from the folder where your video projects live (`~/Documents/projects/hyper`). Start with `/vault-film` so the skill loads, then say what you want in plain words.

## The shortest prompt that works

```
/vault-film make a 3 minute code-explainer about why sea mines have spikes
```

Claude asks only what is missing, then stops for your approval at each ★ step: intake, storyline, script, chapter plan, look proof, final review.

## What to put in a first prompt

| Say | Example | If you leave it out |
|---|---|---|
| the style | `schematic explainer`, `silent film`, `organ sitcom`, `saga on stills` (all names: `names.md`) | Claude proposes one from your topic |
| the topic or the vault note | `about the Carpathia's rescue run` / `from my vault note "11 - Segment Zero"` | Claude offers 10 ideas |
| the length | `90 seconds`, `4 minutes` (1–8 min) | Claude suggests one and tells you the effort |
| the voice | `historian voice`, `no voice`, `three character voices` | the style's default |
| anything fixed | `keep this wording`, `use my stills`, `16:9`, `dark blue and amber` | Claude decides and shows you |

## Three ways to start

```
/vault-film make this vault note into a video: "09 - Ricks Clips". New story, same grammar. 2 minutes.
```
```
/vault-film I have a script ready (pasted below). Make it a 5 minute saga on my own stills.
```
```
/vault-film give me 10 ideas for a silent film about phone addiction, 3 minutes
```

## Prompts for each stage

| Stage | What you can say |
|---|---|
| Ideas | `pick 4` · `more like 7 but darker` · `10 new ones, all true stories` |
| Storyline | `storyline 2, but end on the callback from storyline 3` |
| Script | `tighten scene 2` · `the hook is weak, give me 3 new first lines` · `approved` |
| Voice | `audition 3 voices` · `use the second one, a little slower` |
| Chapter plan | `make chapter 3 a canvas character scene` · `fewer engines, keep it all in Remotion` · `approved` |
| Look proof | `warmer palette` · `the character is too small` · `approved, build it` |
| Build | `show me the contact sheet for c02` · `rebuild shot 07, the label is unreadable` |
| Review | `fix: at 0:41 the caption covers the diagram, keep the timing` |
| Finish | `make 2 Shorts from it` · `write the publish kit` |

## Mixing engines in one film

Name what each part should be and Claude plans the chapters:

```
/vault-film 5 minute saga about the Night Witches on my stills, but make the "why the fighters stalled" part
a Remotion cutaway and the last scene a silent canvas character moment
```

## Useful one-liners

- `no stops, build it through to the review` (you still approve the script and the final)
- `don't spend time on a storyboard, go straight to the look proof`
- `continue the film in ./night-witches` (resume an existing project folder)
- `re-voice line s03_l02 and re-time everything after it`
- `use this as the template for the next episode: <new topic>`

## What Claude will not do

Copy a reference channel's story, characters, lines, shots or music; use real living people or brand logos; state a fact that has no source; or use paid voices or image generation unless you ask.

Each style has its own file with ready prompts: see `names.md`.

## See the styles

Open `samples/index.html` to watch a 10-second sample of all 16 styles side by side, or look at `samples/all-styles.jpg`. To rebuild them after changing `samples/src/main.js`: render each with `cd ~/lemo-opuscar && node core/render/video.mjs <samples/src> --fps 30 --q "style=<name>" --out <samples>/<name>.mp4`, then `~/lemo-opuscar/.venv/bin/python samples/src/make_sheets.py`.
