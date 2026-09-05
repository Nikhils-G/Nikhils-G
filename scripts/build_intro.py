#!/usr/bin/env python3
"""Assemble assets/intro.svg from the baked sky and the wordmark outlines.

    python3 scripts/build_intro.py <inputs_dir> assets/intro.svg
    python3 scripts/build_intro.py <inputs_dir> test.svg --at 5.5     # jump to second 5.5

<inputs_dir> holds sky.jpg (build_sky.py) and wordmark.txt (build_wordmark.py).

The film: the lettering badge rises over the sky, a light sweeps the letters,
night falls to black and a wishing star sweeps through once, leaving golden
stardust that glints and dissolves; a few motes linger while seven sentences
play one at a time; then dawn returns and the cover holds. --at shifts every
delay so a screenshot shows that exact moment.
"""

import base64
import math
import random
import re
import sys
from pathlib import Path

W, H = 800, 450
LINE1_Y, LINE2_Y, RIBBON_Y = 176, 310, 340
DEPTH, BEVEL = 15, 2.4
FACE, HIGHLIGHT, SHADE, EXTRUDE = "#f4917a", "#ffd8c8", "#d96a52", "#9c3626"
BAND, TABS, CAPTION_FILL = "#3a2670", "#2a1a52", "#fff3e6"
CAPTION = "FOUNDING AI ENGINEER · FIKA.AI · HYDERABAD"

# the wishing star's path: in from the lower left, up past the top left, a loop over the top, out at the top right
TRAIL = [((-20, 380), (70, 330), (30, 160), (140, 120)), ((140, 120), (230, 80), (350, 30), (430, 50)),
         ((430, 50), (500, 70), (500, 150), (420, 150)), ((420, 150), (340, 150), (330, 60), (410, 40)),
         ((410, 40), (520, 20), (640, 50), (700, 110))]
PARTICLES, TRAVEL = 220, 3.4
MOTES = [(250, 70), (560, 60), (700, 150), (90, 250), (740, 300), (170, 120), (640, 380), (330, 400)]

FRAMES = [
    ("I build AI agents and the models behind them,",
     "end to end: from training and fine-tuning to production."),
    ("When turn detection wasn't good enough, I trained my own:",
     "TurnWave, a 7M-parameter transformer, from scratch in PyTorch."),
    ("Fine-tuned Qwen2.5-7B with QLoRA and served it on vLLM.",
     "Built a 200k-pair dataset that beat the baseline: F1 0.798 vs 0.753."),
    ("Real-time voice agents on LiveKit, STT to LLM to TTS,",
     "in Hindi and Telugu, on live phone calls."),
    ("A collections agent lifting recovery by around 50%.",
     "A dialer placing 30,000 calls a day."),
    ("WhatsApp agents that take payments without leaving the chat.",),
    ("Available today, for voice AI, agents, and fine-tuning.",),
]

# timeline (seconds)
NAME_IN, SWEEP_AT = 0.0, 2.0
NIGHT_AT, FIRST, FRAME = 3.2, 4.0, 2.8
NIGHT_LEN = FIRST + FRAME * len(FRAMES) - NIGHT_AT + 1.0   # fades out over the last second

ARIA = ("Nikhil Sukthe, Founding AI Engineer at Fika.ai, Hyderabad. "
        + " ".join(" ".join(lines) for lines in FRAMES))


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def data_uri(path, mime):
    return f"data:{mime};base64," + base64.b64encode(Path(path).read_bytes()).decode()


def sparkle_path(r):
    return f"M0 {-r} Q0 0 {r} 0 Q0 0 0 {r} Q0 0 {-r} 0 Q0 0 0 {-r} Z"


