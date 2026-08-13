#!/usr/bin/env python3
"""Render the project specimen through the same OpenType shaping used by apps."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, features


ROOT = Path(__file__).resolve().parents[1]
FONT_PATH = ROOT / "fonts" / "ttf" / "TeleportationOne-Regular.ttf"
DEFAULT_OUTPUT = ROOT / "documentation" / "teleportation-one-specimen.png"

BACKGROUND = "#f4eee4"
FOREGROUND = "#17130f"
ACCENT = "#ff513b"


def shaped_font(size: int) -> ImageFont.FreeTypeFont:
    if not features.check_feature("raqm"):
        raise RuntimeError("Pillow must be built with RAQM/HarfBuzz support")
    return ImageFont.truetype(
        FONT_PATH,
        size,
        layout_engine=ImageFont.Layout.RAQM,
    )


def draw_shaped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    *,
    fill: str = FOREGROUND,
) -> None:
    draw.text(
        xy,
        text,
        font=font,
        fill=fill,
        direction="ltr",
        language="en",
        features=["kern", "liga"],
        anchor="la",
    )


def render(output: Path) -> None:
    image = Image.new("RGB", (1400, 760), BACKGROUND)
    draw = ImageDraw.Draw(image)

    draw_shaped(draw, (64, 48), "TELEPORTATION ONE", shaped_font(30), fill=ACCENT)
    draw_shaped(draw, (64, 142), "MOVE", shaped_font(190))
    draw_shaped(draw, (64, 295), "INSTANTLY", shaped_font(190))

    draw.rounded_rectangle((64, 490, 1336, 495), radius=2, fill=ACCENT)

    draw_shaped(draw, (64, 540), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", shaped_font(46))
    draw_shaped(
        draw,
        (64, 615),
        "À Á Â Ã Ä Å  Æ  Ç  Ď  Ñ  Ö  Œ  Š  Þ  Ž    0123456789    ← → ↔",
        shaped_font(42),
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    render(args.output)


if __name__ == "__main__":
    main()
