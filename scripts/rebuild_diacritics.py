#!/usr/bin/env python3
"""Rebuild Teleportation One's Latin diacritics as a coherent component system.

The script intentionally uses only the Python standard library. It keeps the
original base-letter drawings, replaces the combining/spacing marks, and then
recomposes every canonically decomposable encoded glyph in the UFO. Running it
again is idempotent.
"""

from __future__ import annotations

import plistlib
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional


PROJECT = Path(__file__).resolve().parent.parent
GLYPHS = PROJECT / "sources/TeleportationOne-Regular.ufo/glyphs"


def number(value: float) -> str:
    return str(int(value)) if float(value).is_integer() else str(value)


def point(x: float, y: float, kind: Optional[str] = "line", smooth: bool = False):
    data = {"x": number(x), "y": number(y)}
    if kind:
        data["type"] = kind
    if smooth:
        data["smooth"] = "yes"
    return data


def polygon(*coordinates: tuple[float, float]):
    return [point(x, y) for x, y in coordinates]


def read_contents():
    with (GLYPHS / "contents.plist").open("rb") as handle:
        return plistlib.load(handle)


CONTENTS = read_contents()


def tree_for(name: str):
    path = GLYPHS / CONTENTS[name]
    return path, ET.parse(path)


def add_anchor(root, name: str, x: float, y: float):
    ET.SubElement(root, "anchor", {"x": number(x), "y": number(y), "name": name})


def add_contour(outline, points):
    contour = ET.SubElement(outline, "contour")
    for attrs in points:
        ET.SubElement(contour, "point", attrs)


def replace_drawing(name: str, contours, anchors=(), components=()):
    path, tree = tree_for(name)
    root = tree.getroot()
    for child in list(root):
        if child.tag in {"anchor", "outline"}:
            root.remove(child)
    for anchor_name, x, y in anchors:
        add_anchor(root, anchor_name, x, y)
    outline = ET.SubElement(root, "outline")
    for contour in contours:
        add_contour(outline, contour)
    for base, x, y in components:
        attrs = {"base": base}
        if x:
            attrs["xOffset"] = number(x)
        if y:
            attrs["yOffset"] = number(y)
        ET.SubElement(outline, "component", attrs)
    ET.indent(tree, space="  ")
    tree.write(path, encoding="UTF-8", xml_declaration=True)


TOP_ANCHORS = (("_top", 0, 0), ("top", 0, 220))
BOTTOM_ANCHORS = (("_bottom", 0, 0), ("bottom", 0, -220))


