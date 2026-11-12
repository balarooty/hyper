#!/usr/bin/env python3
"""lint_script.py <script.md> [--seconds N] [--wps W] [--persona NAME]

Deterministic craft lint for narration and dialogue scripts. No network, stdlib only.

- Narration mode (the file has `sNN_lNN:` lines): only those lines are speech - exactly the lines voice.py voices.
  `sNN_lNN [NAME]: text` is spoken by NAME. Headings, notes, tables and prose around them are ignored, so a
  vault note with a voiceover block can be linted as it is.
- Screenplay mode (no id lines): the line(s) after an ALL-CAPS character cue are speech; other prose is action.
- Delivery cues *(beat)* *(beat — action)* *(inhale)* *(drop register)* *(dry — cut music)* *(anchor)* are checked
  and never counted as words.
- Length = lead-in + words / words-per-second + gaps + beats + tail, from the persona (personas.json),
  <script dir>/audio/voice.json and, once voiced, the measured words/s in audio/voice_timing.json.
Prints warnings with line numbers and exits 1 if any were found.
"""
import argparse, json, re, sys
from pathlib import Path

EMOTION = re.compile(r"\b(i|we)\s+(feel|felt|am|'m|was)\s+(so\s+|really\s+|very\s+)?(angry|sad|scared|afraid|hurt|happy|upset|frustrated|anxious|nervous|terrified|excited)\b|\bi just wanted to say\b|\bmakes? me feel\b", re.I)
THERAPY = re.compile(r"\b(coping mechanism|projecting|abandonment issues|trust issues|sabotag\w+ (myself|us)|my trauma|emotionally unavailable|boundaries)\b", re.I)
EXPO = re.compile(r"\b(as you know|what i'?m trying to say|the point is|as we discussed|let me explain)\b", re.I)
OPENER = re.compile(r"^\W*(hello|hi there|hey guys|good (morning|evening|afternoon)|how are you|long time no see|welcome back|in this video|today we|let'?s dive in|without further ado)\b", re.I)
CLICHE = re.compile(r"\b(we'?ve got company|it'?s quiet\.{0,3} too quiet|i have a bad feeling about this|let'?s do this|this changes everything|you don'?t understand|it'?s not what it looks like|we need to talk|game[- ]changer|buckle up|stay tuned|smash that like)\b", re.I)
HOOK = re.compile(r"\b(in a world where|have you ever wondered|ever wondered why|imagine a world|since the dawn of time|throughout (human )?history|did you know|what if i told you)\b", re.I)
INTENS = re.compile(r"\b(very|extremely|incredibly|unbelievably|shockingly|insanely|utterly|terribly|awfully)\s+(?!(much|many|few|little|well|first|last|same|end|least|most|best|beginning|moment|day|night|thing|one)\b)[a-z']+", re.I)
GUILT = re.compile(r"\b(if you (skip|scroll past|ignore) this|(skip|scroll past|ignore) this (and|if)|don'?t you dare (skip|scroll)|you don'?t (really )?love (god|jesus)|only (true|real) (believers|christians|fans)|(god|jesus) (will|is going to) (punish|curse)|share (this )?or (else|you)|type amen or|if you don'?t (share|subscribe|comment|type))\b", re.I)
FIDGET = re.compile(r"\b(rubs? (the )?back of (his|her|their) neck|shifts? (his|her|their)? ?weight|picks? at (his|her|their) nails|fiddles? with|runs? a hand through (his|her|their) hair|sighs? heavily)\b", re.I)
DIGIT = re.compile(r"\b\d+(\.\d+)?\b")
SLUG = re.compile(r"^(INT\.|EXT\.|INT/EXT|[A-Z][A-Z' .-]+ - [A-Z ]+$|FADE |CUT TO|MONTAGE)")
CUE = re.compile(r"^[A-Z][A-Z0-9' .()-]{1,30}$")
LINE_RX = re.compile(r"^(s\d+_l\d+)(?:\s*\[([A-Za-z][A-Za-z0-9_ -]*)\])?\s*:\s*(.*)$")
CUE_RX = re.compile(r"\*\(\s*([^)]*?)\s*\)\*")
STOP = set("a an the and or but to of in on at for with is are was were it its it's i you he she they we that this be been not no so as by from your my our their his her me him them do does did have has had just".split())
DEFAULTS = {"voice": "am_michael", "speed": 1.0, "wps": 2.6, "beat": 0.9, "inhale": 0.45,
            "lead_in": 0.5, "line_gap": 0.35, "scene_gap": 0.8, "tail": 1.0}
