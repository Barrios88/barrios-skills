# OpenEcon Data MCP setup

Natural-language access to 330k+ indicators (FRED, World Bank, IMF, Eurostat, and more). Upstream: [hanlulong/openecon-data](https://github.com/hanlulong/openecon-data) / [openecon.ai](https://openecon.ai/).

Complements the [`api-data-fetcher`](../skills/research-tools/api-data-fetcher/) skill: prefer the MCP for interactive agent queries; use the skill’s Python patterns for reproducible project scripts.

## Hosted MCP (simplest)

**Claude Code:**

```bash
claude mcp add --transport sse openecon-data https://data.openecon.ai/mcp --scope user
```

**Codex:**

```bash
codex mcp add openecon-data --url https://data.openecon.ai/mcp
```

**Cursor:** add an MCP server entry pointing at the SSE endpoint `https://data.openecon.ai/mcp` (see current Cursor MCP UI for SSE/HTTP transport fields). First queries may work without an account; create a free OpenEcon account if rate-limited.

## Self-host

Follow upstream `./scripts/setup.sh` if you need air-gapped or custom keys. Not required for most Barrios Skills users.

## When to prefer FRED-only MCP

If you only need FRED and want a local API-key server, see [external-mcps.md](external-mcps.md) (stefanoamorelli/fred-mcp-server). For multi-source macro work, OpenEcon is the better default.

## Verify

Ask: “US unemployment rate monthly since 2015 from FRED — return the series id and last observation date.” Confirm against [fred.stlouisfed.org](https://fred.stlouisfed.org/).
