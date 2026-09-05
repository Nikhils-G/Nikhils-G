#!/usr/bin/env python3
"""Assemble assets/intro.svg from the baked layers and the wordmark outlines.

    python3 scripts/build_intro.py <inputs_dir> assets/intro.svg
    python3 scripts/build_intro.py <inputs_dir> test.svg --at 5.5     # jump to second 5.5

<inputs_dir> holds sky.jpg (build_sky.py), moon.png + stars.png + stars.json
(build_night.py) and wordmark.txt (build_wordmark.py).

The film: the 3D name rises over the sky, a light sweeps the letters, night
falls with stars, seven labelled frames play one at a time with a progress
row, then dawn returns and the cover holds. --at shifts every delay so a
screenshot shows that exact moment.
"""

import base64
import json
import sys
from pathlib import Path

W, H = 800, 450
BASELINE, CAPTION_Y = 256, 326
MOON = (85, 17, 130)          # x, y, size on the card
DEPTH = 14                    # extrusion layers

FRAMES = [
    ("MODELS", ("I build AI agents and the models behind them,",
                "end to end: from training and fine-tuning to production.")),
    ("TURN DETECTION", ("When turn detection wasn't good enough, I trained my own:",
                        "TurnWave, a 7M-parameter transformer, from scratch in PyTorch.")),
    ("FINE-TUNING", ("Fine-tuned Qwen2.5-7B with QLoRA and served it on vLLM.",
                     "Built a 200k-pair dataset that beat the baseline: F1 0.798 vs 0.753.")),
    ("VOICE", ("Real-time voice agents on LiveKit, STT to LLM to TTS,",
               "in Hindi and Telugu, on live phone calls.")),
    ("IN PRODUCTION", ("A collections agent lifting recovery by around 50%.",
                       "A dialer placing 30,000 calls a day.")),
    ("WHATSAPP", ("WhatsApp agents that take payments without leaving the chat.",)),
    ("AVAILABILITY", ("Available today, for voice AI, agents, and fine-tuning.",)),
]

# timeline (seconds)
NAME_IN, CAP_IN, SWEEP_AT = 0.0, 1.2, 2.0
NIGHT_AT, FIRST, FRAME = 3.2, 4.0, 2.8
NIGHT_LEN = FIRST + FRAME * len(FRAMES) - NIGHT_AT + 1.0   # fades out over the last second

CAPTION = "FOUNDING AI ENGINEER · FIKA.AI · HYDERABAD"
ARIA = ("Nikhil Sukthe, Founding AI Engineer at Fika.ai, Hyderabad. "
        + " ".join(" ".join(lines) for _, lines in FRAMES))


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def data_uri(path, mime):
    return f"data:{mime};base64," + base64.b64encode(Path(path).read_bytes()).decode()


def frames_markup():
    n = len(FRAMES)
    dot_x = lambda i: W / 2 + (i - (n - 1) / 2) * 16
    out = []
    for i, (label, lines) in enumerate(FRAMES, 1):
        if len(lines) == 1:
            body = f'<text class="lbl" x="400" y="198" text-anchor="middle">{esc(label)}</text>\n' \
                   f'      <text class="s" x="400" y="238" text-anchor="middle">{esc(lines[0])}</text>'
        else:
            body = f'<text class="lbl" x="400" y="190" text-anchor="middle">{esc(label)}</text>\n' \
                   f'      <text class="s" x="400" y="228" text-anchor="middle"><tspan x="400">{esc(lines[0])}</tspan>' \
                   f'<tspan x="400" dy="32">{esc(lines[1])}</tspan></text>'
        out.append(f'<g class="f f{i}">\n      {body}\n'
                   f'      <circle cx="{dot_x(i - 1):.0f}" cy="402" r="6" fill="#f0a63a" opacity="0.35"/>'
                   f'<circle cx="{dot_x(i - 1):.0f}" cy="402" r="3" fill="#f0a63a"/>\n    </g>')
    dots = "".join(f'<circle cx="{dot_x(i):.0f}" cy="402" r="2.5" fill="#fff" opacity="0.3"/>' for i in range(n))
    return "\n    ".join(out), dots


