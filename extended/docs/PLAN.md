# The plan

**One document. If it conflicts with anything else, this wins.**

Last updated 27 September 2026.

---

## The goal, in one sentence

The 2026-09-22 run is finished and frozen. This phase closes the four objections that stand between
it and a journal submission, using public data that already exists.

| # | Objection a reviewer will raise | Closed by | State |
|---|---|---|---|
| 1 | You only beat zero-shot ESM-2, FoldX and EVE | **E3** | data ready |
| 2 | The B6 depletion could be mutational bias, not selection | **G1**, triangulated by **E1** | data ready |
| 3 | Generality asserted from *n* = 1, twice | **H1**; partly **E2** | E2 done |
| 4 | Nothing was measured | **E1**, **E2**, ultimately **H2** | E2 done |

## The rule that governs everything

> **The frozen run is read-only.** This phase imports the atlas, the trained head and the recorded
> values, and never writes back. `input/frozen/` is `chmod a-w` to make that physical.

Two consequences that decide the order of work:

- **Evaluation-only work cannot change a published number.** New test sets, new baselines, new
  external labels. Safe. That is Phase 1.
- **Training or null-model changes do move headline numbers.** Those run as labelled variants
  *beside* the originals, never instead. Phases 2 and 3.

---

## Phase 1 — evaluation only

### ✅ X0 · acquire the external data — **done** · [doc](X0_acquire_external_data.md)

Domainome v5, ClinVar and gnomAD v4 downloaded, verified by MD5, reduced to the 235 SH3 genes and
joined onto the frozen predictions. 74,116 ClinVar records, 431,959 gnomAD missense variants,
46,128 Domainome SH3 measurements. The join preserves the row count exactly (6,884).

### ✅ E2 · external validation against measured human abundance — **done**

**880 atlas cancer variants have a direct Domainome measurement** across 41 domains and 32 genes.
Pooled |ρ| = **0.600**; all 21 sufficiently sampled domains correlate in the right direction.

**The noise ceiling makes that number meaningful.** Seven SH3 domains were measured by both MegaScale
(proteolysis) and Domainome (abundance). The two assays agree at |ρ| = **0.709**, so 0.600 is near the
achievable limit, not a moderate result. On matched variants the head reaches **90–113 %** of the
ceiling.

Program doc: [E2_domainome_external.md](E2_domainome_external.md). Analysis: `results/E2_domainome_external/ANALYSIS_E2.md`.

### ▶ E1 · ClinVar and gnomAD — **next, start here** · [doc](E1_clinvar_gnomad.md)

Cheapest remaining item, highest value, needs no new data and no GPU.

1. **The pre-registration is drafted** — [preregistration/E1.md](preregistration/E1.md), six
   experiments with the main one fixed in advance. **Three decisions are still open** (Part 5): the
   fallback experiment is unusable, popmax is missing from the data, and the groups are small —
   21 disease-causing variants at the main setting, 4 at the stricter one. Resolve, sign, commit,
   *then* write the notebook.
2. Of ClinVar pathogenic missense variants in SH3 domains, how many are called confidently
   destabilising? Of benign, how many are not?
3. Predicted ΔΔG across four groups: pathogenic / benign / gnomAD-common / COSMIC.
4. Compare the pathogenic-destabilising rate with the 60 % Beltran et al. report.
5. **The germline arm for G1:** are germline-tolerated variants depleted of destabilising
   substitutions the way cancer variants are? This attacks B6's confound without depending on a
   signature model being right.

Already decided in X0 and worth keeping or changing deliberately: 249 ClinVar keys carry contradictory
submissions, collapsed by highest star rating then severity.

### E3 · benchmark against SaProtΔG, ESM3ΔG, ThermoMPNN · [doc](E3_sota_benchmark.md)

**The leakage audit is already done and clean** — none of the 15 held-out domains appear in either
published training split, though 13 are in the underlying measurement set. Report the audit *and its
scope*; claim no more than that.

