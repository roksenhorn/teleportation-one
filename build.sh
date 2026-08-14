#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "$0")" && pwd)"
build_dir="$(mktemp -d)"
trap 'rm -rf "$build_dir"' EXIT
export SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-1786492800}"

mkdir -p "$project_dir/fonts/ttf"

fontmake \
  -u "$project_dir/sources/TeleportationOne-Regular.ufo" \
  -o ttf \
  --output-path "$build_dir/TeleportationOne-Regular.ttf" \
  --production-names \
  --overlaps-backend pathops

gftools fix-nonhinting \
  "$build_dir/TeleportationOne-Regular.ttf" \
  "$project_dir/fonts/ttf/TeleportationOne-Regular.ttf"

python3 "$project_dir/scripts/postprocess_font.py" \
  "$project_dir/fonts/ttf/TeleportationOne-Regular.ttf"
