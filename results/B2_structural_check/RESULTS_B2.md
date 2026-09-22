# B2 — Structural check of the folding predictor

*Generated automatically by the notebook on 2026-09-22T13:15:25 (0.2 min). Every number below comes from this run; nothing is typed by hand.*

## Summary

- Predicted damage follows burial: ρ +0.712 over 56 aligned positions.
- It ignores the binding interface: ρ +0.037 — the burial signal is 19× larger.
- Structure was not a model input, so this is independent evidence that the head learned folding, not binding.

**Check against the recorded run: REPRODUCED** (3 identical)

## Predicted damage by structural class (aligned positions with ≥10 variants)

| buried | interface | positions | median_pred |
|---|---|---|---|
| False | False | 28 | 0.629 |
| False | True | 12 | 0.516 |
| True | False | 13 | 1.404 |
| True | True | 3 | 1.207 |

## Predicted damage by the variant’s own structure (AlphaFold)

| cls | variants | median_pred |
|---|---|---|
| buried | 2257 | 1.161 |
| no structure | 219 | 0.659 |
| surface | 4408 | 0.378 |

## Measured, for comparison: GRB2-SH3 ddPCA (from A1)

Median measured ΔΔG (kcal/mol).

| buried | interface | folding_coefficient | binding_coefficient | variants |
|---|---|---|---|---|
| False | False | 0.868 | -0.036 | 524 |
| False | True | 0.569 | 0.645 | 228 |
| True | False | 3.566 | 0.141 | 247 |
| True | True | 1.279 | 2.900 | 57 |

## Measured, cross-fold replication (from A2)

| buried | interface | ddG_fold | ddG_bind |
|---|---|---|---|
| False | False | 0.725 | 0.115 |
| False | True | 0.449 | 0.678 |
| True | False | 2.087 | 0.543 |
| True | True | 0.978 | 1.446 |

## All quantities and their check

| quantity | this_run | recorded | status |
|---|---|---|---|
| positions | 56 | 56 | identical |
| rho_damage_vs_burial | 0.7117 | 0.7117 | identical |
| rho_damage_vs_interface | 0.03698 | 0.03698 | identical |
| rho_damage_vs_burial_all_positions | 0.7117 |  |  |
| burial_to_interface_ratio | 19.24 |  |  |
| median_pred_buried_variants | 1.161 |  |  |
| median_pred_no_structure_variants | 0.6592 |  |  |
| median_pred_surface_variants | 0.3778 |  |  |

## Environment

| python | numpy | pandas | scipy | sklearn | transformers | torch | gpu |
|---|---|---|---|---|---|---|---|
| 3.13.15 | 2.1.3 | 2.2.3 | 1.16.3 | 1.6.1 | 5.16.1 | 2.11.0+cpu | none |
