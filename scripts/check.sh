#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "$0")/.." && pwd)"
font="$project_dir/fonts/ttf/TeleportationOne-Regular.ttf"
skip_network=false

if [[ "${1:-}" == "--skip-network" ]]; then
  skip_network=true
elif [[ $# -ne 0 ]]; then
  echo "usage: $0 [--skip-network]" >&2
  exit 2
fi

ufolint "$project_dir/sources/TeleportationOne-Regular.ufo"
gftools ots "$project_dir/fonts/ttf"
glyphsets coverage "$font"
python3 "$project_dir/scripts/validate_metadata.py" "$font"
if $skip_network; then
  fontbakery check-googlefonts "$font" \
    --no-progress \
    --error-code-on FAIL \
    --skip-network
else
  fontbakery check-googlefonts "$font" \
    --no-progress \
    --error-code-on FAIL
fi
