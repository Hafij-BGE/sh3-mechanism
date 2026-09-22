# A2 — Features

*Generated automatically by the notebook on 2026-09-22T12:17:36 (20.9 min). Every number below comes from this run; nothing is typed by hand.*

## Summary

- 399,640 variants pass the residue check (0 dropped): MegaScale 389,068, ddPCA 3,688, atlas 6,884.
- ESM-2 embedded 725 wild-type domains; each variant = 1,280 + 12 = 1,292 numbers.
- Zero-shot ESM-2: folding ρ -0.404, binding ρ -0.259 (ddPCA).
- Atlas structure coverage 96.8%; reference-frame mapping 89.5%; 9 proteins have no AlphaFold model.

**Check against the recorded run: REPRODUCED** (13 within tolerance, 8 identical)

## Variant table

| set | variants | domains |
|---|---|---|
| atlas | 6884 | 310 |
| ddpca | 3688 | 3 |
| megascale | 389068 | 412 |

## Zero-shot ESM-2 against measured ΔΔG (Spearman)

Folding is tracked better than binding: the gap the thesis is about.

| set | target | n | rho |
|---|---|---|---|
| ddpca | ddG_fold | 3688 | -0.4038 |
| ddpca | ddG_bind | 3368 | -0.2592 |
| megascale | ddG_fold | 389068 | -0.3881 |

## PDB offsets (derived, not assumed)

| domain | pdb | offset | identity |
|---|---|---|---|
| GRB2-SH3 | 2vwf | 0 | 0.982 |
| PSD95-PDZ3 | 1be9 | 310 | 0.988 |
| GB1 | 2gb1 | 1 | 0.982 |

## Cross-fold separation (GRB2-SH3 + PSD95-PDZ3, reliable binding only)

Replication of A1 across two folds.

| buried | interface | ddG_fold | ddG_bind |
|---|---|---|---|
| False | False | 0.725 | 0.115 |
| False | True | 0.449 | 0.678 |
| True | False | 2.087 | 0.543 |
| True | True | 0.978 | 1.446 |

## AlphaFold proteins without a model

Very large proteins that AlphaFold DB splits into fragments; only F1 is requested.

| uniprot |
|---|
| O60229 |
| O75962 |
| P15924 |
| P20929 |
| Q03001 |
| Q15149 |
| Q5VST9 |
| Q9UKN7 |
| Q9UPN3 |

## All quantities and their check

| quantity | this_run | recorded | status |
|---|---|---|---|
| variants_total | 3.996e+05 | 3.996e+05 | identical |
| variants_megascale | 3.891e+05 | 3.891e+05 | identical |
| variants_ddpca | 3688 | 3688 | identical |
| variants_atlas | 6884 | 6884 | identical |
| dropped_by_residue_check | 0 |  |  |
| esm_domains | 725 | 725 | identical |
| esm_rho_ddpca_fold | -0.4038 | -0.404 | within tolerance |
| esm_rho_ddpca_bind | -0.2592 | -0.259 | within tolerance |
| esm_rho_megascale_fold | -0.3881 | -0.388 | within tolerance |
| structure_rows | 1.876e+04 | 1.876e+04 | identical |
| structure_domains | 302 | 302 | identical |
| alphafold_proteins_missing | 9 |  |  |
| atlas_structure_coverage | 0.9682 | 0.968 | within tolerance |
| atlas_refmap_coverage | 0.8947 | 0.895 | within tolerance |
| atlas_groups | 310 | 310 | identical |
| xsep_surface_not_interface_fold | 0.7246 | 0.725 | within tolerance |
| xsep_surface_not_interface_bind | 0.115 | 0.115 | within tolerance |
| xsep_surface_interface_fold | 0.4494 | 0.449 | within tolerance |
| xsep_surface_interface_bind | 0.6785 | 0.678 | within tolerance |
| xsep_buried_not_interface_fold | 2.087 | 2.087 | within tolerance |
| xsep_buried_not_interface_bind | 0.5433 | 0.543 | within tolerance |
| xsep_buried_interface_fold | 0.9783 | 0.978 | within tolerance |
| xsep_buried_interface_bind | 1.446 | 1.446 | within tolerance |

## Environment

| python | numpy | pandas | scipy | sklearn | transformers | Bio | torch | gpu |
|---|---|---|---|---|---|---|---|---|
| 3.13.15 | 2.1.3 | 2.2.3 | 1.16.3 | 1.6.1 | 5.16.1 | 1.88 | 2.11.0+cu128 | Tesla T4 |
