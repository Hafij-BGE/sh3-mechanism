# A0 — The SH3 cancer-variant atlas (Stage 0)

**Purpose.** Collect every somatic missense mutation that falls inside a human SH3 domain, place
it on the right residue, and annotate the tumours it was seen in.

## Inputs
- **COSMIC v104:** `cmc_export.tsv` (Cancer Mutation Census, 5.8 M rows), the genome-screens file
  (62.8 M per-sample rows, read compressed), and the phenotype classification.
- **UniProt snapshot of 2026-09-20:** 325 SH3 domains in 244 reviewed human proteins, their
  canonical sequences, and all 745 isoform sequences. It is frozen because a live query could return
  a different release and silently change the atlas.

## Steps, and why each is there
1. **MD5 check of every input.** The project once used a genome-screens copy that had stopped at 1.35
   of 16.8 GB. With it, tumour-type coverage fell from 96.7 % to 13.3 %, and nothing crashed.
2. **Domain windows.** Each SH3 domain is located on the canonical sequence and, by exact string
   match, on every alternative isoform.
3. **Residue check.** A missense row is kept only if its position lies inside a domain window
   **and** COSMIC's wild-type residue equals the residue actually there. Position numbers alone are
   not trusted.
4. **Isoform recovery.** COSMIC numbers some mutations on alternative transcripts. Those rows are
   mapped through the isoform and re-expressed in canonical coordinates. This recovers 1,034 rows
   (+17 %).
5. **Per-sample annotation.** The genome screens give each variant its samples, tumour sites and
   histologies. A sample with more than 1,000 mutations is called **hypermutated** (18.1 % of samples).
6. **Data-quality report** (roadmap A1/A2): every retained row is re-verified (residue identity,
   one-residue difference, coordinates, lengths), and rejected rows are listed with their reason.
7. **Byte comparison** with the original atlas.

## Outputs
`SH3_cancer_master.tsv` (6,884 × 44), `SH3_cancer_unmapped.tsv` (490 rejected rows),
`qc_checks.csv`, `build_stats.json`, `RESULTS_A0.md`.

## How to read the result
- **Main result: the atlas is byte-identical to the original.**
- **No variant has a COSMIC significance tier or a dN/dS flag, and only 84 recur in 3 or more
  non-hypermutated samples.** Recurrence-based driver detection cannot see this family, so the
  thesis evaluates mechanism, not driver status.
- **65 % of variants occur only in hypermutated tumours.** The atlas is dominated by passengers, and
  B5 has to be read with that in mind.

## Limitations
- The hypermutation threshold (1,000 mutations) is a choice.
- COSMIC over-represents sequenced tumour types.
- The COSMIC licence forbids redistribution, so the atlas never goes to GitHub.
