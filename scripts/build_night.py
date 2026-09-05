#!/usr/bin/env python3
"""Bake the moon and the star field for assets/intro.svg. Pillow only.

    python3 scripts/build_night.py <out_dir>

Writes moon.png (520x520 RGBA, waxing gibbous, lit from the lower right),
stars.png (1600x560 RGBA, the faint and medium stars) and stars.json (the
brightest stars, drawn as vector circles that shimmer in the SVG).
"""

import json
import math
import random
import sys
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageFilter

random.seed(3)


def clamp(v, lo=0, hi=255):
    return max(lo, min(hi, int(round(v))))


def smoothstep(v, lo, hi):
    t = max(0.0, min(1.0, (v - lo) / (hi - lo)))
    return t * t * (3 - 2 * t)


# ------------------------------------------------------------------ moon

MARIA = [  # near side, north up: (cx, cy, rx, ry) as fractions of the radius
    (-0.28, -0.30, 0.34, 0.28),   # Imbrium
    (-0.60, -0.02, 0.26, 0.46),   # Oceanus Procellarum, joins Imbrium on the left
    (-0.40, 0.30, 0.16, 0.12),    # Humorum, small
    (0.14, -0.28, 0.20, 0.17),    # Serenitatis
    (0.36, -0.02, 0.26, 0.21),    # Tranquillitatis
    (0.54, 0.22, 0.14, 0.20),     # Fecunditatis
    (0.72, -0.30, 0.11, 0.09),    # Crisium
]


