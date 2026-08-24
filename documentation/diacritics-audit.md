# Diacritics audit for Google Fonts issue #10813

## Reviewer feedback translated into acceptance criteria

Google Fonts reported that the basic glyphs were improved but accented letters
still had problems with consistency, design, and position. The linked guidance
was converted into the following gates:

| Risk | Acceptance criterion | Implemented evidence |
| --- | --- | --- |
| Marks look unrelated | Related marks share weight, scale, and construction | One source contour per mark; every composite references it |
| Uneven placement | Marks use optical base anchors and a common vertical system | Base `top`/`bottom` anchors plus 220/-220 stacking anchors |
| Precomposed and decomposed text disagree | NFC and NFD must shape equivalently | 145 of 145 canonical pairs checked automatically |
| Broken combining behavior | Combining marks must be zero-width marks with attachment data | 14 of 14 are zero width, GDEF class 3, with `mark` and `mkmk` |
| Ogoneks look like detached punctuation | Ogoneks join the right-hand exit of A/E/I/U | Letter-specific bottom anchors and overlapping attachment contours |
| Cedilla and Romanian comma are confused | Cedilla attaches; comma accent stays detached | Separate U+0327 and U+0326 drawings and positions |
| Czech/Slovak carons use the wrong form or collide | Follow the encoded-language convention and preserve clearance | Centered top carons on Ď/Ť; dedicated `caroncomb.alt` beside Ľ/ď/ľ/ť; independent Ľ/ľ right-side spacing |
| Wide I accents collide with neighbors | Keep visible clearance on both sides | Î/Ï/Ī and î/ï/ī use a widened 264-unit advance and do not inherit I kerning |
| ß and ẞ diverge from the approved design | Both codepoints must use the approved ß form | U+1E9E is a source component of U+00DF with identical compiled outlines and metrics |
| Marks clip in apps | Windows metrics must contain every outline | 1000/-200 Win metrics contain the 990/-184 font bounds |

Because Teleportation One is intentionally unicase, lowercase base letters are
cap-height forms. Reusing the same accent proportions above both encoded cases
is intentional and documented; it is not an accidental failure to draw
x-height accents.

## Reproducibility

`scripts/rebuild_diacritics.py` deterministically rebuilds the 14 mark drawings,
spacing accents, all 145 canonical accented glyphs, letter-specific ogonek
attachments, Czech/Slovak caron forms, accented-I spacing, and the shared ß/ẞ
construction. A second run produced an identical source diff. Two consecutive
font builds produced byte-identical binaries.

## Validation results

- UFOlint: all 337 GLIF files pass.
- OpenType Sanitizer: pass.
- Glyphsets: GF Latin Core 100 percent.
- Custom diacritic validation: 14 combining marks, 145 NFC/NFD pairs, GDEF
  class 3, `mark`, `mkmk`, Czech/Slovak caron forms and spacing, accented-I
  spacing, and identical ß/ẞ outlines and metrics pass.
- Live FontBakery Google Fonts profile: 111 PASS, 0 FAIL, 0 ERROR, 0 FATAL,
  6 reviewed WARN.
- Built font SHA-256:
  `9a3d02b9264cfb3d988481a5ab8676204cf8bbcc3529870bc7a0fe3ab5ac53d8`.

## FontBakery warning disposition

1. **Contour count:** expected false positives from the documented unicase
   construction and display-specific glyph topology. The underlying characters
   were visually reviewed in version 1.003.
2. **Article not detected locally:** the article and licensed image are present
   and mapped by `upstream.yaml`; Google Fonts installs them in its repository.
3. **Unreachable subsetting:** the warning concerns encoded spacing and
   combining marks not currently assigned by the upstream glyphsets definitions
   to the declared `latin`/`latin-ext` subsets. The marks remain required for
   composition and should not be removed.
4. **Shape-languages auxiliary characters:** required Latin Core coverage
   passes. The warning lists optional auxiliary characters outside the declared
   coverage.
5. **Outline alignment:** one- and two-unit points are intentional overshoots or
   overlap-removal rounding in already-reviewed base glyphs.
6. **Colinear vectors:** these are deliberate clipped terminals and outline
   intersections in already-reviewed display glyphs.
7. **Vendor ID:** `RYAN` is unique to the project but is not registered with
   Microsoft. Registration is recommended, not required for Google Fonts.

## Human review

The complete local before/after page and all 323 encoded characters received
human review. The final pass included ogonek attachment, Czech and Slovak
carons and their kerning pairs, accented-I spacing, and identical ß/ẞ forms.
Ryan Oksenhorn approved the glyph set for publication on 2026-08-24.
