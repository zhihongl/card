#!/usr/bin/env bash
# One-shot setup for Cursor/cloud environments and local onboarding.
# Point the Cursor "update script" at: bash scripts/cloud-setup.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -f requirements.txt ]]; then
  pip install -r requirements.txt
else
  echo "cloud-setup: warning: requirements.txt missing, skipping pip" >&2
fi

mvn -B test
echo "cloud-setup: ok"
