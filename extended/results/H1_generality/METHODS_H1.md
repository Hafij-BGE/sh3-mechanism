# H1 — sources and methodology

Companion to `ANALYSIS_H1.md`, which will carry the interpretation once the notebook has run.
**This file declares what is read and what is done to it, and nothing else.**

Written 28 September 2026, **before the notebook was executed**. Nothing here depends on a result.

Judged against `docs/preregistration/H1.md`, committed first. Where this file states a
threshold, it is quoting that one.

---

## 1. Sources

### 1.1 The model — frozen, unchanged

| | |
|---|---|
| File | `results/B1_folding_model/models.pt` (frozen run) — bundled copy at `extended/input/frozen/results/models.pt` |
| Size | 14,579,877 bytes |
| MD5 | `fef10a7b1c1d731e6ce3e430c274b11f` |
| Produced | 22 September 2026 |
| Contents | the seed ensemble of `FoldHead(1292)` state dicts, plus the feature scaler (`m`, `sd`) |

**No weight is updated anywhere in H1**, and no head is trained. H1 changes the evaluation set only.

### 1.2 The pipeline module — the frozen run's own

| | |
|---|---|
| File | `src/sh3_common.py`, uploaded to the frozen run's `code/` folder |
| Used | `SCALARS`, `KD`, `VOL`, `CHG`, `build_X`, `FoldHead`, `load_fold_models`, `fold_scores`, `DEV` |

Imported rather than re-implemented. Re-writing any of it would be the fastest way to make H1's
numbers incomparable with Phase 1's, which is the entire point of the exercise.

### 1.3 The measurements — Human Domainome 1.0

| | |
|---|---|
| File | `Extended_data_Table_2_fitness_scores_normalized_domainranks.txt` |
| Size | 116,304,621 bytes |
| MD5 | `ef1f5c4afe5979b4a5996e48536738db` |
| Rows | 602,882 |
| Columns read | `domain_ID`, `uniprot_ID`, `wt_aa`, `position`, `mut_aa`, `STOP`, `normalized_fitness`, `normalized_fitness_sigma` |

**Upstream.** Beltran A. *et al.*, *Human Domainome 1.0*, **Nature** 2025,
doi:10.1038/s41586-024-08370-4. Zenodo record **14356805** (v5, 10 December 2024); concept DOI
10.5281/zenodo.11043642. Provenance in `extended/docs/DATA_PROVENANCE.md` §1.

`domain_ID` is `UNIPROT_PFAM_index`, so the Pfam accession is field 2 of the identifier split on `_`.
That is the family label; **no external Pfam lookup is performed.**

### 1.4 Domain sequences

| | |
|---|---|
| File | `input/domainome_domain_sequences.tsv` |
| Size | 75,174 bytes · MD5 `00c6fce13ba1fdf757480d9055b460c4` |
| Rows | 1,022 — one per distinct Domainome domain |

Produced by H1.0; its extraction command and the field-offset caveat are in
`../H1_0_leakage_audit/METHODS_H1_0.md` §1.3.

### 1.5 The reproduction target — E2

| | |
|---|---|
| `matched_variants_E2.csv` | 365,114 bytes · MD5 `c0c037a51a904744a6f22308f0c8af87` |
| `per_domain_E2.csv` | 1,459 bytes · MD5 `bfb1c0021a4a978d2de93241d8c5a138` |

E2 is a Phase 2 result about SH3. It is **read, never recomputed**, and serves two distinct purposes
that the pre-registration separates:

- `matched_variants_E2.csv` supplies the variant set for the **reproduction control** (§2.6).
- `per_domain_E2.csv` supplied the **−0.15 margin** and the Part 5 power table, both fixed before
  the notebook existed.

### 1.6 The encoder

`facebook/esm2_t33_650M_UR50D`, from Hugging Face, in half precision on GPU. Not vendored; the
notebook downloads it.

### 1.7 Not used

No structural feature (A2 excludes structure from the model by design). No atlas prediction. No
number from Phase 1 or Phase 2 is recomputed. Nothing outside `extended/` is written.

---

## 2. Methodology

### 2.1 Arms

Selected by Pfam accession, from the H1.0 audit's finding that all four families are absent from
MegaScale training:

| arm | Pfam | why |
|---|---|---|
| **main** | PF00249, PF00628, PF00643 | absent from training **and** length-matched to it (32–72 residues) |
| **secondary** | PF00595 | absent, but 70–97 residues — longer than anything in training |
| **comparator** | PF00018 | SH3, **recomputed on Domainome** under this identical pipeline (Part 9.1) |

Rows are kept when scored, missense (`wt_aa != mut_aa`) and not `STOP`.

### 2.2 The position assertion, before anything else

Domainome's `position` is domain-relative. Every row must satisfy

```
wt_seq[position - 1] == wt_aa
```

and the run stops otherwise. Three Phase 2 defects came from a position index that looked right and
was not; every embedding lookup below depends on this one.

### 2.3 Embeddings and log-odds — A2's procedure, unchanged

One forward pass per **distinct domain**, on the **wild-type** sequence:

- **Embedding**: last hidden state, residues `1..L`, so a variant takes row `pos − 1`.
- **Log-odds**: each position masked in turn, batched; `log_softmax` over the 20 standard residues.

From these, three of the twelve scalars:

```
esm_score   = logodds[mut] − logodds[wt]
esm_wt_logp = logodds[wt]
esm_entropy = −Σ exp(lo)·lo
```

