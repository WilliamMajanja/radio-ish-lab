#!/usr/bin/env python3
"""make_epk_cover.py — generate a Season One house-standard EPK cover.

House standard: 1080x1920, black background, white graphics. The graphic is the
artist's OWN 30 s loop rendered as a mirrored RMS waveform, so nothing about the
image is invented — it is drawn from the same audio the release publishes.

Output: <Artist>/epk/promo/cover_1080x1920_bw.png

Usage: python3 tools/make_epk_cover.py "Artist Name" TAG "Genre / Line"
"""
import subprocess, sys
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FONT_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SR = 22050

def envelope(path, columns=W, win=1024, hop=None):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path),
                        "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                       capture_output=True)
    if r.returncode or not r.stdout:
        raise RuntimeError(f"{path}: {r.stderr.decode(errors='replace')[:160]}")
    x = np.frombuffer(r.stdout, dtype="<i2").astype(np.float64) / 32768.0
    hop = hop or max(1, len(x) // columns)
    n = max(1, (len(x) - win) // hop)
    idx = np.arange(win)[None, :] + hop * np.arange(n)[:, None]
    frames = x[idx]
    rms = np.sqrt((frames ** 2).mean(axis=1))
    rms = rms / (rms.max() + 1e-12)
    # resample the envelope to exactly `columns` bars (max-pool for punch)
    edges = np.linspace(0, len(rms), columns + 1).astype(int)
    bars = np.array([rms[a:b].max() if b > a else 0.0
                     for a, b in zip(edges[:-1], edges[1:])])
    return bars

def fit_font(text, font_path, max_width, start):
    size = start
    while size > 20:
        f = ImageFont.truetype(font_path, size)
        if f.getbbox(text)[2] - f.getbbox(text)[0] <= max_width:
            return f
        size -= 2
    return ImageFont.truetype(font_path, 20)

def centered(draw, y, text, font, fill=255):
    l, t, r, b = draw.textbbox((0, 0), text, font=font)
    draw.text(((W - (r - l)) / 2 - l, y), text, font=font, fill=fill)

def build(name, tag, genre, loop, out):
    bars = envelope(loop)
    im = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(im)

    # keep all artwork in the upper ~60%: the video burns the name/genre/brand
    # into the lower third (y=1240..1530), which must stay clean black.
    fn = fit_font(name.upper(), FONT_B, W - 120, 128)
    centered(d, 230, name.upper(), fn)
    centered(d, 400, genre, ImageFont.truetype(FONT_R, 44))
    d.line([(120, 480), (W - 120, 480)], fill=255, width=3)

    # mirrored RMs waveform of the artist's own loop
    cx0, cx1 = 120, W - 120
    mid, amp = 720, 190
    d.line([(cx0, mid), (cx1, mid)], fill=48, width=2)
    span = (cx1 - cx0) / len(bars)
    for i, v in enumerate(bars):
        x = cx0 + i * span
        h = int(v * amp)
        d.rectangle([x, mid - h, x + max(1, span - 2), mid + h], fill=255)

    centered(d, 1010, "RADIO-ISH LAB  ·  SEASON ONE", ImageFont.truetype(FONT_R, 38))
    centered(d, 1074, "30s seamless loop  ·  1080x1920", ImageFont.truetype(FONT_R, 30))

    out.parent.mkdir(parents=True, exist_ok=True)
    im.convert("1", dither=Image.Dither.NONE).save(out)
    print(f"wrote {out} ({out.stat().st_size} B, mode 1)")

if __name__ == "__main__":
    name, tag, genre = sys.argv[1], sys.argv[2], sys.argv[3]
    loop = Path(name) / "epk" / "audio" / f"{tag}_B4_30s_loop.wav"
    out = Path(name) / "epk" / "promo" / "cover_1080x1920_bw.png"
    build(name, tag, genre, loop, out)
