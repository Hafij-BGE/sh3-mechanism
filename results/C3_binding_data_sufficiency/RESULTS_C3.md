# C3 — Binding data sufficiency

*Generated automatically by the notebook on 2026-09-22T14:57:30 (0.1 min). Every number below comes from this run; nothing is typed by hand.*

## Summary

- Matched budget: PSD95-PDZ3 cut to GRB2-SH3's data falls to median ρ -0.024 (corrected), -0.023 (original).
- Keeping all positions while cutting rows costs almost nothing; cutting positions at the same row budget collapses it: corrected: B +0.327 vs C +0.054, original: B +0.357 vs C +0.076.
- Predictability appears at about 76 positions (solid by 82); GRB2-SH3 has 56.
- Single-domain ddPCA cannot supply enough positions for an SH3 domain (56–60 residues): the fix is more domains, not more mutations. The number is calibrated on one domain — quote "of the order of 80", not a precise cut.

**Check against the recorded run: REPRODUCED** (42 identical, 27 new (corrected procedure))

## 1. Matched budget

PSD95-PDZ3 at 56 positions / 619 measurements, 20 draws, against GRB2-SH3 (C2).

| mode | median | ci_lo | ci_hi | draws | grb2_median | covers_grb2 |
|---|---|---|---|---|---|---|
| corrected | -0.024 | -0.163 | 0.155 | 20 | -0.020 | True |
| original | -0.023 | -0.195 | 0.175 | 20 | -0.030 | True |

## 2. Diagnostic grid (PSD95-PDZ3, full data)

A result that swings with the fold count is fragile.

| mode | n_splits | epochs | median_rho |
|---|---|---|---|
| corrected | 5 | 40 | 0.192 |
| corrected | 5 | 60 | 0.196 |
| corrected | 7 | 40 | 0.365 |
| corrected | 7 | 60 | 0.362 |
| original | 5 | 40 | 0.080 |
| original | 5 | 60 | 0.082 |
| original | 7 | 40 | 0.387 |
| original | 7 | 60 | 0.387 |

## 3. Learning curve

Superseded as a model by steps 4–5: a log-linear fit through a step is the wrong shape.

| mode | domain | n_pos | n | median | min | max | size |
|---|---|---|---|---|---|---|---|
| corrected | GRB2-SH3 | 25 | 200 | -0.056 | -0.094 | 0.226 | 6 |
| corrected | GRB2-SH3 | 35 | 350 | -0.068 | -0.234 | 0.156 | 6 |
| corrected | GRB2-SH3 | 45 | 500 | 0.011 | -0.164 | 0.110 | 6 |
| corrected | GRB2-SH3 | 56 | 619 | -0.036 | -0.107 | 0.206 | 6 |
| corrected | PSD95-PDZ3 | 25 | 200 | -0.107 | -0.274 | 0.059 | 6 |
| corrected | PSD95-PDZ3 | 35 | 350 | 0.010 | -0.235 | 0.076 | 6 |
| corrected | PSD95-PDZ3 | 45 | 500 | 0.039 | 0.006 | 0.113 | 6 |
| corrected | PSD95-PDZ3 | 56 | 619 | 0.017 | -0.085 | 0.174 | 6 |
| corrected | PSD95-PDZ3 | 70 | 850 | 0.003 | -0.142 | 0.097 | 6 |
| corrected | PSD95-PDZ3 | 84 | 1221 | 0.362 | 0.314 | 0.405 | 6 |
| original | GRB2-SH3 | 25 | 200 | -0.002 | -0.172 | 0.208 | 6 |
| original | GRB2-SH3 | 35 | 350 | -0.065 | -0.120 | 0.082 | 6 |
| original | GRB2-SH3 | 45 | 500 | 0.026 | -0.080 | 0.100 | 6 |
| original | GRB2-SH3 | 56 | 619 | -0.001 | -0.102 | 0.195 | 6 |
| original | PSD95-PDZ3 | 25 | 200 | -0.063 | -0.132 | 0.097 | 6 |
| original | PSD95-PDZ3 | 35 | 350 | -0.109 | -0.156 | 0.132 | 6 |
| original | PSD95-PDZ3 | 45 | 500 | 0.004 | -0.054 | 0.107 | 6 |
| original | PSD95-PDZ3 | 56 | 619 | -0.032 | -0.219 | 0.074 | 6 |
| original | PSD95-PDZ3 | 70 | 850 | 0.078 | -0.067 | 0.107 | 6 |
| original | PSD95-PDZ3 | 84 | 1221 | 0.387 | 0.362 | 0.414 | 6 |

## 4. Three sweeps

