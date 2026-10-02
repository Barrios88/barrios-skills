# Audit lenses

Use with `econ-referee`. Record findings during the pass. Leave the lens empty when the paper has no such object, or when nothing material fails.

Search the web only for literature identity, a named registry or pre-analysis plan, and institutional facts that change interpretation. If search is unavailable, mark those items **Cannot verify**. Do not imply they were checked.

## Always on

### Source fidelity

Build a ledger for every central claim about the paper's own analysis:

- table, figure, panel, column, row, outcome, treatment, reference group
- population, restriction, unit, timing, denominator, transformation, sign, threshold, coding rule
- analysis *N* versus recruited, randomized, or downloaded counts, including item nonresponse and complete-case drops
- the same acronym across displays: label, coding source, sample, and threshold
- prose that says a result persists, is robust, or uses a named specification, matched to the appendix display

Then walk each main table and figure: title, caption, axes, legend, sample, and plotted quantity. Use the page image when extracted text cannot establish a sign or label.

Report clear contradictions and mappings too ambiguous to interpret a central result. Do not report confirmed matches.

### Numbers

Check text against tables for sign, scale, units, and rounding. Recompute sentences with difference, increase, decrease, percent, percentage points, ratios, log points, standardized effects, or elapsed time. Confirm the baseline the sentence uses.

Test adding-up identities only after the components share sample, denominator, timing, and specification. If a balancing category is missing, **Cannot verify**. Do not invent it.

Set an expected value only when the estimand and inputs are in the paper. Dividing a mean numerator by a mean denominator does not by itself disprove a mean of ratios.

Keep this pass numerical. Design critiques belong in identification.

### Claims and summaries

Reconcile abstract, introduction, results, and conclusion sentences that name a table, figure, population, denominator, or outcome with that display.

Flag summary language that is staler or stronger than the body, including translations from a survey item, proxy, platform metric, or lab outcome into behavior, welfare, or a mechanism.

Flag a label only when it changes the claim: a coded-mention share is not the share who hold a belief; non-mention is not measured disagreement.

### Displayed specifications

For each main regression or model table, match dependent variable, sample, treatment or instrument, reference group, fixed effects, estimator, and displayed equation to the prose and note.

Notation drift is a correction when a reused symbol changes meaning inside a result the reader needs. Cosmetic notation goes to editing notes.

### Cross-references

Check references a result depends on. A target missing from extracted text is a manuscript defect only after the page images also lack it.

## Conditional

### Identification

Run when the paper uses causal, mechanism, or policy language, or names a design (difference-in-differences, instrument, regression discontinuity, bunching, event study, experiment).

Check estimand, population, treatment, outcome, and timing against the design. Name the identifying assumption the claim needs. Flag "driven by," "shows why," or "true preference" when the design does not identify that mechanism.

Post-treatment variables described as mechanisms need a mediation design or narrower language.

### Sample construction

Trace screened or invited observations through eligibility, assignment, activity filters, follow-up, and the analysis sample. Compare table *N* with stated exclusions.

Watch person versus firm versus account versus time-weighted units, and first versus last versus average when a unit appears more than once. Reconcile human-coded and model-coded versions of the same construct.

Archival papers: Compustat filters, fiscal-year alignment, winsorization, delisting, and merge keys are part of this pass.

### Robustness language

Inventory "robust," "persists," "unchanged," "heterogeneity," and checks promised in the text or a pre-analysis plan. Match each to the reported specification.

"Larger for group X" needs a direct comparison or an interaction, or a descriptive caveat. Do not request extra subgroups the paper never claimed.

### Economic magnitude

Run when the paper calls an effect large, material, welfare-relevant, or policy-relevant.

Check baseline, unit, population, and horizon. Percent versus percentage points. A standardized effect is not a return in basis points unless the paper builds that translation.

Report only where magnitude language changes the interpretation.

### Power, multiplicity, and nulls

Run when the paper emphasizes many outcomes, subgroups, or specifications, or says "no effect."

Do not complain about multiplicity when the manuscript aggregates tests, labels results descriptive, or does not rest the claim on the fragile test.

"No effect" needs a minimum detectable effect, an equivalence bound, or narrower language. Match emphasized outcomes to declared primary outcomes when a plan exists.

### Randomization and implementation

Run for experiments and field assignments. Reconstruct recruitment, baseline, assignment, treatment, outcomes, and exclusions in time order.

Check unit of assignment, attrition after assignment, spillovers, noncompliance, and carryover from earlier modules. A defined pairwise contrast inside a multi-arm design is not an omitted arm. A missing balance table is a finding only when the claim needs it.

### Institutional context

Run when a law, standard, regulator, platform rule, market structure, or event date does work in the design or the interpretation.

Check primary sources: statute, FASB or IASB material, SEC release, call-report dictionary, official platform documentation. Secondary descriptions are weaker. Report only mismatches that change measurement or timing. Record the source. If you cannot open it, **Cannot verify**.

### Pre-analysis and replication

Run when the manuscript names a registry, a pre-analysis plan, or a replication package, or when a planned-versus-reported gap is at issue.

Open the linked registry record. Compare planned sample, exclusions, arms, outcomes, and estimands with the paper. Deviations must be disclosed enough to separate confirmatory from exploratory work.

Do not hunt the web for an undisclosed plan. Do not turn a missing GitHub link into a finding unless the paper claims the package exists or the missing files block a material check.

### Literature

Check characterizations the paper uses for novelty, a contrasting mechanism, or a cited estimate. Verify the specific claim, not merely that the paper exists.

Working papers change. Note the version and date you opened. Prefer the author or publisher copy. If you cannot open the relevant version, **Cannot verify**.

Distinguish "this sentence overclaims relative to paper X" from "nothing like this exists," which requires proving absence.

### Formal theory

Run only when the paper states a proposition, lemma, or equilibrium result. Read the proof or appendix.

Check whether the result follows from the stated assumptions, including existence, uniqueness, boundary cases, and quantifiers. Do not ask for a more realistic model unless the paper's own claim fails.

This pass is validity. Isolated symbol typos belong to displayed specifications or editing notes.

### External validity and policy

Run when the paper generalizes beyond the sample or recommends a policy.

The limitation belongs in the report when the design makes the claim too broad: selected firms, one standard change, one platform, a lab stake. A generic "more countries would be nice" is exploratory.
