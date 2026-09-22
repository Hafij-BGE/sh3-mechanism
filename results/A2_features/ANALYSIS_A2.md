# A2 — Analysis of the result: features for every variant

**Colab run:** 2026-09-22, 20.9 min on a Tesla T4. **Verdict: REPRODUCED** — 8 values identical, 13 within
tolerance, 0 failed.
The run's own numbers are in `RESULTS_A2.md`, `metrics_A2.json` and `comparison_A2.csv`. The tables it
produced are `features_{megascale,ddpca,atlas}.parquet`, `esm_scores.parquet`, `esm_domain_embeddings.npz`,
`esm_logodds.npz`, `structure_features.csv`, `cross_fold_separation.csv` and `alphafold_log.csv`. The
AlphaFold models are cached in `cache/`.

---

## 1. Did A2 do its job?

A2 turns every variant into the numbers the models use, and adds structural labels (burial, interface,
reference-frame position) for testing.

| Check | Result |
|---|---|
| Variant counts (total, MegaScale, ddPCA, atlas), ESM domains, structure rows and domains, atlas groups | **8 / 8 identical** |
| Zero-shot ESM ρ, structure coverage, reference-frame coverage, cross-fold separation (8 medians) | **13 / 13 within tolerance** (4th-decimal rounding only) |
| Variants dropped by the residue check | **0** of 399,640 |
| New: proteins without an AlphaFold model | 9 |

**What this means.** The feature matrix that B1–B6 and C1–C4 use is the same as in the original run. ESM-2 on
a GPU is not always bit-for-bit deterministic, but every derived quantity agrees to the recorded precision.

---

## 2. The variant table

| Set | Variants | Domains | Role |
|---|---|---|---|
| MegaScale | 389,068 | 412 | Training set for folding (B1) |
| ddPCA | 3,688 | 3 | Training and test set for binding (C1–C3); test set for folding |
| Cancer atlas | 6,884 | 310 | What the thesis predicts (B3, B5, B6) |
| **Total** | **399,640** | **725** | |

**0 dropped.** Every variant's wild-type residue matched its sequence, so no data were lost when three
different sources were merged. A1 and A0 had already checked this; A2 confirms it after the merge.

---

## 3. The features: 1,292 numbers per variant

- **1,280** come from the ESM-2 650M embedding of the mutated position. There is **one pass per wild-type domain** (725 passes), not one per variant, which makes 399,640 variants feasible on a T4 in about 7 minutes (the ESM files were written 7 min after the start).
- **12 scalars:**
  - ESM: the log-odds score, the wild-type log-probability and the entropy at the position;
  - position: relative position in the domain, and domain length;
  - substitution: the changes in hydropathy, volume and charge, the BLOSUM62 score, and three flags (to proline, from glycine, to glycine).

**Structure is not a model input.** Burial and interface are computed below only as *labels*, used to test
what the model learned (B2). If structure were an input, B2's result would be circular.

---

## 4. Zero-shot ESM-2: the baseline before any training

Spearman correlation between the ESM log-odds and the measured ΔΔG:

| Set | Target | n | ρ |
|---|---|---|---|
| ddPCA | ΔΔG_fold | 3,688 | **−0.404** |
| ddPCA | ΔΔG_bind | 3,368 | **−0.259** |
| MegaScale | ΔΔG_fold | 389,068 | **−0.388** |

**Interpretation:**
- **The sign is expected to be negative.** A high log-odds means the language model finds the substitution acceptable, and a high ΔΔG means damage. Negative ρ is the correct direction.
- **ESM tracks folding better than binding:** |ρ| 0.40 vs 0.26 on the same ddPCA variants. This is the gap the thesis is about. Evolution constrains the fold everywhere, but binding specificity depends on the partner, which a sequence-only model cannot see.
- **This is the number B1 must beat.** In the recorded run, the trained folding head beat zero-shot ESM-2 on 15 of 15 held-out SH3 domains.

---

## 5. Structures: AlphaFold models, burial, interface

| | |
|---|---|
| Atlas variants with a structure | **96.8 %** |
| Atlas variants mapped to the GRB2-SH3 reference frame (56 positions) | **89.5 %** |
| Structure rows / domains | 18,760 / 302 |
| ddPCA PDB offsets (derived by alignment) | GRB2-SH3 2VWF: 0 (identity 0.982) · PSD95-PDZ3 1BE9: 310 (0.988) · GB1 2GB1: 1 (0.982) |