VOCAB = "beat, beat — <action>, inhale, drop register / almost a whisper / whisper, dry / dry — cut music, anchor"

def words(s): return re.findall(r"[A-Za-z']+|\d+", s)
def content(s): return {w.lower() for w in words(s) if w.lower() not in STOP and len(w) > 2}
def sentences(t): return [x for x in re.split(r"(?<=[.!?])\s+", t) if words(x)]

def cue_kind(body):
    parts = re.split(r"\s*[—–]\s*|\s+-{1,2}\s+", body.strip(), maxsplit=1)
    head = parts[0].strip().lower().rstrip(".")
    rest = parts[1].strip() if len(parts) > 1 else ""
    first = head.split(",")[0].split("/")[0].strip()
    if first == "beat": return "beat", rest or None
    if first in ("inhale", "breath", "inhale slow"): return "inhale", None
    if first in ("drop register", "almost a whisper", "whisper"): return "drop", None
    if first in ("dry", "cut music"): return "dry", None
    if first == "anchor": return "anchor", None
    return "unknown", body

def parse_narration(lines, w):
    """-> speech [(n, speaker, text, scene)], cues [dict n, kind, arg, line (speech index it acts on), gap_after],
    actions [(n, text)]: plain lines between the first and last id line (dialogue action; never voiced)."""
    speech, cues, pending, actions = [], [], [], []
    ids = [i for i, l in enumerate(lines, 1) if LINE_RX.match(l.strip())]
    lo, hi = (ids[0], ids[-1]) if ids else (0, 0)
    for n, raw in enumerate(lines, 1):
        l = raw.strip()
        m = LINE_RX.match(l)
        if not m and not CUE_RX.search(l):
            if l and lo < n < hi and not l.startswith(("#", "|", ">", "<!--", "```")) and not SLUG.match(l): actions.append((n, l))
            continue
        if m:
            lid, body = m.group(1), m.group(3)
            spk = (m.group(2) or "").strip().upper() or "NARRATOR"
            text = re.sub(r"\s+", " ", CUE_RX.sub(" ", body)).strip()
            if not text: w(n, f"{lid} has no words"); continue
            idx = len(speech); speech.append((n, spk, text, lid.split("_")[0]))
            for c in pending: c["line"] = idx
            pending = []
            for c in CUE_RX.finditer(body):
                kind, arg = cue_kind(c.group(1))
                if kind == "unknown": w(n, f"unknown delivery cue *({c.group(1)})* - use: {VOCAB}"); continue
                at_start = not CUE_RX.sub("", body[:c.start()]).strip()
                at_end = not CUE_RX.sub("", body[c.end():]).strip()
                if not (at_start or at_end): w(n, f"cue *({c.group(1)})* in the middle of a line - split the line there (each line is one voice take)"); continue
                gap_after = kind == "beat" and at_end and not at_start
                cues.append({"n": n, "kind": kind, "arg": arg, "line": idx, "gap_after": gap_after})
        elif CUE_RX.search(l) and not CUE_RX.sub("", l).strip():
            for c in CUE_RX.finditer(l):
                kind, arg = cue_kind(c.group(1))
                if kind == "unknown": w(n, f"unknown delivery cue *({c.group(1)})* - use: {VOCAB}"); continue
                cue = {"n": n, "kind": kind, "arg": arg, "line": None, "gap_after": False}
                if kind == "beat" and speech: cue.update(line=len(speech) - 1, gap_after=True)
                else: pending.append(cue)
                cues.append(cue)
    for c in pending: w(c["n"], f"*({c['kind']})* after the last line has no line to act on")
    return speech, [c for c in cues if c["line"] is not None], actions

