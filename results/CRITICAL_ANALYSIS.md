# Critical analysis of all experiments, and what improved over the previous run

**Scope.** Every program of the rebuild from raw data (Colab run of 2026-09-22: A0–D1, plus C4, B6, F1, F2),
compared with the previous (original) stage-by-stage run whose values are recorded in
`reference/expected_values.json`. Every number below is taken from the programs' own `RESULTS_<ID>.md`
files. The per-program interpretation is in `results/<ID>_*/ANALYSIS_<ID>.md`.

**Short answer.**
- **The headline numbers did not get better.** The main results are the same as before, to the recorded precision: folding ρ 0.839, burial ρ +0.712, 410 destabilising calls, the ~80-position threshold.
- **The improvements are in validity, not in performance.**
  - Several earlier numbers were inflated or wrong, and are now corrected.
  - Several claims that previously rested on one fit or one partition are now tested properly.
  - Four new experiments were added: C4, B6, F1, F2.
- **In three places the corrected number is worse than the previous one.** In each case the new number is the honest one.

---

## 1. Did the rebuild reproduce the previous run?

| | Previous run | Rebuild |
|---|---|---|
| Starting point | Stage 0 scripts with hard-coded paths; atlas taken as given | Raw COSMIC + frozen UniProt snapshot, MD5-checked |
| Atlas | `SH3_cancer_master_v3.tsv` | **byte-identical** (MD5 `cef897f4…`) |
| Recorded quantities re-checked | — | **187 / 187** (160 identical, 27 within tolerance, 0 different) |
| Structure | 8 stage notebooks, one long fresh notebook | 14 + 2 programs, each reading only files, each writing its own report |

**Verdict: full reproduction.** This is the precondition for every comparison below: any difference is a
deliberate change of procedure, not drift.

---

## 2. Experiment by experiment: previous vs now

Legend: **=** unchanged · **↑** improved (more valid, more complete, or a corrected error) ·
**↓** the number got worse, because the old one was inflated · **NEW** did not exist before.

### Part A — data

| Exp. | Previous | Now | Change | Critical note |
|---|---|---|---|---|
| A0 atlas | 6,884 variants / 310 domains / 235 genes | same, byte-identical; 8/8 QC checks; streamed `.gz` avoids the truncated-file incident | ↑ reproducibility | The biology is unchanged. COSMIC counts still reflect sequencing effort, and 490 rows are rejected. |
| A1 ground truth | calibration r 0.829 / 0.612; separation table | same | = | Still **one SH3 domain with binding data** (GRB2-SH3, 56 positions, 619 reliable energies). This single fact limits all of Part C. |
| A1 FoldX baseline | r 0.494 (1,024 variants) | **aligned r 0.418 (2,879 variants)** | ↑ corrected | The old value mixed correct GRB2-SH3 rows with **misaligned GB1 rows** (PDB numbering +1) and had no PDZ3 rows at all (+310). |
| A2 features | 1,292 per variant; ESM ρ −0.404 / −0.259 | same; 0 of 399,640 dropped | = | 219 atlas variants (9 giant proteins) have no structure, because only AlphaFold fragment F1 is fetched. Not fixed. |

### Part B — loss of fold

