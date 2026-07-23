> **Barrios Skills** — John Barrios's curated workflow for economists and accountants. Prioritize reproducible empirical work, clear identification language, and journal-ready output.

# Editing an existing Beamer deck without changing its visual language

Use this workflow when the user asks to add slides, add backup material, add a
discussion, polish selected frames, or adapt an existing deck to another
venue. The existing deck is the design specification. Do not load a bundled
`econ-slides-*` theme, replace the preamble, or impose a standard talk arc
unless the user explicitly asks for a restyle.

The procedures below are not slide outlines. The paper, the request, the
audience, and the existing deck determine what belongs in the talk and where.

## Contents

1. Establish the baseline
2. Reverse-engineer the deck's style
3. Decide what needs clarification
4. Make a minimal, coherent change
5. Procedures for common requests
6. Compile, render, and inspect

## 1. Establish the baseline

Before editing source:

1. Identify the authoritative root `.tex` file, local `\input`/`\include`
   files, conditional venue cuts, notes or handout variants, generated versus
   hand-edited sources, figure and table pipelines, custom `.sty` files, fonts,
   and build engine. Respect a `% !TEX` directive, `latexmkrc`, bibliography,
   `minted`, externalization, or documented Overleaf workflow. Do not assume
   XeLaTeX merely because it is this skill's default.
2. Record the existing worktree state and keep build artifacts isolated. Run
   the untouched deck's native build to convergence. Record the page count,
   aspect ratio, warnings, unresolved references, and whether overlay builds
   create extra PDF pages. Classify defects already present in the baseline so
   they are not mistaken for regressions caused by the requested edit. When
   the helper checker is compatible with the project, save its JSON output
   beside the untouched build; Section 6 shows how to compare the edited deck
   against it without excusing new blockers.
3. Render the untouched PDF and inspect every page at presentation size. A
   stale PDF is not a baseline; compile the current source. If the source no
   longer compiles, preserve the last known PDF as visual evidence, isolate the
   environment or missing-asset problem, and avoid opportunistic preamble
   modernization.
4. Save a compact style fingerprint in the work notes: the conventions in the
   checklist below, plus two or three representative frames to use as local
   models. If no trustworthy baseline can be built or located, stop before
   making layout changes and ask whether to repair the build or proceed against
   the available PDF.

A single user's archive may contain several style families because of venue,
coauthor, institution, and time. Weight evidence in this order:

1. the target deck's rendered PDF;
2. repeated conventions in the target deck's active source;
3. a recent deck by the same user for a similar venue and genre;
4. older or collaborator-authored decks.

Do not average incompatible styles. A current 16:9 research deck with centered
titles and a 4:3 institutional deck with bold left-aligned titles are two
coherent systems, not ingredients to mix.

## 2. Reverse-engineer the deck's style

Record what the deck actually does; do not translate it into the bundled house
theme.

### Document and title page

- Document class options: base font size, aspect ratio, `handout`, color-table
  options, and any engine-specific packages.
- Theme, color theme, font theme, institutional package, page margins,
  headline, footline, and navigation-symbol settings.
- Whether the title frame is `plain`, `noframenumbering`, or manually
  de-counted; whether the title page has visible footer material.
- Title line breaks, alignment, color, weight, and size; the direct mapping
  from each author to institution; venue/date placement; and the treatment of
  a disclaimer. Record whether a central-bank or public-institution disclaimer
  is required and reuse the deck's established wording and placement.
- Whether the source provides a subtitle. Do not invent one to summarize or
  judge the paper.

### Typography, titles, and spacing

- Body and math fonts; frame-title and frame-subtitle alignment, color, weight,
  case, and size; ordinary body size; local font reductions; table-note size.
- Citation and bibliography style; theorem, block, proof, and equation-number
  conventions; notation macros; and any speaker-note architecture.
- Whether substantive titles usually assert a result or name an economic
  object, and which short labels the deck uses for structural frames. Match the
  local register. Keep new frame titles on one rendered line when the idea can
  be stated clearly that way.
- What `\framesubtitle` does in this deck. In many research decks it carries
  the precise exhibit reading, sample, units, or comparison while the title
  carries the claim; in others it is rarely used. Follow the target deck.
- Bullet glyphs, enumerate style, indentation, number of nesting levels, and
  the usual relationship between a claim and its explanation.