def parse_screenplay(lines, w):
    """Old parser (screenplay or plain prose), with cue-only lines and inline cues taken out."""
    out, cues, speaker, after_cue = [], [], None, False
    has_cues = any(CUE.match(l.strip()) and not SLUG.match(l.strip()) for l in lines)
    for i, raw in enumerate(lines, 1):
        l = raw.strip()
        if l.startswith("```"): continue
        if not l: after_cue = False; speaker = None if has_cues else speaker; continue
        if l.startswith(("#", "|", ">", "<!--")) or SLUG.match(l): continue
        found = list(CUE_RX.finditer(l))
        for c in found:
            kind, arg = cue_kind(c.group(1))
            if kind == "unknown": w(i, f"unknown delivery cue *({c.group(1)})* - use: {VOCAB}")
            else: cues.append({"n": i, "kind": kind, "arg": arg, "line": None, "gap_after": False})
        l = re.sub(r"\s+", " ", CUE_RX.sub(" ", l)).strip()
        if not l: continue
        if has_cues:
            if CUE.match(l) and len(words(l)) <= 4:
                speaker, after_cue = re.sub(r"\s*\(.*\)", "", l).strip(), True; continue
            if after_cue and l.startswith("(") and l.endswith(")"): continue
            if after_cue: out.append((i, speaker, l, "speech")); continue
            out.append((i, None, l, "action"))
        else:
            l2 = re.sub(r"^[-*\d.)\s]+", "", l)
            if l2: out.append((i, "NARRATOR", l2, "speech"))
    for c in cues:  # attach to the nearest speech line after (or before) the cue
        nxt = [k for k, x in enumerate([o for o in out if o[3] == "speech"]) if x[0] >= c["n"]]
        c["line"] = nxt[0] if nxt else max(0, len([o for o in out if o[3] == "speech"]) - 1)
    return out, cues

