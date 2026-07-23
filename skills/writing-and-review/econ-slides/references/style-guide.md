> **Barrios Skills** — John Barrios's curated workflow for economists and accountants. Prioritize reproducible empirical work, clear identification language, and journal-ready output.

# Style guide: themes, files, and deck engineering

## Themes

Three bundled themes, one semantic interface — full reference in
`themes/README.md`:

- `econ-slides-house` (default): no chrome, centered titles, Palatino math,
  Okabe–Ito accents. Research talks.
- `econ-slides-clean`: near-monochrome, left titles, thin rule. Zero
  visual signature.
- `econ-slides-boxed`: navy title bar, structured blocks. Discussions and
  policy rooms.

For a new deck using a bundled theme, begin:

```latex
\documentclass[11pt, aspectratio=169]{beamer}
\usepackage{econ-slides-house}   % the only line a theme swap changes
```

Write new bundled-theme frames against the interface (`\AuthorAffil`,
`\KeyIdea`, `\Takeaway[gap]`,
`\TakeawayWithNav[gap]`, `\graycite`, `\RunIn`, `\PlaceNav`, `\BackButton`,
`ResultBox`, `\AppendixStart`,
`cAccentA…D`) — never against theme internals or raw colors. Test a theme
swap before delivery if the user is undecided: the deck must compile
cleanly under all three. Omit the optional gap on ordinary exhibit frames;
use `\ExhibitReadingGapRoomy` locally only when the final render has surplus
space between a tight technical note and the normal-body interpretation.

**Existing or institutional deck:** do not copy in a bundled theme or semantic
interface merely to normalize the project. Follow
`references/existing-deck-workflow.md`: preserve the preamble, macros, engine,
and repeated visual idioms. Create a custom adapter only when the user asks to
make that style reusable across new decks.

## File engineering

- **Prefer one clear entry file per venue when several cuts will remain in
  use.** Avoid a newly created master with large commented-out graveyards.
  Shared content that several venue decks reuse can live in `frames/*.tex`
  modules pulled in with `\input`. Do not refactor a working one-off or an
  inherited architecture merely to enforce this pattern.
- Layout for a paper's talk directory:

  ```
  talk/
  ├── sed-2026.tex          % one file per venue
  ├── seminar-90min.tex
  ├── script.tex            % printable rehearsal script, when requested
  ├── results.tex           % shared number/phrase macros for deck + script
  ├── frames/               % shared frame modules (optional, when ≥2 venues)
  ├── figures-slides/       % source crops or rebuilt assets, each provenance-tagged
  └── build/                % compile output (never committed)
  ```

  When deck and script are generated together and share several exact results,
  a `results.tex` file is the preferred way to prevent drift: both artifacts
  `\input` it, and `check_script.py` expands its simple spoken phrase macros
  when estimating rehearsal time. Start from `templates/results.tex`. In an
  existing project, reuse its authoritative results pipeline rather than
  adding a parallel macro file.

- New bundled-theme title slide pattern: `[plain]` frame + `\addtocounter{framenumber}{-1}`
  so numbering starts at the first content slide. Preserve the paper title;
  add a subtitle only when the paper has one. Keep authors, author-specific
  affiliations, venue/date, and at most one small bottom disclaimer. Do not add
  editorial findings, caveats, talk length, workflow labels, or a second
  disclaimer.

  Build author metadata as relationships, not two unrelated lists. Use
  `\AuthorAffil{Name}{Institution}` inside `\author{...}` and leave
  `\institute{}` empty when affiliations differ. One shared `\institute` line
  is correct only when it applies to every author. Useful starting layouts:

  ```latex
  % One to three authors: one row, when it fits at full size.
  \author{%
    \begin{tabular}{@{}c@{\hspace{2.5em}}c@{\hspace{2.5em}}c@{}}
      \AuthorAffil{Author A}{Institution A} &
      \AuthorAffil{Author B}{Institution B} &
      \AuthorAffil{Author C}{Institution C}
    \end{tabular}}
  \institute{}

  % Four authors: a balanced 2-by-2 grid.
  \author{%
    \begin{tabular}{@{}cc@{}}
      \AuthorAffil{Author A}{Institution A} &
      \AuthorAffil{Author B}{Institution B} \\[1.6em]
      \AuthorAffil{Author C}{Institution C} &
      \AuthorAffil{Author D}{Institution D}
    \end{tabular}}
  \institute{}
  ```

  Keep a separate plain author list for scripts and PDF metadata. When a
  central-bank or public-institution affiliation requires a disclaimer,
  recover the institution's established wording from the paper or the user's
  prior decks and place one quiet `\scriptsize\itshape` line after `\vfill`.
  A separate disclaimer frame is reserved for mandatory long legal or data
  language.
