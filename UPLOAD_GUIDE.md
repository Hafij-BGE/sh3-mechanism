# Upload guide — what goes where on Google Drive

Everything runs from one new Drive folder, **`MyDrive/sh3_repro/`**. It does not read
`sh3_thesis/` or `sh3_fresh/`.

## 1. Create these folders on Drive

```
MyDrive/sh3_repro/
├── code/
├── input/
│   ├── cosmic/
│   ├── uniprot/
│   └── datasets/
└── reference/
```

`results/` and `cache/` are created by the notebooks themselves. Do not make them.

## 2. Upload these files

Paths on the left are on your laptop, relative to `~/Documents/thesis/`.

| # | Laptop file | Drive folder | Size |
|---|---|---|---|
| 1 | `<cancer/claude/cmc_export.tsv` | `input/cosmic/` | 1.9 GB |
| 2 | `<cancer/Cosmic_GenomeScreensMutant_Tsv_v104_GRCh38/Cosmic_GenomeScreensMutant_v104_GRCh38.tsv.gz` | `input/cosmic/` | 4.5 GB |
| 3 | `<cancer/claude/Cosmic_Classification_v104_GRCh38.tsv` | `input/cosmic/` | 0.9 MB |
| 4 | `sh3/phase1_domain_atlas/sh3_domains_human.tsv` | `input/uniprot/` | 33 KB |
| 5 | `sh3/phase1_domain_atlas/sh3_proteins_seq.tsv` | `input/uniprot/` | 271 KB |
| 6 | `sh3/phase1_domain_atlas/scripts/isoforms_all.json` | `input/uniprot/` | 777 KB |
| 7 | `sh3/new stage 1 data/Processed_K50_dG_datasets.zip` | `input/datasets/` | 1.0 GB |
| 8 | `sh3/new stage 1 data/Data.zip` | `input/datasets/` | 575 MB |
| 9 | `sh3/new stage 1 data/DMS_ProteinGym_substitutions.zip` | `input/datasets/` | 43 MB |
| 10 | `sh3/new stage 1 data/DMS_substitutions.csv` | `input/datasets/` | 209 KB |
| 11 | `sh3/new stage 1 data/SH3_PWM.zip` | `input/datasets/` | 189 KB |
| 12 | `sh3/HumanSH3TableS2.xlsx` | `input/datasets/` | 64 KB |
| 13 | `sh3 updated/reference/expected_values.json` | `reference/` | small |
| 14 | `sh3 updated/reference/checksums.md5` | `reference/` | small |
| 15 | `sh3 updated/reference/data_manifest.json` | `reference/` | small |
| 16 | `sh3 updated/src/sh3_common.py`, `sh3_atlas.py`, `run_tests.py` | `code/` | small |
| 17 | `sh3 updated/notebooks/*.ipynb` (all 14) | `code/` | small |

**Shortcut for items 13–17:** drag the two folders in `sh3 updated/drive_upload/` (`code/` and `reference/`)
into `MyDrive/sh3_repro/`.

**About 8.1 GB in total.** The two big COSMIC files are the slow part; start them first.

**Take care with these:**
- **File 2** must be the `.tsv.gz` from the `Cosmic_GenomeScreensMutant_Tsv_v104_GRCh38` folder.
  The `.tsv` copy in `<cancer/claude/` is **truncated** (1.35 of 16.8 GB) and will be rejected.
- **The atlas itself (`SH3_cancer_master_v3.tsv`) is not uploaded.** A0 derives it from the raw COSMIC files and checks
  the result against the atlas's recorded MD5.
- Do not rename anything. Every input is checked by MD5 against `reference/checksums.md5`, and
  a wrong or incomplete file stops the notebook with a message saying which one.

**Short of Drive space?** Once this run has finished, you can delete
`MyDrive/sh3_fresh/input/`: it holds copies of files 7–10.

## 3. Run the notebooks, in this order

Open each one from `MyDrive/sh3_repro/code/` in Colab. For the GPU notebooks, first choose
Runtime → Change runtime type → **T4 GPU**. Every notebook ends by writing
`results/<its folder>/RESULTS_<ID>.md`.

| Order | Notebook | Runtime | Time |
|---|---|---|---|
| 1 | `A0_cancer_atlas` | CPU | 10–25 min |
| 2 | `A1_ground_truth` | CPU | ~10 min |
| 3 | `A2_features` | **T4** | ~25 min (first run) |
| 4 | `B1_folding_model` | **T4** | ~25 min |
| 5 | `B2_structural_check` | CPU | 1 min |
| 6 | `C1_binding_cross_domain` | **T4** | ~3 min |
| 7 | `C2_binding_within_domain` | **T4** | ~15 min |
| 8 | `C3_binding_data_sufficiency` | **T4** | 30–45 min |
| 9 | `B3_uncertainty_and_calls` | CPU | 1 min |
| 10 | `C4_specificity_axis` | **T4** | ~10 min |
| 11 | `B4_external_validation` | **T4** | ~15 min |
| 12 | `B5_cancer_biology` | CPU | ~3 min |
| 13 | `B6_virtual_saturation_mutagenesis` | CPU | ~5 min |
| 14 | `D1_figures_and_verification` | CPU | 1 min |

About **3.5 hours** in total. If Colab disconnects, run the same notebook again: with
`RESUME = True` it skips the steps already saved.

## 4. Bring the results back

Download `MyDrive/sh3_repro/results/` into `~/Documents/thesis/sh3 updated/results/`,
then commit it to GitHub (see `GITHUB_GUIDE.md`). The `.gitignore` there keeps the large and
COSMIC-derived files out automatically.
