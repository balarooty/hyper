# Style pack: saga

A long narrated story over illustrated stills: an untold or misread episode, told as a human drama with its sources named. Vault sources: folders `04 Mythological & Historical Documentaries` and `09 Untold Biblical Lore & Apocryphal Sagas` (its master blueprint, the 7-minute script and the five story blueprints). Take the grammar; write a new telling with its own shots.

- **Default engine**: HyperFrames (`engine-hyperframes.md`): the person's stills with parallax and slow camera moves. A chapter that explains a mechanism or a map may go to Remotion; a wordless character scene to canvas.
- **Format**: C. long-form saga (`formats.md`), 5–8 min, 16:9. **Persona**: chronicler or historian.
- **Pictures**: the person makes the stills (the art board, `shots-and-sound.md` § Art board). One image per 1–3 lines.

## Two shapes

- **The untold drama** (folder 09): a story the viewer knows in a tidy childhood version, retold with its real stakes: betrayal, a trap, a verdict. Six movements, below.
- **Myth versus the original text** (folder 04): a belief everyone holds, checked against the oldest source. The universal belief → the question → the passage itself on screen with the key phrase highlighted → where the popular version came from, on a timeline of retellings → what the change tells us. Silence right after the core finding. Maps, satellite views and engineering diagrams are Remotion chapters.

## Six movements (for ~7 min; scale the windows, keep the order)

| Scene | Job | Share |
|---|---|---|
| s01 The disruption and the oath | shatter the tidy version inside the first 30–45 s | 18% |
| s02 The escalation | the immediate consequence | 18% |
| s03 The point of no return | the trap closes | 18% |
| s04 The confrontation | peak drama, the tokens held up | 21% |
| s05 The verdict | the reversal; the one dry turn | 14% |
| s06 The echo | ancient dust to the viewer's own life; one honest invitation, no guilt | 11% |

Each scene is usually one chapter, and every scene ends on a rehook. Write every word: about 135 spoken words per minute at chronicler pace, never an outline.

## Sources

The vault notes that "banned", "hidden" and "untold" drive clicks. Use such a word only when a source supports it, and say what actually happened (left out of a canon, by whom, when); several popular versions of these claims are false.

Every claim has a row in `sources.md`; disputed or legendary material is said plainly as such. Scripture and apocrypha name their translation, public-domain ones only (KJV, WEB, R. H. Charles' 1 Enoch). For epics, say which text a detail comes from and which tradition added it.

## Look

- Image style for the prompts: dark baroque realism, strong chiaroscuro, candlelight and dust, weathered cloth; for the text-checking shape, public-domain classical paintings and manuscripts.
- Light arc: cold practical light until the turn (`#1B2A4A`), warm sourceless amber after (`#E3A857`); `shots.json` eras `cold` and `warm` carry it into the image prompts.
- 2.5D: a slow push or drift on every still, foreground and background at different speeds when the image is cut into layers. No still sits frozen.
- No text in any image; names, maps, verses and dates are overlays in the look's fonts.
- Grain 4–8, added once at assembly.

## Sound

Layer 1 a constant sub-bass drone (30–60 Hz) and foley (wind over stone, torch crackle, parchment, iron); Layer 2 one folk soloist (duduk, ney, bowed cello; a tanpura drone for Indian epics); silence at the dry turn. Never an upbeat stock track. The voice sits 18–20 dB over the music.

## Review flags

`checks.py export/final.mp4 --project . --warm-ending`. Captions are uploaded as an SRT made from the final narration, not burned in.
