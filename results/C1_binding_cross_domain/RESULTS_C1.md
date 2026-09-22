# C1 — Binding across domains (leave-one-domain-out)

*Generated automatically by the notebook on 2026-09-22T13:44:01 (1.1 min). Every number below comes from this run; nothing is typed by hand.*

## Summary

- Held-out GRB2-SH3: head ρ +0.097 (original) / -0.042 (corrected) against zero-shot ESM -0.126.
- The head beats ESM on 0/3 held-out domains in the corrected version.
- Transfer between unrelated binding modes fails; the next question (C2) removes transfer altogether.

**Check against the recorded run: REPRODUCED** (15 new (corrected procedure), 9 identical)

## Leave-one-domain-out

Spearman ρ on the held-out domain, 95% bootstrap CI. ESM = zero-shot score.

| mode | held_out | n | rho | lo | hi | esm | beats_esm |
|---|---|---|---|---|---|---|---|
| original | GB1 | 1000 | -0.090 | -0.151 | -0.028 | 0.042 | False |
| corrected | GB1 | 1000 | -0.151 | -0.216 | -0.086 | 0.042 | False |
| original | GRB2-SH3 | 619 | 0.097 | 0.017 | 0.176 | -0.126 | False |
| corrected | GRB2-SH3 | 619 | -0.042 | -0.119 | 0.036 | -0.126 | False |
| original | PSD95-PDZ3 | 1221 | 0.112 | 0.057 | 0.171 | -0.438 | False |
| corrected | PSD95-PDZ3 | 1221 | 0.132 | 0.076 | 0.188 | -0.438 | False |

## All quantities and their check

| quantity | this_run | recorded | status |
|---|---|---|---|
| original.GB1.rho | -0.09037 | -0.09037 | identical |
| original.GB1.esm | 0.04213 | 0.04213 | identical |
| original.GB1.n | 1000 | 1000 | identical |
| original.GB1.lo | -0.1506 |  |  |
| original.GB1.hi | -0.02766 |  |  |
| corrected.GB1.rho | -0.1508 |  | new (corrected procedure) |
| corrected.GB1.esm | 0.04213 |  | new (corrected procedure) |
| corrected.GB1.n | 1000 |  | new (corrected procedure) |
| corrected.GB1.lo | -0.2159 |  | new (corrected procedure) |
| corrected.GB1.hi | -0.08628 |  | new (corrected procedure) |
| original.GRB2-SH3.rho | 0.09684 | 0.09684 | identical |
| original.GRB2-SH3.esm | -0.1261 | -0.1261 | identical |
| original.GRB2-SH3.n | 619 | 619 | identical |
| original.GRB2-SH3.lo | 0.01709 |  |  |
| original.GRB2-SH3.hi | 0.176 |  |  |
| corrected.GRB2-SH3.rho | -0.04214 |  | new (corrected procedure) |
| corrected.GRB2-SH3.esm | -0.1261 |  | new (corrected procedure) |
| corrected.GRB2-SH3.n | 619 |  | new (corrected procedure) |
| corrected.GRB2-SH3.lo | -0.1195 |  | new (corrected procedure) |
| corrected.GRB2-SH3.hi | 0.0358 |  | new (corrected procedure) |
| original.PSD95-PDZ3.rho | 0.1118 | 0.1118 | identical |
| original.PSD95-PDZ3.esm | -0.438 | -0.438 | identical |
| original.PSD95-PDZ3.n | 1221 | 1221 | identical |
| original.PSD95-PDZ3.lo | 0.05694 |  |  |
| original.PSD95-PDZ3.hi | 0.1708 |  |  |
| corrected.PSD95-PDZ3.rho | 0.1315 |  | new (corrected procedure) |
| corrected.PSD95-PDZ3.esm | -0.438 |  | new (corrected procedure) |
| corrected.PSD95-PDZ3.n | 1221 |  | new (corrected procedure) |
| corrected.PSD95-PDZ3.lo | 0.07597 |  | new (corrected procedure) |
| corrected.PSD95-PDZ3.hi | 0.1881 |  | new (corrected procedure) |

## Environment

| python | numpy | pandas | scipy | sklearn | transformers | torch | gpu |
|---|---|---|---|---|---|---|---|
| 3.13.15 | 2.1.3 | 2.2.3 | 1.16.3 | 1.6.1 | 5.16.1 | 2.11.0+cu128 | Tesla T4 |
