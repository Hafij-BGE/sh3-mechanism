# F1 — Experimental validation candidates

*Generated automatically by the notebook on 2026-09-22T15:56:40 (0.1 min). Every number below comes from this run; nothing is typed by hand.*

## Summary

- 20 candidates in 2 classes, 8 of them tier 1.
- Controls from the same domains as the destabilising picks: 10 of 10.
- Specificity axis validated (C4): False — no rewiring panel and no four-group design, by design.
- Nothing upstream was re-run or changed; a prioritisation aid, not a result.

**Check against the recorded run: no recorded values to compare** ()

## Panel sizes by class

Tier 1 = seen in a non-hypermutated tumour and a below-median 90% half-width.

| mechanism | candidates | tier1 |
|---|---|---|
| destabilising (Panel S) | 10 | 3 |
| tolerated control (Panel S) | 10 | 5 |

## Candidates

Full table (with tumour sites): `experimental_candidates.csv`, on Drive only.

| variant_id | gene | domain_idx | pos | pred_ddG_fold | fold_lo | fold_halfwidth | rewiring | nonhyper | mechanism | priority_tier |
|---|---|---|---|---|---|---|---|---|---|---|
| O15034_d2_I906N | RIMBP2 | 2 | 59 | 4.621 | 3.814 | 0.807 |  | True | destabilising (Panel S) | 1 |
| Q9BX66_d1_V820D | SORBS1 | 1 | 28 | 4.113 | 3.392 | 0.721 |  | True | destabilising (Panel S) | 1 |
| P02549_d1_V982D | SPTA1 | 1 | 6 | 4.264 | 3.105 | 1.158 |  | True | destabilising (Panel S) | 2 |
| P07947_d1_A98D | YES1 | 1 | 8 | 3.983 | 2.831 | 1.152 |  | True | destabilising (Panel S) | 2 |
| Q8NFA2_d2_R282P | NOXO1 | 2 | 46 | 4.628 | 2.677 | 1.951 |  | True | destabilising (Panel S) | 2 |
| Q9BVN2_d1_A851P | RUSC1 | 1 | 8 | 4.033 | 2.593 | 1.440 |  | True | destabilising (Panel S) | 2 |
| Q99962_d1_A297D | SH3GL2 | 1 | 8 | 4.276 | 2.547 | 1.730 |  | True | destabilising (Panel S) | 2 |
| Q15642_d1_A547P | TRIP10 | 1 | 8 | 4.000 | 2.529 | 1.471 |  | True | destabilising (Panel S) | 2 |
| Q13588_d2_I185T | GRAP | 2 | 28 | 3.980 | 2.491 | 1.488 |  | True | destabilising (Panel S) | 2 |
| Q8TDM6_d1_A1600P | DLG5 | 1 | 8 | 3.553 | 2.469 | 1.084 |  | True | destabilising (Panel S) | 1 |
| Q99962_d1_E306K | SH3GL2 | 1 | 17 | 0.192 | -0.251 | 0.443 |  | False | tolerated control (Panel S) | 2 |
| P07947_d1_A148V | YES1 | 1 | 58 | 0.003 | -0.505 | 0.507 |  | False | tolerated control (Panel S) | 2 |
| Q9BX66_d1_M795L | SORBS1 | 1 | 3 | 0.155 | -0.354 | 0.509 |  | True | tolerated control (Panel S) | 1 |
| Q15642_d1_L600V | TRIP10 | 1 | 61 | 0.262 | -0.277 | 0.539 |  | True | tolerated control (Panel S) | 1 |
| Q9BVN2_d1_D880N | RUSC1 | 1 | 37 | 0.132 | -0.417 | 0.549 |  | False | tolerated control (Panel S) | 2 |
| P02549_d1_G978A | SPTA1 | 1 | 2 | 0.125 | -0.438 | 0.563 |  | True | tolerated control (Panel S) | 1 |
| O15034_d2_A916T | RIMBP2 | 2 | 69 | 0.125 | -0.459 | 0.584 |  | True | tolerated control (Panel S) | 1 |
| Q8TDM6_d1_D1607N | DLG5 | 1 | 15 | 0.179 | -0.426 | 0.605 |  | False | tolerated control (Panel S) | 2 |
| Q8NFA2_d2_E249Q | NOXO1 | 2 | 13 | 0.120 | -0.736 | 0.857 |  | False | tolerated control (Panel S) | 2 |
| Q13588_d2_Q172L | GRAP | 2 | 15 | 0.030 | -0.832 | 0.863 |  | True | tolerated control (Panel S) | 1 |

## Assays by class

| class | recommended assays |
|---|---|
| stability (Panel S) | thermal denaturation (CD or DSF); proteolysis-based stability assay; cellular abundance assay; ddPCA (AbundancePCA) if the domain can be cloned into that system |
| specificity (Panel R) | phage display against the peptide library; peptide array; fluorescence polarisation (WT vs mutant against candidate peptides); SPR for kinetic confirmation of the top hits; yeast two-hybrid or a cell-based binding assay |

## Why there is no specificity or four-group panel

C4's pre-registered rule returned validated=False (median centred r 0.288; wins vs the average profile 55/115). Panel R and the rewiring groups of Panel D are intentionally empty rather than built from the disclaimed ESM-based label in B3.

## All quantities and their check

| quantity | this_run | recorded | status |
|---|---|---|---|
| n_per_panel | 10 |  |  |
| specificity_axis_validated | False |  |  |
| panel_s_destabilising | 10 |  |  |
| panel_s_control | 10 |  |  |
| panel_s_control_same_domain | 10 |  |  |
| panel_r_rewiring_only | 0 |  |  |
| four_group_design_available | False |  |  |
| total_candidates | 20 |  |  |
| total_tier1 | 8 |  |  |
| median_atlas_fold_halfwidth | 1.115 |  |  |

## Environment

| python | numpy | pandas | scipy | sklearn | transformers | torch | gpu |
|---|---|---|---|---|---|---|---|
| 3.13.15 | 2.1.3 | 2.2.3 | 1.16.3 | 1.6.1 | 5.16.1 | 2.11.0+cpu | none |
