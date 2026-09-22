# C4 — Analysis of the result: an independent specificity axis (PWMs)

**Colab run:** 2026-09-22, 8.1 min on a Tesla T4. **New program:** there are no recorded values to compare. It ran
without errors on first use.
The run's own numbers are in `RESULTS_C4.md`, `metrics_C4.json` and `specificity_decision.json`. The tables are
`pwm_profiles.csv`, `specificity_cv.csv` and `atlas_rewiring.parquet`.

**Result in one line:** the pre-specified validation rule **failed**. The specificity axis is **not validated**,
so no rewiring claim is made from it. That is the honest outcome, and it closes Part C.

---

## 1. The question

Parts C1–C3 showed that SH3 **binding energy** cannot be learned from the one SH3 domain with ddPCA data (too
few positions). C3 concluded that the fix is **more domains**. C4 tries the one dataset that has many SH3
domains: **peptide-binding specificity profiles** (position weight matrices, PWMs) for human SH3 domains.

> From its sequence, can a model predict *which* peptides an SH3 domain prefers? If yes, the predicted change
> in that preference for a cancer variant would be an **independent** rewiring axis, not built from ESM scores
> like B3's binding axis.

**Design, fixed before the run:**
- **Target:** each PWM reduced to an information-weighted amino-acid preference profile (20 numbers).
- **Model:** ridge regression from the domain's ESM-2 embedding to that profile, in centred log-ratio space.
- **Test:** hold out **whole clusters of related domains** (≥ 40 % identity) together, so a domain is never predicted from a close relative.
- **Pre-specified rule:** validated only if **(1)** the 95 % CI of the median centred correlation is above 0 **and** **(2)** the model beats the *average SH3 profile* on significantly more domains (sign test p < 0.05).
- **Rewiring score for a variant:** Jensen–Shannon distance between the predicted profiles of the wild-type and the mutant domain.

---

## 2. The data

| | |
|---|---|
| PWMs | 154, all linked to a domain sequence |
| Distinct SH3 domain sequences | 115 |
| Clusters of related domains (≥ 40 % identity) | 52 |
| Identity of each domain to its nearest *training* domain | median 0.34 (max 0.40, by design) |

---

## 3. Result of the cross-validated test

Per held-out domain:
- **centred r:** correlation of the predicted and observed profile after removing the training average. This removes the proline preference that all SH3 domains share.
- **JS:** Jensen–Shannon distance to the observed profile. Lower is better.

| Predictor | Median centred r | Median JS distance |
|---|---|---|
| **Model** (ridge on ESM-2 embedding) | **+0.288** (95 % CI +0.218 to +0.337) | **0.212** |
| Average SH3 profile (no model) | — | **0.214** |
| Nearest related domain's profile | +0.119 | 0.310 |

| Comparison | Model wins (JS distance) |
|---|---|
| vs the average SH3 profile | **55 / 115** (sign test p = 1.0) |
| vs the nearest-neighbour profile | 85 / 115 |

**Against the rule:**
- **(1) CI of median centred r above 0:** met (+0.218 to +0.337).
- **(2) Beats the average profile on significantly more domains:** **failed.** The model wins on 55 of 115, *fewer than half*.
- **→ Not validated.**

**Interpretation:**
- **The model captures a little real signal.** After the shared proline preference is removed, its predicted deviations correlate positively with the observed ones (r about +0.29, CI above zero).
- **But the signal is too weak to matter.** Measured by how close the predicted profile is to the real one, the model is no better than predicting "the average SH3 domain" for every domain (JS 0.212 vs 0.214; wins 55/115). The shared SH3 preference explains almost everything the model gets right.
- **The model is much better than copying a relative's profile** (wins 85/115; JS 0.21 vs 0.31). At under 40 % identity, a relative's specificity is a poor guide, and even worse than the average.
- **Consequence:** at the level of individual domains, SH3 specificity cannot be predicted from sequence with this data and model well enough to beat the family average. A variant-level "rewiring" score built on it would mostly measure noise.

---

## 4. The two-axis map (shown, not claimed)

Because the axis failed validation, this section is **for completeness only**. No rewiring claim is made.

| Folding axis (B3) | Top-10 % rewiring score | Other | Total |
|---|---|---|---|
| Destabilising (fold interval ≥ 1) | 90 | 320 | 410 |
| Not destabilising | 599 | 5,875 | 6,474 |

| Check | Value |
|---|---|
| ρ, rewiring score vs predicted fold damage | **+0.356** |
| ρ, rewiring score vs zero-shot ESM score | −0.393 |
| Median rewiring score: interface positions vs elsewhere | 0.031 vs 0.027 (one-sided p = 7.6 × 10⁻²⁴) |

**Why these numbers do not rescue the axis:**
- **The rewiring score correlates with fold damage** (ρ +0.36) and with ESM (−0.39). It is not independent of "this substitution is bad in general". A likely reason is that substitutions which change the ESM embedding a lot move both predictions.
- **Interface positions do score higher, and the p-value is tiny, but the effect is small** (0.031 vs 0.027, about 15 %). With thousands of variants, even a trivial difference becomes "significant". Statistical significance is not validation.
- **The 599 "rewiring but not destabilising" variants** would be the rewiring candidates *if* the axis were valid. Without validation they are not reported as findings.

---

## 5. What this means for the thesis

- **Part C ends with an honest negative result on both routes:**
  1. SH3 binding **energies** cannot be learned: one domain, 56 positions, below the ~80-position threshold (C1–C3).
  2. SH3 binding **specificity** across 115 domains cannot be predicted better than the family average (C4).
- **The fold/rewiring separation for individual cancer variants therefore stays untested.** It is reported as a **data limit**, not as a finding either way.
- **The thesis's confident claims remain those of Part B:** loss of fold is predictable, specific to folding, and calibrated, with 410 confidently destabilising cancer variants.
- **What would change this:**
  - binding energies (ddPCA-type) for many SH3 domains on a common frame, to reach the position coverage found in C3; or
  - larger, more uniform specificity datasets.

---

## 6. Limitations

- **One model family (ridge on ESM-2 embeddings).** A different model might do better. The rule was fixed in advance precisely so that it could not be tuned after the fact.
- **PWMs summarise specificity for a peptide library** and depend on the experiment. They are not binding energies.
- **Profile collapse:** reducing a PWM to 20 information-weighted numbers loses position-specific detail.
- **The one-sided sign test returns p = 1.0** when the model wins on fewer than half the domains. It is not tested in the other direction.

---

## 7. Conclusion and next step

- **The independent specificity axis is not validated.** The model has weak real signal (centred r +0.29) but does not beat the average SH3 profile (55/115 wins).
- **No rewiring claim is made.** The two-axis map is shown only for completeness.
- **Part C's conclusion stands:** binding and rewiring for SH3 cancer variants cannot be predicted from current data. This is quantified (about 80 positions needed) and reported as a data limit.

**Next:** run `B5_cancer_biology` on CPU (about 3 min), then `B6_virtual_saturation_mutagenesis` (CPU, about 5 min).