def moon(size=320, lit_fraction=0.85, sun_dir_deg=40):
    n = size * 2                       # drawn at 2x, downsampled for a clean limb
    c, r = n / 2, n / 2 * 0.94

    # albedo: highlands bright, maria dark with irregular edges
    maria = Image.new("L", (n, n), 0)
    d = ImageDraw.Draw(maria)
    for mx, my, rx, ry in MARIA:
        d.ellipse([c + mx * r - rx * r, c + my * r - ry * r, c + mx * r + rx * r, c + my * r + ry * r], fill=255)
    maria = maria.filter(ImageFilter.GaussianBlur(r * 0.03))
    rough = Image.effect_noise((40, 40), 60).resize((n, n), Image.BICUBIC)
    fine = Image.effect_noise((110, 110), 40).resize((n, n), Image.BICUBIC)
    maria = ImageChops.multiply(maria, Image.blend(rough, fine, 0.25).point(lambda v: clamp(40 + v * 1.1)))
    maria = maria.point(lambda v: clamp((v - 90) * 2.2)).filter(ImageFilter.GaussianBlur(4))
    albedo = ImageChops.subtract(Image.new("L", (n, n), 228), maria.point(lambda v: v * 0.32))
    grain = Image.effect_noise((n // 3, n // 3), 6).resize((n, n), Image.BICUBIC)
    albedo = ImageChops.add(albedo, grain, 1.0, -128)
    for mx, my, rad, peak in [(-0.12, 0.70, 0.05, 60), (-0.22, 0.12, 0.035, 45), (-0.66, -0.22, 0.03, 40)]:
        spot = Image.new("L", (n, n), 0)      # Tycho, Copernicus, Aristarchus as soft bright spots
        ImageDraw.Draw(spot).ellipse([c + mx * r - rad * r, c + my * r - rad * r, c + mx * r + rad * r, c + my * r + rad * r], fill=peak)
        albedo = ImageChops.add(albedo, spot.filter(ImageFilter.GaussianBlur(rad * r * 0.8)))
    albedo = albedo.filter(ImageFilter.GaussianBlur(0.6))

    # lighting: sphere normal dot sun direction, soft terminator, mild limb darkening
    phase = math.acos(2 * lit_fraction - 1)
    th = math.radians(sun_dir_deg)
    sx, sy, sz = math.sin(phase) * math.cos(th), math.sin(phase) * math.sin(th), math.cos(phase)
    m = 260
    light = Image.new("L", (m, m))
    px = light.load()
    for j in range(m):
        for i in range(m):
            nx, ny = (i + 0.5 - m / 2) / (m / 2 * 0.94), (j + 0.5 - m / 2) / (m / 2 * 0.94)
            rr = nx * nx + ny * ny
            if rr >= 1:
                px[i, j] = 0
                continue
            nz = math.sqrt(1 - rr)
            lit = smoothstep(nx * sx + ny * sy + nz * sz, -0.06, 0.28)
            limb = 1 - 0.28 * rr * rr
            px[i, j] = clamp(255 * limb * (0.10 + 0.90 * lit))
    light = light.resize((n, n), Image.BICUBIC)
    value = ImageChops.multiply(albedo, light)

    disc = Image.new("L", (n, n), 0)
    ImageDraw.Draw(disc).ellipse([c - r, c - r, c + r, c + r], fill=255)
    alpha = ImageChops.multiply(disc, light.point(lambda v: clamp(70 + v * 0.75)))
    rgb = Image.merge("RGB", (value, value.point(lambda v: v * 0.985), value.point(lambda v: v * 0.95)))
    out = Image.merge("RGBA", (*rgb.split(), alpha)).resize((size, size), Image.LANCZOS)
    return out


# ----------------------------------------------------------------- stars

def sprite(sigma, color, peak):
    s = max(3, int(sigma * 3.2))
    size = 2 * s + 1
    a = Image.new("L", (size, size))
    px = a.load()
    for j in range(size):
        for i in range(size):
            px[i, j] = clamp(peak * math.exp(-((i - s) ** 2 + (j - s) ** 2) / (2 * sigma * sigma)))
    return Image.merge("RGBA", (*Image.new("RGB", (size, size), color).split(), a))


def stars(w=1200, h=420, count=420, vector=16):
    sky = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    colors = [(255, 255, 255)] * 11 + [(200, 220, 255)] * 5 + [(255, 236, 208)] * 4
    made = []
    while len(made) < count:
        x, y = random.uniform(6, w - 6), random.uniform(6, h - 6)
        band = math.exp(-((y - (0.22 * x + 60)) / 150) ** 2)    # a faint diagonal richer band
        if random.random() > 0.5 + 0.5 * band:
            continue
        b = random.random() ** 2.8
        made.append((x, y, b, random.choice(colors)))
    made.sort(key=lambda s: -s[2])
    top, baked = made[:vector], made[vector:]
    for x, y, b, col in baked:
        sigma = 0.7 + 1.5 * b
        sp = sprite(sigma, col, 70 + 185 * b)
        sky.alpha_composite(sp, (int(x - sp.width / 2), int(y - sp.height / 2)))
        if b > 0.8:                                             # halo and faint spikes
            halo = sprite(sigma * 3, col, 40)
            sky.alpha_composite(halo, (int(x - halo.width / 2), int(y - halo.height / 2)))
            spikes = Image.new("RGBA", (33, 33), (0, 0, 0, 0))
            sd = ImageDraw.Draw(spikes)
            sd.line([16, 2, 16, 30], fill=col + (70,)); sd.line([2, 16, 30, 16], fill=col + (70,))
            spikes = spikes.filter(ImageFilter.GaussianBlur(0.8))
            sky.alpha_composite(spikes, (int(x - 16), int(y - 16)))
    fade = Image.new("L", (1, h))
    fp = fade.load()
    for y in range(h):
        fp[0, y] = clamp(255 * (1 - smoothstep(y / h, 0.55, 1.0)))
    alpha = ImageChops.multiply(sky.split()[3], fade.resize((w, h)))
    sky.putalpha(alpha)
    k = 800 / w
    shimmer = [{"x": round(x * k, 1), "y": round(y * k, 1), "r": round(1.6 + 1.6 * b, 2),
                "color": "#%02x%02x%02x" % col} for x, y, b, col in top]
    return sky, shimmer


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    out.mkdir(parents=True, exist_ok=True)
    moon().save(out / "moon.png", optimize=True)
    field, shimmer = stars()
    field.save(out / "stars.png", optimize=True)
    (out / "stars.json").write_text(json.dumps(shimmer))
    print("wrote moon.png, stars.png, stars.json in", out)
