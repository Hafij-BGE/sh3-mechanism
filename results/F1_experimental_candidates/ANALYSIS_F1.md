# F1 — Analysis of the result: experimental validation candidates

**Colab run:** 2026-09-22, 0.2 min on CPU. It ran without errors on first use. Re-run at 15:56 with the display fix: the same 20 candidates, values identical, and the domain index now printed as an integer. No recorded values to compare
against: F1 is a follow-up that reads frozen outputs, and it changed nothing upstream.
The run's own numbers are in `RESULTS_F1.md` and `panel_summary.csv`. The full list with tumour sites is
`experimental_candidates.csv`, which stays on Drive.

---

## 1. What came out

| Class | Candidates | Tier 1 |
|---|---|---|
| Destabilising (Panel S) | 10 | 3 |
| Tolerated controls (Panel S) | 10 | 5 |
| Rewiring (Panel R) | not built | — |
| Four-group design (Panel D) | not built | — |

- **The output is exactly what was expected:** C4 was not validated, so only the two-group stability design exists.
- **All 10 controls come from the same domains as the 10 destabilising picks.** Each of the 10 genes (RIMBP2, SORBS1, SPTA1, YES1, NOXO1, RUSC1, SH3GL2, TRIP10, GRAP, DLG5) has one predicted fold-breaker and one predicted-neutral variant. Every domain can therefore be tested as a positive and a negative in the same background, which is the cleanest bench design.
- **All 10 destabilising picks were seen in a non-hypermutated tumour.** Their lower 90 % bounds range from 2.47 to 3.81 kcal/mol, far above the 1 kcal/mol threshold.
- **The controls** have predicted ΔΔG between 0.00 and 0.26 kcal/mol, and every interval includes 0.

---

## 2. Destabilising picks

| Gene | Variant | Predicted ΔΔG_fold | Lower 90 % bound | Tier |
|---|---|---|---|---|
| RIMBP2 | I906N | 4.62 | 3.81 | 1 |
| SORBS1 | V820D | 4.11 | 3.39 | 1 |
| SPTA1 | V982D | 4.26 | 3.11 | 2 |
| YES1 | A98D | 3.98 | 2.83 | 2 |
| NOXO1 | R282P | 4.63 | 2.68 | 2 |
| RUSC1 | A851P | 4.03 | 2.59 | 2 |
| SH3GL2 | A297D | 4.28 | 2.55 | 2 |
| TRIP10 | A547P | 4.00 | 2.53 | 2 |
| GRAP | I185T | 3.98 | 2.49 | 2 |
| DLG5 | A1600P | 3.55 | 2.47 | 1 |

**Tier 2** here means only that the interval is wider than the atlas median (1.115 kcal/mol). Every pick is
still confidently destabilising.

---

## 3. Two things to know before ordering experiments

1. **The panel is concentrated on one position and two substitution types.**
   - In each domain's own numbering, 5 picks are at position 8. **On the common aligned frame (F2), 4 of them share one position, aligned position 5** (YES1, RUSC1, SH3GL2, DLG5). TRIP10's position 8 aligns to position 8. The 10 picks cover only **6 of 56 aligned positions** (3, 5, 8, 25, 43, 47).
   - 4 of the 10 are substitutions to proline, which B1 found to be among the harder cases (MAE 0.61 kcal/mol).
   - A buried Ala → Asp or Pro near the start of the domain (likely the first β-strand) is a textbook destabiliser, so the picks are plausible. But the panel tests mostly one structural mechanism.
   - **To test the model across the fold,** limit the panel to one pick per aligned position (or per substitution type) and let the next-ranked variants fill the gaps. This is a one-line change; tell me if you want it.
2. **SPTA1 V982D is in the panel,** and SPTA1 was also the one borderline gene in B5 (q = 0.085). Its prediction is strong (lower bound 3.11), so it is a good pick. But a positive result would confirm loss of fold, not that SPTA1 is a cancer gene (B5).

---

## 4. The assays

- **Panel S:** thermal denaturation (CD or DSF), proteolysis-based stability, cellular abundance, or ddPCA if the domain can be cloned into that system.
- **Test each pick and its same-domain control side by side.**
- **Expected outcome if the model is right:** the pick destabilises by ≥ 1 kcal/mol, likely more (B1 compression), and the control changes stability by less than about 0.5 kcal/mol.

---

## 5. Limitations

- **Assay feasibility** (expression, solubility, cost) is not modelled.
- **In vitro stability of an isolated domain** may differ from the full-length protein in cells.
- **A confirmed destabiliser is still not a driver** (B5).
- **No specificity experiments are planned,** because C4 did not validate. Any rewiring experiment would be exploratory, not a test of a prediction.

---

## 6. Status

See `results/F2_candidate_figures/ANALYSIS_F2.md` for the figures and for how F1 agrees with the earlier results.


- **F1 works.**
- **Cosmetic fix applied and re-run:** the domain index now prints as `2`, not `2.000`.
- **`RESULTS_F1.md` lists 20 COSMIC variant IDs, without tumour sites.** That is fine for a private repository. If the repository is ever made public, drop the candidate table from it first.
