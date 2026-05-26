---
name: wrds
version: 1.0
description: This skill should be used when the user asks to "query WRDS", "access Compustat", "get CRSP data", "pull Form 4 insider data", "query ISS compensation", "download SEC EDGAR filings", "get ExecuComp data", "access Capital IQ", "query TRACE bond data", "clean TRACE", "merge FISD", "query TAQ", "pull intraday trades or quotes", "build NBBO", "compute effective spread", or needs WRDS PostgreSQL query patterns.
curated-by: John Barrios
collection: barrios-skills
---
> **Barrios Skills** — John Barrios's curated workflow for economists and accountants. Prioritize reproducible empirical work, clear identification language, and journal-ready output.

## WRDS MCP (recommended for AI agents)

John Barrios's **wrds-mcp** server exposes WRDS to Cursor, Claude, and other MCP clients.

**Before querying WRDS, the user must:**

1. Install the MCP from [`mcp/wrds-mcp/`](../../../mcp/wrds-mcp/) — see **[install/wrds-mcp.md](../../../install/wrds-mcp.md)**
2. Set **their own** credentials: `WRDS_USERNAME` and `WRDS_PASSWORD` (from their WRDS account)
3. Start the tunnel: `bash mcp/wrds-mcp/tunnel/tunnel_up.sh` and approve **Duo MFA** once per session
4. Register the MCP with `WRDS_TUNNEL_PORT=49600` in Cursor or Claude config

When MCP tools are available (`wrds_run_sql`, `wrds_get_compustat`, etc.), **prefer MCP over raw Python connections**. Still apply all filter rules in this skill.

If the user has not configured MCP credentials, **stop and walk them through** [install/wrds-mcp.md](../../../install/wrds-mcp.md) — do not guess usernames or passwords.


## Contents