def load_timing(script, persona_flag):
    root = Path(script).resolve().parent
    pj = Path(__file__).resolve().parents[1] / "personas.json"
    personas = json.loads(pj.read_text()) if pj.exists() else {}
    vj = root / "audio" / "voice.json"
    proj = json.loads(vj.read_text()) if vj.exists() else {}
    name = persona_flag or proj.get("persona") or "explainer"
    s = dict(DEFAULTS); s.update(personas.get(name, {}))
    if "voices" in s: s["voice"] = s["voices"][0]
    if "speed" in proj and "wps" not in proj:  # a faster/slower voice.json speed scales the persona's rate
        s["wps"] = round(s["wps"] * proj["speed"] / s["speed"], 3)
    s.update({k: v for k, v in proj.items() if k != "persona"})
    s["persona"], s["wps_source"] = name, "persona" if name in personas else "default"
    vt = root / "audio" / "voice_timing.json"
    if vt.exists():
        t = json.loads(vt.read_text())
        if t.get("wps") and t.get("persona", name) == name and t.get("voice") == s["voice"] and t.get("speed") == s["speed"]:
            s["wps"], s["wps_source"] = t["wps"], "measured"
    if not personas: s["wps_source"] = "default (personas.json not found)"
    return s

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script"); ap.add_argument("--wps", type=float, help="words per second of speech (overrides persona/measured)")
    ap.add_argument("--seconds", type=float, help="target length; warns if the estimate is off by more than 12%%")
    ap.add_argument("--persona", help="voice persona from personas.json (default: audio/voice.json or explainer)")
    a = ap.parse_args()
    lines = open(a.script, encoding="utf-8").read().splitlines()
    warn = []
    def w(n, msg): warn.append((n, msg))
    narration = any(LINE_RX.match(l.strip()) for l in lines)
    if narration:
        sp, cues, actions = parse_narration(lines, w)
        items = sorted([(n, spk, t, "speech") for n, spk, t, _ in sp] + [(n, None, t, "action") for n, t in actions])
        scenes = [sc for *_, sc in sp]
    else:
        items, cues = parse_screenplay(lines, w)
        scenes = None
    speech = [x for x in items if x[3] == "speech"]

    # line checks
    for n, spk, t, kind in items:
        if kind == "action":
            if FIDGET.search(t): w(n, f"filler fidget in action: '{FIDGET.search(t).group(0)}' — use a status-shifting action or cut it")
            continue
        for rx, name in ((EMOTION, "names an emotion"), (THERAPY, "therapist-speak"), (EXPO, "exposition plug"), (CLICHE, "cliché"),
                         (OPENER, "throat-clearing opener"), (INTENS, "intensifier — let a concrete noun or verb carry it"),
                         (GUILT, "guilt-trip CTA — invite, never threaten (echo the film's hand/prop motif)")):
            m = rx.search(t)
            if m: w(n, f"{name}: '{m.group(0).strip()}'")
        if DIGIT.search(t): w(n, f"digits '{DIGIT.search(t).group(0)}' — write numbers as spoken words")
        if spk == "NARRATOR":
            for s in sentences(t):
                if len(words(s)) > 22: w(n, f"sentence of {len(words(s))} words — split it (aim 8–15)")
        elif len(words(t)) > 25: w(n, f"{len(words(t))}-word speech — too long for one breath; cut or split with an action")
    if speech and HOOK.search(speech[0][2]): w(speech[0][0], f"cliché hook: '{HOOK.search(speech[0][2]).group(0)}' — open on the hand, the prop or the counter-intuitive fact")

    # dialogue structure (named speakers)
    dlg = [x for x in speech if x[1] != "NARRATOR"]
    if len(dlg) >= 2:
        run = 0
        for x in items:
            if x[3] == "speech" and x[1] != "NARRATOR":
                run += 1
                if run == 5: w(x[0], "5+ speeches with no action line between — anchor with a status-shifting action")
            elif x[3] == "action" or x[1] == "NARRATOR": run = 0
        for k in range(len(dlg) - 2):
            if all(d[2].rstrip().endswith("?") for d in dlg[k:k+3]): w(dlg[k][0], "3 questions in a row — break the ping-pong")
        for k in range(len(dlg) - 3):
            lens = [len(words(d[2])) for d in dlg[k:k+4]]
            if max(lens) - min(lens) <= 2: w(dlg[k][0], f"4 speeches of near-equal length {lens} — vary the rhythm")
        for k in range(len(dlg) - 5):
            firsts = [words(d[2])[0].lower() for d in dlg[k:k+6] if words(d[2])]
            for f in set(firsts):
                if firsts.count(f) >= 3: w(dlg[k][0], f"'{f}' opens 3+ of 6 speeches — vary openers"); break
        for k in range(len(dlg) - 1):
            a1, b1 = dlg[k], dlg[k+1]
            ca, cb = content(a1[2]), content(b1[2])
            if a1[1] != b1[1] and len(ca) >= 3 and len(cb) >= 3 and len(ca & cb) / min(len(ca), len(cb)) >= 0.6:
                w(b1[0], f"echoes {a1[1]}'s line — two voices saying the same thing")
    nar = [x for x in speech if x[1] == "NARRATOR"]
    firsts = [words(s[2])[0].lower() for s in nar if words(s[2])]
    for k in range(len(firsts) - 5):
        win = firsts[k:k+6]
        for f in set(win):
            if win.count(f) >= 3 and f not in ("the", "a"): w(nar[k][0], f"'{f}' opens 3+ of 6 lines — vary openers"); break

    # cadence: long-long-short. Monotone runs and scenes with no hammer line
    sents = [(n, len(words(s)), (scenes[i] if scenes else None)) for i, (n, spk, t, _) in enumerate(speech) if spk == "NARRATOR" for s in sentences(t)]
    k = 0
    while k + 5 <= len(sents):
        lens = [x[1] for x in sents[k:k+5]]
        if min(lens) >= 7 and max(lens) - min(lens) <= 4: w(sents[k][0], f"5 sentences of near-equal length {lens} — break the drone with a short hammer line"); k += 5
        else: k += 1
    if scenes:
        for sc in dict.fromkeys(scenes):
            ss = [x for x in sents if x[2] == sc]
            if len(ss) >= 4 and min(x[1] for x in ss) > 6:
                w(ss[0][0], f"scene {sc} has no hammer line (a sentence of 6 words or fewer after the longer ones)")

    # delivery cues: every scene directed, one dry turn, anchor after it
    if scenes:
        cued = {scenes[c["line"]] for c in cues}
        for sc in dict.fromkeys(scenes):
            if sc not in cued:
                n0 = next(n for (n, *_), s in zip(speech, scenes) if s == sc)
                w(n0, f"scene {sc} has no delivery cue — a flat wall of text; mark at least one *(beat)*")
    if speech:
        dry = [c for c in cues if c["kind"] == "dry"]
        anchor = [c for c in cues if c["kind"] == "anchor"]
        if not dry: w(speech[0][0], "no *(dry — cut music)* cue — mark the one turning-point line where the music drops out")
        for c in dry[1:]: w(c["n"], f"{len(dry)} dry cues — total silence lands once, on the turn")
        for c in anchor[1:]: w(c["n"], "more than one *(anchor)* — one verse, quote or moral per film")
        if anchor:
            c = anchor[0]
            if dry and c["line"] < dry[0]["line"]:
                w(c["n"], "anchor before the turn — the verse/moral lands after the dry turning-point line, never as decoration first")
            elif not dry:
                before = sum(len(words(x[2])) for x in speech[:c["line"]]); total_w = sum(len(words(x[2])) for x in speech)
                if total_w and before / total_w < 0.6: w(c["n"], "anchor in the first 60% — the verse/moral lands after the turn")

    # length estimate
    s = load_timing(a.script, a.persona)
    if a.wps: s["wps"], s["wps_source"] = a.wps, "--wps"
    total_w = sum(len(words(x[2])) for x in speech)
    speech_s = total_w / s["wps"]
    per_scene = {}
    if narration:
        beats = {}
        for c in cues:
            if c["kind"] == "beat":
                key = c["line"] if c["gap_after"] else c["line"] - 1
                beats[key] = beats.get(key, 0) + 1
        pauses, prev_sc = s["lead_in"] + s["beat"] * beats.get(-1, 0), None
        inhales = {c["line"] for c in cues if c["kind"] == "inhale"}
        for i, (n, spk, t, sc) in enumerate(sp):
            p = 0.0
            if i:
                gap = s["scene_gap"] if sc != prev_sc else s["line_gap"]
                p += max(gap, s["beat"] * beats.get(i - 1, 0))
            if i in inhales: p += s["inhale"]
            pauses += p
            r = per_scene.setdefault(sc, [0, 0, 0.0]); r[0] += 1; r[1] += len(words(t)); r[2] += p + len(words(t)) / s["wps"]
            prev_sc = sc
        last = len(sp) - 1
        pauses += max(s["tail"], s["beat"] * beats.get(last, 0))
    else:
        pauses = 0.0
    est = speech_s + pauses
    who = f"{s['persona']}, {s['voice']} @ {s['speed']}" if narration else "screenplay"
    print(f"speech words: {total_w}  ·  est. {est:.1f}s (speech {speech_s:.1f}s + pauses {pauses:.1f}s) at {s['wps']} words/s "
          f"[{who}; rate: {s['wps_source']}]  ·  speech lines: {len(speech)}  ·  cues: {len(cues)}")
    if per_scene:
        print("  scene  lines  words    est.")
        for sc, (nl, nw, sec) in per_scene.items(): print(f"  {sc:5s}  {nl:5d}  {nw:5d}  {sec:5.1f}s")
    if a.seconds and abs(est - a.seconds) / a.seconds > 0.12:
        target_w = max(0, round((a.seconds - pauses) * s["wps"]))
        print(f"WARN length: {est:.1f}s vs target {a.seconds:.0f}s — aim for ~{target_w} words at this pace")
        warn.append((0, "length"))
    seen = set()
    for n, msg in sorted(warn):
        if (n, msg) in seen or msg == "length": continue
        seen.add((n, msg)); print(f"WARN line {n}: {msg}")
    nwarn = len(seen) + (1 if any(m == "length" for _, m in warn) else 0)
    print("OK: 0 warnings" if not warn else f"{nwarn} warning(s)")
    sys.exit(1 if warn else 0)

if __name__ == "__main__":
    main()
