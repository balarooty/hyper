#!/usr/bin/env python3
"""Local prompt + upload page for ChatGPT-made art. Stdlib only, binds to 127.0.0.1.

usage: python3 ~/.claude/skills/vault-film/scripts/art_server.py [--project <episode dir>] [--port 8765]
       then open http://127.0.0.1:8765  (needs art/prompts.json from plan.py)
Each card: copy the prompt -> generate in ChatGPT -> drop, choose, or paste (Cmd+V) the image.
Images are saved as art/<id>.<ext>; uploading again replaces the old one.
"""
import argparse, html, json, re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = ART = None  # set in main from --project
EXT = {b"\x89PNG": ".png", b"\xff\xd8\xff": ".jpg", b"RIFF": ".webp"}

def existing(i):
    for e in (".png", ".jpg", ".webp"):
        if (ART / f"{i}{e}").exists(): return f"{i}{e}"
    return None

def title():
    try:
        t = json.loads((ROOT / "shots.json").read_text()).get("title")
        if t: return t
    except Exception: pass
    b = ROOT / "brief.md"
    if b.exists():
        m = re.search(r"^#\s+(?:Brief\s*[—:-]\s*)?(.+?)(?:\s*\(.*\))?\s*$", b.read_text(), re.M)
        if m: return m.group(1)
    return ROOT.name

def page():
    d = json.loads((ART / "prompts.json").read_text())
    T = html.escape(title())
    portrait = d.get("aspect") == "9:16"
    ar, orient, colw = ("9/16", "portrait 9:16", "260px") if portrait else ("16/9", "landscape", "340px")
    cards = []
    for s in d["shots"]:
        f = existing(s["id"])
        img = f'<img src="/art/{f}?v={(ART/f).stat().st_mtime_ns}">' if f else '<span>drop / paste / click</span>'
        cards.append(f'''<section class="card{' done' if f else ''}" data-id="{s['id']}" tabindex="0">
 <header><b>{s['id']}</b><em>{s['dur']:.0f}s · {html.escape(s.get('era', ''))}</em><button class="copy">Copy prompt</button></header>
 <p class="vo">{('“' + html.escape(s['words']) + '”') if s['words'] else '(no narration)'}</p>
 <details><summary>prompt</summary><pre>{html.escape(s['prompt'])}</pre></details>
 <label class="slot">{img}<input type="file" accept="image/*" hidden></label>
</section>''')
    n = sum(1 for s in d["shots"] if existing(s["id"]))
    return f'''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{T} · art board</title>
<style>
:root{{--bg:#111;--card:#1c1c1c;--fg:#eee;--mut:#999;--red:#d4141c;--ok:#2e8b57}}
body{{margin:0;background:var(--bg);color:var(--fg);font:14px/1.45 system-ui,sans-serif}}
.top{{position:sticky;top:0;z-index:2;background:#000c;backdrop-filter:blur(6px);padding:12px 16px;display:flex;gap:16px;align-items:center;flex-wrap:wrap}}
.top h1{{font-size:16px;margin:0}} .bar{{flex:1;min-width:160px;height:8px;background:#333;border-radius:4px}} .bar i{{display:block;height:100%;background:var(--red);border-radius:4px;width:{n*100/len(d['shots']):.1f}%}}
.tip{{color:var(--mut);padding:0 16px;max-width:1100px}}
main{{display:grid;grid-template-columns:repeat(auto-fill,minmax({colw},1fr));gap:14px;padding:16px}}
.card{{background:var(--card);border:2px solid #2a2a2a;border-radius:10px;padding:10px;outline:none}}
.card:focus,.card.sel{{border-color:var(--red)}} .card.done{{border-left:6px solid var(--ok)}}
header{{display:flex;gap:8px;align-items:center}} header em{{color:var(--mut);font-style:normal;flex:1}}
button{{background:var(--red);color:#fff;border:0;border-radius:6px;padding:6px 10px;cursor:pointer}} button.ok{{background:var(--ok)}}
.vo{{color:#ccc;font-style:italic;margin:6px 0}} pre{{white-space:pre-wrap;font-size:12px;color:#bbb}}
.slot{{display:flex;align-items:center;justify-content:center;aspect-ratio:{ar};background:#0b0b0b;border:2px dashed #444;border-radius:8px;cursor:pointer;overflow:hidden;color:var(--mut)}}
.slot img{{width:100%;height:100%;object-fit:cover}} .slot.over{{border-color:var(--red)}}
</style>
<div class="top"><h1>{T} · art board</h1><span id="count">{n} / {len(d['shots'])} images</span><div class="bar"><i></i></div></div>
<p class="tip">Do every image in <b>one ChatGPT conversation</b> ({orient}). Click a card, press <b>Copy prompt</b>, paste into ChatGPT, then copy the image and press <b>Cmd+V</b> here (or drag the file onto the card, or click the slot). The next empty card is selected automatically. Uploading again replaces an image.</p>
<main>{''.join(cards)}</main>
<script>
let sel=document.querySelector('.card:not(.done)')||document.querySelector('.card');
function pick(c){{document.querySelectorAll('.card').forEach(x=>x.classList.remove('sel'));sel=c;c.classList.add('sel');}}
pick(sel);
async function up(card,file){{
  const r=await fetch('/upload/'+card.dataset.id,{{method:'POST',body:file}});const j=await r.json();
  if(!j.ok){{alert(j.error);return}}
  card.querySelector('.slot').innerHTML='<img src="/art/'+j.file+'?v='+Date.now()+'">';card.classList.add('done');
  document.getElementById('count').textContent=j.count;
  const nx=[...document.querySelectorAll('.card:not(.done)')][0]; if(nx){{pick(nx);nx.scrollIntoView({{behavior:'smooth',block:'center'}})}}
}}
document.querySelectorAll('.card').forEach(c=>{{
  c.addEventListener('click',()=>pick(c));
  c.querySelector('.copy').onclick=async e=>{{e.stopPropagation();pick(c);await navigator.clipboard.writeText(c.querySelector('pre').textContent);e.target.textContent='Copied';e.target.classList.add('ok');}};
  const s=c.querySelector('.slot'),inp=s.querySelector('input');
  inp.onchange=()=>inp.files[0]&&up(c,inp.files[0]);
  s.ondragover=e=>{{e.preventDefault();s.classList.add('over')}}; s.ondragleave=()=>s.classList.remove('over');
  s.ondrop=e=>{{e.preventDefault();s.classList.remove('over');const f=e.dataTransfer.files[0];f&&up(c,f)}};
}});
document.addEventListener('paste',e=>{{const it=[...e.clipboardData.items].find(i=>i.type.startsWith('image/'));if(it&&sel){{e.preventDefault();up(sel,it.getAsFile())}}}});
</script>'''

