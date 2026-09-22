# F2 — Figures for the experimental candidate panel

**Why it is needed.** F1 produces a ranked table of bench candidates. F2 turns that table into three figures
that show whether the panel is defensible: how confident each pick is, how extreme it is relative to the
atlas, and how much of the SH3 fold it covers. These are the figures to show before any experiment is
planned.

**What it does not do.** It draws only. Nothing is recomputed, and no number from A0–F1 changes.

## Inputs
| File | From |
|---|---|
| `experimental_candidates.csv` | F1 (picks and same-domain controls) |
| `atlas_predictions.parquet` | B3 (all 6,884 lower bounds; aligned position, wild-type and mutant residue) |
| `family_position_map.csv` | B6 (mean predicted damage per aligned position, burial, interface) |

## The figures
| File | Shows | What to look for |
|---|---|---|
| `figF1_candidate_pairs` | Each destabilising pick (red) next to its same-domain control (blue), with 90 % conformal intervals and the 1 kcal/mol line | Every red interval should lie right of the line; every blue interval should straddle 0 |
| `figF2_atlas_context` | Histogram (log scale) of the lower bound for all atlas variants, with picks and controls marked | Picks sit in the far right tail; controls sit in the bulk |
| `figF3_position_map` | B6 family landscape (bars: buried orange, exposed grey, interface outlined), with the aligned positions of the picks marked | How many positions the panel covers, and whether one position dominates |

## Outputs
PNG + PDF of each figure; `candidate_positions.csv` (picks per aligned position, with gene names);
`RESULTS_F2.md`. All are small and contain no tumour sites, so they can go to GitHub.

## Reading the current panel (2026-09-22 F1 run)
- 5 of the 10 F1 picks are at domain position 8 (Ala → Asp or Pro), and 4 of the 10 are substitutions to proline. figF3 shows this concentration directly.
- A panel spread over more positions would test the model across the fold (see `results/F1_experimental_candidates/ANALYSIS_F1.md`, Section 3).

## Honest limits
- The figures inherit every limit of B3 and B6: compression of severe effects, isolated-domain scoring, and a folding axis only.
- The aligned position uses the GRB2-SH3 frame. About 10 % of atlas variants have no equivalent position, and such picks would be missing from figF3.
