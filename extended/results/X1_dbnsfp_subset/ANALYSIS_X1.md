# X1 — analysis

Run 27 September 2026, final pass 17:29. Machine numbers in `RESULTS_X1.md`, `crosscheck_X1.json`
and `columns_X1.json` on Drive.

X1 acquires and reduces. It computes no comparison and returns no verdict — that needs a
pre-registration written first, and none exists yet.

---

## What came out

| | |
|---|---|
| `dbnsfp_sh3.tsv.gz` | 2,120,008 rows, 235 genes, 37 columns |
| `dbnsfp_sh3_domains.parquet` | **152,852 rows inside an SH3 domain**, 231 of 235 genes, 300 of 310 domains |

152,852 is the expected magnitude: 300 domains × ~60 residues × ~9 reachable missense alleles ≈
162,000. Nothing is missing at the scale of a chromosome.

## What dbNSFP is for, and what it is not

It carries ~50 precomputed **pathogenicity** predictors per missense variant. Our head predicts
**ΔΔG of folding**. They answer different questions:

- **Not an E3 competitor.** E3 benchmarks *stability* predictors. A pathogenicity score in that table
  would be a category error.
- **The external comparison for E1**, whose question was whether our stability calls track
  pathogenicity.

dbNSFP ships its own ClinVar benchmark. On all genes, star 1+ missense, the best scores reach
**AUC 0.94–0.99** (MetaRNN 0.988, REVEL 0.976, AlphaMissense 0.964). E1 put our stability head at
rank-biserial +0.615, i.e. **AUC ≈ 0.81**. So the question worth pre-registering is not whether a
folding model beats dedicated pathogenicity predictors — it should not — but **whether ΔΔG_fold
carries anything they do not**, on the same variants.

## Coverage is the evidence that the extraction is correct

Every predictor now lands within a few points of dbNSFP's published coverage, and **systematically
just under it**, which is exactly right: our denominator is every possible in-domain missense SNV,
theirs is ClinVar-labelled variants, which are biased toward well-annotated positions.

| | ours | published |
|---|---|---|
| phyloP100way | 100.0 % | 100.0 % |
| CADD | 100.0 % | 99.6 % |
| GERP++ | 99.4 % | 99.5 % |
| ESM1b | 91.9 % | 91.7 % |
| BayesDel | 89.6 % | 88.9 % |
| VEST4 | 85.5 % | 85.3 % |
| AlphaMissense | 85.4 % | 88.5 % |
| REVEL | 78.0 % | 83.7 % |
| SIFT | 76.1 % | 82.4 % |
| MPC | 70.7 % | 73.1 % |

That agreement is not decoration. It is the only external check available on a reduction with no
ground truth of its own, and **three earlier versions of this table were nonsense** — which is the
substance of X1.

## Four defects, and how each was caught

| # | defect | how it showed | consequence if missed |
|---|---|---|---|
| 1 | `cut -f` emits fields in **ascending file order**, whatever order they are listed; the header was written in a different order | AlphaMissense 2.5 %, CADD_phred 0.0 %, `clinvar_id` 100 % | every predictor column under the wrong name — silently wrong analysis |
| 2 | dbNSFP writes `.` for missing, not an empty field | every predictor showed 100.0 % coverage | missingness invisible; coverage claims false |
| 3 | pandas infers dtypes **per chunk**, so `#chr` was int64 in some chunks and object in the ones with X/Y | `ArrowInvalid` on the parquet write | crash, at least loud |
| 4 | taking element `[0]` of a semicolon-separated per-transcript field | transcript-keyed predictors at ~half their published coverage; position-keyed ones correct | a systematic, predictor-specific bias that looks like real missingness |

**Defect 1 is the dangerous one.** It produced a complete, plausible, internally consistent file whose
every predictor column was mislabelled. The 11 key columns escaped only by luck — my hand-written
order happened to match dbNSFP's for `#chr` through `HGVSp_VEP` — which is why the domain filtering
gave the right answer (152,852, unchanged across every version) while the predictors were wrong.

Nothing in the pipeline would have caught it. It was caught by **comparing coverage against the
publisher's own figures** — an external reference the reduction did not control. That is the
transferable lesson: a derived table needs at least one number that can be checked against something
outside itself.

The extraction now asserts that the header field count, the first data row's field count and
`len(KEEP)` all agree, before the result is cached.

## The one thing still unexplained: 63.8 %

Of the 3,725 ClinVar variants we independently found inside SH3 domains, dbNSFP's in-domain set
contains **2,377 — 63.8 %**. Two explanations were proposed and both are refuted:

- **The first-listed-value convention.** Refuted: fixing it changed predictor coverage substantially
  and the cross-check **not at all** (2,377 before and after). `aapos` is populated on the first
  transcript for essentially every row.
- **Non-SNV records.** Refuted by direct count: of the 3,725 keys, **3,717 have at least one
  single-nucleotide record**. dbNSFP is SNV-only, so this accounts for 8 of ~1,348.

What remains is the **transcript axis**: dbNSFP gives one `aapos` per transcript and we filter on the
first, while ClinVar reports on the transcript *it* chose. A variant at residue 45 on transcript A and
112 on transcript B is in-domain under one and not the other. A diagnostic is now in the notebook that
explodes every transcript position and reports recovery both ways; it has not yet been run.

**Until that number exists, dbNSFP's ClinVar column should not be used as a cross-check on ours**, and
any E1 follow-up must join on its own terms rather than assuming the two sets align.

## Practical notes worth keeping

- **No tabix or CSI index ships with the release**, so a region query is impossible and the subset
  costs one full streaming pass. `dbNSFP5.4a_grch38.gz` **is** BGZF with 508 columns, so it could be
  indexed once and queried thereafter — worth doing if this is ever repeated.
- **The popmax frequency is spelled `gnomAD4.1_joint_POPMAX_AF`** in this release. A fuzzy column
  matcher had been silently resolving the request to `gnomAD4.1_joint_POPMAX_AC` — an allele *count*
  where a *frequency* was asked for. Exact matching only, now, with candidates printed on a miss.
- The two large files on Drive hold the same release twice, about 100 GB together.

## Status

Complete as an acquisition. Not yet usable as a comparison: the 63.8 % question is open, and any
program that uses these predictors needs a pre-registration first.
