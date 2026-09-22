# A0 — Cancer-variant atlas from raw COSMIC

*Generated automatically by the notebook on 2026-09-22T11:38:04 (14.3 min). Every number below comes from this run; nothing is typed by hand.*

## Summary

- 6,884 residue-verified missense variants in 310 SH3 domains of 235 genes.
- 1,034 COSMIC rows recovered through alternative isoforms; 490 rejected.
- 2,165 variants are seen outside hypermutated tumours; only 84 of them in 3 or more such samples.
- No variant carries a COSMIC significance tier 1-3 or a dN/dS flag - recurrence-based driver detection cannot see this domain family.
- Byte-identical to the original atlas: True.

**Check against the recorded run: REPRODUCED** (20 identical)

## Data-quality report

Every retained row re-verified against its own sequence.

| check | passed |
|---|---|
| variant_id unique | True |
| wild-type residue matches domain sequence | True |
| mutant sequence differs at one residue | True |
| position inside the domain | True |
| protein position = domain start + offset | True |
| domain length = sequence length | True |
| wild-type differs from mutant | True |
| standard amino acids only | True |

## How the variants were mapped

| route | COSMIC rows |
|---|---|
| canonical sequence | 5923 |
| recovered via an isoform | 1034 |
| rejected: residue mismatch on every sequence | 490 |

## Rejected rows, by gene (top 10)

Full list: `SH3_cancer_unmapped.tsv`.

| gene | rejected rows |
|---|---|
| SAMSN1 | 38 |
| SH3PXD2A | 38 |
| OBSCN | 30 |
| MYH15 | 25 |
| TNK2 | 25 |
| FYB1 | 24 |
| ARHGAP27 | 23 |
| MAPK8IP2 | 22 |
| SORBS2 | 22 |
| DLG2 | 22 |

## Hypermutation

A sample with more than 1,000 mutations in the genome screens is called hypermutated: 9,725 of 53,598 samples (18.1%); median burden 172.

## All quantities and their check

| quantity | this_run | recorded | status |
|---|---|---|---|
| cmc_rows | 5802907 | 5802907 | identical |
| missense_rows_in_sh3_genes | 91842 | 91842 | identical |
| mapped_canonical | 5923 | 5923 | identical |
| mapped_isoform | 1034 | 1034 | identical |
| unmapped | 490 | 490 | identical |
| variants | 6884 | 6884 | identical |
| columns | 44 | 44 | identical |
| domains | 310 | 310 | identical |
| genes | 235 | 235 | identical |
| gsm_rows | 62765128 | 62765128 | identical |
| gsm_short_rows | 0 |  |  |
| gsm_samples | 53598 | 53598 | identical |
| hypermutated_fraction | 0.1814 |  |  |
| with_sample_records | 6657 | 6657 | identical |
| nonhyper_variants | 2165 | 2165 | identical |
| recurrent_nonhyper | 84 | 84 | identical |
| hypermutated_only | 4492 | 4492 | identical |
| recurrent_any | 501 | 501 | identical |
| likely_germline | 78 | 78 | identical |
| significance_tier_1_3 | 0 | 0 | identical |
| dnds_flagged | 0 | 0 | identical |
| master_md5 | cef897f4dd25f9cd56f2c40bb7ec0b08 | cef897f4dd25f9cd56f2c40bb7ec0b08 | identical |

## Environment

| python | numpy | pandas | scipy | sklearn | transformers | torch | gpu |
|---|---|---|---|---|---|---|---|
| 3.13.15 | 2.1.3 | 2.2.3 | 1.16.3 | 1.6.1 | 5.16.1 | 2.11.0+cpu | none |
