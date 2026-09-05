#!/usr/bin/env python3
"""Assemble assets/intro.svg from the baked sky and the wordmark outlines.

    python3 scripts/build_intro.py sky.jpg wordmark.txt assets/intro.svg
    python3 scripts/build_intro.py sky.jpg wordmark.txt test.svg --at 5.5   # jump to second 5.5

The film: the name and caption rise over the sky, a light sweeps the letters,
night falls, seven sentences play one at a time, then dawn returns and the
cover holds. --at shifts every delay so a screenshot shows that exact moment.
"""

import base64
import random
import sys

W, H = 800, 450
BASELINE, CAPTION_Y = 240, 276

SENTENCES = [
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
NAME_IN, CAP_IN, SWEEP_AT = 0.0, 1.2, 2.0
NIGHT_AT, FRAME = 3.2, 2.8
FIRST = 4.0
NIGHT_LEN = FIRST + FRAME * len(SENTENCES) - NIGHT_AT + 1.0   # fades out over the last second

CAPTION = "FOUNDING AI ENGINEER · FIKA.AI · HYDERABAD"
ARIA = ("Nikhil Sukthe, Founding AI Engineer at Fika.ai, Hyderabad. "
        + " ".join(" ".join(s) for s in SENTENCES))


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def stars(n=64, seed=11):
    rng = random.Random(seed)
    out = []
    for i in range(n):
        x, y = rng.uniform(12, W - 12), rng.uniform(14, H * 0.62)
        r = rng.choice([0.6, 0.8, 1.0, 1.3, 1.6])
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" style="animation-duration:{rng.uniform(2.2, 4.4):.1f}s;'
                   f'animation-delay:{-rng.uniform(0, 4):.1f}s;opacity:{rng.uniform(0.35, 0.9):.2f}"/>')
    return "\n    ".join(out)


def sentence_markup():
    parts = []
    for i, lines in enumerate(SENTENCES, 1):
        if len(lines) == 1:
            parts.append(f'<text class="s s{i}" x="400" y="232" text-anchor="middle">{esc(lines[0])}</text>')
        else:
            parts.append(f'<text class="s s{i}" x="400" y="216" text-anchor="middle"><tspan x="400">{esc(lines[0])}</tspan>'
                         f'<tspan x="400" dy="32">{esc(lines[1])}</tspan></text>')
    return "\n    ".join(parts)


