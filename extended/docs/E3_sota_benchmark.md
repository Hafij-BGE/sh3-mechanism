# E3 — Benchmark against the state of the art  *(planned)*

**Why it is needed.** The single biggest objection to B1. The head beats zero-shot ESM-2, FoldX and
EVE — but a reviewer will name three current supervised ΔΔG predictors and ask why they are missing.

**What it does not do.** It changes no frozen number. If the baselines win, that is reported; the
project's contribution is the mechanism separation and the positional-coverage limit, not a
leaderboard position — and a better folding predictor makes the 410 calls better.

## Inputs
| File | From | Used for |
|---|---|---|
| `folding_per_domain_ci.csv` | B1 (frozen) | the 15 held-out domains and our ρ per domain |
| SaProtΔG / ESM3ΔG checkpoints | HF `Yehlin/absolute-stability` | 12 LoRA weights, archived, verify 12/12 |
| `fig3__megascale_point_mutants_predictions.csv` | MGnify | **ThermoMPNN and ProteinDPO** predictions, free |
| `mgnify_training_index.csv`, `dmsv4_filtered_train_splits.csv` | MGnify | the leakage audit |
| `megascale_uniprot_mappings_offsets.tsv` | Domainome archive | maps held-out domains to PDB names |

## The leakage audit — already done, and clean
SaProtΔG and ESM3ΔG were trained on data that includes SH3 domains (CATH 2.30.30.40), so a benchmark
is meaningless without checking whether they saw our test set.

Name matching fails — the training index labels everything `rocklin_batch2_N`, not by PDB — so the
audit matched on sequence, using a 22-residue core per domain, with a positive control confirming the
method finds a known sequence exactly once.

| Searched | Rows | Held-out domains found |
|---|---|---|
| `mgnify_training_index.csv` | 965,856 | **0 / 15** |
| `dmsv4_filtered_train_splits.csv` | 455,589 | **0 / 15** |
| `230515_K50dG…concat.csv` (measurements) | 2.2 GB | 13 / 15 |

**Report the audit and its scope.** It proves absence from the two *published splits*, not from
whatever subset trained the final checkpoints. Say that.

## Two decisions to make before running
1. **Base or augmented?** There are matching notebooks for both. Running all four and reporting the
   best is exactly the trap C4 taught. Pick one on a stated reason; report the other as a labelled
   sensitivity check if at all.
2. **Which structures?** Inference takes a PDB/CIF path plus a chain ID, not a sequence. AlphaFold
   `.cif` is accepted (the repo's `examples/` includes TED AlphaFold models), so A2's output works.
   Note the confound in the write-up: the baselines receive structural input our head never had.

## Setup
GPU runtime; ESM3 licence accepted on Hugging Face under your own account; SaProt 650M; PyTorch
matching the CUDA version **before** the package. `ddg_scanning=True` gives a full saturation scan
from one structure, so E3 is 15 structures × 3 checkpoints, not thousands of calls.