- Preserve the local bullet family, but do not introduce a right-arrow as a
  list marker. Use an ordinary nested bullet or a neutral run-in sentence; an
  arrow belongs in a genuine causal chain or equation.
- Vertical alignment (`[t]`, `[c]`, or Beamer's default), title-to-body gap,
  `\itemsep`, `\topsep`, and the deck's usual `\smallskip`, `\medskip`, or
  scoped `\vspace{...}` adjustments.
- Where the final meaningful line or exhibit normally lands. Distinguish
  deliberate white space from an accidental empty lower band.

### Color and emphasis

- Structure color, neutral text colors, and all custom color or emphasis
  macros.
- The meaning of each recurring accent, including whether neutral text denotes
  a standard/old object while an accent introduces the paper's new object.
  Preserve a concept-to-color mapping in text, equations, tables, and editable
  figures. Do not borrow a concept color for an unrelated label.
- The deck's emphasis vocabulary: bold lead phrases, colored terms, boxes,
  row/column highlights, underbraces, or overlay spotlights. Use the nearest
  existing treatment; do not add a new visual dialect for one frame.

### Layouts, exhibits, and overlays

- The dominant reading order. Note when the deck uses one column and when it
  uses `columns`, paired `minipage`s, or a figure-plus-text layout.
- Treat one column as the starting point. Use two columns only when the new
  material must be compared simultaneously: paired panels, data/model,
  before/after, treated/control, or two genuinely parallel mechanisms. Reuse a
  local comparison pattern when one exists; otherwise construct the smallest
  pattern compatible with the deck and verify it closely.
- Figure width/height conventions, `keepaspectratio`, `trim`/`clip`, centering,
  panel labels, legends, and whether slide-specific versions of exhibits exist.
- Table conventions: `booktabs`, font size, `\arraystretch`, column selection,
  notes, coefficient or column highlighting, and whether tables are rebuilt for
  slides rather than imported whole.
- What follows an exhibit. Separate a source note or caption from an
  interpretation. A newly added interpretation line uses the deck's ordinary
  body font, sits in a stable relationship directly below the exhibit, and
  states the insight, intuition, economic scale, interpretation, or decisive
  limit. It is not a small floating footnote or a restatement of a visible
  cell.
- Overlay commands, reserved geometry (`overlayarea`, fixed minipages, or
  figure swaps), and handout behavior. Preserve the deck's reveal rhythm only
  when the new build advances the evidence or reasoning.
- Whether tables and figures are generated from code, and which file is
  authoritative. Never hand-edit a generated artifact that will be overwritten
  by the next build.

### Navigation and appendix

- Section and roadmap conventions, including whether roadmap frames recur and
  how completed/current sections are marked.
- Footer numbering: current/total, whether the title is counted, whether the
  appendix is excluded from the main total, and whether backups use `A1`,
  `A2`, and so on.
- Existing target/link syntax, placement and styling of buttons, and whether
  appendix frames carry Back buttons. Check absolute-positioning macros as
  rendered, not only in source.
- Overlay-specific destinations, duplicate-label behavior, and which build a
  link should open. Targets must be unique and usable in both presentation and
  handout modes when the project supports both.
- Appendix divider, ordering, titles, and use of `noframenumbering`. Do not call
  `\appendix` a second time inside an existing appendix.

Recurring professional conventions are useful clues, not defaults to impose:
restrained title metadata, hidden navigation symbols, generous horizontal
margins, one-line frame titles, large source exhibits, semantic color use,
bottom-right detail links, and separately numbered backup slides. The target
deck decides their exact implementation.

## 3. Decide what needs clarification

Ask only when the answer changes the content, file architecture, or genre.
Material questions include:

- Which source is canonical when several venue cuts exist, and whether the
  user wants the canonical file edited or a new sibling cut.
- Whether “discussion” means an author-led discussion/interpretation section
  or a discussant's independent assessment. The stance changes the voice and
  the evidence hierarchy.
- Which paper, result, or source supports the requested new topic when it is
  not identifiable from the supplied files.
- The target venue, audience, and clock for a retargeting request; whether a
  stated duration is total session time or speaking time.
- A genuinely ambiguous insertion point when different placements would make
  different arguments.

Do not ask the user to choose a theme when an existing deck makes the choice
clear. Do not ask about aspect ratio, fonts, footer style, bullet shape,
appendix numbering, or button placement when they can be inferred. When an
insertion point or layout has one strong local precedent, proceed and state the
assumption in the change plan.

## 4. Make a minimal, coherent change

Before writing, specify the delta:

- frames to add, revise, move, or remove;
- the evidence and message of each affected frame;
- the insertion point and why it helps the existing argument;
- the closest frame in the deck whose source structure will be reused;
- any roadmap, numbering, target, appendix, or script consequences;
- the expected change in prepared speaking time, when relevant.

Then follow the minimal-diff rule:

1. Reuse the target deck's packages, macros, list environments, color names,
   asset paths, and frame idioms. Copy the source skeleton of the closest
   local analogue, then replace its content; do not copy stale labels or
   claims.
2. Keep a local change local. Scope `\arraystretch`, font size, list spacing,
   and color changes inside the frame or exhibit. Change a shared macro only
   when every use should change, and inspect every use afterward.
3. Do not replace the preamble, add an `econ-slides-*` package, change the
   engine, normalize title case across untouched slides, or reformat unrelated
   frames merely because another style is preferable.
4. Preserve source-supported meaning and provenance. Check new or changed
   claims and numbers against the canonical paper, data output, or exhibit,
   and add source-location comments without changing the visible style. Flag a
   conflict instead of silently preserving an error or substituting a new
   result; obtain approval before making a substantive correction outside the
   requested scope. If the evidence is unavailable, ask or leave an explicit
   `\TODO{}` rather than filling the gap.
5. Prefer existing exhibits, tight crops, selective native tables, equations,
   and concise text. Create or rebuild a figure only when the argument needs
   it and the underlying source data or code are available. Record why it is
   necessary, then inspect the standalone asset and every composed frame that
   uses it.

When a concise new research question carries an opening frame, put it in the
title. Otherwise call the opening object **Key question**, not “economic
question,” and keep the question in the body rather than a subtitle. Do not rename an established
“Introduction” frame merely to satisfy that wording preference. Keep the
conclusion free of detail-navigation buttons; the final substantive answer
should remain on screen.

### Account for Beamer reflow

Read `references/beamer-layout-mechanics.md` before a structural edit. The
source is not a canvas: a changed word can wrap, add a full line, shrink
stretchable glue, move an exhibit, and collide with a footer or button.

- Use bounded spacing such as `\smallskip`, `\medskip`, a scoped
  `\vspace{...}`, or local `\itemsep` between ordinary idea groups.
- If the final render has surplus room, increase spacing by hierarchy: first
  between distinct claim groups, then by a smaller amount between each claim
  and its support. Preserve the deck's local idiom and keep nested support
  visibly attached; do not change global list defaults for one roomy frame.
- Use `\vfill` only for a deliberately anchored object whose position remains
  appropriate when nearby text gains or loses a line. Do not use it as a
  generic separator or to strand an exhibit reading at the bottom.
- Do not introduce a smaller font just to make a new line fit. Rewrite first,
  split genuinely distinct ideas second, and use a local font step only when
  that is already an established convention in the deck.
- Keep an exhibit interpretation at normal body size directly after the
  exhibit. Put navigation in a separate lower lane so neither object controls
  the other's spacing.
- Reserve stable geometry for overlays. The fullest build governs the frame's
  fit, but every intermediate build must also look intentional.

For each layout-affecting edit or small coherent batch, use this loop:

```text
source edit
  -> compile and read warnings
  -> render the affected frame and all overlay builds
  -> inspect the reflow in the PDF
  -> revise the source
```

## 5. Procedures for common requests

### Add slides on a requested topic

1. Read the relevant paper section, tables, figures, appendix, and nearby deck
   frames. Determine what the audience must learn from the addition and what
   evidence supports it.
2. Place the material where it answers a question already raised, supplies a
   prerequisite before a result, interprets existing evidence, or extends the
   argument. Do not create a new section merely because a new frame is being
   added.
3. Decide the number of frames from the reasoning. One object with one message
   may need one frame; a new empirical result may need data/measure context
   before the exhibit; a theoretical result may need primitives or intuition
   before a proposition. There is no fixed anatomy.
4. Reuse the nearest local frame type: text, equation, table, full-width
   figure, paired comparison, or semantic build. Match its title/subtitle,
   spacing, font, color, and exhibit treatment.
5. Update a roadmap only if the new material changes the talk's section-level
   contract. Do not add generic roadmap sublines that merely announce what
   will arrive.
6. Add or update source comments, labels, links, and any title-keyed script
   block. Compile and inspect after each layout-affecting edit or small
   coherent batch; do not let several unverified source changes accumulate.

### Add appendix material

1. Identify the anticipated question the backup slide answers and the main
   frame from which it is most naturally reached.
2. Insert the frame inside the existing appendix, using its title, numbering,
   font, and exhibit conventions. Preserve the existing appendix start and
   main-deck total.
3. If the deck already uses linked backups, create a distinct main target and
   appendix target, add the detail button in the existing navigation lane, and
   point the Back button to the main target. Never create a self-link. If the
   deck has no linked navigation, do not introduce a new button system for one
   backup unless the user asks.
4. Place the backup near related appendix material. Give it enough context to
   answer the question when reached out of order; do not assume the preceding
   appendix slide was seen.
5. Build to convergence and test every new link in the PDF. Check duplicate
   destinations, intended overlay targets, main totals, appendix labels, and
   the footer on overlay builds. Repeat in handout mode when the deck supports
   one.

### Add a discussion section

1. Establish the stance. An author discussion interprets, connects, or limits
   the paper's own findings; a discussant section evaluates another paper and
   proposes constructive next steps. Ask if the request leaves this genuinely
   unclear.
2. Preserve the deck's genre and visual system. Adding discussion frames to an
   author deck is not a reason to switch to a boxed discussant theme.
3. Build the section from the paper and the request, not a fixed count of
   comments. For a discussant, anchor each main comment to the paper's claim or
   design, explain why it matters for interpretation, and end with a concrete
   question, diagnostic, or feasible suggestion. Keep the tone generous and
   direct.
4. Use substantive titles rather than “Discussion 1” or “Comment 2” when the
   local title style permits. Reuse the deck's text, equation, or exhibit
   patterns. Keep the section static unless an existing semantic-build idiom
   materially improves the reasoning.
5. Add a roadmap stop only when the discussion is a real section of the talk.
   Keep minor points in the appendix or a compact final discussion frame.

### Polish selected frames

1. Render the selected frames and their neighbors before editing. Diagnose the
   problem as content hierarchy, wording, line wrapping, crowding, accidental
   empty space, exhibit scale, table legibility, color semantics, overlay
   movement, or navigation collision.
2. Preserve the frame's warranted message. Rewrite the title and body first;
   improve the crop or table selection second; tune bounded local spacing
   third. Shrinking the whole frame is a last resort, not a first move.
3. Keep the interpretation close to the exhibit and at normal body size. If
   it only repeats a coefficient, replace it with the economic meaning,
   intuition, scale, interpretation, or decisive limitation.
4. Compare before and after at the same scale. A polished frame should look as
   though it was always part of the deck, not as though it came from a new
   template.
5. If the fix touches a shared macro, theme setting, font, or footer, search
   for every use and render the full deck. Do not accept a local improvement
   that breaks another frame.

### Retarget the deck to a new length or venue

1. Establish venue, audience, total session clock, and whether the user instead
   stated speaking time. When only total session time is given, plan about
   75--80% for prepared speech and reserve 20--25% for questions. When the
   user explicitly gives speaking time, preserve that allocation directly and
   validate it with `check_script.py --speaking-minutes`; do not discount it a
   second time.
2. Work from the paper's emphasis hierarchy and the existing talk, not a fixed
   slide count. Load-bearing exhibits, identification arguments, mechanisms,
   and propositions take longer than orientation frames.
3. Make a `keep / compress / move to appendix / cut / deepen` ledger. Preserve
   the central takeaway and the information required to understand it. For an
   empirical paper, do not cut necessary data and design objects; for a theory
   paper, do not cut the primitives, mechanism, or conditions that make the
   result interpretable.
4. For a shorter cut, remove branches before compressing individual frames.
   Move useful detail to the appendix rather than shrinking fonts or packing
   unrelated objects together. Repair roadmaps, transitions, labels, and
   links after every cut.
5. For a longer talk, deepen source-supported motivation, institutional
   context, design logic, mechanism, exhibit reading, robustness, or economic
   interpretation. Do not add filler, demonstration figures, or generic
   literature slides to occupy time.
6. Prefer a new sibling venue file when the original remains useful. Reuse
   shared frame modules if the project already has that architecture; do not
   refactor a small one-off cut into a new system without need.
7. If a title-keyed speaker script exists, retarget it with the deck. Remove
   cut blocks, synchronize renamed frames and real clicks, and change timing
   only through useful spoken content.

## 6. Compile, render, and inspect

Use the deck's native build command and engine. The skill helpers are useful
when compatible:

```bash
python3 <skill-dir>/scripts/compile_deck.py path/to/talk.tex --engine <engine>
python3 <skill-dir>/scripts/check_deck.py path/to/build/talk.pdf \
  --tex path/to/talk.tex --log path/to/build/talk.log \
  --render-dir path/to/build/pages
```

For a scoped edit, preserve a machine-readable check of the freshly compiled,
untouched source before changing it:

```bash
python3 <skill-dir>/scripts/check_deck.py path/to/baseline/talk.pdf \
  --tex path/to/talk.tex --log path/to/baseline/talk.log --json \
  > path/to/baseline/check-deck.json || [ "$?" -eq 1 ]
```

Exit status 1 is expected when the untouched deck already has an objective
blocker; status 2 still stops the command. Open the JSON and confirm that its
page count and findings describe the actual untouched build. Do not reuse a
baseline from another venue cut, an older source state, or a stale PDF.

After the edit, compare the new build to that saved result:

```bash
python3 <skill-dir>/scripts/check_deck.py path/to/edited/talk.pdf \
  --tex path/to/talk.tex --log path/to/edited/talk.log \
  --baseline-json path/to/baseline/check-deck.json --json
```

The comparison matches objective blockers by semantic context and occurrence
count, not page number, so inserting or deleting an earlier frame does not
turn an unchanged defect into a regression. In baseline mode, `blockers` and
the exit status reflect only `new_blockers`; `all_blockers` still lists every
current blocker, while `inherited_blockers` and `resolved_blockers` make the
comparison auditable. An additional identical occurrence is new. The ordinary
`score` continues to describe the edited deck as a whole; `regression_score`
removes only matched inherited objective blockers.

This mode is a scope-control aid, not a waiver of visual QA. It cannot prove
that an old-looking defect is physically the same object after a wholesale
rewrite, and it cannot see an ugly crop, reflow inside a box, misleading
emphasis, or a content regression. Use it only with a trustworthy adjacent
baseline, review all prompts, compare the affected frames before and after,
and still inspect every final page.

Static findings are diagnostics, not permission to restyle the deck to obtain
a score. Compilation errors, missing assets, newly introduced unresolved
references or broken links, edge overflow, collisions, unreadable text, and
unintended reflow are objective blockers. A newly wrapped title or bullet
deserves an editorial pass, but an intentional, readable multi-line item may
be part of the deck's established style. Do not expand the task into unrelated
cleanup of inherited defects without authorization. Density, columns, and
whitespace still require judgment against the paper, the request, and the
target deck's established language.

After each layout-affecting change or coherent local batch:

- inspect the affected frame, every overlay build, and the adjacent frames;
- check title and subtitle line breaks, title-to-body gap, bullet indentation
  and spacing, exhibit size and crop, table readability, and the last
  meaningful line;
- verify that the exhibit reading is useful, set in normal body text, and
  visually attached to the exhibit;
- verify that navigation occupies a separate lane and does not collide with
  the reading or footer;
- test targets, Back buttons, frame totals, appendix numbering, and handout
  output when relevant.

At the end, render and inspect every page of the modified deck. Any shared
macro, font, theme, margin, footer, or navigation change requires a full-deck
before/after pass. The compiled PDF is the artifact that must match the user's
visual language; clean source alone is not evidence of a successful edit.

Hand off a concise regression report: changed files and frames, baseline and
final page counts, introduced or resolved warnings, assumptions, unresolved
`\TODO`s, and inherited defects deliberately left untouched. Include the
location of every new or rebuilt exhibit and any source conflict requiring the
user's decision.
