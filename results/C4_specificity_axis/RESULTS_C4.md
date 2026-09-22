# C4 — Independent specificity axis (PWMs)

*Generated automatically by the notebook on 2026-09-22T15:03:10 (8.1 min). Every number below comes from this run; nothing is typed by hand.*

## Summary

- 154 of 154 PWMs linked to 115 domain sequences; tested by holding out 52 clusters of related domains.
- Predicted vs observed specificity: median centred r +0.288 [95% CI +0.218, +0.337]; beats the average profile on 55/115 domains and the nearest-neighbour profile on 85/115.
- Pre-specified rule: NOT validated.
- Without a validated axis, the fold/rewiring separation stays untested; this is reported as a data limit.

**Check against the recorded run: no recorded values to compare** ()

## Cross-validated test (whole clusters of related domains held out)

centred r: correlation of predicted and observed profile after removing the training average (the shared proline preference). js: Jensen–Shannon distance, lower is better.

| index | cluster | alpha | nearest_identity | r_model | r_nearest | js_model | js_nearest | js_mean |
|---|---|---|---|---|---|---|---|---|
| count | 115.000 | 115.000 | 115.000 | 115.000 | 115.000 | 115.000 | 115.000 | 115.000 |
| mean | 44.870 | 483.478 | 0.296 | 0.245 | 0.126 | 0.242 | 0.306 | 0.233 |
| 50% | 35.000 | 100.000 | 0.339 | 0.288 | 0.119 | 0.212 | 0.310 | 0.214 |
| min | 0.000 | 100.000 | -0.146 | -0.635 | -0.749 | 0.073 | 0.067 | 0.059 |
| max | 111.000 | 1000.000 | 0.397 | 0.822 | 0.887 | 0.524 | 0.541 | 0.557 |

## Decision

```
{
 "validated": false,
 "median_centred_r": 0.2884351199911039,
 "ci": [
  0.21787147270325652,
  0.33709832953579966
 ],
 "wins_vs_mean": 55,
 "wins_vs_nearest": 85,
 "domains": 115,
 "sign_test_p": 1.0,
 "rule": "CI of median centred r above 0 AND sign test vs average profile p < 0.05"
}
```

## Two-axis map of the atlas

**NOT validated — shown for completeness; no rewiring claim is made.** Rewiring vs predicted folding damage ρ +0.356; vs zero-shot ESM ρ -0.393. Interface positions: median rewiring 0.0309 vs 0.0269 elsewhere (one-sided p 7.6e-24).

| folding axis | other | top-10% rewiring |
|---|---|---|
| destabilising | 320 | 90 |
| not destabilising | 5875 | 599 |

## All quantities and their check

| quantity | this_run | recorded | status |
|---|---|---|---|
| pwms | 154 |  |  |
| pwms_matched | 154 |  |  |
| domains | 115 |  |  |
| clusters | 52 |  |  |
| median_centred_r | 0.2884 |  |  |
| median_centred_r_ci_lo | 0.2179 |  |  |
| median_centred_r_ci_hi | 0.3371 |  |  |
| wins_vs_average_profile | 55 |  |  |
| wins_vs_nearest_neighbour | 85 |  |  |
| sign_test_p | 1 |  |  |
| validated | False |  |  |
| rho_rewiring_vs_predicted_fold | 0.3555 |  |  |
| rho_rewiring_vs_esm_score | -0.3932 |  |  |
| rewiring_interface_median | 0.03094 |  |  |
| rewiring_other_median | 0.02693 |  |  |
| interface_test_p | 7.581e-24 |  |  |
| n_top_rewiring_not_destabilising | 599 |  |  |
| n_both_axes | 90 |  |  |

## Environment

| python | numpy | pandas | scipy | sklearn | transformers | Bio | torch | gpu |
|---|---|---|---|---|---|---|---|---|
| 3.13.15 | 2.1.3 | 2.2.3 | 1.16.3 | 1.6.1 | 5.16.1 | 1.88 | 2.11.0+cu128 | Tesla T4 |
