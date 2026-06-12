#!/usr/bin/env bash
# Create Barrios88/barrios-skills on GitHub, push main, and trigger Pages deploy.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

if ! gh auth status >/dev/null 2>&1; then
  echo "GitHub login required (one time)."
  echo "Run: gh auth login --hostname github.com --git-protocol ssh --web"
  echo "Then re-run: bash scripts/publish-github.sh"
  exit 1
fi

OWNER="$(gh api user --jq .login)"
REPO="barrios-skills"
OWNER_LC="$(printf '%s' "$OWNER" | tr '[:upper:]' '[:lower:]')"

if ! gh repo view "${OWNER}/${REPO}" >/dev/null 2>&1; then
  echo "Creating ${OWNER}/${REPO}..."
  gh repo create "${REPO}" --public \
    --description "Curated AI agent skills and MCP servers for economists and accountants" \
    --homepage "https://${OWNER_LC}.github.io/${REPO}/" \
    --source . --remote origin --push
else
  echo "Repo exists. Pushing main..."
  git push -u origin main
fi

echo ""
echo "Enable GitHub Pages (if not already):"
echo "  Settings → Pages → Build and deployment → GitHub Actions"
echo ""
echo "Site URL (after workflow runs):"
echo "  https://${OWNER_LC}.github.io/${REPO}/"
