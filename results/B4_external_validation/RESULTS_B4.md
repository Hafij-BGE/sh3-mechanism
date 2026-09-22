# B4 — External validation (ProteinGym)

*Generated automatically by the notebook on 2026-09-22T13:22:04 (11.4 min). Every number below comes from this run; nothing is typed by hand.*

## Summary

- Primary (external stability): head 0.361 vs ESM 0.406, head wins 2/3.
- Secondary (abundance): head 0.400 vs ESM 0.491, wins 6/15.
- Sanity (training data): 0.940 vs 0.580 — the pipeline is wired correctly.
- Claim: a domain-scale predictor validated within its regime. Not claimed: a general stability predictor.

**Check against the recorded run: REPRODUCED** (12 identical)

## By block

|Spearman ρ| per assay, medians. The sanity block is the training distribution: a wiring check.

| block | assays | model_median_abs_rho | esm_median_abs_rho | model_wins |
|---|---|---|---|---|
| primary | 3 | 0.361 | 0.406 | 2 |
| sanity | 10 | 0.940 | 0.580 | 10 |
| secondary | 15 | 0.400 | 0.491 | 6 |

## Transfer drop from the internal SH3 result

Internal: head 0.839, ESM 0.617 (per-domain medians, B1).

| block | head_drop | esm_drop | ratio |
|---|---|---|---|
| primary | 0.478 | 0.211 | 2.267 |
| secondary | 0.439 | 0.126 | 3.491 |

## By sequence length (primary + secondary)

Small n and confounded with assay type; shown only to rule out the explanation that the 128-residue window is the problem.

| length | assays | model | esm |
|---|---|---|---|
| >250 | 11 | 0.450 | 0.406 |
| ≤250 | 7 | 0.340 | 0.493 |

## Every assay

| DMS_id | block | n | seq_len | rho_model | rho_esm |
|---|---|---|---|---|---|
| PRKN_HUMAN_Clausen_2023 | primary | 1500 | 465 | -0.455 | 0.406 |
| ESTA_BACSU_Nutschel_2020 | primary | 1500 | 212 | -0.340 | 0.325 |
| AACC1_PSEAI_Dandage_2018 | primary | 1500 | 177 | -0.361 | 0.493 |
| S22A1_HUMAN_Yee_2023_abundance | secondary | 1500 | 553 | -0.469 | 0.605 |
| PPARG_HUMAN_Majithia_2016 | secondary | 1500 | 505 | -0.188 | 0.558 |
| HXK4_HUMAN_Gersing_2023_abundance | secondary | 1500 | 465 | -0.360 | 0.289 |
| CAS9_STRP1_Spencer_2017_positive | secondary | 1500 | 1368 | -0.085 | 0.035 |
| OXDA_RHOTO_Vanella_2023_expression | secondary | 1500 | 364 | -0.400 | 0.273 |
| CP2C9_HUMAN_Amorosi_2021_abundance | secondary | 1500 | 490 | -0.584 | 0.611 |
| CCR5_HUMAN_Gill_2023 | secondary | 1500 | 352 | -0.269 | 0.352 |
| PTEN_HUMAN_Matreyek_2021 | secondary | 1500 | 403 | -0.450 | 0.354 |
| TPMT_HUMAN_Matreyek_2018 | secondary | 1500 | 245 | -0.534 | 0.552 |
| Q53Z42_HUMAN_McShan_2019_expression | secondary | 1500 | 365 | -0.496 | 0.525 |
| VKOR1_HUMAN_Chiasson_2020_abundance | secondary | 1500 | 163 | -0.515 | 0.486 |
| KCNE1_HUMAN_Muhammad_2023_expression | secondary | 1500 | 129 | -0.079 | 0.127 |
| RPC1_LAMBD_Li_2019_high-expression | secondary | 351 | 237 | -0.312 | 0.533 |
| RPC1_LAMBD_Li_2019_low-expression | secondary | 351 | 237 | -0.332 | 0.494 |
| OPSD_HUMAN_Wan_2019 | secondary | 165 | 348 | -0.580 | 0.491 |
| HECD1_HUMAN_Tsuboyama_2023_3DKM | sanity | 1244 | 72 | -0.937 | 0.643 |
| POLG_PESV_Tsuboyama_2023_2MXD | sanity | 995 | 53 | -0.933 | 0.093 |
| UBE4B_HUMAN_Tsuboyama_2023_3L1X | sanity | 1118 | 69 | -0.948 | 0.584 |
| MYO3_YEAST_Tsuboyama_2023_2BTT | sanity | 947 | 61 | -0.943 | 0.510 |
| CSN4_MOUSE_Tsuboyama_2023_1UFM | sanity | 1353 | 72 | -0.946 | 0.342 |
| SPTN1_CHICK_Tsuboyama_2023_1TUD | sanity | 1051 | 60 | -0.947 | 0.589 |
| OBSCN_HUMAN_Tsuboyama_2023_1V1C | sanity | 1213 | 65 | -0.756 | 0.646 |
| AMFR_HUMAN_Tsuboyama_2023_4G3O | sanity | 820 | 47 | -0.958 | 0.521 |
| DOCK1_MOUSE_Tsuboyama_2023_2M0Y | sanity | 1213 | 66 | -0.772 | 0.576 |
| SDA_BACSU_Tsuboyama_2023_1PV0 | sanity | 834 | 44 | -0.805 | 0.608 |

## All quantities and their check

| quantity | this_run | recorded | status |
|---|---|---|---|
| primary_assays | 3 | 3 | identical |
| primary_model_median_abs_rho | 0.3615 | 0.3615 | identical |
| primary_esm_median_abs_rho | 0.4059 | 0.4059 | identical |
| primary_model_wins | 2 | 2 | identical |
| sanity_assays | 10 | 10 | identical |
| sanity_model_median_abs_rho | 0.9397 | 0.9397 | identical |
| sanity_esm_median_abs_rho | 0.5803 | 0.5803 | identical |
| sanity_model_wins | 10 | 10 | identical |
| secondary_assays | 15 | 15 | identical |
| secondary_model_median_abs_rho | 0.3997 | 0.3997 | identical |
| secondary_esm_median_abs_rho | 0.4907 | 0.4907 | identical |
| secondary_model_wins | 6 | 6 | identical |
| primary_drop_ratio_head_vs_esm | 2.267 |  |  |
| secondary_drop_ratio_head_vs_esm | 3.491 |  |  |

## Environment

| python | numpy | pandas | scipy | sklearn | transformers | Bio | torch | gpu |
|---|---|---|---|---|---|---|---|---|
| 3.13.15 | 2.1.3 | 2.2.3 | 1.16.3 | 1.6.1 | 5.16.1 | 1.88 | 2.11.0+cu128 | Tesla T4 |
