# C2 — Binding within one domain

*Generated automatically by the notebook on 2026-09-22T13:47:23 (7.0 min). Every number below comes from this run; nothing is typed by hand.*

## Summary

- PSD95-PDZ3 (84 positions): median ρ +0.397 over six repeats — learnable.
- GRB2-SH3 (56 positions): median ρ -0.020 (corrected), -0.030 (original); the six repeats cross zero, and ESM gives -0.126.
- Binding predictor of record: esm_zero_shot.
- The single +0.124 fit reported by Stage 3b is one draw from this spread, not a result.

**Check against the recorded run: REPRODUCED** (21 new (corrected procedure), 21 identical)

## Within-domain binding, six repeats per domain

Spearman ρ on held-out positions. single_fit = seed 0 (what Stage 3b reported), with its bootstrap CI; the repeats show what the bootstrap cannot: variance of the procedure.

| mode | domain | n | positions | repeats | repeats_median | repeats_lo | repeats_hi | esm | single_fit_rho | single_fit_ci_lo | single_fit_ci_hi | spread | crosses_zero | beats_esm |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| corrected | GB1 | 1000 | 55 | 6 | 0.053 | 0.030 | 0.212 | 0.042 | 0.043 | -0.022 | 0.111 | 0.181 | False | True |
| corrected | GRB2-SH3 | 619 | 56 | 6 | -0.020 | -0.068 | 0.022 | -0.126 | 0.022 | -0.057 | 0.105 | 0.091 | True | False |
| corrected | PSD95-PDZ3 | 1221 | 84 | 6 | 0.373 | 0.324 | 0.418 | -0.438 | 0.324 | 0.272 | 0.379 | 0.094 | False | False |
| original | GB1 | 1000 | 55 | 6 | 0.009 | -0.118 | 0.197 | 0.042 | -0.085 | -0.147 | -0.029 | 0.315 | True | True |
| original | GRB2-SH3 | 619 | 56 | 6 | -0.030 | -0.109 | 0.124 | -0.126 | 0.124 | 0.044 | 0.205 | 0.233 | True | False |
| original | PSD95-PDZ3 | 1221 | 84 | 6 | 0.397 | 0.363 | 0.412 | -0.438 | 0.391 | 0.338 | 0.443 | 0.049 | False | False |

## Decision for the atlas (read by B3)

```
{
 "head_beats_esm": false,
 "grb2_median_rho": {
  "corrected": -0.020228518867251515,
  "original": -0.030234757271434334
 },
 "grb2_esm_rho": -0.1261237460942462,
 "predictor_of_record": "esm_zero_shot"
}
```

## All quantities and their check

| quantity | this_run | recorded | status |
|---|---|---|---|
| corrected.GB1.single_fit_rho | 0.04308 |  | new (corrected procedure) |
| corrected.GB1.n | 1000 |  | new (corrected procedure) |
| corrected.GB1.positions | 55 |  | new (corrected procedure) |
| corrected.GB1.repeats_median | 0.05316 |  | new (corrected procedure) |
| corrected.GB1.repeats_lo | 0.03027 |  | new (corrected procedure) |
| corrected.GB1.repeats_hi | 0.2117 |  | new (corrected procedure) |
| corrected.GB1.spread | 0.1814 |  | new (corrected procedure) |
| GB1.esm | 0.04213 | 0.04213 | identical |
| corrected.GRB2-SH3.single_fit_rho | 0.02222 |  | new (corrected procedure) |
| corrected.GRB2-SH3.n | 619 |  | new (corrected procedure) |
| corrected.GRB2-SH3.positions | 56 |  | new (corrected procedure) |
| corrected.GRB2-SH3.repeats_median | -0.02023 |  | new (corrected procedure) |
| corrected.GRB2-SH3.repeats_lo | -0.06837 |  | new (corrected procedure) |
| corrected.GRB2-SH3.repeats_hi | 0.02222 |  | new (corrected procedure) |
| corrected.GRB2-SH3.spread | 0.09059 |  | new (corrected procedure) |
| GRB2-SH3.esm | -0.1261 | -0.1261 | identical |
| corrected.PSD95-PDZ3.single_fit_rho | 0.3241 |  | new (corrected procedure) |
| corrected.PSD95-PDZ3.n | 1221 |  | new (corrected procedure) |
| corrected.PSD95-PDZ3.positions | 84 |  | new (corrected procedure) |
| corrected.PSD95-PDZ3.repeats_median | 0.3732 |  | new (corrected procedure) |
| corrected.PSD95-PDZ3.repeats_lo | 0.3241 |  | new (corrected procedure) |
| corrected.PSD95-PDZ3.repeats_hi | 0.4183 |  | new (corrected procedure) |
| corrected.PSD95-PDZ3.spread | 0.09421 |  | new (corrected procedure) |
| PSD95-PDZ3.esm | -0.438 | -0.438 | identical |
| original.GB1.single_fit_rho | -0.08462 | -0.08462 | identical |
| original.GB1.n | 1000 | 1000 | identical |
| original.GB1.positions | 55 | 55 | identical |
| original.GB1.repeats_median | 0.009339 | 0.009339 | identical |
| original.GB1.repeats_lo | -0.1182 | -0.1182 | identical |
| original.GB1.repeats_hi | 0.1966 | 0.1966 | identical |
| original.GB1.spread | 0.3148 |  |  |
| original.GRB2-SH3.single_fit_rho | 0.1243 | 0.1243 | identical |
| original.GRB2-SH3.n | 619 | 619 | identical |
| original.GRB2-SH3.positions | 56 | 56 | identical |
| original.GRB2-SH3.repeats_median | -0.03023 | -0.03023 | identical |
| original.GRB2-SH3.repeats_lo | -0.1086 | -0.1086 | identical |
| original.GRB2-SH3.repeats_hi | 0.1243 | 0.1243 | identical |
| original.GRB2-SH3.spread | 0.233 |  |  |
| original.PSD95-PDZ3.single_fit_rho | 0.3911 | 0.3911 | identical |
| original.PSD95-PDZ3.n | 1221 | 1221 | identical |
| original.PSD95-PDZ3.positions | 84 | 84 | identical |
| original.PSD95-PDZ3.repeats_median | 0.397 | 0.397 | identical |
| original.PSD95-PDZ3.repeats_lo | 0.3631 | 0.3631 | identical |
| original.PSD95-PDZ3.repeats_hi | 0.412 | 0.412 | identical |
| original.PSD95-PDZ3.spread | 0.04891 |  |  |
| head_beats_esm_on_grb2 | False |  |  |

## Environment

| python | numpy | pandas | scipy | sklearn | transformers | torch | gpu |
|---|---|---|---|---|---|---|---|
| 3.13.15 | 2.1.3 | 2.2.3 | 1.16.3 | 1.6.1 | 5.16.1 | 2.11.0+cu128 | Tesla T4 |
