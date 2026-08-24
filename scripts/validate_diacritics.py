#!/usr/bin/env python3
"""Validate the source and compiled diacritic system."""

from __future__ import annotations

import plistlib
import sys
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.ttLib import TTFont


TOP_MARKS = {
    0x0300,
    0x0301,
    0x0302,
    0x0303,
    0x0304,
    0x0306,
    0x0307,
    0x0308,
    0x030A,
    0x030B,
    0x030C,
}
BOTTOM_MARKS = {0x0326, 0x0327, 0x0328}
SIDE_CARONS = {
    0x010F: 0x0064,  # dcaron / d
    0x013D: 0x004C,  # Lcaron / L
    0x013E: 0x006C,  # lcaron / l
    0x0165: 0x0074,  # tcaron / t
}
SIDE_CARON_MIN_EXTENSION = {0x013D: 4, 0x013E: 4}
TOP_CARONS = {
    0x010E: 0x0044,  # Dcaron / D
    0x0164: 0x0054,  # Tcaron / T
}


def shape(font_data: bytes, text: str):
    face = hb.Face(font_data)
    font = hb.Font(face)
    buffer = hb.Buffer()
    buffer.add_str(text)
    buffer.guess_segment_properties()
    hb.shape(font, buffer)
    return [
        (info.codepoint, position.x_advance, position.x_offset, position.y_offset)
        for info, position in zip(buffer.glyph_infos, buffer.glyph_positions)
    ]


