> **Barrios Skills** — John Barrios's curated workflow for economists and accountants. Prioritize reproducible empirical work, clear identification language, and journal-ready output.

# Slide guidance and rendered quality gates

Use these procedures for new decks. For an existing deck, its rendered PDF
and repeated source idioms define the visual language; this file supplies
diagnostics rather than permission to restyle it. `scripts/check_deck.py`
reports a measurable subset, while the rendered pages and the argument decide
the detailed treatment.

## Titles

- The title page preserves the paper's actual title. Do not replace it with a
  finding, an editorial verdict, or a subtitle about what the evidence can and
  cannot establish. Use a subtitle only when it belongs to the paper itself.
  Pair every author with the correct institution; a flat institution list is
  not acceptable when affiliations differ.
- **Prefer one rendered line.** If a frame title wraps, first test whether a
  shorter and clearer title preserves the claim. An irreducible, readable wrap
  may remain when the paper or target style requires it. A long paper title may
  use two balanced lines on the title page.
- Prefer an **assertion title** when the warranted message is concise
  ("Effects build over three years"). A short economic object title can be
  better when a sequence, model, or paired exhibit needs orientation
  ("Model fit", "Optimal policy", "Counterfactual"). Structural slides use
  short labels ("Key question", "Data", "This paper", "Roadmap",
  "Conclusion"). Use **Key question**, not "The economic question," for the
  opening research object. When the research question itself is concise and
  carries the frame, make that question the title. Use ``Key question'' when
  the body must first motivate or set up the question; never put the actual
  question only in `\framesubtitle`. Never manufacture an
  editorial verdict merely to make the title assertive. Sentence case
  throughout.
- When the deck uses `\framesubtitle` for exhibit context, put the precise
  experiment there rather than overloading the title: title = claim, subtitle
  = "Log labor productivity; firm and year fixed effects; 95% CIs". If the
  target deck rarely uses subtitles, follow its local caption or note pattern.
- Figure/table slides usually state the message rather than the axes. When an
  object title better matches the surrounding sequence, use it with a precise
  `\framesubtitle` and a one-line reading below the exhibit.

## Story hierarchy and frame anatomy

An author deck has a stable hierarchy. Decide it before choosing layouts:

1. **One primary takeaway** — the result the audience should repeat after the
   talk. It appears on ``This paper,'' the main-result slide, and the close.
2. **Up to two supporting claims** — the design, mechanism, or heterogeneity
   results that make the takeaway interesting or credible.
3. **Boundary audit** — identify the load-bearing qualification to the
   headline. Show it only when omitting it would materially misstate the
   result, normally once beside the evidence it qualifies. It is not promoted
   to an equal contribution, repeated as the deck's refrain, or inserted by
   default on ``This paper'' and the conclusion.

The hierarchy determines screen space and emphasis. A main claim may need a
short reading or intuition underneath it, but there is no sub-bullet quota.
Use sub-bullets only when they advance the same reasoning; a clear one-line
claim, a full-size source exhibit, or a compact result can stand on its own.
Likewise, a figure, equation, or box appears because the argument needs it,
not because a target share of frames must contain a ``hero'' element.

Numbered contribution items use a bold lead phrase (``\textbf{Closed-form
responses} with two expectation wedges: …'') so the phrase can be supported by
a later slide. A qualification stays subordinate to the claim it qualifies.

## Bullets and body text

- **Prefer 1–4 top-level bullets** when bullets are the right form. More items
  trigger a content-hierarchy review, not an automatic font reduction. A
  results slide is often one figure plus one short reading. Avoid a third
  nesting level because the audience cannot recover that hierarchy quickly.
- **Keep each bullet on one rendered line when possible.** Escalation path
  when it does not:
  1. Rewrite tighter (cut clauses, drop hedges).
  2. Put the payoff in one ordinary nested bullet or a neutral run-in line
     (`\RunIn{Interpretation:}`) directly beneath its parent.
  3. Move the qualifying detail to `\framesubtitle` or the appendix.
  4. Last resort, one step down (`\small`) for that list only.
  Inspect any remaining wrap in the PDF; never `\footnotesize` a whole slide
  to cram it.
- **No arrow-shaped bullet markers.** Do not use `\item[$\Rightarrow$]` or
  `\item[$\rightarrow$]`. They make every subpoint look like the slide's
  punchline and create a repetitive mechanical rhythm. Arrows may still appear
  inside a real causal chain or equation, where direction is the content.