Cached to `esm_H1.npz` on Drive so a disconnected session resumes without repeating GPU work.

### 2.4 The twelve scalars

`sh3_common.SCALARS` fixes both the membership and the **order**:

```
esm_score, esm_wt_logp, esm_entropy, rel_pos, dom_len,
d_hydropathy, d_volume, d_charge, blosum62, to_proline, from_glycine, to_glycine
```

| scalar | formula | source of constants |
|---|---|---|
| `dom_len` | `len(wt_seq)` | — |
| `rel_pos` | `pos / dom_len` | — |
| `d_hydropathy` | `KD[mut] − KD[wt]` | `sh3_common.KD`, Kyte–Doolittle |
| `d_volume` | `VOL[mut] − VOL[wt]` | `sh3_common.VOL` |
| `d_charge` | `CHG[mut].fillna(0) − CHG[wt].fillna(0)` | `sh3_common.CHG` |
| `blosum62` | `B62[wt][mut]` | `Bio.Align.substitution_matrices` |
| `to_proline`, `from_glycine`, `to_glycine` | indicators | — |

`build_X` concatenates the 1,280 embedding dimensions with these twelve and **the notebook asserts
`X.shape[1] == 1292`**, which is what catches a silent mismatch.

### 2.5 Prediction

```
fold_scores(FOLD, X, SC_M, SC_SD, clip=10).mean(0)
```

**`clip = 10` is not a choice made here.** It is how B1 produced the atlas predictions that B3 and E2
used (`Pa = fold_scores(..., clip=10)`), so it is the setting under which the comparator was
measured. Pre-registration Part 9.4 pins it.

### 2.6 The reproduction control

Restricted to E2's own matched variants, joined on `domain_ID`, `position`, `mut_aa`:

| | |
|---|---|
| must return | median per-domain \|ρ\| of **0.573** |
| tolerance | **±0.02** |

If it fails, the features or the model are not the frozen ones and **no arm is interpretable** — the
run stops. This is the role G1's reproduction check played, and the reason G1's result could be
trusted when it overturned a published claim.

### 2.7 The statistic and the test

- **Per domain**: Spearman |ρ| between `pred_ddG_fold` and `normalized_fitness`, for domains with
  **≥ 20** scored variants (E2's convention).
- **Per arm**: the **median** of those.
- **Test**: non-inferiority, not significance. `Δ = median|ρ|(arm) − median|ρ|(SH3)`, with a 95 %
  interval from **4,000 bootstrap resamples over domains, not variants**, because domains are the
  unit of replication.

| verdict | condition |
|---|---|
| supported | CI lower bound > −0.15 |
| not supported | CI upper bound < −0.15 |
| inconclusive | CI spans −0.15 |

**The −0.15 margin is the standard deviation of SH3's own per-domain \|ρ\| (0.140, rounded)**, taken
from `per_domain_E2.csv` before the notebook existed. Fewer than 20 domains in the main arm → no
verdict.

Seed for the bootstrap: `20260928`, fixed in the notebook.

### 2.8 Reading the two arms

Part 6's 2 × 2 is implemented as a lookup table, so the reading cannot be composed after seeing the
numbers. **PDZ carries no verdict of its own** under any cell.

### 2.9 The assay-quality figure, and what it is not

`median(|normalized_fitness| / normalized_fitness_sigma)` per arm is reported. **This is not a noise
ceiling in E2's sense.** E2 could state that 0.600 was 85 % of what two independent assays achieve
against each other, because SH3 has both MegaScale and Domainome measurements. The new families have
no MegaScale data **by construction** — that is precisely why they are held out — so no
between-assay ceiling exists for them. The replicate ratio is a weaker within-assay quantity and is
labelled as such wherever it appears.

---

## 3. Execution

| | |
|---|---|
| Notebook | `extended/notebooks/H1_generality.ipynb` — MD5 `809db4f6f83b3ff8cb69b90e222b9d9e`, 24 cells |
| Generated by | `tools/nb_H1.py` |
| Hardware | **A100 40 GB** |
| GPU work | ESM-2 650M over ~102 domains of 45–97 residues: one forward pass each plus a masked scan. Minutes |
| Memory | far below 40 GB; the mask batch is 64 for comfort, not for the limit |

The generator runs a **cell-order guard** — a static pass asserting that no cell reads a name an
earlier cell has not bound. It exists because the G1 notebook shipped with exactly that defect and
raised `NameError` on Colab.

### Reproducing it

```bash
python3 tools/nb_H1.py      # regenerate the notebook
# then run notebooks/H1_generality.ipynb on Colab with an A100
```

## 4. Known limits of the method

- **No between-assay noise ceiling for the new families** (§2.9), so a lower |ρ| cannot be separated
  from noisier measurements except through the weaker replicate ratio.
- **Three families pooled are still three families**, and Myb/SANT, PHD and B-box are all small
  zinc- or DNA-binding folds — not a random sample of protein space.
- **PHD and B-box coordinate zinc.** Their stability in an abundance assay may depend on metal
  availability, which the model cannot represent and SH3 never required.
- **Abundance is not ΔΔG.** The same interpretive gap E2 carried.
- **This tests folding, not binding.** Phase 1's ~80-position threshold is a binding claim on
  PSD95-PDZ3 and is untouched by H1.
- **The embedding is of the wild-type sequence**, so two substitutions at the same position share
  1,280 of their 1,292 features and differ only in the scalars. That is Phase 1's design, inherited
  here deliberately so the comparison holds.
