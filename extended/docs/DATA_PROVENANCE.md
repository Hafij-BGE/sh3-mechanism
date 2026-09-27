# How each dataset was actually obtained

Written as it happened, 26–27 September 2026, including the routes that failed. A reader who wants to
rebuild `input/` from nothing should be able to follow this. `docs/DATA.md` says *what* the data is;
this says *how it got here*.

Every file has a checksum in `reference/checksums_ext.md5` (43 entries; 8 checked against a
publisher's own published value, the rest recorded locally).

---

## 1. Human Domainome 1.0 — Zenodo, direct, verified

**First attempt used the wrong version.** The record has five. v3 (`11493742`, June 2024) was
downloaded first, but the Nature paper appeared in January 2025 and **v5 (`14356805`, 10 December
2024) is the version that matches it**. v5 also renames the files and zips the tables, so a script
written against v3 names fails.

```
https://zenodo.org/records/14356805/files/<name>?download=1
```

Taken: Supplementary Tables 1, 2, 3, 5 (+ the extracted members) and
`files_to_reproduce_analyses.tar.gz` (3.9 GB). MD5s match the values Zenodo publishes.

Cite by the concept DOI `10.5281/zenodo.11043642`, which always resolves to the latest version.

**The 4 GB archive was not unpacked.** It is a macOS-made tarball with the author's own path seven
levels deep and `._` resource-fork files throughout. Only eight files matter, extracted selectively:

```bash
tar xzf files_to_reproduce_analyses.tar.gz --strip-components=7 --wildcards \
    '*/analysis_files/K50_dG_Dataset1_Dataset2_in_aPCA.csv' \
    '*/analysis_files/megascale_uniprot_mappings_offsets.tsv' \
    '*/analysis_files/domains_from_tsuboyama_rocklin_overlaps.txt' \
    '*/analysis_files/gnomad_v4_variants_domainome.txt' \
    '*/analysis_files/domainome_structural_annotation.txt' \
    '*/02_validation.Rmd' '*/11_prepare_data_for_homolog_mochi.Rmd' \
    '*/12_evaluate_mochi_models.Rmd'
```

**The `.Rmd` files are data, not decoration.** Four of the extracted tables have no header row, and
the R notebooks are the only definition of their columns — including that the ΔΔG sign is the
opposite of ours. Decoded in `reference/domainome_column_map.md`.

**Finding the SH3 domains.** Supplementary Table 1 was checked first, on the assumption it listed the
500 domains. It does not — it is a library-design summary by size range, and names nothing. The
answer is in Table 2's `domain_ID`, which is `UNIPROT_PFAM_index`: filtering on `PF00018`, `PF07653`
and `PF14604` gives **45 SH3 domains**.

## 2. MGnify Stability — request form

The dataset is gated behind a Google Form (`https://forms.gle/4ZnXZSnTBvaykkAi9`); the access page
then lists Zenodo-hosted files with published MD5s.

Taken: `230515_K50dG_dmsv4_dmsv5_dmsv7_concat260429.csv` (2.1 GB, the ΔG measurements),
`mgnify_training_index.csv`, `dmsv4_filtered_train_splits.csv`, `README.md`, plus `benchmarks.zip`
and `figures.zip`. All four core MD5s verified.

`figures.zip` was initially dismissed as "figures". It is not — it contains
`fig3__megascale_point_mutants_predictions.csv`, which carries **ThermoMPNN and ProteinDPO**
predictions alongside the two ΔG models. Two extra baselines for E3, free.

## 3. SaProtΔG / ESM3ΔG checkpoints — GitHub script

```bash
git clone https://github.com/yehlincho/absolute-stability-predictor    # @ c55db530
bash download_weights.sh                                               # needs huggingface_hub
```

Pulls 12 LoRA checkpoints (213 MB) from `Yehlin/absolute-stability`: two models × base/augmented ×
3 seeds. All 12 verify against `reference/checksums_models.md5`.

Two things the README does not make obvious: inference takes a **structure file plus a chain ID**, not
a sequence, and `examples/` includes AlphaFold `.cif` models — so the `.cif` files A2 already fetches
are valid input. `ddg_scanning=True` returns a full saturation scan from one structure.

## 4. ClinVar — direct FTP, no login

```
https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz
```

450 MB, public domain. 9,224,097 records; **140,572 are GRCh38 records in the 235 SH3 genes**, of
which 74,116 have a parseable protein change.

NCBI reissues this monthly and publishes no stable checksum, so the MD5 in
`reference/checksums_ext.md5` is *recorded, not verified*. **Note the retrieval date** —
`0ef1c60048748efe12ea3120ecc848ce`, fetched 26 September 2026.

Chunked pandas took minutes; `pyarrow.csv.open_csv` streaming scans the whole file in **11 seconds**.

## 5. gnomAD v4 — the API, not the VCFs

The exome sites VCFs total about 200 GB, for 310 domains of ~60 residues. gnomAD's own documentation
recommends the API at this scale, so X0 issues 235 GraphQL queries against
`https://gnomad.broadinstitute.org/api`, giving **431,959 missense variants**.

**This went wrong first.** Eight concurrent workers triggered `HTTP 429 Too Many Requests`, and the
failure path cached the result as `[]` — indistinguishable from "this gene has no variants". Two
genes (ARHGEF4, DLG4) were silently skipped and would never have been retried. ARHGEF4 in fact has
8,140 variants. Fixed by: never caching a failure, 60 s × attempt backoff honouring `Retry-After`,
**three** workers rather than eight, and purging empty entries on startup.

## 6. COSMIC mutational signatures — web form, terms apply

`https://cancer.sanger.ac.uk/signatures/downloads/` → Release v3.6, Variant Class SBS, Context Size
96, file `COSMIC_v3.6_SBS_GRCh38`. No login, but COSMIC's terms apply. 96 context rows × 101
signature columns.

This gives the *reference profiles* only. Per-tumour signature activities are not here; G1 should
start from the observed trinucleotide spectrum of our own variants, with decomposition as the
interpretation layer.

## 7. GRCh38 reference genome — Ensembl, direct

```
https://ftp.ensembl.org/pub/current_fasta/homo_sapiens/dna/Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz
```

881,964,081 bytes, gzip verified. Ensembl chromosome naming (`1`, `2`, `X`) matches COSMIC, so no
renaming is needed. Needed by G1 to read trinucleotide contexts.

## 8. SH3 binding affinities — three routes, two blocked

Kazemein Jasemi et al. 2024, *Cells* 13(2):195, doi:10.3390/cells13020195.

| Route | Result |
|---|---|
| `https://www.mdpi.com/article/10.3390/cells13020195/s1` | **blocked** — Akamai returns a 412-byte "Access Denied" page |
| `https://pmc.ncbi.nlm.nih.gov/articles/instance/10814857/bin/cells-13-00195-s001.zip` | **blocked** — 1.8 KB of HTML |
| `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10814857/supplementaryFiles` | **worked** — 9.5 MB zip |

A browser session passes the MDPI bot check where `curl` does not; downloading it that way afterwards
gave a **byte-identical** PDF (`5ddcaebd…`, 9,530,126 bytes), confirming Europe PMC serves the same
file. Both the publisher zip and the PDF are kept.

**The data is inside a PDF.** Table S6 holds the dissociation constants as a 25 × 12 grid. It is
text-based, so `pypdf` extracts it, and a parser turns it into
`kazemein_jasemi_2024_TableS6_Kd.csv`:

> **45 measured interactions, 17 SH3 domains, Kd 0.2–125 µM**

Both the count and the range match the paper exactly, which is the check that the parse is right.

**Table S2 gives the peptide sequences**, which E4 needs and the Kd table does not carry — it names
peptides `P1`–`P10`, `RP1`, `RP2` only. Extracted from the same PDF with `pdftotext -layout` and a
one-line regex, into `kazemein_jasemi_2024_TableS2_peptides.csv`:

```
P3   1146EVPVPPPVPPRRRPESAPAESSPSKI1171
```

Each row carries the residue coordinates, so the parse checks itself: `end − start + 1` must equal the
sequence length, and it does for all twelve. That check also surfaces a fact the analysis has to
handle — **RP1 (1147–1158) is a sub-sequence of P3 (1146–1171)**, so those two measurements are not
independent.

Ten peptides are SOS1-derived; RP1 and RP2 are the paper's reference peptides. Nine of the twelve carry
at least one Kd.

**These two CSVs are the only files under `input/` that are committed to git.** The paper is CC BY,
which permits redistribution with attribution, and without them E4 cannot be reproduced from the
repository alone. Everything else under `input/` stays out, for size or licence.

## 9. dbNSFP — arrived 27 September 2026, after it had been written off

Registration requires an institutional email and a returned access code. It had not come through when
§4 and §5 were written, so ClinVar and gnomAD were taken from primary sources and **nothing was ever
blocked**. The access then came through the same day E4 finished. This is an *addition*, not a repair,
and the earlier route stays exactly as it was — the primary-source extraction is what X0 verified and
what E1 ran on.

Four files, on Drive at `input/dbNSFP/`:

| File | Bytes | What it is |
|---|---|---|
| `dbNSFP5.4a.zip` | 51,053,386,192 | the release archive |
| `dbNSFP5.4a_grch38.gz` | 55,386,634,577 | the same release, second packaging |
| `dbNSFP5.4_gene.gz` | 24,069,120 | per-gene annotation and constraint |
| `dbnsfp_performance_matrix.csv` | 127,915 | **dbNSFP's own ClinVar benchmark of every score it ships** |

**The two large files are ~100 GB together and are believed to hold the same release twice.** That is
not assumed: X1 §1 probes both cheaply — a zip central directory, and the first 64 KB of the gz — and
reports which is usable and whether one can be deleted, *before* anything reads 50 GB. **No tabix or
CSI index ships with the release**, so a region query is impossible and the subset is built by one
streaming pass filtered on the 235 gene names. The pass is cached, so it is paid once.

**What dbNSFP is, precisely.** About 50 precomputed **pathogenicity** predictors per missense variant —
AlphaMissense, REVEL, MetaRNN, ESM1b, CADD and the rest — plus its own copies of ClinVar and gnomAD.
It does **not** predict ΔΔG. So it is **not** a competitor for E3, which benchmarks stability
predictors; putting a pathogenicity score in that table would be a category error. It is the external
comparison for **E1**, whose question was whether our stability calls track pathogenicity.

The performance matrix is worth reading before any such comparison is designed. On all genes, ClinVar
2026, star 1+ missense, the best scores reach **AUC 0.94–0.99** (MetaRNN 0.988, REVEL 0.976,
AlphaMissense 0.964). E1 put our stability head at rank-biserial +0.615, which is AUC ≈ 0.81. The
useful question is therefore not whether we win — we should not, and we are not trying to — but
**whether ΔΔG_fold carries anything those predictors do not**.

X1 (`notebooks/X1_dbnsfp_subset.ipynb`) does the acquisition and reduction only. It computes no
comparison and returns no verdict, because that needs a pre-registration written first.

## 10. The 12 original inputs — not re-obtained

COSMIC, UniProt, MegaScale, ddPCA/MoCHI, ProteinGym and the PWM data, 7.5 GB. They belong to the
frozen run and already sit on Drive at `sh3_repro/input/` and on the DEU thesis drive, where they
verify 12/12 against the original project's `reference/checksums.md5`. They are **not** duplicated
into `extended/`; only G3 and H1 need them. See `../docs/DATA_ACCESS.md`.

---

## Two rules learned the hard way

**A derived table is not a database download.** COSMIC's licence restricts redistributing their data.
An analysis table carrying protein positions, model predictions and external measurements — with no
COSMIC identifiers, counts, tumour sites or coordinates — is ordinary supplementary material. Only
`atlas_with_external.csv`, which is the complete atlas with extra columns, stays out of git.

**Verify against the publisher, not against yourself.** Recording an MD5 of what you downloaded proves
only that the file has not rotted since. Where the host publishes a checksum — Zenodo and MGnify do —
compare against *theirs*. That is the difference between detecting corruption and detecting the wrong
file. `reference/checksums_ext.md5` marks which is which.
