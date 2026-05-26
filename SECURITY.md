# Security & redaction

This repository is a **public, shareable copy** of curated AI skills. Before publishing, we removed or replaced sensitive content from the originals on the author's machine.

## What was redacted

| Type | Example (removed) | Replacement |
|------|-------------------|-------------|
| Browserless tokens | Hardcoded service tokens | `$BROWSERLESS_TOKEN` env var |
| Private hostnames | Tailscale / internal API hosts | `$BROWSERLESS_HOST` or placeholder URLs |
| Institutional proxy | Yale SOCKS proxy hostnames | `$PROXY_HOST` / `$PROXY_PORT` |
| Search API keys | MeiliSearch bearer keys | `MEILI_API_KEY` env var |
| Personal paths | `/Users/.../Dropbox/...` | Generic `~/` paths |

## Env vars you may need

Set these in your shell or a local `.env` file (never commit real values):

| Variable | Used by | Purpose |
|----------|---------|---------|
| `FRED_API_KEY` | api-data-fetcher | FRED economic data |
| `MEILI_API_KEY` | econ-lit-search | Economics paper search index |
| `MEILI_HOST` | econ-lit-search | Search server URL (optional override) |
| `OPENROUTER_API_KEY` | research-lookup, scientific-schematics, scientific-slides | AI-powered lookup / image generation |
| `OPENAI_API_KEY` | paper-2-web, markitdown | Document conversion pipelines |
| `OPENALEX_API_KEY` | openalex-api | Higher-rate OpenAlex access |
| `NCBI_API_KEY` | citation-management | PubMed searches |
| `BROWSERLESS_TOKEN` | web-scrape | Optional JS rendering (institutional setup) |
| `BROWSERLESS_HOST` | web-scrape | Browserless server hostname |
| WRDS credentials | wrds | Via `~/.pgpass` (see skill docs) |

## Before you commit changes

Always run:

```bash
bash scripts/audit-secrets.sh
```

The audit scans `skills/` for known secret patterns and credential files.
