# E3 — Benchmark against the state of the art  *(Experiment 1 run, 27 September 2026)*

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
from one structure, so E3 is 26 constructs × 3 checkpoints per model, not
thousands of calls — but a scan is still ~1,200 forward passes, so every scan is cached to Drive per
(model, version, seed, construct) and the notebook resumes rather than restarts.

## What was settled before the notebook was written

Pre-registration: [preregistration/E3.md](preregistration/E3.md) @ `ccd3446`, Part 6.

**ThermoMPNN cannot be a competitor here.** The pre-commit leakage check — the same one already run
for SaProtΔG and ESM3ΔG — found **13 of our 15 held-out domains in ThermoMPNN's own published train
(12) or validation (1) split**, covering 23,191 of 27,590 held-out variants. Running it across all 15
would have scored its training data against our held-out set. It runs on **FYN and NPHP1 only**
(4,399 variants) and carries **no verdict at any n**. ProteinDPO was dropped before any result, for
cost and risk.

| competitor | held-out domains in its published training data | role |
|---|---|---|
| SaProtΔG | 0 of 15 | verdict |
| ESM3ΔG | 0 of 15 | verdict |
| ThermoMPNN | **13 of 15** | descriptive only |

So **two competitors carry a verdict and the threshold is p < 0.025**, not the 0.0125 the draft assumed
for four. The audit is reported as a result in its own right: a MegaScale-derived benchmark cannot
compare MegaScale-trained predictors without it.

**Structures resolved, with no fallback needed.** Every held-out variant already names its structure —
for MegaScale rows the frozen run set `domain_key` to the construct name and `pos` to the position
inside it. The 26 constructs resolve to 22 PDB entries and **all 22 are present at RCSB**: 10 NMR
(model 1 is used), 11 X-ray, one powder diffraction, and only 1A0N has a second chain. Eight
constructs are background point mutants with no structure of their own — parent coordinates, the
background applied to the sequence only, affected count reported. **The AlphaFold fallback fires for
zero domains**, so Experiment 3 stays a genuine sensitivity check.

**Version: base** for Experiment 1, so the comparison is about method rather than training-set size;
augmented remains Experiment 2.

**Signs are aligned by each source's documented convention**, never by which direction correlates
better, and the unaligned correlations are printed beside the aligned ones so that is visible.

## What Experiment 1 found

Numbers in `results/E3_sota_benchmark/RESULTS_E3_exp1.md`; reading in `ANALYSIS_E3.md`.

- **No clear difference against SaProtΔG.** Median per-domain ρ +0.855 against our +0.839, median
  paired difference −0.028, Wilcoxon p = 0.107 against α = 0.025. 27,590 variants, 0 dropped.
- **The asymmetry is the point.** Our head is sequence-only and saw no SH3 domain in training;
  SaProtΔG gets the experimentally determined structure of the measured construct.
- **Not a claim of parity.** SaProtΔG is nominally ahead on 11 of 15 domains. 15 domains cannot
  resolve a 0.03 gap, which the plan stated before any result existed.
- **ESM3ΔG was not run** (gated model, no token), so one of the two verdicts is outstanding.
- **ThermoMPNN was not run** — `from datasets import Mutation` collided with the Hugging Face
  `datasets` package. Fixed by setting `PYTHONPATH`. Its leakage audit, which is the valuable part,
  did not depend on running it.
