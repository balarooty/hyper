# The vault: reading a note into a film, and filing back

## From a vault note to a brief

The vault is where the grammar comes from. At intake, read the note the person names (or the channel note closest to their topic) and carry into `brief.md`:

| From the note | Into |
|---|---|
| folder and note type | the style pack: `01`, channel notes 01–02 → `silent-film`; `05`, `07`, channel notes 03, 04, 07 → `character-comedy`; `04`, `09`, and `02` (storybook persona) → `saga`; `06`, channel notes 05, 06, 08–11 → `code-explainer`; `03` and `08` are sub-minute devotional Shorts: the nearest pack, said in the brief, or a Short through `shorts.md` |
| hook archetype, beat map, where the turn falls | Hook, Beats |
| voice persona and measured WPM | Voice |
| light arc and palette hex | Palette, then `look.json` |
| sound bed | Sound bed |
| "Take (grammar)" / "Never copy" | Policy notes |
| a recreation script's voiceover block | `script.md`, unchanged, then the lint |
| a recreation script's Four Decisions and shot table | `brief.md`, `shots.json` |

Channel note 12 holds measured cut rates, motion shares and palettes; the style pack files already quote them. Claims inside a note are the original creator's claims until checked against a source.

Filing back is additive only: new notes, new hub lines, new slate rows. Never rename, move or rewrite what is there. After a script is approved, offer once to file it (Template A or B below, status "In production", the film folder's path).

## Paths, taxonomy, templates, hub entries

Vault folder: `~/Library/Mobile Documents/com~apple~CloudDocs/obsidian/Balaji's-Note/youtube inspration/` (spelled "inspration"; keep it). Hub: `YouTube Inspiration Hub.md` in that folder; its dataview table reads the frontmatter fields `genre`, `style`, `status`, `url`.

## Folder taxonomy

| Folder | Scope |
|---|---|
| `01 Animated Short Films` | 2D/3D habit, psychology and silent narrative short films |
| `02 Illustrated Parables` | storybook fables, nature metaphors, gentle voiceover wisdom |
| `03 Devotional & Cultural Shorts` | sacred temple geography, cultural heritage, fast vertical devotional Shorts |
| `04 Mythological & Historical Documentaries` | investigative fact-checking of ancient epics, manuscripts |
| `05 Educational Comedy & Character Animation` | anthropomorphic biology/science comedy |
| `06 Science & History Video Essays` | minimalist ink/line-art anthropology and evolutionary mysteries |
| `07 Meme Storytelling & Digital Philosophy` | internet-culture existential audits, dopamine-detox stories |
| `08 Faith & Biblical Devotional Media` | human-first Christian Shorts, worship anchors; scripts in `Recreated Scripts/` (series bible: `00 - Series Bible - Faith Is a Hand That Opens`) |
| `09 Untold Biblical Lore & Apocryphal Sagas` | long-form (7–30 min) biblical dramas: Enoch, Jubilees, Tamar, Absalom, Elisha |
| `10 Channel Inspiration` | whole-channel breakdowns (methods, voice, formats) and the measured telemetry report |

A video that fits none: propose a new numbered folder and a one-line scope, and ask before creating it.

## Breakdown note (`<folder>/<Video Title> - <Channel>.md`)

```markdown
---
created: YYYY-MM-DD HH:mm
tags: [youtube, inspiration, <genre tags>]
url: <link>
genre: <Genre / sub-genre>
style: <format · length · visual and audio style in one line>
status: To Recreate
---

# <Video Title> | <Channel>

> [!INFO] Video Details
> - **URL:** [Watch on YouTube](<link>)
> - **Creator / Channel:** <channel>
> - **Duration:** <m:ss, format>
> - **Core Premise:** <one or two sentences>

## 1. Genre & Style Classification
## 2. Why It Works (The Viral Mechanics)
<retention mechanics, comment loop, shareability; the CTA type: ethical invitation or guilt>
## 3. Narrative Breakdown
<the beat map with timestamps: hook, wound/setup, breaking/escalation, turn, anchor/payoff, ending>
## 4. Measured Grammar
<the ref_metrics.py block; "not measured" when there was no file>
## 5. Craft Lenses
| Lens | This video |
|---|---|
| Hook archetype | <1–5 / E> — what happens at 0:00–0:02 |
| Architecture | <explainer / A micro-drama / B silent / C saga> |
| Voice | <persona match + Kokoro equivalent>, <WPM>, delivery (beats, whispers) |
| Light | <arc: cold → warm? palette hex> |
| Sound | <Layer 1 foley> · <Layer 2 instrument> · <silences> |
## 6. Recreation Blueprint
- **Take (grammar):** <hook type, structure, pacing, light, sound>
- **Never copy:** <their characters, lines, shots, music, art>
- **Three original story seeds:** <human + prop + value turn, one line each>
```

**Hub entry** (append under the genre's `### 📁` heading, after its last bullet; change nothing else):

```markdown
- [[<note title without .md>]]
  - **Creator:** <channel>
  - **Core Idea:** <one line>
  - **Style:** <one line>
  - **Link:** [YouTube Video](<link>)
```

## Script notes

File scripts in `<folder>/Recreated Scripts/<NN> - <Title> - Recreation Script.md` (create the folder if missing). If the folder's `README.md` has a slate table, add a row (`| NN | [[note]] | runtime | Human | The hand does this | Anchor |`). Link the script in the hub inside the genre's `> [!TIP]` callout:

```markdown
> - **[[<script note title>]]**
>   - *Production-Ready Screenplay:* <one line: runtime, format, persona>
```

### Template A: Short, human first (20–70 s)

````markdown
---
created: YYYY-MM-DD HH:mm
tags: [youtube, recreation, script, shorts, human-story]
genre: <Genre>
status: Recreation Script
runtime: <the lint's estimate> seconds
aspect: 9:16 vertical
persona: <confessor | …> (<kokoro voice>)
source: "[[<inspiration note>]]"
---

# <TITLE IN CAPS>
### Recreation Script · <runtime> seconds · 9:16

> [!INFO] Logline
> <one sentence: the human, the prop, the turn>

## THE STORY — Human First
### THE LIFE
### THE BREAKING
### THE BELIEVING / THE TURN

## Four Decisions
| Element | Decision |
|---|---|
| **Human** | <name, age, job, the lie they believe> |
| **Prop** | <one object> |
| **Value Turn** | <start → end, in the hand> |
| **Anchor Word** | <verse/quote + translation; after the turn> |

## Shot-by-Shot
| Time | Picture (camera & blocking) | Sound & Voice | Text on Screen |
|---|---|---|---|
| 0:00–0:02 | **MACRO** — <the hand + the prop> | <foley only> | — |

## Voiceover (paste into an episode's script.md unchanged)
```
## s01 The hand
s01_l01: <line>
*(beat)*
s01_l02: <line>
*(beat — <the hand's action>)*
## s02 The turn
s02_l01 [VOICE]: *(dry — cut music)* <the one sentence>
*(beat)*
s02_l02: <line>
```

## Production Notes
- **Voice:** persona <name>, <voice> (auditioned or to audition); cast <NAME → voice>.
- **Image prompts:** style + era + scene + character sheet, no text in any image, portrait 9:16 (Midjourney users append `--ar 9:16 --style raw`).
- **Light:** cold #1B2A4A until the turn, warm #E3A857 after; the last frame warmer than the first.
- **Sound:** Layer 1 <foley>, Layer 2 <one instrument, key>, silence at the dry line.

## Craft Check
<the nine questions from story-and-script.md §8, answered>
````

### Template B: long-form saga (~7 min)

````markdown
---
created: YYYY-MM-DD HH:mm
tags: [youtube, recreation, script, long-form, storytelling]
genre: <Genre>
style: <visual & audio style>
duration: <the lint's estimate> (~<words> spoken words)
persona: <chronicler | historian> (<kokoro voice>)
status: Recreation Script
source: "[[<inspiration note>]]"
---

# <Title> — Saga Script

> [!INFO] Production Metadata
> - **Run time:** <estimate> at <persona> pace incl. beats
> - **Narrator:** <persona, voice, processing>
> - **Visual engine:** <art style, light arc, camera>
> - **Audio bed:** <sub-bass/foley, solo instrument, silence at the verdict>

## Logline

## Screenplay
### Scene 1: <title> [0:00 – 1:15]
**VISUAL:** <camera, light, environment, prop action> · *SFX:* <foley>
```
## s01 <title>
s01_l01: <narration with cues>
```
<Scenes 2–6 the same, per the windows in formats.md § C; the dry turn in scene 5>

## Image Prompt Bank
1. **<shot>:** <style + era + scene; no text; 16:9 (Midjourney: `--ar 16:9 --style raw`)>

## Packaging Matrix
| Option | Title (≤ 60 chars) | Thumbnail concept | Thumbnail text (2–3 words) |
|---|---|---|---|
| **A** ← recommended | | | |
| **B** | | | |
| **C** | | | |
````
