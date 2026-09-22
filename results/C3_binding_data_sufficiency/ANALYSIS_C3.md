# C3 — Analysis of the result: is the limit the number of measurements, or the number of positions?

**Colab run:** 2026-09-22, 53.3 min on a Tesla T4. **Verdict after the fix: REPRODUCED — 42 identical, 27 new (corrected procedure).**
The first run had 1 DIFF, a table-grouping error (Section 8). After the fix, a 0.1-min re-run (all steps
reloaded) gives the recorded value exactly.
The run's own numbers are in `RESULTS_C3.md`, `metrics_C3.json` and `comparison_C3.csv`. The data files are
`matched_budget.csv`, `diagnostic_grid.csv`, `learning_curve.csv`, `threshold_sweeps.csv`,
`position_sweep.csv` and `position_leverage.csv`.

---

## 1. The question

C2 found that binding is learnable within PSD95-PDZ3 (ρ about 0.37–0.40) but not within GRB2-SH3 (ρ about 0).
PDZ3 has **twice the measurements** (1,221 vs 619) **and 1.5× the positions** (84 vs 56). C3 separates the
two:

> Is GRB2-SH3 unlearnable because of **something about SH3 binding**, because there are **too few measurements**,
> or because there are **too few positions**? And would more mutagenesis of GRB2-SH3 fix it?

Everything is tested on PDZ3, the domain where binding *is* learnable, by removing data in controlled ways.

---

## 2. Step 1 — Matched budget: cut PDZ3 down to GRB2-SH3's data

PDZ3 was reduced to exactly GRB2-SH3's budget (56 positions, 619 measurements), in 20 random draws:

| Mode | Median ρ | 95 % range of draws | GRB2-SH3 (C2) | GRB2 inside the range? |
|---|---|---|---|---|
| Corrected | **−0.024** | −0.163 to +0.155 | −0.020 | yes |
| Original | **−0.023** | −0.195 to +0.175 | −0.030 | yes |

**Interpretation:**
- **With GRB2-SH3's amount of data, PDZ3 collapses to exactly GRB2-SH3's level** (ρ about −0.02).
- **So GRB2-SH3's failure needs no SH3-specific explanation.** A domain whose binding *is* learnable becomes unlearnable when given the same data. The limit is the data, not the biology of SH3 binding.
- The remaining question: which part of the data — measurements or positions?

---

## 3. Step 2 — Diagnostic grid: how fragile is the full-data result?

PDZ3 with all its data, varying the number of cross-validation folds and training epochs:

| Mode | 5 folds, 40 ep | 5 folds, 60 ep | 7 folds, 40 ep | 7 folds, 60 ep |
|---|---|---|---|---|
| Original | 0.080 | 0.082 | 0.387 | 0.387 |
| Corrected | 0.192 | 0.196 | 0.365 | 0.362 |

**Interpretation:**
- **Epochs do not matter** (40 vs 60 gives the same result).
- **The fold count matters a lot.** With 5 folds, each fold holds out about 17 of 84 positions, so every model trains on about 67. With 7 folds it holds out 12 and trains on about 72. Losing just 5 training positions drops ρ from about 0.37 to 0.08–0.19.
- **This is the first sign of a threshold.** PDZ3 sits *just* above the amount of position coverage it needs. A small reduction pushes it over the edge.
- **The corrected (shuffled) partition is less extreme** (0.19 vs 0.08 at 5 folds). Part of the original drop came from one unlucky fixed partition. The direction is the same.

---

## 4. Step 3 — Learning curve: both domains at matched budgets

Median ρ over 6 draws. Positions and measurements are reduced together:

| Budget (positions / measurements) | PDZ3 original | PDZ3 corrected | GRB2-SH3 original | GRB2-SH3 corrected |
|---|---|---|---|---|
| 25 / 200 | −0.063 | −0.107 | −0.002 | −0.056 |
| 35 / 350 | −0.109 | +0.010 | −0.065 | −0.068 |
| 45 / 500 | +0.004 | +0.039 | +0.026 | +0.011 |
| 56 / 619 | −0.032 | +0.017 | −0.001 | −0.036 |
| 70 / 850 | +0.078 | +0.003 | — | — |
| **84 / 1,221** | **+0.387** | **+0.362** | — | — |

**Interpretation:**
- **There is no gradual learning curve.** PDZ3 stays at about zero up to 70 positions / 850 measurements, then jumps to about 0.37 at the full 84 / 1,221.
- **This is a step, not a slope.** Fitting a smooth curve through it (as the recorded analysis did) is the wrong shape, which is why this table is marked superseded.
- **GRB2-SH3 stays at about zero at every budget it can reach,** matching PDZ3 at the same budgets.
- **This curve reduces positions and measurements together,** so it cannot say which one causes the step. Step 4 separates them.

---

## 5. Step 4 — The decisive test: remove measurements or remove positions?

Three sweeps on PDZ3, 114 runs per mode:
- **A — fold count only:** all data, 3–10 folds.
- **B — thin the measurements, keep all 84 positions:** 700–1,221 measurements.
- **C — remove positions at the same measurement budget:** the same totals as B, but fewer positions.

