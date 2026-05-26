---
name: econ-humanizer-plus
description: Supplements the econ-humanizer skill with a more exhaustive and specific rule set for eliminating AI-generated writing patterns in economics, finance, and accounting prose. Adds (1) a 10+ phrase deletion list specific to econ papers ("it should be noted that", "this paper contributes to the literature by", "the remainder of this paper is organized as follows", "we perform/conduct/carry out a regression"), (2) an expanded banned-word list for AI tells ("delve", "landscape", "multifaceted", "notably", "leverage" as verb, "robust" outside stats, "pivotal", "groundbreaking", "shed light on", "pave the way", "crucial", "comprehensive", "furthermore", "utilize"), (3) sentence-length variation rules (mix 8-12 and 15-25 words), (4) explicit permission for em-dashes and parentheticals (real writers use these; over-sanitization is itself an AI tell), (5) hedging guidance ("this likely reflects", "one interpretation is"), (6) field-vocabulary naturalness ("extensive margin", "pass-through", "treatment on treated"), (7) micro rules on "clothe naked this", "where vs in which" for models, compound-modifier hyphenation, and named Greek letters. USE alongside econ-humanizer whenever rewriting for voice in econ/finance/accounting papers. Works on any section (intro, lit review, hypothesis development, results, conclusion). Also use when the user says "humanize", "make this sound less AI", "remove AI tells", "Cochrane style", or requests prose cleanup before top-journal submission.
---

# Econ Humanizer Plus

**Use alongside** `econ-humanizer` — not instead of it. The original handles the core Cochrane-style transforms (active voice, short sentences, plain words, concrete claims). This skill adds the specific lists and micro-rules below.

---

## 1. PHRASES TO DELETE ON SIGHT

Search for these and cut them. In most cases the paragraph is stronger with them removed entirely; occasionally the meaning needs to be rewritten.

**Meta-prose / throat-clearing:**
- "It should be noted that..."
- "It is worth noting that..."
- "It is important to note that..."
- "It is easy to show that..."
- "A comment is in order."
- "In other words..."
- "As mentioned above..."
- "As we will see..."

**Literature-review padding:**
- "An important question in the literature is..."
- "This paper contributes to the literature by..."
- "The literature has long been interested in..."
- "The literature lacks a model of..."

**Methods padding:**
- "We investigate/examine/explore the relationship between X and Y."
- "We perform/conduct/carry out a regression of Y on X."
- "Results are reported in Table X." (tables speak for themselves if captioned well)

**Roadmap:**
- "The remainder of this paper is organized as follows." (Keep the roadmap content, drop this sentence.)

**"That"-deletion heuristic:**
Search for "that" and try deleting the preceding clause. Often the sentence tightens: "The results show that X increases Y" → "X increases Y."

---

## 2. BANNED AI WORDS

These are tells. A single use is fine; repeated use (>1 per section) signals AI prose.

