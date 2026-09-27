# The data

Everything this phase reads. `input/` verifies **43 / 43** against
`reference/checksums_ext.md5` (8 of them against the publishers' own checksums).

```bash
cd extended && md5sum -c reference/checksums_ext.md5
```

---

## Layout

```
input/                                     5.1 GB
├── external/    new data for this phase
│   ├── domainome/     Human Domainome 1.0 — Zenodo v5, CC BY 4.0
│   │   ├── Supplementary_Table_{1,2,3,5}      tables + extracted members
│   │   ├── analysis_files/                    from files_to_reproduce_analyses.tar.gz
│   │   └── notebooks/                         the R Markdown that DEFINES those columns
│   ├── stability/
│   │   ├── mgnify/    MGnify Stability ΔG (2.1 GB) + the two training-split files
│   │   └── benchmarks/  ThermoMPNN & ProteinDPO predictions, S1724 ThermoMutDB
│   ├── clinical/      ClinVar variant_summary.txt.gz
│   ├── signatures/    COSMIC v3.6 SBS96 GRCh38
│   ├── genome/        GRCh38 primary assembly (882 MB) — for G1
│   └── binding/       Kazemein Jasemi 2024 + the extracted Kd and peptide tables — for E4
└── frozen/      read-only copies from the 2026-09-22 run (chmod a-w)
    ├── results/    atlas, B3 predictions, B1 held-out CIs, models.pt, F1 candidates,
    │               C4's collapsed PWM profiles + its CV table and decision (for E4)
    └── reference/  expected_values.json, checksums.md5, data_manifest.json
```

## Sources

| Dataset | Source | Licence | Used by |
|---|---|---|---|
| Human Domainome 1.0 | Zenodo **v5**, record 14356805 · doi:10.1038/s41586-024-08370-4 | CC BY 4.0 | E2 |
| MGnify Stability + SaProtΔG/ESM3ΔG | Cho et al. 2026 (bioRxiv, PMC13228446) · models on HF `Yehlin/absolute-stability` | MIT (code) | E3 |
| ClinVar | `ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz` | public domain | E1 |
| gnomAD v4 | the GraphQL API, 235 gene queries | open | E1, G1 |
| COSMIC SBS v3.6 | cancer.sanger.ac.uk/signatures | COSMIC terms | G1 |
| GRCh38 | Ensembl `current_fasta` primary assembly | open | G1 |
| SH3 affinities | Kazemein Jasemi et al. 2024, *Cells* 13(2):195 · doi:10.3390/cells13020195 | CC BY | E4 |
| dbNSFP 5.4a | registration; ~100 GB in two packagings on Drive at `input/dbNSFP/` | academic use | X1, then any E1 follow-up |
| The 12 original inputs | on Drive at `sh3_repro/input/` and on the DEU drive — **not duplicated here** | mixed; COSMIC restricted | G3, H1 only |

Cite Zenodo by the concept DOI `10.5281/zenodo.11043642`, which always resolves to the latest version.

### Use v5, not v3

The Domainome record has five versions. v3 predates the Nature paper; **v5 (10 Dec 2024) matches it**,
and the file names differ between them — a script written against v3 names will fail.

### dbNSFP arrived late, and is an addition

It was the convenience route to gnomAD and ClinVar in one file; both were taken from primary sources
instead, so nothing was blocked. Access came through on 27 Sep, after E1 and E4 had run. Its value is
the ~50 **pathogenicity** predictors it carries — not ΔΔG, so **not** an E3 competitor. Reduced to the
SH3 domains by `X1`. See [DATA_PROVENANCE.md](DATA_PROVENANCE.md) §9.

---

## Two traps

**The ΔΔG sign is inverted.** In `domainome/analysis_files/K50_dG_Dataset1_Dataset2_in_aPCA.csv`,
**negative = destabilising**. Our pipeline uses positive = destabilising, because the MegaScale
proteolysis sign is negated on load. Negate before comparing with anything from B1 or B3. This is the
same class of error as the FoldX residue-numbering bug.

**Four files have no header row.** The first line is data. Column meanings come from the R notebooks in
`domainome/notebooks/`, not from guessing. Decoded in
[`reference/domainome_column_map.md`](../reference/domainome_column_map.md), which also records the
MegaScale ↔ Domainome position mapping:

```
rocklin_pos = domainome_position − domain_start + 1 + offset
```

---

## Where each copy lives

| | local `extended/` | DEU drive | Drive |
|---|---|---|---|
| Working set (5.1 GB) | ✓ | ✓ | partly — see [SYNC.md](SYNC.md) |
| Full downloads (19 GB, incl. the 4 GB tarball, TED files, uncompressed ClinVar) | — | ✓ | — |
| 12 original inputs (7.5 GB) | — | ✓ | ✓ |
| SaProtΔG/ESM3ΔG checkpoints (221 MB) | — | ✓ verifies 12/12 | — |

Three independent copies of everything the analysis needs, each verified against a publisher's
checksum or a recorded local one.

## What is never committed

`atlas_with_external.csv` is `SH3_cancer_master.tsv` with extra columns — republishing the complete
atlas is republishing the atlas. Derived analysis tables (subsets with predictions and external
measurements, carrying no COSMIC identifiers, counts, sites or coordinates) **are** committed: they
are ordinary supplementary-material results. The large public exports (gnomAD 25 MB, ClinVar 17 MB,
Domainome 9 MB) stay out for size, not licence; X0 regenerates them.

**One exception under `input/`.** The two derived binding tables E4 reads — the Kd table and the
peptide table, together under 2 KB — *are* committed. Kazemein Jasemi et al. 2024 is CC BY, so
redistribution with attribution is permitted, and E4 cannot otherwise be reproduced from the repository
alone.
