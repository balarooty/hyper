// 10-second look samples for the vault-film prompt guide: one scene per style name, chosen with ?style=<name>.
// Lemo-Opuscar page contract (window.DUR / render(t) / READY). Deterministic: every frame is a function of t.
// These are previews of each style's LOOK, all drawn on the canvas engine; a real film is built on the style's own engine.
const W = 1920, H = 1080, DUR = 10;
const cv = document.getElementById('c'); cv.width = W; cv.height = H;
const g = cv.getContext('2d');
const STYLE = new URLSearchParams(location.search).get('style') || 'schematic-explainer';
const TAU = Math.PI * 2;
const cl = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, t) => a + (b - a) * t;
const seg = (t, a, b) => cl((t - a) / (b - a));
const ss = t => t * t * (3 - 2 * t);
const eo = t => 1 - Math.pow(1 - t, 3);
const eio = t => (t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
const rnd = i => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
const twos = t => Math.floor(t * 12) / 12;   // hold poses on twos (12 fps) while the camera stays smooth

await Promise.all([['Anton', 400, 'anton-400'], ['Inter', 400, 'inter-400'], ['Inter', 700, 'inter-700'], ['JetBrains Mono', 700, 'jetbrains-mono-700'],
  ['Cormorant Garamond', 700, 'cormorant-garamond-700'], ['Fredoka', 700, 'fredoka-700']].map(async ([f, w, file]) => {
  const ff = new FontFace(f, `url(fonts/${file}.woff2)`, { weight: String(w) }); document.fonts.add(await ff.load());
}));

// ---------- drawing helpers ----------
const font = (px, fam = 'Inter', w = 700) => { g.font = `${w} ${px}px "${fam}"`; };
function txt(s, x, y, col, al = 'center', a = 1) { g.save(); g.globalAlpha *= a; g.fillStyle = col; g.textAlign = al; g.textBaseline = 'middle'; g.fillText(s, x, y); g.restore(); }
function typed(s, x, y, col, p, al = 'left') { txt(s.slice(0, Math.round(s.length * cl(p))), x, y, col, al); }
function poly(pts, p = 1, close = false) {
  const L = []; let tot = 0;
  for (let i = 1; i < pts.length; i++) { const d = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); L.push(d); tot += d; }
  let rem = tot * cl(p); if (rem <= 0) return;
  g.beginPath(); g.moveTo(pts[0][0], pts[0][1]);
  for (let i = 1; i < pts.length && rem > 0; i++) {
    const d = L[i - 1];
    if (rem >= d) { g.lineTo(pts[i][0], pts[i][1]); rem -= d; }
    else { const k = rem / d; g.lineTo(lerp(pts[i - 1][0], pts[i][0], k), lerp(pts[i - 1][1], pts[i][1], k)); rem = 0; }
  }
  if (close && p >= 1) g.closePath(); g.stroke();
}
function circ(x, y, r, fill, stroke, lw = 4) { g.beginPath(); g.arc(x, y, Math.max(0, r), 0, TAU); if (fill) { g.fillStyle = fill; g.fill(); } if (stroke) { g.strokeStyle = stroke; g.lineWidth = lw; g.stroke(); } }
function arc(x, y, r, a0, a1, col, lw) { if (a1 <= a0) return; g.beginPath(); g.arc(x, y, r, a0, a1); g.strokeStyle = col; g.lineWidth = lw; g.stroke(); }
function rr(x, y, w, h, r, fill, stroke, lw = 4) { g.beginPath(); g.roundRect(x, y, w, h, r); if (fill) { g.fillStyle = fill; g.fill(); } if (stroke) { g.strokeStyle = stroke; g.lineWidth = lw; g.stroke(); } }
function stroke(col, lw) { g.strokeStyle = col; g.lineWidth = lw; g.lineCap = 'round'; g.lineJoin = 'round'; }
function cam(z, cx, cy, fn) { g.save(); g.translate(W / 2, H / 2); g.scale(z, z); g.translate(-cx, -cy); fn(); g.restore(); }
function grad(x0, y0, x1, y1, stops) { const q = g.createLinearGradient(x0, y0, x1, y1); stops.forEach(([o, c]) => q.addColorStop(o, c)); return q; }
function glow(x, y, r, col, a = 1) { const q = g.createRadialGradient(x, y, 0, x, y, r); q.addColorStop(0, col); q.addColorStop(1, 'rgba(0,0,0,0)'); g.save(); g.globalAlpha *= a; g.fillStyle = q; g.fillRect(x - r, y - r, r * 2, r * 2); g.restore(); }
function callout(x, y, lx, ly, s, col, p, fam = 'JetBrains Mono') {
  if (p <= 0) return; stroke(col, 3); circ(x, y, 8 * cl(p * 2), col);
  g.beginPath(); g.moveTo(x, y); g.lineTo(lerp(x, lx, cl(p * 1.5)), lerp(y, ly, cl(p * 1.5))); g.stroke();
  font(30, fam, 700); txt(s, lx + (lx < x ? -14 : 14), ly, col, lx < x ? 'right' : 'left', seg(p, .5, 1));
}
// stick figure: angles in radians from straight down; (x, y) is the feet
function stick(x, y, s, col, { a1 = .5, a2 = -.5, l1 = .25, l2 = -.25, lean = 0, lw = 9, hx = 0 } = {}) {
  g.save(); g.translate(x, y); g.scale(s, s); g.rotate(lean); stroke(col, lw);
  const hip = [0, -95], sh = [0, -190];
  g.beginPath(); g.moveTo(hip[0], hip[1]); g.lineTo(sh[0], sh[1]);
  for (const a of [l1, l2]) { g.moveTo(hip[0], hip[1]); g.lineTo(hip[0] + Math.sin(a) * 95, hip[1] + Math.cos(a) * 95); }
  for (const a of [a1, a2]) { g.moveTo(sh[0], sh[1] + 12); g.lineTo(sh[0] + Math.sin(a) * 80, sh[1] + 12 + Math.cos(a) * 80); }
  g.stroke(); circ(hx, -225, 30, null, col, lw); g.restore();
}
// bean-head cartoon: (x, y) is the feet
function bean(x, y, s, { skin = '#F3D9B1', shirt = '#3A7D5D', ink = '#241726', mood = 'flat', look = 0, arm = 0, walk = 0, hat = null, talk = 0 } = {}) {
  g.save(); g.translate(x, y - 150 * s); g.scale(s, s); stroke(ink, 8);
  const lg = Math.sin(walk) * 20;
  g.beginPath(); g.moveTo(-16, 60); g.lineTo(-16 - lg, 150); g.moveTo(16, 60); g.lineTo(16 + lg, 150); g.stroke();
  g.beginPath(); g.moveTo(-40, 0); g.lineTo(-80, 46); g.moveTo(40, 0); g.lineTo(80 - arm * 6, 46 - arm * 110); g.stroke();
  rr(-44, -30, 88, 100, 38, shirt, ink, 8);
  g.beginPath(); g.ellipse(0, -100, 76, 71, 0, 0, TAU); g.fillStyle = skin; g.fill(); g.stroke();
  if (hat) { rr(-62, -190, 124, 50, 8, hat, ink, 8); rr(-80, -146, 160, 14, 6, hat, ink, 8); }
  const ex = look * 10; g.fillStyle = ink;
  if (mood === 'wide') { circ(-26 + ex, -108, 11, ink); circ(26 + ex, -108, 11, ink); }
  else if (mood === 'happy') { stroke(ink, 7); arc(-26 + ex, -104, 13, Math.PI, TAU, ink, 7); arc(26 + ex, -104, 13, Math.PI, TAU, ink, 7); }
  else { g.beginPath(); g.moveTo(-40 + ex, -108); g.lineTo(-14 + ex, -108); g.moveTo(14 + ex, -108); g.lineTo(40 + ex, -108); stroke(ink, 8); g.stroke(); }
  if (mood === 'happy') arc(0, -84, 22, .15 * Math.PI, .85 * Math.PI, ink, 7);
  else { g.beginPath(); g.ellipse(ex * .4, -68, 9, 4 + 9 * talk, 0, 0, TAU); g.fillStyle = '#7A1E28'; g.fill(); stroke(ink, 5); g.stroke(); }
  g.restore();
}
function tag(name) {
  font(26, 'Inter', 700); const w = g.measureText(name).width + 36;
  g.save(); g.globalAlpha = .82; rr(36, H - 84, w, 48, 24, 'rgba(0,0,0,.62)'); g.restore(); txt(name, 54, H - 59, '#FFFFFF', 'left');
}
function grain(t, a = .05, n = 900) { g.save(); g.globalAlpha = a; const f = Math.floor(t * 30); for (let i = 0; i < n; i++) { g.fillStyle = rnd(i * 3 + f * 17) > .5 ? '#fff' : '#000'; g.fillRect(rnd(i + f * 31) * W, rnd(i * 7 + f * 13) * H, 3, 3); } g.restore(); }

// ---------- the styles ----------
const S = {};

