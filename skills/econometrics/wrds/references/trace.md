# TRACE Corporate Bond Transaction Data

FINRA TRACE (Trade Reporting and Compliance Engine) reports OTC secondary-market
transactions in corporate, agency, and securitized debt. WRDS ships multiple
vintages — pick the right one or results will be wrong.

## Contents

- [Libraries: Which One to Use](#libraries-which-one-to-use)
- [Key Tables](#key-tables)
- [Key Fields (trace_enhanced.trace_enhanced)](#key-fields-trace_enhancedtrace_enhanced)
- [Dick-Nielsen (2014) Cleaning Procedure](#dick-nielsen-2014-cleaning-procedure)
- [Agency Double Counting](#agency-double-counting)
- [Commissioned Trades](#commissioned-trades)
- [Price and Volume Sanity Checks](#price-and-volume-sanity-checks)
- [Merging with FISD Bond Characteristics](#merging-with-fisd-bond-characteristics)
- [Common Gotchas](#common-gotchas)

## Libraries: Which One to Use

| Library | Contents | When to Use |
|---------|----------|-------------|
| `trace_enhanced` | Historic Enhanced TRACE (**uncapped volumes**, dealer identities masked but consistent, 18-month lag) | **Academic research default** — needed for volume analysis, dealer networks, liquidity measures |
| `trace_standard` | Regulatory/real-time TRACE (**volume capped** at $5MM IG / $1MM HY, dissemination-grade) | Only when you need recent data inside the 18-month embargo, or match what retail bond screens show |
| `trace` | Legacy alias — prefer the explicit schemas above | Avoid in new code |
| `*_old` | Frozen prior vintages | Reproducibility / replication only |

Standard tables (`trace_standard.trace_*`) carry dissemination-grade fields (high/low/last prices, `chng_cd`, `function`, halt metadata) that do not exist in `trace_enhanced`. Enhanced tables carry the fields needed for Dick-Nielsen cleaning (`msg_seq_nb`, `orig_msg_seq_nb`, `trc_st`, `asof_cd`).

## Key Tables

Within `trace_enhanced`:

| Table | Contents |
|-------|----------|
| `trace_enhanced` | Corporate bond transactions (the main BTDS table) |
| `trace_btds144a_enhanced` | Rule 144A corporate trades |
| `trace_agency_enhanced` | Agency debentures |
| `trace_spds_mbs_enhanced` | Agency MBS specified pool |
| `trace_spds_tba_enhanced` | Agency MBS TBA |
| `trace_spds_abs_enhanced` | ABS |
| `trace_spds_cmo_enhanced` | CMO |
| `trace_spds144a_abs_enhanced`, `trace_spds144a_cmo_enhanced` | 144A ABS / CMO |
| `absmasterfile`, `cmomasterfile`, `mbsmasterfile`, `tbamasterfile`, `camasterfile` | Security master files for the corresponding SPDS streams |

## Key Fields (trace_enhanced.trace_enhanced)

### Identifiers
- `cusip_id` — 9-digit CUSIP (matches FISD `complete_cusip` / `issue_cusip`)
- `bond_sym_id` — FINRA symbol
- `company_symbol` — issuer ticker-style symbol

### Trade timestamps
- `trd_exctn_dt`, `trd_exctn_tm` — execution date / time (**use these**)
- `trd_rpt_dt`, `trd_rpt_tm` — reporting date / time (used in reversal matching)
- `stlmnt_dt` — settlement date
- `pr_trd_dt` — prior-trade date

### Economics
- `rptd_pr` — reported clean price (percent of par)
- `yld_pt`, `yld_sign_cd` — reported yield (sign code `+`/`-` applied separately)
- `entrd_vol_qt` — par volume, **uncapped** in enhanced (capped in standard)
- `rpt_side_cd` — reported side: `B` buy, `S` sell, `D` interdealer

### Cleaning flags (critical — do not ignore)
- `trc_st` — trade status: `T` original, `X` same-day cancel of T, `R` same-day correction of T, `C` cancel of a non-same-day trade, `W` correction of a non-same-day trade, `Y` reversal
- `msg_seq_nb` — message sequence number (key for cancel/correct matching)
- `orig_msg_seq_nb` — points back to the cancelled/corrected original
- `asof_cd` — `A` as-of (delayed report), `R` reversal (pre-2012 encoding), `X` special
- `cmsn_trd` — commission trade flag (`Y`/`N`)
- `cntra_mp_id` — contra market participant: `C` customer, `D` dealer (the agency double-count signal on interdealer trades)
- `spcl_trd_fl` — special trade flag (non-standard pricing — exclude for liquidity work)
- `wis_fl` — when-issued flag
- `agu_qsr_id` — give-up or QSR indicator
- `ats_indicator` — ATS (alternative trading system) flag

### Post-2012 structural break
FINRA restructured TRACE dissemination on **2012-02-06**. Before that date, corrections/cancellations beyond the same day used `asof_cd = 'R'` encoding; after it, anything past T+0 uses `trc_st IN ('C','W','Y')` with explicit `orig_msg_seq_nb` pointers, and reversals now have a **T-21 day** window. Pre- and post-2012 cleaning code paths are not interchangeable.

## Dick-Nielsen (2014) Cleaning Procedure

The canonical academic filter. Skip it and you will overstate volume and double-count trades. Reference: Dick-Nielsen (2014), "How to Clean Enhanced TRACE Data," SSRN 2337908.

### Post-2012-02-06 logic (majority of modern samples)

**Step 1 — drop same-day cancels and corrections**
```sql
-- Remove the cancelled/corrected originals + the X/W records themselves.
-- Match on (cusip_id, entrd_vol_qt, rptd_pr, trd_exctn_dt, trd_exctn_tm,
--          rpt_side_cd, cntra_mp_id, msg_seq_nb)
DELETE FROM trades
WHERE trc_st IN ('X', 'C');   -- X = same-day cancel, C = later cancel
-- Also delete the corresponding originals matched by the 8-field key above.
```

**Step 2 — drop reversals**
```sql
-- trc_st = 'Y' flags a reversal; remove both the reversal and the
-- matched original (same 8-field key). Reversal window is T-21 days.
DELETE FROM trades WHERE trc_st = 'Y';
```

**Step 3 — drop corrections `W`** by matching `orig_msg_seq_nb` back to the
original, removing both, and keeping the corrected replacement.

Recursive matching is required: a `W` can correct a record that was itself a
correction, chaining up to ~7 levels. A single non-recursive pass
under-removes.

### Pre-2012-02-06 logic

- Cancellations/corrections: `trc_st IN ('C', 'W')` matched recursively via `msg_seq_nb ↔ orig_msg_seq_nb` (7 join levels).
- Reversals: `asof_cd = 'R'`, matched on `(trd_exctn_dt, cusip_id, trd_exctn_tm, rptd_pr, entrd_vol_qt, rpt_side_cd, cntra_mp_id)` with the constraint `reversal.trd_rpt_dt > original.trd_rpt_dt`.
- Delayed-dissemination reclassification: map `asof_cd = 'X' → 'R'` and `asof_cd = 'D' → 'A'` before matching.

## Agency Double Counting

When a dealer acts as agent between two customers, TRACE can report the trade
twice (once from each side). Drop the duplicate leg with:

```sql
-- Agency trades with a dealer contra: keep one leg only
AND NOT (cmsn_trd = 'Y' AND cntra_mp_id = 'D')
```

Some workflows additionally drop interdealer trades (`rpt_side_cd` of the
dealer-report side) when aggregating customer flow — document the choice.

## Commissioned Trades

For yield/price studies, commissioned trades distort the reported price
(commission is folded in). Remove with:

```sql
AND cmsn_trd = 'N'
```

Keep them in when studying **total investor cost** or dealer revenue.

## Price and Volume Sanity Checks

Even after Dick-Nielsen cleaning, filter obvious errors:

```python
df = df[
    (df.rptd_pr.between(1, 500)) &      # price in % of par, reasonable band
    (df.entrd_vol_qt >= 10_000) &       # drop odd lots if studying institutional flow
    (df.entrd_vol_qt < 1e10) &          # guard against reporting typos
    (df.yld_pt.between(-5, 100) | df.yld_pt.isna())
]
```

Palleja (2023) documents additional error-filter heuristics (median-absolute-deviation price jumps, reversed-sign yields) that catch records Dick-Nielsen misses.

## Merging with FISD Bond Characteristics

TRACE carries no coupon, maturity, rating, or issuer identity — merge FISD on
`cusip_id`:

```sql
SELECT t.cusip_id,
       t.trd_exctn_dt,
       t.rptd_pr,
       t.yld_pt,
       t.entrd_vol_qt,
       i.offering_date,
       i.maturity,
       i.coupon,
       i.offering_amt,
       i.bond_type,
       i.rating_cat,       -- if using fisd_mergedissue
       isr.issuer_id,
       isr.cusip_name AS issuer_name,
       isr.industry_group,
       isr.country_domicile
FROM trace_enhanced.trace_enhanced t
INNER JOIN fisd.fisd_mergedissue i
    ON t.cusip_id = i.complete_cusip
INNER JOIN fisd.fisd_mergedissuer isr
    ON i.issuer_id = isr.issuer_id
WHERE t.trd_exctn_dt BETWEEN %s AND %s
  AND t.trc_st = 'T'                 -- keep only originals (after cleaning)
  AND t.cmsn_trd = 'N'
  AND NOT (t.cmsn_trd = 'Y' AND t.cntra_mp_id = 'D')
  AND i.bond_type IN ('CDEB','CMTN','CMTZ','CDEBZ')   -- plain corporate
  AND i.security_level = 'SEN'                        -- senior only, optional
```

Standard bond-universe filters applied to `fisd_mergedissue`:

- Exclude convertibles: `convertible = 'N'`
- Exclude callable/putable optionality (for term-structure work): `putable = 'N' AND redeemable = 'N'`
- Exclude private placements: `private_placement = 'N'`
- Exclude asset-backed: `asset_backed = 'N'`
- Exclude 144A (if using public-only): `rule_144a = 'N'`
- USD denomination: `foreign_currency = 'N'` and `currency = 'USD'`
- Sensible issue size: `offering_amt >= 10_000` (amounts are in thousands)
- Maturity bounds: `maturity BETWEEN offering_date + interval '1 year' AND offering_date + interval '100 years'`

## Common Gotchas

1. **Enhanced vs standard mix-up** — volumes in `trace_standard` are capped
   (\$5MM IG, \$1MM HY). If mean volume looks suspiciously round, you are
   probably in the standard table.
2. **Ignoring the 2012 break** — applying post-2012 cleaning to pre-2012 data
   leaves reversals (`asof_cd='R'`) in the sample.
3. **Non-recursive cancel/correct matching** — `W` correcting a `W` is common;
   a single join pass leaves phantom originals.
4. **Dropping `trc_st` filter after cleaning** — always retain
   `trc_st = 'T'` (or whatever the cleaned-original label is) downstream; new
   analysts commonly re-pull raw data and forget.
5. **Timestamp timezone** — `trd_exctn_tm` is America/New_York wall clock
   without tz info; don't `AT TIME ZONE 'UTC'` blindly.
6. **Price is percent of par** — a `rptd_pr` of 102.5 means \$1,025 per \$1,000
   face, not dollars. Par-dollar volume = `entrd_vol_qt * rptd_pr / 100`.
7. **Settlement-date fields drift** — use `trd_exctn_dt` for event studies,
   not `stlmnt_dt` or `trd_rpt_dt`.
8. **`wis_fl = 'Y'`** — when-issued trades execute before settlement of the new
   issue; exclude for secondary-market liquidity studies.
9. **`spcl_trd_fl`** — special trades (non-standard pricing) should typically
   be excluded for price/yield analysis.
10. **FISD `complete_cusip` vs `issue_cusip`** — both exist; `complete_cusip`
    is the 9-digit canonical form used to join to TRACE `cusip_id`.

## References

- Dick-Nielsen, J. (2014). *How to Clean Enhanced TRACE Data*. SSRN 2337908.
- Dick-Nielsen, J. (2009). *Liquidity biases in TRACE*. Journal of Fixed Income.
- Palleja, M. (2023). *Error Filter for the TRACE Database*.
- FINRA (2023). *Web API Specifications for the TRACE Corporate and Agency Debt File Downloads*, v4.12a.
- WRDS FINRA vendor page: `https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/finra/`
- Reference R ports: `github.com/hannes101/FilterTRACE` (pre-2012 and post-2012 scripts).
