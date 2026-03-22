#!/usr/bin/env bash
# Opens the WI-000001 HTML progress view in Chrome (for demos / screen recording).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HTML="$ROOT/AllocationsManagement.Content/specs/active/WI-000001/progress-dashboard.html"
if [[ ! -f "$HTML" ]]; then
  echo "Missing: $HTML" >&2
  exit 1
fi
# Replace green/blank VM background with a neutral slate (best-effort).
if command -v xsetroot >/dev/null 2>&1; then
  xsetroot -solid '#1e293b' || true
fi
URL="file://$HTML"
# Isolated profile avoids locks with other Chrome instances; flags align with typical cloud VMs.
exec google-chrome \
  --user-data-dir="/tmp/wi-000001-progress-chrome" \
  --no-first-run --no-default-browser-check \
  --window-size=1200,860 \
  --new-window "$URL" "$@"
