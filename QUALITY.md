# Quality review notes

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