S['schematic-explainer'] = t => {
  const C = { bg: '#0B0F17', ink: '#E6EDF3', cy: '#38BDF8', am: '#F59E0B', red: '#EF4444', mu: '#8B98A9' };
  g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
  for (let i = 0; i <= 32; i++) { stroke(C.mu, 1); g.globalAlpha = i % 4 ? .07 : .15; g.beginPath(); g.moveTo(i * 60, 0); g.lineTo(i * 60, H); g.moveTo(0, i * 60); g.lineTo(W, i * 60); g.stroke(); } g.globalAlpha = 1;
  if (t < 5) cam(lerp(1, 1.1, ss(seg(t, 0, 5))), 960, 560, () => {
    const cx = 960, cy = 580, R = 230, open = seg(t, 2.6, 3.4);
    g.save(); g.globalAlpha = lerp(1, .22, open); circ(cx, cy, R, '#111A28'); g.restore();
    arc(cx, cy, R, -Math.PI / 2, -Math.PI / 2 + TAU * eo(seg(t, .2, 1.5)), C.cy, 6);
    for (let i = 0; i < 6; i++) { const a = -Math.PI + i * Math.PI / 5, p = eo(seg(t, 1.2 + i * .12, 1.7 + i * .12)); stroke(i === 2 ? C.am : C.cy, 14); g.beginPath(); g.moveTo(cx + Math.cos(a) * R, cy + Math.sin(a) * R); g.lineTo(cx + Math.cos(a) * (R + 70 * p), cy + Math.sin(a) * (R + 70 * p)); g.stroke(); }
    stroke(C.mu, 5); g.setLineDash([14, 12]); poly([[cx, cy + R], [cx, cy + R + 200]], seg(t, 1.6, 2.2)); g.setLineDash([]);
    if (open > 0) { g.save(); g.globalAlpha = open; rr(cx - 70, cy - 20, 140, 110, 10, '#16263A', C.cy, 4); font(26, 'JetBrains Mono'); txt('BATTERY', cx, cy + 35, C.cy);
      for (let i = 0; i < 6; i++) { const a = -Math.PI + i * Math.PI / 5; stroke(i === 2 ? C.am : C.mu, 3); poly([[cx + Math.cos(a) * R, cy + Math.sin(a) * R], [cx + Math.cos(a) * 110, cy + Math.sin(a) * 110], [cx + (i - 2.5) * 20, cy - 20]], seg(t, 3 + i * .08, 3.6 + i * .08)); } g.restore(); }
    callout(cx + Math.cos(-.6 * Math.PI) * (R + 60), cy + Math.sin(-.6 * Math.PI) * (R + 60), 1340, 190, 'LEAD HORN', C.am, seg(t, 3.3, 3.9));
    callout(cx + 60, cy + 30, 1380, 640, 'DRY BATTERY', C.cy, seg(t, 3.8, 4.4));
    callout(cx, cy + R + 120, 560, 900, 'MOORING CABLE', C.mu, seg(t, 4.2, 4.8));
  });
  else cam(lerp(1, 1.08, ss(seg(t, 5, 10))), 960, 540, () => {
    const bend = eo(seg(t, 6.4, 7.0)) * .32, hit = seg(t, 5.2, 6.4);
    g.fillStyle = C.red; g.globalAlpha = .9; g.fillRect(lerp(2100, 1290, eo(hit)), 0, 900, H); g.globalAlpha = 1;
    font(34, 'JetBrains Mono'); txt('SHIP HULL', lerp(2300, 1500, eo(hit)), 120, '#fff', 'left');
    g.save(); g.translate(960, 760); g.rotate(-bend);
    g.globalAlpha = .25; rr(-110, -520, 220, 520, 100, '#9AA7B5'); g.globalAlpha = 1; rr(-110, -520, 220, 520, 100, null, C.am, 6);
    rr(-34, -420, 68, 260, 30, 'rgba(56,189,248,.15)', C.cy, 4);
    const lvl = lerp(200, 40, seg(t, 7, 8.2)); g.fillStyle = C.am; g.globalAlpha = .85; g.beginPath(); g.roundRect(-26, -170 - lvl, 52, lvl, 20); g.fill(); g.globalAlpha = 1;
    if (t > 6.8) { stroke(C.ink, 4); poly([[-30, -330], [-6, -300], [-20, -270], [10, -240], [-4, -205]], seg(t, 6.8, 7.2)); }
    g.restore();
    if (t > 7) { const d = seg(t, 7, 8.2); for (let i = 0; i < 5; i++) { const k = cl(d * 1.4 - i * .1); if (k > 0 && k < 1) circ(960 - 30 + i * 6, lerp(600, 880, k), 9, C.am); } }
    rr(820, 880, 120, 26, 4, C.cy); rr(980, 880, 120, 26, 4, C.cy); font(26, 'JetBrains Mono'); txt('ZINC', 880, 930, C.mu); txt('CARBON', 1040, 930, C.mu);
    const sp = seg(t, 8.2, 8.5); if (sp > 0) { glow(960, 893, 220 * (1 - sp * .5) + 60, 'rgba(245,158,11,.9)', 1 - seg(t, 8.5, 9.4) * .6); stroke('#fff', 5); for (let i = 0; i < 8; i++) { const a = i * TAU / 8 + .3; g.beginPath(); g.moveTo(960 + Math.cos(a) * 20, 893 + Math.sin(a) * 20); g.lineTo(960 + Math.cos(a) * (40 + 50 * sp), 893 + Math.sin(a) * (40 + 50 * sp)); g.stroke(); } }
    callout(960 - 100, 420, 420, 300, 'SOFT LEAD: BENDS', C.am, seg(t, 5.3, 5.9));
    callout(940, 560, 400, 620, 'GLASS VIAL OF ACID', C.cy, seg(t, 5.7, 6.3));
    if (t > 8.3) { font(88, 'Anton', 400); txt('CIRCUIT CLOSED', 470, 900, C.red, 'center', seg(t, 8.3, 8.6)); }
  });
  font(30, 'JetBrains Mono'); typed('CONTACT MINE · CROSS-SECTION', 70, 70, C.mu, seg(t, .1, 1.2));
};

S['continuous-canvas-explainer'] = t => {
  const C = { bg: '#5E2725', ink: '#F2E6DA', bad: '#FF7A6B', ok: '#8FD694', sh: '#271B29', blue: '#6396DE' };
  g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
  const panX = lerp(0, 900, eio(seg(t, 0, 10)));
  const track = (kind, n = 140) => { const pts = []; for (let i = 0; i <= n; i++) { const u = i / n; let x, y;
      if (u < .35) { x = u / .35 * 700; y = 0; }
      else { const v = (u - .35) / .65;
        if (kind === 'circle') { const a = v * Math.PI * 1.25; x = 700 + Math.sin(a) * 260; y = -260 + Math.cos(a) * 260; }
        else { let px = 700, py = 0, th = 0; const steps = Math.round(v * 80); for (let k = 0; k < steps; k++) { th += (k / 80) * .062; px += Math.cos(th) * 11; py -= Math.sin(th) * 11; } x = px; y = py; } }
      pts.push([x, y]); } return pts; };
  cam(1, 960, 540, () => {
    g.save(); g.translate(130 - seg(t, 6.3, 9.2) * 200, -90); g.scale(1.18, 1.18);
    const m = eio(seg(t, 4.6, 6.2)), A = track('circle'), B = track('spiral'), P = A.map((p, i) => [lerp(p[0], B[i][0], m) + 260, lerp(p[1], B[i][1], m) + 760]);
    stroke(C.sh, 26); poly(P, eo(seg(t, .2, 2.2))); stroke(C.ink, 6); g.setLineDash([4, 26]); poly(P, eo(seg(t, .2, 2.2))); g.setLineDash([]);
    stroke(C.ink, 5); poly(P, eo(seg(t, .2, 2.2)));
    const run = t < 4.6 ? seg(t, 2.2, 4.2) * .52 : seg(t, 6.3, 9.2), idx = Math.floor(cl(run) * (P.length - 2)), p0 = P[idx], p1 = P[idx + 1];
    const crash = t < 4.6 ? seg(t, 3.5, 3.8) : 0, ang = Math.atan2(p1[1] - p0[1], p1[0] - p0[0]);
    if (t > 2.2) { g.save(); g.translate(p0[0] + crash * 60, p0[1] - crash * 30); g.rotate(ang + crash * 1.1); rr(-70, -44, 140, 44, 10, C.blue, C.sh, 6); circ(-40, 0, 12, C.sh); circ(40, 0, 12, C.sh); g.restore(); }
    if (t > 2.9 && t < 4.6) { const k = seg(t, 2.9, 3.5); stroke(C.bad, 9); const bx = 960, by = 700; g.beginPath(); g.moveTo(bx, by); g.lineTo(bx + 190 * k, by + 40 * k); g.stroke(); font(44, 'Inter'); txt('sudden sideways force', bx - 330, by + 110, C.bad, 'left', k); }
    if (t > 3.6 && t < 4.8) { stroke(C.bad, 16); const k = seg(t, 3.6, 3.9), x = 1250, y = 330; g.beginPath(); g.moveTo(x - 60 * k, y - 60 * k); g.lineTo(x + 60 * k, y + 60 * k); g.moveTo(x + 60 * k, y - 60 * k); g.lineTo(x - 60 * k, y + 60 * k); g.stroke(); }
    if (t > 6.4) { const k = seg(t, 6.4, 7.2); stroke(C.ok, 7); for (let i = 0; i < 4; i++) { const q = P[60 + i * 18]; g.beginPath(); g.moveTo(q[0], q[1]); g.lineTo(q[0] + (20 + i * 16) * k, q[1] + (8 + i * 6) * k); g.stroke(); } font(44, 'Inter'); txt('force grows a little at a time', 640, 900, C.ok, 'left', k); }
    if (t > 8.6) { stroke(C.ok, 16); const k = eo(seg(t, 8.6, 9)); poly([[1500, 250], [1540, 295], [1620, 200]], k); }
    g.restore();
  });
  font(64, 'Inter'); txt(t < 4.6 ? 'a straight track meets a perfect circle' : 'so the curve tightens gradually', 110, 120, C.ink, 'left', t < 4.6 ? seg(t, .3, .9) * (1 - seg(t, 4.2, 4.6)) : seg(t, 4.9, 5.5));
};

