# Keeping local and Drive in step

Local root: `sh3 updated/extended/` · Drive root: `MyDrive/sh3_repro/extended/`

The two are one folder each, mirroring the single GitHub repository. Colab reads Drive; the frozen
run sits beside it at `MyDrive/sh3_repro/`, which every old notebook hardcodes — **do not rename it.**

---

## Outstanding: upload to Drive

Checked 27 September 2026.

| Upload | into | Size |
|---|---|---|
| `input/external/genome/Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz` | `input/external/genome/` | **842 MB** |
| `input/external/binding/` — the whole folder | `input/external/` | 18 MB |
| `reference/checksums_ext.md5` — **Drive's copy is stale**, 35 entries against 39 | `reference/` | 4 KB |
| `results/E2_domainome_external/` — `noise_ceiling_E2.csv`, `noise_ceiling_matched_E2.csv`, `ANALYSIS_E2_noise_ceiling.md` | same path | small |
| `tools/*.py` — `nb_X.py`, `e2_domainome_validation.py`, `e2_noise_ceiling.py` | `code/` | small |
| `docs/` — `PLAN.md`, `DATA.md`, `SYNC.md` | `docs/` | small |

Everything but the genome is under 20 MB, and the genome is needed only by G1, so it can wait.

Use **New → Folder upload** for whole folders — it preserves the tree and is far less error-prone
than file-by-file.

## Then verify

In a Colab cell (two lines — `%cd` is notebook magic and does not work in a shell):

```python
%cd /content/drive/MyDrive/sh3_repro/extended
!md5sum -c reference/checksums_ext.md5
```

Expect **39 OK**. Drive's web uploader truncates large files silently often enough that this is worth
running after every bulk upload.

If it reports failures on the model checkpoints, you used the wrong file — those live in
`reference/checksums_models.md5` and are absent from Drive by design.

---

## Already in sync

`input/external/{domainome,stability,clinical,signatures}` · `input/frozen/` · the X0 notebook ·
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
