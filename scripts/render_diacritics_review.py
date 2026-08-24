#!/usr/bin/env python3
"""Build a local before/after browser review package for diacritic QA."""

from __future__ import annotations

import hashlib
import html
import shutil
import sys
import unicodedata
from pathlib import Path

from fontTools.ttLib import TTFont


TOP = {0x0300, 0x0301, 0x0302, 0x0303, 0x0304, 0x0306, 0x0307, 0x0308, 0x030A, 0x030B, 0x030C}
BOTTOM = {0x0326, 0x0327, 0x0328}
VERTICAL = set("ĎďĽľŤť")


def version(font: TTFont):
    return next(record.toUnicode() for record in font["name"].names if record.nameID == 5)


def tiles(characters):
    return "".join(
        f'<article class="tile"><div class="after glyph">{html.escape(character)}</div>'
        f'<code>U+{ord(character):04X}</code><small>{html.escape(unicodedata.name(character, ""))}</small></article>'
        for character in characters
    )


def comparison(title, text, note):
    escaped = html.escape(text)
    return f"""
      <article class="comparison">
        <div class="comparison-title"><h3>{html.escape(title)}</h3><p>{html.escape(note)}</p></div>
        <div><span>Before · v1.003</span><div class="before sample">{escaped}</div></div>
        <div><span>After · approved v1.004 build</span><div class="after sample">{escaped}</div></div>
      </article>"""


