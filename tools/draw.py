#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""draw.py — the pictures, computed. No photographs, no stock.

Every raster on the site is a function of a few equations in numpy:

    hero.jpg          two point sources on a pond — interference, the engine
    band-slits.jpg    the two-slit pattern, cos² × sinc²
    band-lattice.jpg  a surface-code checkerboard, data and checker qubits glowing
    band-ions.jpg     a chain of trapped ions in a rail trap
    band-sphere.jpg   a Bloch sphere, Lambert-shaded, with its arrow
    card.jpg          the share card, 1200×630, hero crop plus the title

    python3 tools/draw.py            # all, into build/img/
    python3 tools/draw.py hero       # one
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build" / "img"

NAVY = np.array([0.03, 0.05, 0.11])
TEAL = np.array([0.05, 0.62, 0.60])
GOLD = np.array([1.00, 0.78, 0.30])
VIOLET = np.array([0.62, 0.40, 0.95])
WHITE = np.array([0.98, 0.97, 0.94])


def ramp(t, stops):
    """t in [0,1] (any shape) → RGB through a list of (pos, colour)."""
    t = np.clip(t, 0, 1)
    out = np.zeros(t.shape + (3,), np.float32)
    for (p0, c0), (p1, c1) in zip(stops[:-1], stops[1:]):
        m = (t >= p0) & (t <= p1)
        u = ((t - p0) / max(p1 - p0, 1e-9))[..., None]
        out[m] = ((1 - u) * np.asarray(c0) + u * np.asarray(c1))[m]
    return out


def save(img, name, quality=86):
    OUT.mkdir(parents=True, exist_ok=True)
    arr = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(arr).save(OUT / name, quality=quality, optimize=True, progressive=True)
    print(f"  {name}  {arr.shape[1]}×{arr.shape[0]}")


def vignette(w, h, strength=0.55):
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.hypot((xx - w / 2) / (w / 2), (yy - h / 2) / (h / 2))
    return 1 - strength * np.clip(r - 0.35, 0, 1) ** 1.6


# ------------------------------------------------------------------ hero: two stones in a pond
def hero(w=2000, h=1000):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    k = 2 * np.pi / 46.0
    a = (xx - w * 0.38, yy - h * 0.50)
    b = (xx - w * 0.62, yy - h * 0.50)
    ra = np.hypot(*a)
    rb = np.hypot(*b)
    decay = lambda r: np.exp(-r / (w * 0.55)) / np.sqrt(1 + r / 60)
    wave = np.cos(k * ra) * decay(ra) + np.cos(k * rb) * decay(rb)
    # the standing-wave envelope: where the two are in step it leaps, where opposite it goes flat
    env = np.abs(np.cos(k * (ra - rb) / 2))
    t = 0.5 + 0.5 * wave / (2 * decay(0))
    img = ramp(t, [(0, NAVY * 0.6), (0.42, NAVY), (0.5, TEAL * 0.35 + NAVY * 0.65), (0.72, TEAL), (0.9, GOLD), (1, WHITE)])
    img *= (0.55 + 0.45 * env)[..., None]
    img *= vignette(w, h, 0.5)[..., None]
    return img


# ------------------------------------------------------------------ two slits
def slits(w=2000, h=900):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    x = (xx - w / 2) / w * 22.0
    stripes = np.cos(x * 2.6) ** 2
    sinc = np.sinc(x / 3.2) ** 2
    beam = np.exp(-((yy - h * 0.5) / (h * 0.42)) ** 2)
    t = stripes * sinc * (0.35 + 0.65 * beam)
    img = ramp(t ** 0.8, [(0, NAVY * 0.5), (0.25, NAVY), (0.55, VIOLET * 0.6 + NAVY * 0.4), (0.85, VIOLET), (1, WHITE)])
    # the single electron dots that build the pattern
    rng = np.random.default_rng(3)
    n = 9000
    px = rng.uniform(0, w, n * 6)
    py = rng.uniform(0, h, n * 6)
    prob = (np.cos((px - w / 2) / w * 22.0 * 2.6) ** 2) * np.sinc((px - w / 2) / w * 22.0 / 3.2) ** 2
    keep = rng.uniform(0, 1, n * 6) < prob
    for x0, y0 in zip(px[keep][:n].astype(int), py[keep][:n].astype(int)):
        img[max(y0 - 1, 0):y0 + 2, max(x0 - 1, 0):x0 + 2] += 0.12
    img *= vignette(w, h, 0.45)[..., None]
    return img


