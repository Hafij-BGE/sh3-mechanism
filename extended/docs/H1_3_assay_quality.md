# H1.3 — Is H1's family ordering assay quality?

**Why it is needed.** H1 returned inconclusive on its main arm and named two explanations it could
not separate: zinc coordination, and assay quality. This tests the second — the one answerable with
data already in hand.

**Pre-registered** in `docs/preregistration/H1_3_assay_quality.md`, committed before accuracy and
assay quality were joined. It is pre-registered *because* it is post-hoc: the question came from
H1's result, so the rule had to be fixed before the answer existed.

**What it does not do.** No prediction is recomputed. H1's per-domain correlations are read as
published.

## Method

Assay quality per domain is `median(|normalized_fitness| / replicate σ)`. The two arms are restricted
to a common band — the main arm's 10th percentile to SH3's 90th, **1.28–3.80** — and the H1 statistic
is recomputed inside it: median per-domain |ρ|, Δ against SH3, 95 % CI from 4,000 bootstrap
resamples over domains, margin −0.15.

Matching retains **31 of 35** main domains and **30 of 36** SH3, so power is essentially H1's.

## What it found

**Measurement quality does not explain the gap.**

| | main | SH3 | Δ | 95 % CI |
|---|---|---|---|---|
| Unmatched (H1) | 0.420 | 0.623 | −0.203 | [−0.249, −0.120] |
| Matched | 0.432 | 0.619 | **−0.187** | [−0.232, −0.098] |

A shift of 0.015, against the 0.05 threshold the pre-registration set as this design's resolution.

**Myb/SANT settles it more cleanly than the matched test:** assay quality 2.535 against SH3's 2.086,
accuracy 0.507 against 0.623. **Better measurements, lower accuracy.**

H1's variant-weighted arm figures (main 1.863, SH3 2.199) pointed the other way and were misleading —
PHD and B-box have many variants and poor measurements, so they dominated the average. Per domain the
arms overlap almost entirely.

**Two caveats it produced:**

- Assay quality does predict accuracy *between domains* — Spearman **+0.629**, n = 102 — but this is
  partly mechanical, since a noisier domain has an attenuated correlation with anything.
- **It qualifies H1's PDZ result.** Matched, PDZ keeps 18 of 31 domains, its median falls 0.602 →
  0.541 and Δ goes −0.021 → **−0.077** (CI still includes 0). The length finding survives; the parity
  is partly better measurements.

**Zinc is not promoted by elimination** — Part 5 ruled that out in advance, and Myb/SANT binds no
metal yet sits 0.12 below SH3.

## Outputs

`per_domain_rho_and_snr.csv`, `metrics_H1_3.json`, `METHODS_H1_3.md`, `ANALYSIS_H1_3.md`.

## Runtime

Seconds on CPU. `python3 tools/h1_3_assay_quality.py --rho ... --domainome ... --out ...`
