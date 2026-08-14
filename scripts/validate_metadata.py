#!/usr/bin/env python3
"""Validate release metadata and OpenType features required by this project."""

import sys

from fontTools.ttLib import TTFont


def name_values(font: TTFont, name_id: int) -> list[str]:
    values = []
    for record in font["name"].names:
        if record.nameID == name_id:
            values.append(record.toUnicode())
    return values


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: validate_metadata.py FONT.ttf")

    font = TTFont(sys.argv[1])
    assert "Teleportation One" in name_values(font, 1)
    expected_version = f"Version {font['head'].fontRevision:.3f}"
    assert set(name_values(font, 5)) == {expected_version}
    assert not name_values(font, 7), "trademark metadata must not be present"
    assert any("SIL Open Font License" in value for value in name_values(font, 13))
    assert font["OS/2"].fsType == 0
    assert font["OS/2"].usWinAscent == font["head"].yMax
    assert font["OS/2"].usWinDescent == abs(font["head"].yMin)
    assert font["meta"].data == {"dlng": "Latn", "slng": "Latn"}

    gsub_features = {
        record.FeatureTag for record in font["GSUB"].table.FeatureList.FeatureRecord
    }
    gpos_features = {
        record.FeatureTag for record in font["GPOS"].table.FeatureList.FeatureRecord
    }
    assert {"liga", "locl", "tnum"} <= gsub_features
    assert {"kern", "mark", "mkmk"} <= gpos_features

    cmap = font.getBestCmap()
    math_widths = {
        font["hmtx"].metrics[cmap[codepoint]][0]
        for codepoint in (0x002B, 0x003C, 0x003D, 0x003E, 0x00D7, 0x00F7, 0x2212)
    }
    assert math_widths == {432}
    print("Release metadata and OpenType feature validation passed.")


if __name__ == "__main__":
    main()
