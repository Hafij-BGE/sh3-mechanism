# Recommendations for improving the experiments

**Basis:** the Colab run of 2026-09-22 (A0–D1, C4, B6, F1, F2; 187/187 recorded values reproduced) and its
critical review in `results/CRITICAL_ANALYSIS.md`. The recommendations are ordered by value against effort.

**Principle.** None of the "now" items changes the model or any value that already reproduces. Anything that
would change a headline number is marked, and should be run as a clearly labelled variant beside the original,
never in place of it.

---

## A. Feasible now (current data, Colab T4)

| # | Program | Improvement | Why it matters | Effort | Changes headline numbers? |
|---|---|---|---|---|---|
| 1 | **F1** | Spread the panel: at most one pick per aligned position, at most one change to proline | 4 of 10 picks share aligned position 5, and the panel covers only 6 of 56 positions (F2). A spread panel tests the model across the fold, not one site. | very low: small code change, re-run F1 + F2 in seconds | no |
| 2 | **B6, B5** | Replace the mutational null with a signature-aware one: trinucleotide context and codon usage, weighted by the mutational signatures of the tumours each variant occurs in | Decides whether B6's depletion (5.9 % observed vs 9.2 % expected destabilising) is **purifying selection** or **mutational bias**. Currently the claim must stay hedged. | medium: one new null function, re-run B5 + B6 | no (adds a second null beside the current one) |
| 3 | **B3** | Per-domain (Mondrian) conformal intervals, with a fallback to the global quantile for small domains | Coverage now ranges from 83.3 % (LYN) to 95.0 % (FYN), and 86.9 % above 2 kcal/mol. Per-domain calibration makes the 90 % promise hold in every domain. | low | the destabilising count may shift. Report it beside the global version (410). |
| 4 | **A2** | Fetch the AlphaFold fragment that contains the SH3 domain, not only fragment F1 | Recovers 219 variants in 9 large proteins (TRIO, OBSCN, PLEC, MYO15A, DSP, DST, NEB, MACF1, KALRN) for B2 and B5, including TRIO Q2579R, one of the most recurrent non-hypermutated variants | low code, but re-runs A2 (about 25 min) and everything downstream | small changes in B2/B5 coverage |
| 5 | **C3** | Repeat the position sweep on a second domain (GB1, 55 positions) | The ~80-position threshold rests on PDZ3 alone. A second domain turns one estimate into a range. | medium: 1–2 h of T4 time | no (new table) |
| 6 | **B1** | A second evaluation that holds out whole MegaScale **folds**, not only the SH3 family | Shows whether the head generalises to any small domain or mainly to β-barrels; B4's weak external transfer hints at the latter | medium: one extra split, retraining | no (new table) |
| 7 | **B1, B3** | A tail-preserving loss (for example quantile or rank-based) as a **variant** of the head | Fixes the compression: severe variants are under-predicted by 0.87 kcal/mol, and stabilising ones are not detected. That would make effect sizes usable, not only rankings. | medium | **yes.** Run as a separate variant; keep 0.839 as the reference. |
| 8 | **C4** | One pre-registered second attempt: predict per-position PWM columns on a common peptide frame instead of one 20-number profile | The failure may come from collapsing each PWM into 20 numbers. The decision rule must be fixed *before* running, and the attempt reported as the second one. | medium | no |
| 9 | **B5** | Add per-position mutability (from the atlas mutation spectrum) as a covariate in the positional test | Removes the confound that makes "positions are non-uniform" (p = 0.0002) uninterpretable | low | no |
| 10 | **All** | One run log listing seeds, library versions and re-runs; a "changed since the previous run" line in each `RESULTS_<ID>.md` | With 16 programs and several re-runs, it keeps the thesis text and the result files in step | low | no |

### Recommended order
1. **#1, #2, #3.** They are cheap and remove the two hedges that most weaken the thesis: B6's depletion and B3's uneven coverage. They touch no model.
2. **#4**, if a re-run of A2 and downstream (about 2 h) is acceptable.
3. **#5 and #6** strengthen the generality of the two main conclusions.
4. **#7 and #8** only as clearly labelled variants or second attempts, after the thesis draft is stable.

---

## B. Needs new data or a separate project

| Recommendation | What it needs | What it buys |
|---|---|---|
| **Multi-domain SH3 binding data (the key recommendation of the thesis)** | ddPCA-style binding energies for 15–20 SH3 domains against a shared ligand, aligned on one frame | The only route to predicting SH3 binding. C3 shows the limit is positional coverage (about 80 positions), which no single SH3 domain (56–60 residues) can provide. |
| **Bench validation of F1** | Thermal denaturation or proteolysis stability for the 10 pick/control pairs (after #1) | Turns 410 predictions into evidence and tests the calibration directly |
| **Independent calibration set** | Published stability measurements for human SH3 variants outside MegaScale | Tests the exchangeability assumption behind B3's intervals, which is currently untested |
| **Other domain families** | PDZ, SH2 or WW domains through the same pipeline | Shows whether the ~80-position limit is general or specific to SH3 |
| **More tumour samples** | GENIE / TCGA with harmonised mapping | Power for B5 in non-hypermutated tumours (only 17 genes are testable now) |

---

## C. What not to do

- **Do not tune the folding head for a higher ρ.** 0.839 with 15/15 wins is sufficient, and an unchanged value is what makes the reproduction convincing.
- **Do not build a rewiring analysis on ESM-2 scores.** Part C showed the axis is too weak (ρ −0.13 on GRB2-SH3), and C4 failed its own pre-registered rule. Repeated attempts on the same data would amount to tuning until something passes. #8 is the single allowed second attempt.
- **Do not add further COSMIC recurrence statistics.** A0 and B5 show the data cannot support driver claims for SH3.
- **Do not report a number from the previous run where a corrected one exists.**
  - FoldX r 0.494 → **0.418**.
  - GRB2-SH3 binding +0.097 → **−0.042**.
  - GRB2-SH3 single fit +0.124 → the six-repeat median **−0.020 / −0.030**.
  - "Head beats ESM 1/3" → **0/3**.

---

## D. How each recommendation maps to the thesis text

| Thesis claim | Current strength | Strengthened by |
|---|---|---|
| Loss of fold is predictable for unseen SH3 domains | robust | #6 (generality), bench validation |
| Prediction is specific to folding | robust | #4 (more variants with structure) |
| 410 variants confidently destabilising | robust on average; coverage 83–95 % by domain | #3, #7, bench validation |
| Cancer variants depleted of fold-breaking substitutions | hedged | **#2** |
| No gene or tumour-site enrichment | robust but low-powered | #9, more tumour samples |
| Binding needs about 80 positions | one calibration domain | #5, other families |
| No rewiring claim possible | robust (C4 failed) | #8 (one pre-registered retry), multi-domain binding data |