def source_composites(project: Path, cmap):
    glyph_dir = project / "sources/TeleportationOne-Regular.ufo/glyphs"
    with (glyph_dir / "contents.plist").open("rb") as handle:
        contents = plistlib.load(handle)
    source_cmap = {}
    for name, filename in contents.items():
        root = ET.parse(glyph_dir / filename).getroot()
        unicode_node = root.find("unicode")
        if unicode_node is not None:
            source_cmap[int(unicode_node.get("hex"), 16)] = name

    checked = 0
    for codepoint in cmap:
        decomposition = unicodedata.decomposition(chr(codepoint))
        if not decomposition or decomposition.startswith("<"):
            continue
        sequence = [int(value, 16) for value in decomposition.split()]
        if len(sequence) != 2 or sequence[1] not in TOP_MARKS | BOTTOM_MARKS:
            continue
        root = ET.parse(glyph_dir / contents[source_cmap[codepoint]]).getroot()
        components = root.findall("./outline/component")
        assert len(components) == 2, f"U+{codepoint:04X} is not a two-component source glyph"
        assert components[0].get("base") == source_cmap[sequence[0]]
        checked += 1
    return checked


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: validate_diacritics.py FONT.ttf")

    font_path = Path(sys.argv[1])
    font_data = font_path.read_bytes()
    font = TTFont(font_path)
    cmap = font.getBestCmap()
    mark_codepoints = TOP_MARKS | BOTTOM_MARKS

    gdef_classes = font["GDEF"].table.GlyphClassDef.classDefs
    for codepoint in mark_codepoints:
        glyph_name = cmap[codepoint]
        assert font["hmtx"].metrics[glyph_name][0] == 0, f"{glyph_name} must have zero advance"
        assert gdef_classes[glyph_name] == 3, f"{glyph_name} must be GDEF class 3"

    canonical_pairs = 0
    for codepoint in sorted(cmap):
        decomposition = unicodedata.decomposition(chr(codepoint))
        if not decomposition or decomposition.startswith("<"):
            continue
        sequence = [int(value, 16) for value in decomposition.split()]
        if len(sequence) != 2 or not all(value in cmap for value in sequence):
            continue
        if sequence[1] not in mark_codepoints:
            continue
        composed = shape(font_data, chr(codepoint))
        decomposed = shape(font_data, "".join(chr(value) for value in sequence))
        assert composed == decomposed, f"NFC/NFD shaping differs for U+{codepoint:04X}"
        canonical_pairs += 1

    top_stack = shape(font_data, "A\u0301\u0308")
    bottom_stack = shape(font_data, "A\u0328\u0326")
    assert len(top_stack) >= 2 and top_stack[-1][3] >= 1000, "top mkmk stacking failed"
    assert len(bottom_stack) >= 2 and bottom_stack[-1][3] <= -200, "bottom mkmk stacking failed"

    glyf = font["glyf"]
    for codepoint, base_codepoint in SIDE_CARONS.items():
        glyph_name = cmap[codepoint]
        base_name = cmap[base_codepoint]
        glyph = glyf[glyph_name]
        base = glyf[base_name]
        glyph.recalcBounds(glyf)
        base.recalcBounds(glyf)
        width = font["hmtx"].metrics[glyph_name][0]
        min_extension = SIDE_CARON_MIN_EXTENSION.get(codepoint, 60)
        assert glyph.xMax >= base.xMax + min_extension, f"{glyph_name} side caron is too close to the base"
        assert width >= glyph.xMax + 20, f"{glyph_name} side caron has insufficient right sidebearing"

    for codepoint, base_codepoint in TOP_CARONS.items():
        glyph_name = cmap[codepoint]
        base_name = cmap[base_codepoint]
        glyph = glyf[glyph_name]
        base = glyf[base_name]
        glyph.recalcBounds(glyf)
        base.recalcBounds(glyf)
        assert glyph.yMax >= base.yMax + 150, f"{glyph_name} caron is not above the capital"
        assert font["hmtx"].metrics[glyph_name][0] == font["hmtx"].metrics[base_name][0], (
            f"{glyph_name} must retain the base capital's advance"
        )

    lower_eszett = cmap[0x00DF]
    upper_eszett = cmap[0x1E9E]
    assert font["hmtx"].metrics[lower_eszett] == font["hmtx"].metrics[upper_eszett], (
        "ß and ẞ must have identical horizontal metrics"
    )
    glyph_set = font.getGlyphSet()
    eszett_drawings = []
    for glyph_name in (lower_eszett, upper_eszett):
        pen = DecomposingRecordingPen(glyph_set)
        glyph_set[glyph_name].draw(pen)
        eszett_drawings.append(pen.value)
    assert eszett_drawings[0] == eszett_drawings[1], "ß and ẞ must have identical outlines"

    for side_caron in "Ľľ":
        glyph_name = cmap[ord(side_caron)]
        unkerned_advance = font["hmtx"].metrics[glyph_name][0]
        for following in "TŤVWY\"'":
            first_advance = shape(font_data, side_caron + following)[0][1]
            assert first_advance == unkerned_advance, (
                f"{glyph_name} must not inherit L's right-side kerning before {following}"
            )

    for wide_i in "ÎÏĪîïī":
        glyph_name = cmap[ord(wide_i)]
        glyph = glyf[glyph_name]
        glyph.recalcBounds(glyf)
        width = font["hmtx"].metrics[glyph_name][0]
        assert width == 264, f"{glyph_name} must use the widened accented-I advance"
        assert glyph.xMin >= 10 and width - glyph.xMax >= 10, (
            f"{glyph_name} must retain spacing on both sides of its accent"
        )
        assert shape(font_data, wide_i + "Y")[0][1] == width, (
            f"{glyph_name} must not inherit I's right-side kerning"
        )

    source_count = source_composites(font_path.resolve().parents[2], cmap)
    assert source_count == canonical_pairs
    print(
        f"Diacritic validation passed: {len(mark_codepoints)} combining marks, "
        f"{canonical_pairs} NFC/NFD pairs, GDEF class 3, mark and mkmk stacking, "
        f"{len(TOP_CARONS)} uppercase top carons, {len(SIDE_CARONS)} detached side carons, "
        "matching ß/ẞ, independent Ľ/ľ right-side spacing, and widened ÎÏĪ/îïī."
    )


if __name__ == "__main__":
    main()
