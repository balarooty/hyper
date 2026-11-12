#!/usr/bin/env python3
"""Per-line Kokoro voiceover for a vault-film project (reusable template).

usage:
  python3 ~/.claude/skills/vault-film/scripts/voice.py --project <episode dir> [--persona explainer]
          [--voice am_michael] [--speed 1.0] [--lead-in 0.5] [--only s03_l02,s05_l01] [--force] [--jobs 4]
  python3 ~/.claude/skills/vault-film/scripts/voice.py --project <dir> --audition [--voices a,b,c] [--lines 3]

Reads script.md lines `s01_l01: text` (or `s01_l01 [NAME]: text`, voiced by NAME from `cast` in audio/voice.json)
and delivery cues, which are never spoken:
  *(beat)*  *(beat — action)*  *(inhale)*  *(drop register)* / *(almost a whisper)* / *(whisper)*
  *(dry)* / *(dry — cut music)*  *(anchor)*
A cue on its own line acts on the gap after the previous line (beat) or on the next line (the others).
A cue at the start or end of a line acts on that line (a beat at the end: the gap after it). Mid-line: error.

Settings: personas.json[persona] -> <project>/audio/voice.json -> command-line flags.
Writes audio/voice/<id>.wav (only lines whose text, voice or speed changed, unless --force),
audio/voice_timing.json (settings, measured words/s, lines, cues), audio/narration.wav and
audio/narration_norm.wav (-16 LUFS integrated by one static gain, then a -1.5 dBFS limiter: quiet lines stay quiet).
"""
import argparse, hashlib, json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
PERSONAS = HERE.parent / "personas.json"
ENV = dict(os.environ, HYPERFRAMES_PYTHON=str(Path.home() / ".venvs/hyperframes-tts/bin/python"))
LINE_RX = re.compile(r"^(s\d+_l\d+)(?:\s*\[([A-Za-z][A-Za-z0-9_ -]*)\])?\s*:\s*(.*)$")
CUE_RX = re.compile(r"\*\(\s*([^)]*?)\s*\)\*")
DROP_DB, DROP_SPEED, TARGET_LUFS, LIMIT = -4.4, 0.95, -16.0, 0.841  # LIMIT = -1.5 dBFS sample peak
LINE_LUFS = -20.0  # every line is levelled here before stitching (static gain per line, then the drop cue)
DEFAULTS = {"voices": ["am_michael"], "speed": 1.0, "wps": 2.6, "beat": 0.9, "inhale": 0.45,
            "lead_in": 0.5, "line_gap": 0.35, "scene_gap": 0.8, "tail": 1.0, "fx_chain": []}


def words(s): return re.findall(r"[A-Za-z']+|\d+", s)


def cue_kind(body):
    """'beat — the fist closes' -> ('beat', 'the fist closes'); anything unrecognised -> ('unknown', body)."""
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


def parse_script(path):
    """-> (pre_cues, items, errors). Each item: id, scene, speaker, text (cues removed), before[], after[], n."""
    items, pending, pre, errors = [], [], [], []
    for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        l = raw.strip()
        m = LINE_RX.match(l)
        if m:
            lid, body = m.group(1), m.group(3)
            spk = (m.group(2) or "").strip().upper() or None
            if spk == "NARRATOR": spk = None
            text = re.sub(r"\s+", " ", CUE_RX.sub(" ", body)).strip()
            before, after = pending, []
            pending = []
            for c in CUE_RX.finditer(body):
                kind, arg = cue_kind(c.group(1))
                if kind == "unknown":
                    errors.append(f"line {n}: unknown cue *({c.group(1)})*"); continue
                at_start = not CUE_RX.sub("", body[:c.start()]).strip()
                at_end = not CUE_RX.sub("", body[c.end():]).strip()
                if not (at_start or at_end):
                    errors.append(f"line {n}: cue *({c.group(1)})* in the middle of a line - split the line there"); continue
                cue = {"kind": kind, "arg": arg}
                (after if kind == "beat" and at_end and not at_start else before).append(cue)
            if not text:
                errors.append(f"line {n}: {lid} has no words"); continue
            items.append({"id": lid, "scene": lid.split("_")[0], "speaker": spk, "text": text,
                          "before": before, "after": after, "n": n})
        elif CUE_RX.search(l) and not CUE_RX.sub("", l).strip():  # a line holding only cues
            for c in CUE_RX.finditer(l):
                kind, arg = cue_kind(c.group(1))
                if kind == "unknown":
                    errors.append(f"line {n}: unknown cue *({c.group(1)})*"); continue
                cue = {"kind": kind, "arg": arg}
                if kind == "beat": (items[-1]["after"] if items else pre).append(cue)
                else: pending.append(cue)
    if pending:
        errors.append("cue(s) after the last line have no line to act on: " + ", ".join(c["kind"] for c in pending))
    return pre, items, errors


