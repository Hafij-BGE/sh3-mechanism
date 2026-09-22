# A1 — Ground truth

*Generated automatically by the notebook on 2026-09-22T12:08:38 (1.4 min). Every number below comes from this run; nothing is typed by hand.*

## Summary

- ddPCA: 3,688 single substitutions in 3 domains; 2,840 reliable binding energies (GRB2-SH3 619, the only SH3).
- MegaScale: 389,068 folding stabilities in 412 domains, sign flipped; 26 structures of 15 human SH3 genes (27,590 variants).
- Sign check: folding r +0.829 (n=15), binding r +0.612 (n=12, offset 310).
- Measured: buried non-interface residues cost 3.57 kcal/mol of folding energy; buried interface residues cost 2.90 of binding energy.

**Check against the recorded run: REPRODUCED** (15 identical, 11 within tolerance)

## ddPCA per domain

Reliable binding: coefficient present, |ΔΔG_bind| ≤ 4 and bootstrap SD ≤ 0.5.

| domain | singles | with_binding | reliable_binding | reliable_folding | positions | bootstraps | duplicated_ids |
|---|---|---|---|---|---|---|---|
| GB1 | 1045 | 1045 | 1000 | 878 | 55 | 10 | 0 |
| GRB2-SH3 | 1056 | 756 | 619 | 1032 | 56 | 10 | 0 |
| PSD95-PDZ3 | 1587 | 1567 | 1221 | 1199 | 84 | 10 | 0 |

## In vitro calibration

Both correlations must be positive; they are the pipeline-wide sign check.

| axis | reference | n | pearson_r | numbering_offset |
|---|---|---|---|---|
| folding | Troilo 2018 (GRB2-SH3, Kf/Ku) | 15 | 0.8291 |  |
| binding | Chi 2008 (PSD95-PDZ3, b_ddg) | 12 | 0.6123 | 310 |

## Measured separation (GRB2-SH3, median ΔΔG in kcal/mol)

The empirical premise of the thesis: the two energies separate along structural lines.

| buried | interface | folding_coefficient | binding_coefficient | variants |
|---|---|---|---|---|
| False | False | 0.868 | -0.036 | 524 |
| False | True | 0.569 | 0.645 | 228 |
| True | False | 3.566 | 0.141 | 247 |
| True | True | 1.279 | 2.900 | 57 |

## MegaScale domains matched to human SH3 domains

| WT_name | gene | uniprot | domain_idx | identity |
|---|---|---|---|---|
| 4HCK.pdb | HCK | P08631 | 1 | 0.78 |
| 3I35.pdb | LASP1 | Q14847 | 1 | 0.754 |
| 2KGT.pdb | PTK6 | Q13882 | 1 | 0.635 |
| 1V1C.pdb | OBSCN | Q5VST9 | 1 | 0.631 |
| 6NMW.pdb | LYN | P07948 | 1 | 0.627 |
| 2LJ3.pdb | SPTAN1 | Q13813 | 1 | 0.593 |
| 1S1N.pdb_F11S | NPHP1 | O15259 | 1 | 0.593 |
| 1S1N.pdb_V29A | NPHP1 | O15259 | 1 | 0.593 |
| 1QLY.pdb | BTK | Q06187 | 1 | 0.586 |
| 1PWT.pdb | SPTAN1 | Q13813 | 1 | 0.579 |
| 2M0Y.pdb | DOCK1 | Q14185 | 1 | 0.565 |
| 1H92.pdb | LCK | P06239 | 1 | 0.561 |
| 1ZLM.pdb | OSTF1 | Q92882 | 1 | 0.554 |
| 1A0N.pdb_L7S | FYN | P06241 | 1 | 0.552 |
| 1A0N.pdb_V55A | FYN | P06241 | 1 | 0.552 |
| 6SCW.pdb | SPTAN1 | Q13813 | 1 | 0.55 |
| 2O2W.pdb | SORBS1 | Q9BX66 | 2 | 0.548 |
| 1QKX.pdb | SPTAN1 | Q13813 | 1 | 0.536 |
| 2CDT.pdb | SPTAN1 | Q13813 | 1 | 0.536 |
| 1E6H.pdb | SPTAN1 | Q13813 | 1 | 0.533 |
| 1BK2.pdb_F47A | SPTAN1 | Q13813 | 1 | 0.518 |
| 1BK2.pdb_L5S | SPTAN1 | Q13813 | 1 | 0.518 |
| 1Y0M.pdb | PLCG1 | P19174 | 1 | 0.517 |
| 1GL5.pdb | TEC | P42680 | 1 | 0.5 |
| 5FWB.pdb_A10S | SPTAN1 | Q13813 | 1 | 0.5 |
| 5FWB.pdb_M24A | SPTAN1 | Q13813 | 1 | 0.5 |

## All quantities and their check

| quantity | this_run | recorded | status |
|---|---|---|---|
| ddpca_singles | 3688 | 3688 | identical |
| ddpca_both_energies | 3368 | 3368 | identical |
| reliable_binding | 2840 | 2840 | identical |
| reliable_folding | 3109 | 3109 | identical |
| reliable_binding_GRB2-SH3 | 619 | 619 | identical |
| reliable_binding_PSD95-PDZ3 | 1221 | 1221 | identical |
| reliable_binding_GB1 | 1000 | 1000 | identical |
| calibration_fold_r | 0.8291 | 0.829 | within tolerance |
| calibration_fold_n | 15 | 15 | identical |
| calibration_bind_r | 0.6123 | 0.612 | within tolerance |
| calibration_bind_n | 12 | 12 | identical |
| chi_offset | 310 | 310 | identical |
| megascale_singles | 3.891e+05 | 3.891e+05 | identical |
| megascale_domains | 412 | 412 | identical |
| megascale_sh3_structures | 26 | 26 | identical |
| megascale_sh3_genes | 15 | 15 | identical |
| megascale_sh3_variants | 2.759e+04 |  |  |
| foldx_overlap | 1024 | 1024 | identical |
| foldx_vs_mochi_r | 0.4944 | 0.494 | within tolerance |
| sep_surface_not_interface_fold | 0.8679 | 0.868 | within tolerance |
| sep_surface_not_interface_bind | -0.03568 | -0.036 | within tolerance |
| sep_surface_interface_fold | 0.5687 | 0.569 | within tolerance |
| sep_surface_interface_bind | 0.6455 | 0.645 | within tolerance |
| sep_buried_not_interface_fold | 3.566 | 3.566 | within tolerance |
| sep_buried_not_interface_bind | 0.1414 | 0.141 | within tolerance |
| sep_buried_interface_fold | 1.279 | 1.279 | within tolerance |
| sep_buried_interface_bind | 2.9 | 2.9 | within tolerance |

## Environment

| python | numpy | pandas | scipy | sklearn | transformers | Bio | torch | gpu |
|---|---|---|---|---|---|---|---|---|
| 3.13.15 | 2.1.3 | 2.2.3 | 1.16.3 | 1.6.1 | 5.16.1 | 1.88 | 2.11.0+cpu | none |
