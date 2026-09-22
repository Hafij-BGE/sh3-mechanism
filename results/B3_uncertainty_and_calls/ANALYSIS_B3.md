# B3 — Analysis of the result: uncertainty, and a mechanism call for every cancer variant

**Colab run:** 2026-09-22, 0.2 min on CPU; re-run at 15:45 with the new tolerance: **REPRODUCED (7 identical, 1 within tolerance).** First run: **7 identical, 1 DIFF.** The DIFF (3 × 10⁻⁷ in a quantity
flagged "not a valid test") comes from tie-ordering, not from a changed result (Section 8). Its tolerance is
now set accordingly; nothing needs re-running.
The run's own numbers are in `RESULTS_B3.md`, `metrics_B3.json` and `comparison_B3.csv`. The tables are
`atlas_predictions.parquet` (read by B5, B6 and C4), `calibration_curve.csv`, `rejection_curve.csv` and
`stratified_coverage.csv`.

---

## 1. The question

B1 gives a predicted ΔΔG_fold for each of the 6,884 cancer variants. A point estimate alone is not enough to
call a variant destabilising: the model has an error of about 0.5 kcal/mol, and more for severe variants. B3:
1. puts a **90 % prediction interval** on every prediction, with a guarantee that it is honest (split-conformal);
2. calls a variant **destabilising only if the whole interval is above 1 kcal/mol** (lower bound ≥ 1);
3. adds the **binding axis**, which C2 decided must be zero-shot ESM-2 (the trained head has no signal);
4. assigns each variant one of four labels: tolerated, destabilising, rewiring, both.

---

## 2. The intervals are honest: conformal calibration

**Method.** Normalised split-conformal prediction. The interval half-width is q × (seed spread + ε). q is
chosen on one half of the held-out SH3 variants and checked on the other half, which the model has never
seen.

| Nominal coverage | q | **Empirical coverage** | Median half-width (kcal/mol) |
|---|---|---|---|
| 50 % | 2.363 | 50.7 % | 0.36 |
| 60 % | 2.997 | 60.2 % | 0.45 |
| 70 % | 3.820 | 70.1 % | 0.58 |
| 80 % | 4.910 | 79.9 % | 0.74 |
| **90 %** | **6.807** | **89.9 %** | **1.03** |
| 95 % | 8.771 | 95.2 % | 1.33 |

**Interpretation:**
- **The intervals do what they claim at every level.** A 90 % interval contains the true value 89.9 % of the time, and the same holds from 50 % to 95 %. The recorded q (6.807) and coverage (89.9 %) are reproduced exactly.
- **A 90 % interval is about ±1 kcal/mol wide** (median 1.03 on the validation half; 1.12 on the atlas). A variant needs a predicted ΔΔG of roughly 2 kcal/mol or more before its whole interval clears 1 kcal/mol.

---

## 3. Where the 90 % is met and where it is not (stratified coverage)

The conformal guarantee is **on average**, not for every subgroup. This table shows the subgroups.

**By predicted ΔΔG:**

| Predicted ΔΔG_fold | n | Coverage | Half-width |
|---|---|---|---|
| < 0 | 1,322 | 93.7 % | 0.95 |
| 0–1 | 6,490 | 91.2 % | 0.87 |
| 1–2 | 3,238 | 88.3 % | 1.20 |
| **> 2 kcal/mol** | 2,745 | **86.9 %** | 1.32 |

**By held-out domain (15 SH3 genes):** coverage ranges from **83.3 % (LYN)** to **95.0 % (FYN)**.
- Below 90 %: LYN 83.3, LASP1 83.9, HCK 84.6, BTK 85.8, PLCG1 88.6 and LCK 89.0.
- At about 90 % or above: SPTAN1 90.0, DOCK1 90.4, OBSCN 90.7, NPHP1 90.8, SORBS1 90.9, OSTF1 91.4, PTK6 93.3, TEC 93.9 and FYN 95.0.

**Interpretation:**
- **Coverage is slightly low for the most damaging predictions** (86.9 % above 2 kcal/mol). This is the same compression found in B1: severe variants are under-predicted, so their true values fall above the interval a little more often. **The practical effect is conservative.** The error is mostly on the "more damaging than predicted" side, so a destabilising call is unlikely to be a false alarm for this reason.
- **Coverage varies by domain, from 83 % to 95 %.** SPTAN1 alone is 5,049 of the 13,795 validation variants, so the global 90 % partly reflects SPTAN1. For some domains the true coverage is nearer 84 %. **The thesis should state the 90 % as an average,** with the domain range.
- **Burial cannot be used as a stratum,** because the held-out MegaScale variants carry no structure.

---

## 4. Why the old confidence filter was replaced

The recorded Stage 3 called a prediction "confident" when the five seeds agreed (SD < 0.5).

| | |
|---|---|
| Atlas variants passing the old filter | **99.94 %** |
| Correlation of seed spread with actual error | ρ **+0.304** |

**Rejection curve** (validation half, keeping the variants with the smallest seed spread):

| Kept (most confident) | n | ρ | MAE (kcal/mol) |
|---|---|---|---|
| 5 % | 689 | 0.655 | **0.27** |
| 10 % | 1,379 | 0.713 | 0.28 |
| 20 % | 2,759 | 0.751 | 0.31 |
| 50 % | 6,897 | 0.815 | 0.37 |
| 100 % | 13,795 | 0.843 | 0.49 |

