# Data downloads for the extended study

Every link below was checked on 26 September 2026. Sizes are as reported by the host.
Anything marked **verify** is something I could not confirm from the public page and you must check
after downloading.

**Disk, checked 26 September 2026:**

| Mount | Type | Free | Use |
|---|---|---|---|
| `/` (includes `~`) | ext4 | **60 GB** | **put `input_new/` here** — native Linux, git works |
| `/mnt/E6CEDEF1CEDEB8CF` | NTFS | 55 GB | bulk overflow, acceptable |
| `/mnt/BA8EBF6B8EBF1EB7` ("DEU thesis") | NTFS | 19 GB | backup drive |
| `/mnt/1CD47885D47862C6` | NTFS | 78 GB | **Windows C: — do not use** |

Phase 1 needs roughly 10–15 GB in total, which fits on `/` comfortably, so nothing here has to be
streamed. **dbNSFP is the one exception:** ~50 GB nominally fits in 60 GB, but you need room for the
archive and the extracted per-chromosome files at once. For that one, filter per chromosome and delete
as you go, or use the online academic portal and download nothing.

Every file that survives filtering gets an MD5 in `reference/checksums_ext.md5`, exactly as A0 does for
the original inputs.

---

## Priority 1 — closes a publication blocker, costs nothing

### 1.1 Human Domainome 1.0 — external human stability measurements