| Exp. | Previous | Now | Change | Critical note |
|---|---|---|---|---|
| B1 folding head | median ρ 0.839, 15/15 vs ESM | same (retrained, identical) | = | **New checks added:** ablation, ridge, error decomposition, sign test p = 6.1 × 10⁻⁵. The ablation shows the gain needs *both* the embedding and the scalars (0.68 / 0.73 → 0.83), and a non-linear model (ridge 0.75). |
| B1 cross-assay | not among the recorded values | ρ 0.738 on GRB2-SH3 | NEW (reported) | **Weakness made explicit:** in ddPCA the head barely beats ESM (0.738 vs 0.728). The +0.22 gain is a MegaScale result, not a general one. |
| B1 vs FoldX / EVE | only A1's pooled FoldX r 0.494 (misaligned); no per-domain comparison. The rebuild's first run showed GB1 FoldX −0.13 on 69 misaligned variants and no PDZ3. | GB1: head 0.825, FoldX 0.487, EVE 0.370 (836 variants); PDZ3: head 0.540, FoldX 0.466, **EVE 0.589** (1,080) | ↑ corrected | The corrected table is more honest **and less flattering**: EVE beats the head on PDZ3. |
| B1 errors | not reported | glycine (ρ 0.69) and proline (MAE 0.61) are the weakest; severe effects under-predicted by 0.87 kcal/mol | NEW | Compression means the destabilising calls are **conservative**. The model cannot find stabilising mutations. |
| B2 structural check | burial +0.712, interface +0.037 | same | = | Rests on 56 positions and **one** reference complex for the interface. |
| B3 intervals | q90 6.807, coverage 89.9 %; seed-SD filter | same q and coverage; filter replaced; calibration curve (50–95 %) and stratified coverage added | ↑ | **Coverage is not uniform:** 83 % (LYN) to 95 % (FYN) by domain, and 86.9 % for predictions above 2 kcal/mol. The old filter passed 99.94 % of variants and was useless. |
| B3 calls | 297 / 113 / 191 / 6,283 | same | = | "Rewiring" (191) and "both" rest on zero-shot ESM, a weak binding predictor. They are hypotheses, not findings. |
| B4 ProteinGym | head 0.361 vs ESM 0.406 (primary) | same | = | **Negative result, stated plainly:** outside small-domain proteolysis data, ESM-2 is as good or better. The head is a specialist. |
| B5 cancer biology | 1/170 genes, 0/22 sites | same | = | **Null result.** The one hit (SPTA1, q 0.085) is borderline. Power is low: only 17 genes can be tested in non-hypermutated tumours. |
| B6 virtual scan | — | 366,168 substitutions; observed 5.9 % vs expected 9.2 % destabilising, p ≤ 0.001 | NEW | The most interesting new signal, and the most fragile: the null ignores codon and trinucleotide context, so **depletion ≠ selection** yet. |

### Part C — why binding cannot be predicted

| Exp. | Previous | Now | Change | Critical note |
|---|---|---|---|---|
| C1 cross-domain | GRB2-SH3 ρ **+0.097** (CI above 0); "head beats ESM 1/3" | corrected **−0.042** (CI includes 0); **0/3** | ↓ number, ↑ validity | The old positive came from **test-domain leakage** through early stopping. The old "win" was a wrong-direction correlation counted by absolute value. |
| C2 within-domain | the single seed-0 fit +0.124 (CI 0.044–0.205) was reported as the GRB2-SH3 result; the repeats (median −0.030) were recorded but not used as the headline | same repeats reproduced; corrected median −0.020; +0.124 shown to be the **best of six** | ↑ | A single split was reported as a result. With repeats there is **no signal**. PDZ3 stays learnable (0.397 → 0.373 corrected). |
| C2 decision | — | predictor of record = ESM zero-shot, with a **signed** comparison | ↑ | The old absolute-value rule could have picked the head for a large *negative* ρ. |
| C3 sufficiency | threshold ~76–82 positions; sweeps B 0.357 vs C 0.076 | same; corrected B 0.327 vs C 0.054; one table bug fixed | = / ↑ | The conclusion (**positions, not rows**) holds in both modes. Critically, the threshold is **calibrated on one domain (PDZ3) and one ligand**. "About 80" is an order of magnitude, not a constant. |
| C4 specificity | — | 154 PWMs / 115 domains; centred r +0.288, but 55/115 wins vs the average → **not validated** | NEW | A pre-registered negative result. It closes the last route to a binding axis with current data. |

### Part D/F — synthesis and follow-up

| Exp. | Previous | Now | Change | Critical note |
|---|---|---|---|---|
| D1 | report, figures | 187/187 check; original-vs-corrected table; 8 figures | ↑ | The figures were checked only as text so far. They need a visual check. |
| F1 | — | 10 destabilising picks + 10 same-domain controls; no rewiring panel | NEW | Picks are the most confident calls, but **concentrated** (see F2). |
| F2 | — | picks above the 99.65th percentile; 8/10 buried; **6 of 56 positions, 4 at aligned position 5** | NEW | It exposed a misreading in the first F1 analysis ("position 8" was domain-internal numbering). |

---

## 3. Where the rebuild genuinely improved on the previous run

1. **Errors removed.**
   - **FoldX misalignment:** the baseline r corrects from 0.494 to 0.418, and the GB1/PDZ3 comparisons become valid.
   - **Absolute-value "wins":** C1 corrects from 1/3 to 0/3, and the C2 decision rule is now safe.
   - **Test-domain leakage (C1):** GRB2-SH3 corrects from +0.097 to −0.042.
   - **Unshuffled `GroupKFold` repeats:** C2 and C3 now run both modes. The conclusions hold, and GRB2-SH3's spread narrows from 0.23 to 0.09.
   - **A table-grouping error (C3)** and an **over-tight tolerance (B3)**.