**Nine proteins have no AlphaFold model.** All are very large — 2,871 to 8,525 residues — and AlphaFold DB
splits them into fragments. Only fragment F1 is requested, so the SH3 domain is missing.

| Protein | Gene | Length | Atlas variants |
|---|---|---|---|
| O75962 | TRIO | 3,097 | 54 |
| Q5VST9 | OBSCN | 7,968 | 38 |
| Q15149 | PLEC | 4,684 | 27 |
| Q9UKN7 | MYO15A | 3,530 | 26 |
| P15924 | DSP | 2,871 | 22 |
| Q03001 | DST | 7,570 | 22 |
| P20929 | NEB | 8,525 | 12 |
| Q9UPN3 | MACF1 | 7,388 | 10 |
| O60229 | KALRN | 2,986 | 8 |
| **Total** | | | **219 variants, 11 domains** |

219 of 6,884 = 3.2 %, which is exactly the missing 100 − 96.8 %.

**Consequences:**
- **These variants still get fold predictions** (B1 and B3), because the model uses only sequence.
- **They are left out of the burial-based analyses:** B2 and the burial-matched null in B5.
- **One effect to keep in mind:** TRIO Q2579R, one of the most recurrent non-hypermutated variants in A0 (24 samples), is in this group. It has a fold prediction but no burial label.
- **Possible fix, as future work:** request the AlphaFold fragment that contains the SH3 domain, not just F1.

**Reference-frame mapping at 89.5 %:** about 1 in 10 atlas variants falls at a position that has no
equivalent in the 56-position GRB2-SH3 frame. Most likely these are insertions in longer SH3 domains (domains range from 50 to 87 residues).
These variants are simply absent from the per-position tables.

The PDB offsets are **derived** by aligning the ddPCA sequence to the structure, all with identity > 98 %.
The PDZ3 offset (310) matches the one A1 derived independently from the Chi 2008 data. Two separate routes
give the same number, which confirms the numbering.

---

## 6. Cross-fold separation: does A1's premise hold beyond one domain?

GRB2-SH3 and PSD95-PDZ3 pooled, reliable binding only; median ΔΔG (kcal/mol):

| Residue class | ΔΔG_fold | ΔΔG_bind | Which energy it hits | GRB2-SH3 alone (A1): fold / bind |
|---|---|---|---|---|
| Surface, not interface | 0.72 | 0.12 | Neither much | 0.87 / −0.04 |
| Surface, interface | 0.45 | 0.68 | Binding slightly | 0.57 / 0.65 |
| **Buried, not interface** | **2.09** | 0.54 | **Folding** | 3.57 / 0.14 |
| **Buried, interface** | 0.98 | **1.45** | **Binding** | 1.28 / 2.90 |

**Interpretation:**
- **The same pattern holds across two different folds** (β-barrel SH3 and PDZ). Buried core residues → folding; buried binding-site residues → binding. The premise is not a quirk of GRB2-SH3.
- **The contrast is weaker in the pooled table** (2.09 vs 3.57; 1.45 vs 2.90). Two things contribute:
  - this table keeps only variants with *reliable binding*, which may remove some strongly destabilising core variants (not tested);
  - PDZ3 has a different energy scale.
- The direction is identical in every class.

---

## 7. Limitations

- **ESM-2 embeddings on GPU** can differ in the last digits between runs or hardware. All derived quantities matched to the recorded precision, but the saved embeddings are not guaranteed bit-identical.
- **9 proteins (219 variants) lack structure.** They are the largest proteins in the atlas, so the missingness is not random with respect to protein size.
- **AlphaFold models are predictions, not experimental structures.** Burial from a model is reliable for a well-folded SH3 domain, but less so in low-confidence regions.
- **10.5 % of atlas variants are outside the 56-position reference frame,** so position-wise comparisons use only 89.5 %.

---

## 8. Conclusion and next step

- **All 399,640 variants have their 1,292 features, identical to the original run.**
- **Zero-shot ESM already shows the thesis in miniature:** folding is tracked better (|ρ| 0.40) than binding (0.26).
- **Structural labels cover 96.8 % of the atlas.** The missing 3.2 % are nine giant proteins.
- **The fold/binding separation by structure** is confirmed across two protein folds.

**Next: B1 — the folding model. It needs a T4 GPU (about 25 min).** It trains the 5-seed folding head on
non-SH3 MegaScale data, tests it on the held-out SH3 family, and compares it with zero-shot ESM-2, FoldX and
EVE.