Maximum disagreement between sweeps at a shared training size: {'corrected': 0.26706259086743017, 'original': 0.37709277716881484}. B keeps all positions and holds its accuracy; C removes positions at the same row budget and loses it.

| mode | sweep | median | runs |
|---|---|---|---|
| corrected | A_folds | 0.302 | 42 |
| corrected | B_thin | 0.327 | 36 |
| corrected | C_fewpos | 0.054 | 36 |
| original | A_folds | 0.356 | 42 |
| original | B_thin | 0.357 | 36 |
| original | C_fewpos | 0.076 | 36 |

## 4b. Logistic fits (superseded by step 5)

Kept for the record; the apparent sharp step came from the unshuffled partition.

| mode | fit | plateau | steepness | midpoint_rows |
|---|---|---|---|---|
| corrected | all sweeps | 1 | 5.25 | 1.39e+03 |
| corrected | A only | 0.431 | 54.8 | 842 |
| original | all sweeps | 1 | 6.1 | 1.28e+03 |
| original | A only | 0.387 | 300 | 838 |

## 5. Position sweep (shuffled partitions)

First count significantly above 60 positions (Mann–Whitney, p < 0.05): **76**. GRB2-SH3 has 56 positions in total.

| target_pos | median_x | min | max | size | median_y | p_vs_60 |
|---|---|---|---|---|---|---|
| 60 | -0.0141 | -0.207 | 0.263 | 10 |  |  |
| 62 | -0.00388 | -0.151 | 0.153 | 10 | -0.00388 | 0.367 |
| 64 | -0.008 | -0.219 | 0.038 | 10 | -0.008 | 0.515 |
| 66 | -0.0701 | -0.119 | 0.0355 | 10 | -0.0701 | 0.93 |
| 68 | 0.0126 | -0.254 | 0.164 | 10 | 0.0126 | 0.339 |
| 70 | -0.0262 | -0.205 | 0.113 | 10 | -0.0262 | 0.688 |
| 72 | 0.00253 | -0.0729 | 0.149 | 10 | 0.00253 | 0.425 |
| 74 | 0.00582 | -0.113 | 0.139 | 10 | 0.00582 | 0.367 |
| 76 | 0.113 | -0.00891 | 0.191 | 10 | 0.113 | 0.00701 |
| 78 | 0.116 | -0.00883 | 0.266 | 10 | 0.116 | 0.00566 |
| 80 | 0.208 | 0.036 | 0.317 | 10 | 0.208 | 0.00141 |
| 82 | 0.33 | 0.287 | 0.38 | 10 | 0.33 | 9.13e-05 |
| 84 | 0.322 | 0.281 | 0.427 | 10 | 0.322 | 9.13e-05 |

## 5b. Is it which positions, or how many?

Counts where both successes (ρ > 0.25) and failures (ρ < 0.15) occur: [60, 78, 80]. The original notebook read any overlap as 'leverage'. The enrichment table says otherwise: every position scores 0.27–0.48, i.e. the base rate of successes to failures. No position carries the signal; the controlling variable is the **count**.

## All quantities and their check

