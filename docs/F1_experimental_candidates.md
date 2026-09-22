# F1 — Experimental validation candidates (roadmap N1–N3)

**Why it is needed.** B3 calls 410 atlas variants confidently destabilising. Those calls are predictions.
The step that turns them into evidence is a bench experiment. F1 picks a small, defensible first panel and
says which assay fits each pick. It is a planning tool for the thesis's "future work / validation" section,
not a new result.

**What it does not do.** It trains nothing and recomputes nothing. It reads files that A0, B3 and C4 have
already written. Running it cannot change any number in A0–D1, and it is not part of the reproduction check.

## Inputs
| File | From | Used for |
|---|---|---|
| `SH3_cancer_master.tsv` | A0 | non-hypermutated occurrence, tumour sites. Checked against A0's recorded MD5 first. |
| `atlas_predictions.parquet` | B3 | `pred_ddG_fold`, `fold_lo` (lower 90 % bound), destabilising call |
| `specificity_decision.json` | C4 | whether the independent specificity axis passed its pre-registered rule |
| `atlas_rewiring.parquet` | C4 | rewiring score, **read only if** C4 was validated |

## Method
1. **Panel S — stability (roadmap N1).**
   - **Picks:** destabilising calls (`fold_lo ≥ 1`), ranked by how far `fold_lo` clears 1 kcal/mol. Variants seen in a non-hypermutated tumour come first.
   - **Controls:** confidently tolerated variants (|predicted ΔΔG| < 0.3 kcal/mol, narrowest interval), taken from the **same domains** as the picks where possible. Each domain is then tested with a positive and a negative, in the same protein background.
   - **Assays:** thermal denaturation (CD/DSF), proteolysis-based stability, cellular abundance, or ddPCA if the domain fits that system.
2. **Panel R — specificity (roadmap N2).**
   - **Built only if C4's rule returned `validated: true`.**
   - **Picks:** top-decile C4 rewiring score, not destabilising.
   - **Assays:** phage display, peptide array, fluorescence polarisation, SPR, yeast two-hybrid.
3. **Panel D — four-group design (roadmap N3).**
   - **Groups:** destabilising-only / rewiring-only / both / neither, up to 6 each.
   - **Only with a validated C4 axis.** Without it, only two groups exist, and they are Panel S and its controls.
4. **Priority tier.**
   - **Tier 1:** seen in a non-hypermutated tumour **and** a 90 % half-width below the atlas median.
   - **Tier 2:** everything else in the panel.

## Why B3's "rewiring" label is not used
B3's `mechanism` column labels 191 variants "rewiring" and 113 "both". The binding half of those labels is
rank-matched **zero-shot ESM-2**. Part C showed that ESM-2 is a weak binding predictor (ρ −0.13 on
GRB2-SH3), and the project makes no binding claim (`binding_claims_made = False`). A specificity panel built
from that label would present an unvalidated axis as a prediction, so F1 refuses to use it.

## Expected output with the current results
C4 was **not validated** (median centred r +0.288; 55/115 wins vs the average profile). So:
- **Panel S:** 10 destabilising picks + 10 controls, 20 candidates in total;
- **Panel R and Panel D:** not built. `RESULTS_F1.md` explains why.

## Outputs
| File | Content | Goes to GitHub? |
|---|---|---|
| `experimental_candidates.csv` | one row per candidate: prediction, interval, tumour sites, assay, tier | **No.** Per-variant COSMIC-derived; blocked by `.gitignore`. |
| `panel_summary.csv` | candidates and tier-1 count per class | yes |
| `RESULTS_F1.md` | the panel without the tumour-site column, assays, and the reason for any empty panel | yes |

## Setting
`N_PER_PANEL = 10` (first cell of section 1): candidates per class. Change it and re-run. F1 takes seconds.

## Honest limits
- **Assay feasibility is not modelled:** expression, solubility, peptide availability, cost, throughput. Check before ordering anything.
- **Predictions are conservative for severe variants (B1, B3),** so the true effect of a Panel S pick is on average at least as large as predicted.
- **Stability measured in vitro on an isolated domain** may differ from the effect in the full-length protein in cells.
- **A confirmed destabilising variant is still not a driver (B5).** Loss of fold is a mechanism, not proof of pathogenicity.