S['bizarre-history-story'] = t => {
  const C = { sky: '#D5A05C', gnd: '#9C6126', dk: '#592B1A', ink: '#271818', paper: '#EAE4E1', red: '#C0392B' };
  const shot = t < 2 ? 0 : t < 3.6 ? 1 : t < 5.4 ? 2 : t < 7.4 ? 3 : 4, t0 = [0, 2, 3.6, 5.4, 7.4][shot], u = t - t0, push = 1 + u * .02;
  const scene = (far = 1) => { g.fillStyle = C.sky; g.fillRect(0, 0, W, H); circ(1520, 230, 110, '#F4DBA5'); g.fillStyle = C.dk; for (let i = 0; i < 9; i++) g.fillRect(i * 240 - 60, 520 - rnd(i) * 150, 200, 400); g.fillStyle = C.gnd; g.fillRect(0, 760, W, 320); stroke(C.ink, 6); g.beginPath(); g.moveTo(0, 760); g.lineTo(W, 760); g.stroke(); };
  const stop = (x, y, s) => { g.save(); g.translate(x, y); g.scale(s, s); stroke(C.ink, 8); g.beginPath(); g.moveTo(0, 0); g.lineTo(0, -430); g.stroke(); rr(-70, -520, 140, 100, 14, '#E8B93B', C.ink, 8); font(64, 'Fredoka'); txt('BUS', 0, -468, C.ink); rr(60, -150, 330, 26, 8, C.dk, C.ink, 8); g.beginPath(); g.moveTo(90, -124); g.lineTo(90, 0); g.moveTo(360, -124); g.lineTo(360, 0); g.stroke(); g.restore(); };
  if (shot === 0) cam(push * 1.25, 760, 520, () => { scene(); stop(620, 760, 1); bean(840, 700, 1.05, { shirt: '#6C8EBF', mood: 'flat', skin: '#E9CDA6', hat: '#7A6A58', look: 1 }); });
  if (shot === 1) cam(push * 2.4, 620, 300, () => { scene(); stop(620, 760, 1); font(40, 'Fredoka'); const k = eo(seg(u, .2, .5)); g.save(); g.translate(880, 250); g.scale(k, k); rr(-190, -60, 380, 120, 20, C.paper, C.ink, 7); txt('NO BUS EVER COMES', 0, 2, C.red); g.restore(); });
  if (shot === 2) cam(push, 960, 540, () => { scene(); stop(620, 760, 1); bean(840, 700, 1.05, { shirt: '#6C8EBF', skin: '#E9CDA6', hat: '#7A6A58', look: -1, mood: 'wide' }); bean(lerp(1900, 1120, eo(seg(u, 0, 1.1))), 760, 1.15, { shirt: '#F2F2F2', mood: 'happy', walk: u * 9, look: -1, arm: seg(u, 1.1, 1.5) }); });
  if (shot === 3) cam(push * 1.9, 960, 430, () => { scene(); bean(840, 760, 1.15, { shirt: '#6C8EBF', skin: '#E9CDA6', hat: '#7A6A58', look: 1, mood: u > .8 ? 'happy' : 'flat', talk: u < .8 ? Math.abs(Math.sin(u * 14)) : 0 }); bean(1100, 760, 1.15, { shirt: '#F2F2F2', mood: 'happy', look: -1, talk: u > .9 ? Math.abs(Math.sin(u * 14)) * .8 : 0 }); });
  if (shot === 4) cam(push * .95, 960, 540, () => { scene(); stop(620, 760, 1); const x = lerp(900, 1500, seg(u, 0, 2.6)); bean(x, 760, 1, { shirt: '#6C8EBF', skin: '#E9CDA6', hat: '#7A6A58', look: 1, mood: 'happy', walk: u * 8 }); bean(x + 190, 760, 1.05, { shirt: '#F2F2F2', mood: 'happy', look: -1, walk: u * 8 + 1 }); rr(1500, 300, 380, 460, 6, C.paper, C.ink, 8); rr(1640, 560, 100, 200, 6, C.dk, C.ink, 8); font(40, 'Fredoka'); txt('CARE HOME', 1690, 350, C.ink); });
  if (u < .1 && shot > 0) { g.fillStyle = '#fff'; g.globalAlpha = .5 * (1 - u / .1); g.fillRect(0, 0, W, H); g.globalAlpha = 1; }
  font(54, 'Fredoka'); const cap = ['He waits here every afternoon.', 'For a bus that does not exist.', 'A nurse walks over.', '"Shall we wait inside?"', 'The stop was built on purpose.'][shot];
  g.lineJoin = 'round'; g.lineWidth = 12; g.strokeStyle = C.ink; g.textAlign = 'center'; g.textBaseline = 'middle'; g.strokeText(cap, 960, 970); txt(cap, 960, 970, '#fff');
};

S['neon-dilemma'] = t => {
  const C = { bg: '#120C1A', cy: '#22E6FF', mg: '#FF3DCB', gold: '#FFD23F', gr: '#7CFF6B', mu: '#655062' };
  g.fillStyle = C.bg; g.fillRect(0, 0, W, H); glow(480, 620, 520, 'rgba(34,230,255,.10)'); glow(1440, 620, 520, 'rgba(255,61,203,.10)');
  stroke(C.mu, 3); g.setLineDash([10, 16]); g.beginPath(); g.moveTo(960, 150); g.lineTo(960, 1000); g.stroke(); g.setLineDash([]);
  const day = 1 + Math.floor(eio(seg(t, 1.2, 8.6)) * 29), sam = day * 800, mia = Math.pow(2, day - 1) / 100, neon = (c, fn) => { g.save(); g.shadowColor = c; g.shadowBlur = 26; fn(); g.restore(); };
  font(120, 'Anton', 400); neon(C.gold, () => txt('DAY ' + day, 960, 110, C.gold));
  const sway = Math.sin(t * 5) * .1;
  neon(C.cy, () => stick(330, 900, 1.25, C.cy, { a1: 2.4 + sway, a2: -2.4 - sway, l1: .3, l2: -.3 }));
  neon(C.mg, () => stick(1290, 900, 1.25, C.mg, { a1: .5 - seg(t, 8.6, 9) * 2.9, a2: -.5 + seg(t, 8.6, 9) * 2.9, l1: .15, l2: -.15, lean: -.05 }));
  const hS = Math.min(560, sam / 24000 * 560), hM = Math.min(600, Math.pow(seg(day, 1, 30), 5) * 600);
  neon(C.cy, () => rr(560, 900 - hS, 150, hS, 10, null, C.cy, 6)); g.globalAlpha = .25; g.fillStyle = C.cy; g.fillRect(560, 900 - hS, 150, hS); g.globalAlpha = 1;
  neon(C.mg, () => rr(1520, 900 - Math.max(6, hM), 150, Math.max(6, hM), 10, null, C.mg, 6)); g.globalAlpha = .25; g.fillStyle = C.mg; g.fillRect(1520, 900 - hM, 150, hM); g.globalAlpha = 1;
  font(44, 'JetBrains Mono'); txt('$800 A DAY', 480, 220, C.cy, 'center', seg(t, .2, .7)); txt('1¢, DOUBLED DAILY', 1440, 220, C.mg, 'center', seg(t, .5, 1));
  font(64, 'JetBrains Mono'); neon(C.cy, () => txt('$' + sam.toLocaleString('en-US'), 480, 990, C.cy)); neon(C.mg, () => txt('$' + mia.toLocaleString('en-US', { maximumFractionDigits: mia < 100 ? 2 : 0 }), 1440, 990, C.mg));
  if (t > 8.9) { font(96, 'Anton', 400); neon(C.gr, () => txt('WHICH WOULD YOU TAKE?', 960, 540, C.gr, 'center', seg(t, 8.9, 9.3))); }
};

