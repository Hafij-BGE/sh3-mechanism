# H1.0 — sources and methodology

Companion to `ANALYSIS_H1_0.md`, which carries the interpretation. **This file declares what was
read and what was done to it, and nothing else.** Every number in the analysis is reproducible from
what is below.

Run 28 September 2026, locally, CPU only. Tool: `tools/h1_leakage_audit.py`.

---

## 1. Sources

### 1.1 Training set — MegaScale, as reduced by A2

| | |
|---|---|
| File | `results/A2_features/features_megascale.parquet` |
| Size | 5,653,716 bytes |
| MD5 | `7484f147d556cb74ab6529d22c93917b` |
| Written | 22 September 2026, by A2 (the frozen run) |
| Contents used | `domain_key`, `wt_seq`, `is_sh3` — **no prediction column was read** |
| Rows | 389,068 substitutions, **412 distinct domains** |

**Upstream.** Tsuboyama K. *et al.*, mega-scale experimental analysis of protein folding stability,
2023; dataset `Tsuboyama2023_Dataset2_Dataset3_20230416`, distributed as
`Processed_K50_dG_datasets.zip`. A2 derived this table from it; H1.0 does not re-derive it and does
not modify it.

**Why this file and not the raw release.** It is the exact set the frozen head was trained on. The
raw release contains more than was used, so auditing it would answer a different question than "what
did this model see".

### 1.2 Evaluation candidates — Human Domainome 1.0

| | |
|---|---|
| File | `extended/input/external/domainome/analysis_files/domainome_structural_annotation.txt` |
| Size | 769,119,845 bytes |
| MD5 | `1e457968404ec60dfa7834af57667439` |
| Dated | 2 September 2024 (as distributed) |

**Upstream.** Beltran A. *et al.*, *Human Domainome 1.0*, **Nature** 2025,
doi:10.1038/s41586-024-08370-4. Zenodo record **14356805** (v5, 10 December 2024), the version that
matches the published paper; concept DOI 10.5281/zenodo.11043642. Provenance and the v3-versus-v5
correction are recorded in `extended/docs/DATA_PROVENANCE.md` §1.

**Field layout, stated because it caused an error.** The header names 
`"aa_seq" "dom_ID" "pos" …`, but each data row carries an **unnamed leading row-number field**, so
the columns are offset by one: `$3` is `dom_ID` and `$7` is `wt_seq`. A first pass keyed on `$2`/`$6`
returned zero PDZ domains, which is a false negative, not a finding.

### 1.3 Derived input, produced here

| | |
|---|---|
| File | `input/domainome_domain_sequences.tsv` |
| Size | 75,174 bytes |
| MD5 | `00c6fce13ba1fdf757480d9055b460c4` |
| Rows | **1,022** — one per distinct Domainome domain |

Extracted by one streaming pass, first occurrence per `dom_ID`:

```bash
awk 'NR>1 {gsub(/"/,"",$3); gsub(/"/,"",$7);
           if(!($3 in s)) {s[$3]=1; print $3"\t"$7}}' \
    domainome_structural_annotation.txt > domainome_domain_sequences.tsv
```

`dom_ID` is `UNIPROT_PFAM_index`, so the Pfam accession is field 2 of the identifier split on `_`.
That is the family label used throughout; **no external Pfam lookup was performed.**

### 1.4 Corroborating source, used only as context

`domains_from_tsuboyama_rocklin_overlaps.txt` (4,964 bytes, same Zenodo record) lists 32 domains
present in both MegaScale and the aPCA assay, with Pfam ids. It is the aPCA∩MegaScale intersection,
**not** all of MegaScale, so it can show a family *is* in MegaScale and can never show one is
absent. It is cited in the analysis only as the weaker evidence that prompted the full audit.

### 1.5 Not used

No model was loaded, no prediction was computed, no network request was made, and no file outside
`extended/` was written. The frozen run was read only.

---

## 2. Methodology

### 2.1 The question, stated precisely