| quantity | this_run | recorded | status |
|---|---|---|---|
| corrected.matched_median_rho | -0.02365 |  | new (corrected procedure) |
| corrected.matched_ci_lo | -0.1628 |  | new (corrected procedure) |
| corrected.matched_ci_hi | 0.1548 |  | new (corrected procedure) |
| corrected.matched_draws | 20 |  | new (corrected procedure) |
| corrected.matched_covers_grb2 | True |  | new (corrected procedure) |
| original.matched_median_rho | -0.02296 | -0.02296 | identical |
| original.matched_ci_lo | -0.1946 | -0.1946 | identical |
| original.matched_ci_hi | 0.1754 | 0.1754 | identical |
| original.matched_draws | 20 | 20 | identical |
| original.matched_covers_grb2 | True |  |  |
| corrected.diag_k5_ep40_median | 0.1917 |  | new (corrected procedure) |
| corrected.diag_k5_ep60_median | 0.1964 |  | new (corrected procedure) |
| corrected.diag_k7_ep40_median | 0.3646 |  | new (corrected procedure) |
| corrected.diag_k7_ep60_median | 0.3615 |  | new (corrected procedure) |
| original.diag_k5_ep40_median | 0.07951 | 0.07951 | identical |
| original.diag_k5_ep60_median | 0.08159 | 0.08159 | identical |
| original.diag_k7_ep40_median | 0.3867 | 0.3867 | identical |
| original.diag_k7_ep60_median | 0.3873 | 0.3873 | identical |
| corrected.lc_GRB2-SH3_25pos_median | -0.05588 |  | new (corrected procedure) |
| corrected.lc_GRB2-SH3_35pos_median | -0.06776 |  | new (corrected procedure) |
| corrected.lc_GRB2-SH3_45pos_median | 0.01105 |  | new (corrected procedure) |
| corrected.lc_GRB2-SH3_56pos_median | -0.03632 |  | new (corrected procedure) |
| corrected.lc_PSD95-PDZ3_25pos_median | -0.1068 |  | new (corrected procedure) |
| corrected.lc_PSD95-PDZ3_35pos_median | 0.009584 |  | new (corrected procedure) |
| corrected.lc_PSD95-PDZ3_45pos_median | 0.03934 |  | new (corrected procedure) |
| corrected.lc_PSD95-PDZ3_56pos_median | 0.01728 |  | new (corrected procedure) |
| corrected.lc_PSD95-PDZ3_70pos_median | 0.003285 |  | new (corrected procedure) |
| corrected.lc_PSD95-PDZ3_84pos_median | 0.3615 |  | new (corrected procedure) |
| original.lc_GRB2-SH3_25pos_median | -0.002275 | -0.002275 | identical |
| original.lc_GRB2-SH3_35pos_median | -0.06522 | -0.06522 | identical |
| original.lc_GRB2-SH3_45pos_median | 0.02554 | 0.02554 | identical |
| original.lc_GRB2-SH3_56pos_median | -0.0009976 | -0.0009976 | identical |
| original.lc_PSD95-PDZ3_25pos_median | -0.06296 | -0.06296 | identical |
| original.lc_PSD95-PDZ3_35pos_median | -0.1095 | -0.1095 | identical |
| original.lc_PSD95-PDZ3_45pos_median | 0.003719 | 0.003719 | identical |
| original.lc_PSD95-PDZ3_56pos_median | -0.03198 | -0.03198 | identical |
| original.lc_PSD95-PDZ3_70pos_median | 0.07793 | 0.07793 | identical |
| original.lc_PSD95-PDZ3_84pos_median | 0.3873 | 0.3873 | identical |
| corrected.sweep_A_folds_median | 0.3015 |  | new (corrected procedure) |
| corrected.sweep_A_folds_runs | 42 |  | new (corrected procedure) |
| corrected.sweep_B_thin_median | 0.3268 |  | new (corrected procedure) |
| corrected.sweep_B_thin_runs | 36 |  | new (corrected procedure) |
| corrected.sweep_C_fewpos_median | 0.05424 |  | new (corrected procedure) |
| corrected.sweep_C_fewpos_runs | 36 |  | new (corrected procedure) |
| original.sweep_A_folds_median | 0.356 | 0.356 | identical |
| original.sweep_A_folds_runs | 42 | 42 | identical |
| original.sweep_B_thin_median | 0.3571 | 0.3571 | identical |
| original.sweep_B_thin_runs | 36 | 36 | identical |
| original.sweep_C_fewpos_median | 0.07586 | 0.07586 | identical |
| original.sweep_C_fewpos_runs | 36 | 36 | identical |
| original.sweep_max_gap | 0.3771 | 0.3771 | identical |
| original.sweep_runs | 114 | 114 | identical |
| corrected.sweep_max_gap | 0.2671 |  | new (corrected procedure) |
| corrected.sweep_runs | 114 |  | new (corrected procedure) |
| position_sweep_60_median | -0.01407 | -0.01407 | identical |
| position_sweep_62_median | -0.003876 | -0.003876 | identical |
| position_sweep_64_median | -0.008004 | -0.008004 | identical |
| position_sweep_66_median | -0.07006 | -0.07006 | identical |
| position_sweep_68_median | 0.01258 | 0.01258 | identical |
| position_sweep_70_median | -0.02621 | -0.02621 | identical |
| position_sweep_72_median | 0.002527 | 0.002527 | identical |
| position_sweep_74_median | 0.005815 | 0.005815 | identical |
| position_sweep_76_median | 0.1128 | 0.1128 | identical |
| position_sweep_78_median | 0.1161 | 0.1161 | identical |
| position_sweep_80_median | 0.2077 | 0.2077 | identical |
| position_sweep_82_median | 0.3296 | 0.3296 | identical |
| position_sweep_84_median | 0.3224 | 0.3224 | identical |
| position_sweep_runs | 130 | 130 | identical |
| crossing_positions | 76 | 76 | identical |
| grb2_positions | 56 | 56 | identical |
| success_failure_share_counts | 3 |  |  |
| position_enrichment_max | 0.4808 |  |  |

## Environment

| python | numpy | pandas | scipy | sklearn | transformers | torch | gpu |
|---|---|---|---|---|---|---|---|
| 3.13.15 | 2.1.3 | 2.2.3 | 1.16.3 | 1.6.1 | 5.16.1 | 2.11.0+cu128 | Tesla T4 |
