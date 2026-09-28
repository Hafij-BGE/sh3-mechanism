# Upload note — what G1 needs on Drive

Two notebooks, `G1a_observed_spectrum` and `G1b_cosmic_spectrum`. They read from the same Drive
folder the E-series used, **`MyDrive/sh3_repro/`**, and write to
`sh3_repro/extended/results/G1_mutational_context/`.

**Four files to upload, 596 KB in total.** The 842 MB genome is *not* one of them — see §3.

---

## 1. Upload these

Paths on the left are relative to `~/Documents/thesis/sh3 updated/`.

| # | Laptop file | Drive folder | Size |
|---|---|---|---|
| 1 | `extended/results/G1_mutational_context/atlas_grch38_coordinates.tsv` | `sh3_repro/extended/results/G1_mutational_context/` | 396 KB |
| 2 | `extended/docs/preregistration/G1.md` | `sh3_repro/extended/docs/preregistration/` | 24 KB |
| 3 | `extended/input/external/signatures/COSMIC_v3.6_SBS_GRCh38.txt` | `sh3_repro/extended/input/external/signatures/` | 176 KB |
| 4 | `extended/notebooks/G1a_observed_spectrum.ipynb`, `G1b_cosmic_spectrum.ipynb` | anywhere you open Colab from | small |

**Item 2 is not documentation.** The notebook reads `G1.md` to decide its own α — 0.025 if a
`PRIMARY SPECTRUM:` line is present, 0.0125 for both if it is not. If the file is missing, both
notebooks run co-primary at 0.0125, which is the safe default but not necessarily the one you want.

**`extended/tools/*.py` is not in this list and must not be uploaded.** `g1_core.py` is embedded
inside both notebooks byte-for-byte, and each asserts its SHA-256 at run time. A stray copy on Drive
would be ignored at best and shadow the embedded one at worst.

## 2. Check these are already there

All three were used by earlier programs, so they should be on Drive already. Verify rather than
re-upload.

| | Drive path | Used by |
|---|---|---|
| `dbnsfp_sh3_domains.parquet` | `sh3_repro/extended/results/X1_dbnsfp_subset/` | X1 |
| `SH3_cancer_master.tsv` | `sh3_repro/extended/input/frozen/results/` | E1, E2, E4 |
| `sh3_virtual_dms.parquet` | `sh3_repro/results/B6_virtual_saturation_mutagenesis/` | E1 |

**The dbNSFP parquet is the one that matters.** It is the null pool — the only source of a genomic
coordinate for every *possible* in-domain missense SNV, not just the observed ones. It is **not on
this laptop**; only the older, superseded `.tsv.gz` is. If it is missing from Drive, say so and the
notebook gets a cell that rebuilds it from the raw release.

## 3. The genome fetches itself

`Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz` is 842 MB. **Do not upload it.** Colab pulls it from
Ensembl in a couple of minutes — far faster than a home connection can push it — and the notebook
does that automatically when the Drive copy is absent.

It asserts the download is exactly **881,964,081 bytes**, the figure pinned in `DATA_PROVENANCE.md`
§7. If Ensembl rolls to a new release the assertion fires rather than silently reading contexts from a
different assembly.

## 4. Run order

```
G1a_observed_spectrum   →  metrics_G1a.json, RESULTS_G1a.md
G1b_cosmic_spectrum     →  metrics_G1b.json, RESULTS_G1b.md
```

Either order; they do not read each other. Each takes one streaming pass over the genome, so budget a
few minutes apiece. **CPU is fine — there is no model inference anywhere in G1.**

Then, on the laptop, once both metrics files are back:

```bash
python3 extended/tools/g1_compare.py --results extended/results/G1_mutational_context --out extended/results/G1_mutational_context/RESULTS_G1_comparison.md
```

## 5. What to expect, and what stops the run

Both notebooks check themselves. The ones that will actually fire:

| Check | Means |
|---|---|
| **3a control ≠ 9.18 %** | this implementation differs from B6 in something that is *not* the trinucleotide weighting. **Stop.** The spectrum arm is not interpretable, and the pre-registration says so |
| `g1_core.py` hash mismatch | the notebook was edited by hand. Regenerate with `python3 tools/nb_G1.py` |
| reference base disagrees | the coordinate table and the genome are not the same assembly |
| fewer than 3,000 eligible | Part 4: numbers are printed, **no verdict** |
| genome byte count | Ensembl moved release, or the download truncated |

`g1_compare.py` additionally refuses to compare at all if the two notebooks ran different
`g1_core.py` hashes, produced different uniform-control rates, or used different eligible sets — any
of which would make a difference between them attributable to the code rather than the spectrum.
