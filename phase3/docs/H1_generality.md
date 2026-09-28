# H1 — Does the frozen model generalise beyond SH3?

**Why it is needed.** Phase 1's median per-domain ρ of 0.839 and Phase 2's |ρ| of 0.600 are both
about **one family**. A reviewer's first question is whether those numbers describe the method or
describe SH3.

**What it does not do.** It re-fits nothing. The frozen head is applied unchanged, `clip = 10` as the
atlas predictions were produced, and no Phase 1 or Phase 2 number is recomputed.

**Pre-registered** in `docs/preregistration/H1.md`, committed before the notebook existed, amended
through Part 9, unsigned. The notebook reads that file at run time.

## The design, and why it is this design

H1.0's audit settled two things. Every candidate family is **absent from MegaScale training**, so no
retraining is needed — but PDZ is absent **because it is longer than anything in training**
(MegaScale caps constructs at 72 residues; PDZ runs 70–97). Evaluating on PDZ alone would confound
*new family* with *longer than training*.

| arm | families | domains | verdict? |
|---|---|---|---|
| **MAIN** | Myb/SANT + PHD + B-box — absent **and** length-matched | 35 | **yes** |
| secondary | PDZ — absent, length-confounded | 31 | no |
| control | SH3, recomputed on Domainome | 36 | no — must reproduce E2 |

**The main arm pools three families because one would not have worked.** At 15 domains the 95 %
interval on the median |ρ| is 0.243 wide — wider than the margin it would be compared against, so
the answer would have been "inconclusive" whatever the data said. At 35 domains it is 0.148, tighter
than SH3's own reference arm.

## What would count as a result

Non-inferiority against a **−0.15** margin — one SD of SH3's own per-domain spread — with a 95 % CI
from 4,000 bootstrap resamples **over domains**. "Comparable accuracy" cannot be supported by failing
to reject a null; that is the trap E1 hit from the other side.

Part 6 fixes the 2 × 2 in advance. The informative cell is **main supported, PDZ not** — that would
show the limit is **construct length rather than family**, and it is reachable only because both arms
run.

## Inputs

| | |
|---|---|
| `models.pt` | the frozen seed ensemble, unchanged |
| `sh3_common.py` | the frozen pipeline module — imported, not re-implemented |
| Domainome Table 2 | measured abundance, Zenodo 14356805 v5 |
| `domainome_domain_sequences.tsv` | produced by H1.0 |
| `matched_variants_E2.csv`, `per_domain_E2.csv` | the reproduction target and the margin |

## Outputs

| | |
|---|---|
| `per_domain_H1.csv`, `metrics_H1.json`, `RESULTS_H1.md` | machine-written |
| `METHODS_H1.md` | sources and methodology — written before the run |
| `ANALYSIS_H1.md` | interpretation — **after** the run |

## Runtime

**A100 40 GB.** ESM-2 650M over ~102 domains of 45–97 residues — one forward pass each plus a masked
scan. Minutes. Embeddings cache to Drive, so a disconnected session resumes without repeating the
GPU work.

## What it found

**Reproduction passed** — 0.5660 against E2's published 0.573, so the pipeline is the frozen one.

| arm | domains | median \|ρ\| | Δ vs SH3 | 95 % CI | verdict |
|---|---|---|---|---|---|
| MAIN length-matched | 35 | 0.420 | −0.203 | [−0.249, −0.120] | **inconclusive** |
| PDZ | 31 | 0.602 | −0.021 | [−0.082, +0.027] | *supported*, no verdict by design |

**Length is not the barrier.** PDZ's median construct is 88 residues against a training maximum of
72, in a family never seen, and it matches SH3. Part 6 anticipated the opposite cell.

The main arm's difficulty is not resolved. The two worst families coordinate zinc — a risk Part 7
named in advance — but Myb/SANT binds no metal and is also low, and assay quality runs in the same
order as the result (PDZ 3.27, SH3 2.20, main 1.86). **The two explanations cannot be separated with
this design**, and the new families have no second assay by construction.

## Status

Complete as pre-registered. Interpretation in `results/H1_generality/ANALYSIS_H1.md`. The
pre-registration is unsigned.