MARKS = {
    "acutecomb": [polygon((-58, 44), (6, 44), (92, 184), (12, 184))],
    "gravecomb": [polygon((-92, 184), (-12, 184), (58, 44), (-6, 44))],
    "circumflexcomb": [
        polygon((-122, 76), (-76, 44), (0, 124), (76, 44), (122, 76), (0, 184))
    ],
    "caroncomb": [
        polygon((-122, 152), (-76, 184), (0, 104), (76, 184), (122, 152), (0, 44))
    ],
    "brevecomb": [[
        point(-118, 184), point(-105, 88, None), point(-55, 44, None),
        point(0, 44, "curve", True), point(55, 44, None), point(105, 88, None),
        point(118, 184, "curve"), point(56, 184), point(48, 132, None),
        point(27, 106, None), point(0, 106, "curve", True), point(-27, 106, None),
        point(-48, 132, None), point(-56, 184, "curve"),
    ]],
    "dieresiscomb": [
        polygon((-106, 72), (-36, 72), (-36, 156), (-106, 156)),
        polygon((36, 72), (106, 72), (106, 156), (36, 156)),
    ],
    "dotaccentcomb": [polygon((-43, 72), (43, 72), (43, 158), (-43, 158))],
    "hungarumlautcomb": [
        polygon((-126, 44), (-70, 44), (0, 184), (-72, 184)),
        polygon((2, 44), (58, 44), (128, 184), (56, 184)),
    ],
    "macroncomb": [polygon((-116, 92), (116, 92), (116, 150), (-116, 150))],
    "ringcomb": [[
        point(74, 116, "curve", True), point(74, 156, None), point(40, 190, None),
        point(0, 190, "curve", True), point(-40, 190, None), point(-74, 156, None),
        point(-74, 116, "curve", True), point(-74, 76, None), point(-40, 42, None),
        point(0, 42, "curve", True), point(40, 42, None), point(74, 76, None),
    ], [
        point(30, 116, "curve", True), point(30, 99, None), point(17, 86, None),
        point(0, 86, "curve", True), point(-17, 86, None), point(-30, 99, None),
        point(-30, 116, "curve", True), point(-30, 133, None), point(-17, 146, None),
        point(0, 146, "curve", True), point(17, 146, None), point(30, 133, None),
    ]],
    "tildecomb": [[
        point(-38, 162, "qcurve", True), point(-17, 162, None), point(11, 136, None),
        point(20, 127, "qcurve"), point(31, 115, None), point(40, 107, None),
        point(43, 107, "qcurve", True), point(56, 107, None), point(73, 126, None),
        point(92, 152, "qcurve"), point(128, 105), point(118, 92, None),
        point(95, 62, None), point(65, 40, None), point(43, 40, "qcurve", True),
        point(23, 40, None), point(-5, 67, None), point(-13, 76, "qcurve", True),
        point(-23, 87, None), point(-33, 96, None), point(-38, 96, "qcurve", True),
        point(-55, 96, None), point(-74, 74, None), point(-92, 50, "qcurve"),
        point(-128, 98), point(-118, 110, None), point(-95, 141, None),
        point(-62, 162, None),
    ]],
    # Slovak/Czech side caron used by L/d/l/t. Keep the whole mark to the right
    # of the base rather than letting its lower edge disappear into the stem.
    "caroncomb.alt": [polygon((-24, 178), (44, 178), (10, 44), (-20, 44))],
    "cedillacomb": [[
        point(-31, 8), point(39, 8), point(16, -48), point(69, -55, None),
        point(92, -76, None), point(92, -112, "qcurve", True),
        point(92, -151, None), point(55, -176, None), point(11, -176, "qcurve", True),
        point(-20, -176, None), point(-44, -161, None), point(-56, -149, "qcurve"),
        point(-25, -113), point(-12, -124, None), point(4, -130, None),
        point(22, -130, "qcurve", True), point(38, -130, None), point(49, -122, None),
        point(49, -110, "qcurve", True), point(49, -100, None), point(39, -92, None),
        point(22, -92, "qcurve"), point(-27, -92),
    ]],
    "ogonekcomb": [[
        point(-34, 10, "qcurve"), point(18, 10), point(18, -52, "line", True),
        point(18, -91, None), point(29, -119, None), point(50, -126, "qcurve", True),
        point(66, -131, None), point(82, -121, None), point(94, -111, "qcurve"),
        point(102, -157), point(84, -174, None), point(56, -184, None),
        point(24, -184, "qcurve", True), point(-24, -184, None), point(-48, -147, None),
        point(-48, -99, "qcurve", True), point(-48, -52, None), point(-39, -10, None),
    ]],
    "commaaccentcomb": [polygon((-24, -38), (48, -38), (7, -174), (-61, -174))],
}


def rewrite_marks():
    for name, contours in MARKS.items():
        anchors = BOTTOM_ANCHORS if name in {"cedillacomb", "ogonekcomb", "commaaccentcomb"} else TOP_ANCHORS
        replace_drawing(name, contours, anchors)


SPACING_TO_COMBINING = {
    "acute": "acutecomb",
    "grave": "gravecomb",
    "circumflex": "circumflexcomb",
    "caron": "caroncomb",
    "breve": "brevecomb",
    "dieresis": "dieresiscomb",
    "dotaccent": "dotaccentcomb",
    "hungarumlaut": "hungarumlautcomb",
    "macron": "macroncomb",
    "ring": "ringcomb",
    "tilde": "tildecomb",
    "cedilla": "cedillacomb",
    "ogonek": "ogonekcomb",
}


def rewrite_spacing_marks():
    for spacing, combining in SPACING_TO_COMBINING.items():
        _, tree = tree_for(spacing)
        root = tree.getroot()
        advance = root.find("advance")
        width = float(advance.get("width")) if advance is not None else 300
        y = 620 if combining not in {"cedillacomb", "ogonekcomb"} else 720
        replace_drawing(spacing, [], components=[(combining, width / 2, y)])


def unicode_map():
    result = {}
    for name, filename in CONTENTS.items():
        root = ET.parse(GLYPHS / filename).getroot()
        node = root.find("unicode")
        if node is not None:
            result[int(node.get("hex"), 16)] = name
    return result


def anchors_for(name: str):
    _, tree = tree_for(name)
    return {
        node.get("name"): (float(node.get("x")), float(node.get("y")))
        for node in tree.getroot().findall("anchor")
    }