- One sentence per line ≈ 45–75 characters (Goldsmith-Pinkham). Vertical
  whitespace (`\medskip`) between idea groups; hand-tune rhythm rather than
  cramming.
- **Choose vertical alignment from the composition.** Beamer's default
  centering often gives a compact Roadmap or short coherent list balanced
  whitespace. `[t]` is useful when a text frame must align with neighboring
  frames or begin close to the title. Compare the render before deciding;
  neither alignment fixes weak content. Never add an exhibit, box, or
  qualification merely to occupy the lower page, and do not use `\vfill` as a
  generic separator or to push a capstone to the footer.
- **Tune bullet spacing by role and local style.** Start from the theme or
  target deck's ordinary list spacing. Give distinct claims more air than a
  nested explanation, then inspect the total composition; numeric `\itemsep`
  recipes are starting points, not a cross-deck standard.
- **Generous between ideas, tight within an idea.** A nested explanation
  belongs to the bullet above it. Keep nested `itemize` compact, or use a
  direct `\RunIn{Interpretation:}` sentence after the parent, so the eye reads
  claim and explanation as one unit while wide gaps separate distinct ideas.
- **Run a surplus-room spacing pass after the words are final.** When a frame
  has extra vertical room, increase bounded spacing in this order: between
  distinct claim groups; modestly between a parent claim and its nested
  support; between sibling support lines; and before the final implication.
  The within-claim gaps must remain visibly smaller than the between-claim
  gaps. Adjust local `\itemsep`, `\topsep`, and bounded skips one small step at
  a time, then re-render. Do not change global list defaults or line spacing,
  and do not add `\vfill` to consume the surplus.
- **Roadmaps use regular weight.** Their job is orientation, not emphasis. In
  a repeated seminar roadmap, gray inactive modules and leave the current
  module in ordinary black; do not bold every stop or enlarge the list merely
  to fill the slide.
- On a single-bullet frame, tighten the indent only if the target style does
  so and the rendered line otherwise looks unnecessarily displaced.
- Nothing on the slide you will not say out loud; screen space = emphasis
  (Shapiro). If attention lapsed for 30 seconds, the slide alone should let
  a listener catch back up (Meager).
- More than about 15 extracted text lines on a non-exhibit slide prompts a
  density review; the PDF decides whether the material is actually readable.

## Single-column default

- Draft every frame in one reading column first. A single visual path is
  easier to scan while listening and is the default across author talks.
- Use two columns only when the comparison is irreducible and simultaneous:
  paired panels, before/after, data/model, treated/control, or two genuinely
  parallel mechanisms. The audience should gain something from seeing the
  objects side by side that it would lose from seeing them in sequence.
- Do not use columns for two ordinary bullet lists, process cards, a question
  beside its caveat, or as a cure for empty space. When columns are necessary,
  give them comparable visual weight and inspect both at final slide size.

## Filling space with depth, not breadth

Geometric fill is a diagnostic, not a content target. Compare the title-to-body
gap, spacing between idea groups, and lower whitespace with nearby frames in
the same deck. Content that stops very early may leave an accidental bottom
band; content pushed too low competes with the footer and navigation lane.
Title pages, roadmaps, and dividers may be intentionally sparse, but their
whitespace should look balanced rather than accidental. A frame that looks
unfinished deserves another editorial pass, while deliberate white space can
be the correct emphasis. When a frame has room and the paper has
something genuinely interesting to add, deepen the *same* point — never add a
new one. The enrichment moves, in order of preference:

1. **A one-line framing sentence** above a numbered list when it improves the
   logic — especially on a contribution slide. Do not add one to a conclusion
   that already lands cleanly.
2. **Sharper `\framesubtitle`** — the precise reading of the exhibit
   (sample, units, specification) instead of a vague one.
3. **A plain intuition line** — an ordinary nested bullet or
   `\RunIn{Interpretation:}` sentence carrying the economic logic or the "so
   what" of the point above it.
4. **A gray parenthetical** — `\graycite{}` with the closest antecedent, a
   benchmark magnitude ("about half the college wage premium"), or the
   institutional detail that pre-empts a question.
5. **A clearer existing exhibit** — enlarge or crop the source exhibit when
   it is already part of the argument.
6. **A small annotated equation** — one term `\underbrace`d with its
   meaning, only when the mechanism is the point.

