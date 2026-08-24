# Changelog

## 1.004 - 2026-08-24

- Rebuilt all 145 canonical accented glyphs from a shared combining-mark
  system so precomposed and decomposed text shape identically.
- Corrected optical spacing and centering across the top accents, attached
  cedillas and letter-specific ogoneks, distinguished Romanian comma accents,
  used centered top carons for uppercase Ď/Ť, and used the compact side-caron
  form for Ľ/ď/ľ/ť with independent right-side spacing.
- Added bilateral spacing for Î/Ï/Ī and î/ï/ī so their wide marks do not collide
  with neighboring glyphs.
- Made U+00DF ß and U+1E9E ẞ intentionally share the same outline and metrics.
- Added automated checks for zero-width marks, GDEF class 3, `mark`/`mkmk`
  stacking, component construction, clipping, and all NFC/NFD pairs.
- Expanded Windows metrics to the 1000/-200 line box to prevent clipping.

## 1.003 - 2026-08-17

- Replaced low-quality extended and symbol glyphs with reviewed source
  artwork, including Ø/ø, Æ/æ, Þ/þ, Ð/ð, Đ/đ, ß/ẞ, ¶, §, ¢, £, ¥, €, ©,
  and ®.
- Repaired the tilde and tilde-combining families so accented composites use
  clean, consistent outlines.
- Added a complete browser specimen for visual review of all 323 encoded
  characters.
- Completed a full visual glyph audit and rebuilt the release font from the
  corrected UFO source.

## 1.002 - 2026-08-14

- Corrected the pinned gftools release so FontBakery and the build toolchain
  resolve together in a clean environment.
- Added clean-install verification through the public GitHub Actions workflow.
- No glyph design changes from version 1.001.

## 1.001 - 2026-08-14

- Added tabular numeral alternates through the `tnum` OpenType feature.
- Added Catalan localization and mark-to-mark positioning.
- Added ligature caret positions and normalized mathematical-symbol widths.
- Added OpenType script metadata and exact Windows bounding-box metrics.
- Removed family nameID 7 metadata.
- Expanded Google Fonts article, image licensing, automated QA, and release
  documentation.

## 1.000 - 2026-08-12

- Initial public OFL release with Google Fonts Latin Core coverage.
