# D1 — Analysis of the result: figures and the full reproduction check

**Colab run:** 2026-09-22, 0.6 min on CPU; **re-run 15:47 after the B3 tolerance fix: 187 / 187 reproduced.** D1 collects every program's check against the recorded run, draws
the 8 figures and writes `results/RESULTS_SUMMARY.md`.

---

## 1. The whole pipeline reproduced from raw data

| Program | Identical | Within tolerance | DIFF | Verdict |
|---|---|---|---|---|
| A0 cancer atlas | 20 | 0 | 0 | REPRODUCED (byte-identical atlas) |
| A1 ground truth | 15 | 11 | 0 | REPRODUCED |
| A2 features | 8 | 13 | 0 | REPRODUCED |
| B1 folding model | 8 | 2 | 0 | REPRODUCED |
| B2 structural check | 3 | 0 | 0 | REPRODUCED |
| B3 intervals and calls | 7 | 1 | 0 | REPRODUCED (after re-run) |
| B4 external validation | 12 | 0 | 0 | REPRODUCED |
| B5 cancer biology | 15 | 0 | 0 | REPRODUCED |
| C1 binding across domains | 9 | 0 | 0 | REPRODUCED |
| C2 binding within a domain | 21 | 0 | 0 | REPRODUCED |
| C3 data sufficiency | 42 | 0 | 0 | REPRODUCED |
| **Total** | **160** | **27** | **0** | **187 of 187 recorded quantities reproduced** |

- **"Within tolerance"** (26 values) means the recorded value was stored with fewer decimals, for example 0.829 recorded and 0.8291 now. None moved beyond its last recorded digit.
- **The last DIFF (first run only)** was B3's `axis_rank_correlation`: 0.6745674 against 0.6745677, a difference of 3 × 10⁻⁷. The cause is the ordering of tied ESM scores, and the quantity is flagged "not a valid test" (B3 analysis, Section 8). **No mechanism call changed.**
  - Its tolerance has since been set to 10⁻⁶ in `reference/expected_values.json`.
  - B3 and D1 were re-run with the new file: B3 now reads 7 identical + 1 within tolerance, and D1 reads **160 identical, 27 within tolerance, 0 different**.
- **C4 and B6 are new programs** with no recorded values, so they are not in this table. Both ran without errors.
- **Total compute** for all 14 programs was about 2.3 h on Colab (first runs; re-runs excluded).

---

## 2. Original vs corrected procedure (binding)

| Program | Quantity | Original (= recorded) | Corrected | Change |
|---|---|---|---|---|
| C1 | GRB2-SH3 ρ, leave-one-domain-out | +0.097 | **−0.042** | −0.139 |
| C2 | GRB2-SH3 median of 6 repeats | −0.030 | −0.020 | +0.010 |
| C2 | PSD95-PDZ3 median of 6 repeats | +0.397 | +0.373 | −0.024 |
| C3 | Matched budget (PDZ3 cut to GRB2) | −0.023 | −0.024 | −0.001 |
| C3 | Sweep B (fewer rows, all positions) | +0.357 | +0.327 | −0.030 |
| C3 | Sweep C (fewer positions) | +0.076 | +0.054 | −0.022 |

**The corrections change numbers, not conclusions.** The one sizeable change is C1: removing test-domain
early stopping turns the small positive GRB2-SH3 result into zero. Every Part C conclusion (binding not
learnable for SH3; positions, not rows; about 80 positions needed) holds under both procedures.

---

## 3. The eight figures

| Figure | Shows (from its title and labels) | Program |
|---|---|---|
| fig1_folding_vs_esm | Per-domain ρ of the folding head vs zero-shot ESM-2, 15 held-out SH3 domains | B1 |
| fig2_burial_specificity | Predicted damage vs burial (ρ +0.71) and vs interface (ρ +0.04) | B2 |
| fig3_binding_positions | Matched rows / different positions, and accuracy against number of positions (step at about 76–82) | C2, C3 |
| fig4_proteingym_transfer | Head vs ESM-2 on external ProteinGym blocks | B4 |
| fig5_atlas_mechanisms | Mechanism calls for the 6,884 cancer variants | B3 |
| fig6_binding_refits | Spread of the six within-domain refits (the "+0.124" as one draw) | C2 |
| fig7_specificity_axis | PWM cross-validation (not validated) | C4 |
| fig8_family_landscape | Mean predicted damage per aligned position across all SH3 domains | B6 |

