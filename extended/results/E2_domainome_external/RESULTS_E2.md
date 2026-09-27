# E2 - validation against measured human abundance

Run 2026-09-27 05:29. Machine-written; see ANALYSIS_E2.md for interpretation.

## Coverage

| atlas variants | 6,884 |
|---|---|
| measured in Domainome | **880** |
| domains / genes | 41 / 32 |

## Agreement with measured abundance

Pooled Spearman rho = **-0.600** (p = 4.09e-87, n = 880).
Per-domain median -0.573; correct direction in 21/21 domains with n >= 20.

| gene | n | rho |
|---|---|---|
| VAV1 | 41 | -0.744 |
| PSTPIP1 | 24 | -0.742 |
| LCK | 26 | -0.735 |
| BTK | 40 | -0.725 |
| NCF2 | 24 | -0.718 |
| DNMBP | 22 | -0.705 |
| DNMBP | 22 | -0.675 |
| ITK | 25 | -0.656 |
| RASA1 | 27 | -0.634 |
| GRB2 | 28 | -0.613 |
| SRC | 25 | -0.573 |
| SPTA1 | 38 | -0.548 |
| ABL1 | 34 | -0.522 |
| BLK | 20 | -0.508 |
| SRGAP3 | 29 | -0.491 |
| PLCG2 | 27 | -0.462 |
| NCF2 | 25 | -0.398 |
| EPS8 | 24 | -0.385 |
| FYN | 41 | -0.380 |
| NPHP1 | 21 | -0.374 |
| HCK | 24 | -0.339 |

## Confidently destabilising calls (fold_lo >= 1)

median fitness -0.748 (n=63) against -0.106 (n=817); Mann-Whitney p = 2.324e-22.

## Noise ceiling

MegaScale vs Domainome on the same variants. |rho| throughout.

| gene | n | ceiling | ours | share |
|---|---|---|---|---|
| BTK | 1036 | 0.746 | 0.725 | 97% |
| LCK | 971 | 0.735 | 0.735 | 100% |
| HCK | 819 | 0.684 | 0.339 | 50% |
| SPTB1 | 1182 | 0.574 | - | - |

Median ceiling **0.709**.

### Matched subset (identical variants both sides)

| gene | n | ceiling | ours | share |
|---|---|---|---|---|
| LCK | 26 | 0.815 | 0.735 | 90% |
| HCK | 19 | 0.593 | 0.604 | 102% |
| BTK | 39 | 0.623 | 0.704 | 113% |

## Data handling

- 45 Domainome rows dropped: fitness present but a null position.
- 3,856 rows collapsed: one domain can carry two Pfam annotations at the same start.
- The left join is asserted not to change the atlas row count.