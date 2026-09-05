#!/usr/bin/env python3
"""Assemble assets/intro.svg from the baked sky and the wordmark outlines.

    python3 scripts/build_intro.py <inputs_dir> assets/intro.svg
    python3 scripts/build_intro.py <inputs_dir> test.svg --at 5.5     # jump to second 5.5

<inputs_dir> holds sky.jpg (build_sky.py) and wordmark.txt (build_wordmark.py).

The film: the lettering badge rises over the sky, a light sweeps the letters,
night falls (black, a small moon, a few golden sparkles), seven sentences play
one at a time, then dawn returns and the cover holds. --at shifts every delay
so a screenshot shows that exact moment.
"""

import base64
import re
import sys
from pathlib import Path

W, H = 800, 450
LINE1_Y, LINE2_Y, RIBBON_Y = 176, 310, 340
MOON_AT = (95, 70)
DEPTH, BEVEL = 15, 2.4
FACE, HIGHLIGHT, SHADE, EXTRUDE = "#f4917a", "#ffd8c8", "#d96a52", "#9c3626"
BAND, TABS, CAPTION_FILL = "#3a2670", "#2a1a52", "#fff3e6"
CAPTION = "FOUNDING AI ENGINEER · FIKA.AI · HYDERABAD"

SPARKLES = [(300, 60, 9), (520, 118, 6), (700, 68, 11), (640, 300, 5), (120, 300, 7), (420, 38, 4), (760, 190, 4)]
PINS = [(80, 96), (380, 160), (720, 340), (180, 400), (600, 30)]

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
    sparkles = "\n      ".join(
        f'<g transform="translate({x} {y})"><g class="sp" style="animation-duration:{2.6 + (i % 4) * 0.6:.1f}s;animation-delay:{-(i * 0.7) % 3:.1f}s">'
        f'<circle r="{r * 2.2:.1f}" fill="url(#sg)"/><path d="{sparkle_path(r)}" fill="#ffd98a"/></g></g>'
        for i, (x, y, r) in enumerate(SPARKLES))
    pins = "".join(f'<circle cx="{x}" cy="{y}" r="1.4" fill="#ffd98a" opacity="0.8"/>' for x, y in PINS)
    mx, my = MOON_AT
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
    <radialGradient id="sg"><stop offset="0" stop-color="#ffd98a" stop-opacity="0.55"/><stop offset="1" stop-color="#ffd98a" stop-opacity="0"/></radialGradient>
    <radialGradient id="mg"><stop offset="0" stop-color="#ffe9b8" stop-opacity="0.6"/><stop offset="1" stop-color="#ffe9b8" stop-opacity="0"/></radialGradient>
    <radialGradient id="md" cx="0.42" cy="0.38" r="0.7"><stop offset="0" stop-color="#fffaf0"/><stop offset="0.75" stop-color="#f6ead0"/><stop offset="1" stop-color="#dcc9a4"/></radialGradient>
    <filter id="lift" x="-10%" y="-20%" width="120%" height="150%"><feDropShadow dx="0" dy="8" stdDeviation="9" flood-color="#2a1d4a" flood-opacity="0.3"/></filter>
    <filter id="soft"><feGaussianBlur stdDeviation="2.6"/></filter>
  </defs>
  <style>
    .cap {{ font-family: ui-sans-serif, -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 12.5px; letter-spacing: 2.5px; fill: {CAPTION_FILL}; }}
    .s   {{ font-family: ui-sans-serif, -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 22px; fill: #fff8ee; }}

    .sky   {{ transform-box: fill-box; transform-origin: center; animation: drift 60s ease-in-out infinite alternate; }}
    .name  {{ opacity: 0; transform: translateY(10px); animation: rise 1.4s ease-out {d(NAME_IN)} forwards, hide {NIGHT_LEN:.1f}s linear {d(NIGHT_AT)} forwards; }}
    .sweep {{ opacity: 0.8; transform: translateX(0) skewX(-18deg); animation: sweep 1.2s ease-in-out {d(SWEEP_AT)} forwards; }}
    .night {{ opacity: 0; animation: night {NIGHT_LEN:.1f}s linear {d(NIGHT_AT)} forwards; }}
    .moon  {{ opacity: 0.78; animation: moonup {NIGHT_LEN:.1f}s linear {d(NIGHT_AT)} forwards; }}
    .halo  {{ opacity: 0.25; animation: haloup {NIGHT_LEN:.1f}s linear {d(NIGHT_AT)} forwards; }}
    .sp    {{ transform-box: fill-box; transform-origin: center; animation-name: twinkle; animation-timing-function: ease-in-out; animation-iteration-count: infinite; animation-direction: alternate; }}
    .f     {{ opacity: 0; animation: say {FRAME}s ease-in-out forwards; }}
{delays}

    @keyframes drift   {{ from {{ transform: scale(1); }} to {{ transform: scale(1.06); }} }}
    @keyframes rise    {{ to {{ opacity: 1; transform: translateY(0); }} }}
    @keyframes sweep   {{ to {{ transform: translateX(600px) skewX(-18deg); }} }}
    @keyframes hide    {{ 0% {{ opacity: 1; }} {night_in:.2f}% {{ opacity: 0; }} {night_out:.2f}% {{ opacity: 0; }} 100% {{ opacity: 1; }} }}
    @keyframes night   {{ 0% {{ opacity: 0; }} {night_in:.2f}% {{ opacity: 1; }} {night_out:.2f}% {{ opacity: 1; }} 100% {{ opacity: 0; }} }}
    @keyframes moonup  {{ 0% {{ opacity: 0.78; }} {night_in:.2f}% {{ opacity: 1; }} {night_out:.2f}% {{ opacity: 1; }} 100% {{ opacity: 0.78; }} }}
    @keyframes haloup  {{ 0% {{ opacity: 0.25; }} {night_in:.2f}% {{ opacity: 0.55; }} {night_out:.2f}% {{ opacity: 0.55; }} 100% {{ opacity: 0.25; }} }}
    @keyframes twinkle {{ from {{ opacity: 0.55; transform: scale(0.9); }} to {{ opacity: 1; transform: scale(1.06); }} }}
    @keyframes say     {{ 0% {{ opacity: 0; transform: translateY(4px); }} 16% {{ opacity: 1; transform: translateY(0); }} 84% {{ opacity: 1; transform: translateY(0); }} 100% {{ opacity: 0; transform: translateY(0); }} }}

    @media (prefers-reduced-motion: reduce) {{
      .sky, .name, .moon, .halo, .sp {{ animation: none; opacity: 1; transform: none; }}
      .moon {{ opacity: 0.78; }} .halo {{ opacity: 0.25; }}
      .sweep, .night, .f {{ display: none; }}
    }}
  </style>

  <g clip-path="url(#frame)">
    <image class="sky" width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice" href="{data_uri(inputs / 'sky.jpg', 'image/jpeg')}"/>

    <!-- night: black, a few golden sparkles -->
    <g class="night">
      <rect width="{W}" height="{H}" fill="#000"/>
      {sparkles}
      {pins}
    </g>

    <!-- moon: above the night so it shines on the frames -->
    <g transform="translate({mx} {my})">
      <circle class="halo" r="80" fill="url(#mg)"/>
      <g class="moon">
        <circle r="30" fill="url(#md)"/>
        <g fill="#c9b48e" opacity="0.22" filter="url(#soft)"><ellipse cx="-9" cy="-8" rx="9" ry="7"/><ellipse cx="6" cy="-3" rx="7" ry="6"/><ellipse cx="-4" cy="9" rx="6" ry="4"/><ellipse cx="12" cy="8" rx="4" ry="3"/></g>
      </g>
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