class H(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype):
        self.send_response(code); self.send_header("Content-Type", ctype); self.send_header("Cache-Control", "no-store")
        self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        p = self.path.split("?")[0]
        if p == "/": return self._send(200, page().encode(), "text/html; charset=utf-8")
        m = re.fullmatch(r"/art/(\d{2}\.(png|jpg|webp))", p)
        if m and (ART / m.group(1)).exists():
            return self._send(200, (ART / m.group(1)).read_bytes(), {"png": "image/png", "jpg": "image/jpeg", "webp": "image/webp"}[m.group(2)])
        self._send(404, b"not found", "text/plain")
    def do_POST(self):
        m = re.fullmatch(r"/upload/(\d{2})", self.path)
        n = int(self.headers.get("Content-Length", 0))
        data = self.rfile.read(n) if n < 60_000_000 else b""
        ext = next((e for sig, e in EXT.items() if data.startswith(sig)), None)
        if not m or not ext:
            return self._send(400, json.dumps({"ok": False, "error": "send a PNG, JPEG or WebP image"}).encode(), "application/json")
        i = m.group(1)
        for e in (".png", ".jpg", ".webp"): (ART / f"{i}{e}").unlink(missing_ok=True)
        (ART / f"{i}{ext}").write_bytes(data)
        total = len(json.loads((ART / "prompts.json").read_text())["shots"])
        done = sum(1 for f in ART.iterdir() if re.fullmatch(r"\d{2}\.(png|jpg|webp)", f.name))
        print(f"saved art/{i}{ext} ({len(data)//1024} KB) · {done}/{total}", flush=True)
        self._send(200, json.dumps({"ok": True, "file": f"{i}{ext}", "count": f"{done} / {total} images"}).encode(), "application/json")
    def log_message(self, *a): pass

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--port", type=int, default=8765); ap.add_argument("--project", default=".")
    a = ap.parse_args()
    ROOT = Path(a.project).resolve(); ART = ROOT / "art"
    if not (ART / "prompts.json").exists(): raise SystemExit(f"{ART/'prompts.json'} missing: run plan.py --project {ROOT} first")
    print(f"art board: http://127.0.0.1:{a.port}  (Ctrl+C to stop)", flush=True)
    ThreadingHTTPServer(("127.0.0.1", a.port), H).serve_forever()
