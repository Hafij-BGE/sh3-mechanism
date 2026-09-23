# Mechanism-resolved prediction of cancer mutation effects in human SH3 domains

*Distinguishing loss of fold from the limits on predicting rewiring of binding.*
Master's thesis project — Hafijur Rahman.

For a cancer missense mutation in a human SH3 domain, does it **destabilise the fold**, or leave the
fold intact and **change binding**? This repository rebuilds every result **from the raw data**,
starting with the COSMIC atlas, in 14 Colab notebooks, plus one follow-up notebook (F1) that plans
experimental validation. Each notebook comes with an explanation file, and each run writes a results
report automatically.

## The pipeline

| Part | Programs |
|---|---|
| **A. Initial data processing** | A0 cancer atlas from raw COSMIC · A1 measured folding/binding energies · A2 features |
| **B. Main task: loss of fold** | B1 folding predictor · B2 structural check · B3 intervals and calls · B4 external validation · B5 cancer biology · B6 virtual saturation mutagenesis |
| **C. Why binding cannot be predicted** | C1 across domains · C2 within a domain · C3 positions, not rows · C4 an independent specificity axis |
| **D. Figures and verification** | D1 |
| **F. Follow-up (reads results only)** | F1 experimental validation candidates · F2 figures for the candidate panel |

Start with [`docs/00_pipeline_overview.md`](docs/00_pipeline_overview.md).
A paper-style write-up of the whole project is in [`docs/REPORT.md`](docs/REPORT.md).

## Headline results (recorded run; re-checked by every notebook)

- **Folding is predictable.** Per-domain median Spearman ρ 0.839 on 15 SH3 domains held out as a
  family; the head beats zero-shot ESM-2 on 15 of 15.
- **It is specific to folding.** Predicted damage follows burial (ρ +0.712), not the binding
  interface (ρ +0.037). Structure was never a model input.
- **Binding is not predictable for SH3 from current data**, and the reason is quantified.
  Predictability needs about 80 distinct mutated positions; an SH3 domain has 56–60. The fix is
  more domains, not more mutations.
- **The cancer biology is null.** 1 of 170 genes and 0 of 22 tumour sites enriched against a
  burial-matched null. The atlas is a mechanism map, not a driver list.
- **Stage 0 rebuilds the original atlas byte-for-byte** from raw COSMIC.
- **410 cancer variants (6 %) are confidently destabilising** (lower 90 % conformal bound ≥ 1 kcal/mol).
- **An independent specificity axis (C4, 154 PWMs) did not pass its pre-registered rule,** so no rewiring
  claim is made.
- **Observed cancer variants are depleted of fold-breaking substitutions** against a domain-matched
  single-nucleotide background (5.9 % vs 9.2 %, B6). Consistent with purifying selection; mutational
  context is not modelled.

## Status of the full Colab run (2026-09-22)

All 14 programs ran from raw data. **All 187 recorded values reproduced** (160 identical, 27 equal to the
recorded decimals or within tolerance). B3's axis correlation differs by 3 × 10⁻⁷ (tie ordering), which
changes no call; its tolerance was set to 10⁻⁶ and B3/D1 re-run. Four problems were found and fixed on the way:
- FoldX residue numbering (FoldX vs measured r corrects from 0.494 to 0.418);
- an absolute-value "beats ESM" comparison;
- a table-grouping error in C3;
- that tolerance.

Details: [`results/D1_figures_and_verification/ANALYSIS_D1.md`](results/D1_figures_and_verification/ANALYSIS_D1.md).
Critical comparison with the previous run: [`results/CRITICAL_ANALYSIS.md`](results/CRITICAL_ANALYSIS.md).
Next improvements: [`results/RECOMMENDATIONS.md`](results/RECOMMENDATIONS.md).

## How to run

1. Upload the inputs to Drive (see `UPLOAD_GUIDE.md`, kept outside the repository; about 8 GB, 17 items).
2. Run the notebooks in the order given there (about 2.5 h; GPU for 7 of them). F1 and F2 are optional and
   run last, in seconds.
3. Download `results/` and commit it (see `GITHUB_GUIDE.md`, kept outside the repository).
4. Read the results: [`results/README.md`](results/README.md) explains the two report files in every
   program folder (`RESULTS_<ID>.md`, written by the run; `ANALYSIS_<ID>.md`, the interpretation).

## Repository layout

```
notebooks/   16 Colab notebooks (generated from tools/nb_*.py; do not edit by hand)
src/         sh3_common.py (shared code), sh3_atlas.py (Stage 0), run_tests.py
docs/        one explanation per program + overview + roadmap status
reference/   expected_values.json (187 recorded values), checksums.md5, data_manifest.json
results/     after a run: RESULTS_<ID>.md + ANALYSIS_<ID>.md per program, metrics, small tables, figures
tools/       notebook generator
```

## Re-checking found three procedural flaws; all are kept visible

- **Binding folds:** cross-validation used unshuffled `GroupKFold`, so "repeats" shared one
  partition. Both procedures now run side by side.
- **Leakage in Stage 3:** the cross-domain binding head used the test domain for early stopping.
  The original is kept for the record, beside a corrected version.
- **Confidence filter:** the seed-spread filter passed 6,880 of 6,884 variants. It is replaced by
  conformal intervals.

**Data are not in this repository.** COSMIC's licence forbids redistribution. Raw archives,
per-variant tables, embeddings and model weights stay on Drive (see `.gitignore`).
