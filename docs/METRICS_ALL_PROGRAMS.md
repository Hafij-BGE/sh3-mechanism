# Every metric, every program

The complete numeric record: **28 programs across three phases**, taken from the committed
`metrics_*.json` files rather than retyped from prose.

For *what the numbers mean*, see [`METRICS_AND_FINDINGS.md`](METRICS_AND_FINDINGS.md). For *why each
step was done that way*, see [`METHODOLOGY.md`](METHODOLOGY.md).

Conventions: ρ is Spearman; |ρ| is used where the model correlates negatively by construction;
positive ΔΔG is destabilising; **pp** is percentage points.

---

# Phase 1 — build the model (A, B, C, D, F)

## A0 · cancer atlas

| | |
|---|---|
| COSMIC CMC rows read | 5,802,907 |
| Genome-screens rows | 62,765,128 · 53,598 samples |
| Missense in SH3 genes | 91,842 |
| Mapped: canonical / isoform / unmapped | 5,923 / 1,034 / 490 |
| **Atlas** | **6,884 variants · 310 domains · 235 genes · 44 columns** |
| With sample records | 6,657 |
| Non-hypermutated variants | 2,165 · hypermutated-only 4,492 |
| Hypermutated sample fraction | 18.14 % |
| Recurrent (any / non-hyper) | 501 / 84 |
| Likely germline | 78 |
| Significance tier 1–3 · dN/dS flagged | 0 · 0 |

## A1 · ground truth

| | |
|---|---|
| ddPCA singles · both energies | 3,688 · 3,368 |
| Reliable folding / binding | 3,109 / 2,840 |
| Reliable binding by domain | GRB2-SH3 619 · PSD95-PDZ3 1,221 · GB1 1,000 |
| Calibration r, folding / binding | 0.829 (n = 15) / 0.612 (n = 12) |
| MegaScale singles · domains | **389,068 · 412** |
| MegaScale SH3 | 26 structures · 15 genes · **27,590 variants** |
| FoldX overlap · agreement with MoCHI | 1,024 · r = 0.494 |

**Burial/interface separation (fold vs bind, kcal/mol):** buried-not-interface **3.57 / 0.14**;
buried-interface 1.28 / **2.90**; surface-not-interface 0.87 / −0.04. *Folding tracks burial, binding
tracks the interface — the separation the whole project rests on.*

## A2 · features

| | |
|---|---|
| Variants featurised | 399,640 (MegaScale 389,068 · ddPCA 3,688 · atlas 6,884) |
| Dropped by the residue check | **0** |
| Domains embedded | 725 |
| Zero-shot ESM-2 ρ: ddPCA fold / bind | −0.404 / −0.259 |
| Zero-shot ESM-2 ρ: MegaScale fold | −0.388 |
| Structure rows · domains | 18,756 · 302 |
| Atlas structural coverage | **96.82 %** (9 proteins have no AlphaFold model) |
| Reference-frame coverage | 89.47 % |

## B1 · folding model

| | |
|---|---|
| Train / val / held-out | 327,027 (348 groups) / 34,451 (38) / **27,590 SH3** |
| **Per-domain median ρ** | **0.8392** · min 0.754 · max 0.934 · IQR 0.809–0.845 |
| All CIs exclude zero | **yes** |
| Pooled ρ · Pearson r · RMSE | 0.843 · 0.837 · 0.672 |
| Zero-shot ESM-2, per-domain median | 0.617 — **beaten on 15/15**, sign test p = 6.1 × 10⁻⁵ |

**Ablation (per-domain median ρ):**

| | |
|---|---|
| ESM embedding only | 0.676 |
| 12 scalars only, no embedding | 0.729 |
| embedding + 5 ESM scalars | 0.761 |
| ridge, all 1,292 features | 0.754 |
| MLP, all features, 1 seed | 0.831 |
| **MLP, all features, 5-seed ensemble** | **0.839** |
| zero-shot ESM-2, no training | 0.617 |

**Against other methods on the three ddPCA domains (ρ):**

| domain | head | ESM-2 | FoldX | EVE |
|---|---|---|---|---|
| GB1 | **0.825** | 0.204 | 0.487 | 0.370 |
| GRB2-SH3 | **0.761** | 0.728 | 0.701 | 0.638 |
| PSD95-PDZ3 | 0.540 | 0.480 | 0.466 | **0.589** |

