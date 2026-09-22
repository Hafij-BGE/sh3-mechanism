# B1 — Analysis of the result: the folding predictor

**Colab run:** 2026-09-22, 18.4 min on a Tesla T4. **Verdict: REPRODUCED** — 8 values identical, 2 within
tolerance, 0 failed.
The run's own numbers are in `RESULTS_B1.md`, `metrics_B1.json` and `comparison_B1.csv`. The files it
produced are `models.pt`, `folding_per_domain_ci.csv`, `heldout_predictions.parquet`,
`atlas_fold_predictions.parquet` and `ablation.csv`.

> **One problem was found in the first run: the FoldX baseline (Section 7). It is fixed and re-run.**
> The headline results in Sections 1–6 are not affected.

---

## 1. Did B1 do its job?

B1 has to show that ΔΔG_fold can be predicted for **SH3 domains the model never saw**, and that it beats the
zero-shot ESM-2 score it is built on.

| Check | Result |
|---|---|
| Domains, per-domain median / min / max ρ, all CIs > 0, ESM median, domains won, held-out variants | **8 / 8 identical** (to 4 decimals) |
| Pooled ρ, pooled RMSE | **2 / 2 within tolerance** |
| New: sign-test p, IQR, pooled Pearson r, split sizes, ablation, error tables | reported for the first time |

**What this means.** Five networks were retrained from scratch on a GPU, and the per-domain median came out
at 0.8392 again. The folding result is stable, not a lucky seed.

---

## 2. The design: a clean leave-family-out test

| Split | Variants | Domains (groups) |
|---|---|---|
| Training (non-SH3 MegaScale) | 327,027 | 348 |
| Validation (whole held-out non-SH3 domains, for early stopping) | 34,451 | 38 |
| **Test: the entire SH3 family** | **27,590** | **15 genes** |

- **No SH3 domain is ever used for training or for early stopping.** The notebook asserts this: no SH3 group may appear in the training split.
- **Splits are grouped by domain** (UniProt accession + domain index). No domain has variants on both sides.
- **The model gets sequence features only** (ESM-2 embedding + 12 scalars). Structure is held back for the independent test in B2.

This is the strictest honest test available. It asks whether the model has learned the physics of folding in
general, or merely memorised families.

---

## 3. Main result: per held-out SH3 domain

Spearman ρ between predicted and measured ΔΔG_fold, with a 95 % bootstrap CI (2,000 resamples):

