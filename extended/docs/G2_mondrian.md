# G2 — Per-domain (Mondrian) conformal intervals

**Why it is needed.** The frozen run reports 89.9 % coverage for a 90 % interval. That is *marginal*
coverage, correct on average over all held-out variants, and B3's own stratified table shows the
per-domain spread is wide: **83.3 % on LYN against 95.0 % on FYN**. A 90 % interval that is 83 % on
one domain and 95 % on another is two instruments sharing a name.

**What it does not do.** It re-fits nothing, changes no prediction, and does not move `fold_lo >= 1`.
It recalibrates an interval and reports the consequence beside the published 410 rather than in place
of it. No pass/fail verdict, so no pre-registration.

## Inputs

| | |
|---|---|
| `heldout_predictions.parquet` (B1) | 27,590 variants, 15 genes, with `pred_c10` and `sd_c10` |
| `atlas_fold_predictions.parquet` (B1) | 6,884 atlas variants, 310 domains |

## Method

B3's procedure unchanged — `err / (sd + 0.05)`, the same 50/50 split at seed 0, the same quantile
index — first globally, to reproduce, then within each gene.

The global calibration is **asserted** before anything else runs: q90 = 6.8073 against 6.807,
coverage 89.92 % against 89.9 %, and 410 confident calls. A mismatch means the inputs changed.

## What it found

**The per-domain quantile ranges 5.42 (FYN) to 9.71 (LYN), a factor of 1.79.** Mondrian calibration
narrows the coverage spread from 11.8 pp to 6.3 pp; the residual is close to what sampling noise
alone produces at ~500 calibration points, where the 11.8 pp was structural.

The count of confident calls is robust:

| | calls |
|---|---|
| global q90 (published) | **410** |
| per-domain where calibrated, global elsewhere | 409 |
| each domain drawn from the observed spread (2,000 draws) | **400, 95 % interval 378–421** |
| every domain at min / max q90 | 613 / 149 — *not* the uncertainty, since no domain set can be all-extreme |

**The distinction that matters.** A *per-variant* 90 % claim is not reliable at the stated
confidence — on a LYN-like domain it is 83 %. The *aggregate count* is, moving only within ±8 %. The
threshold is for ranking and triage, not for a per-variant confidence statement, which is the same
conclusion E1 reached from sensitivity.

## Outputs

| | |
|---|---|
| `per_domain_q90_G2.csv` | per-gene q90, coverage under both calibrations |
| `metrics_G2.json` | including the resampled band on 410 |
| `ANALYSIS_G2.md` | interpretation and limitations |

## Runtime

Seconds on CPU. `python3 tools/g2_mondrian.py --root . --out results/G2_mondrian`