Not *"what family is each MegaScale domain?"* — 312 of the 412 are de novo designs with no natural
family. The question is the one that governs H1:

> **Are the Domainome domains we would evaluate on present in the MegaScale training set?**

So the match runs **from** MegaScale **to** Domainome, and an unmatched MegaScale design is not a gap
in the audit. A family reported as absent means *no Domainome domain of that family appears in
MegaScale*, which is exactly the condition H1 needs.

### 2.2 Sequence matching

Both sides are assay constructs of the same domain region rather than diverged homologues, so a
gapless comparison is appropriate and no alignment library is used:

```
best_identity(a, b) = max over all offsets k of
                      (# positions where a[i] == b[k+i]) / len(shorter)
```

This is the same sliding comparison A2 used to derive PDB→construct offsets.

| parameter | value | why |
|---|---|---|
| `MIN_IDENTITY` | **0.50** | the threshold Phase 1 used to match MegaScale to UniProt; carried over rather than chosen here |
| `LEN_TOLERANCE` | **40** residues | pairs differing by more cannot align meaningfully; skipping them is a speed measure, not a filter on the result |

Every MegaScale domain is compared against every Domainome domain within the length tolerance, and
the single best match is kept. 412 × 1,022 pairs.

### 2.3 The assertion that validates the method

SH3 is the one family known to be in training, because the frozen split held it out by name. The tool
**asserts** before reporting anything else:

```python
assert sh3_found >= 20   # 27 matched PF00018; the training table flags 26 as is_sh3
```

If the matching were broken, this fails and no family table is produced. It is the only external
check available on a procedure whose output has no ground truth of its own — the same reasoning that
made X1's coverage comparison against the publisher's figures the check that caught its worst defect.

### 2.4 Length comparison

Construct length is `len(wt_seq)` on both sides, so the two are measured identically. A family is
flagged `length_matched` when its **median** Domainome length falls inside MegaScale's observed
range:

```
length_matched  ⟺  32 ≤ median_len ≤ 72
```

The bounds are MegaScale's own minimum and maximum, computed here rather than assumed. They are a
property of the proteolysis assay, not a modelling choice.

### 2.5 Candidate rule

A family is reported as a candidate second family when **all three** hold:

1. `megascale_domains == 0` — absent from training
2. `length_matched` — median length inside MegaScale's range
3. `domainome_domains >= 15` — enough domains for a per-domain correlation to mean anything

The count floor of 15 is set against SH3's own evaluation, which used 15 held-out domains.

---

## 3. Outputs

| File | Contents |
|---|---|
| `megascale_family_map.csv` | one row per MegaScale domain: best Domainome match, identity, Pfam |
| `family_audit.csv` | one row per Domainome family: domain count, length range, whether in training, whether length-matched |
| `metrics_H1_0.json` | the summary, including the SH3 control and the candidate list |
| `ANALYSIS_H1_0.md` | interpretation — separate from this file by design |

## 4. Reproducing it

```bash
python3 tools/h1_leakage_audit.py \
    --root . \
    --domainome input/domainome_domain_sequences.tsv \
    --out results/H1_0_leakage_audit
```

Minutes on CPU. Requires `pandas`. Deterministic — there is no sampling anywhere in this program.

## 5. Known limits of the method

- **Absence is established only for Domainome domains.** For the 312 unmatched MegaScale designs the
  family is unknown, so "PF00249 appears nowhere in MegaScale" is stronger than the evidence
  supports. "No Domainome PF00249 domain is in MegaScale" is what was shown.
- **Gapless matching** would miss a homologue with an indel relative to the construct. At the 50 %
  threshold over same-region constructs this is unlikely, but it is not impossible, and it would
  cause a false *absent*.
- **Pfam labels are taken from the Domainome identifier**, so the family assignment is the Domainome
  authors', not ours, and inherits whatever their Pfam version decided.
- **The length ceiling is measured, not documented.** 72 residues is the maximum observed in this
  table; the assay's design limit is not quoted from the Tsuboyama paper here.
