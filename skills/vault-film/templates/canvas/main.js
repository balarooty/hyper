// One canvas chapter of a vault-film, on the Lemo-Opuscar page contract: the picture is a function of time.
// Render from the library:  cd ~/lemo-opuscar && node core/render/video.mjs <this folder> --fps <fps> --size <WxH> --out <film>/build/out/<id>.mp4
// chapter.json (scripts/timeline.py) gives the frames; read voice timing from CH.shots / CH.lines / CH.cues, never type it.
// Deterministic: no Date.now(), no unseeded Math.random() (mulberry / hash from /core/lib.js), no state kept between frames.
// No audio here: scripts/mix.py owns the sound. List sound moments in window.EV so they can go into audio/events.json.
import { clamp, lerp, seg, ss, eio, eo } from '/core/lib.js';

const CH = await (await fetch('chapter.json')).json();
const W = innerWidth, H = innerHeight, S = Math.min(W, H) / 1080;   // S: 1 at 1080 px on the short side
const cv = document.getElementById('c'); cv.width = W; cv.height = H;
const g = cv.getContext('2d');
const P = { bg: '#1E2126', ink: '#ECE7DF', accent: '#E3A857', accent2: '#6C8EBF', alert: '#C0392B', muted: '#7C8088', ...(CH.look.palette || {}) };
const FONTS = { display: { family: 'Inter', weights: [700] }, body: { family: 'Inter', weights: [400, 700] }, ...(CH.look.fonts || {}) };
const CAP = CH.look.caption || {};

// the look's fonts, copied into ./fonts by new_film.py (the same files every engine of the film uses)
const slug = f => f.toLowerCase().replace(/\s+/g, '-');
await Promise.all(Object.values(FONTS).filter(Boolean).flatMap(r => r.weights.map(async w => {
  const f = new FontFace(r.family, `url(fonts/${slug(r.family)}-${w}.woff2)`, { weight: String(w) });
  document.fonts.add(await f.load());
})));
const font = (role, px, weight) => `${weight || FONTS[role].weights.at(-1)} ${px * S}px "${FONTS[role].family}"`;

window.DUR = CH.frames / CH.fps;   // exactly the chapter's frame count at CH.fps
const shotAt = t => CH.shots.findLast(s => t >= s.start) || CH.shots[0];
export const cue = (type, nth = 0) => CH.cues.filter(c => c.type === type)[nth];   // {t, frame, action}: land the action on it

// ---- captions (sentence pages from the voice lines, in the look's caption style) ----
const PAGES = CH.lines.flatMap(l => {
  const words = l.text.split(/\s+/).filter(Boolean), n = Math.ceil(words.length / 8), per = Math.ceil(words.length / n);
  return [...Array(n)].map((_, k) => { const a = k * per, b = Math.min(words.length, a + per);
    return { id: `${l.id}.${k}`, text: words.slice(a, b).join(' '), t0: lerp(l.start, l.end, a / words.length), t1: lerp(l.start, l.end, b / words.length) }; });
});
const capOn = (CAP.style || 'none') !== 'none';
const capBox = () => { const y = CAP.position === 'upper' ? H * 0.12 : CAP.position === 'center' ? H * 0.5 : H * 0.86; return { y, size: (CAP.size || 46) }; };

// ---- shots: replace drawStub with real drawing, one function per shot id ----
const DRAW = {
  // '01': (u, t, shot) => { ... }   // u: 0→1 through the shot, t: chapter seconds
};
function drawStub(u, t, shot) {
  g.textAlign = 'center'; g.textBaseline = 'middle';
  g.fillStyle = P.alert; g.font = font('body', 34, 700);
  g.fillText(`PLACEHOLDER · shot ${shot.id} · ${shot.end_f - shot.start_f} f`, W / 2, H * 0.38);
  g.fillStyle = P.ink; g.font = font('body', 44, 400);
  wrap(shot.draw || shot.overlay || shot.words || '', W * 0.8).forEach((ln, i) => g.fillText(ln, W / 2, H * 0.48 + i * 58 * S));
  g.fillStyle = P.muted; g.font = font('body', 28, 400); g.fillText(shot.move || '', W / 2, H * 0.72);
}
function wrap(text, maxW) {
  const out = []; let cur = '';
  for (const w of text.split(/\s+/)) { const tryl = cur ? cur + ' ' + w : w; if (g.measureText(tryl).width > maxW && cur) { out.push(cur); cur = w; } else cur = tryl; }
  if (cur) out.push(cur); return out.slice(0, 4);
}

window.render = (t) => {
  t = clamp(t, 0, window.DUR);
  g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1;
  g.fillStyle = P.bg; g.fillRect(0, 0, W, H);
  const shot = shotAt(t), u = seg(t, shot.start, shot.start + shot.dur);
  g.save();
  const z = 1 + 0.02 * u;   // every hold creeps: a slow push-in, never a frozen frame
  g.translate(W / 2, H / 2); g.scale(z, z); g.translate(-W / 2, -H / 2);
  (DRAW[shot.id] || drawStub)(u, t, shot);
  g.restore();
  if (capOn) { const p = PAGES.findLast(p => t >= p.t0 && t < p.t1 + 0.2); if (p) { const b = capBox();
    g.textAlign = 'center'; g.textBaseline = 'middle'; g.font = font('body', b.size, 700); g.lineJoin = 'round';
    g.lineWidth = 10 * S; g.strokeStyle = P.bg; g.strokeText(p.text, W / 2, b.y); g.fillStyle = P.ink; g.fillText(p.text, W / 2, b.y); } }
};

// every text on screen at t, with its box, for lemo's readcheck.mjs (captions are checked by their .srt instead)
window.TEXTS = (t) => [];
// sound moments for the mix: [{t, type}] in chapter seconds; copy them into audio/events.json with "chapter": CH.id
window.EV = [];
window.READY = true;
