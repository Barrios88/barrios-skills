#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ALLOWLIST="$REPO_ROOT/scripts/audit-allowlist.txt"
hits=0
check_pattern() {
  local label="$1" pattern="$2" results
  results=$(grep -rniE "$pattern" "$REPO_ROOT/skills" --include='*.md' --include='*.py' --include='*.sh' --include='*.yaml' --include='*.json' --exclude-dir='.git' 2>/dev/null || true)
  if [[ -f "$ALLOWLIST" && -n "$results" ]]; then
    while IFS= read -r line; do
      [[ -z "$line" || "$line" =~ ^# ]] && continue
      results=$(echo "$results" | grep -vF "$line" || true)
    done < "$ALLOWLIST"
  fi
  if [[ -n "$results" ]]; then
    echo "FAIL: $label"
    echo "$results" | head -20
    hits=$((hits + 1))
  fi
}
echo "Auditing $REPO_ROOT..."
check_pattern "Hardcoded browserless token" "Gravity-Fanta"
check_pattern "Private API host (kyle.pub)" "kyle\.pub"
check_pattern "Private Tailscale host" "tailcddce6"
check_pattern "Personal username in paths" "jmb432"
check_pattern "Personal Dropbox path" "Yale University Dropbox"
check_pattern "Real-looking API key (sk-)" "sk-[a-zA-Z0-9]{20,}"
while IFS= read -r f; do echo "FAIL: Credential file: $f"; hits=$((hits + 1)); done < <(find "$REPO_ROOT" -type f \( -name '.env' -o -name '.pgpass' -o -name '*.pem' \) ! -path '*/.git/*' 2>/dev/null)
if [[ "$hits" -eq 0 ]]; then echo "Audit passed."; exit 0; else echo "Audit failed: $hits issue(s)."; exit 1; fi

check_pattern "Hardcoded MeiliSearch key" "mpx_[a-zA-Z0-9_]+"