## B2 · structural check

| | |
|---|---|
| Aligned positions | 56 |
| ρ, predicted damage vs **burial** | **+0.712** |
| ρ, predicted damage vs **interface** | **+0.037** |
| Ratio, burial : interface | **19.2×** |
| Median prediction: buried / surface / no structure | 1.161 / 0.378 / 0.659 |

*Structure was never a model input, so this is an independent test.*

## B3 · uncertainty and calls

| | |
|---|---|
| **Conformal q90** | **6.807** |
| **Empirical coverage** | **89.92 %** (target 90 %) |
| Coverage range across domains | **83.27 % – 95.04 %** |
| ρ, ensemble SD vs absolute error | 0.304 |
| Median interval half-width | 1.115 kcal/mol |
| Mechanism: tolerated / destabilising / rewiring / both | 6,283 / 297 / 191 / 113 |
| **Confidently destabilising** | **410** = 297 + 113 |
| Point-estimate calls (no interval) | 2,220 |

*The interval removes 1,810 of 2,220 point-estimate calls. That is what "conservative" costs.*

## B4 · external validation (ProteinGym) — **the weakest result in the project**

| block | assays | head \|ρ\| | zero-shot ESM-2 \|ρ\| | head wins |
|---|---|---|---|---|
| Sanity — MegaScale domains | 10 | **0.940** | 0.580 | **10 / 10** |
| **Primary — external stability** | 3 | 0.361 | **0.406** | 2 / 3 |
| **Secondary — abundance** | 15 | 0.400 | **0.491** | 6 / 15 |

**Off MegaScale, the head does not beat zero-shot ESM-2.** It drops 2.27× more than ESM-2 on primary
assays and 3.49× more on secondary. The 0.940 on the sanity block confirms the pipeline is wired
correctly and confirms nothing else.

## B5 · cancer biology — **null**

| | |
|---|---|
| Destabilising fraction, all / non-hyper | 5.96 % / 5.59 % |
| Genes tested → significant (all) | 170 → **1** |
| Genes tested → significant (non-hyper) | 17 → **0** |
| Tumour sites tested → significant | 22 → **0** |
| Positional non-uniformity | p = 2.0 × 10⁻⁴ |
| ρ, variant count vs damage / vs burial | −0.009 / −0.178 |

*The atlas is a mechanism map, not a driver list.*

## B6 · virtual saturation mutagenesis

| | |
|---|---|
| Virtual variants · domains | **366,168 · 310** |
| Max difference vs observed predictions | 9.5 × 10⁻⁷ |
| Destabilising: all possible / SNV-reachable | 12.10 % / **9.23 %** |
| Observed / observed-and-reachable | 5.96 % / **5.93 %** |
| Domain-matched null median | **9.18 %** |
| One-sided p | 0.000999 |
| ρ, family damage vs burial | +0.775 |

> **This depletion was withdrawn by G1.** See below.

## C1–C3 · why binding cannot be predicted

**C1 · across domains (corrected ρ):** GB1 −0.151 (n = 1,000) · GRB2-SH3 −0.042 (619) ·
PSD95-PDZ3 +0.132 (1,221).

**C2 · within a domain (corrected, single fit):**

| domain | ρ | positions | n |
|---|---|---|---|
| GB1 | 0.043 | 55 | 1,000 |
| GRB2-SH3 | 0.022 | **56** | 619 |
| PSD95-PDZ3 | **0.324** | **84** | 1,221 |

**`head_beats_esm_on_grb2 = False`** — the gate that stopped every binding claim downstream.

**C3 · what it would take.** Position sweep, 130 runs: ρ stays near zero to 74 positions, then
60 → −0.014, 76 → 0.113, **80 → 0.208, 82 → 0.330, 84 → 0.322**. Crossing at **76 positions**;
GRB2-SH3 has **56**. Matched-size draws around GRB2-SH3: median −0.024, CI −0.163 to +0.155.

**The limiting resource is distinct mutated positions, not variants.** More domains, not more
mutations.

## C4 · specificity axis — **not validated**

