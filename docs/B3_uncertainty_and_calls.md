# B3 — Uncertainty and the mechanism call

**Purpose.** Call a variant destabilising only when the evidence survives error control.

## Method
- **Normalised split-conformal prediction** (Lei et al. 2018) on the held-out SH3 family.
  - *Calibration half:* the 90th percentile of |error| / (ensemble SD + 0.05) gives q90.
  - *Validation half:* measures the coverage actually achieved.
- **Interval:** prediction ± q90 × (SD + 0.05).
- **Call:** a variant is **destabilising** only if the interval's lower bound is ≥ 1 kcal/mol.
  This turns the point-estimate calls into a smaller set under error control.
- **Binding axis:** zero-shot ESM-2, rank-matched to the measured GRB2-SH3 binding distribution so the
  1 kcal/mol threshold has units. B3 reads C2's decision file and stops if a trained binding head
  ever beats ESM-2.

## Terminology (roadmap Tier 1, item 1)
The binding column is an **ESM-2 proxy**, not a binding prediction. Mutations it flags are labelled
`rewiring` for continuity with the original run, but no binding claim rests on them. C4 is the
attempt at a real second axis.

## Diagnostics (roadmap I1, I3, I4)
- **Calibration curve:** nominal vs empirical coverage at 50–95 %.
- **Rejection curve:** accuracy of the 5 %, 10 %, 20 % … most confident predictions.
- **Stratified coverage:** coverage by predicted-effect bin and by domain. Burial cannot be a
  stratum, because the held-out MegaScale variants carry no structure.
- **The old filter:** ensemble spread correlates only about +0.30 with the real error, which is why
  the original "confidence" filter (SD < 0.5) passed almost everything.

## Expected result
q90 6.807, coverage 89.9 %; 297 destabilising, 113 both, 191 rewiring (proxy), 6,283 tolerated.
