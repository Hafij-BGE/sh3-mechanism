# Keeping local and Drive in step

Local root: `sh3 updated/extended/` · Drive root: `MyDrive/sh3_repro/extended/`

The two are one folder each, mirroring the single GitHub repository. Colab reads Drive; the frozen
run sits beside it at `MyDrive/sh3_repro/`, which every old notebook hardcodes — **do not rename it.**

---

## Outstanding: upload to Drive

Checked 27 September 2026, after E1.

| Upload | into | Size |
|---|---|---|
| `notebooks/E1_clinvar_gnomad.ipynb` — **patched after the run**, re-upload and re-run | `code/` | 20 KB |
| `input/README.md` — **local copy was refreshed**, Drive's is now the stale one | `input/` | 3 KB |
| `input/external/binding/` — the whole folder | `input/external/` | 18 MB |
| `input/external/genome/Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz` | `input/external/genome/` | **842 MB** |
| `reference/checksums_ext.md5` — **Drive's copy is stale**, 35 entries against 43 | `reference/` | 4 KB |
| `results/E1_clinvar_gnomad/ANALYSIS_E1.md` | same path | small |
| `results/E4_specificity_independent/ANALYSIS_E4.md` | same path | small |
| `notebooks/E3_sota_benchmark.ipynb` — new, ready to run | `code/` | 28 KB |
| `results/E2_domainome_external/` — everything but `per_domain_E2.csv` and `matched_variants_E2.csv` | same path | small |
| `notebooks/E2_domainome_external.ipynb`, `tools/*.py` | `code/` | small |
| `docs/` — the whole folder, `preregistration/` included; Drive's `docs/` is empty | `docs/` | small |
| `README.md` | root | small |

Everything but the genome is under 20 MB, and the genome is needed only by G1, so it can wait.

E3 creates `input/external/structures/` on Drive itself (22 PDB entries, ~2 MB) and caches every
saturation scan under `results/E3_sota_benchmark/cache/`. Neither needs uploading; both are worth
leaving in place, because the cache is what makes a timed-out E3 session resumable.

Use **New → Folder upload** for whole folders — it preserves the tree and is far less error-prone
than file-by-file. Close any document open in OnlyOffice first, or its `.~lock.*#` file rides along.

`input/frozen/results/` gained three C4 artefacts (`pwm_profiles.csv`, `specificity_cv.csv`,
`specificity_decision.json`) so E4 runs from the bundle as well as from the frozen run. Drive already
serves them at `sh3_repro/results/C4_specificity_axis/`, so **they do not need uploading** — E4 prefers
the frozen run and falls back to the bundle.

**Downloaded from Drive instead:** E1 and E2 run in Colab and write to Drive, so
`results/E1_clinvar_gnomad/{RESULTS_E1.md,summary_E1.csv,metrics_E1.json}` and all five of
`results/E4_specificity_independent/` came the other way and are now in git. `input/README.md` was lost locally during the input redistribution and was recovered the
same way — the Drive copy matched its recorded MD5 exactly, which is what the manifest is for.

## Then verify

In a Colab cell (two lines — `%cd` is notebook magic and does not work in a shell):

```python
%cd /content/drive/MyDrive/sh3_repro/extended
!md5sum -c reference/checksums_ext.md5
```

Expect **43 OK**. Drive's web uploader truncates large files silently often enough that this is worth
running after every bulk upload.

If it reports failures on the model checkpoints, you used the wrong file — those live in
`reference/checksums_models.md5` and are absent from Drive by design.

---

## Already in sync

`input/external/{domainome,stability,clinical,signatures}` · the two binding CSVs ·
`input/frozen/` · the E4 notebook ·
`results/E1_clinvar_gnomad/` (written there by Colab) · the X0 notebook ·
all five X0 output CSVs · `reference/{checksums_X0.md5,data_manifest_X0.csv,sh3_genes_uniprot.tsv,
domainome_column_map.md,checksums_models.md5}` · `results/E2_domainome_external/{per_domain,
matched_variants}_E2.csv`

## Different by design

| | |
|---|---|
| `Downloded data/` (19 GB archive) | DEU drive only |
| `absolute-stability-predictor/` (221 MB) | DEU drive only; `download_weights.sh` refetches it in Colab |
| `.git`, `.gitignore` | local only |
| The 12 original inputs (7.5 GB) | Drive `sh3_repro/input/` and the DEU drive — not duplicated into `extended/` |

---

## Notes that have already cost time

**Drive cannot copy folders**, only move them. A move is instant (metadata only) even for gigabytes;
a copy has to be done from Colab, and `shutil.copytree` over the FUSE mount is glacial. Use
`pathlib.Path.rename()`.

**The X0 notebook tolerates a renamed project folder.** It resolves `sh3_repro/extended`, then
`SH3_extended`, `SH3 extended`, `sh3_extended`, and raises a clear error naming what it tried. But
re-upload it after any local edit — a stale copy on Drive pointing at a folder that no longer exists
fails on the setup cell.