S['ink-line-essay'] = t => {
  const C = { paper: '#EDE3CF', ink: '#1E1A16', sep: '#9B704F', wash: '#C9B690' };
  g.fillStyle = C.paper; g.fillRect(0, 0, W, H); for (let i = 0; i < 260; i++) { g.fillStyle = `rgba(120,95,60,${rnd(i) * .05})`; g.fillRect(rnd(i * 3) * W, rnd(i * 5) * H, 60 + rnd(i * 7) * 180, 2); }
  const wob = (pts, s) => pts.map(([x, y], i) => [x + (rnd(i * 3 + s) - .5) * 5, y + (rnd(i * 5 + s) - .5) * 5]);
  const hominid = (x, h, bulk, p, s, lab, yr) => { const y = 800, w = 44 * bulk, top = y - h; stroke(C.ink, 5);
    poly(wob([[x - w, y], [x - w * .8, y - h * .45], [x - w * 1.25, y - h * .78], [x - w * .5, y - h * .84], [x - w * .42, top + 30], [x - w * .62, top - 6], [x - w * .2, top - 46], [x + w * .5, top - 34], [x + w * .6, top + 8], [x + w * .34, top + 32], [x + w * 1.25, y - h * .76], [x + w * .8, y - h * .44], [x + w, y]], s), p);
    if (p >= 1) { g.save(); g.globalAlpha = .18; g.fillStyle = C.sep; g.beginPath(); g.ellipse(x, y - h * .5, w * 1.1, h * .5, 0, 0, TAU); g.fill(); g.restore(); stroke(C.sep, 3); poly([[x - w * 1.6, y + 8], [x + w * 1.6, y + 8]], 1); font(30, 'Cormorant Garamond'); txt(lab, x, y + 50, C.ink); font(24, 'Inter', 400); txt(yr, x, y + 88, C.sep); } };
  const fade = 1 - seg(t, 5.2, 5.8);
  if (fade > 0) { g.save(); g.globalAlpha = fade; cam(lerp(1, 1.06, seg(t, 0, 5.8)), 960, 540, () => {
    [['H. floresiensis', 250, .8, '1.1 m'], ['H. erectus', 430, 1, '1.7 m'], ['Neanderthal', 410, 1.3, '1.65 m'], ['Denisovan', 440, 1.25, 'unknown'], ['H. sapiens', 450, 1, '1.7 m']].forEach(([lab, h, b, yr], i) => hominid(340 + i * 310, h, b, eo(seg(t, .3 + i * .7, 1.3 + i * .7)), i * 20, lab, yr));
    stroke(C.ink, 3); poly([[180, 808], [1740, 808]], seg(t, .1, .8)); }); font(60, 'Cormorant Garamond'); txt('Five kinds of human, at the same time', 960, 150, C.ink, 'center', seg(t, .2, .8)); g.restore(); }
  if (t > 5.4) { g.save(); g.globalAlpha = seg(t, 5.6, 6.1); cam(lerp(1, 1.05, seg(t, 5.6, 10)), 960, 540, () => {
    stroke(C.ink, 5); const land = wob([[300, 620], [380, 420], [560, 330], [760, 380], [900, 300], [1150, 320], [1380, 260], [1600, 380], [1650, 560], [1500, 700], [1280, 660], [1100, 760], [900, 700], [760, 820], [560, 790], [420, 720], [300, 620]], 5);
    poly(land, eo(seg(t, 5.7, 7.2)), true); g.fillStyle = 'rgba(155,112,79,.10)'; g.beginPath(); land.forEach((p, i) => i ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1])); g.fill();
    const r1 = eo(seg(t, 6.8, 9.2)) * 330, r2 = eo(seg(t, 7.4, 9.4)) * 280; g.save(); g.beginPath(); land.forEach((p, i) => i ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1])); g.clip();
    g.fillStyle = 'rgba(30,26,22,.22)'; g.beginPath(); g.arc(640, 640, r1, 0, TAU); g.fill(); g.fillStyle = 'rgba(155,112,79,.45)'; g.beginPath(); g.arc(1320, 440, r2, 0, TAU); g.fill();
    for (let i = -20; i < 40; i++) { stroke('rgba(30,26,22,.25)', 2); g.beginPath(); g.moveTo(i * 44, 200); g.lineTo(i * 44 + 500, 900); g.stroke(); } g.restore();
    font(30, 'Cormorant Garamond'); txt('H. sapiens', 640, 640, C.ink, 'center', seg(t, 7, 7.5)); txt('Neanderthal', 1320, 440, C.ink, 'center', seg(t, 7.6, 8.1));
    if (t > 8.6) { stroke(C.ink, 4); g.setLineDash([10, 10]); circ(985, 540, 70 * eo(seg(t, 8.6, 9.1)), null, C.ink, 4); g.setLineDash([]); font(30, 'Cormorant Garamond'); txt('where they met', 985, 440, C.ink, 'center', seg(t, 8.9, 9.3)); } });
    font(60, 'Cormorant Garamond'); txt('…and their ranges overlapped', 960, 150, C.ink, 'center'); g.restore(); }
};

S['deep-sea-descent'] = t => {
  const d = eio(seg(t, 0, 5.2)), depth = Math.round(lerp(40, 2000, d));
  g.fillStyle = grad(0, 0, 0, H, [[0, `rgb(${lerp(10, 0, d)},${lerp(70, 4, d)},${lerp(110, 12, d)})`], [1, `rgb(0,${lerp(22, 1, d)},${lerp(40, 5, d)})`]]); g.fillRect(0, 0, W, H);
  if (d < .5) { g.save(); g.globalAlpha = (1 - d * 2) * .25; for (let i = 0; i < 5; i++) { g.fillStyle = '#BFE9FF'; g.beginPath(); g.moveTo(300 + i * 320, 0); g.lineTo(380 + i * 320, 0); g.lineTo(200 + i * 330 + Math.sin(t + i) * 40, H); g.lineTo(60 + i * 330, H); g.fill(); } g.restore(); }
  for (let i = 0; i < 90; i++) { const y = (rnd(i) * H + t * (120 + rnd(i * 3) * 160) * (t < 5.2 ? 1 : .35)) % H; circ(rnd(i * 7) * W, H - y, 1.5 + rnd(i * 5) * 2.5, `rgba(190,230,240,${.15 + rnd(i * 9) * .3})`); }
  stroke('#5ED6C4', 3); g.beginPath(); g.moveTo(110, 160); g.lineTo(110, 920); g.stroke(); for (let i = 0; i <= 10; i++) { g.beginPath(); g.moveTo(110, 160 + i * 76); g.lineTo(i % 5 ? 126 : 142, 160 + i * 76); g.stroke(); }
  circ(110, 160 + d * 760, 12, '#5ED6C4'); font(44, 'JetBrains Mono'); txt(depth + ' m', 160, 160 + d * 760, '#5ED6C4', 'left');
  const fa = seg(t, 3.9, 5.2), fx = lerp(2200, 1040, eo(seg(t, 3.6, 6))) + Math.sin(t * 1.3) * 14, fy = 560 + Math.sin(t * .9) * 16, xr = seg(t, 7.2, 8);
  if (fa > 0) { glow(fx - 60, fy - 40, 420, 'rgba(60,230,200,.22)', fa);
    g.save(); g.translate(fx, fy); g.globalAlpha = fa * lerp(1, .35, xr); g.fillStyle = '#0B2B33'; g.beginPath(); g.moveTo(-330, 0); g.bezierCurveTo(-260, -170, 60, -190, 250, -40); g.lineTo(390, -130); g.lineTo(360, 0); g.lineTo(390, 130); g.lineTo(250, 40); g.bezierCurveTo(60, 170, -260, 150, -330, 0); g.fill(); stroke('#3CE6C8', 4); g.stroke();
    g.globalAlpha = fa; g.fillStyle = 'rgba(60,230,200,.18)'; g.beginPath(); g.ellipse(-150, -70, 150, 80, -.1, 0, TAU); g.fill(); stroke('#8FF5E3', 3); g.stroke();
    circ(-190, -80, 30, '#7CFF9B'); circ(-110, -86, 30, '#7CFF9B'); circ(-190, -88, 12, '#03241C'); circ(-110, -94, 12, '#03241C');
    if (xr > 0) { g.globalAlpha = xr; stroke('#E6FFFA', 4); g.beginPath(); g.moveTo(-60, 0); g.lineTo(250, 0); g.stroke(); for (let i = 0; i < 9; i++) { g.beginPath(); g.moveTo(-40 + i * 34, 0); g.lineTo(-58 + i * 34, -64 + i * 4); g.moveTo(-40 + i * 34, 0); g.lineTo(-58 + i * 34, 64 - i * 4); g.stroke(); } }
    g.restore();
    callout(fx - 150, fy - 150, fx - 330, fy - 300, 'EYES POINT UP', '#8FF5E3', seg(t, 6.2, 6.9));
    const dv = seg(t, 8.4, 9); if (dv > 0) { stick(fx + 520, fy + 150, .42, `rgba(230,255,250,${dv})`, { a1: 1.3, a2: 1.6, l1: 1.2, l2: 1.5, lean: 1.2, lw: 14 }); font(26, 'JetBrains Mono'); txt('DIVER, TO SCALE (x10 smaller)', fx + 480, fy + 220, '#8FF5E3', 'center', dv); } }
  if (t > 5.6) { font(96, 'Anton', 400); txt('TRANSPARENT HEAD', 960, 930, '#fff', 'center', seg(t, 5.6, 6)); }
  if (t < 3) { font(54, 'Inter'); txt('Below 1,000 metres, sunlight stops.', 960, 930, '#CFEFF5', 'center', seg(t, .5, 1.1) * (1 - seg(t, 2.5, 3))); }
};

