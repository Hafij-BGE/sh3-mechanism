# E1 - ClinVar and gnomAD

Run 2026-09-27 04:54. Machine-written. Plan fixed in advance: `docs/preregistration/E1.md` @ 07d2b81, amended e9b509e.

Predictions come from B6 (22 Sep 2026), computed for an unrelated question five days before this plan and without reference to any clinical label.

ClinVar variants inside SH3 domains: 134. gnomAD: 24,005.

## Q1 - do the calls track pathogenicity? (continuous, primary)

| arm | n path | n benign | verdict | p | effect |
|---|---|---|---|---|---|
| 1 - MAIN (1+ stars) | 21 | 101 | yes | 4.89e-06 | +0.615 |
| 3 (0+ stars) | 28 | 106 | yes | 1.18e-06 | +0.582 |
| 4 (1+ stars, AF>5%) | 21 | 101 | yes | 4.89e-06 | +0.615 |
| 2 (2+ stars) | 4 | 25 | too few | - | - |
| 6 (atlas only) | 3 | 35 | too few | - | - |

## Q2 - are common variants depleted? (B6 null)

| arm | n common | observed | expected | verdict | p |
|---|---|---|---|---|---|
| 1 - MAIN (popmax>1%) | 35 | 0.0% | 9.6% | no | 0.0289 |
| 3 (popmax>1%) | 35 | 0.0% | 9.6% | no | 0.0289 |
| 4 (popmax>5%) | 19 | 0.0% | 9.4% | too few | - |
| 2 (popmax>1%) | 35 | 0.0% | 9.6% | no | 0.0289 |
| 6 (atlas only) | 30 | 0.0% | 9.4% | no | 0.0513 |

## Reading, by the rule fixed in advance

The verdict is arm 1's: **yes**.
Every arm with enough data agrees, so the result does not depend on these choices.

**Power.** 21 disease-causing against 126 harmless detects a large effect and nothing smaller; a null here is ambiguous between absence and insufficient power, as stated in the pre-registration before any result existed.