# C3 — Why binding cannot be predicted for SH3: positions, not rows (Stages 3c–3e)

**Question.** PSD95-PDZ3 is learnable and GRB2-SH3 is not. Is that the amount of data, the number of
positions, or SH3 biology? Could more mutagenesis of GRB2-SH3 ever fix it?

## Steps (each answers the question the previous one raised)
| Step | Test | Result in the original run |
|---|---|---|
| 1. Matched budget | PSD95 cut to GRB2's 56 positions / 619 rows, 20 draws | Collapses to median −0.023; its interval covers GRB2's −0.030 |
| 2. Diagnostic grid | Full PSD95 at 7 vs 5 folds, 60 vs 40 epochs | 5 folds give ~0.08, 7 give ~0.39: fragile near the edge |
| 3. Learning curve | Six budgets for both domains | PSD95 rises; GRB2 stays flat |
| 4. Three sweeps | A: fold count; B: rows thinned, all 84 positions kept; C: positions removed at the same rows | B holds (+0.357), C collapses (+0.076): **positions matter** |
| 5. Position sweep | 60–84 positions, 10 shuffled subsets each | Flat to 74; first significant rise at **76**, solid by 82 |

## The conclusion, stated carefully
1. **Positional coverage is the controlling variable.** Rows matter only through the positions they
   cover.
2. **It is an absolute count, not a fraction.** GRB2-SH3 has 100 % of its 56 positions and still
   fails.
3. **No SH3 domain can reach it.** SH3 domains are 56–60 residues, and the threshold is of the order
   of 80 positions. The fix is **more domains, not more mutations per domain**.
4. **Caveat:** the curve is calibrated on one domain. Quote "of the order of 80", and treat the
   ordering (56 fails, 84 barely works) as the robust claim.

## Two corrections to the original reading
- Step 4 in the original used unshuffled partitions. Its apparent sharp step at 70 positions was an
  artefact, which is why step 5 (shuffled) is the one to quote. Steps 1–4 now also run with
  `corrected` partitions, side by side.
- The original 3e notebook flagged "leverage" (the idea that *which* positions matter). The
  enrichment table shows every position at 0.27–0.48, the base rate of successes to failures. No
  position carries the signal; the mechanism is the **count**.