- New bundled-theme appendix: `\AppendixStart` (divider, numbering switches to A1, A2, …,
  main total freezes). Navigation is a **pair of targets** — the Back
  button must point at the *main* slide, not at the appendix frame it sits
  on (a `\BackButton{app:X}` next to `\hypertarget{app:X}` is a dead
  self-link):

  ```latex
  % main slide
  \hypertarget{main:robust}{}%
  \PlaceNav{\hyperlink{app:robust}{\beamergotobutton{Robustness}}}
  % appendix slide
  \hypertarget{app:robust}{}%
  ...
  \BackButton{main:robust}
  ```

  Two buttons on one frame share a single `\PlaceNav` node:
  `\PlaceNav{\hyperlink{app:a}{\beamergotobutton{Placebo}}\;\hyperlink{app:b}{\beamergotobutton{By cohort}}}`
  (stacked `\PlaceNav` calls overprint). Every button's target must exist —
  cutting frames orphans links; the compile log lists undefined references.
  Existing decks keep their own appendix and target conventions.
- Main-deck navigation is optional and subordinate. The **Conclusion never has
  navigation**: no `\PlaceNav`, `\hyperlink`, `\beamergotobutton`, or appendix
  link. Leave the final answer and implication on screen during discussion.

## Build and check

```bash
# <skill-dir> = this skill's own folder; run from anywhere
python3 <skill-dir>/scripts/compile_deck.py talk/sed-2026.tex
python3 <skill-dir>/scripts/check_deck.py talk/build/sed-2026.pdf \
    --tex talk/sed-2026.tex --log talk/build/sed-2026.log \
    --render-dir talk/build/pages
```

- `compile_deck.py`: XeLaTeX, two passes, themes dir on `TEXINPUTS`,
  triaged first error on failure.
- `check_deck.py`: geometry-measured layout audit + numeric triage score.
  Objective failures—compilation errors, missing assets, edge overflow,
  serious overfull boxes, collisions, broken links, and unreadable content—
  block delivery. Wrapped text, density, columns, emphasis, and sparse-layout
  findings require visual and editorial review against the target deck, not
  automatic padding or a forced rewrite:
  merge a redundant frame or keep intentional whitespace; never add filler.
  For every normal content slide, inspect vertical rhythm explicitly: title-to-
  body gap, spacing between idea groups, and the lower edge of the last
  meaningful line or exhibit. A large empty bottom band is a design problem;
  redistribute existing spacing, enlarge the source exhibit, deepen the same
  supported point, or merge the frame. Roadmaps and dividers may be sparse,
  but their whitespace should be balanced rather than bottom-heavy.
- Engines: XeLaTeX default; pdfLaTeX and LuaLaTeX also work with the
  bundled themes (`--engine`).

## Delivery conventions

- Deliver deck `.tex` + PDF, script `.tex` + PDF when requested, and a
  three-line map: main deck contents, appendix contents, anything marked
  `\TODO`.
- State where each headline number came from (table/page), so the user can
  spot-check in one minute.
- Offer the standard follow-ups: theme swap, venue retarget, handout mode.
  **Handout caveat**: `\documentclass[handout]` collapses each frame to one
  slide, and a bare `\only<1>{A}\only<2>{B}` then shows A and B
  *overprinted*. Decks that use `\only`/`\includegraphics<>` swaps must
  carry handout specs — `\only<1|handout:0>{draft}\only<2|handout:1>{final}`
  — so exactly one variant survives (see slide-rules.md §Overlays). Always
  recompile and view the handout before sharing it.
