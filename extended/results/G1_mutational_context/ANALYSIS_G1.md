# G1 — analysis

Run 28 September 2026, on two machines independently. Machine numbers in
`metrics_G1a.json`, `metrics_G1b.json` and `RESULTS_G1_comparison.md`; the plan they were judged
against is `docs/preregistration/G1.md`, committed before the notebooks existed, signed off in
Part 13.

---

## The result

**The cancer-variant depletion does not survive a trinucleotide-aware null. Both spectra agree.**

| arm | null median | observed | gap | p | α | verdict |
|---|---|---|---|---|---|---|
| 1 — observed spectrum | 0.0604 | 0.0596 | **+0.08 pp** | 0.401 | 0.0125 | **vanishes** |
| 2 — COSMIC SBS1+SBS5 | 0.0558 | 0.0596 | −0.39 pp | 0.918 | 0.0125 | **vanishes** |

No primary spectrum was named before the run, so Part 9.3's co-primary rule applied and both arms
took α = 0.0125. It made no difference: both p-values are more than thirty times the threshold, so
either arm as primary at α = 0.025 returns the same verdict.

Per Part 4, this is the second of three outcomes fixed in advance: *consistent with mutational bias
alone → the frozen claim is withdrawn.* **Withdrawn, not weakened.**

## Where B6's 3.25 points went

This is the substance of G1, and the order matters.

| step | null rate | change | p at that step |
|---|---|---|---|
| B6 published — amino-acid-pair reachability | 0.0923 | — | 0.001 (B6) |
| 3a — codon reachability | 0.0860 | −0.64 pp | **0.0001** |
| 3b — + reachability multiplicity | 0.0788 | −0.71 pp | **0.0001** |
| 1 — + trinucleotide context | 0.0604 | −1.84 pp | **0.401** |
| observed | 0.0596 | | |

**The depletion survives both reachability corrections at p = 0.0001. Trinucleotide context alone
removes it.**

That distinction is worth insisting on. Along the way G1 found two genuine defects in B6's null, and
it would be easy to present the result as the sum of three bookkeeping fixes. It is not. Had the
corrections stopped at 3b, the depletion would still have been significant and B6's conclusion would
have stood. What overturns it is exactly the one thing B6 said it could not do:

> "mutational context was not modelled, and a trinucleotide-aware null is needed before claiming
> selection."

B6 named the two candidate explanations — weak purifying selection, or mutational bias — and stated
that its own test could not separate them. The separation has now been made, and it came down on
mutational bias.

## The null is not a wide net that the observation happened to fall through

A null result is only informative if the test could have seen the effect. Part 5 fixed the power
claim before the run, from *n* and B6's rate alone, and the run bears it out almost exactly:

| | |
|---|---|
| Pre-registered binomial SD | 0.00296 |
| Observed Monte-Carlo SD | **0.00295** |
| Smallest gap detectable at α = 0.0125 | **0.66 pp** |
| Gap observed | **+0.08 pp** |
| Null 95 % interval | 0.0548 – 0.0663 |

Part 5 said that if the empirical SD exceeded the binomial approximation by more than a factor of
two, the power claim would be restated. It did not; it matched to three decimal places, so the claim
stands as written.

**The observed rate sits in the middle of the null distribution, and the residual gap is roughly an
eighth of what the test could have resolved.** This is not a failure to detect. There is nothing
there to detect.

That is the contrast with E1, where the honest verdict on the same objection was *underpowered*:
35 germline variants against a test that needed hundreds. G1 has 6,456.

## Why two spectra that disagree about the mutational process still agree about the answer

The two spectra are genuinely different, and the cosine similarity says so: **0.688**.

| | observed atlas | COSMIC SBS1+SBS5 |
|---|---|---|
| C>T at CpG | **19.3 %** | **47.2 %** |
| all C>T | 47.1 % | — |

COSMIC's clock-like pair is dominated by CpG deamination to a degree the atlas is not. That is a real
mismatch — SBS1+SBS5 assume clock-like processes dominate, and across an atlas aggregating many
tumour types they evidently do not. So arm 2 weights the null differently enough to push it *below*
the observed rate (0.0558 against 0.0596), which is why its p-value is 0.918 rather than merely
non-significant.

**The two arms disagree about the mutational process and still agree about the verdict.** That is
the outcome Part 9.4 called robustness, and it settles the design's one admitted weakness: arm 1's
spectrum is estimated from the variants under test, so it is not independent of them. An externally
fixed spectrum, fitted from nothing in this project and demonstrably a poor fit to this data,
reaches the same conclusion. The non-independence is moot.

Judged as Part 9.4 required — on fit and robustness, never on which p-value is smaller — arm 1 is
the better description of this atlas and arm 2 is the stronger evidence that the answer does not
depend on that description.

## Two corrections to B6's null, which stand on their own

Neither changes G1's verdict. Both are defects in a published null model, found by a control written
before any of it was known, and both would apply to any reuse of B6's reachability machinery.

### 1. `snv_reachable` is amino-acid-level, and mutation is codon-level

B6 asks whether a substitution is reachable by one base change from **some** codon of the wild-type
residue. What can occur at a position is whatever is reachable from **the codon that is there**.
115,742 of B6's 150,040 reachable substitutions (77.1 %) survive that distinction.

The shortfall is a property of the amino-acid pair, not of our coverage:

| pair | observed | genetic code | |
|---|---|---|---|
| S→W | 0.07 | 0.17 | only `TCG` reaches `TGG` |
| L→W | 0.14 | 0.17 | only `TTG` reaches `TGG` |
| S→T | 1.00 | 1.00 | every Ser codon reaches Thr |
| L→V | 1.00 | 1.00 | every Leu codon reaches Val |