def load_settings(a, root):
    personas = json.loads(PERSONAS.read_text()) if PERSONAS.exists() else {}
    vj = root / "audio/voice.json"
    proj = json.loads(vj.read_text()) if vj.exists() else {}
    name = a.persona or proj.get("persona") or "explainer"
    if personas and name not in personas:
        sys.exit(f"unknown persona '{name}' (have: {', '.join(k for k in personas if not k.startswith('_'))})")
    s = dict(DEFAULTS); s.update(personas.get(name, {}))
    s["persona"], s["voice"], s["cast"] = name, s["voices"][0], {}
    s.update({k: v for k, v in proj.items() if k != "persona"})
    for k in ("voice", "speed", "lead_in"):
        if getattr(a, k) is not None: s[k] = getattr(a, k)
    return s


def tts_text(t, pron):
    for k, v in pron.items():
        t = re.sub(rf"\b{re.escape(k)}\b", v, t)
    return t


def tts(text, voice, speed, out, cwd):
    args = ["--text-file", str(out.with_suffix(".txt"))] if text.startswith("-") else [text]
    if text.startswith("-"): out.with_suffix(".txt").write_text(text)
    r = subprocess.run(["npx", "-y", "hyperframes", "tts", *args, "-v", voice, "-s", f"{speed:.3f}", "-o", str(out), "--json"],
                       capture_output=True, text=True, env=ENV, cwd=cwd)
    try: js = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception: js = {}
    if not js.get("ok"): sys.exit(f"tts failed for {out.name}: {r.stdout[-500:]}{r.stderr[-500:]}")
    return js["durationSeconds"]


def probe(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
                                capture_output=True, text=True).stdout)


def loudness(f):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(f), "-af",
                        "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True)
    js = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    return float(js["input_i"]), float(js["input_tp"])


def silence(aud, d):
    f = aud / f"_sil_{int(round(d * 1000))}.wav"
    if not f.exists():
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
                        "-t", f"{d:.3f}", str(f)], check=True)
    return f


def stitch(parts, aud, out):
    (aud / "list.txt").write_text("".join(f"file '{p}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(aud / "list.txt"),
                    "-ar", "48000", str(out)], check=True)


def line_voice(it, s):
    if not it["speaker"]: return s["voice"], s["speed"]
    c = s["cast"].get(it["speaker"])
    if not c: sys.exit(f"{it['id']}: speaker [{it['speaker']}] is not in `cast` of audio/voice.json")
    return c.get("voice", s["voice"]), c.get("speed", s["speed"])


