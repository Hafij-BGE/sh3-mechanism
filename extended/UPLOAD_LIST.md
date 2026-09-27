# Upload list — local → Drive `SH3_extended`

Compared 2026-09-27, after the X0 run of 2026-09-26 23:27.

Drive already holds what X0 downloaded for itself. Everything below exists **only locally** and is
needed on Drive before the next programs can run in Colab.

**Total to upload: ~3.5 GB.** One item (`analysis_files`, 1.2 GB) and one (`mgnify`, 2.3 GB) dominate.

---

## Priority 1 — blocks E2 and E3 (3.5 GB)

| Upload to | File | Size | Needed by |
|---|---|---|---|
| `input_new/domainome/analysis_files/` | `K50_dG_Dataset1_Dataset2_in_aPCA.csv` | 71 MB | **E2** — the only route from aPCA fitness to kcal/mol, so the conformal coverage test |
| | `megascale_uniprot_mappings_offsets.tsv` | 5 KB | **E3** — maps the 15 held-out domains to PDB names |
| | `domains_from_tsuboyama_rocklin_overlaps.txt` | 5 KB | **E2** — the 7 SH3 domains in both datasets |
| | `gnomad_v4_variants_domainome.txt` | 415 MB | optional: cross-check against X0's own gnomAD pull |
| | `domainome_structural_annotation.txt` | 734 MB | optional: burial, comparable to B2 |
| `input_new/domainome/notebooks/` | `02_validation.Rmd`, `11_…mochi.Rmd`, `12_…mochi.Rmd` | 39 KB | **decodes the headerless columns** — do not skip |
| `input_new/stability/mgnify/` | `230515_K50dG_…concat260429.csv` | 2.1 GB | **E3** leakage audit + extra SH3 training data |
| | `mgnify_training_index.csv` | 131 MB | **E3** leakage audit |
| | `dmsv4_filtered_train_splits.csv` | 57 MB | **E3** leakage audit |
| | `README.md` | 3 KB | column definitions |
| `input_new/stability/benchmarks/` | `fig3__megascale_point_mutants_predictions.csv` | 7.3 MB | ThermoMPNN + ProteinDPO baselines |
| | `S1724_thermomutdb_cleaned_withseq.csv`, `S1724_PDB_sequences.csv` | 1 MB | external ΔΔG benchmark |
| `input_new/signatures/` *(create)* | `COSMIC_v3.6_SBS_GRCh38.txt` + the zip | 0.4 MB | **G1** |

If bandwidth is tight, the four marked optional (`gnomad_v4_variants_domainome`,
`domainome_structural_annotation`) can wait — they total 1.1 GB and nothing in E2/E3 needs them.
That cuts the upload to **2.4 GB**.

## Priority 2 — code and documentation (small)

| Upload to | File |
|---|---|
| `reference/` | `domainome_column_map.md`, `checksums_ext.md5` |
| `code/` | `tools/nb_X.py`, `tools/e2_domainome_validation.py` |
| `code/` or root | `PLAN.md`, `DOWNLOADS.md`, `README.md`, `input_new/README.md` |
| `results/E2_domainome_external/` | `per_domain_E2.csv`, `matched_variants_E2.csv` |

## Priority 3 — only if E3 runs in Colab

`absolute-stability-predictor/` (221 MB, 12 LoRA checkpoints). **Don't upload** — the repo's
`download_weights.sh` refetches them in Colab in under a minute, and the MD5s are in
`checksums_ext.md5`.

---

## Already on Drive, do not re-upload

`input_new/domainome/`: Tables 1, 2 (zip + extracted), 5 (zip + extracted) ·
`input_new/clinical/`: `variant_summary.txt.gz`, `gnomad_cache.json` ·
`reference/`: `sh3_genes_uniprot.tsv`, `checksums_X0.md5`, `data_manifest_X0.csv` ·
`code/X0_acquire_external_data.ipynb` · all five X0 output CSVs.

**Missing on Drive but trivial:** `Supplementary_Table_3_esm1v_residuals.txt` (3 MB) — X0 doesn't
fetch it and nothing currently uses it.

## Two things to clean up on Drive

- **`input_new/domainome/__MACOSX/`** — junk from the zip extraction. Delete.
- **`input_new/clinical/gnomad_cache.json` is 219 MB.** That is the raw API cache, already distilled
  into `gnomad_sh3_missense.csv` (25 MB). Keep it while X0 might be rerun; delete it afterwards.

---

## Suggested upload method

Uploading 2.3 GB through the Drive web UI is slow and fails silently on large files. Prefer:

```bash
rclone copy "input_new/stability" "drive:SH3_extended/input_new/stability" -P
```

or, if rclone isn't set up, upload the two big files individually through the web UI and watch each
one complete. After uploading, verify from a Colab cell:

```python
!cd "/content/drive/MyDrive/SH3_extended" && md5sum -c reference/checksums_ext.md5
```

The paths in `checksums_ext.md5` are relative to the project root, so they resolve on Drive exactly
as they do locally.