S['silent-habit-film'] = t => {
  const tt = twos(t), turn = seg(t, 6.2, 9.6), R = eo(turn) * 2300;
  const room = (col) => { const k = col ? 1 : 0, c = (a, b) => k ? a : b;
    g.fillStyle = c('#3B4A6B', '#3A3D42'); g.fillRect(0, 0, W, H); g.fillStyle = c('#2C3654', '#2D3035'); g.fillRect(0, 760, W, 320);
    rr(1220, 150, 420, 380, 6, c('#F5C56B', '#5B5E64'), c('#22283C', '#232529'), 12); g.fillStyle = c('rgba(255,220,150,.9)', 'rgba(140,145,150,.5)'); g.fillRect(1232, 162, 396, 356); stroke(c('#22283C', '#232529'), 10); g.beginPath(); g.moveTo(1430, 150); g.lineTo(1430, 530); g.moveTo(1220, 340); g.lineTo(1640, 340); g.stroke();
    if (k) glow(1430, 340, 900, 'rgba(255,200,120,.35)');
    rr(360, 560, 700, 240, 40, c('#8C4A3C', '#55585D'), c('#1D1B22', '#1E1F22'), 10); rr(330, 500, 110, 300, 34, c('#A45A48', '#606368'), c('#1D1B22', '#1E1F22'), 10); rr(980, 500, 110, 300, 34, c('#A45A48', '#606368'), c('#1D1B22', '#1E1F22'), 10);
    const pick = seg(tt, 6.2, 7.4), gx = lerp(1650, 880, eo(pick)), gy = lerp(790, 640, eo(pick)), ga = lerp(-.25, .95, eo(pick));
    const sit = { x: 700, y: 640 }, slump = lerp(.32, .02, eo(seg(tt, 5.6, 6.6))), ink = c('#1D1B22', '#1E1F22'), skin = c('#F0C9A0', '#9DA0A5'), shirt = c('#E3A857', '#70737A');
    g.save(); g.translate(sit.x, sit.y); stroke(ink, 10); g.beginPath(); g.moveTo(-30, 60); g.lineTo(60, 80); g.lineTo(70, 190); g.moveTo(20, 60); g.lineTo(130, 80); g.lineTo(140, 190); g.stroke();
    g.rotate(slump); rr(-56, -110, 112, 180, 46, shirt, ink, 10); circ(0 + slump * 60, -170, 62, skin, ink, 10);
    const ey = -170 + slump * 30; g.fillStyle = ink; if (pick > .5) { arc(-18 + slump * 60, ey - 4, 10, Math.PI, TAU, ink, 6); arc(22 + slump * 60, ey - 4, 10, Math.PI, TAU, ink, 6); arc(2 + slump * 60, ey + 20, 16, .2, Math.PI - .2, ink, 6); } else { g.fillRect(-28 + slump * 60, ey, 20, 6); g.fillRect(12 + slump * 60, ey, 20, 6); }
    g.restore();
    const ph = 1 - seg(tt, 5.6, 6.2); if (ph > 0) { g.save(); g.globalAlpha = ph; rr(760, 610, 46, 80, 8, '#DDEBFF', ink, 6); g.restore(); glow(783, 650, 260, 'rgba(160,200,255,.35)', ph * (.75 + .25 * Math.sin(tt * 9))); }
    g.save(); g.translate(gx, gy); g.rotate(ga); stroke(ink, 9); rr(-14, -330, 28, 240, 6, c('#6B3E26', '#5A5C60'), ink, 8); g.beginPath(); g.ellipse(0, 0, 92, 110, 0, 0, TAU); g.fillStyle = c('#D98E4A', '#77797E'); g.fill(); g.stroke(); circ(0, -10, 30, ink); g.restore();
    if (k && pick >= 1) for (let i = 0; i < 3; i++) { const n = seg(t, 7.6 + i * .5, 9 + i * .5); if (n > 0 && n < 1) { font(60, 'Inter'); txt('♪', 960 + i * 70 + Math.sin(t * 3 + i) * 12, 520 - n * 200, `rgba(255,236,190,${1 - n})`); } }
  };
  cam(lerp(1.04, 1.12, ss(seg(t, 0, 10))), 930, 550, () => {
    room(false);
    if (R > 0) { g.save(); g.beginPath(); g.arc(880, 640, R, 0, TAU); g.clip(); room(true); g.restore(); }
    const days = Math.min(5, Math.floor(tt / 1.1)); rr(150, 180, 300, 260, 6, '#D9D9D9', '#1E1F22', 8); stroke('#B33A3A', 9);
    for (let i = 0; i < days; i++) { const x = 190 + (i % 3) * 86, y = 230 + Math.floor(i / 3) * 90; g.beginPath(); g.moveTo(x, y); g.lineTo(x + 50, y + 50); g.moveTo(x + 50, y); g.lineTo(x, y + 50); g.stroke(); }
    if (turn > .3) { stroke('#3E9B5F', 10); poly([[362, 330], [384, 356], [420, 306]], seg(turn, .3, .5)); }
  });
  grain(t, .04, 600);
};

S['object-with-a-soul'] = t => {
  g.fillStyle = '#0C1220'; g.fillRect(0, 0, W, H);
  const hop = Math.abs(Math.sin(seg(t, 2.4, 7.4) * Math.PI * 5)), cx = lerp(420, 980, eio(seg(t, 2.4, 7.4))), cy = 760 - hop * 46, grow = lerp(.55, 1.25, eo(seg(t, 6.8, 9.4))), fl = .85 + .15 * Math.sin(t * 23) * Math.sin(t * 7.3);
  cam(lerp(1, 1.08, ss(seg(t, 0, 10))), 960, 560, () => {
    for (let i = 0; i < 3; i++) { const x = 620 + i * 430, lit = eo(seg(t, 7 + i * .35, 8.6 + i * .35)); g.fillStyle = '#141C30'; g.beginPath(); g.ellipse(x, 320, 150, 170, 0, 0, TAU); g.fill(); g.fillRect(x - 230, 440, 460, 460);
      glow(x, 470, 230, 'rgba(120,170,255,.55)', (1 - lit) * (.8 + .2 * Math.sin(t * 6 + i))); g.save(); g.globalAlpha = 1 - lit; rr(x - 46, 500, 92, 150, 12, '#BFD8FF'); g.restore();
      if (lit > 0) { g.save(); g.globalAlpha = lit * .85; g.fillStyle = '#8A5A3A'; g.fillRect(x - 230, 440, 460, 460); g.fillStyle = '#E8A55C'; g.beginPath(); g.ellipse(x, 320, 150, 170, 0, 0, TAU); g.fill(); g.fillStyle = '#3A2414'; circ(x - 46, 300, 12, '#3A2414'); circ(x + 46, 300, 12, '#3A2414'); arc(x, 350, 46, .15, Math.PI - .15, '#3A2414', 9); g.restore(); } }
    g.fillStyle = '#2A1D16'; g.fillRect(-100, 800, W + 200, 400); stroke('#4A3324', 6); g.beginPath(); g.moveTo(-100, 800); g.lineTo(W + 100, 800); g.stroke();
    glow(cx, cy - 190, 700 * grow * fl, 'rgba(255,170,70,.55)'); glow(cx, 800, 520 * grow, 'rgba(255,150,60,.35)');
    const sq = 1 - hop * .08; g.save(); g.translate(cx, cy + 40); g.scale(1 / sq, sq);
    rr(-52, -170, 104, 170, 26, '#F6E7C8', '#3A2414', 8); g.fillStyle = '#EAD6AE'; g.beginPath(); g.ellipse(-52, -150, 16, 26, 0, 0, TAU); g.fill();
    const bl = (t % 3.1) < .12 ? .15 : 1; g.fillStyle = '#3A2414'; g.beginPath(); g.ellipse(-20, -96, 9, 12 * bl, 0, 0, TAU); g.ellipse(20, -96, 9, 12 * bl, 0, 0, TAU); g.fill();
    arc(0, -70, t > 7.4 ? 18 : 8, .2, Math.PI - .2, '#3A2414', 6); stroke('#3A2414', 6); g.beginPath(); g.moveTo(0, -170); g.lineTo(0, -192); g.stroke();
    g.fillStyle = '#FFB347'; g.beginPath(); g.moveTo(0, -196); g.bezierCurveTo(-30 * fl, -230, -8, -270 * fl, Math.sin(t * 9) * 8, -300 * fl); g.bezierCurveTo(10, -260, 30 * fl, -230, 0, -196); g.fill(); g.fillStyle = '#FFF2B0'; g.beginPath(); g.ellipse(0, -216, 9, 18, 0, 0, TAU); g.fill();
    g.restore();
    g.fillStyle = '#05070D'; g.beginPath(); g.moveTo(-100, 1100); g.lineTo(-100, 520); g.bezierCurveTo(40, 560, 150, 760, 190, 1100); g.fill();
  });
  grain(t, .05, 700);
};

