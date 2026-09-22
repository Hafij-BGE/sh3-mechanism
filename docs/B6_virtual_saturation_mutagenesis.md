# B6 — Virtual saturation mutagenesis (roadmap L3/L4, G4)

**Purpose.**
- Produce a predicted deep mutational scan of every atlas SH3 domain: all 19 substitutions at every
  position, about 350,000 variants, each with a conformal interval.
- Use it to see where observed cancer mutations sit.

**Why it is cheap.** Embeddings and log-odds are stored per domain (A2), so every virtual variant's
features are a lookup. No new ESM pass is needed.

## Checks built in
- **Consistency:** the 6,884 observed variants must receive exactly the B1 prediction (maximum
  difference < 10⁻⁴), or the notebook stops.

## Analyses
1. **Family map:** mean predicted damage and destabilising fraction at each of the 56 aligned
   positions, with burial and interface flags.
2. **Observed vs possible:** the destabilising fraction among all substitutions, among the
   **single-nucleotide-reachable** ones (derived from the genetic code), and among observed cancer
   variants.
3. **Domain-matched test:** are observed variants depleted of damage relative to random reachable
   substitutions in the same domains?
   - *Depletion* would suggest purifying selection.
   - *Enrichment* would suggest positive selection.

## Limitations
- The actual codons, codon usage and trinucleotide context are not modelled, so this is **not** a
  mutational-opportunity null (roadmap G1).
- Predictions inherit B1's regime limits: domain-scale, sequence-only.

## Outputs
`sh3_virtual_dms.parquet` (stays on Drive), `family_position_map.csv`, `domain_summary.csv`.
