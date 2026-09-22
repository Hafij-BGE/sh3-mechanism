# B1 — Folding predictor

*Generated automatically by the notebook on 2026-09-22T13:10:01 (1.5 min). Every number below comes from this run; nothing is typed by hand.*

## Summary

- Per-domain median ρ 0.839 (range 0.754–0.934, IQR 0.809–0.845) over 15 held-out SH3 domains; every 95% CI excludes zero: True.
- Beats zero-shot ESM-2 (median |ρ| 0.617) on 15/15 domains; two-sided sign test p = 6.1e-05.
- Pooled over 27,590 variants: ρ 0.843, RMSE 0.672 kcal/mol (quote the per-domain figure: SPTAN1 alone contributes 10,112 variants).
- The model uses no structural feature; structure is kept for the independent check in B2.

**Check against the recorded run: REPRODUCED** (8 identical, 2 within tolerance)

## Per held-out SH3 domain

Spearman ρ against measured ΔΔG_fold, 95% bootstrap CI (2,000 resamples). ESM is the zero-shot score on the same variants (negative sign is correct).

| group | gene | n | rho | lo | hi | esm |
|---|---|---|---|---|---|---|
| Q5VST9_1.0 | OBSCN | 1209 | 0.754 | 0.723 | 0.781 | -0.644 |
| P19174_1.0 | PLCG1 | 1091 | 0.772 | 0.744 | 0.798 | -0.660 |
| Q14185_1.0 | DOCK1 | 1208 | 0.774 | 0.747 | 0.799 | -0.578 |
| Q9BX66_2.0 | SORBS1 | 1210 | 0.797 | 0.773 | 0.819 | -0.617 |
| P07948_1.0 | LYN | 1014 | 0.822 | 0.797 | 0.845 | -0.524 |
| Q13882_1.0 | PTK6 | 1125 | 0.829 | 0.808 | 0.847 | -0.629 |
| P06239_1.0 | LCK | 983 | 0.837 | 0.816 | 0.856 | -0.557 |
| P42680_1.0 | TEC | 1072 | 0.839 | 0.818 | 0.857 | -0.679 |
| O15259_1.0 | NPHP1 | 2212 | 0.842 | 0.825 | 0.857 | -0.599 |
| Q14847_1.0 | LASP1 | 1045 | 0.844 | 0.825 | 0.862 | -0.606 |
| P08631_1.0 | HCK | 1034 | 0.845 | 0.823 | 0.865 | -0.603 |
| Q92882_1.0 | OSTF1 | 1028 | 0.845 | 0.823 | 0.865 | -0.684 |
| Q06187_1.0 | BTK | 1060 | 0.855 | 0.834 | 0.873 | -0.669 |
| Q13813_1.0 | SPTAN1 | 10112 | 0.872 | 0.865 | 0.878 | -0.527 |
| P06241_1.0 | FYN | 2187 | 0.934 | 0.926 | 0.940 | -0.647 |

## Cross-assay check on ddPCA folding energies (reliable fits)

A different assay (AbundancePCA) from the training data (proteolysis); GRB2-SH3 is the only SH3.

| domain | n | rho_model | rho_esm |
|---|---|---|---|
| GB1 | 878 | 0.827 | -0.199 |
| GRB2-SH3 | 1032 | 0.738 | -0.728 |
| PSD95-PDZ3 | 1199 | 0.530 | -0.481 |

## Feature ablation and simpler models (K1, K2)

Per-domain median ρ on the 15 held-out SH3 domains. Single-seed rows should be compared with the single-seed full model, not the ensemble.

| model | features | per_domain_median_rho | pooled_rho |
|---|---|---|---|
| MLP, ESM embedding only | 1280 | 0.676 | 0.680 |
| MLP, embedding + 5 ESM scalars | 1285 | 0.761 | 0.766 |
| MLP, 12 scalars only (no embedding) | 12 | 0.729 | 0.706 |
| MLP, all 1,292 features (seed 0) | 1292 | 0.831 | 0.836 |
| MLP, all features, 5-seed ensemble (the model) | 1292 | 0.839 | 0.843 |
| ridge regression, all features (alpha 1000) | 1292 | 0.754 | 0.736 |
| zero-shot ESM-2 score (no training) | 0 | 0.617 | 0.580 |

## Error by substitution type (J4)

bias = mean(predicted − measured); negative means under-predicted damage.

| substitution | n | rho | mae | bias |
|---|---|---|---|---|
| from glycine | 1898.000 | 0.694 | 0.705 | -0.272 |
| hydrophobic to polar | 2820.000 | 0.848 | 0.555 | 0.033 |
| other | 16006.000 | 0.823 | 0.471 | -0.051 |
| polar to hydrophobic | 4350.000 | 0.747 | 0.414 | -0.041 |
| to glycine | 1331.000 | 0.864 | 0.489 | -0.037 |
| to proline | 1185.000 | 0.800 | 0.610 | -0.031 |

