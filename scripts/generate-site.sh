#!/usr/bin/env bash
# Refresh site catalog and skill download zips before publishing.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cp "$REPO_ROOT/catalog/skills.json" "$REPO_ROOT/docs/data/skills.json"
python3 "$REPO_ROOT/scripts/build-skill-zips.py"
echo "Updated docs/data/skills.json and skill zip downloads"
