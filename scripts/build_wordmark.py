#!/usr/bin/env python3
"""Turn the name into SVG path outlines so it renders identically everywhere.

    PYTHONPATH=<dir with fontTools> python3 scripts/build_wordmark.py InstrumentSerif-Regular.ttf > wordmark.txt

Prints a <g> of <path>s: one per glyph, positioned with the font's advances
and GPOS pair kerning, scaled to SIZE px, baseline at y=0, centred on x=0.
Instrument Serif is licensed under the SIL Open Font License; outlines may
be embedded freely.
"""

import sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

TEXT = "Nikhil Sukthe"
SIZE = 88  # px; cap height in Instrument Serif is 0.72 em


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
    scale = SIZE / font["head"].unitsPerEm
    cmap, glyphs, hmtx = font.getBestCmap(), font.getGlyphSet(), font["hmtx"]
    names = [cmap[ord(c)] for c in TEXT]

    positions, x = [], 0.0
    for i, name in enumerate(names):
        positions.append(x)
        x += hmtx[name][0] * scale
        if i + 1 < len(names):
            x += pair_kern(font, name, names[i + 1]) * scale
    width = x

    fmt = lambda v: ("%.1f" % v).rstrip("0").rstrip(".")
    print(f'<g id="wordmark" aria-hidden="true"><!-- {TEXT}, Instrument Serif {SIZE}px, width {width:.0f} -->')
    for name, gx in zip(names, positions):
        pen = SVGPathPen(glyphs, ntos=fmt)
        glyphs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, gx - width / 2, 0)))
        d = pen.getCommands()
        if d:
            print(f'  <path d="{d}"/>')
    print("</g>")


if __name__ == "__main__":
    main(sys.argv[1])