S['organ-sitcom'] = t => {
  const C = { bg: '#FFF4DC', ink: '#2A1B2E', red: '#E63946', teal: '#2EC4B6', or: '#FF6B4A', pink: '#F7A8B8', ylw: '#FFD166' };
  g.fillStyle = C.bg; g.fillRect(0, 0, W, H); g.fillStyle = '#FFE6B5'; g.fillRect(0, 800, W, 280); for (let i = 0; i < 12; i++) circ(100 + i * 160, 120 + (i % 2) * 60, 16, 'rgba(255,107,74,.16)');
  const who = t < 3.2 ? 0 : t < 6.4 ? 1 : 2, tk = i => (who === i ? Math.abs(Math.sin(t * 13)) : 0), bob = i => Math.sin(t * 5 + i * 2) * (who === i ? 16 : 5);
  const limbs = (x, y, i, up) => { stroke(C.ink, 9); g.beginPath(); g.moveTo(x - 110, y); g.quadraticCurveTo(x - 190, y + 20 - up * 150, x - 170 - up * 30, y + 60 - up * 220); g.moveTo(x + 110, y); g.quadraticCurveTo(x + 190, y + 40, x + 170, y + 90); g.moveTo(x - 40, y + 130); g.lineTo(x - 50, y + 230); g.lineTo(x - 90, y + 232); g.moveTo(x + 40, y + 130); g.lineTo(x + 50, y + 230); g.lineTo(x + 90, y + 232); g.stroke(); };
  const face = (x, y, i, mood) => { circ(x - 36, y - 14, 20, '#fff', C.ink, 7); circ(x + 36, y - 14, 20, '#fff', C.ink, 7); circ(x - 32, y - 12, 8, C.ink); circ(x + 40, y - 12, 8, C.ink);
    stroke(C.ink, 8); g.beginPath(); if (mood === 'angry') { g.moveTo(x - 62, y - 54); g.lineTo(x - 16, y - 40); g.moveTo(x + 62, y - 54); g.lineTo(x + 16, y - 40); } else { g.moveTo(x - 60, y - 46); g.lineTo(x - 16, y - 52); g.moveTo(x + 60, y - 46); g.lineTo(x + 16, y - 52); } g.stroke();
    g.beginPath(); g.ellipse(x, y + 44, 26, 6 + 22 * tk(i), 0, 0, TAU); g.fillStyle = '#7A1E28'; g.fill(); g.stroke(); };
  cam(1 + .015 * Math.sin(t * .8) + t * .004, 960, 540, () => {
    let x = 430, y = 560 + bob(0); limbs(x, y, 0, who === 0 ? .9 : 0); g.fillStyle = C.pink; stroke(C.ink, 10); g.beginPath(); for (let k = 0; k <= 24; k++) { const a = k / 24 * TAU, r = 150 + Math.sin(a * 7) * 16; k ? g.lineTo(x + Math.cos(a) * r * 1.12, y + Math.sin(a) * r * .9) : g.moveTo(x + r * 1.12, y); } g.closePath(); g.fill(); g.stroke(); stroke(C.ink, 5); g.beginPath(); g.moveTo(x, y - 130); g.quadraticCurveTo(x - 30, y - 60, x + 6, y - 46); g.stroke(); face(x, y + 10, 0, 'angry'); stroke(C.ink, 7); circ(x - 36, y - 4, 34, null, C.ink, 7); circ(x + 36, y - 4, 34, null, C.ink, 7);
    x = 960; y = 580 + bob(1); limbs(x, y, 1, who === 1 ? .6 : 0); g.fillStyle = C.red; stroke(C.ink, 10); const bt = 1 + .06 * Math.max(0, Math.sin(t * 8)); g.save(); g.translate(x, y); g.scale(bt, bt); g.beginPath(); g.moveTo(0, 150); g.bezierCurveTo(-240, 10, -150, -190, 0, -80); g.bezierCurveTo(150, -190, 240, 10, 0, 150); g.fill(); g.stroke(); rr(-112, -92, 224, 30, 10, '#fff', C.ink, 7); g.restore(); face(x, y, 1, 'ok');
    x = 1490; y = 570 + bob(2); limbs(x, y, 2, who === 2 ? .8 : 0); g.fillStyle = C.ylw; stroke(C.ink, 10); g.beginPath(); g.moveTo(x - 60, y - 170); g.bezierCurveTo(x + 60, y - 170, x + 190, y - 60, x + 150, y + 80); g.bezierCurveTo(x + 110, y + 190, x - 150, y + 180, x - 160, y + 40); g.bezierCurveTo(x - 170, y - 40, x - 60, y - 60, x - 60, y - 170); g.closePath(); g.fill(); g.stroke(); face(x, y + 10, 2, who === 2 ? 'angry' : 'ok');
    const lines = [['WE WALK 10,000 STEPS!', 430, C.or], ['I can take it!', 960, C.red], ['…is there cake after?', 1490, C.teal]], [s, bx, bc] = lines[who], st = [0, 3.2, 6.4][who], k = eo(seg(t, st + .1, st + .4));
    font(48, 'Fredoka'); const bw = g.measureText(s).width + 70; g.save(); g.translate(bx, 250); g.scale(k, k); rr(-bw / 2, -56, bw, 112, 40, '#fff', C.ink, 8); g.fillStyle = '#fff'; g.beginPath(); g.moveTo(-24, 52); g.lineTo(0, 100); g.lineTo(30, 52); g.fill(); stroke(C.ink, 8); g.beginPath(); g.moveTo(-24, 54); g.lineTo(0, 100); g.lineTo(30, 54); g.stroke(); txt(s, 0, 2, bc); g.restore();
  });
  rr(1560, 50, 300, 90, 45, C.ink); font(48, 'Fredoka'); txt('DAY ' + (1 + Math.floor(t / 3.34)), 1710, 97, C.ylw);
};

S['mascot-essay'] = t => {
  const C = { bg: '#F4EFE6', ink: '#23212B', owl: '#8C6A4F', owl2: '#D9B48F', blue: '#3B6FD4', or: '#F28C28', mu: '#8A8794' };
  g.fillStyle = C.bg; g.fillRect(0, 0, W, H); g.fillStyle = '#EAE2D3'; g.fillRect(0, 0, 720, H);
  const w = i => (rnd(i + Math.floor(t * 8) * 13) - .5) * 5, ox = 360, oy = 600 + Math.sin(t * 2) * 8, pt = eo(seg(t, 1.6, 2.2));
  stroke(C.ink, 9); g.fillStyle = C.owl; g.beginPath(); g.ellipse(ox + w(1), oy + w(2), 190, 240, 0, 0, TAU); g.fill(); g.stroke(); g.fillStyle = C.owl2; g.beginPath(); g.ellipse(ox + w(3), oy + 60, 120, 150, 0, 0, TAU); g.fill(); g.stroke();
  g.fillStyle = C.owl; g.beginPath(); g.moveTo(ox - 150, oy - 190); g.lineTo(ox - 120 + w(4), oy - 290); g.lineTo(ox - 60, oy - 220); g.moveTo(ox + 150, oy - 190); g.lineTo(ox + 120 + w(5), oy - 290); g.lineTo(ox + 60, oy - 220); g.fill(); g.stroke();
  const bl = (t % 2.7) < .14; circ(ox - 70, oy - 90, 62, '#fff', C.ink, 9); circ(ox + 70, oy - 90, 62, '#fff', C.ink, 9); if (bl) { stroke(C.ink, 9); g.beginPath(); g.moveTo(ox - 120, oy - 90); g.lineTo(ox - 20, oy - 90); g.moveTo(ox + 20, oy - 90); g.lineTo(ox + 120, oy - 90); g.stroke(); } else { circ(ox - 56 + pt * 14, oy - 86, 24, C.ink); circ(ox + 84 + pt * 14, oy - 86, 24, C.ink); }
  g.fillStyle = C.or; g.beginPath(); g.moveTo(ox - 24, oy - 30); g.lineTo(ox + 24, oy - 30); g.lineTo(ox, oy + 14 + Math.abs(Math.sin(t * 12)) * 10); g.closePath(); g.fill(); g.stroke();
  stroke(C.ink, 12); g.beginPath(); g.moveTo(ox + 170, oy + 20); g.quadraticCurveTo(ox + 250, oy + 60 - pt * 120, ox + 300, oy - 10 - pt * 150); g.stroke();
  g.beginPath(); g.moveTo(ox - 60, oy + 236); g.lineTo(ox - 70, oy + 290); g.moveTo(ox + 60, oy + 236); g.lineTo(ox + 70, oy + 290); g.stroke();
  font(44, 'Fredoka'); txt('owl sleep good.', ox, 180, C.ink, 'center', seg(t, .3, .8)); txt('you sleep bad. why.', ox, 240, C.ink, 'center', seg(t, .9, 1.4));
  circ(840, 150, 54, C.blue); font(64, 'Anton', 400); txt('1', 840, 154, '#fff'); font(60, 'Inter'); txt('Light tells the clock what time it is', 920, 150, C.ink, 'left', seg(t, 1.8, 2.4));
  const X0 = 860, X1 = 1800, Y0 = 860, Y1 = 330; stroke(C.mu, 4); g.beginPath(); g.moveTo(X0, Y1 - 30); g.lineTo(X0, Y0); g.lineTo(X1, Y0); g.stroke();
  font(28, 'Inter', 400); ['6 pm', '9 pm', 'midnight', '3 am', '6 am'].forEach((s, i) => txt(s, X0 + i * 235, Y0 + 44, C.mu)); g.save(); g.translate(X0 - 50, 600); g.rotate(-Math.PI / 2); txt('melatonin', 0, 0, C.mu); g.restore();
  const curve = (shift, amp) => Array.from({ length: 80 }, (_, i) => { const u = i / 79; return [lerp(X0, X1, u), Y0 - 20 - amp * Math.exp(-Math.pow((u - shift) / .2, 2)) * 440]; });
  stroke(C.blue, 9); poly(curve(.5, 1), eo(seg(t, 2.6, 4.6))); font(34, 'Inter'); txt('dark evening', 1300, 350, C.blue, 'center', seg(t, 4.4, 4.9));
  stroke(C.or, 9); g.setLineDash([22, 16]); poly(curve(.68, .55), eo(seg(t, 5.4, 7.4))); g.setLineDash([]); txt('bright screen at 11 pm', 1560, 570, C.or, 'center', seg(t, 7.2, 7.7));
  if (t > 7.9) { const k = eo(seg(t, 7.9, 8.5)); stroke(C.ink, 5); g.beginPath(); g.moveTo(1332, 420); g.lineTo(lerp(1332, 1500, k), 420); g.stroke(); g.beginPath(); g.moveTo(lerp(1332, 1500, k), 420); g.lineTo(lerp(1332, 1500, k) - 18, 408); g.moveTo(lerp(1332, 1500, k), 420); g.lineTo(lerp(1332, 1500, k) - 18, 432); g.stroke(); font(40, 'Inter'); txt('peak arrives ~90 min late', 1420, 250, C.ink, 'center', seg(t, 8.3, 8.8)); }
  font(24, 'Inter', 400); txt('Illustrative curve for the look sample, not data', 1800, 1030, C.mu, 'right');
};

