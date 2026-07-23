> **Barrios Skills** — John Barrios's curated workflow for economists and accountants. Prioritize reproducible empirical work, clear identification language, and journal-ready output.

# Beamer layout mechanics: source changes and rendered consequences

Read this before editing an existing deck or changing a theme macro. Beamer
does not place independent objects on a canvas. Each frame is a vertical TeX
box whose paragraphs, lists, displays, tables, glue, navigation, and theme
footer compete for the same height. A small source edit can therefore reflow
the entire lower half of a slide.

## The mental model

1. The theme fixes the usable text rectangle: page size minus headline,
   frametitle, footline, and margins.
2. TeX lays out each paragraph horizontally at the current font size. If one
   word no longer fits, the paragraph gains a full extra line.
3. TeX computes the natural vertical height of every paragraph, display,
   list, table, and fixed skip.
4. Stretchable glue such as `\vfill` receives whatever height remains. Two
   `\vfill`s split the remainder; when a sentence wraps, both gaps shrink and
   every object below can jump.
5. The theme draws its footline and navigation lane. Content that appeared
   safe in source can now look stranded, collide, or leave an accidental band.

The rendered PDF is the artifact. Source indentation and source-line length do
not predict the visual result.

## Consequences of common edits

- **Add or remove words:** may create a new rendered line, increasing the
  frame's height and changing every stretchable gap below it.
- **Change `\small`, `\footnotesize`, or `\normalsize`:** changes both font
  size and line breaks. A smaller interpretation line is not merely quieter;
  it also changes the slide's vertical rhythm and can make the line look like a
  table note rather than part of the argument.
- **Add `\vfill`:** does not mean “add a little space.” It means “absorb all
  remaining space here.” It is appropriate for a deliberately anchored final
  object, not as a generic separator between ordinary ideas.
- **Change `\itemsep`, `\topsep`, or nested lists:** affects the list's total
  height. Beamer's list defaults already include vertical glue, so adding
  manual skips around a list can double the intended gap.
- **Change a table's `\arraystretch`:** changes every row, often by enough to
  move the interpretation or navigation lane. Scope the change inside the
  table group.
- **Change image height:** `height=.60\textheight` is relative to the frame's
  text height, not the remaining height after a long title or subtitle. Always
  inspect the composed frame.
- **Add a Beamer button:** buttons have height and sit above the footline. Keep
  them in a separate navigation lane; do not make the interpretation line
  absorb or compete with button spacing.
- **Use `[t]` on a frame:** top-aligns the frame body. Without it, Beamer may
  vertically center a sparse body. Choose deliberately and verify the PDF.
- **Add an overlay:** every build must fit the same reserved geometry. Use an
  `overlayarea` or an equivalent stable box when later builds are taller.

## Stable layout procedure

1. Identify the frame's role and its primary reading task.
2. Use the user's existing body font and list conventions. Do not introduce a
   smaller local font simply to make a line fit.
3. Rewrite titles, bullets, and run-in sentences so each stays on one rendered
   line when the idea can be stated clearly that way. Split genuinely distinct
   ideas rather than shrinking them.
4. Use bounded spacing (`\smallskip`, `\medskip`, a scoped `\vspace{...}`, or
   list `\itemsep`) between ordinary idea groups. Use `\vfill` only when the
   resulting anchor is intentional under both one-line and two-line variants.
   When a text frame has surplus room, enlarge gaps by hierarchy: distinct
   claim groups first, then parent-to-support and sibling-support gaps by a
   smaller amount. Keep nested support attached to its claim and make the
   change locally, not through global list defaults.
5. Put a table/figure reading directly after the exhibit at normal body size.
   Keep a technical source or table note tight to the exhibit, then use a
   separate bounded gap before the reading so the audience does not mistake
   interpretation for fine print. The reading should state the insight,
   intuition, economic scale, interpretation, or decisive limitation. Put
   navigation buttons in a separate lane below it. Bundled-theme decks may
   use `\Takeaway[\ExhibitReadingGapRoomy]{...}` locally when the final render
   has room; inherited decks use their closest bounded local idiom.
6. Compile after each structural change or coherent local batch. Render the
   affected pages to images and inspect them at presentation size. A shared
   macro change requires inspecting every use; the final pass covers the full
   deck.
7. Crop internal whitespace before enlarging a figure. Then check its width and
   height against the *remaining* frame area, not `\textheight` in isolation;
   the important figure should be large without squeezing its reading.
8. Check the longest title, longest bullet, densest table, sparsest ordinary
   slide, conclusion, and every frame with navigation. A macro is accepted only
   if all of its uses remain balanced.

## Existing-deck rule

Before adding or modifying slides, compile the untouched deck and record its
actual conventions: aspect ratio, theme and font packages, title treatment,
body/list font sizes, margins, color meanings, typical title-to-body gap,
table-note size, interpretation style, navigation, and appendix numbering.
Make the smallest source change that expresses the requested content in those
conventions. Do not import this skill's house theme, spacing macros, or fixed
frame anatomy unless the user explicitly asks for a restyle.

## Verification loop

```text
source edit
  -> compile and read warnings
  -> render affected frames
  -> inspect line breaks, group spacing, exhibit scale, final meaningful line,
     navigation lane, and footer
  -> render and inspect every frame touched by a shared macro
  -> revise source and repeat
```

Static checks are useful for finding overflow and suspicious geometry. They do
not decide whether a gap is intentional, whether an interpretation is worth
saying, or whether a slide matches the user's visual language. Those require a
human visual and substantive review of the PDF.
