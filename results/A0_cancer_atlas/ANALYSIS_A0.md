# A0 — Analysis of the result: the SH3 cancer-variant atlas

**Colab run:** 2026-09-22, 14.3 min. **Verdict: REPRODUCED.**
The run's own numbers are in `RESULTS_A0.md`, `metrics_A0.json`, `comparison_A0.csv`, `qc_checks.csv` and
`build_stats.json`. The descriptive statistics in Sections 4–7 were computed from the atlas itself
(`SH3_cancer_master.tsv`, MD5 `cef897f4dd25f9cd56f2c40bb7ec0b08`). That atlas stays on Drive: it is derived
from COSMIC and is not committed.

---

## 1. Did A0 do its job?

A0 has one job: rebuild the atlas **from raw COSMIC**, and get exactly the atlas used in the original work.
It did.

| Check | Result |
|---|---|
| MD5 of the new atlas vs the original `SH3_cancer_master_v3.tsv` | **identical** (`cef897f4…`) |
| Recorded quantities (row counts at every filter, variants, domains, genes, flags) | **20 / 20 identical** |
| New quantities (no earlier value to compare) | `gsm_short_rows` = 0, hypermutated fraction = 0.1814 |
| Data-quality checks on every retained row | **8 / 8 passed** |
| Genome-screens file complete | 62,765,128 rows, 0 short rows |

**What this means.** Stage 0 is now fully reproducible: raw COSMIC v104 plus the frozen UniProt snapshot
give the same file, byte for byte. Everything after A0 therefore starts from the same data as the original
analysis. The thesis can say the atlas was built from raw data by code that is published, with a checksum.

**The earlier truncation risk is closed.** The old local `.tsv` copy of the genome screens was truncated
(1.35 of 16.8 GB). This run read the compressed `.tsv.gz` by streaming. It found no short rows and the
same number of samples as the recorded run (53,598). The file was complete.

---

## 2. Stage by stage: how 5.8 million rows become 6,884 variants

| Step | Rows left | What was removed, and why |
|---|---|---|
| COSMIC Cancer Mutation Census (CMC) | 5,802,907 | — |
| Missense mutations in genes that contain an SH3 domain | 91,842 | Other mutation types and genes without an SH3 domain |
| Inside an SH3 domain, canonical sequence, wild-type residue matches | 5,923 | Positions outside the domains |
| Recovered through an alternative isoform | +1,034 | Rows whose COSMIC position referred to another isoform. The wild-type residue matches that isoform's SH3 domain. |
| Rejected: the residue matches no sequence | 490 | Kept apart in `SH3_cancer_unmapped.tsv` |
| **Unique variants in the atlas** | **6,884** | Rows for the same protein change are merged into one variant |

**Reading it:**
- Only **about 7.5 %** of the missense rows in SH3-containing genes fall inside an SH3 domain. SH3 domains are short, about 60 residues; the median domain here is 62 (range 50–87), in proteins that are often 500–5,000 residues long.
- **The isoform step matters.** It adds 1,034 rows. In the atlas, 1,000 variants are placed *only* through an isoform, and 21 through both routes. Without the step, about **15 % of the atlas would be lost**. The loss would not be random: it would fall on genes whose COSMIC transcript is not the UniProt canonical one.
- **The wild-type check is strict.** 490 rows were rejected because the reported wild-type residue did not match the canonical sequence or any isoform. These are most likely annotation or transcript errors in COSMIC. They are not silently re-mapped. Most come from large, multi-isoform genes: SAMSN1 (38), SH3PXD2A (38), OBSCN (30), MYH15 (25), TNK2 (25), FYB1 (24). They are listed with reasons, so a reviewer can check them.

The search used 325 canonical SH3 windows and 518 isoform windows.

---

## 3. The eight data-quality checks

Each retained row was re-checked against its own sequence. All eight passed:
1. Every variant_id is unique.
2. The wild-type residue equals the domain sequence at that position.
3. The mutant domain sequence differs from the wild type at exactly one residue.
4. The position lies inside the domain.
5. Protein position = domain start + offset.
6. The domain length equals the length of the stored sequence.
7. The wild-type and mutant residues differ.
8. Only the 20 standard amino acids occur.

**Why this matters downstream.** A2 feeds `wt_domain_seq` and `mut_domain_seq` directly to ESM-2. Checks 2
and 3 guarantee the model sees exactly the substitution COSMIC reported, at the correct position.

---

## 4. What is in the atlas

| | |
|---|---|
| Variants | 6,884 |
| SH3 domains | 310 (median 23 variants per domain; the most is 49) |
| Genes | 235 (43 genes carry variants in more than one SH3 domain; DNMBP has 6) |
| Columns | 44 |

**The genes with the most variants** are not classic cancer genes. They are long, multi-SH3 scaffold
proteins:

| RIMBP2 | SORBS2 | SH3RF3 | SH3D19 | DNMBP | ITSN1 | NCK2 | TSPOAP1 | SORBS1 | ITSN2 |
|---|---|---|---|---|---|---|---|---|---|
| 131 | 104 | 103 | 99 | 98 | 94 | 86 | 83 | 76 | 76 |

This ranking follows **how many SH3 residues a gene has**, and how often it is sequenced in hypermutated
tumours, rather than selection. It is the first sign that raw counts cannot rank drivers here.

**Known cancer genes.** 686 variants (10 %) are in 27 genes listed in the Cancer Gene Census: 433 in tier 1,
253 in tier 2. The best known are VAV1 (60), BTK (42), PIK3R2 (35), ABL1 (35), SRC (29), ITK (27), RASA1 (27),
LCK (26) and PIK3R1 (24). The other 90 % are in genes with no cancer annotation. So the atlas mostly covers
**unexplored** SH3 biology, which suits a mechanism-first analysis.

