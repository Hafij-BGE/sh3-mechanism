# B5 — Analysis of the result: cancer biology

**Colab run:** 2026-09-22, 0.7 min on CPU. **Verdict: REPRODUCED** — 15 of 15 values identical.
The run's own numbers are in `RESULTS_B5.md`, `metrics_B5.json` and `comparison_B5.csv`. The tables include
`gene_enrichment.csv` and the site and positional tables.

---

## 1. The question

B3 labelled 410 cancer variants (5.96 % of the atlas) as confidently destabilising. B5 asks whether this has
biological meaning in cancer:

> Are destabilising variants **concentrated** in particular genes, tumour types or positions, **more than
> expected by chance**? That would hint at selection for loss of fold.

**Why the null is burial-matched.** Buried positions are both more often destabilising (B2) and differently
exposed to mutation. A naive null (random variants) would find "enrichment" simply because some groups have
more buried variants. Each group is therefore compared with **2,000 random samples of the atlas matched on
burial**. Multiple testing is corrected with Benjamini–Hochberg (significant if q < 0.1). Everything is run on
all variants and, separately, on variants seen in non-hypermutated tumours.

---

## 2. Overall rate

| Set | Variants | Destabilising |
|---|---|---|
| All atlas variants | 6,884 | **5.96 %** |
| Seen in non-hypermutated tumours | 2,165 | **5.59 %** |

**The rate is not higher outside hypermutated tumours.** If loss of fold were selected in cancer, variants
from non-hypermutated tumours (fewer passengers) should be *more* often destabilising. They are slightly less.
Variants from hypermutated and non-hypermutated tumours look alike on this axis.

---

## 3. Enrichment tests

| Test | Groups tested | Significant (q < 0.1) | Smallest q |
|---|---|---|---|
| Genes, all variants (≥ 20 variants) | 170 | **1** | 0.085 |
| Genes, non-hypermutated only (≥ 20) | 17 | **0** | 0.314 |
| Tumour primary sites (≥ 30) | 22 | **0** | 0.484 |

**The one significant gene: SPTA1** (erythroid α-spectrin). 49 variants, 18.4 % destabilising against 4.1 %
expected, p = 0.0005, q = 0.085.
- **p = 0.0005 is the smallest value 2,000 permutations can give** (1/2,001). The true p could be smaller, but not measurably with this run.
- **q = 0.085 is just under the 0.1 threshold.** It is a single borderline hit among 170 genes tested.
- **It is not supported by the non-hypermutated test:** no gene is significant there (0 of 17 tested).
- **Biologically, SPTA1 is known mainly as a red-cell cytoskeleton protein** (erythroid α-spectrin). The hit is best reported as a **single candidate, not a finding.**
- **The next genes** (SH3GL2, SH3RF2: q 0.31) are far from significant.

**Tumour sites: 0 of 22 enriched.** Liver has the largest excess (8.0 % vs 5.1 % expected, p = 0.022), but
q = 0.48 after correction. At the other end, large intestine and urinary tract show *fewer* destabilising
variants than expected. None of this survives correction.

---

## 4. Does predicted damage explain where cancer variants fall?

Across the 56 aligned SH3 positions:

| Correlation | ρ |
|---|---|
| Number of cancer variants vs predicted fold damage | **−0.009** |
| Predicted fold damage vs burial | +0.712 (B2) |
| Number of cancer variants vs burial | −0.178 |
| Uniformity of positions (test against equal counts) | p = 0.0002, not uniform |

**Interpretation:**
- **Cancer variants are not concentrated where damage is predicted** (ρ about 0). Positions whose mutation breaks the fold do not collect more cancer variants. That is what selection for loss of fold would produce, and it is absent.
- **Variants are unevenly spread over positions** (p = 0.0002), and somewhat less frequent at buried positions (ρ −0.18). But the null for this test assumes every position is equally mutable. It ignores trinucleotide context and codon composition, which A0 showed dominate the atlas (C>T, UV, mismatch repair). **This is read as a mutational-process pattern, not a selection signal.**

---

## 5. What this means for the thesis

- **Across genes, tumour sites and positions, there is no robust sign that cancer selects for loss of SH3 fold.** There is one borderline gene hit (SPTA1), and no tumour site passes correction.
- **This is consistent with A0:** SH3 cancer variants are mostly rare passengers, many from hypermutated tumours, and COSMIC flags none as a driver.
- **The atlas is therefore a *mechanism map*, not a *driver list*.** It says, for each variant, whether it is likely to break the fold (410 confidently). It does not say that those variants drive cancer. For a specific gene or patient, the fold call is a mechanistic hypothesis to test, not evidence of pathogenicity.
- **No binding claims are made** (`binding_claims_made = False`), in line with Part C.

---

## 6. Limitations

- **Power:** only 17 genes have ≥ 20 non-hypermutated variants. A real but modest enrichment could be missed.
- **The null matches burial but not mutational context** (trinucleotide, codon), so positional non-uniformity cannot be interpreted as selection.
- **2,000 permutations** limit p to ≥ 0.0005.
- **Destabilising calls are conservative** (B3). Enrichment of *weaker* destabilisation is not tested here.
- **COSMIC counts reflect sequencing effort** (A0), not true frequencies in patients.

---

## 7. Conclusion and next step

- **Cancer biology is null:** 1 of 170 genes (SPTA1, borderline q = 0.085) and 0 of 22 tumour sites enriched against a burial-matched null.
- **Cancer variant counts do not follow predicted damage** (ρ −0.009).
- **The atlas is a mechanism map, not a driver list.**

**Next:** run `B6_virtual_saturation_mutagenesis` on CPU (about 5 min), then `D1_figures_and_verification`.
