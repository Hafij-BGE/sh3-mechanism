# Status and next plan — 27 September 2026

## Where the project stands

The frozen run (A0–D1, F1, F2; 187/187 recorded values) is untouched. Phase 1 of the extended study
is **two programs in**, and both produced results.

| Program | State | Headline |
|---|---|---|
| **X0** acquire external data | **done** | Domainome, ClinVar (74,116 records in the 235 genes), gnomAD v4 (431,959 missense) — all joined onto the atlas without expanding a single row |
| **E2** external validation | **done** | 880 atlas cancer variants have a direct Domainome measurement; pooled \|ρ\| = 0.600, 21/21 domains in the right direction |
| **E2 noise ceiling** | **done** | assay-to-assay ceiling is **0.709**; on matched variants the model reaches **90–113 %** of it |
| E1 ClinVar/gnomAD | data ready | not started |
| E3 SOTA benchmark | data ready | not started |
| E4 independent C4 test | data ready | not started |
| G1–G4, H1–H2 | — | Phase 2/3 |

### What E2 actually established

A model trained on MegaScale proteolysis with the **entire SH3 family held out** predicts cellular
abundance for 880 real COSMIC cancer variants it never saw, at close to the limit set by experimental
noise. Two independent experiments measuring the same variants agree only at ρ ≈ 0.71, so 0.600 is not
a moderate result — it is near the ceiling.

This also corrected an earlier misreading: HCK looked like the model's worst domain (0.339), but on
matched variants its ceiling is 0.593 and the model reaches 0.604. The weakness was in *which*
variants were compared, not in the predictor.

---

## Data: complete

`input/` verifies **39 / 39**, 5.1 GB, nothing missing.

| | |
|---|---|
| `external/domainome/` | tables + `analysis_files/` + the R notebooks that decode them |
| `external/stability/` | MGnify ΔG (2.1 GB), training index, splits, benchmarks |
| `external/clinical/` | ClinVar |
| `external/signatures/` | COSMIC v3.6 SBS96 GRCh38 |
| `external/genome/` | GRCh38 primary assembly — **complete**, 881,964,081 bytes, valid gzip |
| `external/binding/` | Kazemein Jasemi 2024 — **45 Kd measurements, 17 SH3 domains, 0.2–125 µM** |
| `frozen/` | atlas, B3, B1, F1 copies, write-protected |

**dbNSFP is still pending and no longer matters.** ClinVar and gnomAD are both in hand from primary
sources, so E1 is unblocked. If the access code arrives, use it for extra predictor scores only.

---

## Next: three programs, all unblocked

### E1 — ClinVar and gnomAD validation *(do this first)*

The cheapest remaining item and the one that most strengthens the paper. Everything is downloaded.

1. **Pre-register the rule before looking.** ClinVar star floor (recommend ≥ 2: multiple submitters,
   no conflicts) and the gnomAD AF threshold for "common". Write them down first — C4 is why.
2. Of ClinVar pathogenic missense variants in SH3 domains, how many are called confidently
   destabilising? Of benign, how many are not?
3. Predicted ΔΔG across four groups: pathogenic / benign / gnomAD-common / COSMIC.
4. Compare the pathogenic-destabilising rate against the 60 % Beltran et al. report.
5. **The germline arm for G1:** are germline-tolerated variants depleted of destabilising substitutions
   in the same way the cancer variants are? This attacks the B6 confound without depending on a
   signature model.

Note the conflict rule already used in X0: 249 ClinVar keys carry contradictory submissions, collapsed
by highest star rating then severity. Keep or change that deliberately.

### E3 — benchmark against SaProtΔG, ESM3ΔG, ThermoMPNN

The leakage audit is **already done and clean**: none of the 15 held-out domains appear in either
published training split, though 13 are in the underlying measurement set. Report the audit and its
scope; do not claim more.

Needs: a GPU runtime, the ESM3 licence accepted on Hugging Face, SaProt 650M, and a structure per
domain (AlphaFold `.cif` is accepted — `examples/` in the repo confirms it). The checkpoints are
archived on the DEU drive and verify 12/12, so no re-download.

Decide **base or augmented** before running, on a stated reason, and report the other only as a
labelled sensitivity check.

### E4 — independent test of the C4 specificity model

`binding/kazemein_jasemi_2024_TableS6_Kd.csv` is ready: 45 affinities over 17 domains, independent of
the PWM data C4 was built from. Expect it to fail again — a second independent failure is a *stronger*
negative result than one internal failure, and that is the honest headline.

### Then Phase 2

G4 (panel redesign, minutes) → G1 (signature-aware null; the genome is now in place) → G2, G3.

---

## Two open defects

1. **NPHP1 (1S1N) and RASA1 (2M51) do not map** between MegaScale and Domainome. Both PDB entries are
   present in the aPCA file, but the recorded offsets do not reconcile their numbering, so their noise
   ceilings are unknown. A mapping bug to fix, not a fact about the domains.
2. **The matched-subset ceilings rest on 19–39 variants.** Indicative, not precise. A ratio above
   100 % should not be read as the model beating the experiment by a specific margin.

---

## Still to upload to Drive

Local and Drive are otherwise in sync. Missing on Drive:

| Upload | into `sh3_repro/extended/` | Size |
|---|---|---|
| `input/external/genome/Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz` | `input/external/genome/` | **842 MB** |
| `input/external/binding/` (whole folder) | `input/external/` | 18 MB |
| `reference/checksums_ext.md5` — **Drive's copy is stale** (35 entries; local has 39) | `reference/` | 4 KB |
| `results/E2_domainome_external/noise_ceiling_E2.csv`, `noise_ceiling_matched_E2.csv`, `ANALYSIS_E2_noise_ceiling.md` | `results/E2_domainome_external/` | small |
| `tools/nb_X.py`, `e2_domainome_validation.py`, `e2_noise_ceiling.py` | `code/` | small |
| `PLAN.md`, `DOWNLOADS.md`, `README.md`, `SYNC.md`, `UPLOAD_LIST.md`, `STATUS.md` | `docs/` (currently empty) | small |

The genome is only needed by G1, so it can wait if bandwidth is short. Everything else is small.

After uploading, verify in a Colab cell:

```python
%cd /content/drive/MyDrive/sh3_repro/extended
!md5sum -c reference/checksums_ext.md5
```

Expect **39 OK**.
