# D1 — Figures and verification

**Purpose.** One place that says whether the whole pipeline reproduced, and draws the figures from
the programs' own output files. Nothing is recomputed here.

## Reproduction report
- **What is checked:** every program compared its numbers with `reference/expected_values.json`.
  D1 gathers those comparisons into `reproduction_table.csv`, with counts per program of
  identical / within tolerance / different.
- **Tolerances:** exact (≤ 1e-9) for anything deterministic. Looser only for values recorded to three
  decimals, and for the pooled folding ρ, which the original computed with a slightly different
  clip setting.
- **ORIGINAL vs CORRECTED:** `original_vs_corrected.csv` puts every binding quantity measured both
  ways side by side, with the recorded value.

## Figures
| File | Shows |
|---|---|
| fig1 | Folding head vs ESM-2 on every held-out SH3 domain |
| fig2 | Damage follows burial, not the interface |
| fig3 | Positions, not rows (both partition modes) |
| fig4 | ProteinGym transfer |
| fig5 | Atlas calls and the biological tests |
| fig6 | Refitting the same binding data, both modes |
| fig7 | The specificity axis (C4), if run |
| fig8 | The family-wide folding landscape (B6), if run |

`results/RESULTS_SUMMARY.md` is the one-page overview.