def build(inputs, at=0.0):
    inputs = Path(inputs)
    wm = [l for l in (inputs / "wordmark.txt").read_text().splitlines() if l.strip().startswith("<path")]
    paths = "\n".join(wm)
    shimmer = json.loads((inputs / "stars.json").read_text())
    d = lambda t: f"{t - at:.2f}s"
    delays = "\n".join(f"    .f{i} {{ animation-delay: {d(FIRST + FRAME * (i - 1))}; }}" for i in range(1, len(FRAMES) + 1))
    night_in, night_out = 0.8 / NIGHT_LEN * 100, (NIGHT_LEN - 1.0) / NIGHT_LEN * 100
    extrude = "".join(f'<use href="#wordmark" transform="translate({k} {k})"/>' for k in range(DEPTH, 0, -1))
    shimmer_markup = "\n      ".join(
        f'<circle cx="{s["x"]}" cy="{s["y"]}" r="{s["r"]}" fill="url(#star)" '
        f'style="animation-duration:{2.8 + (i % 5) * 0.7:.1f}s;animation-delay:{-(i * 0.9) % 4:.1f}s"/>'
        for i, s in enumerate(shimmer))
    frames, dots = frames_markup()
    mx, my, ms = MOON
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(ARIA)}">
  <!-- Built by scripts/build_intro.py from scripts/build_sky.py, scripts/build_night.py and scripts/build_wordmark.py. Lettering: Anton (SIL Open Font License 1.1) as outlines. -->
  <defs>
    <clipPath id="frame"><rect width="{W}" height="{H}" rx="12"/></clipPath>
    <g id="wordmark">
{paths}
    </g>
    <clipPath id="wm-clip">
{paths}
    </clipPath>
    <linearGradient id="face" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff3e5"/><stop offset="1" stop-color="#ffc190"/></linearGradient>
    <linearGradient id="sweep-grad" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffb347" stop-opacity="0"/><stop offset="0.5" stop-color="#ffb347" stop-opacity="1"/><stop offset="1" stop-color="#ffb347" stop-opacity="0"/></linearGradient>
    <linearGradient id="nightgrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#06051a"/><stop offset="0.6" stop-color="#120c2a"/><stop offset="1" stop-color="#2a1a3a"/></linearGradient>
    <radialGradient id="star"><stop offset="0" stop-color="#fff"/><stop offset="0.35" stop-color="#fff" stop-opacity="0.9"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
    <filter id="glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="18"/></filter>
    <filter id="shadow" x="-10%" y="-40%" width="120%" height="180%"><feDropShadow dx="0" dy="2" stdDeviation="5" flood-color="#2a1d4a" flood-opacity="0.5"/></filter>
    <filter id="lift" x="-10%" y="-20%" width="120%" height="150%"><feDropShadow dx="0" dy="10" stdDeviation="10" flood-color="#2a1d4a" flood-opacity="0.28"/></filter>
  </defs>
  <style>
    .cap {{ font-family: ui-sans-serif, -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 12.5px; letter-spacing: 2.5px; fill: #fff; }}
    .lbl {{ font-family: ui-sans-serif, -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 11.5px; letter-spacing: 3px; fill: #f0a63a; }}
    .s   {{ font-family: ui-sans-serif, -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 22px; fill: #fff; }}

    .sky   {{ transform-box: fill-box; transform-origin: center; animation: drift 60s ease-in-out infinite alternate; }}
    .name  {{ opacity: 0; transform: translateY(10px); animation: rise 1.4s ease-out {d(NAME_IN)} forwards, hide {NIGHT_LEN:.1f}s linear {d(NIGHT_AT)} forwards; }}
    .cap   {{ opacity: 0; animation: fade 0.8s ease-out {d(CAP_IN)} forwards, hidecap {NIGHT_LEN:.1f}s linear {d(NIGHT_AT)} forwards; }}
    .sweep {{ opacity: 0.85; transform: translateX(0) skewX(-18deg); animation: sweep 1.2s ease-in-out {d(SWEEP_AT)} forwards; }}
    .night {{ opacity: 0; animation: night {NIGHT_LEN:.1f}s linear {d(NIGHT_AT)} forwards; }}
    .moon  {{ opacity: 0.82; animation: moonup {NIGHT_LEN:.1f}s linear {d(NIGHT_AT)} forwards; }}
    .halo  {{ opacity: 0.16; animation: haloup {NIGHT_LEN:.1f}s linear {d(NIGHT_AT)} forwards; }}
    .shimmer circle {{ animation-name: shimmer; animation-timing-function: ease-in-out; animation-iteration-count: infinite; animation-direction: alternate; }}
    .f     {{ opacity: 0; animation: say {FRAME}s ease-in-out forwards; }}
{delays}

    @keyframes drift   {{ from {{ transform: scale(1); }} to {{ transform: scale(1.06); }} }}
    @keyframes rise    {{ to {{ opacity: 1; transform: translateY(0); }} }}
    @keyframes fade    {{ to {{ opacity: 0.88; }} }}
    @keyframes sweep   {{ to {{ transform: translateX(600px) skewX(-18deg); }} }}
    @keyframes hide    {{ 0% {{ opacity: 1; }} {night_in:.2f}% {{ opacity: 0; }} {night_out:.2f}% {{ opacity: 0; }} 100% {{ opacity: 1; }} }}
    @keyframes hidecap {{ 0% {{ opacity: 0.88; }} {night_in:.2f}% {{ opacity: 0; }} {night_out:.2f}% {{ opacity: 0; }} 100% {{ opacity: 0.88; }} }}
    @keyframes night   {{ 0% {{ opacity: 0; }} {night_in:.2f}% {{ opacity: 1; }} {night_out:.2f}% {{ opacity: 1; }} 100% {{ opacity: 0; }} }}
    @keyframes moonup  {{ 0% {{ opacity: 0.82; }} {night_in:.2f}% {{ opacity: 1; }} {night_out:.2f}% {{ opacity: 1; }} 100% {{ opacity: 0.82; }} }}
    @keyframes haloup  {{ 0% {{ opacity: 0.16; }} {night_in:.2f}% {{ opacity: 0.34; }} {night_out:.2f}% {{ opacity: 0.34; }} 100% {{ opacity: 0.16; }} }}
    @keyframes shimmer {{ from {{ opacity: 0.6; }} to {{ opacity: 1; }} }}
    @keyframes say     {{ 0% {{ opacity: 0; transform: translateY(4px); }} 16% {{ opacity: 1; transform: translateY(0); }} 84% {{ opacity: 1; transform: translateY(0); }} 100% {{ opacity: 0; transform: translateY(0); }} }}

    @media (prefers-reduced-motion: reduce) {{
      .sky, .name, .cap, .moon, .halo {{ animation: none; opacity: 1; transform: none; }}
      .cap {{ opacity: 0.88; }} .moon {{ opacity: 0.82; }} .halo {{ opacity: 0.16; }}
      .sweep, .night, .f {{ display: none; }}
    }}
  </style>

  <g clip-path="url(#frame)">
    <image class="sky" width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice" href="{data_uri(inputs / 'sky.jpg', 'image/jpeg')}"/>

    <!-- night: sky gradient, baked stars, shimmering bright stars, progress row -->
    <g class="night">
      <rect width="{W}" height="{H}" fill="url(#nightgrad)" opacity="0.94"/>
      <image x="0" y="0" width="{W}" height="280" href="{data_uri(inputs / 'stars.png', 'image/png')}"/>
      <g class="shimmer">
      {shimmer_markup}
      </g>
      {dots}
    </g>

    <!-- moon: above the night so it shines on the frames -->
    <circle class="halo" cx="{mx + ms / 2}" cy="{my + ms / 2}" r="{ms * 0.62:.0f}" fill="#fff" filter="url(#glow)"/>
    <image class="moon" x="{mx}" y="{my}" width="{ms}" height="{ms}" href="{data_uri(inputs / 'moon.png', 'image/png')}"/>

    <!-- cover: extruded lettering on an arc, then a light sweep -->
    <g class="name">
      <g transform="translate(400 {BASELINE})" filter="url(#lift)">
        <g fill="#2f1f5c">{"".join(f'<use href="#wordmark" transform="translate({k} {k})"/>' for k in range(DEPTH, DEPTH - 3, -1))}</g>
        <g fill="#4a3585">{"".join(f'<use href="#wordmark" transform="translate({k} {k})"/>' for k in range(DEPTH - 3, 0, -1))}</g>
        <use href="#wordmark" fill="url(#face)" stroke="#3a2670" stroke-width="0.8" stroke-opacity="0.5"/>
      </g>
      <g clip-path="url(#wm-clip)" transform="translate(400 {BASELINE})">
        <rect class="sweep" x="-380" y="-130" width="110" height="170" fill="url(#sweep-grad)"/>
      </g>
    </g>
    <text class="cap" x="400" y="{CAPTION_Y}" text-anchor="middle" filter="url(#shadow)">{esc(CAPTION)}</text>

    <!-- frames -->
    {frames}
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
