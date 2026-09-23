# Data access — what git holds, and how to get the inputs

The repository holds **code, documentation and small result files**. It does **not** hold the input data.
COSMIC's licence forbids redistributing their files, the archives are far larger than GitHub's 100 MB limit,
and per-variant COSMIC-derived tables are blocked by `.gitignore` for the same reason.

What git does hold is everything needed to **obtain and verify** the same inputs:

| In the repository | What it gives you |
|---|---|
| `reference/checksums.md5` | the MD5 of every input file, exactly as the pipeline expects it |
| `reference/data_manifest.json` | for each file: source, size, MD5, licence note, and which program uses it |
| `reference/expected_values.json` | 187 recorded result values, so a fresh run can be checked against the original |
| the notebooks | each one verifies its inputs by MD5 before using them and stops if a file is wrong |

So the data are not *in* git, but the repository pins exactly *which* data a result came from.

---

## 1. The inputs, and where each comes from

| File | Size | Source | Access |
|---|---|---|---|
| `cmc_export.tsv` | 1.9 GB | COSMIC Cancer Mutation Census v104 (GRCh38) | cancer.sanger.ac.uk, personal academic licence and login |
| `Cosmic_GenomeScreensMutant_v104_GRCh38.tsv.gz` | 4.5 GB | COSMIC Genome Screens Mutant v104 | same; keep it compressed, the pipeline streams it |
| `Cosmic_Classification_v104_GRCh38.tsv` | 0.9 MB | COSMIC Classification v104 | same |
| `sh3_domains_human.tsv`, `sh3_proteins_seq.tsv`, `isoforms_all.json` | 1.1 MB | UniProt snapshot of 20 September 2026 | uniprot.org; the pipeline uses the frozen copies, not a live query |
| `Processed_K50_dG_datasets.zip` | 1.0 GB | Mega-scale folding stabilities (Tsuboyama et al. 2023) | public, distributed with the paper (Zenodo record 7992926) |
| `Data.zip` | 575 MB | ddPCA/MoCHI energies, structures, FoldX and EVE baselines (Faure et al. 2022) | public, distributed with the paper |
| `DMS_ProteinGym_substitutions.zip`, `DMS_substitutions.csv` | 43 MB | ProteinGym v1.3 substitution benchmarks | public, proteingym.org |
| `SH3_PWM.zip`, `HumanSH3TableS2.xlsx` | 253 KB | Human SH3 specificity profiles (Teyra et al. 2017) | public, journal supplementary data |

Only the three COSMIC files require a licence. Everything else is public.

---

## 2. Getting a working copy

**If you have access to the project's Drive folder** (the usual case for this thesis), everything is already
in place:

```
MyDrive/sh3_repro/
├── input/{cosmic,uniprot,datasets}/     the 12 files above
├── code/                               notebooks + src (from this repository)
├── reference/                          from this repository
└── results/                            written by the runs
```

Open a notebook from `code/` in Colab and run it. Nothing else is needed.

**If you are starting from the repository alone:**

1. Clone it:
   ```bash
   git clone git@github.com:hafijbd/sh3-mechanism.git
   ```
2. Obtain the 12 input files from the sources in Section 1. The COSMIC ones need your own licence.
3. Put them in a Drive folder with the layout above (`input/cosmic/`, `input/uniprot/`, `input/datasets/`).
4. Copy `notebooks/*.ipynb` and `src/*.py` into `code/`, and `reference/` into `reference/`.
5. Run A0 first. It verifies every file by MD5 and refuses to continue if one does not match.

---

## 3. Verifying a copy

From a folder laid out like the Drive one (`input/...` next to `reference/`):

```bash
md5sum -c reference/checksums.md5
```

Each line prints `OK` or `FAILED`. A failure means the file is incomplete or a different release — the
pipeline would stop on it anyway. One entry, `reference/SH3_cancer_master_v3.tsv`, is the original cancer
atlas; it is optional, because A0 rebuilds it from raw COSMIC and checks the MD5 itself.

---

## 4. If you ever need the data itself under version control

Not recommended here, but for completeness:

- **Git LFS** stores large files outside the repository with pointers in git. It does not solve the COSMIC licence problem, and the free quota is 1 GB.
- **DVC or git-annex** keep hashes in git and the data in external storage (Drive, S3). This is the closest fit if the project grows, and it is compatible with a licence, because only hashes are shared.
- **Zenodo or a similar archive** is the right place for *derived, redistributable* outputs, for example the virtual saturation mutagenesis table, provided the licence of the source data allows it. COSMIC-derived per-variant tables do not qualify.

The current arrangement — hashes and a manifest in git, data on Drive — is the same pattern, done manually.

---

## 5. Rule of thumb

> If a file contains COSMIC records, or is larger than a few megabytes, it belongs on Drive and is named in
> `reference/`. Everything else belongs in git.

`.gitignore` enforces this: `*.tsv`, `*.gz`, `*.zip`, `*.xlsx`, `*.parquet`, `*.npz`, `*.pt`, `*.cif`,
`database/`, `cache/`, the media files and `results/F1_experimental_candidates/experimental_candidates.csv`.