2. **Single numbers replaced by distributions.**
   - C2: six repeats instead of one fit.
   - C3: 20 matched-budget draws and 10 subsets per position count.
   - B3: a full calibration curve instead of one coverage number.
3. **Honest diagnostics added.**
   - Ablation, ridge and error decomposition (B1).
   - Stratified coverage and the rejection curve (B3).
   - The ProteinGym breakdown by block and length (B4).
4. **Independent tests added.**
   - C4 uses an ESM-independent target with a rule fixed in advance.
   - B6 uses a mutational background instead of raw counts.
5. **Reproducibility.**
   - Raw data → byte-identical atlas.
   - MD5-checked inputs.
   - Every report generated by its notebook.
   - 187/187 recorded values re-checked.

## 4. Where it did **not** improve, stated plainly

- **Folding performance is unchanged** (0.839). No model change was made, deliberately, so that the baseline stayed comparable.
- **Binding is still not predictable for SH3.** The rebuild removed the last small positive results (C1 +0.097, C2 +0.124) rather than adding one.
- **The specificity axis failed (C4),** so the central question of the thesis (fold *or* binding for each cancer variant) can be answered only on the fold side.
- **Outside its regime the head loses to zero-shot ESM-2** (B4). In ddPCA it only ties ESM on GRB2-SH3 (0.738 vs 0.728).
- **The cancer biology is null** (B5). B6's depletion needs a context-aware null before it can support a claim.

---

## 5. Critical weaknesses that remain in the study as a whole

| Weakness | Where it bites | Severity | What would fix it |
|---|---|---|---|
| One SH3 domain with binding energies (GRB2-SH3, one ligand) | all of Part C | **high** | ddPCA-type data for many SH3 domains on a common frame |
| Threshold calibrated on one domain (PDZ3) | C3's "~80 positions" | medium | repeat the position sweep on other learnable domains |
| Conformal intervals calibrated on MegaScale SH3 domains, applied to human cancer variants (exchangeability assumed, not tested) | B3 calls | medium | calibration on an independent set of human SH3 stability measurements |
| Per-domain coverage 83–95 % | B3 calls for some domains | medium | per-domain (Mondrian) conformal intervals |
| Compression of severe effects | B1, B3 | low for calls (conservative), high for effect sizes | loss or target transforms that preserve the tails |
| Both atlas axes derive from ESM-2 | B3 labels, C4 input | high for any rewiring claim | an experimental binding target for many domains |
| Mutational null ignores codon and trinucleotide context | B5, B6 | high for the B6 depletion claim | a signature-aware null (e.g. using COSMIC SBS signatures per tumour) |
| 219 variants without structure | B2, B5 | low | fetch the AlphaFold fragment that contains the SH3 domain |
| Low power in non-hypermutated tumours | B5 | medium | more samples (e.g. GENIE/TCGA) with harmonised mapping |
| F1 panel concentrated (6 of 56 positions) | the experimental plan | low (easily fixed) | one pick per aligned position |

---

## 6. What can and cannot be claimed after this rebuild

**Can be claimed (robust across procedures, reproduced exactly):**
- Loss of fold is predictable for SH3 domains never seen in training: median ρ 0.839, 15/15 vs ESM-2.
- The prediction is specific to folding: burial +0.71, interface +0.04.
- 410 of 6,884 cancer variants are confidently destabilising, with calibrated (on average) intervals.
- Binding is not predictable for SH3 from current data, and the limit is quantified: positional coverage, of the order of 80 positions against 56–60 in an SH3.

**Can be claimed only with qualification:**
- "Better than ESM-2": on MegaScale-type domains yes; in ddPCA roughly equal; on ProteinGym no.
- "Cancer variants are depleted of fold-breaking substitutions" (B6): consistent with purifying selection, but not yet separated from mutational bias.

**Cannot be claimed:**
- Any individual "rewiring" call (B3 labels, C4 not validated).
- That any destabilising variant is a cancer driver (B5).
- The exact threshold of 76 or 82 positions as a general constant.

---

## 7. Recommended next steps, in order of value

1. **Visually check the 11 figures** (D1 ×8, F2 ×3) before they go into the thesis.
2. **Spread the F1 panel:** one pick per aligned position, at most one proline. This is a small code change.
3. **Signature-aware null for B6/B5:** decides whether the depletion is selection.
4. **Per-domain conformal intervals (B3):** removes the 83–95 % coverage spread.
5. **In the thesis text,** replace any "FoldX r 0.494", "GRB2-SH3 binding ρ +0.097 / +0.124" or "head beats ESM on 1/3" from the previous run with the corrected values in this file.