def audition(a, s, items, root, pron):
    voices = a.voices.split(",") if a.voices else s["voices"]
    sample = [it for it in items if not it["speaker"]][:a.lines]
    out = root / "audio/audition"; out.mkdir(parents=True, exist_ok=True)
    gap = silence(out, s["line_gap"])
    print(f"persona {s['persona']} · speed {s['speed']} · {len(sample)} lines: " + " / ".join(it["id"] for it in sample))
    for v in voices:
        files, speech = [], 0.0
        for it in sample:
            f = out / f"{v}_{it['id']}.wav"
            speech += tts(tts_text(it["text"], pron), v, s["speed"], f, root)
            files += [f, gap]
        stitch(files[:-1], out, out / f"{v}.wav")
        nw = sum(len(words(it["text"])) for it in sample)
        print(f"  {v:12s} {speech:5.1f}s  {nw / speech:.2f} words/s  -> audio/audition/{v}.wav")
    print("Pick one, then set it in audio/voice.json: {\"persona\": \"%s\", \"voice\": \"<id>\"}" % s["persona"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default="."); ap.add_argument("--persona"); ap.add_argument("--voice")
    ap.add_argument("--speed", type=float); ap.add_argument("--lead-in", dest="lead_in", type=float)
    ap.add_argument("--only"); ap.add_argument("--force", action="store_true"); ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--audition", action="store_true"); ap.add_argument("--voices"); ap.add_argument("--lines", type=int, default=3)
    a = ap.parse_args()
    root = Path(a.project).resolve(); aud = root / "audio"; vdir = aud / "voice"
    vdir.mkdir(parents=True, exist_ok=True)
    pf = aud / "pronounce.json"; pron = json.loads(pf.read_text()) if pf.exists() else {}
    s = load_settings(a, root)
    pre, items, errors = parse_script(root / "script.md")
    if errors: sys.exit("script.md:\n  " + "\n  ".join(errors))
    if not items: sys.exit("script.md has no `sNN_lNN: text` lines")
    if a.audition: return audition(a, s, items, root, pron)

    # 1. generate changed lines (cache keyed on what Kokoro hears + voice + speed + drop)
    cf = vdir / ".cache.json"; cache = json.loads(cf.read_text()) if cf.exists() else {}
    only = set(a.only.split(",")) if a.only else None
    jobs = []
    for it in items:
        voice, speed = line_voice(it, s)
        drop = any(c["kind"] == "drop" for c in it["before"])
        text = tts_text(it["text"], pron)
        if drop: speed = round(speed * DROP_SPEED, 3)
        key = hashlib.sha1(json.dumps([text, voice, speed, drop, LINE_LUFS]).encode()).hexdigest()
        f = vdir / f"{it['id']}.wav"
        wanted = only is None or it["id"] in only
        if not f.exists() or (wanted and (a.force or cache.get(it["id"]) != key)):
            jobs.append((it["id"], text, voice, speed, drop, key, f))

    def gen(job):
        lid, text, voice, speed, drop, key, f = job
        d = tts(text, voice, speed, f, root)
        # level every line to the same loudness (voices and lines differ by a few dB), then apply the drop on top
        i, _ = loudness(f)
        g = (LINE_LUFS - i if -60 < i < 0 else 0.0) + (DROP_DB if drop else 0.0)
        if abs(g) >= 0.05:
            tmp = f.with_name(f"_{f.name}")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(f), "-af", f"volume={g:.2f}dB", str(tmp)], check=True)
            tmp.replace(f)
        print(f"{lid} {d:.2f}s {voice}{' (drop)' if drop else ''}", flush=True)
        return lid, key

    with ThreadPoolExecutor(a.jobs) as ex:
        for lid, key in ex.map(gen, jobs): cache[lid] = key
    cf.write_text(json.dumps(cache, indent=1))
    if not jobs: print("all lines up to date (use --force to regenerate)")

    # 2. timeline: measure every file, place gaps, beats and cue events
    beat, inh = s["beat"], s["inhale"]
    t = s["lead_in"] + beat * sum(c["kind"] == "beat" for c in pre)
    parts, lines, cues, prev, prev_end = [], [], [], None, 0.0
    sil = lambda d: parts.append(silence(aud, d)) if d >= 0.001 else None
    sil(t)
    for it in items:
        if prev is not None:
            gap = s["scene_gap"] if it["scene"] != prev["scene"] else s["line_gap"]
            beats = [c for c in prev["after"] + it["before"] if c["kind"] == "beat"]
            if beats:
                gap = max(gap, beat * len(beats))
                cues.append({"type": "beat", "t": round(prev_end, 3), "dur": round(gap, 3), "after": prev["id"],
                             "action": "; ".join(c["arg"] for c in beats if c["arg"]) or None})
            sil(gap); t = prev_end + gap
        kinds = {c["kind"] for c in it["before"]}
        if "inhale" in kinds:
            cues.append({"type": "breath", "t": round(t, 3), "dur": inh, "line": it["id"]})
            sil(inh); t += inh
        f = vdir / f"{it['id']}.wav"; dur = probe(f); end = t + dur
        for k in ("dry", "anchor", "drop"):
            if k in kinds: cues.append({"type": k, "t": round(t, 3), "end": round(end, 3), "line": it["id"]})
        voice, _ = line_voice(it, s)
        lines.append({"id": it["id"], "scene": it["scene"], "speaker": it["speaker"] or "NARRATOR", "voice": voice,
                      "start": round(t, 3), "end": round(end, 3), "dur": round(dur, 3), "text": it["text"],
                      "words": len(words(it["text"]))})
        parts.append(f); prev, prev_end, t = it, end, end
    tail = s["tail"]
    tb = [c for c in prev["after"] if c["kind"] == "beat"]
    if tb:
        tail = max(tail, beat * len(tb))
        cues.append({"type": "beat", "t": round(prev_end, 3), "dur": round(tail, 3), "after": prev["id"],
                     "action": "; ".join(c["arg"] for c in tb if c["arg"]) or None})
    sil(tail); total = prev_end + tail
    speech = sum(l["dur"] for l in lines); nw = sum(l["words"] for l in lines)

    out = {"persona": s["persona"], "voice": s["voice"], "speed": s["speed"], "wps": round(nw / speech, 3),
           **{k: s[k] for k in ("lead_in", "line_gap", "scene_gap", "beat", "inhale")}, "tail": tail,
           "fx_chain": s["fx_chain"], "cast": s["cast"], "total": round(total, 3), "lines": lines,
           "cues": sorted(cues, key=lambda c: c["t"])}
    (aud / "voice_timing.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))

    # 3. stitch + static loudness: one gain to -16 LUFS, then a limiter for peaks (no dynamic levelling).
    # narration_norm.wav is stereo (dual mono) and measured as stereo: a mono file plays on both channels of the
    # render and reads ~3 LU louder there, so normalising the mono file would overshoot the mix by 3 dB.
    stitch(parts, aud, aud / "narration.wav")
    i_in, _ = loudness(aud / "narration.wav")
    gain = TARGET_LUFS - (i_in + 3.01)
    for _ in range(3):  # the limiter shaves a little loudness; nudge the one static gain until it lands
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(aud / "narration.wav"), "-af",
                        f"volume={gain:.2f}dB,alimiter=limit={LIMIT}:attack=5:release=50:level=false:latency=1",
                        "-ar", "48000", "-ac", "2", str(aud / "narration_norm.wav")], check=True)
        i_out, tp_out = loudness(aud / "narration_norm.wav")
        if abs(TARGET_LUFS - i_out) < 0.3: break
        gain += TARGET_LUFS - i_out
    dry = sum(c["type"] == "dry" for c in cues); nb = sum(c["type"] == "beat" for c in cues)
    print(f"total {total:.1f}s · {len(lines)} lines · {nw} words · {nw / speech:.2f} words/s measured "
          f"({s['persona']}, {s['voice']} @ {s['speed']}) · {nb} beats, {dry} dry")
    print(f"narration_norm.wav {i_out:.1f} LUFS, true peak {tp_out:.1f} dBTP (from {i_in:.1f} LUFS)")


if __name__ == "__main__":
    main()
