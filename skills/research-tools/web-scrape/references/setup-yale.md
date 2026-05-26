# Institutional setup (optional)

> **Note:** Optional proxy/browserless setup for paywalled journal access. Replace env var placeholders with your own credentials.

# Yale-Specific Setup: curl_yale + browserless

## Architecture

```
Your Mac ──→ SOCKS5 (127.0.0.1:1080 via ssh -D) ──→ Yale network ──→ JSTOR, Elsevier, etc.
Your Mac ──→ Browserless ($BROWSERLESS_HOST, Yale IP) ──→ JS-rendered pages
```

`chromium.*.ts.net` is a Tailscale name: it resolves only when Tailscale (or your usual path to that host) is up.

---

## What is installed on this machine

| Piece | Location |
|-------|----------|
| `curl_yale` | `~/.local/bin/curl_yale` — proxies via `socks5h://$PROXY_HOST:$PROXY_PORT` (override with `YALE_SOCKS_HOST` / `YALE_SOCKS_PORT`) |
| Browserless env | `~/.config/yale-web-scrape/env` — `BROWSERLESS_HOST`, `BROWSERLESS_TOKEN` (chmod 600) |
| `url-content` | `~/.local/bin/url-content` — POST to Browserless `/content` |
| `url-scrape` | `~/.local/bin/url-scrape` — same fetch + CSS selectors (Python venv under `~/.local/share/yale-web-scrape/venv`) |
| `yale-socks-start` | `~/.local/bin/yale-socks-start` — background `ssh -D` (needs `YALE_SSH_TARGET` in env) |

`~/.zshrc` sources `~/.config/yale-web-scrape/env` when present.

---

## 1. SOCKS tunnel (for `curl_yale`)

**One-off:**

```bash
ssh -D 1080 -N -f yournetid@golf.cs.yale.edu
```

**Helper:** set `YALE_SSH_TARGET` in `~/.config/yale-web-scrape/env` (uncomment and edit), then:

```bash
yale-socks-start
```

**Verify Yale IP:**

```bash
curl_yale -sf https://httpbin.org/ip | jq .
```

Expect Yale ranges (e.g. 130.132.x.x / 172.x.x.x) when the tunnel is up.

**If on Yale VPN:** traffic may already egress from Yale; try `curl_chrome142` without the proxy first and compare IPs.

---

## 2. Browserless (`url-content` / `url-scrape`)

Env vars are loaded from `~/.config/yale-web-scrape/env`. Override there if the host/token changes.

**Check connectivity:**

```bash
curl -sf "https://${BROWSERLESS_HOST}/pressure?token=${BROWSERLESS_TOKEN}" | jq .
```

**Examples:**

```bash
url-content https://example.com | htmlq 'title' --text

url-scrape -s 'h1' -s 'p' https://example.com | jq '.data[0].results[] | {text}'
```

If the host does not resolve, connect Tailscale (or whatever path you use to `$BROWSERLESS_HOST`) and retry.

---

## Playwright WebSocket endpoints

```
wss://$BROWSERLESS_HOST/chromium/playwright?token=$BROWSERLESS_TOKEN&launch=...
wss://$BROWSERLESS_HOST/chromium?token=$BROWSERLESS_TOKEN&launch=...  (CDP)
```

Always include the stealth launch param:

```python
import json, urllib.parse
launch = urllib.parse.quote(json.dumps({
    'stealth': True,
    'args': ['--disable-blink-features=AutomationControlled']
}))
```
