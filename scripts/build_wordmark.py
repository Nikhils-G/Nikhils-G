#!/usr/bin/env python3
"""Turn the name into arched SVG outlines so it renders identically everywhere.

    PYTHONPATH=<dir with fontTools> python3 scripts/build_wordmark.py Anton-Regular.ttf > wordmark.txt

Prints two groups, <g id="w1"> for NIKHIL and <g id="w2"> for SUKTHE, each a
set of <path>s, one per glyph, carrying its own transform that places it on an
upward arc (centre letters higher, ends lower). Each line is centred on x=0
with its baseline at y=0, so the assembler can stack and extrude them with
<use> copies. Positions use the font's advances, GPOS pair kerning and a
slightly tight tracking. Anton is licensed under the SIL Open Font License;
outlines may be embedded.
"""

import math
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

LINES = (("w1", "NIKHIL"), ("w2", "SUKTHE"))
SIZE = 140          # px font size
TRACKING = -0.02    # em, letters sit a little tighter than the font's default
ARC_R = 1200        # px, radius of the baseline arc


def pair_kern(font, left, right):
    """XAdvance adjustment for (left, right) from GPOS PairPos, or 0."""
    if "GPOS" not in font:
        return 0
    for lookup in font["GPOS"].table.LookupList.Lookup:
        for sub in lookup.SubTable:
            if lookup.LookupType == 9:
                sub = sub.ExtSubTable
            if getattr(sub, "LookupType", 2) != 2 or left not in sub.Coverage.glyphs:
                continue
            if sub.Format == 1:
                pair_set = sub.PairSet[sub.Coverage.glyphs.index(left)]
                for rec in pair_set.PairValueRecord:
                    if rec.SecondGlyph == right and rec.Value1 is not None:
                        return getattr(rec.Value1, "XAdvance", 0) or 0
            elif sub.Format == 2:
                c1 = sub.ClassDef1.classDefs.get(left, 0)
                c2 = sub.ClassDef2.classDefs.get(right, 0)
                value = sub.Class1Record[c1].Class2Record[c2].Value1
                if value is not None and getattr(value, "XAdvance", 0):
                    return value.XAdvance
    return 0


def main(path):
    font = TTFont(path)
    cmap, glyphs, hmtx = font.getBestCmap(), font.getGlyphSet(), font["hmtx"]
    scale = SIZE / font["head"].unitsPerEm
    fmt = lambda v: ("%.1f" % v).rstrip("0").rstrip(".")

    for gid, text in LINES:
        names = [cmap[ord(c)] for c in text]
        own = [hmtx[n][0] * scale for n in names]                       # each glyph's own advance
        step = [w + (pair_kern(font, n, names[i + 1]) * scale if i + 1 < len(names) else 0) + TRACKING * SIZE
                for i, (n, w) in enumerate(zip(names, own))]           # distance to the next glyph
        total = sum(step) - TRACKING * SIZE
        print(f'<g id="{gid}"><!-- {text}, Anton {SIZE}px, {total:.0f}px wide on a {ARC_R}px arc -->')
        x = -total / 2
        for name, w, adv in zip(names, own, step):
            angle = (x + w / 2) / ARC_R
            pen = SVGPathPen(glyphs, ntos=fmt)
            glyphs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, -w / 2, 0)))
            d = pen.getCommands()
            if d:
                print(f'  <path transform="translate({ARC_R * math.sin(angle):.1f} {ARC_R * (1 - math.cos(angle)):.1f}) '
                      f'rotate({math.degrees(angle):.2f})" d="{d}"/>')
            x += adv
        print("</g>")


if __name__ == "__main__":
    main(sys.argv[1])
