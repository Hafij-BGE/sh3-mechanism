# E1 — ClinVar and gnomAD  *(planned — next)*

**Why it is needed.** E2 showed the predictions track a physical measurement. E1 asks the clinical
question: do the confidently destabilising calls line up with variants independently judged
**pathogenic**, and do tolerated calls line up with **benign**? It also supplies the germline arm
that G1 needs.

**What it does not do.** It trains nothing and needs no GPU. Evaluation-only.

## Inputs
| File | From | Used for |
|---|---|---|
| `clinvar_sh3.csv` | X0 | 74,116 records, with review status → star rating |
| `gnomad_sh3_missense.csv` | X0 | 431,959 variants with AC/AN/AF |
| `atlas_predictions.parquet` | B3 (frozen) | `pred_ddG_fold`, `fold_lo` |

## ⚠ Pre-register before running
Two thresholds decide the answer, and both must be **written down and committed before any result is
looked at**. C4 is why this rule exists: a rule chosen after seeing the outcome is not a rule.

| Parameter | Proposed | Reasoning |
|---|---|---|
| ClinVar star floor | **≥ 2** | multiple submitters, no conflicts — excludes single-submitter and no-criteria records |
| gnomAD "common" | **AF > 0.1 %** | standard population-genetics threshold for a tolerated variant |
| Conflict rule | highest stars, ties by severity | already applied in X0; keep or change deliberately |

**Neither number has been chosen by looking at a result.** Confirm or change them, then commit, then
run.

## Method
1. Recall: of ClinVar pathogenic / likely-pathogenic missense variants in SH3 domains, what fraction
   is called confidently destabilising (`fold_lo ≥ 1`)?
2. Specificity: of benign / likely-benign, what fraction is not?
3. Predicted ΔΔG across four groups — pathogenic, benign, gnomAD-common, COSMIC — with effect sizes,
   not only p-values.
4. Compare the pathogenic-destabilising rate with the **60 %** Beltran et al. report for pathogenic
   missense variants generally.
5. **The germline arm.** Are germline-tolerated variants depleted of destabilising substitutions the
   way the cancer variants are (B6: 5.9 % against 9.2 %)? This attacks B6's confound from a second
   direction, without depending on a mutational-signature model being right.

## What would make this fail honestly
If pathogenic variants are not enriched for destabilising calls, that is a real negative result about
the calls, and it should be reported as one. The pre-registered thresholds are what make that
statement credible.