**Never use in academic econ prose:**
- "delve", "delve into"
- "landscape" (as in "the economic landscape")
- "multifaceted"
- "notably" (almost always deletable)
- "leverage" as a verb (use "use" or "exploit")
- "robust" outside its statistical meaning (don't say "robust findings" — say "strong" or just report the evidence)
- "pivotal"
- "groundbreaking"
- "shed light on"
- "pave the way"
- "comprehensive" (almost always hollow)
- "furthermore" (use a period + new sentence)
- "utilize" (use "use")
- "crucial" (usually unsupported; be concrete about why it matters)
- "underscore" / "underscores"

**Use sparingly, with specific content:**
- "important" — only when you say why
- "significant" — reserve for the statistical meaning; use "large" for economic significance
- "interesting" — delete; show, don't tell

---

## 3. SENTENCE LENGTH VARIATION

AI prose trends toward uniform medium-length sentences. Real academic writing mixes:

- **Short** (8-12 words): for punch, for the finding, for the transition.
- **Medium** (13-20 words): most sentences.
- **Long** (20-30 words): for setup, for a qualified claim, for a list.

**Check:** read three consecutive sentences aloud. If they all feel the same length, break one in half or combine two with a semicolon.

---

## 4. EM-DASHES AND PARENTHETICALS ARE ALLOWED (Even Encouraged)

Over-sanitization is itself an AI tell. Real academics use:
- **Em-dashes** for qualifications and asides: "The effect — small but precisely estimated — survives every robustness check."
- **Parentheticals** for side notes: "Workers (particularly those in manufacturing) respond strongly."
- **Semicolons** for paired clauses: "The coefficient is positive; the magnitude is modest."

Do NOT strip all of these in the name of "cleaning up." A paragraph with zero em-dashes and zero parentheticals reads robotic.

---

## 5. HEDGING — USE IT

AI writing over-asserts. Real empirical work hedges where warranted:

- "This likely reflects..."
- "One interpretation is..."
- "A plausible explanation is..."
- "The evidence is consistent with [A] but does not rule out [B]."
- "We cannot distinguish between [A] and [B] with these data."

**But:** do not hedge the main finding itself in the abstract or introduction. Hedge interpretations, not results.

---

## 6. FIELD VOCABULARY — USE IT NATURALLY

Generic phrasing is a tell. Use the actual vocabulary of the subfield:

- **Labor:** extensive margin, intensive margin, job ladder, reservation wage, LATE, compliers
- **IO / trade:** pass-through, markup, market power, demand elasticity, MRPL, gravity, multilateral resistance
- **Public / health:** treatment on treated, ITT, take-up, compliance, salience, framing
- **Finance:** abnormal returns, CAR/BHAR, cross-section, factor loadings, Fama-MacBeth, winsorize
- **Accounting:** discretionary accruals, earnings management, going concern, conservatism, timely loss recognition
- **Macro:** impulse response, steady state, shock, wedge, log-linearization, calibration

If the draft says "the effect of the policy" where "pass-through" is the right word, change it.

---

## 7. NAME SPECIFIC INSTITUTIONS

Generic placeholders are AI tells. Replace:

- "the dataset" → "the Current Population Survey" / "Compustat" / "the HRS"
- "the agency" → "the EPA" / "the FDIC"
- "the policy" → "the 2010 minimum-wage increase in Washington State"
- "the country" / "the economy" → "the United States" / "the German economy"

---

## 8. MICRO-RULES

### Clothe naked "this"
Never let "this" stand alone as a subject. Add the noun:
- ✗ "This shows that wages rose."
- ✓ "This regression shows that wages rose."
- ✓ "This pattern reflects..."

### "Where" vs. "in which"
- "Where" = physical place. "In California, where wages rose..."
- "In which" = abstract / model / conditions. "Models in which consumers have shocks..." NOT "models where consumers have shocks."

### Compound-modifier hyphenation
Before a noun: hyphenate multi-word modifiers.
- "risk-free rate", "after-tax income", "above-median firms", "two-period model"
- BUT NOT when the first word is an -ly adverb: "randomly assigned treatment" (no hyphen), "statistically significant result" (no hyphen).

### Name every Greek letter
Don't leave σ or γ unexplained. On first use:
- "the elasticity of substitution, σ, equals 3"
- "the discount factor β ∈ (0, 1)"
Then remind the reader on re-use in a distant section.

### No double adjectives on your own work
- ✗ "very novel", "truly striking", "highly significant" (unless quoting a test)
- ✓ Just state the magnitude and let the reader judge.

### No self-adjectives at all
Don't tell the reader your results are "striking", "important", "remarkable", "surprising". Report the finding; the reader decides.

---

## 9. PARAGRAPH RHYTHM CHECK

Before finalizing a paragraph, verify:
- Opens with a **claim** (a topic sentence), not a citation.
- Has **one** idea — if it has two, split it.
- Closes with a **claim or transition**, not a citation dump.
- Contains at least one **concrete** datum, magnitude, or institution (unless it's a pure theory paragraph).

---

## 10. COAUTHORSHIP VOICE

Multi-author drafts often have style discontinuities that look AI-like because different authors (or AI at different times) wrote different sections.

- Agree on "we" vs. "I" upfront. Use the same one throughout.
- Designate a **voice editor** who reads end-to-end for tonal consistency.
- If one section feels different, rewrite for rhythm — don't just copy-edit words.

---

## 11. HOW THIS SKILL DIFFERS FROM `econ-humanizer`

| Concern | `econ-humanizer` | `econ-humanizer-plus` |
|--------|-----------------|-----------------------|
| Active voice | ✓ | — |
| Plain words | ✓ | — |
| Specific phrase-deletion list | — | §1 |
| Specific banned AI words | — | §2 |
| Sentence-length variation | — | §3 |
| Em-dash / parenthetical *permission* | — | §4 |
| Hedging guidance | — | §5 |
| Field vocabulary | — | §6 |
| Specific institutions | — | §7 |
| "Where" vs. "in which" | — | §8 |
| Compound-modifier hyphens | — | §8 |
| Greek letter naming | — | §8 |

When both skills trigger, defer to `econ-humanizer` for top-level voice (Cochrane-style active/direct/concrete) and apply the specific rules above as a second pass.

---

*Rules synthesized from the hanlulong/econ-writing-skill corpus: Cochrane "Writing Tips for PhD Students", McCloskey "Economical Writing", Shapiro "Writing Economics", Head "Five Tips for a Perfect Introduction", Bellemare "How to Publish in Top Journals".*