- [WRDS MCP (recommended for AI agents)](#wrds-mcp-recommended-for-ai-agents)
- [Query Enforcement](#query-enforcement)
- [Quick Reference: Table Names](#quick-reference-table-names)
- [Connection](#connection)
- [Critical Filters](#critical-filters)
- [Parameterized Queries](#parameterized-queries)
- [Additional Resources](#additional-resources)

# WRDS Data Access

WRDS (Wharton Research Data Services) provides academic research data via PostgreSQL at `wrds-pgdata.wharton.upenn.edu:9737`.

## Query Enforcement

### IRON LAW: NO QUERY WITHOUT FILTER VALIDATION FIRST

Before executing ANY WRDS query, you MUST:
1. **IDENTIFY** what filters are required for this dataset
2. **VALIDATE** the query includes those filters
3. **VERIFY** parameterized queries (never string formatting)
4. **EXECUTE** the query
5. **INSPECT** a sample of results before claiming success

This is not negotiable. Claiming query success without sample inspection is LYING to the user about data quality.

### Rationalization Table - STOP If You Think:

| Excuse | Reality | Do Instead |
|--------|---------|------------|
| "I'll add filters later" | You'll forget and pull bad data | Add filters NOW, before execution |
| "User didn't specify filters" | Standard filters are ALWAYS required | Apply Critical Filters section defaults |
| "Just a quick test query" | Test queries with bad filters teach bad patterns | Use production filters even for tests |
| "I'll let the user filter in pandas" | Pulling millions of unnecessary rows wastes time/memory | Filter at database level FIRST |
| "The query worked, so it's correct" | Query success ≠ data quality | INSPECT sample for invalid records |
| "I can use f-strings for simple queries" | SQL injection risk + wrong type handling | ALWAYS use parameterized queries |

### Red Flags - STOP Immediately If You Think:

- "Let me run this query quickly to see what's there" → NO. Check Critical Filters section first.
- "I'll just pull everything and filter later" → NO. Database-level filtering is mandatory.
- "The table name is obvious from the request" → NO. Check Quick Reference section for exact names.
- "I can inspect the data after the user sees it" → NO. Sample inspection BEFORE claiming success.

### Query Validation Checklist

Before EVERY query execution:

**For Compustat queries (comp.funda, comp.fundq):**
- [ ] Includes `indfmt = 'INDL'`
- [ ] Includes `datafmt = 'STD'`
- [ ] Includes `popsrc = 'D'`
- [ ] Includes `consol = 'C'`
- [ ] Uses parameterized queries for variables
- [ ] Date range is explicitly specified

**For CRSP v2 queries (crsp.dsf_v2, crsp.msf_v2):**
- [ ] Post-query filter: `sharetype == 'NS'`
- [ ] Post-query filter: `securitytype == 'EQTY'`
- [ ] Post-query filter: `securitysubtype == 'COM'`
- [ ] Post-query filter: `usincflg == 'Y'`
- [ ] Post-query filter: `issuertype.isin(['ACOR', 'CORP'])`
- [ ] Uses parameterized queries

**For Form 4 queries (tr_insiders.table1):**
- [ ] Transaction type filter specified (acqdisp)
- [ ] Transaction codes specified (trancode)
- [ ] Date range is explicitly specified
- [ ] Uses parameterized queries

**For TAQ queries (taqm_YYYY.ctm_* / cqm_* / complete_nbbo_*):**
- [ ] Using `taqm_YYYY` (daily partitioned) for post-2003 work, not legacy `taq`
- [ ] Trade filter: `tr_corr = '00'` (string, not integer)
- [ ] Trade conditions: drop `tr_scond` containing `Z`, `O`, `T`, `U`, `G`, `B` (non-regular)
- [ ] Regular trading hours: `time_m BETWEEN '09:30:00' AND '16:00:00'`
- [ ] Price > 0 and size > 0 sanity checks
- [ ] For NBBO: use `complete_nbbo_*` (not `nbbom_*` — incomplete by design)
- [ ] If joining to CRSP: use `wrdsapps_link_crsp_taqm` with `sdate`/`edate` bounds
- [ ] Consider `wrds_iid_YYYY` for pre-computed daily liquidity measures
- [ ] Never `SELECT *` — specify columns (ctm has 20, cqm/nbbom are huge)
- [ ] Sort explicitly by `(time_m, time_m_nano, tr_seqnum)` — insertion order not guaranteed

**For TRACE queries (trace_enhanced.trace_enhanced):**
- [ ] Using `trace_enhanced` (uncapped) not `trace_standard` (capped) for research
- [ ] Dick-Nielsen cleaning applied: drop `trc_st IN ('X','C','W','Y')` + matched originals
- [ ] Pre-/post-2012-02-06 logic branch selected correctly
- [ ] Agency double-count filter: `NOT (cmsn_trd='Y' AND cntra_mp_id='D')`
- [ ] Commissioned trades handled (`cmsn_trd='N'` for price/yield work)
- [ ] Special trades excluded: `spcl_trd_fl != 'Y'` (for price/liquidity analysis)
- [ ] FISD merge for bond characteristics (coupon, maturity, rating, issuer)
- [ ] Date range is explicitly specified on `trd_exctn_dt`
- [ ] Uses parameterized queries

**For ALL queries:**
- [ ] Sample inspection with `.head()` or `.sample()` BEFORE claiming success
- [ ] Row count verification (is result size reasonable?)
- [ ] NULL value check on critical columns
- [ ] Date range validation (does min/max match expectations?)

## Quick Reference: Table Names

| Dataset | Schema | Key Tables |
|---------|--------|------------|
| Compustat | `comp` | `company`, `funda`, `fundq`, `secd` |
| ExecuComp | `comp_execucomp` | `anncomp` |
| CRSP | `crsp` | `dsf`, `msf`, `stocknames`, `ccmxpf_linkhist` |
| CRSP v2 | `crsp` | `dsf_v2`, `msf_v2`, `stocknames_v2` |
| Form 4 Insiders | `tr_insiders` | `table1`, `header`, `company` |
| ISS Incentive Lab | `iss_incentive_lab` | `comppeer`, `sumcomp`, `participantfy` |
| Capital IQ | `ciq` | `wrds_compensation` |
| IBES | `tr_ibes` | `det_epsus`, `statsum_epsus` |
| SEC EDGAR | `wrdssec` | `wrds_forms`, `wciklink_cusip` |
| SEC Search | `wrds_sec_search` | `filing_view`, `registrant` |
| EDGAR | `edgar` | `filings`, `filing_docs` |
| Fama-French | `ff` | `factors_monthly`, `factors_daily` |
| LSEG/Datastream | `tr_ds` | `ds2constmth`, `ds2indexlist` |
| TRACE Enhanced (bonds, uncapped) | `trace_enhanced` | `trace_enhanced`, `trace_btds144a_enhanced`, `trace_agency_enhanced` |
| TRACE Standard (bonds, capped) | `trace_standard` | `trace`, `trade_summary` |
| FISD bond characteristics (Mergent) | `fisd` | `fisd_mergedissue`, `fisd_mergedissuer`, `fisd_issue`, `fisd_issuer` |
| TAQ Daily MSEC (ticks, µs) | `taqm_YYYY` | `ctm_YYYYMMDD`, `cqm_YYYYMMDD`, `complete_nbbo_YYYYMMDD`, `nbbom_YYYYMMDD`, `mastm_YYYY`, `wrds_iid_YYYY` |
| TAQ Monthly (legacy, 1993–2014, sec) | `taq` | monthly consolidated trades/quotes |
| CRSP↔TAQ link | `wrdsapps_link_crsp_taqm` | link table |

## Connection

Initialize PostgreSQL connection to WRDS:

```python
import psycopg2

conn = psycopg2.connect(
    host='wrds-pgdata.wharton.upenn.edu',
    port=9737,
    database='wrds',
    sslmode='require'
    # Credentials from ~/.pgpass
)
```

Configure authentication via `~/.pgpass` with `chmod 600`:
```
wrds-pgdata.wharton.upenn.edu:9737:wrds:USERNAME:PASSWORD
```

Connect via SSH tunnel:
```bash
ssh wrds
```

This uses `~/.ssh/wrds_rsa` for authentication.

## Critical Filters

### Compustat Standard Filters
Always include for clean fundamental data:
```sql
WHERE indfmt = 'INDL'
  AND datafmt = 'STD'
  AND popsrc = 'D'
  AND consol = 'C'
```

### CRSP v2 Common Stock Filter
Equivalent to legacy `shrcd IN (10, 11)`:
```python
df = df.loc[
    (df.sharetype == 'NS') &
    (df.securitytype == 'EQTY') &
    (df.securitysubtype == 'COM') &
    (df.usincflg == 'Y') &
    (df.issuertype.isin(['ACOR', 'CORP']))
]
```

### Form 4 Transaction Types
```sql
WHERE acqdisp = 'D'  -- Dispositions
  AND trancode IN ('S', 'D', 'G', 'F')  -- Sales, Dispositions, Gifts, Tax
```

### TAQ Standard Cleaning (Holden-Jacobsen 2014)
Minimum filter for academic intraday work:
```sql
-- Trades (ctm_YYYYMMDD)
WHERE tr_corr = '00'                               -- uncorrected
  AND price > 0 AND size > 0
  AND time_m BETWEEN '09:30:00'::time AND '16:00:00'::time
  AND (tr_scond IS NULL OR tr_scond = ''
       OR tr_scond !~ '[BGJKLOTUWZ4567]')          -- regular-way only

-- Quotes (cqm_YYYYMMDD)
WHERE bid > 0 AND ask > 0 AND ask > bid
  AND bidsiz > 0 AND asksiz > 0
  AND qu_cond IN ('A','B','H','O','R','W')
  AND time_m BETWEEN '09:30:00'::time AND '16:00:00'::time
```
**Always prefer `complete_nbbo_*` over `nbbom_*`** — the raw NBBO feed is
incomplete when one exchange holds both sides of the top of book. If
re-deriving, UNION `nbbom` with `cqm` records where
`natbbo_ind='1' OR nasdbbo_ind='4'`. See `references/taq.md`.

### TRACE Enhanced Cleaning (Dick-Nielsen 2014)
Apply BEFORE any price/volume analysis:
```sql
-- Post-2012-02-06: drop cancels, corrections, reversals + their matched originals.
-- Match originals on (cusip_id, entrd_vol_qt, rptd_pr, trd_exctn_dt,
-- trd_exctn_tm, rpt_side_cd, cntra_mp_id, msg_seq_nb).
WHERE trc_st = 'T'                              -- keep only clean originals
  AND NOT (cmsn_trd = 'Y' AND cntra_mp_id = 'D') -- drop agency double count
  AND spcl_trd_fl != 'Y'                         -- drop special-condition trades
  AND wis_fl != 'Y'                              -- drop when-issued
  -- For price/yield work, also:
  AND cmsn_trd = 'N'
```
Pre-2012-02-06 data uses `asof_cd = 'R'` for reversals instead of `trc_st = 'Y'`;
use the pre-2012 branch. See `references/trace.md`.

## Parameterized Queries

Always use parameterized queries (never string formatting):

Use scalar parameter binding for single values:
```python
cursor.execute("""
    SELECT gvkey, conm FROM comp.company WHERE gvkey = %s
""", (gvkey,))
```

Use ANY() for list parameters:
```python
cursor.execute("""
    SELECT * FROM comp.funda WHERE gvkey = ANY(%s)
""", (gvkey_list,))
```

## Additional Resources

### Reference Files

Detailed query patterns and table documentation:

- **`references/compustat.md`** - Compustat tables, ExecuComp, financial variables
- **`references/crsp.md`** - CRSP stock data, CCM linking, v2 format
- **`references/insider-form4.md`** - Thomson Reuters Form 4, rolecodes, insider types
- **`references/iss-compensation.md`** - ISS Incentive Lab, peer companies, compensation
- **`references/edgar.md`** - SEC EDGAR filings, URL construction, DCN vs accession numbers
- **`references/trace.md`** - TRACE bond transactions, Dick-Nielsen cleaning, FISD merge, pre-/post-2012 logic
- **`references/taq.md`** - TAQ/TAQMSEC intraday trades, quotes, complete NBBO, Holden-Jacobsen filters, WRDS Intraday Indicators
- **`references/connection.md`** - Connection pooling, caching, error handling

### Example Files

Working code from real projects:

- **`examples/form4_disposals.py`** - Insider trading analysis (from SVB project)
- **`examples/wrds_connector.py`** - Connection pooling pattern

### Scripts

- **`scripts/test_connection.py`** - Validate WRDS connectivity

### Local Sample Notebooks

WRDS-provided samples at `~/resources/wrds-code-samples/`:
- `ResearchApps/CCM2025.ipynb` - Modern CRSP-Compustat merge
- `ResearchApps/ff3_crspCIZ.ipynb` - Fama-French factor construction
- `comp/sas/execcomp_ceo_screen.sas` - ExecuComp patterns

## Date Awareness

When querying historical data, leverage current date context for dynamic range calculations.

Current date is automatically available via `datetime.now()`. Apply this to:
- Data range validation (e.g., "get data for last 5 years")
- Fiscal year calculations
- Event study windows

Implement dynamic date ranges in queries:
```python
from datetime import datetime, timedelta

# Query last 5 years of data
end_date = datetime.now()
start_date = end_date - timedelta(days=5*365)

query = """
SELECT * FROM comp.funda
WHERE datadate BETWEEN %s AND %s
"""
df = pd.read_sql(query, conn, params=(start_date, end_date))
```

Always incorporate current date awareness in date-dependent queries to ensure results remain fresh across time.
