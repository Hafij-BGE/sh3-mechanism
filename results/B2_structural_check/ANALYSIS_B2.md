# B2 — Analysis of the result: is it really a folding predictor?

**Colab run:** 2026-09-22, 0.2 min on CPU. **Verdict: REPRODUCED** — 3 of 3 values identical.
The run's own numbers are in `RESULTS_B2.md`, `metrics_B2.json` and `comparison_B2.csv`. The tables it
produced are `position_predictions.csv` and `position_structure_check.csv`.

---

## 1. The question

B1 showed that the model predicts measured folding energies well. But a model can score well for the wrong
reason, for example by learning a general "this substitution is bad" signal that mixes folding and binding.
B2 asks:

> If the model has really learned **folding**, its predicted damage must follow **burial** (the core holds the
> fold together) and must **not** follow the **binding interface** (which matters for binding, not folding).

**Why this is an independent test.** Structure was **never a model input**. The model saw only sequence
features. If burial nevertheless emerges from its predictions, the model found the physics of folding by
itself.

**How it is done.**
1. Every atlas variant is placed on the 56-position GRB2-SH3 reference frame (from A2).
2. The predicted ΔΔG_fold (from B1) is averaged per position.
3. That average is correlated across positions with two things:
   - **burial**: 1 − relative solvent accessibility;
   - **closeness to the bound peptide**: −distance in the solved GRB2-SH3 complex.
4. Only positions with ≥ 10 atlas variants are used, which leaves all 56.

---

## 2. Did B2 reproduce?

| Quantity | This run | Recorded | Status |
|---|---|---|---|
| Positions | 56 | 56 | identical |
| ρ, predicted damage vs burial | **+0.7117** | +0.7117 | identical |
| ρ, predicted damage vs interface | **+0.0370** | +0.0370 | identical |

B2 has no randomness. It depends only on the B1 predictions and the A2 structures, and both were reproduced
exactly, so identical values are expected. They confirm that the whole chain A0 → A2 → B1 → B2 gives the same
result.

---

## 3. Main result: burial yes, interface no

| Test (56 positions) | Spearman ρ |
|---|---|
| Predicted fold damage vs **burial** | **+0.712** |
| Predicted fold damage vs **binding interface** | **+0.037** |
| Ratio | **19×** |

**Interpretation:**
- **The model's predicted damage follows burial strongly** (ρ +0.71). Positions in the core of the SH3 fold get high predicted ΔΔG_fold; exposed positions get low values. This is what a folding predictor must do.
- **It is blind to the binding interface** (ρ +0.04, which is essentially zero). Positions that contact the peptide ligand are not predicted as more damaging to the fold than any other position.
- **So the model has learned folding specifically, not general "badness".** Had it learned a mixed signal, interface positions would also score high.
- **This is exactly the property the thesis needs.** A high predicted ΔΔG_fold can be read as "this variant breaks the fold". It does not mean "this variant disrupts binding", and binding needs its own analysis (Part C).

---

## 4. The same pattern in the four structural classes

Median predicted ΔΔG_fold per class (a class median over position averages), next to the measured values from
A1:

| Residue class | Positions | **Predicted** ΔΔG_fold | Measured ΔΔG_fold (A1) | Measured ΔΔG_bind (A1) |
|---|---|---|---|---|
| Surface, not interface | 28 | 0.63 | 0.87 | −0.04 |
| Surface, interface | 12 | 0.52 | 0.57 | 0.65 |
| **Buried, not interface** | 13 | **1.40** | **3.57** | 0.14 |
| Buried, interface | 3 | 1.21 | 1.28 | **2.90** |

**Interpretation:**
- **Predicted damage is highest in the buried non-interface core** (1.40), just as the measured folding energy is (3.57). The model ranks the classes in the same order as the experiment.
- **Surface interface positions get the lowest predicted damage** (0.52), although their measured *binding* cost is real (0.65). The model correctly does not call them fold-breaking.
- **Buried interface positions** (only 3) get an intermediate value (1.21), matching their measured *folding* cost (1.28), not their much larger *binding* cost (2.90). The model reports only the folding part of their effect, which is correct.
- **The predicted values are smaller than the measured ones** (1.40 vs 3.57 in the core). This is the compression found in B1: strong destabilisers are under-predicted. The *ranking* is right; the *size* is conservative.

---

## 5. Per variant, on each protein's own structure

This uses each atlas variant's own AlphaFold model instead of the GRB2 reference frame:

| Variant class (own structure) | Variants | Median predicted ΔΔG_fold |
|---|---|---|
| **Buried** | 2,257 | **1.16** |
| Surface | 4,408 | 0.38 |
| No structure (the 9 giant proteins from A2) | 219 | 0.66 |

- **Buried cancer variants are predicted about 3× more damaging than surface ones** (1.16 vs 0.38). The result holds on each protein's own structure, not only on the GRB2 reference.
- **About one third of atlas variants (33 %) are buried.** These are the main candidates for loss-of-fold, which B3 turns into calls with confidence intervals.
- **The 219 variants without a structure** fall in between (0.66), as expected for a mix of buried and surface positions.

---

## 6. Limitations

- **56 positions.** The correlations are over positions, not variants, so each rests on 56 points. ρ +0.71 is far from zero at n = 56. ρ +0.04 is not distinguishable from zero, which is the claim.
- **One reference structure for interface.** Burial and interface come from the GRB2-SH3 complex with one peptide. Other SH3 domains bind different peptides, sometimes with non-canonical surfaces. The interface test therefore asks about the *canonical* SH3 peptide-binding site.
- **Only 3 buried interface positions.** That class median is shown for completeness; it carries little weight.
- **Position averages hide variation within a position.** Different substitutions at the same position can differ a lot. B3 works variant by variant.

---

## 7. Conclusion and next step

- **The folding predictor passes an independent structural test.** Its predicted damage follows burial (ρ +0.71) and ignores the binding interface (ρ +0.04), although it never saw a structure.
- **A high predicted ΔΔG_fold can be interpreted as loss of fold, specifically.**
- **Buried cancer variants are predicted about 3× more damaging than surface ones.**

**Next: C1 — binding across domains (T4 GPU, about 3 min).** This starts Part C: can binding be predicted at all?
