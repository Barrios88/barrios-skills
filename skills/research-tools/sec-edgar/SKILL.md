---
name: sec-edgar
description: Pull SEC EDGAR filings, XBRL financials, and Form 3/4/5 insider trades for accounting and finance research. Prefer the SEC EDGAR MCP for live lookups; use WRDS for panel Compustat/CRSP merges. Enforces CIK discipline, User-Agent rules, and sample inspection before claiming results.
curated-by: John Barrios
collection: barrios-skills
upstream: https://github.com/stefanoamorelli/sec-edgar-mcp
---
> **Barrios Skills** — John Barrios's curated workflow for economists and accountants. Prioritize reproducible empirical work, clear identification language, and journal-ready output.

## SEC EDGAR MCP (recommended for AI agents)

Use Stefano Amorelli's **sec-edgar-mcp** (built on edgartools) when the agent needs live filings.

**Before querying EDGAR, the user must:**

1. Follow **[install/sec-edgar-mcp.md](../../../install/sec-edgar-mcp.md)**
2. Set a real User-Agent: `SEC_EDGAR_USER_AGENT="Name (email@institution.edu)"` (SEC fair-access requirement)
3. Prefer MCP tools over ad-hoc scraping when the server is registered

**When to use WRDS instead:** Compustat fundamentals panels, CRSP returns, CCM links, ExecuComp, ISS, TRACE/TAQ — use the [`wrds`](../../econometrics/wrds/) skill + wrds-mcp. EDGAR is for filing text, XBRL facts, 8-K events, and public insider Forms 3/4/5 when you do not need WRDS panel infrastructure.

---

# SEC EDGAR for accounting & finance research

## Iron law: no claim without sample inspection

Before asserting that a filing pull "worked":

1. **IDENTIFY** the firm (CIK or ticker → CIK) and form type
2. **VALIDATE** the accession / period you intended
3. **EXECUTE** the pull
4. **INSPECT** a sample (company name, filing date, section heading, one numeric fact)
5. **CITE** the EDGAR URL in notes so numbers are auditable

### Rationalization table — stop if you think

| Excuse | Reality | Do instead |
|--------|---------|------------|
| "Ticker is enough" | Tickers recycle; CIK is stable | Resolve CIK first, store it |
| "XBRL equals Compustat" | Tag coverage and restatements differ | Document source; reconcile if both used |
| "I'll scrape HTML tables" | Layout breaks; XBRL/MCP is stabler | Prefer XBRL facts or MCP financials tools |
| "Form 4 = Insider Trading database" | Public EDGAR ≠ cleaned WRDS panels | Use WRDS for research panels when available |

## Typical workflows

### 1. Company → filings

- Resolve **CIK** from name or ticker
- List recent **10-K / 10-Q / 8-K** with filing dates
- Extract a section (e.g. Item 1A, MD&A) only when needed — avoid dumping full HTML into context

### 2. Financial statement facts

- Prefer XBRL-parsed balance sheet / income / cash flow from MCP
- Record units, scale, and period end
- Flag: never invent a ratio; compute from retrieved facts and show the formula

### 3. Insider trades (Form 3/4/5)

- Pull transactions for a CIK and date window
- Note: open-market vs award/grant; role of reporting person
- For large-sample insider studies, prefer WRDS/Thomson when the user has access

## Accounting / finance research notes

- **Identification language:** filing date ≠ event date for some 8-Ks; use the relevant timestamp the paper needs
- **Restatements:** XBRL history can change; pin accession numbers in replication folders
- **Fair access:** respect SEC rate limits; never share another researcher's User-Agent email
- **Replication:** save accession numbers + URLs alongside any extracted table

## Output checklist

- [ ] CIK recorded
- [ ] Form type and accession (or filing URL) recorded
- [ ] Sample row/section inspected
- [ ] WRDS vs EDGAR choice justified if both could apply