OGONEK_X = {"A": 326, "E": 218, "I": 84, "U": 294, "a": 326, "e": 218, "i": 84, "u": 294}
VERTICAL_CARON_X = {"L": 275, "d": 444, "l": 275, "t": 420}
VERTICAL_CARON_ADVANCE = {"L": 368, "d": 512, "l": 368, "t": 488}
TOP_CARON_BASES = {"D", "T"}
WIDE_I_MARKS = {"circumflexcomb", "dieresiscomb", "macroncomb"}
WIDE_I_SHIFT = 24
WIDE_I_ADVANCE = 264


def set_anchor(name: str, anchor_name: str, x: float, y: float):
    path, tree = tree_for(name)
    root = tree.getroot()
    node = next((a for a in root.findall("anchor") if a.get("name") == anchor_name), None)
    if node is None:
        outline = root.find("outline")
        node = ET.Element("anchor")
        root.insert(list(root).index(outline), node)
    node.attrib = {"x": number(x), "y": number(y), "name": anchor_name}
    ET.indent(tree, space="  ")
    tree.write(path, encoding="UTF-8", xml_declaration=True)


def set_advance(name: str, width: float):
    path, tree = tree_for(name)
    root = tree.getroot()
    advance = root.find("advance")
    if advance is None:
        advance = ET.Element("advance")
        root.insert(0, advance)
    advance.set("width", number(width))
    ET.indent(tree, space="  ")
    tree.write(path, encoding="UTF-8", xml_declaration=True)


def get_advance(name: str) -> float:
    _, tree = tree_for(name)
    advance = tree.getroot().find("advance")
    return float(advance.get("width"))


def rebuild_precomposed():
    cmap = unicode_map()
    mark_map = {codepoint: name for codepoint, name in cmap.items() if unicodedata.category(chr(codepoint)).startswith("M")}

    for base_name, x in OGONEK_X.items():
        set_anchor(base_name, "bottom", x, 0)

    rebuilt = 0
    for codepoint, glyph_name in sorted(cmap.items()):
        decomposition = unicodedata.decomposition(chr(codepoint))
        if not decomposition or decomposition.startswith("<"):
            continue
        sequence = [int(value, 16) for value in decomposition.split()]
        if len(sequence) != 2 or sequence[0] not in cmap or sequence[1] not in mark_map:
            continue
        base_name = cmap[sequence[0]]
        mark_name = mark_map[sequence[1]]
        base_anchors = anchors_for(base_name)
        if mark_name == "caroncomb" and base_name in VERTICAL_CARON_X:
            x, y = VERTICAL_CARON_X[base_name], 610
            mark_name = "caroncomb.alt"
            result_anchors = tuple((key, *value) for key, value in base_anchors.items())
        elif mark_name in {"cedillacomb", "ogonekcomb", "commaaccentcomb"}:
            x, y = base_anchors["bottom"]
            result_anchors = (
                ("top", *base_anchors["top"]),
                ("bottom", x, y - 220),
            )
        else:
            x, y = base_anchors["top"]
            result_anchors = (
                ("top", x, y + 220),
                ("bottom", *base_anchors["bottom"]),
            )
        horizontal_shift = WIDE_I_SHIFT if base_name in {"I", "i"} and mark_name in WIDE_I_MARKS else 0
        if horizontal_shift:
            result_anchors = tuple(
                (anchor_name, anchor_x + horizontal_shift, anchor_y)
                for anchor_name, anchor_x, anchor_y in result_anchors
            )
        replace_drawing(
            glyph_name,
            [],
            anchors=result_anchors,
            components=[
                (base_name, horizontal_shift, 0),
                (mark_name, x + horizontal_shift, y),
            ],
        )
        if base_name in VERTICAL_CARON_ADVANCE and mark_name == "caroncomb.alt":
            set_advance(glyph_name, VERTICAL_CARON_ADVANCE[base_name])
        elif base_name in TOP_CARON_BASES and mark_name == "caroncomb":
            set_advance(glyph_name, get_advance(base_name))
        elif horizontal_shift:
            set_advance(glyph_name, WIDE_I_ADVANCE)
        rebuilt += 1
    return rebuilt


def rebuild_capital_eszett():
    # This family intentionally uses the lowercase eszett design for both
    # encoded forms. Keep the capital as a component so the two cannot drift.
    replace_drawing(
        "Germandbls",
        [],
        anchors=tuple((name, *position) for name, position in anchors_for("germandbls").items()),
        components=[("germandbls", 0, 0)],
    )
    set_advance("Germandbls", get_advance("germandbls"))


def main():
    rewrite_marks()
    rewrite_spacing_marks()
    rebuilt = rebuild_precomposed()
    rebuild_capital_eszett()
    print(f"Rebuilt marks, spacing accents, {rebuilt} precomposed glyphs, and matching ß/ẞ")


if __name__ == "__main__":
    main()