Never enrich with filler, a second idea, or detail the speaker will not
say out loud. Never invent a demonstration figure to satisfy a layout metric.
If nothing interesting exists to add, the white space stays — space is
emphasis.

## Setup and conclusion discipline

- Do not impose one sequence. Order frames by audience dependency: the shortest
  path through question, answer, required setup, reason to believe or interpret
  the answer, mechanism or intuition, any necessary boundary, and implication. A useful new
  empirical-talk default is Key question, answer, quick Roadmap, setting/data,
  design, and results; it is not a contract for theory, an inherited deck, or a
  request to add only selected slides.
- Before the first result, the audience must know: data source and linkage,
  unit of observation, period, sample size and consequential restriction,
  outcome construction, treatment or exposure, and every nonstandard measure
  used to interpret heterogeneity. A combined Data + design slide is acceptable
  only when none of those fields disappears into the equation.
- Before a theoretical result, the audience must know the relevant agents,
  timing and information, choices and constraints, equilibrium or solution
  concept, load-bearing assumption, and any nonstandard notation. A pure
  theory talk does not need a Data slide. Structural work supplies both the
  empirical targets and the model objects required for fit and counterfactuals.
  Diagnose whether the mechanism is singular, complementary, or competing;
  when opposing forces need separate frames, use the same explanatory skeleton
  and synthesize their net effect before the proposition that depends on it.
- A conclusion normally has three visible moves: the answer to the Key
  question, one supporting pattern, and the implication. Recall a boundary
  only when ending without it would materially overstate the evidence. It contains no sample bookkeeping, robustness
  ranges, table notes, new claims, `\PlaceNav`, `\hyperlink`, or Beamer buttons.
- Treat each appendix link and return control as a one-to-one pair. A backup
  reached from one main frame returns to that frame. Never point several main
  frames to a shared backup with one generic ``Back'' target; duplicate the
  backup or provide explicit labeled return choices when sharing is essential.

## Color consistency across the deck

For a new bundled-theme deck, write a color ledger before drafting: economic
object, old/new status, alias, and every recurring use. Standard or inherited
objects normally remain black; the paper's new friction, treatment, wedge, or
mechanism may receive a concept color. Declare the aliases once at the top of
the `.tex`, so slides never reference raw accents. For an existing deck,
record and reuse its current map:

```latex
% COLOR LEDGER (one color per concept, held for the whole talk):
%   baseline/old object = neutral
%   treatment/new object = cAccentA   mechanism/model = cAccentC
\colorlet{cTreat}{cAccentA}
\colorlet{cModel}{cAccentC}
```

Slides and rebuilt figures use `cTreat`/`cModel`, so a concept cannot
change color between slide 6 and slide 12. Audit the map during the visual
pass: same concept, same color, every appearance — and no accent used
without a meaning. In a theory talk, this often means familiar benchmark terms
remain neutral while the paper's new wedge is colored at introduction and on
every return. In an experiment, treatment, outcome, and comparison objects may
need separate aliases when that distinction drives the argument.

## Overlays

- Use overlays **only to build reasoning**: revealing an identification argument
  step by step, adding channels to a figure one at a time, "Data | Model"
  columns appearing after the data is absorbed.
- Reserve stable geometry with `overlayarea`, fixed boxes, or full figure
  swaps so content does not jump between builds. Reuse the target deck's
  established stable-overlay method when editing an existing presentation.
- **Make every `\only`/figure swap handout-safe**: tag which variant the
  handout keeps — `\only<1|handout:0>{build}\only<2|handout:1>{final}` —
  otherwise `[handout]` mode overprints all variants on one slide.
  `\item<2->` needs no spec (it simply shows).
- Never `\pause` down a bullet list (the checker flags 3+ `\pause` per
  frame). If a reveal isn't rehearsed, show everything at once.
- A build must change the evidence or the reasoning. Revealing a bullet while
  the final figure is already visible is decorative; make the exhibit itself
  progress or remove the click and show the frame statically.
- Discussant decks: fully static.

## Math

- One to three display equations is a useful starting range. Introduce each in
  words and explain each key symbol *on that slide* — no one remembers notation across slides
  (Piazzesi). Prefer words to symbols where words are exact.
- Build the estimating equation in stages (baseline → add the interaction
  → add fixed effects), not as a wall. The full system, derivations, and
  proofs live in the appendix behind a button.
- A load-bearing proposition may use one compact `ResultBox` when the box can
  hold the assumptions and result without crowding. Otherwise state the result
  in words or with the annotated equation; theoretical content does not create
  a box requirement.