## Error by measured effect size (J4)

| effect | n | rho | mae | bias |
|---|---|---|---|---|
| stabilising (<0) | 4955.000 | 0.201 | 0.489 | 0.465 |
| 0-1 | 9791.000 | 0.482 | 0.314 | 0.044 |
| 1-2 | 6362.000 | 0.348 | 0.523 | -0.146 |
| 2-3 | 4166.000 | 0.287 | 0.628 | -0.315 |
| >3 kcal/mol | 2316.000 | 0.358 | 0.941 | -0.866 |

## Against conventional predictors on the ddPCA domains (J6)

Spearman ρ with measured ΔΔG_fold on variants all four methods score. FoldX needs a structure; EVE needs a deep alignment; the head needs neither. FoldX (PDB numbering) and EVE residue numbers are converted to construct numbering by offsets derived from the wild-type residues.

| domain | common_variants | head | esm_zero_shot | foldx | eve | foldx_offset | eve_offset |
|---|---|---|---|---|---|---|---|
| GB1 | 836 | 0.825 | 0.204 | 0.487 | 0.370 | 1 | 0 |
| GRB2-SH3 | 877 | 0.761 | 0.728 | 0.701 | 0.638 | 0 | 0 |
| PSD95-PDZ3 | 1080 | 0.540 | 0.480 | 0.466 | 0.589 | 310 | 0 |

## All quantities and their check

| quantity | this_run | recorded | status |
|---|---|---|---|
| domains | 15 | 15 | identical |
| per_domain_median_rho | 0.8392 | 0.8392 | identical |
| per_domain_min_rho | 0.7542 | 0.7542 | identical |
| per_domain_max_rho | 0.9338 | 0.9338 | identical |
| per_domain_iqr_low | 0.8095 |  |  |
| per_domain_iqr_high | 0.8447 |  |  |
| all_ci_exclude_zero | True | True | identical |
| esm_per_domain_median_rho | -0.6166 | -0.6166 | identical |
| domains_won | 15 | 15 | identical |
| sign_test_p | 6.104e-05 |  |  |
| heldout_variants | 27590 | 27590 | identical |
| pooled_rho | 0.8428 | 0.8428 | within tolerance |
| pooled_pearson_r | 0.8365 |  |  |
| pooled_rmse | 0.6717 | 0.6717 | within tolerance |
| train_variants | 327027 |  |  |
| train_groups | 348 |  |  |
| val_variants | 34451 |  |  |
| val_groups | 38 |  |  |
| heldout_sh3_variants | 27590 |  |  |
| ablation: MLP, ESM embedding only | 0.6757 |  |  |
| ablation: MLP, embedding + 5 ESM scalars | 0.7607 |  |  |
| ablation: MLP, 12 scalars only (no embedding) | 0.7293 |  |  |
| ablation: MLP, all 1,292 features (seed 0) | 0.831 |  |  |
| ablation: MLP, all features, 5-seed ensemble (the model) | 0.8392 |  |  |
| ablation: ridge regression, all features (alpha 1000) | 0.7539 |  |  |
| ablation: zero-shot ESM-2 score (no training) | 0.6166 |  |  |
| baseline_GB1_head | 0.8247 |  |  |
| baseline_GB1_esm_zero_shot | 0.2038 |  |  |
| baseline_GB1_foldx | 0.4868 |  |  |
| baseline_GB1_eve | 0.3699 |  |  |
| baseline_GRB2-SH3_head | 0.7605 |  |  |
| baseline_GRB2-SH3_esm_zero_shot | 0.7284 |  |  |
| baseline_GRB2-SH3_foldx | 0.7013 |  |  |
| baseline_GRB2-SH3_eve | 0.638 |  |  |
| baseline_PSD95-PDZ3_head | 0.5396 |  |  |
| baseline_PSD95-PDZ3_esm_zero_shot | 0.4803 |  |  |
| baseline_PSD95-PDZ3_foldx | 0.4658 |  |  |
| baseline_PSD95-PDZ3_eve | 0.5886 |  |  |
| foldx_overlap_aligned | 2879 |  |  |
| foldx_vs_mochi_r_aligned | 0.4178 |  |  |
| foldx_vs_mochi_r_aligned_GB1 | 0.375 |  |  |
| foldx_vs_mochi_r_aligned_GRB2-SH3 | 0.5174 |  |  |
| foldx_vs_mochi_r_aligned_PSD95-PDZ3 | 0.3512 |  |  |

## Environment

| python | numpy | pandas | scipy | sklearn | transformers | torch | gpu |
|---|---|---|---|---|---|---|---|
| 3.13.15 | 2.1.3 | 2.2.3 | 1.16.3 | 1.6.1 | 5.16.1 | 2.11.0+cu128 | Tesla T4 |
