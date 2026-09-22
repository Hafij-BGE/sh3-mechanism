# C2 — Binding within one domain (Stages 3b and 3c)

**Question.** With transfer removed, can binding be learned inside a single domain? And is a single
fit trustworthy?

## Protocol
- **Folds:** 7-fold cross-validation **grouped by position**, so the model never sees another
  substitution at a held-out position and cannot interpolate.
- **Early stopping:** on an inner validation split, also grouped by position. The first Stage 3b run
  stopped on the test fold, which is leakage.
- **Preprocessing:** variance-floored scaler (the 1e-6 floor made training diverge), whitened
  64-component PCA, clipping at ±10.
- **Models:** three seeds per fold.
- **Repeats:** six per domain. A single fit is what Stage 3b reported, and a bootstrap of its
  predictions cannot show how much the answer depends on the split itself.

## Partition modes
Stage 3b and 3c assigned positions to folds with scikit-learn's `GroupKFold`, which is
deterministic (shuffling only exists from version 1.6, and is off by default). All six "repeats"
therefore used **the same partition**; only the inner split and the seeds varied.
- **original** reproduces that.
- **corrected** shuffles the positions with each repeat's seed.

## Decision file
`binding_decision.json` records whether the trained head beats zero-shot ESM-2 on GRB2-SH3 in either
mode. B3 reads it.

## Expected result (original)
| Domain | Positions | Single fit | Six repeats: median [range] | ESM |
|---|---|---|---|---|
| PSD95-PDZ3 | 84 | +0.391 | +0.397 [+0.363, +0.412] | −0.438 |
| GRB2-SH3 | 56 | +0.124 | −0.030 [−0.109, +0.124] | −0.126 |
| GB1 | 55 | −0.085 | +0.009 [−0.118, +0.197] | +0.042 |

The +0.124 that Stage 3b reported is the top of GRB2-SH3's range, not its typical value.
