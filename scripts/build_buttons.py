#!/usr/bin/env python3
"""Write the five link buttons under the README text.

    python3 scripts/build_buttons.py

Slim outlined buttons, 36 px tall: hairline border, a faint surface gradient,
a violet line icon and a medium-weight label. They follow the reader's light
or dark theme. Widths are fitted to each label.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAD, ICON, GAP = 14, 16, 8

TEMPLATE = '''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="36" viewBox="0 0 {w} 36" role="img" aria-label="{label}">
  <defs>
    <linearGradient id="surf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" class="s0"/><stop offset="1" class="s1"/></linearGradient>
  </defs>
  <style>
    .s0 {{ stop-color: #ffffff; }} .s1 {{ stop-color: #f6f8fa; }}
    .edge {{ stroke: #d0d7de; }}
    .inner {{ stroke: #ffffff; }}
    .label {{ fill: #1f2328; font-family: ui-sans-serif, -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 13px; font-weight: 500; }}
    .ic {{ fill: none; stroke: #6f42c1; stroke-width: 1.5; stroke-linecap: round; stroke-linejoin: round; }}
    .gl {{ fill: #6f42c1; font-family: ui-sans-serif, -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; font-weight: 700; }}
    @media (prefers-color-scheme: dark) {{
      .s0 {{ stop-color: #1c2128; }} .s1 {{ stop-color: #161b22; }}
      .edge {{ stroke: #3d444d; }}
      .label {{ fill: #e6edf3; }}
      .ic {{ stroke: #b197fc; }} .gl {{ fill: #b197fc; }}
    }}
  </style>
  <rect x="0.5" y="0.5" width="{w1}" height="35" rx="9" fill="url(#surf)" class="edge" stroke-width="1"/>
  <rect x="1.5" y="1.5" width="{w3}" height="33" rx="8" fill="none" class="inner" stroke-opacity="0.35" stroke-width="1"/>
{icon}
  <text class="label" x="{tx}" y="22.5">{label}</text>
</svg>
'''


def linkedin(x):
    return f'  <text class="gl" x="{x + 7.5}" y="23" text-anchor="middle" font-size="12.5">in</text>'


def medium(x):
    return f'  <text class="gl" x="{x + 7.5}" y="23" text-anchor="middle" font-size="13">M</text>'


def email(x):
    return (f'  <rect class="ic" x="{x + 0.75}" y="12.75" width="14.5" height="10.5" rx="2"/>\n'
            f'  <path class="ic" d="M{x + 1.5} 14.2 L{x + 8} 19 L{x + 14.5} 14.2"/>')


def website(x):
    cx = x + 8
    return (f'  <circle class="ic" cx="{cx}" cy="18" r="7"/>\n'
            f'  <ellipse class="ic" cx="{cx}" cy="18" rx="3" ry="7"/>\n'
            f'  <path class="ic" d="M{cx - 7} 18 H{cx + 7} M{cx - 6.2} 14.6 H{cx + 6.2} M{cx - 6.2} 21.4 H{cx + 6.2}"/>')


def orcid(x):
    return (f'  <circle class="ic" cx="{x + 8}" cy="18" r="7"/>\n'
            f'  <text class="gl" x="{x + 8}" y="21" text-anchor="middle" font-size="8">iD</text>')


BUTTONS = [  # file, label, label width in px at 13px/500, icon
    ("btn-linkedin", "LinkedIn", 54, linkedin),
    ("btn-medium", "Medium", 50, medium),
    ("btn-email", "Email", 36, email),
    ("btn-website", "Website", 50, website),
    ("btn-orcid", "ORCID", 42, orcid),
]

if __name__ == "__main__":
    for name, label, label_w, icon in BUTTONS:
        w = PAD + ICON + GAP + label_w + PAD
        svg = TEMPLATE.format(w=w, w1=w - 1, w3=w - 3, label=label, icon=icon(PAD), tx=PAD + ICON + GAP)
        (ROOT / "assets" / f"{name}.svg").write_text(svg)
        print(f"{name}.svg {w}x36")
