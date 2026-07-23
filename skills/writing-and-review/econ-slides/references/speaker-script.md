> **Barrios Skills** — John Barrios's curated workflow for economists and accountants. Prioritize reproducible empirical work, clear identification language, and journal-ready output.

# Speaker scripts: the voice layer

A deck says what is true; the script says how to *tell* it. The skill
generates a speaker script alongside any deck on request (and offers it by
default for conference talks and job talks). Everything here is
audience-oriented and written for the ear, not the eye.

## The deliverable

`script.tex` — a standalone `article` that compiles to a printable
rehearsal script — with this structure:

1. **Opening block** (over the title slide): fully scripted, about 40–70
   words. Greet the room, name the paper and coauthors, identify the occasion,
   and give a one-line disclaimer when required. Do not turn the title slide
   into a second motivation or results slide; the substantive takeaway lands
   on the deck's first intelligible answer frame within the opening minutes.
2. **One block per content frame**, keyed to the **exact frame title**
   (never the slide number — numbers drift when frames move; titles are
   stable). Each block carries: the title, a time budget, and the spoken
   text.
   If the deck has a **Key question** or **Roadmap** frame, preserve that exact
   title and its actual location; do not invent, rename, or reorder frames to
   satisfy a script template. Never call the research object "the economic
   question" in a heading or transition.
3. **Conclusion block**: tight, near-verbatim, and shorter than the deck's
   main answer frame. State the answer to the central question, one useful supporting result, and the
   one proportionate boundary only when needed to prevent overreading. Do not
   recite the sample, specification range, robustness inventory, or appendix
   links. End on the economic implication, not a new caveat or "thank you".
   Finish within the approved speaking window; running over is never the plan.
