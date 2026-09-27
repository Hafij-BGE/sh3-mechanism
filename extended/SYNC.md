# Making local and Drive identical

State as of 2026-09-27 00:15. Local root is `sh3 updated/extended/`; Drive root is
`MyDrive/sh3_repro/extended/`.

Three things differ, and they differ in both directions.

---

## A. Drive-side restructuring — run this first

Drive still has the old flat `input_new/` layout, plus junk from a zip extraction. Do it from a Colab
cell rather than the web UI: renames on Drive are metadata-only and instant, while dragging folders in
the browser is slow and easy to get wrong.

```python
from google.colab import drive; drive.mount('/content/drive')
import shutil, pathlib
P = pathlib.Path('/content/drive/MyDrive/sh3_repro/extended')

# 1. input_new -> input/external   (matches local; the notebook already accepts both)
old, new = P/'input_new', P/'input'/'external'
if old.exists() and not new.exists():
    new.parent.mkdir(parents=True, exist_ok=True)
    old.rename(new); print('renamed input_new -> input/external')

# 2. drop the macOS resource-fork junk from the zip
mac = new/'domainome'/'__MACOSX'
if mac.exists(): shutil.rmtree(mac); print('removed __MACOSX')

# 3. the folders that are still missing
for d in ('domainome/analysis_files','domainome/notebooks','stability/mgnify',
          'stability/benchmarks','signatures','binding','genome'):
    (new/d).mkdir(parents=True, exist_ok=True)
(P/'input'/'frozen').mkdir(parents=True, exist_ok=True)

print(sorted(p.name for p in (P/'input').iterdir()))
```

---

## B. Local → Drive: 2.4 GB to upload

Use **New → Folder upload** in the Drive web UI and drop each local folder into its destination. Folder
upload preserves the tree, so this is far less error-prone than file-by-file.

| Upload this local folder | into Drive | Size | Needed by |
|---|---|---|---|
| `input/external/stability/mgnify/` (4 files) | `extended/input/external/stability/` | 2.3 GB | **E3** leakage audit |
| `input/external/domainome/analysis_files/` (5 files) | `extended/input/external/domainome/` | 1.2 GB | **E2** kcal/mol, domain map |
| `input/external/domainome/notebooks/` (3 `.Rmd`) | `extended/input/external/domainome/` | 39 KB | decodes headerless columns |
| `input/external/stability/benchmarks/` (3 files) | `extended/input/external/stability/` | 8.3 MB | ThermoMPNN, ProteinDPO |
| `input/external/signatures/` (2 files) | `extended/input/external/` | 0.4 MB | **G1** |
| `input/frozen/` (10 files) | `extended/input/` | 19 MB | atlas + B3 + B1 + F1 copies |
| `results/E2_domainome_external/` (2 files) | `extended/results/` | 0.5 MB | E2 output |

Single files:

| File | into Drive |
|---|---|
| `input/external/domainome/Supplementary_Table_3_esm1v_residuals.txt` | `…/domainome/` |
| `reference/checksums_ext.md5`, `reference/domainome_column_map.md` | `extended/reference/` |
| `tools/nb_X.py`, `tools/e2_domainome_validation.py` | `extended/code/` |
| `PLAN.md`, `DOWNLOADS.md`, `README.md`, `UPLOAD_LIST.md`, `SYNC.md` | `extended/` |
| `input/README.md` | `extended/input/` |

**Dropping the two optional large files** — `gnomad_v4_variants_domainome.txt` (415 MB) and
`domainome_structural_annotation.txt` (734 MB) — cuts the upload to **1.3 GB**. Neither is used by
E1, E2 or E3.

### Re-upload the notebook — this one is not optional

The Drive copy was uploaded before the folder move and still resolves `SH3_extended`, which no longer
exists. **The next run would fail on the setup cell.** Replace
`extended/code/X0_acquire_external_data.ipynb` with the local
`notebooks/X0_acquire_external_data.ipynb`, which resolves `sh3_repro/extended` first.

---

## C. Drive → local: 55 MB to download

X0 ran on Drive, so its outputs exist only there.

| Download from Drive | to local | Size |
|---|---|---|
| `extended/results/X0_external_data/` (7 files) | `results/X0_external_data/` | 55 MB |
| `extended/reference/checksums_X0.md5`, `data_manifest_X0.csv` | `reference/` | 1 KB |

Right-click the folder in Drive → **Download** gives a zip.

**Optional, 219 MB:** `input/external/clinical/gnomad_cache.json` — the raw API responses for all 235
genes. Already distilled into `gnomad_sh3_missense.csv`, so it only matters if you want to re-derive
the gnomAD table without re-querying the API.

---

## D. Verify

From a Colab cell, once B is done:

```python
%cd /content/drive/MyDrive/sh3_repro/extended
!md5sum -c reference/checksums_ext.md5 2>&1 | tail -20
```

47 lines, 8 of them checked against the publishers' own checksums. Anything reporting `FAILED` is a
truncated or corrupted upload — Drive's web uploader fails silently on large files often enough that
this check is worth running.

---

## What will still differ, by design

| | Local only | Drive only |
|---|---|---|
| `Downloded data/` (14 GB archive) | ✓ | |
| `absolute-stability-predictor/` (221 MB) | ✓ | refetched by its own script |
| `.git`, `.gitignore` | ✓ | |
| `input/external/genome/`, `binding/` | empty both sides | |

The 12 original raw inputs (7.5 GB) live at `sh3_repro/input/` on Drive and on the `DEU thesis` drive
locally. They are not duplicated into `extended/` on either side; only G3 and H1 need them.
