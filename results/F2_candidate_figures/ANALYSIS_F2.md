# F2 — Analysis of the result: the candidate panel in figures, and F1 checked against the earlier results

**Colab run:** 2026-09-22, CPU, seconds. It ran without errors on first use. It draws only, so no number from
A0–F1 changed.
The run's own numbers are in `RESULTS_F2.md`, `comparison_F2.csv` and `candidate_positions.csv`. The figures
are `figF1_candidate_pairs`, `figF2_atlas_context` and `figF3_position_map`, each as PNG and PDF.

---

## 1. What F2 measured

| Quantity | Value |
|---|---|
| Destabilising picks / same-domain controls | 10 / 10 |
| Lowest atlas percentile of any pick's lower 90 % bound | **99.65th** |
| Picks at buried positions (GRB2-SH3 frame) | **8 of 10** |
| Picks that are substitutions to proline | 4 of 10 |
| Aligned positions covered by the picks | **6 of 56** |
| Most-used aligned position | **position 5, with 4 picks** |

**Picks per aligned position** (`candidate_positions.csv`):

| Aligned position | Picks | Genes |
|---|---|---|
| 3 | 1 | SPTA1 |
| **5** | **4** | YES1, RUSC1, SH3GL2, DLG5 |
| 8 | 1 | TRIP10 |
| 25 | 2 | SORBS1, GRAP |
| 43 | 1 | NOXO1 |
| 47 | 1 | RIMBP2 |

---

## 2. The three figures

**figF1 — each pick next to its control.** For all 10 genes the red interval (the pick) lies entirely to the
right of the 1 kcal/mol line. The blue interval (the control) straddles zero. The separation is clean for
every pair, which is what a bench panel needs: a clear positive and a clear negative in the same protein.

**figF2 — the panel against the atlas.** Every pick lies above the 99.65th percentile of the 6,884 atlas lower
bounds. The picks are among the 25 or so most confident destabilising calls in the atlas, not borderline ones.
The controls sit in the bulk of the distribution, around zero.

**figF3 — the panel on the SH3 fold.** The picks cover only 6 of the 56 aligned positions, and 4 of them share
position 5.
- **This corrects an earlier reading.** In the F1 analysis, 5 picks appeared to share "position 8", but that was each domain's own numbering. On the common frame, TRIP10's position 8 maps to aligned position 8 and the other four to position 5.
- **The point stands:** the panel is concentrated. It would test mainly one site of the fold.

**What to check by eye.** The figures could be read here only as text, so open the PNGs once. Check that the
residue labels in figF1 do not overlap and that the counts above the bars in figF3 are legible.

---

## 3. F1 against the earlier results: does the panel agree with what the pipeline found?

| Earlier result | What it predicts for a good panel | What F1/F2 show | Agreement |
|---|---|---|---|
| **B3:** 410 variants confidently destabilising | Picks drawn from those 410, with lower bounds well above 1 | All 10 are among the 410; lower bounds 2.47–3.81; all above the 99.65th percentile | ✔ |
| **B2:** damage follows burial (ρ +0.71), not the interface | Picks mostly buried | 8 of 10 at buried aligned positions | ✔ |
| **B6:** most fragile family positions are 19, 25, 47, 5, 27 (mean predicted damage 2.2–2.5) | Picks at fragile core positions | 3 of the 6 positions used (25, 47, 5) are in the top 5; position 3 is 14th; 8 and 43 are not in the top 15 | ✔ mostly |
| **B1:** weakest on substitutions *from* glycine (ρ 0.69) and *to* proline (MAE 0.61) | Avoid the weakest classes, or flag them | 0 picks from glycine; **4 to proline** | partly: the proline picks carry more model uncertainty |
| **B1/B3:** severe effects are under-predicted (compression) | True effects at least as large as predicted | Predicted 3.6–4.6 kcal/mol; likely larger in reality | ✔ (conservative) |
| **A2:** 9 giant proteins lack structure | Picks should have structural labels | All 10 map to the aligned frame | ✔ |
| **B5:** no enrichment by gene, except borderline SPTA1 | Gene choice should not be read as "cancer genes" | 3 pick genes (SPTA1, SH3GL2, TRIP10) are among B5's ten top-ranked genes, but only SPTA1 was borderline (q 0.085) | ✔, but see note |
| **C4:** specificity axis not validated | No rewiring panel | none built | ✔ |
| **F1 first run vs re-run** | Deterministic | The same 20 candidates, identical values | ✔ |

**The B5 note.** Genes with many destabilising variants rank high in B5 *and* supply the strongest picks, so
the overlap is expected. It is not independent evidence that these genes matter in cancer. A confirmed
destabiliser proves loss of fold, not a driver role.

**Overall:** the panel is internally consistent with every earlier result. The picks are the most confident
calls, sit in the buried core, and fall mostly at the family's most fragile positions. Their controls are
neutral. Its one weakness is **narrow coverage**: 6 of 56 positions, 4 picks at one position, and 4 picks to
proline.

---

## 4. What this means for planning experiments

- **As a first test of "does the model call loss of fold correctly?", the panel is strong.** Clear positives, clear negatives, and the same protein background for each pair.
- **As a test of the model across the SH3 fold, it is narrow.** If the 4 picks at position 5 all destabilise, that confirms one site four times. Two better options, each a small change to F1:
  1. **One pick per aligned position:** keep the best pick at position 5 and fill the other slots with the next-ranked picks at new positions.
  2. **At most one proline substitution,** since B1 is less certain about those.
- **Recommendation:** use option 1 (with option 2 as a tie-breaker) for the thesis's validation plan. The current panel stays valid as the "highest-confidence" list. Tell me if you want F1 to write both panels.

---

## 5. Limitations

- **The figures inherit the limits of B3 and B6:** folding only, isolated domains, compressed severe effects.
- **Burial and interface labels come from the GRB2-SH3 reference structure,** not from each pick's own domain.
- **Only 10 picks:** percentages over the panel (for example 8 of 10 buried) are descriptive, not tests.

---

## 6. Conclusion

- **F2 confirms the F1 panel is sound:** top 0.35 % of the atlas, 8 of 10 buried, and clean separation from same-domain controls.
- **F1 agrees with every earlier result** (B1, B2, B3, B5, B6, C4, A2). No contradiction was found.
- **The one improvement to make is spreading the picks over more positions.** Currently 4 of 10 share aligned position 5, and the panel covers 6 of 56 positions.
