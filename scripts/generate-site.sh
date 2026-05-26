#!/usr/bin/env bash
# Refresh docs/data/skills.json from catalog before publishing the site.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cp "$REPO_ROOT/catalog/skills.json" "$REPO_ROOT/docs/data/skills.json"
echo "Updated docs/data/skills.json"