- For a load-bearing higher-order or Jensen term, show the economic state
  comparison before manipulating the formula: keep today's state and the
  relevant mean fixed, widen a two-state distribution, and name the current
  choice that changes because the expectation is nonlinear. The equation then
  formalizes an intuition the audience already understands.

### Defining new notation (the discipline)

Every **key, new, or nonstandard** symbol is defined at its first
appearance, on the same slide, and the definition is *economic*, not
lexical:

1. **The `where` line**, directly under the display, in plain economic
   language: "where $\kappa$ governs how fast prices adjust and
   $\rho$ is the persistence of the shock" — never "where $\kappa$ is a
   parameter". If the `where` line needs more than one sentence, the
   equation carries too many new symbols — split the build.
2. **In-place naming for composite terms**:
   `\underbrace{...}_{\text{adjustment cost $>0$}}` — the economic name
   *plus the sign* whenever the sign drives the argument; compact sign
   tags via `\overbrace{...}^{\scriptscriptstyle(+)}`.
3. **Color as identity for the talk's key objects**: introduce a central
   object once with its concept color and name
   (`\textcolor{cModel}{u^{NK}}`, per the color map); afterwards the color
   alone carries the identity across every equation, bullet, and figure.
4. **Spotlight one term at a time** when walking a decomposition:
   `{\color<2>{cHighlight}\underbrace{...}_{...}}` — discuss term by term
   over overlays, never all at once.
5. **Re-ground returning notation**: when a symbol reappears after several
   slides, remind rather than assume — a parenthetical "(recall $\kappa$ =
   price-adjustment cost)" or the `\framesubtitle`.

What NOT to define: standard objects (logs, expectations, $i$/$t$
subscripts, OLS notation). Defining the obvious clutters exactly where
clean definition should stand out — knowing what needs no definition is
half the discipline.

## Color

- In a new bundled-theme deck, use its Okabe–Ito palette: `cAccentA` (blue), `cAccentB`
  (vermillion), `cAccentC` (teal), `cAccentD` (amber), `cHighlight`
  (spotlight). Never raw `\color{red}`/`green` — and never a red-vs-green
  semantic pair. In an existing deck, preserve its established accessible
  concept colors instead of importing these names.
- **One color per recurring concept, for the whole talk**: if the treatment
  effect is blue on slide 6, it is blue in every equation, bullet, figure
  line, and legend thereafter. The audience learns the mapping once.
- **Slide colors = figure colors when the figure is editable.** A rebuilt
  exhibit uses the same hex values (see exhibit-surgery.md). For a reused
  source figure, adapt the slide's concept colors to it or keep the nearby
  text neutral; a blue line beside a vermillion label for the same object is
  a bug.
- ≤ 3 active concept colors on any one slide. Reserve `cHighlight` for a
  transient spotlight, such as the term currently being explained in a build;
  it is not the automatic color for every headline number.
- At most one primary emphasis treatment per slide. Use neutral bold or the
  relevant concept color for the load-bearing phrase. Do not give caveats,
  source-status labels, navigation, or decorative boxes more visual weight
  than the economic result.

## Voice and anti-AI tells

- Slide text is telegraphic but human: verbs, concrete nouns, actual
  magnitudes. "Productivity is 3.4% higher after rollout" not "has important
  implications for productivity"; use "raises" only when the source-integrity
  pass supports a causal verb.
- Banned on slides: "delve", "crucial(ly)", "notably", "landscape",
  "multifaceted", "novel insights", "shed light on", "it is worth noting",
  decorative em-dash chains, exclamation marks, rhetorical questions as
  filler, three-noun stacks.
- Vary slide composition when the source warrants it: exhibit slides,
  one-bullet slides, and an occasional genuine `ResultBox`. Variation is not
  permission to manufacture a picture or a box.
- Numbers: 2–3 significant digits on slides; units on every number; state
  what the parentheses are (SEs? clustered by what?) in the exhibit note.

## Slide-count sanity (checker-visible symptoms of deeper problems)

| Symptom | Real problem |
|---|---|
| Title wraps | The claim isn't distilled yet |
| 6+ bullets | Two slides, or the point isn't chosen |
| Font shrunk to fit | The content belongs in the appendix |
| 4+ colors active | The color code has no meaning |
| `\pause` chain | Overlay as decoration |
| Wall of text | The paper is being pasted, not presented |
