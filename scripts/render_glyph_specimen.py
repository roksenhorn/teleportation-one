#!/usr/bin/env python3
"""Generate a self-contained browser specimen for every encoded character."""

from __future__ import annotations

import json
import hashlib
import sys
import unicodedata
from pathlib import Path

from fontTools.ttLib import TTFont


BLOCKS = (
    (0x0000, 0x007F, "Basic Latin"),
    (0x0080, 0x00FF, "Latin-1 Supplement"),
    (0x0100, 0x017F, "Latin Extended-A"),
    (0x0180, 0x024F, "Latin Extended-B"),
    (0x02B0, 0x02FF, "Spacing Modifier Letters"),
    (0x0300, 0x036F, "Combining Diacritical Marks"),
    (0x1E00, 0x1EFF, "Latin Extended Additional"),
    (0x2000, 0x206F, "General Punctuation"),
    (0x20A0, 0x20CF, "Currency Symbols"),
    (0x2100, 0x214F, "Letterlike Symbols"),
    (0x2190, 0x21FF, "Arrows"),
    (0x2200, 0x22FF, "Mathematical Operators"),
    (0x25A0, 0x25FF, "Geometric Shapes"),
)


def block_name(codepoint: int) -> str:
    for start, end, name in BLOCKS:
        if start <= codepoint <= end:
            return name
    return "Other Characters"


def font_version(font: TTFont) -> str:
    for record in font["name"].names:
        if record.nameID == 5:
            return record.toUnicode().removeprefix("Version ")
    return "unknown"


def main() -> None:
    project_dir = Path(__file__).resolve().parent.parent
    font_path = project_dir / "fonts/ttf/TeleportationOne-Regular.ttf"
    output_path = project_dir / "documentation/glyph-specimen.html"
    if len(sys.argv) > 1:
        output_path = Path(sys.argv[1]).resolve()

    font = TTFont(font_path)
    cmap = font.getBestCmap()
    rows = []
    for codepoint, glyph_name in sorted(cmap.items()):
        character = chr(codepoint)
        category = unicodedata.category(character)
        rows.append(
            {
                "codepoint": codepoint,
                "hex": f"U+{codepoint:04X}",
                "char": character,
                "display": f"◌{character}" if category.startswith("M") else character,
                "glyph": glyph_name,
                "name": unicodedata.name(character, "UNNAMED CHARACTER"),
                "category": category,
                "block": block_name(codepoint),
            }
        )

    payload = json.dumps(rows, ensure_ascii=False).replace("</", "<\\/")
    html = TEMPLATE.replace("__GLYPH_DATA__", payload)
    html = html.replace("__GLYPH_COUNT__", str(len(rows)))
    html = html.replace("__FONT_VERSION__", font_version(font))
    html = html.replace("__FONT_CACHE_KEY__", hashlib.sha256(font_path.read_bytes()).hexdigest()[:12])
    output_path.write_text(html, encoding="utf-8")
    print(f"Wrote {output_path} with {len(rows)} encoded characters")