# ------------------------------------------------------------------ surface code lattice
def lattice(w=2000, h=900):
    img = np.tile(NAVY.astype(np.float32) * 0.8, (h, w, 1))
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    step = 92
    ox, oy = (w % step) / 2 + 30, (h % step) / 2 + 20
    # faint wires
    gx = np.abs(((xx - ox) % step) - step / 2) < 1.2
    gy = np.abs(((yy - oy) % step) - step / 2) < 1.2
    img[gx | gy] += 0.05
    rng = np.random.default_rng(11)
    glow = np.zeros((h, w, 3), np.float32)
    cols = int(w / step) + 2
    rows = int(h / step) + 2
    for i in range(cols):
        for j in range(rows):
            cx, cy = ox + i * step - step / 2, oy + j * step - step / 2
            data = (i + j) % 2 == 0
            col = GOLD if data else TEAL
            if not data and rng.uniform() < 0.10:
                col = np.array([1.0, 0.35, 0.30])   # a checker complaining
            r2 = (xx - cx) ** 2 + (yy - cy) ** 2
            glow += np.exp(-r2 / (2 * (18 if data else 12) ** 2))[..., None] * col * (1.0 if data else 0.85)
            glow += np.exp(-r2 / (2 * 60 ** 2))[..., None] * col * 0.10
    img += glow
    img *= vignette(w, h, 0.5)[..., None]
    return img


# ------------------------------------------------------------------ a chain of ions
def ions(w=2000, h=900):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    img = ramp((yy / h), [(0, NAVY * 0.5), (0.5, NAVY * 0.9), (1, NAVY * 0.4)])
    # trap rails
    for y0 in (h * 0.36, h * 0.64):
        band = np.exp(-((yy - y0) / 6) ** 2)
        img += band[..., None] * (TEAL * 0.35)
    n = 12
    xs = np.linspace(w * 0.16, w * 0.84, n)
    glow = np.zeros_like(img)
    for i, cx in enumerate(xs):
        cy = h * 0.5
        r2 = (xx - cx) ** 2 + (yy - cy) ** 2
        c = VIOLET if i % 3 else WHITE
        glow += np.exp(-r2 / (2 * 11 ** 2))[..., None] * c * 1.4
        glow += np.exp(-r2 / (2 * 40 ** 2))[..., None] * VIOLET * 0.35
        glow += np.exp(-r2 / (2 * 140 ** 2))[..., None] * VIOLET * 0.06
    # the laser beam, off-axis, faint
    beam = np.exp(-((yy - (h * 0.5 + (xx - w / 2) * 0.05)) / 14) ** 2) * np.exp(-((xx - w / 2) / (w * 0.5)) ** 2)
    img += beam[..., None] * (GOLD * 0.22)
    img += glow
    img *= vignette(w, h, 0.45)[..., None]
    return img