---

## 5. Recurrence and hypermutation: is anything selected?

| Quantity | Value |
|---|---|
| Variants seen in only **1 sample** in CMC | 5,395 (78 %) |
| Recurrent (≥ 3 samples) | 501 (7.3 %) |
| Highest count for any single variant | 32 samples |
| Variants with sample-level records in the genome screens | 6,657 |
| … seen **only** in hypermutated tumours (> 1,000 mutations) | **4,492 (67 %)** |
| … seen in at least one non-hypermutated tumour | 2,165 |
| … in **≥ 3** non-hypermutated tumours | **84** |

**Tumour mutation burden, across 53,598 samples:** median 172 mutations; 95th percentile 6,075; 99th
percentile 16,293. 9,725 samples (18.1 %) are above the 1,000 threshold.

**Interpretation:**
- **Two thirds of the variants occur only in hypermutated tumours.** In those tumours thousands of mutations accumulate at random, so any single SH3 variant there is far more likely to be a passenger than a driver.
- **Once hypermutated tumours are removed, recurrence almost disappears.** Only 84 variants are seen three or more times. That is too few, and too spread across genes, for recurrence-based statistics to have power.
- **The most recurrent non-hypermutated variants** are ARHGAP9 R66C (26 samples), TRIO Q2579R (24), ASAP2 D978E (22), RIMBP2 F1013V (10) and CACNB4 A106T (10). These are candidates for follow-up. Recurrence alone does not make them drivers, and B5 tests them against a burial-matched null.
- **78 variants are flagged as likely germline.** They are kept but marked, so they can be excluded.

**The key negative result:** **0 variants** carry a COSMIC mutation-significance tier 1–3, and **0** a
significant dN/dS flag. By COSMIC's own recurrence and selection criteria, not one SH3 missense variant is a
recognised driver. **This is the motivation for the thesis.** If recurrence cannot say which SH3 variants
matter, the question must be answered from mechanism: does the substitution break the fold (Part B), or change
binding (Part C)?

---

## 6. Where, and by what process, the mutations arise

**Most frequent tumour sites.** The table counts variants that list each site among their top sites.

| skin | large intestine | lung | stomach | endometrium | haematopoietic/lymphoid | oesophagus | liver | CNS | breast |
|---|---|---|---|---|---|---|---|---|---|
| 1,418 | 1,109 | 908 | 559 | 543 | 346 | 337 | 312 | 307 | 272 |

**Substitution spectrum,** from 6,825 variants whose CDS change could be parsed:

| C>T | C>A | T>C | C>G | T>A | T>G |
|---|---|---|---|---|---|
| **46.8 %** | 20.8 % | 12.0 % | 9.6 % | 5.7 % | 5.2 % |

The most common protein changes are E>K (389), D>N (258), P>S (218), G>R (202), A>T (194), R>Q (188) and P>L
(167). All of them are C>T (G>A on the other strand) transitions.

**Interpretation.** The atlas is dominated by **mutational processes, not selection.** C>T transitions make up
almost half the spectrum. The top sites are skin (UV damage, a C>T signature), large intestine and
endometrium (often mismatch-repair deficient and hypermutated) and lung (tobacco, C>A — the second-largest
class). The hypermutation pattern agrees. Among variants whose most frequent site is:
- skin: 1,158 of 1,303 are seen only in hypermutated tumours;
- endometrium: 424 of 471;
- large intestine: 697 of 957.

This is why B5 compares cancer variants with a **burial-matched null**, not a uniform one. The mutation
processes do not hit all residues equally, so a naive test would confuse mutability with selection.

---

## 7. Other annotations (context only; not used by the models)

| Annotation | Value |
|---|---|
| SIFT predicts "deleterious" | 4,761 of 6,654 annotated (72 %) |
| ClinVar entry present | 190; mostly "uncertain significance". Only 4 are "likely pathogenic". |
| gnomAD exome frequency present | 1,544 variants; 66 have a frequency > 0.1 % |

SIFT calls most variants deleterious, so it does not separate them. ClinVar has almost nothing to say about
SH3 cancer variants. **Existing annotation does not answer the fold-or-binding question**, which the thesis
addresses directly.

---

## 8. Limitations

- **COSMIC-specific.** The atlas contains only variants reported in COSMIC v104 (GRCh38). Other databases, such as TCGA and GENIE, overlap with COSMIC but are not identical.
- **UniProt snapshot of 2026-09-20.** Domain boundaries come from UniProt, and UniProt revises them. The snapshot is frozen under MD5, so the result is reproducible, but a later release could move some domain edges.
- **490 rejected rows.** These may include some real variants whose COSMIC transcript is not in UniProt. They are not modelled.
- **Hypermutation threshold.** 1,000 mutations per sample, fixed in advance and not tuned. Another threshold would change the non-hypermutated counts, though not the atlas itself.
- **Counts reflect sequencing effort.** Genes and tumour types sequenced more often have more variants. The counts are not frequencies in patients.

---

## 9. Conclusion and next step

- **A0 reproduced Stage 0 exactly from raw data.** The whole pipeline now stands on a verified starting point.
- **The atlas holds 6,884 residue-verified variants in 310 SH3 domains.** Most are rare and arise in hypermutated tumours through UV, mismatch-repair and tobacco mutation processes.
- **COSMIC's own tools recognise none of them as drivers.**
- **So SH3 cancer variants cannot be interpreted by recurrence.** They need a mechanism-based prediction, which the rest of the pipeline builds.

**Next: A1 — the measured ground truth.** These are the experimental ΔΔG_fold and ΔΔG_bind values
(ddPCA/MoCHI, MegaScale) that the models in Parts B and C learn from and are tested against.
