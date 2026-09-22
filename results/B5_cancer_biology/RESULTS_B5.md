# B5 — Cancer biology

*Generated automatically by the notebook on 2026-09-22T15:15:22 (0.7 min). Every number below comes from this run; nothing is typed by hand.*

## Summary

- 5.96% of atlas variants are called destabilising (5.59% of non-hypermutated).
- Genes enriched: 1/170 (all), 0/17 (non-hypermutated; underpowered); tumour sites 0/22.
- Variant counts do not follow predicted damage (ρ -0.009) while damage follows burial (ρ +0.712).
- Positions are non-uniform (p = 2.0e-04), but the null ignores mutational opportunity and the pattern is unrelated to damage: a mutational-process observation, not a selection signal.

**Check against the recorded run: REPRODUCED** (15 identical)

## Enrichment tests

Burial-matched permutation null, Benjamini–Hochberg, q < 0.1.

| test | tested | significant | smallest_q |
|---|---|---|---|
| genes, all variants (≥20 variants) | 170 | 1 | 0.085 |
| genes, non-hypermutated only (≥20) | 17 | 0 | 0.314 |
| tumour primary sites (≥30) | 22 | 0 | 0.484 |

## Tumour sites

| site | n | frac_destab | expected | excess | p | q |
|---|---|---|---|---|---|---|
| liver | 312 | 0.0801 | 0.0513 | 0.0288 | 0.022 | 0.484 |
| lung | 908 | 0.0683 | 0.0573 | 0.011 | 0.0659 | 0.542 |
| skin | 1418 | 0.0642 | 0.0557 | 0.00846 | 0.0739 | 0.542 |
| kidney | 120 | 0.0917 | 0.0583 | 0.0333 | 0.108 | 0.593 |
| breast | 272 | 0.0662 | 0.0478 | 0.0184 | 0.139 | 0.611 |
| central_nervous_system | 307 | 0.0684 | 0.0554 | 0.013 | 0.21 | 0.769 |
| cervix | 115 | 0.0522 | 0.0435 | 0.0087 | 0.407 | 1 |
| thyroid | 123 | 0.065 | 0.0569 | 0.00813 | 0.42 | 1 |
| haematopoietic_and_lymphoid_tissue | 346 | 0.0578 | 0.0549 | 0.00289 | 0.458 | 1 |
| stomach | 559 | 0.0572 | 0.0572 | 0 | 0.522 | 1 |
| pancreas | 108 | 0.0556 | 0.0556 | 0 | 0.577 | 1 |
| endometrium | 543 | 0.0534 | 0.0552 | -0.00184 | 0.629 | 1 |
| ns | 94 | 0.0532 | 0.0532 | 0 | 0.632 | 1 |
| oesophagus | 337 | 0.0504 | 0.0549 | -0.00445 | 0.681 | 1 |
| prostate | 107 | 0.0467 | 0.0561 | -0.00935 | 0.694 | 1 |
| ovary | 102 | 0.0392 | 0.049 | -0.0098 | 0.78 | 1 |
| biliary_tract | 103 | 0.0388 | 0.0583 | -0.0194 | 0.807 | 1 |
| soft_tissue | 71 | 0.0141 | 0.0423 | -0.0282 | 0.964 | 1 |
| upper_aerodigestive_tract | 221 | 0.0271 | 0.0543 | -0.0271 | 0.986 | 1 |
| urinary_tract | 241 | 0.0166 | 0.0498 | -0.0332 | 0.999 | 1 |
| large_intestine | 1109 | 0.0406 | 0.0577 | -0.0171 | 1 | 1 |
| small_intestine | 39 | 0 | 0.0513 | -0.0513 | 1 | 1 |

## All quantities and their check

| quantity | this_run | recorded | status |
|---|---|---|---|
| variants | 6884 | 6884 | identical |
| nonhyper | 2165 | 2165 | identical |
| frac_destab_all | 0.05956 | 0.05956 | identical |
| frac_destab_nonhyper | 0.05589 | 0.05589 | identical |
| genes_tested_all | 170 | 170 | identical |
| genes_sig_all | 1 | 1 | identical |
| genes_tested_nonhyper | 17 | 17 | identical |
| genes_sig_nonhyper | 0 | 0 | identical |
| sites_tested | 22 | 22 | identical |
| sites_sig | 0 | 0 | identical |
| positions_mapped | 56 | 56 | identical |
| positional_uniform_p | 0.0002 | 0.0002 | identical |
| rho_variants_vs_damage | -0.008853 | -0.008853 | identical |
| rho_damage_vs_burial | 0.7117 | 0.7117 | identical |
| rho_variants_vs_burial | -0.1778 | -0.1778 | identical |
| binding_claims_made | False |  |  |

## Environment

| python | numpy | pandas | scipy | sklearn | transformers | torch | gpu |
|---|---|---|---|---|---|---|---|
| 3.13.15 | 2.1.3 | 2.2.3 | 1.16.3 | 1.6.1 | 5.16.1 | 2.11.0+cpu | none |
