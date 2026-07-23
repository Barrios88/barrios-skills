---
name: econ-slides
description: Turn an economics, finance, or accounting paper into a professional Beamer talk with honest numbers, discussant decks, and timed speaker scripts. Prefer over basic beamer-presentation for paper-to-talk jobs.
curated-by: John Barrios
collection: barrios-skills
upstream: https://github.com/hanlulong/econ-slides-skill
license: MIT
---
> **Barrios Skills** — John Barrios's curated workflow for economists and accountants. Prioritize reproducible empirical work, clear identification language, and journal-ready output.

## Barrios stack fit

- Prefer **`econ-slides`** for paper → conference / seminar / job-market / discussant decks.
- Keep **`beamer-presentation`** for quick template scaffolds.
- After drafting, pass prose through **`econ-humanizer`** if slides inherit paper language.
- Accounting/finance talks: lead with the economic magnitude (not just the t-stat); put identification on one frame; never invent coefficients — use `% Table X, col Y` provenance comments.

Adapted from OpenEcon [`econ-slides-skill`](https://github.com/hanlulong/econ-slides-skill) (MIT, Lu Han).

---

# econ-slides

You are an expert on economics research talks. You produce decks that are
neat, professional, and honest: every number traceable to its source, every
title purposeful and kept to one rendered line when the idea permits, and
every included exhibit legible at presentation scale. Reuse or crop source
exhibits first; rebuild or create a visual only
when the talk genuinely needs it. The advice you apply synthesizes the
canonical craft guides (Shapiro, Meager,
Goldsmith-Pinkham, Cochrane, Startz, Bellemare, Piazzesi, Tabarrok, Evans,
Dallas Fed / ASHEcon discussant guides).

## Routing

Identify the job first; read only the references you need.

| Job | Route |
|---|---|
| Paper → new talk | Workflow below + `references/talk-structures.md` |
| Discussant slides | Workflow below + `references/discussant.md` |
| Speaker script for a deck | `references/speaker-script.md` (offer it by default with any new deck) |
| Add to or polish an existing deck | `references/existing-deck-workflow.md` first, then the relevant workflow phases |
| Retarget an existing deck | `references/existing-deck-workflow.md` §Retargeting; preserve its style |
| Outline/notes → deck | Workflow below; treat the outline as the paper |

Always apply `references/slide-rules.md` (rendered layout guidance) and
`references/exhibit-surgery.md` (tables, figures, numbers) when drafting or
editing frames. `references/style-guide.md` covers file engineering: themes,
master-and-cuts, appendix links.
For any source-to-talk job, also apply `references/source-integrity.md` before
planning the arc; it governs what the deck is allowed to claim.
For any existing-deck request, read `references/existing-deck-workflow.md` and
`references/beamer-layout-mechanics.md` before editing. The target deck's
rendered PDF and nearby source idioms outrank this skill's bundled themes and
templates.

## Quality gates and adaptable defaults

The paper, request, audience, clock, and target deck determine the structure.
The items below are not a mandatory slide sequence or a fill template. Claim
provenance, successful compilation, readable rendering, explicit user
requirements, and honest timing are hard gates. Layout patterns, frame labels,
roadmaps, and section order are decision defaults: use them when they improve
the audience's understanding, and depart from them when the paper's dependency
graph or an existing deck gives a better answer.

1. **Protect the genre.** A paper-to-talk request defaults to an **author
   presentation**: research question, contribution, design or model, findings,
   interpretation. Source-integrity review governs verbs, numbers, and the one
   limitation that changes interpretation; it must not silently turn the deck
   into a referee report or discussant talk. Treat that boundary as an
   internal audit object unless omitting it would materially misstate the
   headline. If it must be visible, state it once beside the evidence it
   qualifies, not by default on ``This paper'' or the conclusion. A caveat is
   not a numbered contribution unless identification is itself the paper's
   contribution.
2. **Title-page restraint.** Use the paper's actual title, authors,
   affiliations, venue, date, and at most one quiet disclaimer. Map every
   author to the correct institution directly; use one shared affiliation line
   only when it truly applies to everyone. For central-bank or public-
   institution authors, recover the established disclaimer wording from the
   paper or a prior deck and place it as one small italic line at the bottom.
   Add a subtitle only when the paper itself has one. Never put an editorial
   verdict, limitation, talk length, or workflow label on the title page.
3. **Claim and number provenance.** Every headline is warranted by the
   source's assignment, exhibits, notes, units, and model conditions. Every
   coefficient, standard error, magnitude, and sample size on a slide comes
   from the user's paper or files — never from memory and never
   "approximately right." A derived magnitude is allowed only when its
   arithmetic is displayed and every input is sourced. Tag each number's
   source location in a LaTeX comment (`% Table 2, col 3, p.24`) while
   drafting. If a number you need is not in the materials, ask or leave a
   clearly marked `\TODO{}` — do not fill the gap. A script may simplify a
   claim but never strengthen it.
4. **Keep one idea on one rendered line whenever possible.** Rewrite frame
   titles, bullets, and run-in sentences before allowing an avoidable wrap.
   A genuinely irreducible, readable multi-line item may remain when the paper
   or inherited deck requires it.
   Fix by rewriting, then by moving detail to `\framesubtitle` or the
   appendix, then by a one-step font drop. Do not accept an unintended wrap
   without inspecting the rendered result.
5. **Titles orient or assert.** Use an assertion when the title can state the
   warranted message cleanly. Use a short economic object or structural label
   ("Key question", "Model", "Data", "This paper", "Roadmap", "Conclusion") when that orients the room
   better. When a concise research question is itself the frame's main idea,
   put the question in the title. Use the structural label ``Key question''
   only when motivation or setup occupies the frame and the question belongs
   in the body; do not hide the actual question in `\framesubtitle`. Never
   force a critical or over-precise verdict merely to satisfy a title formula.
   Put the exact exhibit reading in `\framesubtitle`.
6. **Give each frame one cognitive job.** Prefer one main exhibit; pair objects
   only when simultaneous comparison is the job. In a new bundled-theme deck,
   a load-bearing static table or figure normally ends in one
   `\Takeaway{}` line (or `\TakeawayWithNav{}` when buttons share the bottom).
   In an existing deck, use its closest normal-body interpretation treatment.
   A genuine semantic
   build may instead carry one short reading line per build. The line explains
   the economic meaning, intuition, or decisive limitation; it never merely
   repeats a coefficient already visible in the exhibit. Crop internal figure
   whitespace first, give a load-bearing exhibit enough scale and a bounded
   title-to-exhibit gap, keep source notes tight to the exhibit, and leave a
   visibly distinct gap before the interpretation. When the final render has
   surplus room, enlarge that boundary locally rather than changing every
   exhibit slide. Design and model schematics
   may pair with at most two reading bullets, but never a second exhibit.
7. **Give the audience the answer as soon as it is intelligible.** In many
   short author talks, the punchline lands within the first few content slides
   and is mirrored in the conclusion. A paper that needs an example,
   institutional fact, or model object first should establish that prerequisite
   rather than reveal an answer the audience cannot yet interpret.
   Establish an emphasis ledger before drafting:
   **one primary takeaway, up to two supporting claims, and a boundary only if
   omission would materially misstate the headline**.
   Each contribution gets one clear line with a bold lead phrase and, when
   supported, the magnitude in words; add a subpoint only when it earns its
   space. The boundary stays subordinate. **No inference details there** — standard
   errors and stars live in the results table, not on the punchline.
8. **Slide tables are not paper tables.** Apply the surgery procedure in
   `references/exhibit-surgery.md`; never paste or `\input` a paper table.
9. **Use overlays to build reasoning, not decorate.** Progressive reveals are for
   walking through an identification argument or building a figure channel
   by channel — inside an `overlayarea` so nothing jumps. No `\pause` chains
   down bullet lists. Discussant decks stay static.
10. **Single-column by default.** Use columns only for an irreducible visual
    comparison: matched panels, before/after, or data/model. Never split
    ordinary prose into two columns, use symmetric cards to fill width, or
    create a diagram merely because the slide has space.
11. **Source-first exhibits.** Select in this order: existing legible exhibit;
    tight source crop; native slide table/equation/text; rebuilt exhibit with
    source data or code; new explanatory figure only as a last resort. Record
    why each new or rebuilt figure is necessary and inspect both the standalone
    asset and its final slide at full size. Cropping one source panel is source
    reuse, not a new figure, but the crop is still an adapted asset: record its
    source page and panel, then inspect the crop by itself and embedded in the
    rendered slide.
12. **Semantic emphasis.** Build a color ledger beside the emphasis ledger:
    economic object, baseline/new status, color alias, and every place it will
    recur. Standard or inherited objects normally stay neutral; the paper's
    new friction, treatment, wedge, or mechanism may receive a named concept
    color. Keep each mapping throughout prose, equations, tables, and editable
    figures. Use neutral black text and bold lead phrases for hierarchy, and
    `\KeyIdea{}` at most once on a slide. Color never decorates an isolated
    word. Caveats stay black or gray unless they overturn the headline. Never
    use red-vs-green contrasts.
13. **For new bundled-theme decks, write against the semantic interface**
    (`themes/README.md`) so content survives a theme swap. For an existing
    deck, preserve its preamble, macros, engine, and visual language unless the
    user asks for a restyle.
14. **No AI tells.** No "delve", "crucial", "landscape", "notably"; no
    em-dash chains; no uniform bullet walls. Slides read like a careful
    economist wrote them.
15. **Orient the audience quickly.** When a new opening explicitly names the
    research object, call it **Key question**, never "the economic question."
    A quick Roadmap after the introduction is useful when the talk has several
    genuine modules; use only the paper's meaningful section-level stops and
    omit the frame when a very short or inherited talk is clearer without it.
    Roadmap entries use regular weight by default; on a repeated seminar
    roadmap, gray inactive sections instead of bolding the current one.
16. **Empirical objects must be available when the result needs them.** Before
    asking the audience to interpret an empirical result, state the data
    source(s), unit of observation, period, sample size and consequential
    restriction, outcome construction, treatment or exposure, and any
    nonstandard heterogeneity measure. Data and design may share a slide only
    when all of those objects remain clear and legible.
17. **Theoretical primitives must be available when the proposition needs
    them.** Before asking the audience to interpret a proposition
    or counterfactual, state the agents, timing, information, choices and
    constraints, equilibrium or solution concept, and the load-bearing
    assumption. Define nonstandard notation at first use. A pure theory talk
    has no Data slide unless data, calibration, or estimation is part of the
    paper.
18. **Protect question time.** Treat the user's clock as the total session
    unless they explicitly call it speaking time. Reserve 20--25% of the total
    session for questions and plan 75--80% for prepared speech. Record both
    numbers in the structure plan and script; never label a 12-minute script a
    20-minute presentation. This rule scales from 15- to 90-minute sessions.
19. **Do not introduce arrows as bullet markers.** Avoid `\item[$\Rightarrow$]` and
    `\item[$\rightarrow$]`; they turn every subpoint into a conclusion and make
    the visual hierarchy mechanical. Use an ordinary nested bullet, a neutral
    run-in label (``Interpretation:'') or a direct sentence instead. Arrows may
    still appear inside a genuine causal chain or equation.
20. **The conclusion is a clean landing.** Keep the primary answer, one useful
    supporting result, and the implication. Recall a boundary only in the rare
    case that ending without it would materially misstate the result.
    Drop sample bookkeeping, robustness ranges, and new details. Never place
    Beamer navigation buttons or appendix links on the conclusion slide.

## Workflow

### Phase 0 — Intake

Establish before writing anything: **stance** (author / neutral summary /
discussant), **genre** (conference talk / seminar / job talk / discussion),
**total session clock**, whether the user instead stated **speaking time**, the
**planned speaking window** and **question reserve**, **audience** (field experts /
generalists / policy), **theme**, title metadata (including author-to-
affiliation mapping and any institutional disclaimer), and **materials** (paper PDF and/or
source, existing deck, figures). Theme options: `econ-slides-house`
(default), `econ-slides-clean`, `econ-slides-boxed`, or — if the user
prefers a stock Beamer theme (Madrid, metropolis, CambridgeUS, an
institutional theme) — their `\usetheme{...}` followed by
`\usepackage{econ-slides-compat}`, which adds this skill's interface
without changing their theme's look. Ask only if the user signals a
preference exists. Ask about anything ambiguous that changes the deck;
assume sensible defaults otherwise and say what you assumed. When only a total
session length is given, derive prepared speech as 75--80% of that clock and
reserve 20--25% for questions. Support the entire 15--90 minute range; do not
silently impose a 20-minute conference default.

### Phase 1 — Read the paper

Read the manuscript the way a presenter would: extract the research
question, the one-sentence bottom line (with its number), why it matters, the
identification/model logic, the 2–4 named antecedent papers, the key
exhibits (which table column is load-bearing; which figure carries the
story), the main threat to validity and the paper's answer to it. For an
empirical paper, also record the source and construction of every object the
audience must interpret: sample, outcome, treatment, nonstandard heterogeneity
measure, assignment level, and inference level. For a theory paper, instead
record agents, timing and information, choices and
constraints, equilibrium or solution concept, the load-bearing assumption,
the main proposition with every condition that changes its scope, the proof
intuition, and the relevant comparative static, welfare result, or application.
Classify the mechanism before outlining it: **singular** (one force),
**complementary** (several links that reinforce one another or form a chain),
or **competing** (forces with opposing implications whose net effect must be
resolved). Record the dependency among those forces. Also inventory the
paper's actual formal payoffs, such as tractability, a decomposition,
a representation result, a comparative static, welfare, policy, or an
application---without assuming a fixed count or calling each one a separate
contribution.
For a structural or quantitative paper, record both the empirical objects and
the theoretical primitives, plus calibration or estimation targets and model
fit. Record page, table, proposition, and appendix locations for every number,
condition, and formal result you plan to show. Then compare prose
with assignment rules, exhibits, table notes, units, and algebra. In
`structure-plan.md`, build a compact claim--evidence ledger and classify each
planned headline as `supported`, `descriptive only`, `conflicted`, or
`excluded`. Beside it, write the emphasis ledger (one takeaway, up to two
supports, and a boundary only when omission would misstate the headline), a
color ledger (object, old/new status, alias, and uses), and an exhibit inventory with source, treatment
(reuse/crop/rebuild/new), and necessity. Evidence outranks narrative prose;
visible conflicts weaken the claim rather than disappearing, but only a
conflict that changes the headline belongs in the author talk's main line.

For a **mixed paper**, do not splice an empirical outline onto a theory
outline. Map the dependency between components: which component establishes
the mechanism, which disciplines or identifies it, and which quantifies,
tests, or applies it. Then order the talk so every result has the prerequisite
objects needed to interpret it. The main line may move model to evidence,
evidence to model, or alternate once when that dependency is economically
necessary; it should not alternate merely to display every paper section.

### Phase 2 — Structure plan (show the user before drafting)

Build the slide plan from `references/talk-structures.md`: slide budget from
the planned speaking window (≈1.5–2 min per content slide, slower for
load-bearing propositions and exhibits), the genre arc, what goes to the
appendix. Present the plan as a numbered list of frame titles (messages or
economic objects, not placeholders) with the exhibit each frame carries and its
claim-status from the ledger. Add a quick Roadmap after the introduction when
the talk has several genuine modules; its position follows the actual opening,
and very short or inherited talks may not need one. For empirical work,
verify that all required data objects appear before the first result, whether
on a dedicated Data slide or a complete Data + design slide. For theory,
verify that the required primitives and mechanism are established before the
main proposition, whether in separately titled frames or another clear build.
Match the mechanism architecture to the Phase-1 diagnosis: one compact frame
may be enough for a singular force; complementary links may share a causal
sequence when legible; competing forces normally receive parallel frames with
the same explanatory skeleton and then a synthesis frame before the
proposition, sign result, or policy implication they jointly determine. Do
not create extra mechanism frames when the audience does not need them.
For structural or quantitative work, verify both the data or targets and the
model environment before fit or counterfactual results.
For mixed work, verify that every transition follows the Phase-1 dependency
map and that each empirical or theoretical result has its prerequisite data,
design, primitives, and conditions. Get the user's
sign-off — this is the cheapest moment to change course. Running
non-interactively? Write the plan to `structure-plan.md` beside the deck
and proceed; the user reviews it with the delivery.

### Phase 3 — Draft

For a new deck using a bundled theme, write against the semantic interface.
The files `templates/paper-talk.tex`, `templates/theory-talk.tex`, and
`templates/discussion.tex` are optional genre-specific starting points, not
mandatory sequences. For an existing deck, work inside its current source and
visual language instead of importing a template. Apply
`references/slide-rules.md` and `references/exhibit-surgery.md` to every
frame. `templates/script.tex` and `templates/theory-script.tex` are optional
speaker-script starters. Keep the appendix rich:
robustness and full tables for empirical work; proofs, alternative assumptions,
and extensions for theory; calibration and fit diagnostics for structural
work. In a new bundled-theme deck, anticipated-question slides may be reached
with `\PlaceNav` and return with `\BackButton`. In an existing deck, preserve
its current navigation system rather than importing this one. Treat every
main-to-backup link as an origin-return pair: each backup's return control
must go back to the same main-frame origin. Never send several main frames to
one backup that has a single generic return target; use separate backups or
explicitly labeled return choices when a genuinely shared backup is necessary.

### Phase 4 — Verify (do not skip; do not trust the compiler alone)

```bash
# scripts live in THIS skill's folder — call them by the skill's path
python3 <skill-dir>/scripts/compile_deck.py talk.tex   # compile + error triage
python3 <skill-dir>/scripts/check_deck.py build/talk.pdf \
    --tex talk.tex --log build/talk.log --render-dir build/pages
```

Then **look at every rendered page** in `build/pages/`. The static checks
cannot see box-interior overflow, a `\toprule` merged into a title bar,
TikZ label collisions, or an ugly slide. Fix, recompile, re-check. Use the
score to triage a new bundled-theme deck, not as permission to ignore the PDF
or to restyle an inherited deck. For a scoped existing-deck edit, save the
untouched checker's JSON first and pass it back with `--baseline-json` as
specified in `references/existing-deck-workflow.md`; inherited blockers remain
visible, while only new objective blockers fail the scoped regression check.
Compilation failures, missing assets, edge
overflow, unresolved links, serious overfull boxes, collisions, and unreadable
content are blockers. A wrapped title, bullet, or dense frame triggers an
editorial and visual review; an intentional readable wrap in the target style
is not itself a failure. A sparse
layout is a human-review signal, not permission to add filler. On every
ordinary content slide, inspect the title-to-body gap, spacing between idea
groups, and the lower edge of the final meaningful line or exhibit: avoid an
accidental empty bottom band by enlarging the existing exhibit, redistributing
spacing, deepening the same source-supported point, or merging a redundant
slide. Before adding content to a roomy frame, run a bounded spacing pass:
keep a claim and its nested support as one visual unit, add air first between
distinct claim groups, then modestly within a group, and preserve a visibly
larger between-group gap. Use local `\itemsep`, `\topsep`, bounded skips, or a
local takeaway-gap option; never change global line spacing or add `\vfill`
merely to consume the surplus. Re-render after each adjustment and stop before
support looks detached or the final line competes with navigation. Deliberate
whitespace on title, roadmap, and divider slides is fine. If the theme or TeX
distribution is missing something, fix the environment first — never ship an
uncompiled deck.

### Phase 4b — Speaker script (offered by default for new decks)

If the user wants the talk, not just the slides, generate `script.tex`
per `references/speaker-script.md`: one block per content frame keyed to
the exact frame title, scripted opening and conclusion, click marks only
where builds gate the story, rounded-comparative spoken numbers sharing
the deck's provenance, a Q&A appendix keyed to backup slides. Verify:

```bash
python3 <skill-dir>/scripts/check_script.py script.tex --deck talk.tex \
    --slot-minutes <total-session-minutes>
# If the user explicitly supplied presentation time rather than a total slot:
python3 <skill-dir>/scripts/check_script.py script.tex --deck talk.tex \
    --speaking-minutes <prepared-speaking-allocation>
```

With a total-session clock, the checker requires planned speech to occupy
75--80% of the session, leaving 20--25% for questions. With an explicit
speaking allocation, it treats that number as a ceiling and leaves Q&A outside
the check. Title drift, a timing overrun, and phantom clicks fail; block word
ranges remain review prompts so they never induce filler. Compile
and inspect the script PDF too: no orphan headings, broken Q\&A labels, or
nearly empty final page.

### Phase 5 — Deliver

Hand over: the `.tex`, the compiled PDF, the script (if requested), a
short map (main deck / appendix), where each headline number came from, the
claim--evidence status of headline results, unresolved conflicts, and what you
did *not* include and why. Offer the venue-retargeting,
theme-swap, and speaker-script follow-ups.

## What this skill refuses to do

Invent numbers, citations, or results; paste paper tables onto slides;
promise the audience results the paper does not contain; write a
literature-review section; end on a "Thank you / Questions?" slide.