# ------------------------------------------------------------------ the Bloch sphere, shaded
def sphere(w=2000, h=900):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    img = np.tile(NAVY.astype(np.float32) * 0.85, (h, w, 1))
    cx, cy, R = w * 0.5, h * 0.52, h * 0.40
    X = (xx - cx) / R
    Y = (cy - yy) / R
    inside = X ** 2 + Y ** 2 <= 1
    Z = np.sqrt(np.clip(1 - X ** 2 - Y ** 2, 0, 1))
    light = np.array([-0.45, 0.55, 0.70]); light /= np.linalg.norm(light)
    lam = np.clip(X * light[0] + Y * light[1] + Z * light[2], 0, 1)
    rim = (1 - Z) ** 3
    base = (TEAL * 0.22 + NAVY * 0.78)
    shade = base * (0.35 + 0.9 * lam)[..., None] + (TEAL * 0.5)[None, None] * rim[..., None]
    img[inside] = shade[inside]
    # latitude rings, as ellipses on the front face
    tilt = 0.28
    for lat in np.linspace(-60, 60, 5):
        y0 = np.sin(np.radians(lat))
        rr = np.cos(np.radians(lat))
        d = np.abs(np.hypot(X / rr, (Y - y0 * np.cos(tilt)) / (rr * np.sin(tilt) + 1e-6)) - 1)
        img[inside & (d < 0.02)] += 0.10
    # two meridians, one face-on and one turned
    d = np.abs(X) ; img[inside & (d < 0.012)] += 0.10
    d = np.abs(np.hypot(X / 0.55, Y) - 1); img[inside & (d < 0.02)] += 0.08
    # equator, brighter
    d = np.abs(np.hypot(X, Y / (np.sin(tilt) + 1e-6)) - 1); img[inside & (d < 0.02)] += 0.16
    # the arrow: from centre to a point on the upper front
    ax, ay = 0.62, 0.55
    px, py = cx + ax * R, cy - ay * R
    t = np.clip(((xx - cx) * (px - cx) + (yy - cy) * (py - cy)) / ((px - cx) ** 2 + (py - cy) ** 2), 0, 1)
    dist = np.hypot(xx - (cx + t * (px - cx)), yy - (cy + t * (py - cy)))
    shaft = np.exp(-(dist / 5) ** 2)
    img += shaft[..., None] * GOLD * 1.2
    tip = np.exp(-((xx - px) ** 2 + (yy - py) ** 2) / (2 * 14 ** 2))
    img += tip[..., None] * GOLD * 1.6
    img += np.exp(-((xx - px) ** 2 + (yy - py) ** 2) / (2 * 60 ** 2))[..., None] * GOLD * 0.25
    # poles
    for (yy0, lab) in ((cy - R, 0), (cy + R, 1)):
        img += np.exp(-((xx - cx) ** 2 + (yy - yy0) ** 2) / (2 * 8 ** 2))[..., None] * WHITE * 1.1
    img *= vignette(w, h, 0.4)[..., None]
    return img


# ------------------------------------------------------------------ the share card
def font(size, bold=True):
    for p in ("/System/Library/Fonts/Avenir Next Condensed.ttc", "/System/Library/Fonts/HelveticaNeue.ttc",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"):
        if Path(p).exists():
            try:
                # index 6 in Avenir Next Condensed.ttc is Demi Bold on macOS; fall back to 0
                for idx in ((8, 0) if "Avenir" in p else (1, 0)):
                    try:
                        return ImageFont.truetype(p, size, index=idx)
                    except Exception:
                        continue
            except Exception:
                continue
    return ImageFont.load_default()


def card(title="Quantum Computing", sub="the history and the theory, in plain words", w=1200, h=630):
    base = hero(w=1200, h=630)
    im = Image.fromarray((np.clip(base, 0, 1) * 255).astype(np.uint8))
    # a scrim so the words sit on something
    scrim = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(scrim)
    for i in range(h // 2, h):
        a = int(200 * ((i - h / 2) / (h / 2)) ** 1.4)
        d.line([(0, i), (w, i)], fill=(5, 8, 20, a))
    im = Image.alpha_composite(im.convert("RGBA"), scrim)
    d = ImageDraw.Draw(im)
    f1 = font(118); f2 = font(40)
    d.text((60, h - 250), title.upper(), font=f1, fill=(255, 250, 240))
    d.text((64, h - 118), sub, font=f2, fill=(220, 230, 235))
    d.text((w - 330, h - 60), "nanobotco.github.io", font=font(28), fill=(160, 200, 205))
    OUT.mkdir(parents=True, exist_ok=True)
    im.convert("RGB").save(OUT / "card.jpg", quality=88, optimize=True)
    print("  card.jpg  1200×630")


PICTURES = {
    "hero": lambda: save(hero(), "hero.jpg"),
    "slits": lambda: save(slits(), "band-slits.jpg"),
    "lattice": lambda: save(lattice(), "band-lattice.jpg"),
    "ions": lambda: save(ions(), "band-ions.jpg"),
    "sphere": lambda: save(sphere(), "band-sphere.jpg"),
    "card": card,
}

if __name__ == "__main__":
    want = sys.argv[1:] or list(PICTURES)
    for k in want:
        PICTURES[k]()
