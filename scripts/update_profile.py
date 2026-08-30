#!/usr/bin/env python3
"""Regenerate the profile's fetch card.

Runs daily from .github/workflows/profile.yml. Also safe to run locally:

    python3 scripts/update_profile.py

Uses only the standard library. If GITHUB_TOKEN is set it is used for
higher API rate limits; unauthenticated works fine too (~4 requests).
"""

import datetime
import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.request

USER = "Nikhils-G"
ROOT = pathlib.Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
CARD = ROOT / "assets" / "fetch-card.svg"

API = "https://api.github.com"


def api_get(path):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": USER}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(API + path, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def esc(text):
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


# ---------------------------------------------------------------- data

def collect():
    user = api_get(f"/users/{USER}")

    repos = []
    page = 1
    while True:
        batch = api_get(f"/users/{USER}/repos?per_page=100&page={page}")
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1

    stars = sum(r["stargazers_count"] for r in repos if not r["fork"])

    year = datetime.date.today().year
    commits = None
    try:
        found = api_get(
            f"/search/commits?q=author:{USER}+author-date:%3E{year}-01-01&per_page=1"
        )
        commits = found.get("total_count")
    except (urllib.error.URLError, urllib.error.HTTPError, KeyError):
        pass  # search API is best-effort; the card just omits the row

    created = datetime.datetime.strptime(
        user["created_at"], "%Y-%m-%dT%H:%M:%SZ"
    ).date()
    days = (datetime.date.today() - created).days
    uptime = f"{days // 365} yrs {(days % 365) // 30} mos"

    return {
        "repos": user["public_repos"],
        "followers": user["followers"],
        "stars": stars,
        "commits": commits,
        "year": year,
        "uptime": uptime,
    }


# ---------------------------------------------------------- fetch card

CARD_W = 820
CARD_H = 300

