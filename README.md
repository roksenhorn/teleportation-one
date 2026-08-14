# Teleportation One

![Teleportation One specimen](documentation/teleportation-one-specimen.png)

Teleportation One is a bold, all-caps display typeface built for speed,
impact, and dependable legibility. Lowercase text uses the same energetic
capital forms, making the family especially effective for headlines, labels,
posters, and compact interface moments.

The family contains one static style, published as Regular under Google Fonts'
single-weight naming convention. It supports the complete
Google Fonts Latin Core glyph set, including Western and Central European
languages, combining marks, currency symbols, mathematical operators, and
typographic punctuation.

Default numerals are proportional. Enable the OpenType `tnum` feature for
tabular figures. The font also includes `kern`, `liga`, `locl`, `mark`, and
`mkmk` support.

## Build

Create a Python virtual environment, install the pinned dependencies, and run
the build script:

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
./build.sh
```

The build reads `sources/TeleportationOne-Regular.ufo` and writes
`fonts/ttf/TeleportationOne-Regular.ttf`.

## Quality assurance

With the dependencies installed, run:

```sh
./scripts/check.sh
```

The checks cover UFO validity, OpenType sanitization, Google Fonts Latin Core
coverage, release metadata, required OpenType behavior, and the FontBakery
Google Fonts profile. GitHub Actions runs the same reproducible build and QA
checks for every change to `main` and every pull request. CI uses
`./scripts/check.sh --skip-network` so external service outages cannot mask the
font's local validation result; release validation uses the default live checks.

Regenerate the documentation specimen through OpenType shaping with:

```sh
python scripts/render_specimen.py
```

## License and copyright

Teleportation One is licensed under the SIL Open Font License, Version 1.1,
with no Reserved Font Names. No name, including Teleportation One, is reserved.
Ryan Oksenhorn is the sole designer, author, and copyright holder. See
`OFL.txt`, `AUTHORS.txt`, and `COPYRIGHT.md`.

## Release history

See [CHANGELOG.md](CHANGELOG.md) for versioned release notes.

## Credits

Design and implementation are by Ryan Oksenhorn. See
[ACKNOWLEDGMENTS.md](ACKNOWLEDGMENTS.md) for the open-source tools used to
build and validate the family.