Across the 150 pairs with *n* ≥ 100, correlation with the pure genetic-code prediction is
**r = +0.955**, mean absolute deviation 0.05, and there is **no pair where the code says unreachable
and any were found**. The residuals go the way codon *usage* predicts — V→M is 0.555 observed
against 0.25 unweighted, because `GTG` is the dominant Val codon and is the one that reaches `ATG`.

What B6 over-counts is more damaging than what it keeps (0.112 against 0.086), so its expected rate
is inflated by **0.60 pp** by substitutions that cannot arise at those positions.

### 2. Reachability multiplicity

One amino-acid substitution can be reached by more than one base change, each with its own context.
Drawing at the amino-acid level treats those as one candidate; drawing at the mutation level treats
them as several, which is what mutation actually does. That is worth a further **−0.71 pp**.

| base changes reaching one substitution | substitutions |
|---|---|
| 1 | 88,082 |
| 2 | 21,114 |
| 3 | 3,959 |
| 4+ | 2,587 |

The tail above 4 is not all real: about 0.8 % of substitutions map to five or more genomic positions,
which exceeds what one codon can support and points to gene-symbol collisions or paralogous
transcripts in dbNSFP. At that share it cannot move the null, but it is not a clean number and is
reported rather than smoothed.

## What made this result trustworthy rather than merely obtained

The control did the work. It was written to answer "does our code reproduce B6?", it failed, and
investigating the failure — rather than adjusting the tolerance — is what produced both corrections
above and, eventually, the verdict.

Three things had to be fixed before the arms could run at all, and each produced a small, plausible,
internally consistent result that would have passed unexamined:

| defect | what it looked like |
|---|---|
| B6's `pos` is **domain-relative**, not a protein position | 187 of 6,456 observed variants "matched" — the 147 whose domains start at residue 1, plus coincidences |
| the pool came from X1's in-domain parquet, filtered on a **different transcript** | a pool 43 % smaller than it should be |
| matching the UniProt **accession** admits a different isoform | 23.7 % of rows on a position whose residue disagrees with the atlas, all-or-nothing per gene |

The first was caught by the eligibility floor four steps downstream; the second and third only by the
control refusing to reproduce a published number. **`build_context` now asserts join retention
directly**, which is X0's rule ("assert `len(out) == n` after every merge") applied where it should
have been from the start.

The pre-registration is the other half. α, the direction, the three outcome labels and the
1.63 pp boundary between *survives* and *shrinks but survives* were all fixed and committed before
either notebook ran — and the notebook **reads the committed file at run time** to set its own
threshold, so the choice could not be made afterwards. A result of +0.08 pp at p = 0.401 leaves no
room for interpretation, but a result of, say, 1.2 pp at p = 0.01 would have, and the rule for it
already existed.

## What G1 licenses as a claim, and what it does not

**Licensed.** *Observed SH3 cancer variants are not depleted of predicted fold-breaking
substitutions once the background is matched to trinucleotide context. The depletion reported by the
frozen run (5.93 % against 9.18 % expected) is accounted for by the mutational process: the residual
after context matching is +0.08 pp, p = 0.40, against a test able to resolve 0.66 pp. Two
independently specified spectra agree.*

**Not licensed.**

- "There is no purifying selection on SH3 domains in cancer." G1 tests one signal — the fraction of
  variants called destabilising by one predictor at one threshold — in 310 domains. Absence of this
  effect is not absence of selection.
- Anything about *positive* selection. The direction was declared in advance and only one was
  tested.
- Any claim that B6 was careless. B6 stated the limitation itself and named the test that would
  resolve it. G1 is that test, not a rebuttal.

**Admitted limitations.**

- **The pool is codon-aware where B6's was not, so the two are not the same test.** Both rates are
  reported wherever the depletion is quoted.
- **A context-matched null removes mutational bias, not every non-selective process.** Replication
  timing, chromatin state and sequencing coverage are not modelled. What the result licenses is that
  *context* explains the depletion, not that nothing else could have.
- **5.9 % of pool base changes did not join to B6** (9,668 of 164,376). The join is constructed so
  that gene, position and wild-type residue agree by definition, and B6 holds all 19 non-wildtype
  standard residues at every position it covers, so the drop can only come from `mut_aa` — dbNSFP's
  `X` for stop-gain and readthrough, which is not missense. **This is a deduction from the code, not
  a measurement.** `build_context` now records `pool_drop_reason_mut_aa`; the next run states it as
  fact, and Part 13 commits to amending the sign-off and re-running if it is anything else.
- **6.2 % of the atlas is excluded** for want of an unambiguous coordinate, 428 of 6,884.

## Effect on the project

**Objection 2 is closed, against us.** It was the last of the four standing objections and the only
frozen claim with no independent support; it now has independent evidence pointing the other way.

`OUTCOMES.md`, `MANUSCRIPT.md` and `ANALYSIS_B6.md` all described it as *untested*. They are updated
to *tested, did not survive*. The frozen run itself is untouched — nothing was re-run or re-fitted,
and 187/187 recorded values still reproduce.

The honest summary of the extended phase changes shape. Three objections moved in the model's
favour; the fourth moved against it. **That is a better position to submit from than four open
questions**, and considerably better than a headline that a reviewer would have dismantled — a
trinucleotide-aware null is the first thing anyone would have asked for, and B6 said so itself.

## Status

Complete. Both arms run, signed off in `docs/preregistration/G1.md` Part 13, reproduced independently
on two machines against two dbNSFP releases agreeing to every digit. One caveat instrumented and
open.
