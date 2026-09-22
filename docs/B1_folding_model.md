# B1 — The folding predictor

**Purpose.** Show that ΔΔG_fold can be predicted for SH3 domains the model has never seen, and that
supervision adds to what the zero-shot ESM-2 score already knows.

## Design
- **Model:** 1292 → 512 → 128 → 1 network on frozen ESM-2 features; AdamW with a cosine schedule,
  30 epochs; the epoch with the best validation RMSE is kept. Five seeds, averaged.
- **Training data:** the ~361,000 **non-SH3** MegaScale variants. Validation uses whole held-out
  domains (10 % of groups).
- **Test data:** the entire SH3 family (15 genes, 27,590 variants). The claim is therefore
  "generalises to an unseen family", not "to a held-out member of a known family".
- **Grouping:** UniProt accession + domain index. The notebook asserts that no SH3 group reached
  training.

## Evaluation
- **Per domain, never pooled only.** Spearman ρ for each of the 15 domains with a 2,000-resample
  bootstrap CI. SPTAN1 alone contributes a third of the pooled variants.
- **Same variants, zero-shot ESM-2 alongside.** Wins are counted and tested with an exact
  two-sided sign test: 12 of 15 wins are needed for p < 0.05.
- **Cross-assay check:** the head scored on ddPCA folding energies, a different assay from the
  training data.

## Robustness checks (from the upgrade roadmap; they do not change the model)
| Check | Question |
|---|---|
| Feature ablation (K1) | Embedding only, embedding + ESM scalars, and scalars only: what does each group contribute? |
| Ridge regression (K2) | Does a linear model on the same features do as well? If so, the MLP is not the point. |
| Error breakdown (J4) | Which substitution types and effect sizes does it get wrong? |
| FoldX and EVE (J6) | How does it compare with a structure-based and an alignment-based predictor on the ddPCA domains? EVE and FoldX numbering are converted to construct numbering by offsets derived from the wild-type residues. FoldX uses PDB numbering: GB1 +1, PDZ3 +310. The first run joined it by raw number; fixed on 2026-09-22 (FoldX vs measured r 0.494 → 0.418). |

## Outputs
`models.pt`, `folding_per_domain_ci.csv`, `heldout_predictions.parquet`,
`atlas_fold_predictions.parquet`, `ablation.csv`, `RESULTS_B1.md`.

## Expected result (recorded run)
Per-domain median ρ **0.839** (0.754–0.934); all 15 CIs exclude zero; the head beats ESM-2
(median |ρ| 0.617) on **15 of 15** domains.