S['stickman-survival-serial'] = t => {
  const C = { bg: '#0A0605', wall: '#6E4C29', dim: '#3A2413', amb: '#D2A46D', red: '#FF4A3D' };
  g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
  cam(lerp(1, 1.05, seg(t, 0, 10)), 960, 540, () => {
    stroke(C.dim, 10); g.strokeRect(260, 180, 1400, 760); g.beginPath(); g.moveTo(1100, 180); g.lineTo(1100, 520); g.moveTo(1100, 680); g.lineTo(1100, 940); g.stroke();
    stroke(C.bg, 14); g.beginPath(); g.moveTo(1660, 600); g.lineTo(1660, 760); g.stroke(); stroke(C.wall, 6); g.beginPath(); g.arc(1660, 600, 160, Math.PI / 2, Math.PI); g.stroke();
    stroke('#7FA8C9', 8); g.beginPath(); g.moveTo(520, 180); g.lineTo(840, 180); g.stroke(); const fr = seg(t, 1, 9); for (let i = 0; i < 26; i++) { const x = 520 + rnd(i) * 320, L = 20 + rnd(i * 3) * 110 * fr; stroke(`rgba(160,205,235,${.25 + rnd(i * 7) * .4})`, 2); g.beginPath(); g.moveTo(x, 186); g.lineTo(x + (rnd(i * 5) - .5) * 50, 186 + L); g.stroke(); }
    rr(330, 700, 300, 170, 10, null, C.dim, 6); rr(1220, 240, 150, 210, 8, null, C.dim, 6); font(24, 'JetBrains Mono'); txt('FRIDGE', 1295, 345, C.dim); txt('BED', 480, 785, C.dim);
    const px = lerp(700, 1340, eio(seg(t, 2, 7))), py = 640, ang = lerp(-.5, .15, eio(seg(t, 2, 7))) + Math.sin(t * 1.7) * .1 + (t > 7.4 ? lerp(0, .35, eo(seg(t, 7.4, 7.8))) : 0);
    g.save(); g.translate(px + 40, py - 150); g.rotate(ang); const q = g.createLinearGradient(0, 0, 800, 0); q.addColorStop(0, 'rgba(255,225,160,.55)'); q.addColorStop(1, 'rgba(255,225,160,0)'); g.fillStyle = q; g.beginPath(); g.moveTo(0, 0); g.lineTo(800, -210); g.lineTo(800, 210); g.closePath(); g.fill(); g.restore();
    stick(px, py + 60, .9, C.amb, { a1: 1.35 + ang, a2: -.3, l1: .2 + Math.sin(t * 6) * .25 * (t > 2 && t < 7 ? 1 : 0), l2: -.2 - Math.sin(t * 6) * .25 * (t > 2 && t < 7 ? 1 : 0) });
    glow(430, 730, 150, 'rgba(255,74,61,.5)', .5 + .5 * Math.sin(t * 4)); rr(412, 716, 36, 22, 4, C.red);
    if (t > 7.4) for (let i = 0; i < 3; i++) { const k = seg(t, 7.4 + i * .45, 8.3 + i * .45); if (k > 0 && k < 1) { stroke(`rgba(255,74,61,${1 - k})`, 6); g.beginPath(); g.arc(1670, 680, 30 + k * 150, Math.PI * .6, Math.PI * 1.4); g.stroke(); } }
  });
  font(40, 'JetBrains Mono'); typed('DAY 1 · 11:38 PM · THE POWER GOES OUT', 90, 80, '#D2A46D', seg(t, .2, 1.8));
  if (t > 3.2 && t < 7) { font(40, 'Inter'); txt('A closed fridge keeps food safe for about 4 hours.', 960, 1000, '#F1E3CC', 'center', seg(t, 3.2, 3.7) * (1 - seg(t, 6.5, 7))); }
  if (t > 7.6) { font(64, 'Inter'); txt('Then someone knocks.', 960, 1000, '#FF4A3D', 'center', seg(t, 7.6, 8)); }
  grain(t, .05, 500);
};

S['untold-saga'] = t => {
  const push = lerp(1, 1.16, ss(seg(t, 0, 10))), turn = seg(t, 6, 8.5);
  g.fillStyle = grad(0, 0, 0, H, [[0, '#0A0F1F'], [.55, `rgb(${lerp(27, 90, turn)},${lerp(42, 60, turn)},${lerp(74, 60, turn)})`], [1, '#120C0A']]); g.fillRect(0, 0, W, H);
  for (let i = 0; i < 120; i++) circ(rnd(i) * W, rnd(i * 3) * 520, .8 + rnd(i * 5) * 1.8, `rgba(230,225,255,${(.3 + rnd(i * 7) * .6) * (.6 + .4 * Math.sin(t * 2 + i))})`);
  const layer = (k, col, base, amp, seed) => cam(1 + (push - 1) * k, 960 + (k - .5) * 40, 600, () => { g.fillStyle = col; g.beginPath(); g.moveTo(-200, H + 300); for (let x = -200; x <= W + 200; x += 40) { const y = base - Math.abs(Math.sin(x * .004 + seed)) * amp - Math.sin(x * .013 + seed * 3) * amp * .25 - rnd(x + seed) * 14; g.lineTo(x, y); } g.lineTo(W + 200, H + 300); g.fill(); });
  glow(960, 470, 620, `rgba(${lerp(120, 227, turn)},${lerp(140, 168, turn)},${lerp(220, 87, turn)},.45)`);
  layer(.25, '#1B2540', 620, 260, 1); layer(.5, '#131A2E', 700, 200, 2.3);
  cam(1 + (push - 1) * .8, 960, 620, () => { g.fillStyle = '#0B0F1C'; g.beginPath(); g.moveTo(-200, H + 300); g.lineTo(-200, 860); g.quadraticCurveTo(960, 600, W + 200, 860); g.lineTo(W + 200, H + 300); g.fill();
    for (let i = 0; i < 11; i++) { const a = Math.PI + i / 10 * Math.PI, x = 960 + Math.cos(a) * 430, y = 742 + Math.sin(a) * 60 + Math.abs(i - 5) * 6, s = .8 + (1 - Math.abs(i - 5) / 5) * .35; g.fillStyle = '#05070D'; g.beginPath(); g.moveTo(x - 34 * s, y + 150 * s); g.quadraticCurveTo(x - 30 * s, y, x, y - 30 * s); g.quadraticCurveTo(x + 30 * s, y, x + 34 * s, y + 150 * s); g.fill(); circ(x, y - 44 * s, 22 * s, '#05070D');
      if (turn > 0) { g.save(); g.globalAlpha = turn * .8; stroke('#E3A857', 3); g.beginPath(); g.moveTo(x - 30 * s, y + 140 * s); g.quadraticCurveTo(x - 28 * s, y, x, y - 30 * s); g.stroke(); g.restore(); } }
    glow(960, 760, 260 + 140 * turn, 'rgba(227,168,87,.5)', .4 + .6 * turn); });
  for (let i = 0; i < 46; i++) { const y = 900 - ((t * (40 + rnd(i) * 70) + rnd(i * 3) * 900) % 900), x = 700 + rnd(i * 5) * 520 + Math.sin(t * 1.3 + i) * 30; circ(x, y, 2 + rnd(i * 7) * 3, `rgba(255,${150 + rnd(i) * 80},70,${(.2 + rnd(i * 9) * .6) * (.3 + turn * .7)})`); }
  layer(1.5, '#030407', 1010, 90, 4.1);
  font(120, 'Cormorant Garamond'); txt('THE OATH', 960, 220, '#F1E6D0', 'center', seg(t, 1, 2.2) * (1 - seg(t, 5, 5.8))); font(40, 'Cormorant Garamond'); txt('“Let us all swear an oath…”', 960, 950, '#E3A857', 'center', seg(t, 6.6, 7.4));
  font(24, 'Inter', 400); txt('1 Enoch 6:4, tr. R. H. Charles', 960, 1000, '#8A7F70', 'center', seg(t, 7.2, 7.8));
  const v = g.createRadialGradient(960, 540, 500, 960, 540, 1150); v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,.65)'); g.fillStyle = v; g.fillRect(0, 0, W, H); grain(t, .07, 1100);
};

S['myth-vs-text'] = t => {
  const C = { bg: '#17120C', pap: '#E9D9B4', ink: '#3A2A18', gold: '#D4AF37', mu: '#8A7F70', red: '#8C2F1B' };
  g.fillStyle = C.bg; g.fillRect(0, 0, W, H); glow(600, 400, 900, 'rgba(227,168,87,.16)');
  const a = 1 - seg(t, 5.2, 5.9);
  if (a > 0) { g.save(); g.globalAlpha = a; cam(lerp(1, 1.12, ss(seg(t, 0, 5.9))), 960, 540, () => {
    g.save(); g.translate(960, 560); g.rotate(-.025); rr(-560, -360, 1120, 720, 8, C.pap); g.fillStyle = 'rgba(120,80,30,.12)'; for (let i = 0; i < 40; i++) g.fillRect(-560 + rnd(i) * 1100, -360 + rnd(i * 3) * 700, 30 + rnd(i * 5) * 90, 3);
    const hl = eo(seg(t, 2.4, 3.4)); g.fillStyle = 'rgba(212,175,55,.55)'; g.fillRect(-250, -24, 520 * hl, 58);
    for (let r = 0; r < 9; r++) { const y = -270 + r * 68; stroke(C.ink, 5); let x = -470; for (let k = 0; k < 16; k++) { const wl = 26 + rnd(r * 31 + k) * 60; if (x + wl > 470) break; g.beginPath(); g.moveTo(x, y); for (let q = 0; q <= 6; q++) g.lineTo(x + q / 6 * wl, y + Math.sin(q * 2.1 + r + k) * 9 - (q % 2) * 5); g.stroke(); stroke(C.ink, 3); g.beginPath(); g.moveTo(x, y - 16); g.lineTo(x + wl, y - 16); g.stroke(); stroke(C.ink, 5); x += wl + 18; } }
    g.restore(); });
    font(54, 'Cormorant Garamond'); txt('The oldest text, line by line', 960, 110, C.pap, 'center', seg(t, .3, 1));
    font(40, 'Inter'); txt('The line everyone remembers is not here.', 960, 990, C.gold, 'center', seg(t, 3.5, 4.1));
    font(24, 'Inter', 400); txt('Stand-in script for the look sample', 1560, 930, C.mu, 'right'); g.restore(); }
  if (t > 5.6) { g.save(); g.globalAlpha = seg(t, 5.8, 6.3); font(54, 'Cormorant Garamond'); txt('So where did it come from?', 960, 200, C.pap);
    const N = [['The original', 'oldest source'], ['A regional retelling', 'centuries later'], ['The stage play', 'a chalk line the crowd can see'], ['Television', 'the version we remember']], X = i => 300 + i * 440;
    stroke(C.mu, 5); poly([[X(0), 560], [X(3), 560]], eo(seg(t, 6, 8.6)));
    N.forEach(([s, d], i) => { const k = eo(seg(t, 6.2 + i * .75, 6.7 + i * .75)); if (k <= 0) return; circ(X(i), 560, 26 * k, i === 0 ? C.pap : i === 3 ? C.gold : C.red); if (i > 0) glow(X(i), 560, 120 * k, i === 3 ? 'rgba(212,175,55,.5)' : 'rgba(140,47,27,.5)');
      font(40, 'Cormorant Garamond'); txt(s, X(i), 470, C.pap, 'center', k); font(26, 'Inter', 400); txt(d, X(i), 640, C.mu, 'center', k); if (i === 0) { font(26, 'Inter'); txt('no line', X(i), 690, C.pap, 'center', k); } if (i === 1) { font(26, 'Inter'); txt('the line appears', X(i), 690, '#D98B6F', 'center', k); } });
    g.restore(); }
  grain(t, .05, 700);
};

