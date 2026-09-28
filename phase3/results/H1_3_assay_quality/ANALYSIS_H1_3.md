# H1.3 — analysis

Run 28 September 2026, locally, seconds on CPU. Machine numbers in `metrics_H1_3.json`; sources and
methodology in `METHODS_H1_3.md`; the plan they were judged against is
`phase3/docs/preregistration/H1_3_assay_quality.md`, committed before the join existed.

**Nothing was re-predicted.** H1's per-domain correlations are read as published.

---

## The answer

**Assay quality does not explain H1's family ordering.**

| | main | SH3 | Δ | 95 % CI |
|---|---|---|---|---|
| Unmatched (H1) | 0.420 (35) | 0.623 (36) | **−0.203** | [−0.249, −0.120] |
| Matched on assay quality | 0.432 (31) | 0.619 (30) | **−0.187** | [−0.232, −0.098] |

Matching moves Δ by **0.015** — a third of the 0.05 threshold the pre-registration set as this
design's resolution, and a thirteenth of the gap itself. The verdict is Part 4's second row:
**`assay_quality_does_not_explain_it`**.

Matching cost almost nothing in power (31 against 30 domains, versus 35 and 36), so this is not a
case of an effect being hidden by a shrunken sample.

## Myb/SANT is the decisive case

The per-family assay quality is the number that settles it:

| Pfam | family | assay quality | median \|ρ\| |
|---|---|---|---|
| PF00595 | PDZ | **3.476** | 0.602 |
| **PF00249** | **Myb/SANT** | **2.535** | **0.507** |
| PF00018 | SH3 *(reference)* | 2.086 | 0.623 |
| PF00643 | B-box | 1.834 | 0.335 |
| PF00628 | PHD | 1.391 | 0.376 |

**Myb/SANT has better measurements than SH3 — 2.535 against 2.086 — and lower accuracy, 0.507 against
0.623.** A family cannot be underperforming because of noisy data when its data is less noisy than
the reference. One clean counterexample does more here than the matched comparison, and it is why
the matched Δ barely moved.

The variant-weighted arm figures H1 reported (main 1.863, SH3 2.199) pointed the other way. They were
misleading: weighting by variant count let PHD and B-box, which have many variants and poor
measurements, dominate the arm average. **Per domain, the main arm and SH3 overlap almost entirely.**
That was recorded in the pre-registration before this analysis ran, not discovered afterwards.

## Assay quality does matter — across domains, not across these families

**Q3: |ρ| and assay quality correlate at Spearman +0.629 (n = 102, p = 1.5 × 10⁻¹²).** That is strong,
and it is real.

It is also **partly mechanical**, and the write-up must say so: a domain with noisier measurements
has an attenuated correlation with *anything*, so some positive relationship is expected even if the
predictions were equally good everywhere. Its existence is not evidence of a problem; its size is
worth knowing, and it is why matching was the right design rather than ignoring the variable.

The two facts are consistent. Assay quality predicts accuracy **between domains**, and still does not
account for the difference **between these families**, because the families are not separated on that
axis in the way the arm-level averages implied.

## This qualifies H1's PDZ finding

| PDZ vs SH3 | Δ | 95 % CI |
|---|---|---|
| Unmatched (H1) | −0.021 | [−0.082, +0.027] |
| Matched | **−0.077** | [−0.172, +0.009] |

PDZ has by far the best measurements in the set (3.476 against SH3's 2.086). Restricted to the shared
band it keeps only 18 of 31 domains, its median falls from 0.602 to 0.541, and the gap to SH3 nearly
quadruples.

**The interval still includes zero, so H1's conclusion is not overturned** — and PDZ carried no
verdict in either file. But the honest reading changes: *PDZ matches SH3 and part of that parity is
its better measurements.* The length finding survives — a family 16 residues beyond anything in
training is still statistically indistinguishable from SH3 — but it should be quoted with the matched
figure beside the unmatched one, not the unmatched one alone.

## What H1.3 licenses, and what it does not

**Licensed.** *The accuracy deficit on the length-matched held-out families is not explained by
measurement quality. Matching the two arms on within-assay signal-to-noise moves the difference from
−0.203 to −0.187, and the family with the best measurements in the main arm — Myb/SANT, better than
SH3's — is also below SH3 in accuracy.*

**Not licensed.**

- **"Zinc coordination is the limit."** Part 5 of the pre-registration ruled this out in advance:
  eliminating assay quality does not promote the remaining named hypothesis. Myb/SANT binds no metal
  and is still 0.12 below SH3, so a third cause is possible and unnamed.
- **"The model is worse on these families."** That is the most natural reading, but H1's own verdict
  on the main arm was *inconclusive* at the −0.15 margin, and H1.3 does not change that verdict — it
  removes one explanation for it.
- **Anything from Q3 about causation.** The correlation is partly an artefact of attenuation.
- **PDZ's parity as a clean result.** See above.

## What would settle it

1. **A family that is length-matched, non-metal-binding, and has assay quality near SH3's.**
   Myb/SANT is the closest available and there is only one of it. The audit's `family_audit.csv` now
   needs a fourth criterion — assay quality — which was not among its three.
2. **A second assay on any held-out family**, which is the only thing that supplies a real noise
   ceiling and would let the E2 comparison be made properly.
3. **Attenuation correction.** Dividing |ρ| by an estimate of the measurement reliability per domain
   would separate the mechanical part of Q3 from the rest. It needs a reliability estimate the
   replicate σ can support only weakly, and it is a further post-hoc step.

## Effect on the project

H1 named two explanations and could separate neither. **One is now removed**, which is progress of
the kind that narrows rather than concludes: the main arm's deficit is a property of the predictions
or of something not yet named, and not of the measurements.

For the manuscript, the practical consequences are two. The PDZ figure should be quoted with its
matched value alongside. And the honest summary of H1 is unchanged in shape but firmer in one part:
**one unseen family matched SH3, three did not, length is not the reason, and measurement quality is
not the reason either.**

## Status

Complete as pre-registered. Post-hoc by construction, and labelled so wherever it is cited. The
pre-registration is unsigned.
