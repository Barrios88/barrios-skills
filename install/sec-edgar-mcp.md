# SEC EDGAR MCP setup

Companion to the [`sec-edgar` skill](../skills/research-tools/sec-edgar/). Upstream: [stefanoamorelli/sec-edgar-mcp](https://github.com/stefanoamorelli/sec-edgar-mcp) (AGPL-3.0 — **not** vendored in this repo; install from upstream).

## What you get

Live MCP tools for CIK lookup, 10-K/10-Q/8-K retrieval, XBRL financial statements, and Form 3/4/5 insider trades.

## Prerequisites

- Python 3.11+ with [`uv`](https://github.com/astral-sh/uv) (**recommended** — no Docker required)
- Or Docker, if you prefer the upstream image
- A contact email for the SEC User-Agent string

## Cursor / Claude config (uvx — recommended)

```json
{
  "mcpServers": {
    "sec-edgar-mcp": {
      "command": "uvx",
      "args": ["sec-edgar-mcp"],
      "env": {
        "SEC_EDGAR_USER_AGENT": "Your Name (you@university.edu)"
      }
    }
  }
}
```

Replace the User-Agent with **your** name and email. The SEC requires identifiable contact info.

## Cursor / Claude config (Docker alternative)

```json
{
  "mcpServers": {
    "sec-edgar-mcp": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "SEC_EDGAR_USER_AGENT=Your Name (you@university.edu)",
        "stefanoamorelli/sec-edgar-mcp:latest"
      ]
    }
  }
}
```

## Pair with WRDS

| Need | Tool |
|------|------|
| Filing text, XBRL facts, public Form 4 | SEC EDGAR MCP + `sec-edgar` skill |
| Compustat/CRSP panels, CCM, ExecuComp | [`wrds-mcp`](wrds-mcp.md) + `wrds` skill |

## Verify

Ask the agent: “Resolve the CIK for Apple Inc. and list the latest 10-K accession.” Confirm the company name and filing date before trusting further pulls.