Needs a GPU runtime, the ESM3 licence accepted on Hugging Face, SaProt 650M, and one structure per
domain (AlphaFold `.cif` is accepted). Checkpoints are archived on the DEU drive and verify 12/12.

Pre-registration drafted — [preregistration/E3.md](preregistration/E3.md), four experiments with
base/measured-constructs/3-seed-average as the main one. **Three decisions open** (Part 5): base vs
augmented is still blank, the measured-construct structures are unconfirmed, and **ThermoMPNN and
ProteinDPO are not actually available for our 15 domains** — the MGnify file covers 26 other
proteins.

### E4 · independent test of the C4 specificity model · [doc](E4_specificity_independent.md)

45 measured affinities across 17 SH3 domains, independent of the PWM data C4 was built from, in
`input/external/binding/kazemein_jasemi_2024_TableS6_Kd.csv`. Expect failure again — a second
*independent* failure is a stronger negative result than one internal failure, and that is the honest
headline.

---

## Phase 2 — labelled variants

Each is reported *beside* the original, never replacing it.

| | | Why |
|---|---|---|
| **G4** | Redesign the F1 panel: one pick per aligned position, one proline | 4 of 10 picks share aligned position 5; 8/10 buried; 4/10 to proline. "Proline in a β-barrel core destabilises" is not a finding. Minutes of compute — **do it before anyone synthesises anything.** |
| **G1** | Signature-aware null for B5 and B6 | Decides whether the 5.9 % vs 9.2 % depletion is selection or mutational bias. GRCh38 is downloaded. Start with the *observed* trinucleotide spectrum; full signature decomposition is the interpretation layer, not a prerequisite. |
| **G2** | Per-domain (Mondrian) conformal intervals | Coverage runs 83.3 % (LYN) to 95.0 % (FYN). Report the new count beside the global 410. |
| **G3** | AlphaFold fragment fix | Recovers 219 variants in nine large proteins, including TRIO Q2579R. Re-runs A2 and everything downstream (~2 h). |

## Phase 3 — generality

**H1 · a second domain family (PDZ).** Two central claims rest on single domains: the ~80-position
threshold on PSD95-PDZ3, every SH3 binding statement on GRB2-SH3. `src/sh3_common.py` is already
family-agnostic; the family-specific logic is the UniProt domain table, the ≥ 50 % identity match to
MegaScale, and the family-holdout split. Converts "we saw a threshold in one domain" into a law.

**H2 · bench validation.** 30 constructs, DSF to screen, CD on anything discordant. Pre-register the
success criterion. Pilot 3 domains first — domains excised from SPTA1, DLG5 and RIMBP2 may not fold in
isolation. Needs G4 done and a collaborator.

---

## Order of work

```
E1  ─ days, no GPU, no new data            ← start here
E4  ─ hours, data in hand
E3  ─ needs GPU + ESM3 licence + structures
G4  ─ minutes
G1  ─ genome downloaded, ready
G2, G3
H1, H2
```

Phase 1 plus rewriting the report as a paper rather than a reproduction record is enough for a
credible submission. Phases 2 and 3 move it up a tier.

---

## Two open defects

1. **NPHP1 (1S1N) and RASA1 (2M51) do not map** between MegaScale and Domainome. Both PDB entries are
   present in the aPCA file, but the recorded offsets do not reconcile their numbering, so their noise
   ceilings are unknown. A mapping bug, not a fact about the domains.
2. **The matched-subset ceilings rest on 19–39 variants.** Indicative, not precise; a ratio above
   100 % is not evidence that the model beats the experiment by a specific margin.

## Conventions carried over

Unchanged, because they are what made the first run defensible: one folder per program under
`results/`; machine-written `RESULTS_<ID>.md` beside a hand-written `ANALYSIS_<ID>.md`; every input
verified by MD5 before use; recorded values so the extended run is itself reproducible; and a
pre-registered decision rule written down **before** any program with a pass/fail verdict.

See also: [DATA.md](DATA.md) and [DATA_PROVENANCE.md](DATA_PROVENANCE.md) for the data, [SYNC.md](SYNC.md) for keeping
local and Drive in step.
