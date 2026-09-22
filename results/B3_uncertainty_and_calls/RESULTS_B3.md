# B3 — Uncertainty and mechanism calls

*Generated automatically by the notebook on 2026-09-22T15:45:06 (0.0 min). Every number below comes from this run; nothing is typed by hand.*

## Summary

- Conformal q90 6.807; empirical coverage 89.9% against a 90% target.
- 297 destabilising, 113 both, 191 rewiring, 6,283 tolerated — 2,220 point-estimate calls reduced to 410 under error control.
- The binding axis is rank-matched zero-shot ESM-2 (Part C); no binding claim is made.

**Check against the recorded run: REPRODUCED** (7 identical, 1 within tolerance)

## Mechanism calls

Destabilising = lower interval bound ≥ 1 kcal/mol. "Rewiring" rests on rank-matched ESM-2 and is reported, not claimed.

| mechanism | variants |
|---|---|
| tolerated | 6283 |
| destabilising | 297 |
| rewiring | 191 |
| both | 113 |

## Calibration curve (validation half)

Nominal against empirical coverage.

| nominal | quantile | empirical | median_halfwidth |
|---|---|---|---|
| 0.500 | 2.363 | 0.507 | 0.357 |
| 0.600 | 2.997 | 0.602 | 0.453 |
| 0.700 | 3.820 | 0.701 | 0.578 |
| 0.800 | 4.910 | 0.799 | 0.743 |
| 0.900 | 6.807 | 0.899 | 1.029 |
| 0.950 | 8.771 | 0.952 | 1.326 |

## Rejection curve (validation half)

Accuracy of the most confident predictions, ranked by ensemble SD.

| kept_most_confident | n | rho | mae |
|---|---|---|---|
| 5% | 689 | 0.655 | 0.266 |
| 10% | 1379 | 0.713 | 0.275 |
| 20% | 2759 | 0.751 | 0.310 |
| 50% | 6897 | 0.815 | 0.374 |
| 100% | 13795 | 0.843 | 0.491 |

## Stratified coverage (validation half)

The 90% target is global; this shows where it is met and where not. Burial cannot be used as a stratum here: the held-out MegaScale variants carry no structure.

| by | stratum | n | coverage | median_halfwidth |
|---|---|---|---|---|
| predicted ΔΔG | <0 | 1322 | 0.937 | 0.954 |
| predicted ΔΔG | 0-1 | 6490 | 0.912 | 0.869 |
| predicted ΔΔG | 1-2 | 3238 | 0.883 | 1.202 |
| predicted ΔΔG | >2 kcal/mol | 2745 | 0.869 | 1.321 |
| domain (gene) | BTK | 549 | 0.858 | 1.146 |
| domain (gene) | DOCK1 | 592 | 0.904 | 1.158 |
| domain (gene) | FYN | 1068 | 0.950 | 0.867 |
| domain (gene) | HCK | 538 | 0.846 | 1.204 |
| domain (gene) | LASP1 | 515 | 0.839 | 1.129 |
| domain (gene) | LCK | 482 | 0.890 | 1.152 |
| domain (gene) | LYN | 508 | 0.833 | 1.100 |
| domain (gene) | NPHP1 | 1124 | 0.908 | 1.197 |
| domain (gene) | OBSCN | 592 | 0.907 | 1.204 |
| domain (gene) | OSTF1 | 513 | 0.914 | 1.126 |
| domain (gene) | PLCG1 | 542 | 0.886 | 1.205 |
| domain (gene) | PTK6 | 564 | 0.933 | 1.144 |
| domain (gene) | SORBS1 | 634 | 0.909 | 1.138 |
| domain (gene) | SPTAN1 | 5049 | 0.900 | 0.904 |
| domain (gene) | TEC | 525 | 0.939 | 1.134 |

## Why the old confidence filter was dropped

The original Stage 3 called a prediction confident when the five seeds agreed (SD < 0.5). Seed spread correlates only ρ +0.304 with the actual error, and 99.9% of atlas variants pass it: agreement between seeds is reproducibility, not accuracy.

## Axis correlation

ρ(predicted fold, predicted bind) = +0.675. **Not a valid test** of whether a separate rewiring class exists: both axes derive from ESM-2 by construction.

## All quantities and their check

| quantity | this_run | recorded | status |
|---|---|---|---|
| conformal_q90 | 6.807 | 6.807 | identical |
| conformal_coverage | 0.8992 | 0.8992 | identical |
| sd_vs_error_rho | 0.3039 | 0.3039 | identical |
| n_tolerated | 6283 | 6283 | identical |
| n_destabilising | 297 | 297 | identical |
| n_rewiring | 191 | 191 | identical |
| n_both | 113 | 113 | identical |
| point_estimate_destabilising | 2220 |  |  |
| old_filter_pass_fraction | 0.9994 |  |  |
| axis_rank_correlation | 0.6746 | 0.6746 | within tolerance |
| axis_correlation_is_valid_test | False |  |  |
| median_fold_halfwidth | 1.115 |  |  |
| coverage_min_domain | 0.8327 |  |  |
| coverage_max_domain | 0.9504 |  |  |

## Environment

| python | numpy | pandas | scipy | sklearn | transformers | torch | gpu |
|---|---|---|---|---|---|---|---|
| 3.13.15 | 2.1.3 | 2.2.3 | 1.16.3 | 1.6.1 | 5.16.1 | 2.11.0+cpu | none |
