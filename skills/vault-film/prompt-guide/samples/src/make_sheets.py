#!/usr/bin/env python3
"""Per-style frame sheets and the all-styles overview from the sample clips (needs Pillow and ffmpeg).
usage: ~/lemo-opuscar/.venv/bin/python src/make_sheets.py      (run from prompt-guide/samples)"""
import io, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent.parent
STYLES = [("schematic-explainer", "Schematic explainer", 4.6), ("continuous-canvas-explainer", "Continuous-canvas explainer", 8.9), ("bizarre-history-story", "Bizarre-history story", 4.6),
          ("cartoon-3d-world", "3D cartoon world", 6.5), ("neon-dilemma", "Neon dilemma", 9.6), ("ink-line-essay", "Ink-line essay", 4.8), ("deep-sea-descent", "Deep-sea descent", 8.6),
          ("silent-habit-film", "Silent habit film", 7.4), ("object-with-a-soul", "Object with a soul", 8.6), ("organ-sitcom", "Organ sitcom", 1.5), ("mascot-essay", "Mascot essay", 8.8),
          ("stickman-survival-serial", "Stickman survival serial", 6.0), ("untold-saga", "Untold saga", 8.2), ("myth-vs-text", "Myth versus the text", 3.6), ("storybook-parable", "Storybook parable", 8.0),
          ("mixed-engine-film", "Mixed-engine film", 4.6)]
BG = (16, 16, 20)
def font(px):
    for f in ("/System/Library/Fonts/Helvetica.ttc", "/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        if Path(f).exists(): return ImageFont.truetype(f, px)
    return ImageFont.load_default()
def frame(slug, t):
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t}", "-i", str(HERE / f"{slug}.mp4"), "-frames:v", "1", "-f", "image2pipe", "-c:v", "png", "-"], capture_output=True)
    return Image.open(io.BytesIO(r.stdout)).convert("RGB")
def fit(im, w, h):
    k = min(w / im.width, h / im.height); im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    out = Image.new("RGB", (w, h), BG); out.paste(im, ((w - im.width) // 2, (h - im.height) // 2)); return out

(HERE / "sheets").mkdir(exist_ok=True)
for slug, name, _ in STYLES:   # five frames across the 10 seconds, with the time under each
    W, Hh, P, L = 480, 270, 8, 44
    sheet = Image.new("RGB", (5 * W + 6 * P, Hh + L + 2 * P + 54), BG); d = ImageDraw.Draw(sheet)
    d.text((P + 4, P + 6), name + "  ·  10 s sample", fill=(240, 240, 240), font=font(30))
    for i, t in enumerate((1, 3, 5, 7, 9)):
        x = P + i * (W + P); sheet.paste(fit(frame(slug, t), W, Hh), (x, P + 54)); d.text((x + 4, P + 54 + Hh + 8), f"{t} s", fill=(160, 160, 170), font=font(24))
    sheet.save(HERE / "sheets" / f"{slug}.jpg", quality=88)
W, Hh, P, L = 640, 360, 12, 52   # the overview: one frame per style, named
ov = Image.new("RGB", (4 * W + 5 * P, 4 * (Hh + L) + 5 * P), BG); d = ImageDraw.Draw(ov)
for i, (slug, name, t) in enumerate(STYLES):
    x, y = P + (i % 4) * (W + P), P + (i // 4) * (Hh + L + P)
    ov.paste(fit(frame(slug, t), W, Hh), (x, y)); d.text((x + 6, y + Hh + 10), f"{i + 1}. {name}", fill=(240, 240, 240), font=font(30))
ov.save(HERE / "all-styles.jpg", quality=88)
print(f"wrote {len(STYLES)} sheets and all-styles.jpg")