CARD_TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Live GitHub stats for {user}">
  <defs>
    <linearGradient id="wave-grad" gradientUnits="userSpaceOnUse" x1="46" y1="0" x2="202" y2="0">
      <stop offset="0" class="g-amber"/>
      <stop offset="1" class="g-violet"/>
    </linearGradient>
  </defs>
  <style>
    .win    {{ fill: #fbf9f4; stroke: #e2dcd0; }}
    .bar    {{ fill: #f1ecdf; }}
    .dot1   {{ fill: #b45309; }} .dot2 {{ fill: #7c3aed; }} .dot3 {{ fill: #0e7490; }}
    .fg     {{ fill: #241f2e; }}
    .amber  {{ fill: #b45309; }}
    .violet {{ fill: #7c3aed; }}
    .muted  {{ fill: #6f6880; }}
    .track  {{ fill: #e2dcd0; }}
    .g-amber  {{ stop-color: #b45309; }}
    .g-violet {{ stop-color: #7c3aed; }}
    @media (prefers-color-scheme: dark) {{
      .win    {{ fill: #0f0a1a; stroke: #2d2640; }}
      .bar    {{ fill: #171126; }}
      .dot1   {{ fill: #f0a63a; }} .dot2 {{ fill: #a78bfa; }} .dot3 {{ fill: #67e8f9; }}
      .fg     {{ fill: #ece7f4; }}
      .amber  {{ fill: #f0a63a; }}
      .violet {{ fill: #a78bfa; }}
      .muted  {{ fill: #8d86a0; }}
      .track  {{ fill: #2d2640; }}
      .g-amber  {{ stop-color: #f0a63a; }}
      .g-violet {{ stop-color: #a78bfa; }}
    }}
    text {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
      font-size: 14.5px;
    }}
    .title {{ font-size: 12.5px; }}
    .host  {{ font-size: 17px; font-weight: 700; }}
    .wave rect {{ transform-origin: center; animation: pulse 2.4s ease-in-out infinite; }}
    @keyframes pulse {{ 0%, 100% {{ transform: scaleY(1); }} 50% {{ transform: scaleY(0.45); }} }}
    @media (prefers-reduced-motion: reduce) {{ .wave rect {{ animation: none; }} }}
  </style>

  <rect class="win" x="1" y="1" width="{w2}" height="{h2}" rx="10" stroke-width="1"/>
  <path class="bar" d="M1 11 a10 10 0 0 1 10 -10 h{barw} a10 10 0 0 1 10 10 v25 h-{w2} z"/>
  <circle class="dot1" cx="24" cy="19" r="6"/>
  <circle class="dot2" cx="46" cy="19" r="6"/>
  <circle class="dot3" cx="68" cy="19" r="6"/>
  <text class="muted title" x="{mid}" y="23" text-anchor="middle">{user}@github: ~/stats</text>

  <g class="wave">
{wave}
  </g>

{rows}
</svg>
"""

WAVE_HEIGHTS = [22, 46, 74, 108, 88, 130, 64, 118, 96, 52, 78, 34]


def build_wave():
    bars = []
    cx = 46
    mid_y = 172
    for i, height in enumerate(WAVE_HEIGHTS):
        delay = (i * 0.15) % 2.4
        bars.append(
            f'    <rect fill="url(#wave-grad)" x="{cx}" y="{mid_y - height // 2}" '
            f'width="7" height="{height}" rx="3.5" '
            f'style="animation-delay: {delay:.2f}s"/>'
        )
        cx += 13
    return "\n".join(bars)


def build_rows(stats):
    x_key, x_val = 240, 372
    y = 72
    parts = [
        f'  <text class="host amber" x="{x_key}" y="{y}">{USER.lower()}@github</text>'
    ]
    y += 12
    parts.append(
        f'  <rect class="track" x="{x_key}" y="{y}" width="540" height="1.5"/>'
    )
    y += 32

    rows = [
        ("role", "Founding AI Engineer @ Fika.ai"),
        ("focus", "multimodal · multi-agent · realtime voice infra"),
        ("repos", f"{stats['repos']} public"),
        ("stars", f"{stats['stars']} earned"),
        ("followers", str(stats["followers"])),
    ]
    if stats["commits"] is not None:
        rows.append(("commits", f"{stats['commits']} in {stats['year']}"))
    rows.append(("uptime", f"{stats['uptime']} on GitHub"))

    for key, val in rows:
        parts.append(f'  <text class="violet" x="{x_key}" y="{y}">{esc(key)}</text>')
        parts.append(f'  <text class="fg" x="{x_val}" y="{y}">{esc(val)}</text>')
        y += 26

    return "\n".join(parts)


def render_card(stats):
    return CARD_TEMPLATE.format(
        w=CARD_W,
        h=CARD_H,
        w2=CARD_W - 2,
        h2=CARD_H - 2,
        barw=CARD_W - 22,
        mid=CARD_W // 2,
        user=USER.lower(),
        wave=build_wave(),
        rows=build_rows(stats),
    )


# ------------------------------------------------------------- readme

def splice(content, start, end, replacement):
    pattern = re.compile(
        re.escape(start) + r".*?" + re.escape(end), flags=re.DOTALL
    )
    if not pattern.search(content):
        sys.exit(f"README markers not found: {start}")
    return pattern.sub(start + "\n" + replacement + "\n" + end, content)


def main():
    stats = collect()

    CARD.parent.mkdir(exist_ok=True)
    CARD.write_text(render_card(stats), encoding="utf-8")

    readme = README.read_text(encoding="utf-8")
    today = datetime.date.today().isoformat()
    readme = splice(
        readme, "<!-- UPDATED:START -->", "<!-- UPDATED:END -->",
        f"Last refreshed: {today} (UTC).",
    )
    README.write_text(readme, encoding="utf-8")
    print(f"fetch card refreshed ({today})")


if __name__ == "__main__":
    main()
