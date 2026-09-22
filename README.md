# Mechanism-resolved prediction of cancer mutation effects in human SH3 domains

*Distinguishing loss of fold from the limits on predicting rewiring of binding.*
Master's thesis project — Hafijur Rahman.

For a cancer missense mutation in a human SH3 domain, does it **destabilise the fold**, or leave the
fold intact and **change binding**? This repository rebuilds every result **from the raw data**,
starting with the COSMIC atlas, in 14 Colab notebooks. Each notebook comes with an explanation file,
and each run writes a results report automatically.

## The pipeline

| Part | Programs |
|---|---|
| **A. Initial data processing** | A0 cancer atlas from raw COSMIC · A1 measured folding/binding energies · A2 features |
| **B. Main task: loss of fold** | B1 folding predictor · B2 structural check · B3 intervals and calls · B4 external validation · B5 cancer biology · B6 virtual saturation mutagenesis |
| **C. Why binding cannot be predicted** | C1 across domains · C2 within a domain · C3 positions, not rows · C4 an independent specificity axis |
| **D. Figures and verification** | D1 |

Start with [`docs/00_pipeline_overview.md`](docs/00_pipeline_overview.md).

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

## How to run

1. Upload the inputs to Drive: [`UPLOAD_GUIDE.md`](UPLOAD_GUIDE.md) (about 8 GB, 18 items).
2. Run the notebooks in the order given there (about 3.5 h; GPU for 7 of them).
3. Download `results/` and commit it: [`GITHUB_GUIDE.md`](GITHUB_GUIDE.md).

## Repository layout

```
notebooks/   14 Colab notebooks (generated from tools/nb_*.py)
src/         sh3_common.py (shared code), sh3_atlas.py (Stage 0), run_tests.py
docs/        one explanation per program + overview + roadmap status
reference/   expected_values.json (187 recorded values), checksums.md5, data_manifest.json
results/     filled after a run: RESULTS_<ID>.md, metrics, small tables, figures
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
