# D1 — Figures and verification

*Generated automatically by the notebook on 2026-09-22T15:47:48 (0.3 min). Every number below comes from this run; nothing is typed by hand.*

## Summary

- Stage 0: 6,884 variants in 310 domains; byte-identical to the original atlas: True.
- Folding: per-domain median ρ 0.839 on 15 held-out SH3 domains; beats ESM-2 on 15/15.
- Specificity: damage vs burial ρ +0.712, vs interface ρ +0.037.
- Binding: GRB2-SH3 median ρ -0.030 (original) / -0.02 (corrected); predictability appears at ~76 positions, GRB2-SH3 has 56.
- Atlas: 297 destabilising, 113 both, 191 rewiring (not claimed), 6,283 tolerated; genes enriched 1/170.
- Specificity axis (C4): median centred r +0.288; not validated - no rewiring claim.
- Virtual scan (B6): 366,168 substitutions; 12.1% of all possible vs 6.0% of observed cancer variants destabilising.
- Reproduction: 160 identical, 27 within tolerance, 0 different, of 187 recorded quantities.

**Check against the recorded run: no recorded values to compare** ()

## Reproduction by program

| program | identical | within tolerance | DIFF | verdict | minutes |
|---|---|---|---|---|---|
| A0 | 20 | 0 | 0 | REPRODUCED | 14.3 |
| A1 | 15 | 11 | 0 | REPRODUCED | 1.4 |
| A2 | 8 | 13 | 0 | REPRODUCED | 20.9 |
| B1 | 8 | 2 | 0 | REPRODUCED | 1.5 |
| B2 | 3 | 0 | 0 | REPRODUCED | 0.2 |
| B3 | 7 | 1 | 0 | REPRODUCED | 0 |
| B4 | 12 | 0 | 0 | REPRODUCED | 11.4 |
| B5 | 15 | 0 | 0 | REPRODUCED | 0.7 |
| C1 | 9 | 0 | 0 | REPRODUCED | 1.1 |
| C2 | 21 | 0 | 0 | REPRODUCED | 7 |
| C3 | 42 | 0 | 0 | REPRODUCED | 0.1 |

## Binding: ORIGINAL vs CORRECTED partitions (key quantities)

Full table: `original_vs_corrected.csv`.

| program | what | corrected | original | recorded | change |
|---|---|---|---|---|---|
| C1 | GRB2-SH3.rho | -0.042 | 0.097 | 0.097 | -0.139 |
| C2 | GRB2-SH3.repeats_median | -0.020228518867251515 | -0.030234757271434334 | -0.030 | 0.010 |
| C2 | PSD95-PDZ3.repeats_median | 0.37324460718252145 | 0.3969932390406754 | 0.397 | -0.024 |
| C3 | matched_median_rho | -0.0236544045511511 | -0.02295522768657405 | -0.023 | -0.001 |
| C3 | sweep_B_thin_median | 0.32680838514224125 | 0.3570813960594219 | 0.357 | -0.030 |
| C3 | sweep_C_fewpos_median | 0.0542360598494859 | 0.0758558404584435 | 0.076 | -0.022 |

## All quantities and their check

| quantity | this_run | recorded | status |
|---|---|---|---|
| quantities_checked | 187 |  |  |
| identical | 160 |  |  |
| within_tolerance | 27 |  |  |
| different | 0 |  |  |

## Environment

| python | numpy | pandas | scipy | sklearn | transformers | torch | gpu |
|---|---|---|---|---|---|---|---|
| 3.13.15 | 2.1.3 | 2.2.3 | 1.16.3 | 1.6.1 | 5.16.1 | 2.11.0+cpu | none |