S['storybook-parable'] = t => {
  const C = { sky1: '#F7D9A8', sky2: '#F2B880', sand: '#E2B36B', soil: '#7A4E2D', soil2: '#5A3620', ink: '#4A2F1B', leaf: '#6FA35C', water: '#5FB3C9', stone: '#9C9488' };
  const HZ = 430;
  cam(lerp(1, 1.07, ss(seg(t, 0, 10))), 960, lerp(500, 600, ss(seg(t, 1, 8))), () => {
    g.fillStyle = grad(0, -100, 0, HZ, [[0, C.sky2], [1, C.sky1]]); g.fillRect(-200, -200, W + 400, HZ + 200); circ(1480, 190, 100, '#FFF1C9'); glow(1480, 190, 420, 'rgba(255,240,200,.6)');
    for (let i = 0; i < 4; i++) { const x = ((i * 520 + t * (14 + i * 5)) % (W + 500)) - 250, y = 110 + i * 48; g.fillStyle = 'rgba(255,255,255,.75)'; g.beginPath(); g.ellipse(x, y, 130, 34, 0, 0, TAU); g.ellipse(x + 80, y - 20, 90, 36, 0, 0, TAU); g.fill(); }
    g.fillStyle = '#D9A55C'; g.beginPath(); g.moveTo(-200, HZ); for (let x = -200; x <= W + 200; x += 60) g.lineTo(x, HZ - 40 - Math.sin(x * .004) * 46); g.lineTo(W + 200, HZ + 40); g.lineTo(-200, HZ + 40); g.fill();
    g.fillStyle = C.sand; g.fillRect(-200, HZ, W + 400, 50); g.fillStyle = grad(0, HZ + 40, 0, 1300, [[0, C.soil], [1, C.soil2]]); g.fillRect(-200, HZ + 40, W + 400, 900);
    for (let i = 0; i < 70; i++) circ(rnd(i) * W, HZ + 80 + rnd(i * 3) * 620, 3 + rnd(i * 5) * 8, 'rgba(60,35,18,.35)');
    g.fillStyle = C.water; g.globalAlpha = .85; g.beginPath(); g.moveTo(-200, 1010); for (let x = -200; x <= W + 200; x += 40) g.lineTo(x, 1000 + Math.sin(x * .02 + t * 2) * 8); g.lineTo(W + 200, 1300); g.lineTo(-200, 1300); g.fill(); g.globalAlpha = 1;
    stroke(C.ink, 7); g.fillStyle = C.stone; g.beginPath(); g.ellipse(960, HZ + 10, 230, 78, 0, 0, TAU); g.fill(); g.stroke();
    const sy = HZ + 150; const grow = seg(t, 2.6, 8.6), roots = [[[960, sy], [940, sy + 150], [900, sy + 300], [880, sy + 440]], [[960, sy], [1000, sy + 120], [1090, sy + 240], [1130, sy + 420]], [[940, sy + 150], [840, sy + 230], [760, sy + 380]], [[1000, sy + 120], [1060, sy + 170], [1210, sy + 250]], [[900, sy + 300], [960, sy + 400], [990, sy + 460]]];
    roots.forEach((r, i) => { stroke('#E9D2A6', i < 2 ? 12 : 7); poly(r, eo(seg(grow, i * .12, .5 + i * .12))); });
    const tryUp = t < 2.6 ? Math.abs(Math.sin(t * 4)) * 26 : 0; stroke(C.leaf, 9); if (t > .6 && t < 2.8) { g.beginPath(); g.moveTo(960, sy); g.lineTo(960, sy - 50 - tryUp); g.stroke(); }
    g.fillStyle = '#8A5A2B'; stroke(C.ink, 7); g.beginPath(); g.ellipse(960, sy, 34, 46, .2, 0, TAU); g.fill(); g.stroke(); circ(950, sy - 8, 5, C.ink); circ(972, sy - 8, 5, C.ink); arc(961, sy + 8, 10, t > 7.6 ? .2 : Math.PI + .2, t > 7.6 ? Math.PI - .2 : TAU - .2, C.ink, 4);
    if (grow > .95) { const k = eo(seg(t, 8.5, 9.6)); stroke(C.leaf, 10); poly([[960, sy - 40], [1010, sy - 110], [1180, HZ - 20], [1215, HZ - 150]], k); if (k > .9) { g.fillStyle = C.leaf; g.beginPath(); g.ellipse(1245, HZ - 172, 40, 18, -.5, 0, TAU); g.ellipse(1188, HZ - 176, 36, 16, .6, 0, TAU); g.fill(); } }
    if (seg(grow, .8, 1) > 0) glow(1000, 1000, 240, 'rgba(120,220,240,.5)', seg(grow, .8, 1));
  });
  font(52, 'Cormorant Garamond'); const cap = t < 2.8 ? 'The seed pushed up, and met a stone.' : t < 8.4 ? 'So it grew the only way it could: down.' : 'And when it found water, it found a way around.';
  rr(360, 940, 1200, 96, 48, 'rgba(247,234,208,.92)'); txt(cap, 960, 990, C.ink);
  grain(t, .03, 500);
};

S['mixed-engine-film'] = t => {
  const parts = [['schematic-explainer', 1.2, 'CHAPTER c01 · REMOTION · schematic'], ['silent-habit-film', 5.6, 'CHAPTER c02 · CANVAS · silent character scene'], ['untold-saga', 5.2, 'CHAPTER c03 · HYPERFRAMES · stills with parallax']];
  const i = Math.min(2, Math.floor(t / 3.3334)), u = t - i * 3.3334;
  S[parts[i][0]](parts[i][1] + u);
  const dip = Math.max(1 - seg(u, 0, .27), i < 2 ? seg(u, 3.06, 3.3334) : 0); if (i > 0 || u > 3) { g.fillStyle = `rgba(0,0,0,${i === 0 && u < 3 ? 0 : dip})`; g.fillRect(0, 0, W, H); }
  font(28, 'JetBrains Mono'); const w = g.measureText(parts[i][2]).width + 40; rr(W - w - 40, 36, w, 52, 10, 'rgba(0,0,0,.7)'); txt(parts[i][2], W - 60, 63, '#FFFFFF', 'right');
  stroke('#fff', 6); for (let k = 0; k < 3; k++) { g.globalAlpha = k === i ? 1 : .35; g.beginPath(); g.moveTo(W / 2 - 160 + k * 110, 1040); g.lineTo(W / 2 - 70 + k * 110, 1040); g.stroke(); } g.globalAlpha = 1;
};

const NAMES = { 'schematic-explainer': 'Schematic explainer', 'continuous-canvas-explainer': 'Continuous-canvas explainer', 'bizarre-history-story': 'Bizarre-history story', 'neon-dilemma': 'Neon dilemma',
  'ink-line-essay': 'Ink-line essay', 'deep-sea-descent': 'Deep-sea descent', 'silent-habit-film': 'Silent habit film', 'object-with-a-soul': 'Object with a soul', 'organ-sitcom': 'Organ sitcom',
  'mascot-essay': 'Mascot essay', 'stickman-survival-serial': 'Stickman survival serial', 'untold-saga': 'Untold saga', 'myth-vs-text': 'Myth versus the text', 'storybook-parable': 'Storybook parable', 'mixed-engine-film': 'Mixed-engine film' };
if (!S[STYLE]) throw new Error(`unknown style "${STYLE}"; have: ${Object.keys(S).join(', ')}`);
window.DUR = DUR;
window.render = (t) => {
  t = cl(t, 0, DUR);
  g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1; g.setLineDash([]); g.shadowBlur = 0; g.lineCap = 'round'; g.lineJoin = 'round';
  S[STYLE](t);
  g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1; g.setLineDash([]); g.shadowBlur = 0;
  tag(NAMES[STYLE]);
};
window.TEXTS = () => [];
window.EV = [];
window.READY = true;
