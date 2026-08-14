#!/usr/bin/env python3
"""Add deterministic OpenType metadata not represented by the UFO source."""

import sys

from fontTools.ttLib import TTFont, newTable


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: postprocess_font.py FONT.ttf")

    path = sys.argv[1]
    font = TTFont(path, recalcTimestamp=False)
    meta = newTable("meta")
    meta.data = {"dlng": "Latn", "slng": "Latn"}
    font["meta"] = meta
    font.save(path, reorderTables=False)


if __name__ == "__main__":
    main()