4. **Q&A appendix**: 40–90-word conditional answers for selected
   high-probability backup slides ("if someone asks about clustering — jump
   to A2, say: …"),
   plus the standing Q&A stance: listen to the whole question, count to
   three, explain rather than capitulate, concede gracefully, first the
   bad news then the good news. A large appendix does not require a scripted
   answer for every slide.
5. **Live cue layer**: frame title plus first sentence and real click marks,
   as one compact, ragged-right list in slide order. Single-column scanning is
   the default; use two columns only when the user explicitly needs a one-page
   physical cue sheet and the rendered result has been inspected. Use the
   largest comfortably readable font that fits, then tune bounded item spacing
   after rendering; do not leave a tiny `\footnotesize` list at the top of an
   otherwise empty page.

Block skeleton:

```latex
\scriptframe{Gains concentrate where the model predicts}{2.0 min}{%
  So why does this happen? [Click 2] Look first at the interaction row —
  the extra gain for a communication-intensive firm. It's about a fifth
  of the main difference. That is the direction predicted by the
  task-outsourcing model, so the pattern is consistent with that channel: ...
}
```

## Timing and budgets

- Treat the clock as the **total session** unless the user explicitly gives
  speaking time. Plan **75--80%** for prepared speech and reserve **20--25%**
  for questions. A 30-minute session therefore carries 22.5--24 minutes of
  prepared speech. Planned time is the opening plus main-deck blocks;
  conditional Q\&A is reported separately and never pads the talk.
- When the user explicitly gives a **speaking-time allocation**, honor that
  number directly; do not apply the 75--80% conversion again. Check it with
  `--speaking-minutes`, which treats the allocation as a ceiling and keeps any
  separately managed question period outside the clock.
- Substantive blocks commonly fall near **80--280 spoken words**, but that is a
  descriptive range, not a ceiling. A load-bearing exhibit or proposition may
  need more when its declared minutes and source-supported reasoning warrant
  it. The checker evaluates each timed main block against that block's own
  minute label, then prints block counts and a cumulative clock. The Roadmap
  often needs only 25--45 words. All ranges are diagnostics, never invitations
  to add filler.
- Appendix answers often need **40–90 words**. The checker reports unusually
  short or long answers for review; it does not ask the writer to pad a simple
  answer or truncate a genuinely technical one mechanically.
- Budget by role, not uniformly: opening, punchline, and conclusion are
  tight and near-verbatim; result exhibits are click-synced and get the
  most time; orientation frames are lighter; a Roadmap, when present, is 25--45 spoken
  words; appendix blocks are
  conditional only.
- Mechanical frames may use short director's cues rather than padded prose.
  Do not add words merely to reach a minute or word target. If the substantive
  script is short, deepen only motivation, exhibit orientation, economic
  intuition, transparent reasoning, meaningful benchmarks, evidence-supported
  interpretation, or transitions the audience actually needs. For a total
  session, a script materially below the 75--80% prepared-speech window calls
  for a scope decision or user input, not filler; finishing near the low end of
  that window is fine. For an explicit speaking-time ceiling, a shorter script
  may be appropriate when the requested content is complete.
- Over budget ⇒ cut content, never plan to talk faster.

## Slide ↔ voice division of labor

- The slide carries the **claim and the precise number**; the voice
  carries the **reading**, on a gradient:
  - headline numbers are spoken rounded ("about one percentage point");
  - comparisons beat levels ("roughly twice as important");
  - numbers too small to say cleanly become qualitative words — a 0.07%
    effect is spoken as "moves only modestly", never as a smaller decimal;
  - numbers that live on a figure's axis are read as **shape**, not value
    ("jumps sharply, then plateaus") — the axis already shows the level.
  Every spoken number is provenance-linked to the same source as the
  slide's. When deck and script are generated together, **share a
  `results.tex` of number macros** used by both — separately maintained
  decks and papers drift (a real deck in the reference corpus quotes a
  15 pp effect where the current paper says 24 pp; shared macros make
  that impossible).
- The voice cannot upgrade the evidence. A descriptive slide cannot become a
  causal sentence; "consistent with" cannot become "confirms"; conditional
  gross-output arithmetic cannot become fiscal payback. Audit first sentences
  against the claim--evidence ledger in `source-integrity.md`.
- In an author talk, evidence discipline changes verbs, not genre. The script
  should still teach the paper's primary takeaway, up to two supports, and one
  boundary. Do not make every transition lead into another objection or repeat
  the boundary after it has been established.
- **Introduce every exhibit before interpreting it**: say what the axes
  are and where to look first, then read the pattern. Never talk over an
  unexplained figure.
- **Equations are never read as algebra.** Each symbol is glossed by its
  economic meaning ("a rise in $q_t$ — a real depreciation — ..."), with
  a marked pause before the walk-through. If the deck's notation isn't
  aurally distinct, flag it back to the deck (a design bug).
- Don't read the slide and don't recite bullets — the voice adds what the
  slide cannot: intuition, story, comparisons, the "why you should care".
- On the Data block, name the source/linkage, unit, period, sample and key
  restriction, outcome construction, treatment/exposure, and nonstandard
  heterogeneity measure in ordinary language. If Data and design share a
  frame, the script still covers both layers explicitly before moving to the
  first result.
- On a theory Environment or Mechanism block, name agents, timing,
  information, choices, constraints, equilibrium object, and the load-bearing
  assumption in spoken economic language. State a proposition in words before
  formal notation, explain the mechanism that makes it true, and leave proof
  steps to Q\&A unless the proof idea is the contribution. When a Jensen term,
  volatility shock, or other higher-order expectation is load-bearing, give a
  concrete two-state or limiting-case comparison before the algebra: hold
  today's state and the relevant mean fixed, change the dispersion, then say
  whose current decision changes and why the nonlinear expectation changes it.

## Oral language rules

- **Speak as an author, not as a report on the paper.** Prefer ``We link the
  rollout to firm records'' and ``We find'' to ``The paper displays'' or
  ``Across the paper's specifications.'' A ``This paper'' block should make
  the paper attractive: what we do, what we find, the economic mechanism or
  interpretation, and why the result matters. It is not the place for a
  specification inventory or a list of qualifications.
- **Define the result positively before guarding against a misreading.** Say
  what a number means in one concrete sentence. Add at most one contrast when
  the room is genuinely likely to confuse the units or object. Do not stack
  defensive clauses such as ``not growth, not adoption, not TFP,'' and do not
  explain a result by listing everything it is not.
- **Translate paper language into speech.** Words such as ``estimand,''
  ``displayed specifications,'' ``descriptive reading,'' ``robustness
  envelope,'' and ``counterfactual'' belong only when the audience needs the
  technical term. In ordinary exposition, say ``the comparison answers,''
  ``the estimates are similar,'' ``we read this as a pattern,'' or ``what
  would have happened otherwise.'' Never say ``the paper's displayed
  specifications'' aloud.
- **Keep disclosure proportionate.** State the one interpretation-changing
  boundary on the first design or result slide where the audience can
  understand it. Do not preview the full limitation in ``This paper,'' repeat
  it on every result, and then end on it again. A conclusion normally returns
  to the answer, mechanism, and implication; recall the boundary only when
  omitting it would make the final claim false.
- Prefer to open each frame's block with a short declarative, then explain
  (the title-slide opening block is the exception — it is a short scripted
  greeting, not a frame block).
  Spoken sentences run ~15–20 words; front-load the shortest.
- Bridge a slide change when the audience needs the logical connection; skip
  mechanical narration such as “this slide shows.” Signpost and repeat only
  when it helps listeners recover the argument. Verbal callbacks and
  forward-pointers are useful when they name the substantive connection, not
  as routine scaffolding.
- Contractions, "So/Now" beats, and the occasional rhetorical question
  are correct oral style. The anti-AI-tell blocklist still applies fully
  (no "delve", "crucial", "notably", "landscape").
- Enthusiasm without spin: sell the question's importance with energy,
  but teach the results like an honest teacher — script the excitement,
  never overclaim beyond what the deck's numbers support.
- Every sentence must establish stakes, orient attention, reason, interpret,
  qualify, or connect. Interest comes from the economic tension, surprising
  contrast, mechanism, benchmark, or implication, not from hype adjectives or
  duration padding. Read aloud and replace abstract labels, noun stacks, and
  phrases a leading economist would not naturally say. As a final mouth test,
  ask whether the presenter would use the sentence while explaining the paper
  to a respected colleague without notes. If not, rewrite it before timing the
  block.

### Oral edit procedure

Use these passes after the source-faithful draft; they are judgment steps, not
word-substitution rules.

1. **First-sentence pass.** Read only the opening and the first sentence of
   every main block. They should recover the question, what the paper does, the
   answer, the evidence, and the implication in a coherent spoken sequence. If
   they sound like file labels (``the table reports,'' ``the specification
   adds''), rewrite them around the economic object.
2. **Colleague pass.** Read every block aloud without looking at the slide.
   Replace sentences one would write in a referee report but not say to a
   colleague: provenance narration, stacked exclusions, abstract noun chains,
   and specification bookkeeping. Keep technical vocabulary when it saves a
   longer explanation for the actual audience.
3. **Explanation pass.** For each result, check the order: orient the exhibit;
   point to the comparison; state the result; explain the intuition or economic
   scale; connect it to the question. A claim with no ``why'' or ``so what'' is
   incomplete even when it is correct. For higher-order mechanisms, require
   the state comparison and current-decision sentence to work without the
   equation; terms such as ``Jensen effect'' or ``third order'' name the object
   but do not explain it.
4. **Author-story pass.** Read ``This paper'' and the conclusion together. They
   should sell the same contribution in the same language. Move a necessary
   boundary to the first design or result block where it changes the reading;
   remove repeated boundary language elsewhere. Never repair a timing shortfall
   by adding another caveat or specification.
5. **Cue pass.** Verify that each live cue reproduces the block's actual first
   spoken sentence and that the cue sequence alone still carries the argument.

## Sync with the deck (mechanical rules)

- **`[Click n]` markers only where a build gates the narrative** (a figure
  gaining a series, a term being spotlighted) — derived from the deck's
  actual overlay specs, never hand-counted. Bullet reveals are not
  click-tracked: when bullets unfold one by one, write the script
  paragraphs **in the same order as the bullets**, so reaching the next
  paragraph *is* the click. The voice then speaks the connective tissue —
  the "because", the intuition — while the audience reads the revealed
  claim; the script never reads a bullet aloud.
  For a semantic frame with builds 1 through N, mark each transition exactly
  once and in order: `[Click 2]`, …, `[Click N]`. Missing, zero, duplicated,
  or reversed markers fail the checker.
- **Title-set check**: every script block title must exactly match a frame
  title in the deck, and every content frame must have a block —
  `scripts/check_script.py` diffs the two and fails on drift.
- Emphasis: mark the 1–2 stress words per block (`\emph`) and deliberate
  pauses (`[pause]`) sparingly — a script that marks everything marks
  nothing.

## Genre and venue variants

- **Discussant scripts** follow the discussion arc, not the talk arc:
  a genuinely generous opening ("a very rich paper — I enjoyed reading
  it"), the one-slide summary told *in the authors' favor*, then each
  titled comment spoken as a hedged critique that lands on a concrete
  suggestion, and a generous close ("I'll stop here."). Hedging is
  correct register here, not weakness. Static slides — no click marks.
- **Retargeting a script** to a new venue: the results spine (the worked
  example, the key magnitudes, the mechanism chain) is reused verbatim;
  the **opening is a venue-templated slot** rewritten each time (workshop
  vs. seminar vs. public audience). Retargeting *up* to a general
  audience is re-authoring — prepend accessible framing and drop the
  equations — never padding the existing script.
- Test every sentence by mouth: if a word is hard to say, replace it —
  the ear, not the page, is the editor.
- Compile and inspect the printable script. Keep a heading with at least the
  first three lines of its block; keep each `Live cue` with the paragraph it
  summarizes; keep a concise conclusion block together; start Q\&A on a fresh
  page; avoid a nearly empty final page. A cue sheet may share the remaining
  space after the conclusion when the resulting page is balanced. The template
  uses `needspace`, `samepage`, and a nonbreaking cue separator to make these
  the default, but the rendered PDF remains the authority.

## What the script is for

It is a **rehearsal instrument and a safety net**, not a teleprompter.
The craft consensus: never read slides aloud, never recite from memory —
rehearse from the full script until it collapses naturally into cues, and
keep the thin, single-column cue layer (frame title + first line + click
marks) for live use. For non-native speakers the full script matters more:
overlearn the opening and the transitions verbatim; those carry the talk.
