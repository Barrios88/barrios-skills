#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_ROOT="$REPO_ROOT/skills"
echo "Sanitizing skills in $SKILLS_ROOT..."
find "$SKILLS_ROOT" -type f \( -name '*.md' -o -name '*.py' -o -name '*.sh' -o -name '*.yaml' -o -name '*.yml' -o -name '*.json' -o -name '*.txt' \) -print0 | while IFS= read -r -d '' file; do
  if file "$file" | grep -q 'binary'; then continue; fi
  perl -i -pe '
    s/Gravity-Fanta-499-Country/\$BROWSERLESS_TOKEN/g;
    s/chromium\.tailcddce6\.ts\.net/\$BROWSERLESS_HOST/g;
    s/yaleproxy:1080/\$PROXY_HOST:\$PROXY_PORT/g;
    s/socks5h:\/\/127\.0\.0\.1:1080/socks5h:\/\/\$PROXY_HOST:\$PROXY_PORT/g;
    s/som-llm-api\.kyle\.pub/your-llm-api.example.com/g;
    s/SOM_LLM_KEY/YOUR_LLM_API_KEY/g;
    s/SOM_LLM_URL/YOUR_LLM_BASE_URL/g;
    s|/Users/jmb432/|~/|g;
    s|Yale University Dropbox/John Barrios/Claude/Skills|your-skills-folder|g;
  ' "$file"
done
YALE_SETUP="$SKILLS_ROOT/research-tools/web-scrape/references/setup-yale.md"
if [[ -f "$YALE_SETUP" ]] && ! grep -q "Institutional setup (optional)" "$YALE_SETUP"; then
  tmp="$(mktemp)"
  printf '%s\n' '# Institutional setup (optional)' '' '> **Note:** Optional proxy/browserless setup for paywalled journal access. Replace env var placeholders with your own credentials.' '' > "$tmp"
  cat "$YALE_SETUP" >> "$tmp"
  mv "$tmp" "$YALE_SETUP"
fi
find "$SKILLS_ROOT" -type f \( -name '.env' -o -name 'env' -o -name '*.pem' -o -name '.pgpass' \) -delete 2>/dev/null || true
echo "Sanitization complete."