| | |
|---|---|
| PWMs · domains · clusters | 154 · 115 · 52 |
| **Median centred r** | **+0.2884** (CI 0.218 – 0.337) |
| Wins vs average profile | **55 / 115** · sign test p = 1.00 |
| Wins vs nearest neighbour | 85 |
| **`validated`** | **false** |
| ρ, rewiring vs predicted fold / vs ESM | +0.356 / −0.393 |
| Interface vs other rewiring | 0.0309 vs 0.0269 · p = 7.6 × 10⁻²⁴ |

## D1 · verification

**187 quantities checked · 160 identical · 27 within tolerance · 0 different.**

## F1 / F2 · experimental candidates — **superseded by G4**

20 candidates (10 destabilising, 10 controls), 8 tier-1. **6 of 56 aligned positions covered,
4 picks at one position, 8/10 buried, 4/10 to proline.**

---

# Phase 2 — test it against the outside world

## X0 · acquire

235 genes · ClinVar **74,116** records · gnomAD **431,959** missense · Domainome **46,128** SH3
variants over 44 domains. Atlas row count unchanged at 6,884 after every join.
**Dropped: 45 null-key rows · collapsed: 3,856 dual-Pfam duplicates.**

## X1 · dbNSFP

2,120,008 rows → **152,852 in domain** · 231/235 genes · 300/310 domains. Predictor coverage matches
the publisher's own figures to within a few points. **63.8 % ClinVar overlap remains unexplained.**

## E1 · clinical labels

| | |
|---|---|
| α · minimum group | 0.025 · 20 |
| ClinVar in domains · gnomAD in domains | 134 · 24,005 |
| Pathogenic vs benign | 21 vs 101 |
| Median predicted ΔΔG | **1.67 vs 0.19** kcal/mol |
| **p** · rank-biserial | **4.9 × 10⁻⁶** · **+0.615** (AUC ≈ 0.81) |
| Robust across arms | **yes** |
| **Sensitivity of `fold_lo ≥ 1`** | **4.8 %** |

## E2 · measured abundance

| | |
|---|---|
| Measured in Domainome | **880** of 6,884 · 41 domains · 32 genes |
| **Pooled \|ρ\|** | **0.600** · p = 4.1 × 10⁻⁸⁷ |
| Per-domain median \|ρ\| | 0.573 · **21/21 in the right direction** |
| Destabilising vs tolerated fitness | −0.748 (n = 63) vs −0.106 (n = 817) · p = 2.3 × 10⁻²² |
| **Noise ceiling** | **0.709** (4 domains with both assays) |

## E3 · benchmark

| competitor | median ρ | ours | diff | p | verdict |
|---|---|---|---|---|---|
| SaProtΔG | 0.8548 | 0.8392 | −0.0276 | 0.107 | no clear difference |
| ESM3ΔG | 0.7925 | 0.8392 | +0.0327 | **0.0084** | **ours better** |

27,590 variants scored by each, **0 dropped**. **Leakage audit: SaProtΔG 0/15 · ESM3ΔG 0/15 ·
ThermoMPNN 13/15 → disqualified.**

## E4 · specificity, independently

| arm | r | p | n | df |
|---|---|---|---|---|
| **model** | **+0.023** | 0.911 | 37 | 24 |
| average profile | −0.043 | 0.835 | 37 | 24 |
| **observed profile (control)** | **−0.051** | 0.804 | 37 | 24 |

Pooled, uncentred: ρ = −0.267 (p = 0.080) — **no verdict by design.** C4 re-run reproduced its
recorded median centred r to **1.6 × 10⁻¹⁴**.

## G1 · context-aware null — **the claim is withdrawn**

Coordinates: **6,456 of 6,884 (93.78 %)** · **100 % verified against the GRCh38 reference base** ·
dropped 314 ambiguous + 114 absent.

| arm | pool | null median | observed | gap | p |
|---|---|---|---|---|---|
| Phase 1, published | — | 0.09232 | 0.0596 | — | 0.001 |
| 3a codon reachability | 115,742 | 0.0860 | 0.0596 | +2.63 pp | 0.0001 |
| 3b + multiplicity | 154,708 | 0.0788 | 0.0596 | +1.92 pp | 0.0001 |
| **1 observed spectrum** | 154,708 | **0.0604** | 0.0596 | **+0.08 pp** | **0.401** |
| **2 COSMIC SBS1+SBS5** | 154,708 | **0.0558** | 0.0596 | −0.39 pp | **0.918** |

