# External MCP servers (not vendored)

Barrios Skills vendors **wrds-mcp** under [`mcp/wrds-mcp/`](../mcp/wrds-mcp/). Everything below is installed from upstream. Pair each with the matching skill when one exists.

| MCP | Why | Install | Skill |
|-----|-----|---------|-------|
| [SEC EDGAR](https://github.com/stefanoamorelli/sec-edgar-mcp) | Filings, XBRL, Form 4 | [sec-edgar-mcp.md](sec-edgar-mcp.md) | `sec-edgar` |
| [OpenEcon Data](https://github.com/hanlulong/openecon-data) | Multi-source macro indicators | [openecon-data-mcp.md](openecon-data-mcp.md) | `api-data-fetcher` |
| [FRED MCP](https://github.com/stefanoamorelli/fred-mcp-server) | FRED-only, local key | Docker/npm + `FRED_API_KEY` | `api-data-fetcher` |
| [Stata-MCP](https://github.com/hanlulong/stata-mcp) | Run Stata from Cursor/VS Code | Upstream extension + Stata license | `stata-regression`, `stata-data-cleaning` |

## License notes

- **SEC EDGAR MCP** and **FRED MCP** are AGPL-3.0 — use upstream images/packages; do not copy their source into this MIT repo without a deliberate license decision.
- **OpenEcon Data** hosted endpoint is fine for agent use; check upstream license before vendoring a self-hosted fork.
- **Stata-MCP** is MIT but requires your own Stata license.

## Stata-MCP (Cursor)

1. Install from [hanlulong/stata-mcp](https://github.com/hanlulong/stata-mcp) (VS Code/Cursor extension + MCP bridge as documented upstream).
2. Point it at your local Stata executable.
3. Prefer `.do` workflows from the Barrios Stata skills (filters, `esttab`, replication hygiene) over ad-hoc one-liners.

If MCP discovery fails in Cursor, fix the Stata path/license first — the skills still work as instruction manuals without MCP.
