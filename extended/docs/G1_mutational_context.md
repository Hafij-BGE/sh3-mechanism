# G1 — A trinucleotide-aware null for the cancer depletion

**Why it is needed.** The frozen run reported that observed SH3 cancer variants are depleted of
predicted fold-breaking substitutions — 5.93 % against 9.18 % expected, p ≤ 0.001 — and B6 stated the
limitation itself: *"mutational context was not modelled, and a trinucleotide-aware null is needed
before claiming selection."* This was the last of the four standing objections and the only frozen
claim with no independent support.

**What it does not do.** It re-fits nothing and re-runs nothing in the frozen phase. It changes the
**null**, not the model. `fold_lo ≥ 1` is still the call, exactly as B3 defined it.

**Pre-registered** in `preregistration/G1.md`, committed before the notebooks existed, signed off in
Part 13. The notebook reads that file at run time to set its own α, so the threshold could not be
chosen after a p-value existed.

## Inputs

| | |
|---|---|
| `sh3_virtual_dms.parquet` (B6, 22 Sep) | 366,168 predictions, never re-fitted |
| `atlas_grch38_coordinates.tsv` | 6,456 of 6,884 atlas variants with a verified GRCh38 coordinate |
| `dbnsfp_sh3.tsv.gz` (X1, gene-level) | the source of every possible in-domain missense SNV |
| `Homo_sapiens.GRCh38...fa.gz` | Ensembl, 881,964,081 bytes, asserted |
| `COSMIC_v3.6_SBS_GRCh38.txt` | SBS96 reference profiles |

## Method

1. **Coordinates.** The atlas records `c.196C>T` and a protein position, not a genomic coordinate.
   `tools/g1_coordinates.py` recovers one by joining to dbNSFP on gene, residue and substitution:
   6,456 resolve uniquely, and **all 6,456 carry the expected GRCh38 reference base**.
2. **Null pool.** Every in-domain missense base change whose reference residue agrees with the
   atlas's own sequence — 154,708 base changes over 115,742 substitutions.
3. **Context.** One streaming pass over GRCh38 gives each a 96-channel trinucleotide class.
4. **Draws.** 10,000 domain-matched draws per arm, weighted by the spectrum.

## The arms

| | draws from | role |
|---|---|---|
| reproduction | B6's own reachable set | **must return 0.09232** — proves our reading of B6 |
| 3a | codon-reachable substitutions | corrected uniform baseline |
| 3b | codon-reachable base changes | + reachability multiplicity |
| 1 / 2 | spectrum-weighted base changes | + trinucleotide context — **the verdict** |

Two notebooks, `G1a_observed_spectrum` and `G1b_cosmic_spectrum`, differ in **exactly one code cell**.
Everything else is `tools/g1_core.py`, embedded byte-for-byte and hash-asserted, so any difference in
the result is attributable to the spectrum rather than to an implementation slip.

## Expected outcome, stated in advance

Three outcomes were fixed before any number existed: *survives* (gap ≥ 1.63 pp and p < α),
*shrinks but survives*, and *vanishes* → **the frozen claim is withdrawn**.

No primary spectrum was named, so both arms ran co-primary at α = 0.0125 (Bonferroni, family-wise
0.025). Deferring cost 0.70 → 0.81 pp of minimum detectable gap, charged in advance.

## What it found

**The depletion vanishes. Both spectra agree.**

| arm | null | observed | gap | p |
|---|---|---|---|---|
| observed spectrum | 0.0604 | 0.0596 | +0.08 pp | 0.401 |
| COSMIC SBS1+SBS5 | 0.0558 | 0.0596 | −0.39 pp | 0.918 |

| step | null | change | p |
|---|---|---|---|
| B6, amino-acid-pair reachability | 0.0923 | — | 0.001 |
| codon reachability | 0.0860 | −0.64 pp | 0.0001 |
| + reachability multiplicity | 0.0788 | −0.71 pp | 0.0001 |
| **+ trinucleotide context** | **0.0604** | **−1.84 pp** | **0.401** |

**The depletion survives both reachability corrections at p = 0.0001; context alone removes it.** The
result is the test B6 asked for, not a pile of bookkeeping fixes.

It is not an underpowered null: the Monte-Carlo SD came in at 0.00295 against a pre-registered
binomial estimate of 0.00296, so the test resolves 0.66 pp and the residual is 0.08 pp.

## Two corrections to B6's null, which stand on their own

1. **`snv_reachable` is amino-acid-level.** It asks whether a substitution is reachable from *some*
   codon of the wild-type residue, not from the codon present. Across 150 amino-acid pairs the
   fraction attainable from the codon present matches the genetic-code prediction at **r = +0.955**,
   and the excluded substitutions are more damaging (0.112 vs 0.086) — inflating the expected rate by
   0.60 pp.
2. **Reachability multiplicity.** One substitution can be reached by several base changes with
   different contexts; drawing at the amino-acid level treats them as one.

## Outputs

| | |
|---|---|
| `metrics_G1a.json`, `metrics_G1b.json`, `RESULTS_G1a/b.md` | machine-written |
| `RESULTS_G1_comparison.md` | `tools/g1_compare.py` — the deliverable |
| `ANALYSIS_G1.md` | the interpretation |
| `atlas_grch38_coordinates.tsv` | **laptop only** — per-variant coordinates |

## Runtime

Minutes on CPU; no GPU anywhere. `tools/g1_run.py` runs both arms locally end to end, which is how
they were verified: two machines and two dbNSFP releases agreeing to every digit.

## Open caveat

9,668 of 164,376 pool base changes (5.9 %) did not join to B6. The join guarantees gene, position and
wild-type residue by construction, so the drop can only come from `mut_aa` not being a standard
residue — dbNSFP's `X` for stop-gain and readthrough, which is not missense. **That is a deduction
from the code, not a measurement**; `build_context` now records it, and Part 13 commits to amending
the sign-off if it is anything else.
