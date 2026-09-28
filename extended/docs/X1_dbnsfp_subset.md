# X1 — Reduce dbNSFP to the SH3 domains

**Why it is needed.** dbNSFP 5.4a carries ~50 precomputed pathogenicity predictors for every possible
human missense SNV, in a 508-column release of about 100 GB. X1 reduces it once to the 235 SH3 genes
and then to the 310 domains, so that any downstream comparison starts from a verified table rather
than a fresh streaming pass.

**What it does not do.** It computes no comparison and returns no verdict. A program that uses these
predictors against ours needs a pre-registration first, and none exists.

## Inputs

| | |
|---|---|
| `dbNSFP5.4a.zip` | the academic release, 508 columns, ~2.1 M rows after gene filtering |
| `sh3_gene_names.txt` | the 235 gene symbols from the UniProt SH3 table |
| `SH3_cancer_master.tsv` | frozen atlas, for the domain boundaries |

## Method

1. Stream the release once, keeping the 235 SH3 gene symbols → `dbnsfp_sh3.tsv.gz`, 2,120,008 rows.
2. Restrict to positions inside an SH3 domain → `dbnsfp_sh3_domains.parquet`, **152,852 rows**,
   231 of 235 genes, 300 of 310 domains.
3. Compare each predictor's coverage against dbNSFP's own published figures.
4. Cross-check the in-domain ClinVar variants against the set X0 found independently.

152,852 is the expected magnitude: 300 domains × ~60 residues × ~9 reachable missense alleles.

## The four defects this program exists to not repeat

| # | Defect | How it showed |
|---|---|---|
| 1 | `cut -f` emits fields in **ascending file order**, whatever order they are listed; the header was written in a different order | AlphaMissense 2.5 %, CADD 0.0 %, `clinvar_id` 100 % |
| 2 | dbNSFP writes `.` for missing, not an empty field | every predictor showed 100 % coverage |
| 3 | pandas infers dtypes **per chunk**, so `#chr` was int64 in some and object in those with X/Y | `ArrowInvalid` on the parquet write |
| 4 | taking element `[0]` of a semicolon-separated **per-transcript** field | transcript-keyed predictors at half their published coverage |

**Defect 1 is the dangerous one.** It produced a complete, plausible, internally consistent file whose
every predictor column was mislabelled, and nothing inside the pipeline could have caught it. It was
caught by comparing coverage against the publisher's own figures — an external reference the reduction
does not control. The extraction now asserts that the header field count, the first data row's field
count and `len(KEEP)` all agree before the result is cached.

## The open question

**63.8 % of our in-domain ClinVar variants appear in dbNSFP's in-domain set** (2,377 of 3,725), and
that is unexplained. Two hypotheses were tested and refuted: the first-listed-value convention
(fixing it changed the cross-check not at all) and non-SNV records (3,717 of 3,725 keys have at least
one single-nucleotide record). The remaining candidate is the transcript axis.

**G1 supplies indirect evidence for it.** Building G1's null pool found that dbNSFP's transcript for a
given UniProt accession can be a different isoform: 31,458 of 132,704 accession-matched rows (23.7 %)
land on a position whose residue disagrees with the atlas, all-or-nothing per gene. That is the same
mechanism at a different scale, and it is why G1 keys on sequence agreement rather than on accession.

Until the ClinVar number is resolved, **dbNSFP's ClinVar column is not a valid cross-check on ours**,
and any follow-up must join on its own terms.

## Outputs

| | |
|---|---|
| `dbnsfp_sh3.tsv.gz` | 2,120,008 rows, 37 columns — **the input G1's null pool is built from** |
| `dbnsfp_sh3_domains.parquet` | 152,852 in-domain rows |
| `columns_X1.json`, `crosscheck_X1.json`, `dbnsfp_published_auc.csv` | provenance and the coverage comparison |

Both large files stay on Drive. Note that the in-domain parquet was filtered on the **first listed**
transcript's `aapos`, which is why G1 rebuilds its pool from the gene-level file instead.

## Practical notes

- **No tabix or CSI index ships with the release**, so a region query is impossible and the subset
  costs one full streaming pass. `dbNSFP5.4a_grch38.gz` *is* BGZF, so it could be indexed once.
- The popmax frequency is spelled `gnomAD4.1_joint_POPMAX_AF` in this release. Exact column matching
  only — a fuzzy matcher had been silently resolving it to the allele *count*.

## Runtime

One streaming pass, about 40 minutes on Colab. Cached thereafter.