**Interpretation:**
- **The old filter filtered nothing.** Almost every variant passed. Seeds agreeing means the training is reproducible, not that the prediction is right.
- **Seed spread carries some information about error:** the absolute error falls from 0.49 to 0.27 kcal/mol in the most confident 5 %.
- **ρ falls in that 5 %** (0.84 → 0.66), because confident predictions cluster in a narrow range of mostly neutral values. A narrow range lowers any correlation.
- **So the spread is useful for scaling an interval, but useless as a yes/no filter.** That is exactly how the conformal method uses it: as the *width*, calibrated by q.

---

## 5. The mechanism calls for the 6,884 cancer variants

**Rules:**
- **Destabilising axis:** the lower 90 % bound of ΔΔG_fold must be ≥ 1 kcal/mol.
- **Binding axis:** zero-shot ESM-2, rank-matched to the measured GRB2-SH3 ΔΔG_bind distribution. It is "high" if its lower bound, the rank-matched value minus a fixed spread, is ≥ 1 kcal/mol.

| Label | Variants | Share | Basis |
|---|---|---|---|
| Tolerated (no call) | 6,283 | 91.3 % | neither axis clears 1 kcal/mol |
| **Destabilising** | **297** | 4.3 % | fold interval fully above 1 kcal/mol |
| Both | 113 | 1.6 % | fold call **plus** high ESM binding axis |
| Rewiring | 191 | 2.8 % | high ESM binding axis only |

All four counts are identical to the recorded run.

**Interpretation:**
- **410 variants (297 + 113, 6.0 % of the atlas) are called destabilising with error control.** These are the robust loss-of-fold candidates of the thesis.
- **Error control cuts the calls by more than 5×.** On point estimates alone, 2,220 variants would be called (predicted ΔΔG ≥ 1). Requiring the whole interval above 1 kcal/mol keeps 410. The other 1,810 are *possibly* destabilising but not confidently.
- **"Tolerated" means "not called", not "proven harmless".** Many of the 6,283 have wide intervals that include both neutral and damaging values.
- **"Rewiring" (191) and the binding half of "both" (113) rest on zero-shot ESM-2,** which Part C showed is a weak binding predictor: ρ −0.13 on GRB2-SH3. The binding band is a fixed width, not a validated interval. These labels are **reported as hypotheses, not claimed.** The thesis's confident claim is the destabilising axis.
- **Destabilising calls are conservative** (B1 compression, Section 3). The true number of fold-breaking cancer variants is likely *higher* than 410, not lower.

---

## 6. The axis correlation is not a test

ρ between the predicted fold axis and the predicted binding axis is **+0.675**. This is **not** evidence
about whether separate "rewiring" variants exist. Both axes come from ESM-2 by construction: the fold head is
built on ESM-2 features, and the binding axis *is* ESM-2. They are bound to correlate. The notebook records it
with `axis_correlation_is_valid_test = False`, and no claim is made from it.

---

## 7. Limitations

- **Coverage is guaranteed on average** over the held-out SH3 domains. Per domain it ranges from 83 % to 95 %, and it is slightly low for severe predictions.
- **The intervals are calibrated on MegaScale held-out SH3 domains** (proteolysis assay) and applied to human cancer variants in the same family, scored on the isolated domain sequence.
- **The binding axis is weak** (Part C). Rewiring labels are hypotheses.
- **The 1 kcal/mol threshold is a convention** for a meaningful destabilisation, not derived from data.

---

## 8. The one DIFF

| Quantity | This run | Recorded | Difference |
|---|---|---|---|
| axis_rank_correlation | 0.6745674 | 0.6745677 | 3.4 × 10⁻⁷ |

**Cause.** The binding axis ranks variants by ESM score using `argsort`. Variants with *exactly equal* ESM
scores (ties) are placed in an order that the sorting algorithm does not fix. It can differ between machines
and library builds; this run was on a Colab CPU runtime. That slightly reshuffles tied variants' rank-matched
values, which moves the correlation in the 7th decimal. **All mechanism counts are identical,** so no call
changed.

**Action.** No re-run. The recorded tolerance for this one quantity was 10⁻⁹, far tighter than float
tie-ordering allows. It is now 10⁻⁶ in `reference/expected_values.json`, with the reason written next to it.
The quantity is also flagged "not a valid test" (Section 6). Re-uploading `reference/expected_values.json` is
optional; it affects only how this line is labelled in future runs.

---

## 9. Conclusion and next step

- **The 90 % intervals are honest on average** (89.9 % coverage; calibrated from 50 % to 95 %). Coverage is slightly low for severe predictions and for some domains.
- **410 cancer variants (6 %) are confidently destabilising.** That is 5× fewer than point estimates suggest, and still conservative.
- **Binding-based labels (rewiring, both) are hypotheses** on a weak ESM axis. The thesis claims only the fold axis.

**Next:** run `C4_specificity_axis` on a T4 GPU (about 10 min). Then run `B5_cancer_biology` and
`B6_virtual_saturation_mutagenesis` on CPU.
