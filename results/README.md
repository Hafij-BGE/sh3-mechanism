# Results — how to read this folder

One folder per program, named as in `src/sh3_common.py` (`PROGRAM_DIRS`). Each folder holds two reports.

| File | Written by | What it is |
|---|---|---|
| `RESULTS_<ID>.md` | the notebook, automatically | The numbers of that run, every table, and the check against the recorded original run (identical / within tolerance / DIFF / new). Nothing typed by hand. |
| `ANALYSIS_<ID>.md` | written after the run | What the numbers mean: design, interpretation, limitations, any problem found and how it was fixed, and the next step. |
| `metrics_<ID>.json` | the notebook | All metrics plus run metadata (date, minutes, library versions, GPU). |
| `comparison_<ID>.csv` | the notebook | Metric by metric: this run, recorded value, status. |
| other `.csv`, `.png`, `.pdf` | the notebook | Small tables and figures. See each notebook's header for the list. |

`RESULTS_SUMMARY.md` (from D1) summarises the whole run on one page.

## Read in this order

0. `CRITICAL_ANALYSIS.md`: every experiment compared with the previous run; what improved and what did not.
0b. `RECOMMENDATIONS.md`: what to improve next, ranked by value and effort.
1. `D1_figures_and_verification/ANALYSIS_D1.md`: the whole run, what reproduced, what was fixed.
2. `A0` → `A1` → `A2`: the data.
3. `B1` → `B2` → `B3` → `B4` → `B5` → `B6`: loss of fold, the confident claims.
4. `C1` → `C2` → `C3` → `C4`: why binding cannot be predicted (a quantified negative result).
5. `F1`: experimental validation candidates, and `F2`: their figures (optional follow-up).

## The run of 2026-09-22 at a glance

| Program | Verdict | Key number |
|---|---|---|
| A0 | reproduced, byte-identical atlas | 6,884 variants, 310 domains, 235 genes |
| A1 | reproduced | buried core: ΔΔG_fold 3.57 vs ΔΔG_bind 0.14 kcal/mol |
| A2 | reproduced | 399,640 variants × 1,292 features |
| B1 | reproduced (FoldX baseline fixed) | per-domain median ρ 0.839; beats ESM-2 on 15/15 |
| B2 | reproduced | damage vs burial ρ +0.712; vs interface +0.037 |
| B3 | reproduced (7 identical, 1 within tolerance) | 410 confidently destabilising |
| B4 | reproduced | a domain-scale specialist; ESM-2 is better on abundance assays |
| B5 | reproduced | 1/170 genes, 0/22 tumour sites enriched |
| B6 | new | cancer variants depleted of damage: 5.9 % vs 9.2 % |
| C1 | reproduced (win count fixed) | GRB2-SH3 corrected ρ −0.042 |
| C2 | reproduced | PDZ3 learnable (about 0.37–0.40); GRB2-SH3 about 0 |
| C3 | reproduced (table fixed) | predictability from about 76 positions; SH3 has 56 |
| C4 | new, **not validated** | centred r +0.288, but 55/115 wins vs the average profile |
| D1 | **187 / 187 recorded values reproduced** | — |
| F1 | new, follow-up | 10 destabilising picks + 10 same-domain controls; no rewiring panel (C4 not validated) |
| F2 | new, figures | picks above the 99.65th atlas percentile; 8/10 buried; cover 6 of 56 aligned positions (4 at position 5) |

## What is not here, and why

The atlas (`SH3_cancer_master.tsv`), every `.parquet` (per-variant predictions and features), embeddings
(`.npz`), model weights (`.pt`), AlphaFold models (`.cif`) and `F1/experimental_candidates.csv` stay on
Drive. They are either COSMIC-derived per-variant data, which the licence forbids redistributing, or too large
for GitHub. `.gitignore` enforces this.