Each figure is saved as PNG and PDF in `results/D1_figures_and_verification/`. I could read only their text
labels through Drive, not the images themselves, so **look at each figure once** before using it in the
thesis. Check especially that labels are readable and that nothing overlaps.

**Fig. 4, one point to check:** the "head wins" count on that figure compares |ρ| values. For B4 this is
correct, because every head ρ and every ESM ρ has the right sign (B4 analysis, Section 6). It is noted here
because the same pattern was a bug in C1/C2.

---

## 4. What the thesis can now say, program by program

**Part A — data**
- **A0:** 6,884 residue-verified SH3 cancer variants, rebuilt byte-identically from raw COSMIC. COSMIC flags none as a driver.
- **A1:** folding and binding separate by structure. The buried core costs folding energy (3.57 kcal/mol); the buried binding site costs binding energy (2.90).
- **A2:** 1,292 sequence features per variant. Structural labels cover 96.8 % of the atlas.

**Part B — loss of fold (the confident claims)**
- **B1:** folding is predictable for SH3 domains never seen in training: median ρ 0.839, beats ESM-2 on 15 of 15. The corrected FoldX-vs-measured r is 0.418.
- **B2:** the prediction is specific to folding: burial ρ +0.71, interface +0.04.
- **B3:** the 90 % intervals are honest on average; **410 variants (6 %) are confidently destabilising.**
- **B4:** it is a domain-scale specialist; outside that regime ESM-2 is as good or better.
- **B5:** there is no enrichment by gene or tumour site. The atlas is a mechanism map, not a driver list.
- **B6:** the full folding landscape of 310 SH3 domains. Observed cancer variants are *depleted* of damage against a single-nucleotide background (5.9 % vs 9.2 %). This is consistent with purifying selection, but mutational context is not modelled.

**Part C — why binding cannot be predicted (quantified negative result)**
- **C1:** binding does not transfer between unrelated domains. The recorded small positive result came from leakage.
- **C2:** within one domain, binding is learnable for PDZ3 (ρ about 0.37–0.40) but not for GRB2-SH3 (about 0). The recorded +0.124 was one lucky draw.
- **C3:** the limit is positional coverage, not measurements. About 80 positions are needed; an SH3 domain has 56–60.
- **C4:** an independent specificity axis over 115 SH3 domains does not beat the family average. No rewiring claim is made.

---

## 5. Problems found and fixed during this rebuild

| Where | Problem | Fix | Effect |
|---|---|---|---|
| A1/B1 | FoldX joined by raw residue number (PDB numbering: GB1 +1, PDZ3 +310) | offsets derived from wild-type residues | FoldX baseline for GB1 and PDZ3 now valid; FoldX r 0.494 → 0.418 |
| C1/C2 | "Beats ESM" counted by absolute value, so wrong-direction correlations counted as wins | signed comparison | C1: 1/3 → 0/3; C2 decision made safe |
| C3 | Learning-curve table split one budget into two rows | group by positions only | the one C3 DIFF resolved |
| B3 | Tolerance 10⁻⁹ on a tie-sensitive quantity | tolerance 10⁻⁶ | the last DIFF explained |
| (earlier) | Unshuffled GroupKFold; test-domain early stopping; seed-spread filter | corrected procedures run side by side | Part C conclusions unchanged |

---

## 6. What to do now

1. ~~Re-run B3 and D1 with the new tolerance~~ — done, 187/187.
2. **Look at the 8 figures once** in `sh3_repro/results/D1_figures_and_verification/`.
3. **Download** `MyDrive/sh3_repro/results/` into `~/Documents/thesis/sh3 updated/results/`.
   - Merge it with the existing folders. The `ANALYSIS_*.md` files already there have different names and are not overwritten.
   - Also bring `RESULTS_SUMMARY.md`.
4. **Commit to GitHub** (`GITHUB_GUIDE.md`). The `.gitignore` keeps `.tsv`, `.parquet`, `.npz`, `.pt` and `.cif` out, which covers the COSMIC-derived atlas, per-variant predictions, embeddings and model weights.