def build(sky_path, wordmark_path, at=0.0):
    sky = base64.b64encode(open(sky_path, "rb").read()).decode()
    wm = open(wordmark_path).read().strip()
    paths = "\n".join(l for l in wm.splitlines() if l.strip().startswith("<path"))
    d = lambda t: f"{t - at:.2f}s"      # delay helper; --at shifts everything earlier
    delays = "\n".join(f"    .s{i} {{ animation-delay: {d(FIRST + FRAME * (i - 1))}; }}" for i in range(1, len(SENTENCES) + 1))
    night_in = 0.8 / NIGHT_LEN * 100
    night_out = (NIGHT_LEN - 1.0) / NIGHT_LEN * 100
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(ARIA)}">
  <!-- Built by scripts/build_intro.py. Sky: scripts/build_sky.py. Wordmark: Instrument Serif (SIL Open Font License 1.1) as outlines. -->
  <defs>
    <clipPath id="frame"><rect width="{W}" height="{H}" rx="12"/></clipPath>
    <clipPath id="wm-clip">
{paths}
    </clipPath>
    <linearGradient id="sweep-grad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#ffd08c" stop-opacity="0"/><stop offset="0.5" stop-color="#ffd08c" stop-opacity="1"/><stop offset="1" stop-color="#ffd08c" stop-opacity="0"/>
    </linearGradient>
    <filter id="glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="16"/></filter>
    <filter id="shadow" x="-10%" y="-40%" width="120%" height="180%"><feDropShadow dx="0" dy="2" stdDeviation="5" flood-color="#2a1d4a" flood-opacity="0.5"/></filter>
  </defs>
  <style>
    .cap {{ font-family: ui-sans-serif, -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 12.5px; letter-spacing: 2.5px; fill: #fff; }}
    .s   {{ font-family: ui-sans-serif, -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 22px; fill: #fff; }}

    .sky   {{ transform-box: fill-box; transform-origin: center; animation: drift 60s ease-in-out infinite alternate; }}
    .name  {{ opacity: 0; transform: translateY(8px); animation: rise 1.4s ease-out {d(NAME_IN)} forwards, hide {NIGHT_LEN:.1f}s linear {d(NIGHT_AT)} forwards; }}
    .cap   {{ opacity: 0; animation: fade 0.8s ease-out {d(CAP_IN)} forwards, hidecap {NIGHT_LEN:.1f}s linear {d(NIGHT_AT)} forwards; }}
    .sweep {{ opacity: 0.9; transform: translateX(0) skewX(-18deg); animation: sweep 1.2s ease-in-out {d(SWEEP_AT)} forwards; }}
    .night {{ opacity: 0; animation: night {NIGHT_LEN:.1f}s linear {d(NIGHT_AT)} forwards; }}
    .stars circle {{ fill: #fff; animation-name: twinkle; animation-timing-function: ease-in-out; animation-iteration-count: infinite; animation-direction: alternate; }}
    .s     {{ opacity: 0; animation: say {FRAME}s ease-in-out forwards; }}
{delays}

    @keyframes drift   {{ from {{ transform: scale(1); }} to {{ transform: scale(1.06); }} }}
    @keyframes rise    {{ to {{ opacity: 1; transform: translateY(0); }} }}
    @keyframes fade    {{ to {{ opacity: 0.88; }} }}
    @keyframes sweep   {{ to {{ transform: translateX(560px) skewX(-18deg); }} }}
    @keyframes hide    {{ 0% {{ opacity: 1; }} {night_in:.2f}% {{ opacity: 0; }} {night_out:.2f}% {{ opacity: 0; }} 100% {{ opacity: 1; }} }}
    @keyframes hidecap {{ 0% {{ opacity: 0.88; }} {night_in:.2f}% {{ opacity: 0; }} {night_out:.2f}% {{ opacity: 0; }} 100% {{ opacity: 0.88; }} }}
    @keyframes night   {{ 0% {{ opacity: 0; }} {night_in:.2f}% {{ opacity: 1; }} {night_out:.2f}% {{ opacity: 1; }} 100% {{ opacity: 0; }} }}
    @keyframes twinkle {{ from {{ opacity: 0.15; }} to {{ opacity: 1; }} }}
    @keyframes say     {{ 0% {{ opacity: 0; transform: translateY(4px); }} 16% {{ opacity: 1; transform: translateY(0); }} 84% {{ opacity: 1; transform: translateY(0); }} 100% {{ opacity: 0; transform: translateY(0); }} }}

    @media (prefers-reduced-motion: reduce) {{
      .sky, .name, .cap {{ animation: none; opacity: 1; transform: none; }}
      .cap {{ opacity: 0.88; }}
      .sweep, .night, .s {{ display: none; }}
    }}
  </style>

  <g clip-path="url(#frame)">
    <image class="sky" width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice" href="data:image/jpeg;base64,{sky}"/>

    <!-- cover -->
    <g class="name" filter="url(#shadow)">
      <g transform="translate(400 {BASELINE})" fill="#fff">
{paths}
      </g>
      <g clip-path="url(#wm-clip)" transform="translate(400 {BASELINE})">
        <rect class="sweep" x="-330" y="-90" width="110" height="120" fill="url(#sweep-grad)"/>
      </g>
    </g>
    <text class="cap" x="400" y="{CAPTION_Y}" text-anchor="middle" filter="url(#shadow)">{esc(CAPTION)}</text>

    <!-- night -->
    <g class="night">
      <rect width="{W}" height="{H}" fill="#0f0a1a" opacity="0.93"/>
      <g class="stars">
    {stars()}
      </g>
    </g>
    <!-- moon: above the night so it shines on the sentences -->
    <circle cx="150" cy="82" r="66" fill="#fff" opacity="0.22" filter="url(#glow)"/>
    <circle cx="150" cy="82" r="34" fill="#f3f1ee" opacity="0.8"/>
    {sentence_markup()}
  </g>
</svg>
'''


if __name__ == "__main__":
    args = sys.argv[1:]
    at = float(args[args.index("--at") + 1]) if "--at" in args else 0.0
    files = [a for a in args if not a.startswith("--") and a != (str(at) if at else None)]
    sky_path, wordmark_path, out = files[0], files[1], files[2]
    open(out, "w").write(build(sky_path, wordmark_path, at))
    print("wrote", out, "at", at)