| Gene | n | ρ (model) | 95 % CI | ρ (zero-shot ESM) |
|---|---|---|---|---|
| OBSCN | 1,209 | 0.754 | 0.723–0.781 | −0.644 |
| PLCG1 | 1,091 | 0.772 | 0.744–0.798 | −0.660 |
| DOCK1 | 1,208 | 0.774 | 0.747–0.799 | −0.578 |
| SORBS1 (SH3 #2) | 1,210 | 0.797 | 0.773–0.819 | −0.617 |
| LYN | 1,014 | 0.822 | 0.797–0.845 | −0.524 |
| PTK6 | 1,125 | 0.829 | 0.808–0.847 | −0.629 |
| LCK | 983 | 0.837 | 0.816–0.856 | −0.557 |
| TEC | 1,072 | **0.839** (median) | 0.818–0.857 | −0.679 |
| NPHP1 | 2,212 | 0.842 | 0.825–0.857 | −0.599 |
| LASP1 | 1,045 | 0.844 | 0.825–0.862 | −0.606 |
| HCK | 1,034 | 0.845 | 0.823–0.865 | −0.603 |
| OSTF1 | 1,028 | 0.845 | 0.823–0.865 | −0.684 |
| BTK | 1,060 | 0.855 | 0.834–0.873 | −0.669 |
| SPTAN1 | 10,112 | 0.872 | 0.865–0.878 | −0.527 |
| FYN | 2,187 | 0.934 | 0.926–0.940 | −0.647 |

**Summary:** median ρ **0.839** (range 0.754–0.934, IQR 0.809–0.845).

**Interpretation:**
- **Folding is predictable for unseen SH3 domains.** Every domain is at ρ ≥ 0.75, and every lower CI bound is ≥ 0.72, far from zero.
- **The spread is narrow** (IQR 0.81–0.85). The model works on the family as a whole, not on a few easy members.
- **The model beats zero-shot ESM-2 on 15 of 15 domains** (median |ρ| 0.617 → 0.839; gain +0.22). A two-sided sign test gives p = 6.1 × 10⁻⁵ (= 2 × 0.5¹⁵, the smallest p possible with 15 domains). Supervised training on non-SH3 stability data adds real information beyond the language model.
- **The weakest domains** (OBSCN, PLCG1, DOCK1) are still at 0.75–0.77. FYN (0.934) and SPTAN1 (0.872) are the strongest. Both have several MegaScale backgrounds (2 for FYN, 10 for SPTAN1), which may help. This was not tested.
- **Why quote the per-domain median, not the pooled ρ.** Pooled over all 27,590 variants, ρ is 0.843 and RMSE 0.672 kcal/mol. But SPTAN1 alone contributes 10,112 variants (37 %), so a pooled number is dominated by one domain. The per-domain median weights every domain equally.

---

## 4. Cross-assay check: does it hold in a different experiment?

MegaScale measures stability by proteolysis. ddPCA measures it by abundance in cells (AbundancePCA). The
table uses reliable ddPCA folding energies:

| Domain | n | ρ (model) | ρ (zero-shot ESM) | Gain over ESM |
|---|---|---|---|---|
| GB1 | 878 | 0.827 | −0.199 | +0.63 |
| **GRB2-SH3** | 1,032 | **0.738** | −0.728 | **+0.01** |
| PSD95-PDZ3 | 1,199 | 0.530 | −0.481 | +0.05 |

**Interpretation — an honest nuance:**
- **The model transfers to a different assay.** ρ is 0.74 on GRB2-SH3, the only SH3 with ddPCA data. That is close to the MegaScale figure.
- **On GRB2-SH3, the model barely beats zero-shot ESM** (0.738 vs 0.728). ESM is already very good on this domain in this assay. The +0.22 gain in Section 3 is therefore a MegaScale result, and **the thesis should not claim the same gain for every assay.**
- **The largest gain is on GB1** (+0.63). ESM nearly fails on GB1 (−0.20), probably because it is a bacterial domain with a shallow alignment. The supervised head rescues it.
- **PDZ3 is the hardest** (0.53). It has a different fold and a longer domain (84 positions). It is not an SH3, so it does not affect the SH3 claims.

---

## 5. What each part of the model contributes (ablation, K1/K2)

Per-domain median ρ on the 15 held-out SH3 domains:

| Model | Features | Median ρ | Pooled ρ |
|---|---|---|---|
| Zero-shot ESM-2 score (no training) | 0 | 0.617 | 0.580 |
| MLP, ESM embedding only | 1,280 | 0.676 | 0.680 |
| MLP, 12 scalars only (no embedding) | 12 | 0.729 | 0.706 |
| Ridge regression, all features (α 1000) | 1,292 | 0.754 | 0.736 |
| MLP, embedding + first 5 scalars (3 ESM scores, position, domain length) | 1,285 | 0.761 | 0.766 |
| MLP, all features, one seed | 1,292 | 0.831 | 0.836 |
| **MLP, all features, 5-seed ensemble (the model)** | 1,292 | **0.839** | **0.843** |

**Interpretation:**
- **No single feature group is enough; the combination is.** The embedding alone reaches 0.68 and the scalars alone 0.73. Together they reach 0.83.
- **The 12 scalars carry a lot for their size.** They include three ESM scores and simple physico-chemical changes. The embedding adds the context of the position in the domain.
- **The substitution scalars matter.** Going from 5 scalars to all 12 (hydropathy, volume and charge changes, BLOSUM62, proline and glycine flags) lifts ρ from 0.76 to 0.83.
- **Non-linearity matters.** Ridge regression on the same 1,292 features reaches 0.754; the MLP reaches 0.831 (+0.08). The relationship is not linear.
- **The ensemble adds a little** (0.831 → 0.839). Its main value is the seed spread used for uncertainty, which B3 replaces with conformal intervals.
- **Single-seed rows are compared with the single-seed full model (0.831), not with the ensemble.**

---

## 6. Where the model is wrong (J4)

**By substitution type.** Bias = mean(predicted − measured); negative means the model under-predicts damage.

| Substitution | n | ρ | MAE | Bias |
|---|---|---|---|---|
| **From glycine** | 1,898 | **0.694** | **0.705** | **−0.272** |
| To proline | 1,185 | 0.800 | 0.610 | −0.031 |
| Hydrophobic → polar | 2,820 | 0.848 | 0.555 | +0.033 |
| To glycine | 1,331 | 0.864 | 0.489 | −0.037 |
| Other | 16,006 | 0.823 | 0.471 | −0.051 |
| Polar → hydrophobic | 4,350 | 0.747 | 0.414 | −0.041 |

- **Mutations away from glycine are the weak spot.** They have the lowest ρ and the highest error, and damage is systematically under-predicted (−0.27 kcal/mol). Glycine is often needed for its backbone flexibility, for example in turns with unusual φ/ψ angles. None of the features describes backbone geometry.
- **Proline substitutions have the second-highest error.** Proline breaks backbone hydrogen bonds, again a geometric effect.
- **Burial-type changes are predicted well** (hydrophobic → polar, ρ 0.85).

**By measured effect size:**

| Measured ΔΔG_fold | n | ρ within bin | MAE | Bias |
|---|---|---|---|---|
| Stabilising (< 0) | 4,955 | 0.201 | 0.489 | **+0.465** |
| 0–1 | 9,791 | 0.482 | 0.314 | +0.044 |
| 1–2 | 6,362 | 0.348 | 0.523 | −0.146 |
| 2–3 | 4,166 | 0.287 | 0.628 | −0.315 |
| > 3 kcal/mol | 2,316 | 0.358 | **0.941** | **−0.866** |

- **The predictions are compressed towards the middle.** Stabilising mutations are predicted as slightly destabilising (+0.47). The strongest destabilisers are under-predicted by 0.87 kcal/mol. This is the usual regression to the mean of a model trained with squared error.
- **Low ρ within each bin is expected.** Restricting the range lowers any correlation. The model ranks variants well across the whole range, not within narrow bands.
- **Consequence for the thesis:** the model is **conservative for severe variants.** When B3 calls a cancer variant destabilising (lower bound ≥ 1 kcal/mol), the true effect is, on average, at least as large. The model also **cannot identify stabilising mutations** reliably.

---

## 7. Against conventional predictors (J6) — bug found, fixed, and re-run

**Re-run on 2026-09-22 (1.5 min).** Training was skipped, because the saved `models.pt` and `ablation.csv`
were reloaded. All headline numbers came out identical, and only this table changed.

Spearman ρ with measured ΔΔG_fold, on variants that all four methods score (ESM sign flipped, so higher = better):

| Domain | Common variants | Head | Zero-shot ESM | FoldX | EVE | FoldX offset |
|---|---|---|---|---|---|---|
| GB1 | 836 | **0.825** | 0.204 | 0.487 | 0.370 | +1 |
| GRB2-SH3 | 877 | **0.761** | 0.728 | 0.701 | 0.638 | 0 |
| PSD95-PDZ3 | 1,080 | 0.540 | 0.480 | 0.466 | **0.589** | +310 |

**Interpretation:**
- **The head is the best method on both GB1 and GRB2-SH3.** It needs neither a structure (unlike FoldX) nor a deep alignment (unlike EVE).
- **On PDZ3, EVE is better** (0.589 vs 0.540). The head is not best everywhere: on the non-SH3 domain that is hardest for it, a family-specific alignment model wins. This is to be reported as it is.
- **On GB1, FoldX and EVE are weak** (0.49 and 0.37), and ESM almost fails (0.20). The head (0.83) is far ahead.

**What the bug was.** The FoldX files number residues as in the PDB structure (GB1 +1, PDZ3 +310). The first
run joined them to ddPCA by raw residue ID. PDZ3 therefore had 0 matches, and GB1 had 69 variants paired with
the neighbouring residue's FoldX value (FoldX ρ −0.13). B1 now derives each offset from the wild-type
residues. The derived offsets (0 / +1 / +310) equal those A2 derived from the PDB structures.

**Corrected FoldX vs MoCHI folding (Pearson r), which replaces A1's 0.494:**

| All three domains | GB1 | GRB2-SH3 | PSD95-PDZ3 |
|---|---|---|---|
| **0.418** (2,879 variants) | 0.375 | 0.517 | 0.351 |

A1's 0.494 (1,024 variants) was mostly correctly aligned GRB2-SH3 rows plus some misaligned GB1 rows. With
correct alignment, FoldX agrees with the measured folding energies at r 0.42 overall.

## 8. Limitations

- **The test is MegaScale-on-MegaScale** (a different family, same assay). Section 4 shows that the gain over ESM is much smaller in another assay for GRB2-SH3.
- **Predictions are compressed:** strong destabilisers are under-predicted, and stabilising mutations are not detected.
- **Glycine and proline substitutions are the weakest** (backbone effects).
- **15 held-out domains from 26 structures.** Some have 50–60 % identity to the human domain. They represent the SH3 family, but not every human SH3.

---

## 9. Conclusion and what to do now

- **Folding is predictable for SH3 domains never seen in training:** per-domain median ρ 0.839, all 15 above 0.75, beating zero-shot ESM-2 on 15 of 15 (p = 6.1 × 10⁻⁵).
- **The model is conservative for severe mutations and weakest at glycine.** Both points are to be stated in the thesis.
- **In the independent ddPCA assay it transfers** (ρ 0.74 on GRB2-SH3), but the gain over ESM there is small.

**Next:** run `B2_structural_check` (CPU, about 1 min).
