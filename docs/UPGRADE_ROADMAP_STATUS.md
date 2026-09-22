# Upgrade roadmap — what is in this pipeline and what is not

Status of every item in `SH3_all_possible_upgrades_from_base_notebook.md`, checked against the data
and hardware available (Colab T4, the downloaded datasets, COSMIC).

## In this pipeline
| Item | Where |
|---|---|
| A1 data-quality report, A2 sequence validation | A0 (QC table, rejected rows with reason), A2 (residue check stops on any failure) |
| A4 dataset versioning | `reference/data_manifest.json`, `checksums.md5` |
| J3 per-domain reporting | B1 (median, IQR, worst, best) |
| I1 stratified coverage, I3 calibration curve, I4 rejection curve | B3 |
| J4 error decomposition | B1 |
| K1 feature ablation, K2 simpler model (ridge) | B1 |
| J6 FoldX / EVE comparison | B1 (on the ddPCA domains) |
| L3/L4 virtual saturation mutagenesis, G4 family hotspot map | B6 |
| F1–F3 specificity model and rewiring score | C4, with a pre-specified validation rule |
| E1 position-coverage experiment | C3 |
| T1 modules, T4 unit tests, T5 run records | 15 notebooks, `src/run_tests.py`, metrics JSON and environment per program |
| Tier 1 item 1, binding terminology | B3 and its doc: the binding column is an ESM-2 proxy, not a prediction |
| N1–N3 experimental validation *design* | F1: ranked, assay-tagged candidate panels from frozen outputs. The experiments themselves are future work; the rewiring and four-group panels are built only if C4 validates. |

## Feasible next, needs extra data or compute
| Item | What it needs |
|---|---|
| G1/G2/R1 mutational-opportunity null | Trinucleotide context from a GRCh38 reference sequence |
| C1/C2/C4/C6 structure-aware folding, B7 SaProt | Structures for all 412 MegaScale training domains (natural ones by PDB ID; designed ones not yet checked) |
| C3 GNN branch | The same structures, and a larger model |
| J1 homology-aware split of the training set | Sequence clustering (MMseqs2 in Colab) |
| D1 antisymmetric head, D3 ranking loss | Model changes; antisymmetry cannot be validated because reverse mutations are not measured |
| B1 ESM-2 size comparison, B2/B3 local context | Re-embedding and retraining (hours on a T4) |
| B5 LoRA | Feasible on a T4 but slow; full fine-tuning (B4) is not |

## Not possible with current data
| Item | Reason |
|---|---|
| E2/E3 multi-domain binding | Only 3 ddPCA domains exist, 1 of them an SH3 (C1 shows pooling fails) |
| F4 contrastive peptide ranking | The phage-display peptides are all binders (signal floor 3.00, no negatives) |
| E5, O1–O3 epistasis | No double-mutant SH3 binding data |
| N1–N3 validation *experiments*, P1–P3 other families, U5–U7 | Need new experiments or separate projects (F1 plans the N1–N3 panels) |
