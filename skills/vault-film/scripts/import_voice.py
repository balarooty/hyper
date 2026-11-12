#!/usr/bin/env python3
"""Bring a narration that already exists into a vault-film project, with the same files voice.py writes.

usage: python3 ~/.claude/skills/vault-film/scripts/import_voice.py --project <film dir> --takes <dir with takes.json>
         [--cues cues.json] [--gap 0.20] [--tail 2.8] [--script <verbatim script.md to compare against>]

Supported now: ElevenLabs takes, as saved by a with-timestamps request:
  <takes>/takes.json     [{"section": 0, "lines": ["…", "…"]}, …]   one entry per take, in film order
  <takes>/takes/N.mp3    the audio of take N
  <takes>/takes/N.json   {"characters": […], "characterStartTimesSeconds": […], "characterEndTimesSeconds": […]}
                         for "\\n".join(lines) of take N
Takes are stitched with --gap seconds after each (then rounded up to a frame), --tail after the last.

Writes (never touching the recording's wording or timing):
  script.md                    the lines verbatim as `sNN_lNN: text` (section -> scene), no cue marks added
  audio/voice_timing.json      lines (id, scene, start, end, dur, text, words) and cues, as voice.py writes them
  audio/narration.wav          the stitched voice, 48 kHz mono
  audio/narration_norm.wav     one static gain to -16 LUFS integrated, stereo, peaks limited to -1.5 dBFS
Cues come from --cues, a JSON list matched to lines by their exact text:
  [{"line": "I quit for seven days.", "type": "beat", "action": "seven-day milestone"},
   {"line": "And start living as someone who has already quit.", "type": "dry"},
   {"line": "Don't just quit the habit. …", "type": "anchor"}]
  beat = the pause after that line (to the next line's start); dry / anchor / drop = the line itself.
--script: checks that the imported words equal the words of a script you supplied, and stops if not.
"""
import argparse, json, math, re, subprocess, sys
from pathlib import Path

FPS, RATE = 30, 48000
words = lambda s: re.findall(r"[A-Za-z']+|\d+", s)

def run(*a):
    r = subprocess.run([str(x) for x in a], capture_output=True)
    if r.returncode: sys.exit(f"{a[0]} failed: {r.stderr.decode()[-400:]}")
    return r

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default="."); ap.add_argument("--takes", required=True); ap.add_argument("--cues")
    ap.add_argument("--gap", type=float, default=0.20); ap.add_argument("--tail", type=float, default=2.8); ap.add_argument("--script")
    a = ap.parse_args()
    root, src = Path(a.project).resolve(), Path(a.takes).resolve()
    takes = json.loads((src / "takes.json").read_text())
    aud = root / "audio"; aud.mkdir(parents=True, exist_ok=True)

    lines, pcm, clock, count = [], bytearray(), 0.0, {}
    for i, take in enumerate(takes):
        al = json.loads((src / "takes" / f"{i}.json").read_text())
        text = "\n".join(take["lines"])
        if "".join(al["characters"]) != text: sys.exit(f"take {i}: alignment characters do not match its lines")
        snd = run("ffmpeg", "-v", "error", "-i", src / "takes" / f"{i}.mp3", "-ar", RATE, "-ac", 1, "-f", "s16le", "-").stdout
        scene = f"s{take['section'] + 1:02d}"; ch = 0
        for ln in take["lines"]:
            count[scene] = count.get(scene, 0) + 1
            st = clock + al["characterStartTimesSeconds"][ch]; en = clock + al["characterEndTimesSeconds"][ch + len(ln) - 1]
            lines.append({"id": f"{scene}_l{count[scene]:02d}", "scene": scene, "speaker": "NARRATOR", "voice": "imported",
                          "start": round(st, 3), "end": round(en, 3), "dur": round(en - st, 3), "text": ln, "words": len(words(ln))})
            ch += len(ln) + 1
        pcm.extend(snd)
        end = clock + len(snd) / (2 * RATE)
        fend = math.ceil((end + (a.tail if i == len(takes) - 1 else a.gap)) * FPS)
        pcm.extend(bytes(2 * (fend * (RATE // FPS) - len(pcm) // 2)))
        clock = fend / FPS
    total = round(clock, 3)

    if a.script:
        theirs = [w.lower() for w in words(re.sub(r"^#.*$", "", Path(a.script).read_text(), flags=re.M))]
        ours = [w.lower() for l in lines for w in words(l["text"])]
        if theirs != ours:
            k = next((j for j, (x, y) in enumerate(zip(theirs, ours)) if x != y), min(len(theirs), len(ours)))
            sys.exit(f"words differ from {a.script} at word {k}: script {theirs[k:k + 6]} vs takes {ours[k:k + 6]}")
        print(f"words match {a.script}: {len(ours)} words")

    cues = []
    by_text = {l["text"]: (j, l) for j, l in enumerate(lines)}
    for c in json.loads(Path(a.cues).read_text()) if a.cues else []:
        if c["line"] not in by_text: sys.exit(f"cue line not found verbatim: {c['line']!r}")
        j, l = by_text[c["line"]]
        if c["type"] == "beat":
            nxt = lines[j + 1]["start"] if j + 1 < len(lines) else total
            cues.append({"type": "beat", "t": l["end"], "dur": round(nxt - l["end"], 3), "after": l["id"], "action": c.get("action")})
        else:
            cues.append({"type": c["type"], "t": l["start"], "end": l["end"], "line": l["id"]})
    if sum(c["type"] == "dry" for c in cues) > 1: sys.exit("more than one dry cue")

    sp = sum(l["dur"] for l in lines); nw = sum(l["words"] for l in lines)
    out = {"persona": "imported", "voice": "imported", "speed": 1.0, "wps": round(nw / sp, 3), "source": str(src),
           "total": total, "fx_chain": [], "cast": {}, "lines": lines, "cues": sorted(cues, key=lambda c: c["t"])}
    (aud / "voice_timing.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))

    md, cur = [f"# Script (imported verbatim from {src.name}; ids only, no words changed)", ""], None
    for l in lines:
        if l["scene"] != cur: cur = l["scene"]; md += ["", f"## {cur}"]
        md.append(f"{l['id']}: {l['text']}")
    (root / "script.md").write_text("\n".join(md) + "\n")

    raw = aud / "narration.wav"
    p = subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(RATE), "-ac", "1", "-i", "-", str(raw)], input=bytes(pcm), capture_output=True)
    if p.returncode: sys.exit(p.stderr.decode()[-400:])
    st = run("ffmpeg", "-hide_banner", "-nostats", "-i", raw, "-filter_complex", "[0]pan=stereo|c0=c0|c1=c0,ebur128", "-f", "null", "-").stderr.decode()
    lufs = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", st)[-1])
    run("ffmpeg", "-v", "error", "-y", "-i", raw, "-af", f"pan=stereo|c0=c0|c1=c0,volume={-16 - lufs:.2f}dB,alimiter=limit=0.841:level=disabled", aud / "narration_norm.wav")
    print(f"{len(lines)} lines in {len(count)} scenes · {total:.2f}s · {nw} words · {nw / sp:.2f} words/s · {len(cues)} cues · narration {lufs:.1f} -> -16 LUFS")

if __name__ == "__main__":
    main()
