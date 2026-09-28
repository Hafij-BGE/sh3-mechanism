# G2 — analysis

Run 28 September 2026, locally, seconds on CPU. Machine numbers in `metrics_G2.json` and
`per_domain_q90_G2.csv`.

G2 recalibrates an interval and reports the consequence. **It re-fits nothing, changes no prediction,
and does not move the `fold_lo ≥ 1` rule.** There is no pass/fail verdict, so there is no
pre-registration.

The frozen calibration reproduces exactly before anything else runs: **q90 = 6.8073** against the
published 6.807, coverage **89.92 %** against 89.9 %, and **410** confident calls on the atlas. All
three are asserted.

---

## The problem

The frozen run reports 89.9 % empirical coverage for a 90 % interval. That is **marginal** coverage —
correct on average over all held-out variants — and it says nothing about any particular domain.
B3's own stratified table already showed the spread, and it is wide:

| | coverage under the global q90 |
|---|---|
| LYN | **83.3 %** |
| LASP1 | 83.9 % |
| … | |
| TEC | 93.9 % |
| FYN | **95.0 %** |

**A "90 % interval" that is 83 % on one domain and 95 % on another is two different instruments
sharing a name.** The normalisation by ensemble SD was supposed to absorb this and does not.

## Per-domain calibration

Mondrian conformal prediction calibrates within each stratum. Using each gene's own calibration half:

| gene | *n* cal | q90 | coverage, global | coverage, Mondrian |
|---|---|---|---|---|
| LYN | 506 | **9.71** | 0.833 | 0.939 |
| LASP1 | 530 | 8.90 | 0.839 | 0.936 |
| HCK | 496 | 7.91 | 0.846 | 0.885 |
| BTK | 511 | 7.58 | 0.858 | 0.893 |
| PLCG1 | 549 | 6.65 | 0.886 | 0.876 |
| LCK | 501 | 6.67 | 0.890 | 0.890 |
| SPTAN1 | 5063 | 6.57 | 0.900 | 0.890 |
| DOCK1 | 616 | 6.99 | 0.904 | 0.907 |
| OBSCN | 617 | 5.98 | 0.907 | 0.882 |
| NPHP1 | 1088 | 6.28 | 0.908 | 0.892 |
| SORBS1 | 576 | 7.77 | 0.909 | 0.929 |
| OSTF1 | 515 | 6.94 | 0.914 | 0.914 |
| PTK6 | 561 | 6.23 | 0.933 | 0.903 |
| TEC | 547 | 5.77 | 0.939 | 0.918 |
| FYN | 1119 | **5.42** | 0.950 | 0.903 |

**The per-domain quantile ranges from 5.42 to 9.71 — a factor of 1.79.** One domain needs an interval
nearly twice as wide as another for the same nominal confidence, and a single global number splits
the difference.

Coverage spread narrows from **11.8 pp to 6.3 pp**. It does not vanish, and should not be expected
to: a 90 % quantile estimated from ~500 calibration points carries its own sampling error, and at
*n* ≈ 500 the binomial standard deviation of an empirical coverage is about 1.3 pp, so a range of
roughly 5 pp across fifteen domains is close to what noise alone produces. **The remaining spread is
mostly finite-sample, where the 11.8 pp under the global quantile was structural.**

The per-domain quantile shows no obvious pattern. Seven of the fifteen are tyrosine kinases and they
sit at both extremes — LYN at 9.71 and FYN at 5.42 — so it is not a family effect, and nothing here
explains it. That is reported rather than rationalised.

## What it does to the published count

This is the number the plan asked for, and it is the reassuring part.

| | confident calls |
|---|---|
| Global q90 = 6.807 (published) | **410** |
| Per-domain where calibrated, global elsewhere | **409** |
| Every domain at the minimum q90 (5.42) | 613 |
| Every domain at the maximum q90 (9.71) | 149 |
| **Each domain drawn from the observed per-domain spread** | **400, 95 % interval 378–421** |

The hybrid moves the count by one, because only **439 of 6,884** atlas variants (6.4 %) belong to a
gene with a per-domain calibration. That is not evidence of robustness — it is evidence that the
hybrid barely applies.

The resampling is the honest test. Giving each of the 310 atlas domains a q90 drawn from the fifteen
observed values, 2,000 times, puts the count at **400 with a 95 % interval of 378–421**. The
published 410 sits inside that band.

**The 149–613 bracket is not the uncertainty.** It places every domain simultaneously at one
extreme, which cannot happen. Quoting it would overstate the problem by an order of magnitude.

## The distinction that matters

The two uses of this interval are affected very differently, and the report should separate them:

- **A per-variant claim** — *"this variant's ΔΔG is at least 1 kcal/mol with 90 % confidence"* — is
  **not** reliable at the stated confidence. On a LYN-like domain the real figure is 83 %. Where a
  per-domain quantile exists it should be used, and where it does not, the claim should carry the
  range rather than the nominal 90 %.
- **The aggregate count** — 410 of 6,884 — **is** robust. Per-domain recalibration moves it within
  378–421, roughly ±8 %, because the count is dominated by variants far from the threshold and only
  those near it can flip.

E1 already established that `fold_lo ≥ 1` has 4.8 % sensitivity on pathogenic variants and is not a
clinical filter. G2 adds the conditional-coverage caveat to the same conclusion: **the threshold is
for ranking and triage, not for a per-variant confidence statement.**

## Limitations

- **Fifteen domains is a small sample of quantiles.** The resampling treats the observed fifteen as
  the population of per-domain behaviour; the true spread across 310 atlas domains could be wider,
  and nothing here bounds it.
- **The held-out domains are MegaScale constructs**, so the per-domain quantiles are estimated on a
  different assay from anything the atlas variants were measured in.
- **No per-domain calibration exists for 295 of the 310 atlas domains**, and none can without
  measurements in them. The hybrid column is therefore more of a demonstration than a
  recommendation.
- G2 does not explain *why* the quantile varies by 1.79×. A normaliser that absorbed it would be the
  real fix, and finding one is a modelling problem, not a calibration one.

## Effect on the project

No published number changes. The frozen run's 410 stands, now with a stated band, and the reported
89.9 % coverage stands as a marginal figure with the conditional spread reported beside it.

`OUTCOMES.md` and `MANUSCRIPT.md` gain the conditional-coverage caveat where the confident-call count
and the coverage figure are quoted.

## Status

Complete. No pre-registration was required and none was written; the global calibration is reproduced
and asserted before any recalibration runs.
