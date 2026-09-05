#!/usr/bin/env python3
"""Bake the dusk sky that sits behind assets/intro.svg.

Pillow only, no numpy. Writes a 1600x900 JPEG (2x for an 800px card):

    python3 scripts/build_sky.py out.jpg

The clouds are fractal noise (several noise grids upscaled and summed),
lit from the upper right, composited over a periwinkle-to-apricot gradient.
"""

import sys
from PIL import Image, ImageChops, ImageFilter

W, H = 1600, 900

TOP, MID, BOTTOM = (0x5C, 0x6D, 0xBB), (0xB3, 0x9F, 0xD3), (0xF6, 0xC7, 0x95)
LIT, SHADOW = (0xFD, 0xE8, 0xD3), (0xB6, 0xA3, 0xD2)


def clamp(v, lo=0, hi=255):
    return max(lo, min(hi, int(round(v))))


def lerp(a, b, t):
    return tuple(clamp(a[i] + (b[i] - a[i]) * t) for i in range(3))


def smoothstep(v, lo, hi):
    t = max(0.0, min(1.0, (v - lo) / (hi - lo)))
    return clamp(255 * t * t * (3 - 2 * t))


def vertical(stops, mode="RGB"):
    """1xH column from (t, value) stops, then stretched to WxH."""
    col = Image.new(mode, (1, H))
    px = col.load()
    for y in range(H):
        t = y / (H - 1)
        for (t0, v0), (t1, v1) in zip(stops, stops[1:]):
            if t0 <= t <= t1:
                u = (t - t0) / (t1 - t0) if t1 > t0 else 0
                px[0, y] = lerp(v0, v1, u) if mode == "RGB" else clamp(v0 + (v1 - v0) * u)
                break
    return col.resize((W, H), Image.BILINEAR)


def radial(cx, cy, radius, strength, power=2.0):
    """L mask: `strength` at (cx, cy) falling smoothly to 0 at `radius`."""
    n = 129
    disc = Image.new("L", (n, n), 0)
    px = disc.load()
    for y in range(n):
        for x in range(n):
            r = ((x - 64) ** 2 + (y - 64) ** 2) ** 0.5 / 64
            px[x, y] = clamp(strength * max(0.0, 1 - r) ** power)
    disc = disc.resize((radius * 2, radius * 2), Image.BICUBIC)
    mask = Image.new("L", (W, H), 0)
    mask.paste(disc, (cx - radius, cy - radius))
    return mask


def corners(tl, tr, bl, br):
    """Smooth bilinear ramp between four corner values (L mask)."""
    tiny = Image.new("L", (2, 2))
    tiny.putdata([tl, tr, bl, br])
    return tiny.resize((W, H), Image.BILINEAR)


def fbm(grids, sigma=64, falloff=2.4):
    """Weighted sum of upscaled noise grids: octave i weighs 1/falloff^i."""
    acc, total = None, 0.0
    for i, (gw, gh) in enumerate(grids):
        layer = Image.effect_noise((gw, gh), sigma).resize((W, H), Image.BICUBIC)
        weight = 1 / (falloff ** i)
        acc = layer if acc is None else Image.blend(acc, layer, weight / (total + weight))
        total += weight
    return acc


def clouds(density, lit_shift=(-9, 9), soften=4, alpha_max=0.94, contrast=2.6):
    """Colour a density map with side lighting; returns (rgb, alpha)."""
    soft = density.filter(ImageFilter.GaussianBlur(soften))
    shifted = ImageChops.offset(soft, *lit_shift).filter(ImageFilter.GaussianBlur(8))
    shade = ImageChops.subtract(soft, shifted, 1.0, 128)              # 128 = flat
    shade = shade.point(lambda v: clamp((v - 128) * contrast + 150))   # push contrast, bias to lit
    rgb = Image.composite(Image.new("RGB", (W, H), LIT), Image.new("RGB", (W, H), SHADOW), shade)
    alpha = soft.point(lambda v: clamp(v * alpha_max))
    return rgb, alpha


def build():
    sky = vertical([(0.0, TOP), (0.55, MID), (1.0, BOTTOM)])

    # glows: sun below the horizon at lower right, cool halo under the moon
    sky = Image.composite(Image.new("RGB", (W, H), (0xFF, 0xDA, 0xA6)), sky, radial(1300, 1050, 1100, 95))
    sky = Image.composite(Image.new("RGB", (W, H), (0xE9, 0xEC, 0xFF)), sky, radial(300, 165, 420, 60))

    # main cumulus: big soft masses, dense in the lower half, thinning upward
    base = fbm([(6, 4), (12, 7), (24, 14), (48, 27), (96, 54), (192, 108)])
    density = base.point(lambda v: smoothstep(v, 112, 156))
    band = vertical([(0.0, 10), (0.25, 30), (0.55, 255), (1.0, 255)], mode="L")
    bank = corners(70, 40, 255, 180)          # heavier toward the lower left
    density = ImageChops.multiply(ImageChops.multiply(density, band), bank)
    rgb, alpha = clouds(density, contrast=3.0)
    sky = Image.composite(rgb, sky, alpha)

    # cirrus: strongly stretched noise, sparse, upper third only
    wisps = fbm([(5, 30), (10, 60), (20, 120), (40, 240)], sigma=60, falloff=2.0)
    wisps = wisps.point(lambda v: smoothstep(v, 138, 172))
    upper = vertical([(0.0, 255), (0.1, 255), (0.45, 0), (1.0, 0)], mode="L")
    wisps = ImageChops.multiply(wisps, upper)
    rgb, alpha = clouds(wisps, lit_shift=(-4, 4), soften=5, alpha_max=0.5, contrast=1.8)
    sky = Image.composite(rgb, sky, alpha)

    # vignette and grain
    vig = Image.radial_gradient("L").resize((W, H), Image.BICUBIC).point(lambda v: clamp((v - 150) * 0.9))
    sky = Image.composite(sky.point(lambda v: v * 0.86), sky, vig)
    grain = Image.effect_noise((W, H), 5).convert("RGB")
    sky = ImageChops.add(sky, grain, 1.0, -128)
    return sky


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "sky.jpg"
    build().save(out, "JPEG", quality=80, progressive=True, optimize=True)
    print("wrote", out)