TEMPLATE = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Teleportation One — Complete Character Specimen</title>
  <style>
    @font-face {
      font-family: "Teleportation One Review";
      src: url("../fonts/ttf/TeleportationOne-Regular.ttf?v=__FONT_CACHE_KEY__") format("truetype");
      font-weight: 400;
      font-style: normal;
      font-display: block;
    }
    :root {
      --ink: #141414;
      --paper: #f2f0e9;
      --panel: #fbfaf6;
      --line: #d8d4ca;
      --accent: #e64b2f;
      --accent-soft: #ffd9cf;
      --muted: #706d66;
      --glyph-size: 72px;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      color: var(--ink);
      background: var(--paper);
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    }
    header {
      padding: clamp(28px, 5vw, 76px);
      color: #fff;
      background: var(--ink);
      border-bottom: 8px solid var(--accent);
    }
    .eyebrow {
      margin: 0 0 18px;
      color: #ff9d87;
      font-size: 12px;
      font-weight: 800;
      letter-spacing: .16em;
      text-transform: uppercase;
    }
    h1 {
      max-width: 1050px;
      margin: 0;
      font-family: "Teleportation One Review", sans-serif;
      font-size: clamp(52px, 9vw, 132px);
      font-weight: 400;
      letter-spacing: -.035em;
      line-height: .92;
    }
    .deck {
      max-width: 760px;
      margin: 28px 0 0;
      color: #cbc7be;
      font-size: 14px;
      line-height: 1.65;
    }
    .stats {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 24px;
    }
    .stat {
      padding: 9px 12px;
      color: #fff;
      background: #292929;
      border: 1px solid #484848;
      border-radius: 999px;
      font-size: 12px;
    }
    main { padding: clamp(20px, 4vw, 56px); }
    .focus-panel {
      margin-bottom: 34px;
      padding: clamp(20px, 3vw, 34px);
      background: var(--accent-soft);
      border: 2px solid var(--accent);
      border-radius: 18px;
    }
    .focus-panel h2, .block h2 { margin: 0; }
    .focus-panel p {
      max-width: 760px;
      margin: 10px 0 22px;
      color: #6c271b;
      font-size: 13px;
      line-height: 1.55;
    }
    .focus-row {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
      gap: 12px;
    }
    .focus-glyph {
      min-height: 200px;
      padding: 12px;
      background: var(--panel);
      border: 1px solid #ef9b87;
      border-radius: 12px;
      text-align: center;
    }
    .focus-glyph .shape {
      display: grid;
      min-height: 118px;
      place-items: center;
      font-family: "Teleportation One Review", sans-serif;
      font-size: 104px;
      line-height: 1;
    }
    .focus-glyph .label { color: var(--muted); font-size: 11px; }
    .focus-glyph .reason {
      margin-top: 9px;
      color: #6c271b;
      font-size: 11px;
      line-height: 1.35;
    }
    .controls {
      position: sticky;
      z-index: 10;
      top: 0;
      display: grid;
      grid-template-columns: minmax(220px, 1fr) auto;
      gap: 14px;
      margin-bottom: 34px;
      padding: 14px;
      background: rgba(242, 240, 233, .94);
      border: 1px solid var(--line);
      border-radius: 14px;
      backdrop-filter: blur(14px);
    }
    input[type="search"] {
      width: 100%;
      padding: 13px 14px;
      color: var(--ink);
      background: #fff;
      border: 1px solid var(--line);
      border-radius: 9px;
      font: inherit;
    }
    .size-control {
      display: flex;
      align-items: center;
      gap: 10px;
      color: var(--muted);
      font-size: 12px;
    }
    .size-control output { min-width: 42px; color: var(--ink); }
    .block { margin: 0 0 46px; }
    .block-heading {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 14px;
      padding-bottom: 10px;
      border-bottom: 2px solid var(--ink);
    }
    .block-heading h2 { font-size: 18px; }
    .block-count { color: var(--muted); font-size: 11px; }
    .glyph-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(148px, 1fr));
      gap: 10px;
    }
    .glyph-card {
      min-width: 0;
      overflow: hidden;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 11px;
    }
    .glyph-shape {
      display: grid;
      min-height: 132px;
      overflow: hidden;
      place-items: center;
      padding: 12px;
      font-family: "Teleportation One Review", sans-serif;
      font-size: var(--glyph-size);
      font-weight: 400;
      line-height: 1;
    }
    .glyph-meta {
      min-height: 76px;
      padding: 10px;
      border-top: 1px solid var(--line);
    }
    .glyph-code { margin-bottom: 6px; font-size: 11px; font-weight: 800; }
    .glyph-name, .glyph-production {
      overflow: hidden;
      color: var(--muted);
      font-size: 10px;
      line-height: 1.4;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .empty {
      padding: 48px;
      color: var(--muted);
      text-align: center;
    }
    footer {
      padding: 24px clamp(20px, 4vw, 56px) 46px;
      color: var(--muted);
      font-size: 11px;
      line-height: 1.6;
    }
    @media (max-width: 660px) {
      .controls { grid-template-columns: 1fr; }
      .glyph-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .focus-row { grid-template-columns: repeat(2, 1fr); }
    }
  </style>
</head>
<body>
  <header>
    <p class="eyebrow">Complete character review · local rebuilt font</p>
    <h1>TELEPORTATION ONE</h1>
    <p class="deck">Every encoded character in the current TTF, grouped by Unicode block. Combining marks are displayed on a dotted circle. Search by character, glyph name, Unicode name, or codepoint.</p>
    <div class="stats">
      <span class="stat">__GLYPH_COUNT__ encoded characters</span>
      <span class="stat">Version __FONT_VERSION__</span>
      <span class="stat">Teleportation One Regular</span>
    </div>
  </header>
  <main>
    <section class="focus-panel">
      <h2>Visual QA shortlist cleared</h2>
      <p>Every glyph flagged by the full 323-character visual pass has now been replaced with reviewed artwork from the design file.</p>
      <div class="focus-row" id="focus-row"></div>
    </section>
    <section class="controls" aria-label="Specimen controls">
      <input id="search" type="search" placeholder="Filter: section, U+00A7, Oslash, currency…" autocomplete="off">
      <label class="size-control">Glyph size <input id="size" type="range" min="42" max="112" value="72"> <output id="size-output">72px</output></label>
    </section>
    <div id="specimen"></div>
  </main>
  <footer>This page loads <strong>fonts/ttf/TeleportationOne-Regular.ttf</strong> from the same checkout. It contains no fallback image of the glyphs, so what you see is the rebuilt font itself.</footer>
  <script id="glyph-data" type="application/json">__GLYPH_DATA__</script>
  <script>
    const glyphs = JSON.parse(document.getElementById('glyph-data').textContent);
    const specimen = document.getElementById('specimen');
    const search = document.getElementById('search');
    const size = document.getElementById('size');
    const sizeOutput = document.getElementById('size-output');
    const focusCandidates = [];
    const escapeHTML = value => String(value).replace(/[&<>"']/g, character => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    })[character]);

    function card(row, focus = false, reason = '') {
      if (focus) {
        return `<div class="focus-glyph"><div class="shape">${escapeHTML(row.display) || '&nbsp;'}</div><div class="label">${escapeHTML(row.hex)} · ${escapeHTML(row.glyph)}</div><div class="reason">${escapeHTML(reason)}</div></div>`;
      }
      const shown = row.codepoint === 0x20 ? '<span style="opacity:.28">SPACE</span>' : (escapeHTML(row.display) || '&nbsp;');
      const searchText = escapeHTML(`${row.hex} ${row.glyph} ${row.name} ${row.block} ${row.char}`.toLowerCase());
      return `<article class="glyph-card" data-search="${searchText}">
        <div class="glyph-shape">${shown}</div>
        <div class="glyph-meta"><div class="glyph-code">${escapeHTML(row.hex)}</div><div class="glyph-name" title="${escapeHTML(row.name)}">${escapeHTML(row.name)}</div><div class="glyph-production" title="${escapeHTML(row.glyph)}">${escapeHTML(row.glyph)}</div></div>
      </article>`;
    }

    document.getElementById('focus-row').innerHTML = focusCandidates.map(item => card(glyphs.find(row => row.codepoint === item.codepoint), true, item.reason)).join('');

    function render() {
      const query = search.value.trim().toLowerCase();
      const filtered = glyphs.filter(row => !query || `${row.hex} ${row.glyph} ${row.name} ${row.block} ${row.char}`.toLowerCase().includes(query));
      const groups = new Map();
      filtered.forEach(row => {
        if (!groups.has(row.block)) groups.set(row.block, []);
        groups.get(row.block).push(row);
      });
      if (!filtered.length) {
        specimen.innerHTML = '<div class="empty">No characters match that filter.</div>';
        return;
      }
      specimen.innerHTML = [...groups.entries()].map(([name, rows]) => `<section class="block">
        <div class="block-heading"><h2>${name}</h2><span class="block-count">${rows.length} characters</span></div>
        <div class="glyph-grid">${rows.map(row => card(row)).join('')}</div>
      </section>`).join('');
    }

    search.addEventListener('input', render);
    size.addEventListener('input', () => {
      document.documentElement.style.setProperty('--glyph-size', `${size.value}px`);
      sizeOutput.value = `${size.value}px`;
    });
    render();
  </script>
</body>
</html>
'''


if __name__ == "__main__":
    main()
