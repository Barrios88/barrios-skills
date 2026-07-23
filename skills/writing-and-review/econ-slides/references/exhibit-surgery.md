> **Barrios Skills** — John Barrios's curated workflow for economists and accountants. Prioritize reproducible empirical work, clear identification language, and journal-ready output.

# Exhibit surgery: tables, figures, and numbers

The most economics-specific work this skill does. A paper exhibit is built
for a referee with unlimited time; a slide exhibit is built for a listener
with eight seconds. Never paste one as the other.

## Where numbers live (level semantics)

- **Inference details (standard errors, t-stats, stars, clustering) live
  inside the inferential exhibit or its note/context** — whether that exhibit
  is a table, coefficient plot, or event study. Keep them off the punchline
  slide, the Implication line, and unrelated prose bullets. The
  punchline carries warranted direction + magnitude ("productivity is 3.4%
  higher after rollout" when the design is descriptive);
  the inferential exhibit defends it.
- Pure-theory results often trade in signs, orderings, and conditions rather
  than invented magnitudes. Quantitative theory and structural papers may need
  calibrated magnitudes, welfare changes, or counterfactual scale; keep those
  tied to the model inputs and source output.
- A figure title carries the warranted claim when it can do so cleanly. The
  interpretation line below the exhibit adds scale, intuition, or the decisive
  limitation rather than mechanically repeating a point estimate.

## Number provenance (governs everything below)

- Every number shown comes from the user's materials, tagged at draft time:
  `0.034 (0.008)  % Table 2, col (3), p.24`.
- Never re-round beyond dropping digits (0.0342 → 0.034 is fine; 0.034 →
  "about 0.05" is fabrication). Never average, rescale, or convert units
  without showing the conversion on the slide or in the note.
- Derived magnitudes ("one SD ⇒ 0.7%") show their arithmetic in the slide
  note or takeaway, with inputs traceable to the paper.
- Missing number → `\TODO{<what is needed>}` in red, surfaced to the user.
  A `\TODO` in a delivered deck must be called out in the summary.
- **Self-contradicting source**: when a conflicted number is displayed, give
  it a visible dagger and both source locations. Use a value only when the
  underlying table or data establishes it; otherwise leave the number
  unresolved. A substantive conflict (for example, prose says no pre-trend
  while the figure shows one) changes the headline and identification status;
  a secondary conflict belongs in a linked backup and the handoff. Never
  silently pick, vote by majority of mentions, or average. See
  `source-integrity.md`.

## Regression table → slide table

Procedure, in order:

1. **Choose the story.** Identify the load-bearing estimate and retain only the
   comparison columns needed to interpret or defend it. Everything else goes
   to a full appendix table.
2. **Keep rows**: the coefficient(s) of interest with SEs. **Collapse
   rows**: controls, fixed effects, and diagnostics become `Controls — No /
   Yes / Yes` indicator lines. **Drop rows**: constants, nuisance
   covariates nobody will ask about.
3. **Column headers say what changes**: `(1) OLS`, `(2) +Controls`,
   `(3) +Region trends` — the identification story reads left to right.
4. **Make the load-bearing comparison easy to locate.** Neutral bold is the
   default. If that estimate belongs to a recurring colored concept, use the
   concept alias already taught by the deck; do not automatically color an
   entire column or introduce a new accent for one table.
5. **Keep the table visually quiet.** Highlight the load-bearing estimate,
   then let one short `\Takeaway` below the table state the economic meaning,
   intuition, or decisive limitation. It must add interpretation rather than
   repeat a coefficient range already visible in the table. Do not add a
   colored full-width interpretation row unless it is part of a deliberate
   build and earns the extra emphasis.
6. **Translate the magnitude when the source supports the scale** via
   `\Takeaway{}`: use one SD, an interquartile range, or the policy's actual
   dose only when that input is traceable. Otherwise give the direct
   plain-language reading; never manufacture a rescaling to make the line
   sound more intuitive. "Significant" is not a magnitude.
7. Typeset: `booktabs` (never vertical rules), right-aligned numbers,
   2–3 significant digits, `threeparttable` with the clustering and stars
   convention in `tablenotes`. Keep it at its natural size when it fits. Only
   an oversized table should be reduced with a command such as
   `\resizebox{0.8\textwidth}{!}{...}`; never use that command to enlarge a
   small table merely to hit a width target. Font floor: if fitting drops below
   `\scriptsize` legibility, the table is too wide — cut columns.
8. **Separate note from reading.** Keep the clustering, units, and star note
   visually tight to the table. Then leave a distinct bounded gap before the
   normal-body interpretation. The note documents the exhibit; the reading
   tells the audience why it matters. In the bundled themes,
   `\Takeaway{}` owns this configurable `\ExhibitReadingGap`. After the final
   render shows surplus room, use the local roomy form
   `\Takeaway[\ExhibitReadingGapRoomy]{...}` or
   `\TakeawayWithNav[\ExhibitReadingGapRoomy]{...}`. Keep the ordinary default
   on tighter frames; never enlarge the global gap to fix one sparse slide.

Pattern — **every value below is illustrative fiction. Copying any number
from this snippet into a real deck is fabrication**; replace all of them
from the user's paper and keep the provenance comments:

```latex
\colorlet{cTreatment}{cAccentA} % declare once with the deck's concept map
\resizebox{0.72\textwidth}{!}{% use only when the natural table is wider
\begin{threeparttable}
  \begin{tabular}{lccc}
    \toprule
    & (1) OLS & (2) +Controls & \textcolor{cTreatment}{(3) +Trends} \\ \midrule
    Broadband $\times$ Post & 0.041*** & 0.036*** & \textcolor{cTreatment}{\textbf{0.034***}} \\
     & (0.009) & (0.008) & \textcolor{cTreatment}{(0.008)} \\ \midrule
    Controls & No & Yes & Yes \\
    Observations & 148,220 & 148,220 & 148,220 \\
    \bottomrule
  \end{tabular}
  \begin{tablenotes}\footnotesize
    \item SEs clustered by municipality. *** $p<0.01$.
  \end{tablenotes}
\end{threeparttable}}
\Takeaway{One SD of exposure moves productivity by 0.7 percent.}
```

- **"Data | Model" tables** (structural/theory-empirics): two value columns
  compared moment by moment; reveal the model column on a second overlay
  step after the data column is absorbed.
- Never place `\toprule` directly under a colored frame title bar — this
  bites under the boxed theme and any compat theme with a title bar
  (Madrid, CambridgeUS): insert `\vspace{4pt}` between title and table.
  The compiler will not warn you and the checker cannot see it — it is a
  visual-pass item.

## Figures

Choose the least intervention that communicates the result clearly:

1. **Use the source figure or crop it.** If the paper already has the
   load-bearing exhibit and it remains legible at slide size, reuse it. Crop
   surrounding captions, margins, or neighboring panels when that is all the
   screen adaptation requires. A crop of one source panel is still source
   reuse, not a new or rebuilt figure. Record the page, figure, and panel; keep
   every axis, legend or colorbar, baseline marker, and source note needed to
   read that panel honestly.
2. **Use a native table, equation, or concise text.** When no source figure
   exists, a surgically reduced table, one annotated equation, or a clear
   single-column explanation is preferable to inventing a demonstration
   graphic.
3. **Rebuild an existing exhibit only when necessary.** Rebuild when the
   source exhibit is central but illegible or visually overloaded, and only
   when source data or figure code are available. Rebuilding from a PDF alone
   means eyeballing coefficients off a plot and violates number provenance.
4. **Create a new figure only as a last resort.** It must convey a relation
   that the source figure/crop, native table, equation, and concise text cannot
   communicate as clearly. Empty space, visual variety, or a geometric fill
   warning is never sufficient reason.

For every new figure, record beside the slide plan:

- **Rationale:** why each less invasive option above fails;
- **Inputs:** exact source locations and any transformation or arithmetic;
- **Status:** `new figure — individual QA required` until the checks below are
  complete.

- Never quote an exact coefficient by reading pixels from a cropped figure.
  Without data or a source table, describe only the visible shape and
  uncertainty.
- When an existing exhibit genuinely must be rebuilt, use figure fonts at
  slide scale, direct labels or a compact internal legend, and line colors
  consistent with the slide's concept map. Keep rebuilt and new assets in a
  `figures-slides/` directory separate from the paper's figures.
- When the paper PDF is the only available source artifact, crop tightly with
  `scripts/crop_figure.py` (`--list` finds candidate regions, `--bbox`
  crops at 300 DPI) and include at `width=0.9\textwidth, keepaspectratio`;
  if its internal text is illegible at that size, it does not go on the
  slide.
- An included paper figure keeps its own colors, so the slide↔figure color
  contract cannot hold for it. Do not fight it: if the figure's palette is
  close to a theme accent, adopt that accent for the concept in the text;
  otherwise drop concept-coloring for that concept rather than color the
  word one hue and the line another.
- One figure per frame, centered; panels labeled `A.`/`B.` only if both
  panels are discussed. Wide figures: `\makebox[\textwidth][c]{...}`.
- Around a figure, crop internal whitespace first, use a bounded half-line to
  one-line title-to-exhibit gap, and let one important figure use most of the
  available central width and height while preserving labels. Center the
  exhibit when that matches the local style, and place one normal-body reading
  directly below a load-bearing static figure when it adds insight. In a new
  bundled-theme deck, `\Takeaway{}` provides that treatment. The line explains
  economic scale, intuition, or the one fact governing interpretation; it does
  not restate the title or an axis label. A genuine semantic build may instead
  use one short synchronized reading per build. Do not show both layers.
- Give a figure slide a concise message or economic-object title and the
  minimum context needed to read the exhibit—often sample, units, and interval
  convention in `\framesubtitle`, or the target deck's established equivalent.
- **`\Takeaway` and `\PlaceNav` share the bottom of the frame** — a long
  centered takeaway runs under the bottom-right pills. When a frame has nav,
  use `\TakeawayWithNav{...}`, which reserves that lane. The checker flags
  button-text collisions, but eyeball it. Its optional first argument changes
  only the exhibit-to-reading gap; it does not change the reserved nav lane.
- Prefer the paper's existing main-result figure when it communicates the
  finding well. Do not manufacture a coefficient plot from a table solely to
  satisfy a figures-over-tables preference; a small native slide table may be
  the more faithful exhibit, with the full table in the appendix.

A useful starting composition for a new bundled-theme figure frame is:

```latex
\framesubtitle{[Sample, outcome, units, and interval convention]}
\medskip
\centering
\includegraphics[
  width=.92\linewidth,
  height=.60\textheight,
  keepaspectratio
]{figure.pdf}
\Takeaway{[Economic insight or intuition, not an axis description.]}
```

These dimensions are not a quota. A long title, an inherited aspect ratio, or
a dense legend changes the available height, so inspect the rendered frame and
enlarge the source exhibit only while its labels and reading remain balanced.

## Event-study / coefficient plots (the workhorse)

- Reference line at zero, treatment date marked, CIs shaded or as bars,
  pre-period visually distinguishable. Normalized coefficient (t = −1)
  shown, not silently dropped.
- Axis label carries the unit ("log points × 100" ≠ "percent" — say which).
  Caption/axis unit mismatches are a classic referee catch; check both
  against the paper's numbers.
- Overlay build (optional, if it aids reasoning): pre-period first, then
  post — the audience judges parallel trends before seeing the effect.

## TikZ and diagrams

- Timelines, DAGs, and model schematics are useful only when relational
  structure is the point and a source exhibit or concise verbal explanation
  cannot do the job. They are not default decorations for data, assignment,
  or robustness slides. When a new diagram is necessary, the new-figure
  rationale and QA requirements above apply. Construction rules:
  - Any point that must sit on a plotted curve is **computed**
    (`\pgfmathsetmacro` from the same function), never eyeballed — an
    eyeballed point drifts on every edit and renders without warning.
  - Explicit `minimum width/height` or `text width` on boxed nodes; bare
    `scale=` is banned (it scales coordinates but not labels) — use
    `transform shape` or scale node styles too.
  - Labels keep ≥ 0.3–0.4 cm clearance from curves, shapes, and each
    other; when a curved arrow and a label compete, compute the arc's
    depth before placing (adapted from Scott Cunningham's MixtapeTools
    measurement rules, with thanks).
- After any TikZ edit, re-render and *look*: label collisions produce zero
  compiler warnings.

## Individual QA for every new, rebuilt, or cropped figure

Do not approve a new, rebuilt, or cropped figure from a contact sheet alone.
A source-panel crop is reuse for provenance but an adapted asset for visual
QA. Inspect the asset itself and every slide that contains it:

1. Cross-check every plotted value, derived value, unit, sample definition,
   event date, normalization, and uncertainty interval against the cited
   source.
2. Open the standalone asset at its native resolution. Check clipped labels,
   overlapping annotations, legend order, line/marker distinction, and font
   size.
3. Open the rendered slide at presentation size. Check that axes and labels
   remain readable, the figure receives the intended emphasis, and its colors
   do not conflict with the deck's concept map.
4. Repeat the embedded-slide check for every overlay state and every slide
   that reuses the asset.
5. Mark the plan entry `QA complete` only after recording the inspected asset
   and slide page(s). If any value or label cannot be verified, do not use the
   figure.

## The visual pass (why the renders exist)

`check_deck.py --render-dir` writes every page as PNG. Inspect each for the
failures no static check sees: content overflowing a `ResultBox` or block
(Beamer suppresses those warnings), `\toprule`-under-title-bar merges, TikZ
label overlap, figure text too small, a slide that is simply ugly. This
deck-wide sweep supplements rather than replaces the individual figure QA
above. One sweep, page by page, before delivery — non-negotiable.
