# B6 — Virtual saturation mutagenesis

*Generated automatically by the notebook on 2026-09-22T15:18:54 (1.9 min). Every number below comes from this run; nothing is typed by hand.*

## Summary

- 366,168 virtual substitutions predicted across 310 SH3 domains; the observed variants reproduce B1 exactly (max difference 9.5e-07).
- 12.1% of all possible substitutions are called destabilising (9.2% of single-nucleotide-reachable ones) against 6.0% of observed cancer variants.
- Domain-matched: observed 5.93% vs expected 9.18% (p depleted = 0.001).
- A citable resource: a predicted folding landscape for every human SH3 domain in the atlas, with intervals.

**Check against the recorded run: no recorded values to compare** ()

## Observed cancer variants against every possible substitution

Destabilising = lower 90% interval bound ≥ 1 kcal/mol.

| set | variants | frac_destabilising | median_pred |
|---|---|---|---|
| all possible substitutions | 366168 | 0.1210 | 0.7716 |
| single-nucleotide-reachable only | 150040 | 0.0923 | 0.6543 |
| observed in cancer | 6884 | 0.0596 | 0.5459 |

## Domain-matched test

Observed single-nucleotide-reachable variants: 5.93% destabilising; random reachable substitutions from the same domains: median 9.18% (1,000 draws); one-sided p that observed variants are depleted of damage = 0.000999. Depletion would be the signature of purifying selection; enrichment of positive selection. Codon usage and trinucleotide context are not modelled.

## Family map: the 15 most damage-sensitive aligned positions

| ref_pos | domains | mean_pred | frac_destabilising | observed_variants | rsasa | buried | interface |
|---|---|---|---|---|---|---|---|
| 19.000 | 304 | 2.519 | 0.525 | 63 | 0.060 | True | False |
| 25.000 | 307 | 2.347 | 0.489 | 74 | 0.000 | True | False |
| 47.000 | 309 | 2.311 | 0.506 | 88 | 0.000 | True | False |
| 5.000 | 310 | 2.230 | 0.428 | 127 | 0.060 | True | False |
| 27.000 | 308 | 2.151 | 0.440 | 96 | 0.110 | True | False |
| 38.000 | 310 | 1.978 | 0.282 | 146 | 0.020 | True | False |
| 9.000 | 310 | 1.951 | 0.314 | 85 | 0.130 | True | True |
| 17.000 | 307 | 1.939 | 0.390 | 49 | 0.030 | True | False |
| 45.000 | 309 | 1.915 | 0.218 | 123 | 0.120 | True | False |
| 36.000 | 310 | 1.915 | 0.333 | 83 | 0.160 | True | False |
| 22.000 | 306 | 1.879 | 0.250 | 155 | 0.340 | False | False |
| 52.000 | 303 | 1.837 | 0.291 | 107 | 0.020 | True | False |
| 51.000 | 304 | 1.780 | 0.200 | 78 | 0.350 | False | True |
| 3.000 | 309 | 1.734 | 0.250 | 101 | 0.000 | True | False |
| 35.000 | 310 | 1.624 | 0.149 | 85 | 0.400 | False | True |

## All quantities and their check

| quantity | this_run | recorded | status |
|---|---|---|---|
| virtual_variants | 3.662e+05 |  |  |
| domains | 310 |  |  |
| max_diff_vs_observed | 9.537e-07 |  |  |
| frac_destabilising_all_possible | 0.121 |  |  |
| frac_destabilising_reachable | 0.09232 |  |  |
| frac_destabilising_observed | 0.05956 |  |  |
| frac_destabilising_observed_reachable | 0.05929 |  |  |
| matched_null_median | 0.09177 |  |  |
| p_observed_depleted | 0.000999 |  |  |
| rho_family_damage_vs_burial | 0.7753 |  |  |

## Environment

| python | numpy | pandas | scipy | sklearn | transformers | Bio | torch | gpu |
|---|---|---|---|---|---|---|---|---|
| 3.13.15 | 2.1.3 | 2.2.3 | 1.16.3 | 1.6.1 | 5.16.1 | 1.88 | 2.11.0+cpu | none |
