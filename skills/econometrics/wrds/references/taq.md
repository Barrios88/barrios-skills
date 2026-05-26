# TAQ — Trade and Quote (NYSE Daily/Monthly TAQ)

Tick-level US equity trades, quotes, and NBBO. WRDS hosts two vintages and
multiple partitioning schemes — picking the wrong one is the most common
TAQ mistake.

## Contents

- [Library Layout](#library-layout)
- [Tables in `taqm_YYYY` (Daily TAQ MSEC)](#tables-in-taqm_yyyy-daily-taq-msec)
- [Key Fields](#key-fields)
- [Regular Trading Hours](#regular-trading-hours)
- [Trade Cleaning Filters](#trade-cleaning-filters)
- [Quote Cleaning Filters](#quote-cleaning-filters)
- [NBBO — Why `nbbom` Is Incomplete](#nbbo--why-nbbom-is-incomplete)
- [Linking TAQ to CRSP](#linking-taq-to-crsp)
- [WRDS Intraday Indicators (pre-computed liquidity)](#wrds-intraday-indicators-pre-computed-liquidity)
- [Query Patterns](#query-patterns)
- [Performance Notes](#performance-notes)
- [Common Gotchas](#common-gotchas)

## Library Layout

| Library | Coverage | Resolution | Notes |
|---------|----------|------------|-------|
| `taq` | 1993-01-01 → 2014-12-31 | **second** | Monthly TAQ (old format); one table per month of trades/quotes. Legacy — use only for deep history |
| `taqmsec` | 2003-09-10 → mid-2015 | millisecond | Daily TAQ MSEC (flat schema, single library) |
| `taqm_YYYY` | 2003-09-10 → present | ms (≤2015-06), **µs (microsecond) from mid-2015** | Daily TAQ MSEC partitioned by year. **Default for modern work.** |
| `taqm_YYYY_old` | frozen vintages | — | Prior reloads — reproducibility only |
| `wrdsapps_link_crsp_taqm` | — | — | Links TAQ `sym_root/sym_suffix` ↔ CRSP `permno` |
| `contrib_liquidity_taq` | — | — | Contributed liquidity-measure datasets |

**Timestamp resolution cutover:** through ~2015-06, `time_m_nano` is
millisecond-resolution scaled to nanos; from mid-2015 onward, microsecond.
Do not compare raw tick counts across this boundary.

## Tables in `taqm_YYYY` (Daily TAQ MSEC)

Each year library holds ~253 tables per type, one per trading day, plus one
year-level aggregate and one yearly master. The day partition lets you skip
scanning a full-year monolith.

| Table pattern | Contents |
|---------------|----------|
| `ctm_YYYY` / `ctm_YYYYMMDD` | **Consolidated trades** (all exchanges) |
| `cqm_YYYY` / `cqm_YYYYMMDD` | **Consolidated quotes** (all exchanges, all quotes) |
| `nbbom_YYYY` / `nbbom_YYYYMMDD` | NBBO message file — **incomplete** (see below) |
| `complete_nbbo_YYYY` / `complete_nbbo_YYYYMMDD` | **Official Complete NBBO** — WRDS-constructed, combining `nbbom` with `cqm` records where a single exchange held both sides. **Use this for NBBO work.** |
| `luld_ctm_YYYYMMDD`, `luld_cqm_YYYYMMDD` | Limit-up / limit-down bands |
| `wct_YYYYMMDD` | Weighted consolidated trades |
| `mastm_YYYY` | Security master (one row per symbol-date: CUSIP, SIC, tape, listed exchange, shares outstanding, round lot) |
| `wrds_iid_YYYY` | **WRDS Intraday Indicators** — pre-computed daily liquidity measures (quoted / effective / realized spreads, depth, Amihud, Roll). Huge time saver. |

## Key Fields

### Trades — `ctm_*`
| Field | Meaning |
|-------|---------|
| `date`, `time_m`, `time_m_nano` | Execution timestamp. Concat `time_m + time_m_nano` for sub-ms ordering |
| `sym_root`, `sym_suffix` | Symbol (e.g. `BRK` + `A`). Join key. Suffix is often NULL/empty |
| `ex` | Exchange reporting the trade (`N`=NYSE, `Q`=NASDAQ, `P`=NYSE Arca, `A`=NYSE American, `T`=NASDAQ BX, `Z`=BATS, `D`=FINRA ADF, etc.) |
| `price` | Trade price |
| `size` | Share volume |
| `tr_scond` | **Sale condition** (up to 4 chars) — see filter section |
| `tr_corr` | **Correction code**: `'00'` = uncorrected original, anything else = later-corrected or canceled |
| `tr_stop_ind` | Stopped stock indicator |
| `tr_seqnum` | Sequence number (for tie-breaking) |
| `tr_rf` | Regulatory flag |
| `tr_source` | `C` = CTA/UTP, `N` = NASDAQ |
| `tte_ind` | Trade-through-exempt indicator |
| `part_time`, `trf_time` | Participant / TRF (FINRA) report times |

### Quotes — `cqm_*`
| Field | Meaning |
|-------|---------|
| `date`, `time_m`, `time_m_nano` | Quote timestamp |
| `sym_root`, `sym_suffix` | Symbol |
| `ex` | Exchange posting the quote |
| `bid`, `bidsiz`, `ask`, `asksiz` | Bid / ask and sizes (shares, not round lots) |
| `qu_cond` | Quote condition (`R`=regular, `A`=slow on ask, `B`=slow on bid, `H`=slow on both, `O`=opening, `C`=closing, `L`=closed, `X`=inactive, etc.) |
| `qu_source` | `C` or `N` (tape) |
| `natbbo_ind` | Exchange asserts it is at the national best — critical for Holden-Jacobsen NBBO reconstruction |
| `nasdbbo_ind` | NASDAQ BBO indicator (`4` = same idea for UTP tape) |
| `qu_cancel` | Quote cancellation flag |
| `qu_seqnum` | Sequence number |

### Complete NBBO — `complete_nbbo_*`
| Field | Meaning |
|-------|---------|
| `date`, `time_m`, `time_m_nano` | Timestamp |
| `sym_root`, `sym_suffix` | Symbol |
| `best_bid`, `best_bidsizeshares` | National best bid and total size |
| `best_ask`, `best_asksizeshares` | National best offer and total size |
| `qu_cond`, `nbbo_qu_cond` | Quote conditions |
| `natbbo_ind` | NBBO indicator |

### Master — `mastm_YYYY`
One row per symbol-date with `cusip`, `sec_type`, `listed_exchange`, `tape`
(`A`=NYSE, `B`=NYSE American/Arca, `C`=NASDAQ), `round_lot`,
`shares_outstanding`, `tick_pilot_indicator`, venue-by-venue listing flags
(`tron_nyse`, `tron_nasdaq`, etc.).

## Regular Trading Hours

US equities regular session: **09:30:00 – 16:00:00 America/New_York**.
Times in TAQ are wall-clock Eastern with no tz info.

```sql
WHERE time_m BETWEEN '09:30:00'::time AND '16:00:00'::time
```

For studies that need the opening or closing cross, include a small buffer
(e.g. 09:30:00.000–16:00:00.000 inclusive both ends, or 15:59:59.999 if
excluding the cross). Holden-Jacobsen (2014) uses the 09:30–16:00 regular
session.

## Trade Cleaning Filters

### Minimum standard (Holden-Jacobsen 2014)

```sql
WHERE tr_corr = '00'                          -- original, uncorrected
  AND price > 0
  AND size > 0
  AND time_m BETWEEN '09:30:00'::time AND '16:00:00'::time
  AND (tr_scond IS NULL OR tr_scond = ''      -- regular-way trades
       OR tr_scond NOT SIMILAR TO '%[BGJKLOTUWZ467]%')
```

### Sale-condition code reference (`tr_scond`)

Up to 4 chars — keep trades whose codes imply **regular way** execution,
drop trades flagged as opening/closing prints, irregular, out-of-sequence,
or non-last-sale-eligible.

| Code | Meaning | Keep? |
|------|---------|-------|
| (blank), `@`, `*`, `E`, `F` | Regular way / intermarket sweep / split / filled-at-single-price | Keep |
| `B` | Average price | Drop |
| `G` | Bunched sold | Drop (price-distorted) |
| `J` | Rule 127 (NYSE) | Drop |
| `K` | Rule 155 (AMEX) | Drop |
| `L` | Sold last | Drop |
| `O` | Opening price | Drop (unless studying open) |
| `T` | Extended-hours | Drop |
| `U` | Extended-hours sold out-of-sequence | Drop |
| `W` | Average price trade | Drop |
| `Z` | Sold (out of sequence) | Drop |
| `4`, `5`, `6`, `7` | Derivatively priced / reopening / closing print / placeholder | Drop unless studying auctions |

Older SAS code bases often filter by a subset and tolerate blanks — the
critical exclusions are `Z`, `O`, `T`, `U`, `G`, `B`.

### `tr_corr` correction codes

- `'00'` — original trade, not corrected. **Only keep these.**
- `'01'` - `'08'` — prior trade was canceled, corrected, or adjusted. Drop.
- `'11'`, `'12'` — late-correction markers. Drop.

## Quote Cleaning Filters

```sql
WHERE bid > 0 AND ask > 0
  AND ask > bid                                -- no crossed/locked quotes
  AND (ask - bid) / ((ask + bid) / 2) < 0.25   -- drop clearly erroneous spreads
  AND bidsiz > 0 AND asksiz > 0
  AND qu_cond IN ('A','B','H','O','R','W')     -- include active-session conditions
  AND time_m BETWEEN '09:30:00'::time AND '16:00:00'::time
```

The exact `qu_cond` set varies by study. The defensible academic default is
to keep `R` (regular) and accept slow-side variants (`A`, `B`, `H`);
strictly exclude `X` (inactive) and `L` (closed).

## NBBO — Why `nbbom` Is Incomplete

The raw NBBO message feed (`nbbom_*`) reports the NBBO **only when
different exchanges hold the best bid vs the best offer**. When **one
exchange has both sides at the top of book simultaneously**, the tape does
not issue an NBBO record — the fact is flagged in that exchange's ordinary
quote record (`cqm_*`) by `natbbo_ind = '1'` (CTA tape) or
`nasdbbo_ind = '4'` (UTP tape).

Two options:

1. **Use `complete_nbbo_*`** — WRDS has already merged `nbbom_*` with the
   qualifying `cqm_*` records for you. **This is the right default.**
2. **Re-derive it** (Holden-Jacobsen 2014 method):

```sql
-- Combine incomplete NBBO (nbbom) with same-exchange-both-sides quotes (cqm).
SELECT date, time_m, time_m_nano, sym_root, sym_suffix,
       best_bid, best_ask, best_bidsizeshares AS bidsize, best_asksizeshares AS asksize
FROM   taqm_2024.nbbom_20240315
UNION ALL
SELECT date, time_m, time_m_nano, sym_root, sym_suffix,
       bid AS best_bid, ask AS best_ask, bidsiz AS bidsize, asksiz AS asksize
FROM   taqm_2024.cqm_20240315
WHERE  natbbo_ind = '1' OR nasdbbo_ind = '4';
```

Reference: Holden & Jacobsen (2014), "Liquidity Measurement Problems in
Fast, Competitive Markets," *Journal of Finance*.

## Linking TAQ to CRSP

TAQ has no `permno`. Use `wrdsapps_link_crsp_taqm`:

```sql
SELECT c.permno, l.sym_root, l.sym_suffix, l.sdate, l.edate
FROM   wrdsapps_link_crsp_taqm l
JOIN   crsp.stocknames_v2 c
  ON   c.permno = l.permno
WHERE  c.permno = %s
  AND  %s BETWEEN l.sdate AND l.edate;
```

Link validity is date-banded by `sdate`/`edate` — honor the bounds or you
will attach the wrong PERMNO after a ticker change.

## WRDS Intraday Indicators (pre-computed liquidity)

`taqm_YYYY.wrds_iid_YYYY` is **one row per symbol-day** with pre-computed
Holden-Jacobsen-style liquidity measures: quoted spread, effective spread,
realized spread, price impact, depth (simple / dollar-weighted /
share-weighted), Amihud illiquidity, and more.

**Prefer `wrds_iid` over running Holden-Jacobsen yourself** unless you
specifically need a non-default filter or window. The precomputed table
saves hours-to-days of WRDS Cloud SAS runtime.

## Query Patterns

### Single-stock, single-day trade pull (clean, RTH only)

```sql
SELECT date, time_m, time_m_nano, ex, price, size, tr_scond, tr_corr
FROM   taqm_2024.ctm_20240315
WHERE  sym_root = %s
  AND  tr_corr = '00'
  AND  price > 0
  AND  size > 0
  AND  time_m BETWEEN '09:30:00'::time AND '16:00:00'::time
  AND  (tr_scond IS NULL OR tr_scond = '' OR tr_scond = '@')
ORDER BY time_m, time_m_nano;
```

### Stock-day pull across a month (use year-partition)

Either loop over daily tables, or query the annual rollup with an extra
date predicate (the planner partition-prunes if you use the per-day
partitions directly):

```sql
-- Per-day loop is simpler and faster on WRDS:
for day in trading_days(start, end):
    table = f"taqm_{day.year}.ctm_{day:%Y%m%d}"
    cur.execute(f"SELECT ... FROM {table} WHERE sym_root = %s AND ...", (sym,))
```

### NBBO snapshot at a point in time

For each trade, attach the **prior** NBBO (Lee-Ready / Holden-Jacobsen
convention uses the NBBO in effect when the trade was reported, not
contemporaneous):

```sql
WITH trades AS (
    SELECT date, time_m, time_m_nano, sym_root, price, size
    FROM   taqm_2024.ctm_20240315
    WHERE  sym_root = %s AND tr_corr = '00'
),
nbbo AS (
    SELECT date, time_m, time_m_nano, sym_root, best_bid, best_ask
    FROM   taqm_2024.complete_nbbo_20240315
    WHERE  sym_root = %s
)
SELECT DISTINCT ON (t.time_m, t.time_m_nano)
       t.*, n.best_bid, n.best_ask
FROM   trades t
LEFT JOIN LATERAL (
    SELECT best_bid, best_ask
    FROM   nbbo n
    WHERE  n.sym_root = t.sym_root
      AND  (n.time_m, n.time_m_nano) <= (t.time_m, t.time_m_nano)
    ORDER BY n.time_m DESC, n.time_m_nano DESC
    LIMIT 1
) n ON TRUE;
```

Holden-Jacobsen recommend using the NBBO lagged by 1 second for pre-2015
data, but contemporaneous (same-message-sequence) for post-2015 data — the
tape latency dropped substantially with the 2015 microsecond migration.

## Performance Notes

- TAQ day-tables are massive (often >100M trades/day SPY alone); never
  `SELECT *` — specify columns and `sym_root` predicate.
- Partition pruning works only when the table name is literal — do not
  wrap `taqm_YYYY.ctm_YYYYMMDD` in a dynamic view.
- Sort by `(time_m, time_m_nano)` explicitly; insertion order is not
  guaranteed.
- For month+ pulls, issue one query per day and stream to parquet rather
  than building a single DataFrame.
- The WRDS Cloud SAS grid has large scratch but finite — Holden-Jacobsen's
  own instructions recommend breaking a year into quarters or months if
  running their full liquidity pipeline.

## Common Gotchas

1. **`nbbom` vs `complete_nbbo`** — the raw NBBO feed misses the one-exchange-both-sides case. Always prefer `complete_nbbo` or reconstruct with the `natbbo_ind='1' OR nasdbbo_ind='4'` merge.
2. **Sub-second ordering** — sort by `(time_m, time_m_nano, tr_seqnum)`, not just `time_m`. Multiple trades share the same ms/µs.
3. **Timestamp resolution break (mid-2015)** — `time_m_nano` went from ms×1000000 to µs×1000. Don't treat the column as monotonic across the break.
4. **`tr_corr = '00'` is a string, not integer** — `tr_corr = 0` silently matches nothing in some clients.
5. **Wall-clock, no tz** — never apply `AT TIME ZONE 'UTC'` blindly; this is Eastern.
6. **Exchange scope** — `ex = 'D'` (FINRA ADF / TRF) aggregates OTC prints, not a single venue. Don't treat FINRA trades as if they were a single exchange's order flow.
7. **Symbol suffix** — `sym_suffix` holds share-class indicators (e.g. `BRK`.`A`). Join on both `sym_root` and `sym_suffix` (or `COALESCE(sym_suffix, '')`) to avoid cross-class contamination.
8. **Short sessions** — half-days (day before Thanksgiving, July 3rd, etc.) close at 13:00:00. Your 09:30–16:00 filter silently returns zero afternoon trades those days.
9. **Reuse `wrds_iid`** — if you need standard spreads/depth, don't recompute. The precomputed table encodes Holden-Jacobsen cleaning and runs in seconds.
10. **CRSP link date bands** — `wrdsapps_link_crsp_taqm` honors `sdate`/`edate`; missing the filter attaches post-change PERMNOs to pre-change tickers.

## References

- Holden, C. W., & Jacobsen, S. (2014). *Liquidity Measurement Problems in Fast, Competitive Markets*. Journal of Finance, 69(4), 1747–1785.
- Holden-Jacobsen WRDS Cloud SAS code: `https://kelley.iu.edu/cholden/` — "Daily TAQ and Monthly TAQ Code" zip.
- WRDS NYSE TAQ page: `https://wrds-www.wharton.upenn.edu/pages/grid-items/taq-introduction/`
- WRDS Intraday Indicators docs: search "WRDS_DTAQ_IID_Manual" on the WRDS site.
- Lee, C. M. C., & Ready, M. J. (1991). *Inferring Trade Direction from Intraday Data*. Journal of Finance.
- Ellis, Michaely & O'Hara (2000); Chakrabarty, Li, Nguyen & Van Ness (2006) — alternative trade-classification conventions used in Holden-Jacobsen.