| Mode | A: fold count | **B: fewer measurements, all positions** | **C: fewer positions, same measurements** |
|---|---|---|---|
| Original | 0.356 | **0.357** | **0.076** |
| Corrected | 0.302 | **0.327** | **0.054** |

The largest disagreement between sweeps at the same training size is 0.38 (original) and 0.27 (corrected).

**Interpretation — this is the central result of Part C:**
- **Cutting measurements while keeping every position costs almost nothing.** B stays at about 0.33–0.36, the same as full data.
- **Cutting positions at the same number of measurements destroys the signal.** C falls to about 0.05–0.08.
- **So the limit is positional coverage, not the number of measurements.** At the same number of rows, *how the rows are spread over positions* decides whether binding is learnable.
- **Why this makes sense:** the model predicts binding at an **unseen position**. To do that, it must learn how binding depends on position context (burial, contact with the ligand, neighbouring residues). Many substitutions at the same few positions teach it about substitutions, not about positions. It needs many different positions.
- **Both partition modes agree.**

---

## 6. Step 5 — Position sweep: how many positions are needed?

PDZ3 reduced to each position count from 60 to 84, with 10 random subsets per count and shuffled partitions.
All data at the kept positions is used.

| Positions | Median ρ | Range over 10 subsets | p vs 60 positions |
|---|---|---|---|
| 60 | −0.014 | −0.207 to +0.263 | — |
| 62–74 | −0.070 to +0.013 | about −0.25 to +0.16 | 0.34–0.93 |
| **76** | **+0.113** | −0.009 to +0.191 | **0.007** |
| 78 | +0.116 | −0.009 to +0.266 | 0.006 |
| 80 | +0.208 | +0.036 to +0.317 | 0.001 |
| **82** | **+0.330** | **+0.287 to +0.380** | 9 × 10⁻⁵ |
| 84 | +0.322 | +0.281 to +0.427 | 9 × 10⁻⁵ |

**Interpretation:**
- **Below 76 positions there is no signal** (medians about 0, with no trend from 60 to 74).
- **At 76 positions predictability first appears** (significantly above 60: Mann–Whitney p = 0.007).
- **By 82 positions it is solid:** all 10 subsets are at ρ ≥ 0.29.
- **GRB2-SH3 has 56 positions,** 20 short of where predictability first appears and 26 short of where it is solid. An SH3 domain has only about 56–60 residues in total, so **no mutagenesis of a single SH3 domain can ever reach this coverage.** Even complete saturation mutagenesis would give at most about 60 positions.

**Honest scale of the number:** it is calibrated on one domain (PDZ3) with one ligand. The thesis should say
"**of the order of 80 positions**", not a precise cut-off.

---

## 7. Step 5b — Is it *which* positions, or *how many*?

Some position counts produced both successes (ρ > 0.25) and failures (ρ < 0.15) in different random subsets:
60, 78 and 80. The recorded analysis read this as "leverage": some special positions that decide success.

The enrichment table tests that directly. For every position, the ratio of successful to failed subsets that contain it
(smoothed: (successes + 1) / (failures + 1)) lies between **0.27 and 0.48**. That is a narrow band: **no position stands out as enriched
in successful subsets.** The controlling variable is the **count** of positions, not their identity.

---

## 8. The one DIFF, and its fix

| Quantity | This run | Recorded |
|---|---|---|
| original.lc_GRB2-SH3_45pos_median | 0.006 | 0.0255 |

**Cause.** At 45 positions, GRB2-SH3 sometimes has only 498 measurements instead of 500. The results table
grouped by *positions and measurements*, so the budget split into two rows:
- 498 measurements: 1 draw, ρ 0.046;
- 500 measurements: 5 draws, median 0.006.

The metric took the second row. The recorded value (0.0255) was the median over **all 6 draws**. The model runs
are the same; only the summary was split.

**Fix (in `tools/nb_C.py`):** the learning-curve table now groups by positions only, so each budget is one row
over all its draws. **Re-run result:** original 0.02554, identical to the recorded value; corrected 0.011.

---

## 9. Limitations

- **One learnable domain (PDZ3) calibrates the threshold.** Another domain or ligand could need somewhat more or fewer positions.
- **The number of positions is fixed by the protein.** The test cannot say what happens beyond 84.
- **The logistic fits (table 4b)** from the recorded analysis are kept for the record but superseded. Their apparent sharp step came partly from the unshuffled partition.

---

## 10. Conclusion and next step

- **GRB2-SH3's binding is not unlearnable because of SH3 biology.** PDZ3 given GRB2-SH3's data fails in exactly the same way.
- **The limit is positional coverage, not measurements.** Thinning measurements at all positions keeps ρ at about 0.33; removing positions at the same budget drops it to about 0.05.
- **Predictability needs about 76–82 distinct positions.** An SH3 domain has 56–60, so single-domain mutagenesis can never reach it.
- **The fix is more domains, not more mutations:** binding data from many SH3 domains, aligned on a common frame, would give the position coverage one domain cannot.

**Next:** run `B3_uncertainty_and_calls` on CPU (about 1 min). The runtime can be switched from T4 to CPU.
