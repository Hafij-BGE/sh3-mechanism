# A1 — Analysis of the result: the measured ground truth

**Colab run:** 2026-09-22, 1.4 min. **Verdict: REPRODUCED** — 15 values identical, 11 within tolerance, 0 failed.
The run's own numbers are in `RESULTS_A1.md`, `metrics_A1.json` and `comparison_A1.csv`. The tables it
produced are `ddpca_ground_truth.parquet`, `megascale_singles.parquet`, `megascale_sh3_matches.csv`,
`separation_table.csv`, and the baselines `baseline_foldx.csv`, `baseline_eve.csv` and
`baseline_msa_conservation.csv`.

---

## 1. Did A1 do its job?

A1 turns the published experiments into the **measured energies** that every later model is trained on or
tested against. It then checks their sign against independent in-vitro measurements.

| Check | Result |
|---|---|
| Row counts (ddPCA singles, both energies, reliable binding/folding, per domain; MegaScale singles, domains, SH3 structures, SH3 genes; FoldX overlap) | **15 / 15 identical** |
| Real-valued quantities (calibration r, separation medians, FoldX r) | **11 / 11 within tolerance.** The differences are rounding only: the recorded values had 3 decimals, and the new run keeps 4. |
| New quantity | 27,590 MegaScale variants in the matched SH3 structures |
| Duplicated variant IDs | 0 in all three ddPCA domains |

**What "within tolerance" means here.** For example, the fold calibration r was recorded as 0.829; this run
gives 0.8291. Not one value moved beyond its last recorded digit.

---

## 2. ddPCA (Faure et al. 2022): the two energies per variant

ddPCA measures each variant twice: once for abundance, once for binding. MoCHI then fits two energies per
variant, **ΔΔG_fold** and **ΔΔG_bind**, separating the folding effect from the binding effect.

| Domain | Singles | With a binding energy | Reliable binding | Reliable folding | Positions |
|---|---|---|---|---|---|
| GB1 | 1,045 | 1,045 | 1,000 | 878 | 55 |
| **GRB2-SH3** | 1,056 | 756 | **619** | 1,032 | **56** |
| PSD95-PDZ3 | 1,587 | 1,567 | 1,221 | 1,199 | 84 |
| **Total** | **3,688** | 3,368 | **2,840** | **3,109** | |

**Reliable binding** means three things: the coefficient exists, |ΔΔG_bind| ≤ 4 kcal/mol, and the
bootstrap SD is ≤ 0.5 (over 10 bootstraps).

**Reading it:**
- **GRB2-SH3 is the only SH3 domain with measured binding energies.** It also loses the most to the reliability filter: only 619 of 1,056 singles (59 %) keep a reliable binding energy, against 96 % for GB1 and 77 % for PDZ3. For 300 GRB2 variants the model gives no binding energy at all. Why was not checked here. A likely reason is that the variants unfold the domain, so their binding cannot be read out.
- **Positions: 56 for GRB2-SH3, 84 for PSD95-PDZ3.** This one number returns in Part C. C3 finds that binding becomes predictable at about 76–82 distinct positions. PDZ3 is above that; GRB2-SH3, like every SH3, is below. The limit that Part C quantifies is already visible here.
- **Folding energies are close to complete for GRB2-SH3** (1,032 reliable). That fits the thesis: folding has plenty of data, binding does not.

---

## 3. The sign check: in-vitro calibration

The whole pipeline uses one sign convention: **positive = destabilising, or weaker binding.** A1 confirms it
against independent low-throughput measurements.

| Axis | Reference | n | Pearson r |
|---|---|---|---|
| Folding | Troilo 2018 (GRB2-SH3, Kf/Ku) | 15 | **+0.829** |
| Binding | Chi 2008 (PSD95-PDZ3, ΔΔG_b) | 12 | **+0.612** (numbering offset 310, derived) |

**Interpretation:**
- **Both correlations are positive,** so the sign convention is correct at the source. A sign error here would reverse every later result.
- **Folding agrees strongly** (r +0.83). The ddPCA folding energies of GRB2-SH3 track real, kinetically measured stability. These are the energies B1 is judged against.
- **Binding agrees moderately** (r +0.61, n = 12). Binding energies are noisier. They have a smaller dynamic range and depend on the chosen ligand.
- **The offset 310** is the difference between the ddPCA residue numbering and the PSD95 protein numbering. It is **derived** from the data, by aligning the two, and not typed in. It is identical to the recorded value.
- **Caveat:** these are small samples (n = 15 and 12). They show the direction and rough agreement, not a precise calibration.

---

## 4. The key premise: fold and binding separate by structure (GRB2-SH3)

Median measured ΔΔG (kcal/mol) by the residue's structural class:

| Residue class | Variants | ΔΔG_fold | ΔΔG_bind | Which energy it hits |
|---|---|---|---|---|
| Surface, not interface | 524 | 0.87 | −0.04 | Neither much |
| Surface, interface | 228 | 0.57 | 0.65 | Both mildly |
| **Buried, not interface** | 247 | **3.57** | 0.14 | **Folding only** |
| **Buried, interface** | 57 | 1.28 | **2.90** | **Binding mostly** |

**Interpretation — this is the empirical premise of the whole thesis:**
- **Buried core residues cost folding energy, not binding energy:** 3.57 vs 0.14. A cancer mutation in the core should break the fold.
- **Buried binding-site residues cost binding energy:** 2.90 vs 1.28 for folding. A mutation there can leave the domain folded but disable binding.
- **So the two mechanisms are physically distinct, and each has a structural signature.** That is what makes it meaningful to ask, for each cancer variant, which one it hits.
- **B2 tests the model against this pattern.** If B1's predicted fold damage follows burial but not the interface, the model has learned folding specifically, not general "badness".
- **Surface, non-interface residues** (half the domain) are close to neutral on both axes. Most random substitutions on the surface do little.

---

## 5. MegaScale (Tsuboyama et al. 2023): folding data at scale

| | |
|---|---|
| Single substitutions | 389,068 |
| Domains | 412 |
| Sign | flipped on loading, to match the project convention |
| Structures matching a human SH3 domain | 26, from 15 human SH3 genes (27,590 variants) |

**The matched SH3 structures** have sequence identity **0.50–0.78** to their human domains. The closest are
HCK (0.78), LASP1 (0.75), PTK6 (0.64), OBSCN (0.63) and LYN (0.63). SPTAN1 alone accounts for 10 of the 26
entries (several PDB structures and mutant backgrounds).

**Why this matters:**
- **MegaScale is what the folding head (B1) trains on.** Holding out every SH3 structure gives a clean *leave-family-out* test. The model never sees an SH3 fold during training, and it is tested on these 15 genes.
- **The sign flip is essential.** MegaScale reports ΔG of unfolding (higher = more stable). Negating it gives ΔΔG in the destabilising-positive convention. The calibration in Section 3 confirms the result is consistent.
- **Identity of 50–78 %** means these are real homologues but not identical to the human domains. Results on them are a fair proxy for the human SH3 family, not a copy of it.

---

## 6. Physics baseline: FoldX

| | |
|---|---|
| Variants with both FoldX and MoCHI ΔΔG_fold | 1,024 |
| Pearson r (FoldX vs MoCHI folding) | **+0.494** |

> **Correction (found in B1):** this 0.494 is contaminated. FoldX uses PDB numbering (GB1 +1, PDZ3 +310). A1
> joined it by raw residue ID, so the 1,024 "overlapping" variants include GB1 rows paired with the
> neighbouring residue's FoldX value, and no PDZ3 rows. The recorded original run had the same bug. B1 now
> derives the offsets and reports the aligned value (`foldx_vs_mochi_r_aligned`); use that in the thesis. B1's re-run gives **r 0.418 over 2,879 variants** (GB1 0.375, GRB2-SH3 0.517, PSD95-PDZ3 0.351).

FoldX, a structure-based energy function, explains only part of the measured folding energy (r ≈ 0.49). This
is the **bar B1 must beat.** A learned model is useful only if it does clearly better than a standard physics
tool. The EVE and MSA-conservation baselines were also written; B1 uses them for its comparison table.

---

## 7. Limitations

- **One SH3 domain with binding data.** Every statement about SH3 binding rests on GRB2-SH3, measured against one ligand. That is why Part C also uses PDZ3 and GB1 as comparison domains, and why C4 adds an independent specificity dataset.
- **The reliability filter removes 41 % of GRB2-SH3 binding energies.** The filter drops uncertain or extreme values, so the removed variants may not be a random subset. This was not tested here.
- **Small calibration sets** (n = 15 and 12).
- **The separation table uses median values per class.** It shows central tendency; individual residues vary.
- **MegaScale covers small, isolated domains** at room temperature. Stability in the full-length protein may differ.

---

## 8. Conclusion and next step

- **The measured data are reproduced exactly.** The sign convention is confirmed at the source.
- **Folding and binding separate by structure:** the core carries the folding energy, the binding site carries the binding energy. This is the physical basis for classifying cancer variants by mechanism.
- **Folding data are plentiful:** 389,068 MegaScale variants, with 26 held-out SH3 structures.
- **Binding data for SH3 are scarce:** one domain, 56 positions, 619 reliable energies. This asymmetry drives the whole thesis. Part B can succeed, and Part C has to explain why binding cannot yet be predicted.

**Next: A2 — features. This notebook needs a T4 GPU (about 25 min).** It computes one ESM-2 pass per wild-type
domain and the 12 scalar features. It also fetches the AlphaFold structures for burial and interface
annotation and caches them on Drive.