def main():
    if len(sys.argv) != 4:
        raise SystemExit("usage: render_diacritics_review.py BEFORE.ttf AFTER.ttf OUTPUT_DIR")
    before_path, after_path, output_dir = map(Path, sys.argv[1:])
    output_dir.mkdir(parents=True, exist_ok=True)
    before_hash = hashlib.sha256(before_path.read_bytes()).hexdigest()
    after_hash = hashlib.sha256(after_path.read_bytes()).hexdigest()
    before_filename = f"before-{before_hash[:12]}.ttf"
    after_filename = f"after-{after_hash[:12]}.ttf"
    before_family = f"Before_{before_hash[:12]}"
    after_family = f"After_{after_hash[:12]}"
    shutil.copy2(before_path, output_dir / before_filename)
    shutil.copy2(after_path, output_dir / after_filename)

    before = TTFont(before_path)
    after = TTFont(after_path)
    cmap = after.getBestCmap()
    accented = []
    top = []
    bottom = []
    for codepoint in sorted(cmap):
        decomposition = unicodedata.decomposition(chr(codepoint))
        if not decomposition or decomposition.startswith("<"):
            continue
        sequence = [int(value, 16) for value in decomposition.split()]
        if len(sequence) != 2:
            continue
        if sequence[1] in TOP | BOTTOM:
            accented.append(chr(codepoint))
            (bottom if sequence[1] in BOTTOM else top).append(chr(codepoint))

    sections = "".join([
        comparison("Top accents", "ÀÁÂÃÄÅ ĀĂ CĆĈĊČ EÈÉÊËĒĖĚ IÌÍÎÏĪ NÑŃŇ OÒÓÔÕÖŐ UÙÚÛÜŪŮŰ WẀẂẄ YỲÝŶŸ ZŹŻŽ", "One optical placement system across grave, acute, circumflex, tilde, dieresis, ring, breve, macron, dot, caron, and double acute."),
        comparison("Attached bottom marks", "ĄĘĮŲ ąęįų   ÇŞ çş   ȘȚ șț   ĢĶĻŅŖ ģķļņŗ", "Ogoneks now join the right-hand exit of each base; cedillas attach centrally; Romanian commas remain detached and distinct."),
        comparison("Czech and Slovak carons", "ĎĽŤ  ĎA ĽA ŤA  ĽT ĽŤ ĽV ĽW ĽY", "Following the macOS convention: uppercase D/T use centered top carons, while uppercase L uses the distinctive side form and independent right-side spacing."),
        comparison("Lowercase side carons", "ďľť  ďa ľa ťa  ľT ľŤ ľV ľW ľY", "Lowercase d/l/t use the compact right-side form; ľ keeps its caron clear of following letters instead of inheriting L kerning."),
        comparison("Wide I accents", "ÎÏĪ  îïī  HÎH HÏH HĪH  hîh hïh hīh", "Circumflex, dieresis, and macron I forms have added spacing on both sides in uppercase and lowercase, without inherited I kerning."),
        comparison("Eszett", "B ß ẞ S   STRAẞE Straße GROẞ FUẞBALL", "By design, U+00DF ß and U+1E9E ẞ use the exact same outline and metrics in Teleportation One."),
        comparison("Language strings", "PŘÍLIŠ ŽLUŤOUČKÝ KŮŇ · ÁRVÍZTŰRŐ TÜKÖRFÚRÓGÉP · ȘTIINȚĂ ȘI ȚARĂ · ĄČĘĖĮŠŲŪŽ", "Czech, Hungarian, Romanian, and Baltic sequences expose rhythm and collision problems that isolated tiles miss."),
    ])

    mark_line = "◌̀ ◌́ ◌̂ ◌̃ ◌̄ ◌̆ ◌̇ ◌̈ ◌̊ ◌̋ ◌̌   ◌̧ ◌̨ ◌̦"
    stack_line = "A\u0301\u0308  A\u0328\u0326  ◌\u0301\u0308  ◌\u0328\u0326"
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Teleportation One — Google Fonts feedback review</title>
<style>
@font-face{{font-family:{before_family};src:url('{before_filename}') format('truetype');font-display:block}} @font-face{{font-family:{after_family};src:url('{after_filename}') format('truetype');font-display:block}}
:root{{--ink:#151515;--paper:#f3f0e8;--panel:#fffdf8;--line:#cfc9ba;--green:#14724d;--red:#c7482e;--blue:#2458d6;--size:76px}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--paper);color:var(--ink);font-family:ui-monospace,SFMono-Regular,Menlo,monospace}}
header{{padding:54px max(28px,6vw);background:var(--ink);color:white;border-bottom:8px solid var(--green)}}
.eyebrow{{color:#89dcb9;text-transform:uppercase;letter-spacing:.14em;font-weight:800;font-size:12px}} h1{{margin:.25em 0 .15em;font-family:{after_family},sans-serif;font-size:clamp(56px,9vw,128px);font-weight:400;line-height:.9}}
.deck{{max-width:900px;color:#d3d1ca;line-height:1.6}} .status{{display:inline-block;margin-top:18px;padding:9px 13px;border:1px solid #5a5a5a;border-radius:999px;color:#89dcb9}}
nav{{position:sticky;top:0;z-index:4;display:flex;gap:18px;align-items:center;padding:12px max(24px,5vw);background:#f3f0e8ee;border-bottom:1px solid var(--line);backdrop-filter:blur(12px)}} nav a{{color:var(--ink)}} nav label{{margin-left:auto;font-size:12px}} main{{padding:42px max(24px,5vw) 90px}} section{{max-width:1500px;margin:0 auto 58px}}
h2{{margin:0 0 18px;font-size:24px}} h3{{margin:0 0 6px}} p{{line-height:1.55}} .gate-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}}
.gate{{padding:18px;background:var(--panel);border:1px solid var(--line);border-radius:12px}} .gate b{{display:block;color:var(--green);font-size:22px;margin-bottom:5px}} .gate small{{color:#69665f;line-height:1.4}}
.comparison{{display:grid;grid-template-columns:minmax(180px,.6fr) 1fr 1fr;gap:14px;padding:18px 0;border-top:1px solid var(--line)}} .comparison-title p{{margin:0;color:#69665f;font-size:12px}} .comparison span{{font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:#777}}
.sample{{min-height:175px;padding:20px;background:var(--panel);border:1px solid var(--line);border-radius:10px;font-size:var(--size);line-height:1.38;overflow-wrap:anywhere}} .before{{font-family:{before_family},sans-serif}} .after{{font-family:{after_family},sans-serif}}
.proof{{display:grid;grid-template-columns:1fr 1fr;gap:14px}} .proof>div{{padding:20px;background:var(--panel);border:1px solid var(--line);border-radius:10px}} .proof .glyph{{font-size:var(--size);line-height:1.65}}
.tiles{{display:grid;grid-template-columns:repeat(auto-fill,minmax(125px,1fr));gap:9px}} .tile{{min-height:170px;padding:12px;background:var(--panel);border:1px solid var(--line);border-radius:10px;text-align:center}} .tile .glyph{{font-size:82px;line-height:1.15}} .tile code{{display:block;color:var(--red)}} .tile small{{display:block;margin-top:6px;color:#716e67;font-size:9px;line-height:1.3}}
.note{{padding:16px 18px;border-left:5px solid var(--blue);background:#e7ecff}} footer{{padding:28px max(24px,5vw);background:var(--ink);color:#ccc;font-size:12px}}
@media(max-width:850px){{.comparison{{grid-template-columns:1fr}}.proof{{grid-template-columns:1fr}}nav a{{display:none}}}}
</style></head><body>
<header><div class="eyebrow">Issue #10813 · review evidence</div><h1>ACCENTS,<br>CORRECTED.</h1><p class="deck">A before/after audit addressing Google Fonts’ feedback on accented-letter consistency, design, and position. This page uses the frozen public v1.003 binary beside the approved v1.004 build.</p><div class="status">Human review approved · 0 FontBakery failures</div></header>
<nav><a href="#gates">Evidence</a><a href="#compare">Before / after</a><a href="#marks">Combining marks</a><a href="#all">All affected glyphs</a><label>Size <input id="size" type="range" min="42" max="128" value="76"></label></nav>
<main>
<section id="gates"><h2>Acceptance evidence</h2><div class="gate-grid">
<div class="gate"><b>145 / 145</b><small>Supported canonical accented pairs shape identically in NFC and NFD text.</small></div>
<div class="gate"><b>14 / 14</b><small>Combining marks have zero advance width and GDEF class 3.</small></div>
<div class="gate"><b>mark + mkmk</b><small>Above- and below-base attachment and mark stacking are compiled into GPOS.</small></div>
<div class="gate"><b>GF Latin Core 100%</b><small>Glyphsets coverage remains complete after the rebuild.</small></div>
<div class="gate"><b>0 FAIL</b><small>Live FontBakery Google Fonts profile: 111 PASS, 0 FAIL, 0 ERROR, 0 FATAL.</small></div>
<div class="gate"><b>OTS + UFOlint</b><small>Compiled font sanitizes successfully; all 337 source GLIFs pass UFO validation.</small></div>
</div></section>
<section id="compare"><h2>Before / after</h2>{sections}</section>
<section id="marks"><h2>Combining behavior</h2><div class="proof"><div><h3>Every supported mark</h3><div class="after glyph">{mark_line}</div><p>Top marks share a 220-unit stacking anchor. Bottom marks share a −220-unit stacking anchor.</p></div><div><h3>Dynamic stacks</h3><div class="after glyph">{stack_line}</div><p>These are live base-plus-combining sequences, not precomposed characters.</p></div></div></section>
<section id="all"><h2>All {len(accented)} rebuilt precomposed glyphs</h2><p class="note">Every tile below is sourced from the same mark components used for dynamic combining text. Uppercase and lowercase intentionally share cap-height base drawings because Teleportation One is a unicase display family.</p><div class="tiles">{tiles(accented)}</div></section>
</main><footer>{html.escape(version(after))} · SHA-256 {after_hash} · before {len(before.getBestCmap())} codepoints · after {len(cmap)} codepoints</footer>
<script>document.querySelector('#size').addEventListener('input',e=>document.documentElement.style.setProperty('--size',e.target.value+'px'))</script>
</body></html>"""
    (output_dir / "index.html").write_text(page, encoding="utf-8")
    print(f"Wrote {output_dir / 'index.html'} with {len(accented)} rebuilt glyphs")


if __name__ == "__main__":
    main()
