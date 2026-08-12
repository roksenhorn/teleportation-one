#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "$0")/.." && pwd)"
font="$project_dir/fonts/ttf/TeleportationOne-Regular.ttf"

ufolint "$project_dir/sources/TeleportationOne-Regular.ufo"
gftools ots "$project_dir/fonts/ttf"
glyphsets coverage "$font"
fontbakery check-googlefonts "$font" --no-progress
