# Quality review notes

## Diacritic review after Google Fonts issue #10813

The post-1.003 source rebuilds all 145 canonically decomposable accented
glyphs from the same 14 combining marks used by decomposed text. The review
covered accent shape, optical centering, clearance, cedilla and ogonek
attachment, Romanian comma accents, Czech and Slovak caron conventions,
accented-I spacing, and identical ß/ẞ forms. Teleportation One is intentionally
unicase, so uppercase and lowercase accented letters use the same cap-height
base and mark proportions except where encoded language conventions differ.

Automated checks enforce that:

- every combining mark has zero advance width and GDEF class 3;
- all 145 supported NFC/NFD pairs produce identical shaping;
- above- and below-base marks position through `mark` and stack through
  `mkmk`;
- each canonical precomposed glyph remains a two-component UFO source glyph;
- Ď/Ť retain top carons while Ľ/ď/ľ/ť use the special side-caron component;
- Ľ/ľ and Î/Ï/Ī/î/ï/ī retain independent collision-safe spacing;
- ß and ẞ retain identical outlines and metrics;
- Windows clipping metrics contain the complete outline bounds.

Run `python scripts/rebuild_diacritics.py` to reproduce the source composition
and `python scripts/validate_diacritics.py fonts/ttf/TeleportationOne-Regular.ttf`
to audit the compiled result. A before/after browser package can be generated
with `scripts/render_diacritics_review.py`.

## Whole-font review

Version 1.003 received a card-by-card visual review of all 323 encoded
characters. The symbols and extended Latin forms flagged during that review
were redrawn from approved source artwork and checked again in the rebuilt
font. The complete local review specimen can be regenerated with
`python scripts/render_glyph_specimen.py`.

FontBakery's contour-count check compares glyph construction with conventional
mixed-case text families. Teleportation One is intentionally unicase, and its
lowercase forms reuse the display construction of the uppercase alphabet. The
reported contour-count differences were visually reviewed and match their
assigned Unicode characters.

The remaining colinear-vector and jagged-segment notices occur at deliberate
clipped terminals and outline intersections in the A/AE, W, Z, and slashed-O
designs. They were reviewed at source size and in rendered specimens; changing
them mechanically would alter the intended display shapes.

Alignment notices at one or two units from the baseline or cap height are
either optical overshoots on rounded forms or fractional points introduced by
overlap removal. The single unintended near-horizontal segment in seven was
aligned to the baseline for version 1.001.

The remaining Google Fonts profile warnings are reviewed and non-blocking:
the contour-count warning is caused by the documented unicase construction;
alignment and colinear-vector warnings are the reviewed display outlines noted
above; the vendor ID is a unique but unregistered ID; article and subset
warnings are evaluated in the Google Fonts repository after `upstream.yaml`
installs the included article and its `latin`/`latin-ext` metadata. The live
shape-languages warning lists optional auxiliary characters outside Latin Core;
required orthographies in the declared coverage continue to shape correctly.
