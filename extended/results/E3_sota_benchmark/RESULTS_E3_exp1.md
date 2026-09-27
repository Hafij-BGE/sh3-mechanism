# E3 - benchmark against current predictors (Experiment 1, base)

Run 2026-09-27 12:37. Machine-written. Plan fixed in advance: `docs/preregistration/E3.md` @ ccd3446.

15 held-out SH3 domains, 27,590 variants. Our numbers are B1 frozen and were re-derived from it here (median rho +0.839).

## Leakage audit, reported as a result

| competitor | held-out domains in its published training data | role |
|---|---|---|
| SaProtΔG | 0 of 15 | verdict |
| ESM3ΔG | 0 of 15 | verdict |
| ThermoMPNN | **13 of 15** (12 train, 1 val) | descriptive only, 2 clean domains |

A MegaScale-derived benchmark cannot compare MegaScale-trained predictors without this check. Presence or absence is established in the *published* split, not in whatever the released weights saw.

## Comparison

| competitor | domains | scored | dropped | median rho | ours | median diff | p | verdict |
|---|---|---|---|---|---|---|---|---|
| SaProtdG | 15 | 27,590 | 0 | +0.855 | +0.839 | -0.028 | 0.107 | **no clear difference** |

Significance: p < 0.025 (0.05 across the two competitors carrying a verdict). Positive median diff means our model correlates better.

Signs were aligned by each source documented convention, not by which direction correlated better. The unaligned median correlations were SaProtdG -0.855.

## Read with

- 15 domains detects large gaps, not small ones - stated in the plan before any result.
- SaProtΔG and ESM3ΔG receive a 3D structure; our model never did.
- ESM3ΔG was NOT RUN (gated model, no token); the other arms stand.
- ThermoMPNN carries no verdict at any n. Its two clean domains are FYN and NPHP1. **It did not run**; the reason is in metrics_E3.json.