| | |
|---|---|
| **What** | 500,000+ variants across 500+ **human** protein domains, measured by abundance selection (aPCA) |
| **Why** | The independent human calibration set `RECOMMENDATIONS.md` lists as "needs new data". Tests the 410 destabilising calls and the conformal exchangeability assumption (Limitation 3) without a wet lab. |
| **Paper** | Beltran A, et al. Site-saturation mutagenesis of 500 human protein domains. *Nature* 2025. doi:[10.1038/s41586-024-08370-4](https://doi.org/10.1038/s41586-024-08370-4) · PMID 39779847 · preprint [bioRxiv 2024.04.26.591310](https://www.biorxiv.org/content/10.1101/2024.04.26.591310v1) |
| **Data** | Zenodo **v5** (10 December 2024) — record [14356805](https://zenodo.org/records/14356805), doi:`10.5281/zenodo.14356805` |
| **Cite** | the concept DOI [10.5281/zenodo.11043642](https://doi.org/10.5281/zenodo.11043642), which always resolves to the latest version |
| **Licence** | CC BY 4.0 — redistributable with attribution |
| **Login** | none |

**Use v5, not v3.** The record has five versions. v3 (June 2024, doi 10.5281/zenodo.11493742) predates the
Nature paper; **v5 is the version closest to it** (10 December 2024 against publication on 8 January 2025).
v5's stated change is "Figure and Supplementary Table name changes", so the file names differ from v3 —
and the tables are now zipped, which makes them four times smaller.

Files on v5:

| File | Size | Take it? |
|---|---|---|
| `Supplementary_Table_2_fitness_scores_normalized_domainranks.txt.zip` | 29.3 MB | **yes — this is the one you need** (121.9 MB in v3, and it now carries domain ranks) |
| `Supplementary_Table_1_library_design.txt` | 792 B | library-design summary only; **it does not name any domains** |
| `Supplementary_Table_5_aPCA_vs_variant_effect_predictors.txt.zip` | 40.5 MB | yes — EVE, popEVE and Tranception scores for the same variants, i.e. free baselines |
| `Supplementary_Table_3_esm1v_residuals.txt` | 3.2 MB | optional |
| `Supplementary_Table_4_homolog_predictions.txt.zip` | 20.3 MB | skip unless you do the homolog analysis |
| `files_to_reproduce_analyses.tar.gz` | 4.1 GB | skip |

Note the v3 file was `Supplementary_Table_1_librarydesign.txt`; in v5 it is `..._library_design.txt`. Same
792 bytes, same content.

**The E2 gate.** Supplementary Table 1 was checked on 26 September 2026 and it is only a library-design
summary — 1,248 domains attempted, 522 retained, 563,534 variants, broken down by amino-acid size range.
**It names no domains, so it does not settle whether SH3 is included.** What it does show is that the
SH3 size band is well covered: libraries D5, D6 and D7 span 46–70 residues and retained 177 domains
between them.

Settle it from Supplementary Table 2 instead (29.3 MB zipped in v5). Match on **UniProt accession, not
gene symbol** — gene symbols collide. The 235 accessions from the atlas are in
`reference/sh3_genes_uniprot.tsv`. If the identifiers turn out to be Pfam-based, search for `PF00018`
(SH3_1).

Three outcomes: several SH3 domains → E2 runs as written; one or two → keep it as a spot check, not a
validation; none → drop E2, keep the Domainome as a general out-of-distribution check on small human
domains, and E1 carries the whole external-validation load.

Note the observable is **abundance**, not ΔΔG in kcal/mol. B4 already showed your head is beaten by
ESM-2 on abundance assays, so expect a weaker correlation and interpret it as a rank test, not a
calibration in energy units. The paper reports 60 % of pathogenic missense variants reduce stability —
a published figure to compare your own rate against.

---

### 1.2 MGnify Stability dataset + SaProtΔG / ESM3ΔG — the state-of-the-art baseline

| | |
|---|---|
| **What** | Folding stability for 1.8 million domains of 60–80 residues from >200,000 sequence families, by cDNA display proteolysis; plus two predictors reaching Spearman 0.88 / 0.87 and RMSE 0.80 kcal/mol |
| **Why** | Fixes the biggest reviewer objection: you currently beat only zero-shot ESM-2, FoldX and EVE. This is the current top of the field, trained on the same assay family as your training data, in exactly the 60–80 residue window where SH3 sits. |
| **Paper** | Cho Y, et al. Accurate protein stability prediction for small domains using mega-scale experiments. bioRxiv, 20 May 2026. [PMC13228446](https://pmc.ncbi.nlm.nih.gov/articles/PMC13228446/) — **preprint, not peer reviewed; cite it as one** |
| **Dataset** | Access request form: https://forms.gle/4ZnXZSnTBvaykkAi9 — file `230515_K50dG_dmsv4_dmsv5_dmsv7_concat260429.csv` |
| **Models** | GitHub https://github.com/yehlincho/absolute-stability-predictor · weights https://huggingface.co/Yehlin/absolute-stability |
| **Licence** | **verify** on the repo and the form response |
| **Login** | Google Form for the data; none for the models |

**Confirmed: the dataset contains SH3 domains** (CATH superfamily 2.30.30.40, their Figure 5d). That
matters twice over — it is a source of extra SH3 training data, and it is a leakage risk for the
benchmark.

You need this for two separate jobs, and the second is not optional:

1. **Benchmark.** Run SaProtΔG and ESM3ΔG on your 15 held-out SH3 domains and report their ρ beside
   your 0.839.
2. **Leakage audit.** Their training set spans 200,000 families and includes SH3. Check every one of
   your 15 held-out domains against their training sequences before you report a single comparison
   number. If they trained on your test domains, the comparison is meaningless and you must say so.

The model weights alone (a few GB) may be enough — download the full dataset only if you do the audit
properly or want the extra training data.

---

### 1.3 dbNSFP v5.4a — gnomAD + ClinVar + baseline predictors in one file

| | |
|---|---|
| **What** | Every possible human missense SNV pre-annotated with gnomAD v4.1 and v2.1.1 allele frequencies, ClinVar significance, and dozens of predictor scores, keyed by transcript and protein position |
| **Why** | One download replaces three. Gives you the germline arm (gnomAD), external pathogenicity labels (ClinVar) and a shelf of baseline predictors, all already mapped to protein positions — which is exactly how your atlas is keyed. |
| **Home** | https://www.dbnsfp.org/ · releases https://www.dbnsfp.org/releases/ |
| **Version** | v5.4a academic (August 2026 release, GENCODE 50 / Ensembl 116; 86.7 M nsSNVs) |
| **Size** | ~50 GB — **more than your free disk** |
| **Licence** | CC BY-NC-ND 4.0, academic branch, non-commercial |
| **Login** | Register with an **institutional email** (use your university address), receive an access code, then request download links |

Three ways to use it, in order of preference given your disk:

1. **Academic Portal** — query.genos.us with the same access code, no download at all. Best first move:
   check coverage for a handful of SH3 genes before committing 50 GB anywhere.
2. **Colab + Drive** — download per-chromosome files into Colab, filter to the 235 genes, delete.
3. **Skip it** and use the two primary sources separately (1.4 and 1.5). More work, no licence
   restriction.

---

### 1.4 ClinVar — external pathogenicity labels (fallback to 1.3)

| | |
|---|---|
| **File** | https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz |
| **Size** | ~450 MB compressed |
| **Licence** | public domain, US Government work |
| **Login** | none |
| **Why** | "*N* of *M* ClinVar pathogenic missense variants in human SH3 domains are called confidently destabilising; *k* of *n* benign are not." Validation with no bench work. |

Filter to the 235 genes on download; the filtered table will be a few hundred kilobytes.

---

### 1.5 gnomAD — the germline arm (fallback to 1.3)

| | |
|---|---|
| **Home** | https://gnomad.broadinstitute.org/downloads |
| **Why** | The strongest independent attack on the B6 confound. Adds a third arm to the depletion comparison: mutational background / germline-tolerated / somatic cancer. Discriminates selection from mutational bias **without** depending on the signature model being right. |
| **Licence** | free, open |
| **Login** | none |

The full sites VCFs are enormous. For 235 genes, prefer the **GraphQL API** per gene over any bulk
download, or take the frequencies from dbNSFP (1.3) where they are already joined to protein positions.
Check the current release version on the page — **verify**.

---

## Priority 2 — needed for specific recommendations

### 2.1 COSMIC mutational signatures (SBS)

| | |
|---|---|
| **Home** | https://cancer.sanger.ac.uk/signatures/ · downloads https://cancer.sanger.ac.uk/signatures/downloads/ |
| **Why** | Recommendation #2: the signature-aware null for B5/B6. Without it the 5.9 % vs 9.2 % depletion cannot be called selection rather than mutational bias. |
| **Login** | **not** required, but COSMIC terms and conditions still apply |
| **Also needed** | GRCh38 reference FASTA, to extract trinucleotide contexts for your variants. You already have GRCh38 coordinates in the atlas. |

### 2.2 AACR Project GENIE

| | |
|---|---|
| **Release** | 20.0-public, July 2026 — >289,000 samples from >242,000 patients |
| **Access** | Synapse https://www.synapse.org/genie (syn7222066) · or via https://genie.synapse.org/Access · also browsable in cBioPortal |
| **Why** | Power for B5, where only 17 genes are currently testable in non-hypermutated tumours |
| **Login** | Synapse account + agreement to terms |

**Caution before you spend time here.** GENIE is panel sequencing: different centres use different gene
panels, so a gene's apparent mutation count depends on how often it was *on a panel*. That is an
ascertainment bias that lands directly on a positional enrichment test. Handle it with per-panel
denominators or leave GENIE out. This is the one Priority 2 item that can make results worse if done
carelessly.

---

## Priority 3 — small, specific, cheap

### 3.1 Independent SH3 binding measurements

Kazemein Jasemi NS, et al. Functional Classification and Interaction Selectivity Landscape of the Human
SH3 Domain Superfamily. *Cells* 2024;13(2):195. doi:[10.3390/cells13020195](https://doi.org/10.3390/cells13020195) ·
open access at https://www.mdpi.com/2073-4409/13/2/195 · [PMC10814857](https://pmc.ncbi.nlm.nih.gov/articles/PMC10814857/)

45 measured interacting pairs, affinities 0.2–125 µM, across 25 SH3 domains against SOS1 proline-rich
peptides, out of 300 tested. Small, but **independent and multi-domain** — and C4 is currently validated
only against the PWM data it came from. Tables are in the MDPI supplementary material; free download.

### 3.2 Context for the discussion, not data

- Jordan DF, et al. Residues neighboring an SH3-binding motif participate in the interaction in vivo.
  *Genetics* 2025;231(2). doi:[10.1093/genetics/iyaf153](https://doi.org/10.1093/genetics/iyaf153) ·
  PMID 40758840. Deep mutational scanning on the **motif** side (Pbs2 × Sho1 SH3, yeast). Not domain-side,
  so it does not fix C1/C2 — but it reports that residues outside the canonical motif modulate binding,
  which is a mechanistic reason your PWM collapse in C4 may have failed.
- Delalande F, et al. Holdup Multiplex, *J. Am. Chem. Soc.* 2025. Thousands of affinity constants per
  mass-spec run; already demonstrated on a PDZ domain against 5,400 peptides. This is the **method** that
  could generate the multi-domain SH3 binding dataset the whole project says is missing. Name it when you
  approach a collaborator. Look up the DOI before citing — **verify**.
- Chu SKS, et al. Protein stability prediction by fine-tuning a protein language model on a mega-scale
  dataset (ESMtherm). *PLOS Computational Biology* 2024. A second benchmark baseline; the repository is
  linked from the paper — **verify** the URL there rather than guessing it.

---

## What you already have and should not download again

`Processed_K50_dG_datasets.zip` (MegaScale), `Data.zip` (ddPCA/MoCHI, FoldX, EVE), ProteinGym,
`SH3_PWM.zip`, the UniProt snapshot and the three COSMIC files. They stay where they are. The extended
study imports the frozen atlas and the trained head from the original run as **fixed inputs** and never
rebuilds them.

---

## Order of downloading

1. ~~Supplementary Table 1~~ — done, and it does not answer the question. Take **Supplementary Table 2
   from Zenodo v5** (29.3 MB) instead and match UniProt accessions against
   `reference/sh3_genes_uniprot.tsv`.
2. dbNSFP registration (the access code takes a while to arrive — start it early, use it via the portal first)
3. ClinVar `variant_summary.txt.gz`
4. MGnify form request + the model weights from Hugging Face
5. COSMIC SBS signatures
6. Everything else only if the plan still calls for it after 1–5
