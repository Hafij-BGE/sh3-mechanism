# B5 — Cancer biology

**Purpose.** Ask whether predicted destabilisation explains where cancer mutations fall.

## Controls
- **Burial-matched permutation null** (2,000 draws). Each gene or site is compared only with random
  atlas variants that have the same buried / surface / unknown composition. A more buried domain
  shows more predicted damage for trivial reasons.
- **Multiple testing:** Benjamini–Hochberg; significance at q < 0.1.
- **Hypermutation:** every test is run on all variants and on non-hypermutated variants only.
- **Positional test:** the 56 aligned positions against a uniform null. It does **not** model
  trinucleotide context or codon-level mutational opportunity (roadmap G1).

## Expected result
| Test | Result |
|---|---|
| Genes enriched | 1 / 170 (all), 0 / 17 (non-hypermutated) |
| Tumour sites enriched | 0 / 22 |
| ρ(variant count, predicted damage) | −0.009 |
| ρ(predicted damage, burial) | +0.712 |
| Positional non-uniformity | p = 2 × 10⁻⁴ |

## How to say it
- **The biology is null, and the controls make the null interpretable.**
- **One gene at q < 0.1 in 170 tests is what BH allows from noise.** It is not named as a finding.
- **The positional non-uniformity is unrelated to damage**, so it is a mutational-process
  observation, not a selection signal.
- **The atlas is a mechanism map, not a driver list.**
