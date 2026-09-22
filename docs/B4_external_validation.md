# B4 — External validation (ProteinGym)

**Purpose.** Find where the predictor stops working.

## Blocks (defined before the run)
| Block | Assays | What it tests |
|---|---|---|
| primary | 3 | External stability assays: the real test |
| secondary | 15 | Expression/abundance: a related phenotype, not ΔΔG |
| sanity | 10 | Tsuboyama assays, i.e. the training distribution: a wiring check |

**Exclusions.** An assay is excluded from primary and secondary if its `DMS_id` is a Tsuboyama assay
**or** its UniProt accession appears in training. ProteinGym's stability category has become largely
one mega-experiment. Without this exclusion, a MegaScale-trained model would be scored on its own
training data, and most published comparisons do not make the exclusion.

**Scoring.** Full-length proteins are scored through a 128-residue window centred on the mutation.
The ESM baseline is the same in-window score, which is fairer than a leaderboard number.

## Expected result, and how to say it
- **Primary:** head 0.361 vs ESM 0.406 (head wins 2/3).
- **Secondary:** 0.400 vs 0.491 (wins 6/15).
- **Sanity:** 0.940 vs 0.580 (wins 10/10).
- **Transfer:** the head falls 2.3–3.5× as far as ESM from its internal performance.
- **Claim:** a domain-scale predictor validated within its regime. **Not a general stability
  predictor.** The length table rules out the window as the explanation.