α = 0.0125 (co-primary) · 10,000 draws · seed 20260928 · cosine fit 1.000 / 0.688.
**Excluded 428 variants differ by 0.12 pp in destabilising rate — no bias.**

## G2 · per-domain conformal

q90 range **5.419 – 9.712** (**1.79×**) · coverage spread **11.77 pp → 6.26 pp** under Mondrian.
Confident calls: global **410** · hybrid 409 · **resampled 400, 95 % CI 378–421** · min/max q90
bracket 613/149 (*not* the uncertainty).

## G3 · scoped, then dropped

219 variants lack structure (3.2 %, 11 domains). **4 proteins have no AlphaFold model at all**; 5 are
keyed to isoform-suffixed ids. Recoverable: **72, not 219.** Changes **no prediction**.

## G4 · rebuilt panel

| | F1 | **G4** |
|---|---|---|
| Distinct aligned positions | 6 | **10** |
| Max picks at one position | 4–5 | **1** |
| To proline | 4 | **1** |
| Distinct mutant residues | 5 | **7** |
| Exposed picks | 2 | **3** |
| Buried controls | 0 | **5** |

Pool: 121 destabilising non-hyper variants over 38 aligned positions.

---

# Phase 3 — generality *(merged into `extended/`, 28 Sep 2026)*

## H1.0 · leakage audit

MegaScale **412 domains, 32–72 aa, median 51**. PDZ: 43 Domainome domains, **70–97 aa, median 88**,
**0 in training**. SH3 control: 27 matched PF00018 against 26 flagged. 100 of 412 training domains
matched any Domainome family.

## H1.2 · evaluation

| arm | domains | median \|ρ\| | Δ vs SH3 | 95 % CI | verdict |
|---|---|---|---|---|---|
| MAIN length-matched | 35 | 0.420 | −0.203 | [−0.249, −0.120] | **inconclusive** |
| PDZ | 31 | 0.602 | −0.021 | [−0.082, +0.027] | *supported*, no verdict |
| SH3 reference | 36 | 0.623 | — | — | — |

Per family: SH3 0.623 · PDZ 0.602 · Myb/SANT 0.507 · PHD 0.376 · B-box 0.335.
Reproduction control **0.5660** against E2's 0.573 (tolerance ±0.02) — **passed**.

## H1.3 · assay quality

Matched band 1.281–3.804 · retained main 31/35, SH3 30/36, PDZ 18/31.

| | Δ | 95 % CI |
|---|---|---|
| unmatched | −0.203 | [−0.249, −0.120] |
| **matched** | **−0.187** | [−0.232, −0.098] |
| shift | **+0.015** (threshold 0.05) | → **does not explain it** |
| PDZ matched | −0.077 | [−0.172, +0.009] |

ρ(|ρ|, assay quality) over 102 domains = **+0.629**, p = 1.5 × 10⁻¹².
Per-family assay quality: PDZ 3.476 · **Myb/SANT 2.535** · SH3 2.086 · B-box 1.834 · PHD 1.391.

---

# The numbers that qualify the headline

Collected because they are the ones easiest to leave out:

| | |
|---|---|
| **B4** | off MegaScale the head **does not beat zero-shot ESM-2** — 0.361 vs 0.406, 0.400 vs 0.491 |
| **B3** | the interval discards 1,810 of 2,220 point-estimate calls |
| **E1** | `fold_lo ≥ 1` has **4.8 %** sensitivity on pathogenic variants |
| **G2** | coverage is 90 % *on average*; per domain it is 83–95 %, and the quantile varies 1.79× |
| **B5** | the cancer biology is **null** — 1 of 170 genes, 0 of 22 sites |
| **C2** | `head_beats_esm_on_grb2 = False` — binding claims were gated off, not argued down |
| **G1** | the depletion was **mutational bias**, and the claim is withdrawn |
| **H1.0** | the model has never seen a domain longer than **72 residues** |