def rounded_star(R, inner=0.48, k_out=0.30, k_in=0.22):
    """five-point star with softened tips, centred on the origin"""
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rad = R if i % 2 == 0 else R * inner
        pts.append((rad * math.cos(a), rad * math.sin(a)))
    d = []
    for i, v in enumerate(pts):
        p, n = pts[i - 1], pts[(i + 1) % 10]
        k = k_out if i % 2 == 0 else k_in
        a = (v[0] + (p[0] - v[0]) * k, v[1] + (p[1] - v[1]) * k)
        b = (v[0] + (n[0] - v[0]) * k, v[1] + (n[1] - v[1]) * k)
        d.append(("M" if i == 0 else "L") + f"{a[0]:.1f},{a[1]:.1f}")
        d.append(f"Q{v[0]:.1f},{v[1]:.1f} {b[0]:.1f},{b[1]:.1f}")
    return " ".join(d) + " Z"


def bezier(p0, p1, p2, p3, t):
    u = 1 - t
    return (u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
            u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1])


def sample_path(segments, n):
    """n points (x, y, nx, ny) at equal arc length along cubic segments, the polyline and its length"""
    poly = [bezier(*seg, i / 60) for seg in segments for i in range(60)] + [segments[-1][3]]
    cum = [0.0]
    for a, b in zip(poly, poly[1:]):
        cum.append(cum[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    length, out = cum[-1], []
    for k in range(n):
        target, j = length * k / (n - 1), 0
        while j < len(cum) - 2 and cum[j + 1] < target:
            j += 1
        seg = cum[j + 1] - cum[j] or 1
        f = (target - cum[j]) / seg
        (ax, ay), (bx, by) = poly[j], poly[j + 1]
        out.append((ax + (bx - ax) * f, ay + (by - ay) * f, -(by - ay) / seg, (bx - ax) / seg))
    return out, poly, length


def trail_markup(d):
    """the wishing star, its stardust, the haze band and the vanish burst; d() shifts delays for --at"""
    rng = random.Random(9)
    points, poly, length = sample_path(TRAIL, PARTICLES)
    t0 = FIRST
    dust = []
    for i, (x, y, nx, ny) in enumerate(points):
        s = i / (PARTICLES - 1)
        spread = 2.5 + 11 * s ** 1.3
        off, along = rng.gauss(0, spread), rng.uniform(-4, 4)
        px, py = x + nx * off - ny * along, y + ny * off + nx * along
        color = rng.choices(["#ffd24a", "#ffe9a0", "#ffb02e", "#fff8e6"], [40, 30, 15, 15])[0]
        style = (f'style="animation-delay:{d(t0 + s * TRAVEL + rng.uniform(-0.12, 0.12))};'
                 f'animation-duration:{1.1 + rng.uniform(0, 0.7):.2f}s"')
        if rng.random() < 0.09:
            dust.append(f'<g transform="translate({px:.1f} {py:.1f})"><path class="dust" d="{sparkle_path(rng.uniform(2.6, 4.6))}" fill="{color}" {style}/></g>')
        else:
            r = rng.choices([0.7, 1.0, 1.4, 2.0, 2.8], [30, 30, 20, 12, 8])[0]
            glow = f'<circle r="{r * 3:.1f}" fill="url(#pg)"/>' if r >= 2.0 else ""
            dust.append(f'<g transform="translate({px:.1f} {py:.1f})"><g class="dust" {style}>{glow}<circle r="{r}" fill="{color}"/></g></g>')
    ex, ey = points[-1][0], points[-1][1]
    burst = "".join(
        f'<g transform="translate({ex:.1f} {ey:.1f}) rotate({k * 30 + rng.uniform(-10, 10):.0f})">'
        f'<circle class="burst" r="{rng.choice([1, 1.4, 2])}" fill="#ffe08a" style="animation-delay:{d(t0 + TRAVEL)}"/></g>'
        for k in range(12))
    stops = " ".join(
        f"{k / 24 * 100:.1f}% {{ transform: translate({points[round(k / 24 * (PARTICLES - 1))][0]:.1f}px, "
        f"{points[round(k / 24 * (PARTICLES - 1))][1]:.1f}px) rotate({k * 15}deg); }}" for k in range(25))
    band = 0.32 * length
    haze_dur = TRAVEL * (length + band) / length
    haze_path = "M" + " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in poly[::3])
    star = rounded_star(20)
    markup = (f'<path class="haze" d="{haze_path}" fill="none" stroke="#ffcf5a" stroke-width="18" stroke-linecap="round" opacity="0.28" filter="url(#haze)"/>\n'
              f'      {"".join(dust)}\n      {burst}\n'
              f'      <g class="head"><g transform="scale(0.42)"><circle r="46" fill="url(#hg)"/><path d="{star}" fill="url(#starfill)"/>'
              f'<path d="{star}" fill="#fff" opacity="0.5" transform="translate(-2 -2) scale(0.55)"/></g></g>')
    css = (f"    .haze {{ stroke-dasharray: {band:.0f} {length:.0f}; stroke-dashoffset: {band:.0f}; animation: haze {haze_dur:.2f}s linear {d(t0)} forwards; }}\n"
           f"    .head {{ opacity: 0; animation: head {TRAVEL}s linear {d(t0)} forwards, headfade {TRAVEL}s linear {d(t0)} forwards; }}\n"
           f"    @keyframes haze {{ to {{ stroke-dashoffset: {-length:.0f}; }} }}\n"
           f"    @keyframes head {{ {stops} }}")
    return markup, css


def motes_markup(d):
    """faint dust left behind after the star has passed; they pulse and drift until dawn"""
    rng = random.Random(4)
    markup, css = [], []
    for i, (x, y) in enumerate(MOTES):
        start = 8.6 + i * 0.25
        r = rng.choice([0.9, 1.2, 1.6])
        glow = f'<circle r="{r * 4:.1f}" fill="url(#pg)"/>' if i in (1, 5) else ""
        markup.append(f'<g transform="translate({x} {y})"><g class="mote m{i}">{glow}<circle r="{r}" fill="#ffe08a"/></g></g>')
        css.append(f"    .m{i} {{ animation-delay: {d(start)}, {d(start + 1.2)}, {d(start)}; animation-duration: 1.2s, {3 + (i % 3):.0f}s, 14s; }}")
    return "".join(markup), "\n".join(css)


def word_block(gid):
    """extrusion, face, then the bevel: lighter top-left edges, darker bottom-right edges"""
    extrusion = "".join(f'<use href="#{gid}" transform="translate({k} {k})"/>' for k in range(DEPTH, 0, -1))
    return (f'<g fill="{EXTRUDE}">{extrusion}</g>\n'
            f'        <use href="#{gid}" fill="{FACE}"/>\n'
            f'        <use href="#{gid}" fill="{HIGHLIGHT}" mask="url(#{gid}-hi)"/>\n'
            f'        <use href="#{gid}" fill="{SHADE}" mask="url(#{gid}-sh)"/>')


def masks(gid, paths):
    region = 'maskUnits="userSpaceOnUse" x="-400" y="-200" width="800" height="300"'
    return (f'<mask id="{gid}-hi" {region}><g fill="#fff">{paths}</g><g fill="#000" transform="translate({BEVEL} {BEVEL})">{paths}</g></mask>\n'
            f'    <mask id="{gid}-sh" {region}><g fill="#fff">{paths}</g><g fill="#000" transform="translate(-{BEVEL} -{BEVEL})">{paths}</g></mask>')


def frames_markup():
    out = []
    for i, lines in enumerate(FRAMES, 1):
        if len(lines) == 1:
            body = f'<text class="s" x="400" y="232" text-anchor="middle">{esc(lines[0])}</text>'
        else:
            body = (f'<text class="s" x="400" y="216" text-anchor="middle"><tspan x="400">{esc(lines[0])}</tspan>'
                    f'<tspan x="400" dy="32">{esc(lines[1])}</tspan></text>')
        out.append(f'<g class="f f{i}">{body}</g>')
    return "\n    ".join(out)


def build(inputs, at=0.0):
    inputs = Path(inputs)
    words = {m.group(1): "".join(re.findall(r"<path[^>]*/>", m.group(2)))
             for m in re.finditer(r'<g id="(w\d)">(.*?)</g>', (inputs / "wordmark.txt").read_text(), re.S)}
    w1, w2 = words["w1"], words["w2"]
    w2_shifted = w2.replace('transform="', f'transform="translate(0 {LINE2_Y - LINE1_Y}) ')
    d = lambda t: f"{t - at:.2f}s"
    delays = "\n".join(f"    .f{i} {{ animation-delay: {d(FIRST + FRAME * (i - 1))}; }}" for i in range(1, len(FRAMES) + 1))
    night_in, night_out = 0.8 / NIGHT_LEN * 100, (NIGHT_LEN - 1.0) / NIGHT_LEN * 100
    trail, trail_css = trail_markup(d)
    motes, motes_css = motes_markup(d)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(ARIA)}">
  <!-- Built by scripts/build_intro.py from scripts/build_sky.py and scripts/build_wordmark.py. Lettering: Anton (SIL Open Font License 1.1) as outlines. -->
  <defs>
    <clipPath id="frame"><rect width="{W}" height="{H}" rx="12"/></clipPath>
    <g id="w1">{w1}</g>
    <g id="w2">{w2}</g>
    {masks("w1", w1)}
    {masks("w2", w2)}
    <clipPath id="wm-clip">{w1}{w2_shifted}</clipPath>
    <linearGradient id="sweep-grad" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff0dd" stop-opacity="0"/><stop offset="0.5" stop-color="#fff0dd" stop-opacity="1"/><stop offset="1" stop-color="#fff0dd" stop-opacity="0"/></linearGradient>
    <radialGradient id="pg"><stop offset="0" stop-color="#ffd24a" stop-opacity="0.6"/><stop offset="1" stop-color="#ffd24a" stop-opacity="0"/></radialGradient>
    <radialGradient id="hg"><stop offset="0" stop-color="#ffe08a" stop-opacity="0.8"/><stop offset="1" stop-color="#ffe08a" stop-opacity="0"/></radialGradient>
    <linearGradient id="starfill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffe36a"/><stop offset="1" stop-color="#f6ad1c"/></linearGradient>
    <filter id="lift" x="-10%" y="-20%" width="120%" height="150%"><feDropShadow dx="0" dy="8" stdDeviation="9" flood-color="#2a1d4a" flood-opacity="0.3"/></filter>
    <filter id="haze" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="7"/></filter>
  </defs>
  <style>
    .cap {{ font-family: ui-sans-serif, -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 12.5px; letter-spacing: 2.5px; fill: {CAPTION_FILL}; }}
    .s   {{ font-family: ui-sans-serif, -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 22px; fill: #fff8ee; }}

    .sky   {{ transform-box: fill-box; transform-origin: center; animation: drift 60s ease-in-out infinite alternate; }}
    .name  {{ opacity: 0; transform: translateY(10px); animation: rise 1.4s ease-out {d(NAME_IN)} forwards, hide {NIGHT_LEN:.1f}s linear {d(NIGHT_AT)} forwards; }}
    .sweep {{ opacity: 0.8; transform: translateX(0) skewX(-18deg); animation: sweep 1.2s ease-in-out {d(SWEEP_AT)} forwards; }}
    .night {{ opacity: 0; animation: night {NIGHT_LEN:.1f}s linear {d(NIGHT_AT)} forwards; }}
    .dust  {{ opacity: 0; transform-box: fill-box; transform-origin: center; animation-name: dust; animation-timing-function: ease-out; animation-fill-mode: forwards; }}
    .burst {{ opacity: 0; animation: burst 1.1s ease-out forwards; }}
    .mote  {{ opacity: 0; transform-box: fill-box; transform-origin: center; animation-name: motein, motepulse, motedrift; animation-timing-function: ease-out, ease-in-out, linear; animation-iteration-count: 1, infinite, 1; animation-direction: normal, alternate, normal; animation-fill-mode: forwards, none, forwards; }}
{motes_css}
{trail_css}
    .f     {{ opacity: 0; animation: say {FRAME}s ease-in-out forwards; }}
{delays}

    @keyframes drift   {{ from {{ transform: scale(1); }} to {{ transform: scale(1.06); }} }}
    @keyframes rise    {{ to {{ opacity: 1; transform: translateY(0); }} }}
    @keyframes sweep   {{ to {{ transform: translateX(600px) skewX(-18deg); }} }}
    @keyframes hide    {{ 0% {{ opacity: 1; }} {night_in:.2f}% {{ opacity: 0; }} {night_out:.2f}% {{ opacity: 0; }} 100% {{ opacity: 1; }} }}
    @keyframes night   {{ 0% {{ opacity: 0; }} {night_in:.2f}% {{ opacity: 1; }} {night_out:.2f}% {{ opacity: 1; }} 100% {{ opacity: 0; }} }}
    @keyframes dust    {{ 0% {{ opacity: 0; transform: scale(0.2); }} 30% {{ opacity: 1; transform: scale(1); }} 100% {{ opacity: 0; transform: translateY(-9px) scale(0.5); }} }}
    @keyframes burst   {{ 0% {{ opacity: 1; transform: translateX(0); }} 100% {{ opacity: 0; transform: translateX(22px); }} }}
    @keyframes headfade {{ 0% {{ opacity: 0; }} 6% {{ opacity: 1; }} 88% {{ opacity: 1; }} 100% {{ opacity: 0; }} }}
    @keyframes motein  {{ to {{ opacity: 0.55; }} }}
    @keyframes motepulse {{ from {{ opacity: 0.35; }} to {{ opacity: 0.8; }} }}
    @keyframes motedrift {{ to {{ transform: translateY(-10px); }} }}
    @keyframes say     {{ 0% {{ opacity: 0; transform: translateY(4px); }} 16% {{ opacity: 1; transform: translateY(0); }} 84% {{ opacity: 1; transform: translateY(0); }} 100% {{ opacity: 0; transform: translateY(0); }} }}

    @media (prefers-reduced-motion: reduce) {{
      .sky, .name {{ animation: none; opacity: 1; transform: none; }}
      .sweep, .night, .f {{ display: none; }}
    }}
  </style>

  <g clip-path="url(#frame)">
    <image class="sky" width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice" href="{data_uri(inputs / 'sky.jpg', 'image/jpeg')}"/>

    <!-- night: black; a wishing star sweeps through once, its dust lingers as motes -->
    <g class="night">
      <rect width="{W}" height="{H}" fill="#000"/>
      {trail}
      {motes}
    </g>

    <!-- cover: two arched lines, extruded and bevelled, with a ribbon for the caption -->
    <g class="name">
      <g filter="url(#lift)">
        <g transform="translate(400 {LINE1_Y})">
        {word_block("w1")}
        </g>
        <g transform="translate(400 {LINE2_Y})">
        {word_block("w2")}
        </g>
        <g transform="translate(400 {RIBBON_Y})">
          <path fill="{TABS}" d="M-256 6 h36 v36 h-36 l10 -18 z M256 6 h-36 v36 h36 l-10 -18 z"/>
          <path fill="{TABS}" opacity="0.6" d="M-220 30 v12 l12 -12 z M220 30 v12 l-12 -12 z"/>
          <rect fill="{BAND}" x="-232" y="0" width="464" height="30"/>
          <text class="cap" y="20" text-anchor="middle">{esc(CAPTION)}</text>
        </g>
      </g>
      <g clip-path="url(#wm-clip)" transform="translate(400 {LINE1_Y})">
        <rect class="sweep" x="-380" y="-130" width="110" height="330" fill="url(#sweep-grad)"/>
      </g>
    </g>

    <!-- frames -->
    {frames_markup()}
  </g>
</svg>
'''


if __name__ == "__main__":
    args = sys.argv[1:]
    at = float(args[args.index("--at") + 1]) if "--at" in args else 0.0
    files = [a for a in args if not a.startswith("--") and a != str(at)]
    inputs, out = files[0], files[1]
    Path(out).write_text(build(inputs, at))
    print("wrote", out, "at", at)
