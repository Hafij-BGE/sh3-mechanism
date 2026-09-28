# H1.3 — sources and methodology

Companion to `ANALYSIS_H1_3.md`. **Declares what was read and what was done to it, and nothing else.**

Run 28 September 2026, locally, CPU, seconds. Tool: `phase3/tools/h1_3_assay_quality.py`.
Pre-registered in `phase3/docs/preregistration/H1_3_assay_quality.md`, committed before the join
between accuracy and assay quality existed.

---

## 1. Sources

### 1.1 Accuracy — H1's published per-domain correlations

| | |
|---|---|
| File | `phase3/results/H1_generality/per_domain_H1.csv` |
| Rows | 102 domains — 35 main, 31 pdz, 36 sh3 |
| Columns used | `domain_ID`, `pfam`, `arm`, `absrho` |
| Origin | written by `H1_generality.ipynb` on Colab, 28 Sep 2026 |

**Read as published. No prediction is recomputed here**, and the ESM encoder, the frozen head and the
feature pipeline are not invoked at all.

### 1.2 Assay quality — Domainome Table 2

| | |
|---|---|
| File | `Extended_data_Table_2_fitness_scores_normalized_domainranks.txt` |
| Size | 116,304,621 bytes · MD5 `ef1f5c4afe5979b4a5996e48536738db` |
| Columns used | `domain_ID`, `wt_aa`, `position`, `mut_aa`, `STOP`, `normalized_fitness`, `normalized_fitness_sigma` |

Beltran A. *et al.*, **Nature** 2025, doi:10.1038/s41586-024-08370-4; Zenodo 14356805 (v5).

### 1.3 A transcription error, recorded because the assertion caught it

H1's per-domain file lives on Drive. It was brought across by decoding a base64 copy, and **two
characters were corrupted in transit**: `Q86UL8` became `Q96UL8` on two rows.

The join assertion in §2.3 fired — 100 of 102 domains found an assay value — and the two missing
identifiers turned out not to exist in Table 2 at all. Corrected, then verified four ways:

| check | result |
|---|---|
| every `domain_ID` present in Table 2 | **102 / 102** |
| `pfam` column agrees with the Pfam embedded in each identifier | **102 / 102** |
| per-family median \|ρ\| against `metrics_H1.json` | **5 / 5 to 4 dp** |
| domains per arm against H1 | 35 / 31 / 36, exact |

Recorded rather than quietly fixed: a hand-carried data file is a real risk, and the only reason it
did not become a silent error is that the join was asserted instead of assumed.

---

## 2. Methodology

### 2.1 Assay quality per domain

```
snr(domain) = median( |normalized_fitness| / normalized_fitness_sigma )
```

over the same rows H1 used — scored, missense, non-STOP, non-null position — and domains with at
least 20 such variants. A σ of exactly 0 is treated as missing rather than infinite.

**This is a within-assay quantity, not a noise ceiling.** It compares a measurement to its own
replicate error, not to an independent assay. A family with consistent, precise and systematically
wrong measurements scores well on it.

### 2.2 The matching band

Fixed in the pre-registration before any join: from the **main arm's 10th percentile** to **SH3's
90th**, computed from the two arms in the primary comparison.

| | value |
|---|---|
| band | **1.28 – 3.80** |
| main retained | 31 of 35 |
| sh3 retained | 30 of 36 |
| pdz retained | 18 of 31 |

### 2.3 The assertion

Every H1 domain must find an assay-quality value, or the comparison would run on a different set than
H1 reported:

```python
assert len(D) == len(R)
```

This is the check that caught §1.3.

### 2.4 The statistic

Identical to H1's, so the two are directly comparable:

- **median per-domain |ρ|** per arm
- **Δ** against SH3
- 95 % CI from **4,000 bootstrap resamples over domains**, seed `20260928`
- margin **−0.15**

### 2.5 The rule for Q1

From Part 4 of the pre-registration, implemented as written:

| verdict | condition |
|---|---|
| `assay_quality_explains_the_gap` | matched CI includes 0 |
| `assay_quality_does_not_explain_it` | matched CI upper < 0 **and** \|shift\| ≤ 0.05 |
| `partly` | matched CI upper < 0 and shift > 0.05 toward zero |
| `inconclusive` | otherwise |

`shift = matched Δ − unmatched Δ`. **0.05 is a third of the margin**, set because H1 established this
design cannot resolve differences that small.

### 2.6 Q2 and Q3

Reported, no verdict. Q2 repeats the matched comparison for PDZ against SH3. Q3 is the Spearman
correlation between per-domain |ρ| and per-domain assay quality across all 102 domains.

---

## 3. Outputs

| | |
|---|---|
| `per_domain_rho_and_snr.csv` | the joined table, 102 rows |
| `metrics_H1_3.json` | all three questions, band, retention, per-family assay quality |
| `ANALYSIS_H1_3.md` | interpretation — separate by design |

## 4. Reproducing it

```bash
python3 phase3/tools/h1_3_assay_quality.py \
    --rho phase3/results/H1_generality/per_domain_H1.csv \
    --domainome extended/input/external/domainome/Extended_data_Table_2_fitness_scores_normalized_domainranks.txt \
    --out phase3/results/H1_3_assay_quality
```

Seconds on CPU. Requires `pandas` and `scipy`. Deterministic apart from the bootstrap, which is
seeded.

## 5. Known limits of the method

- **Matching is not adjustment.** Restricting to a common band removes the gross difference in assay
  quality between arms; it does not remove any residual relationship within the band. Q3 measures
  that relationship and nothing corrects for it.
- **Q3 is partly mechanical.** A domain with noisier measurements has an attenuated correlation with
  *anything*, so a positive |ρ|-versus-quality relationship is expected even if the predictions are
  equally good everywhere. Its size is informative; its existence is not.
- **The ratio ignores systematic error**, per §2.1.
- **This is post-hoc.** The design followed H1's result, and everything it produces is weaker than
  the same finding from a pre-planned experiment.
