# The plan

**One document. If it conflicts with anything else, this wins.**

Last updated 27 September 2026 (after E1, E3 and E4).

---

## The goal, in one sentence

The 2026-09-22 run is finished and frozen. This phase closes the four objections that stand between
it and a journal submission, using public data that already exists.

| # | Objection a reviewer will raise | Closed by | State |
|---|---|---|---|
| 1 | You only beat zero-shot ESM-2, FoldX and EVE | **E3** | **closed** — level with SaProtΔG, better than ESM3ΔG (p = 0.0084) |
| 2 | The B6 depletion could be mutational bias, not selection | **G1** alone — E1 could not | data ready |
| 3 | Generality asserted from *n* = 1, twice | **H1**; partly **E2** | E2 done |
| 4 | Nothing was measured | **E1**, **E2**, ultimately **H2** | **both done** |

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

### ✅ E1 · ClinVar and gnomAD — **done** · [doc](E1_clinvar_gnomad.md)

Judged against [preregistration/E1.md](preregistration/E1.md), signed and committed before the
notebook existed. Analysis: `results/E1_clinvar_gnomad/ANALYSIS_E1.md`.

**Q1 — do the predictions track pathogenicity? Yes, decisively.** 21 pathogenic against 101 benign
ClinVar variants inside SH3 domains: median predicted ΔΔG **1.67** against **0.19** kcal/mol,
Mann–Whitney p = **4.9 × 10⁻⁶**, rank-biserial **+0.615**. Holds with the star filter relaxed. The
head has never seen a clinical label, so this is the project's strongest external validation of the
ranking.

**The binary call is a different story, and it is a limitation to report.** `fold_lo ≥ 1` flags
**4.8 %** of pathogenic variants against 1.0 % of benign (Fisher p = 0.32, no verdict) — against the
~60 % Beltran et al. report. The conformal lower bound answers "certainly destabilising", so it is
conservative by construction. Report ΔΔG with its interval; do not present `fold_lo ≥ 1` as a
clinical filter without stating its sensitivity in the same sentence.

**Q2 — germline depletion: right direction, not significant.** 0 of 35 common variants
(popmax > 1 %) are destabilising against 9.6 % expected, p = **0.0289** against the pre-registered
α = 0.025. Missed by 0.004, so the verdict is *consistent with depletion, not established*. Even
perfect depletion cannot clear the bar at n = 35, so **E1 cannot triangulate B6 — G1 is the only
route left to objection 2.**

Two bookkeeping notes: 25 benign variants dropped against the pre-registered count of 126, all in
large multi-isoform proteins where ClinVar's transcript numbers residues differently from UniProt
canonical (0 pathogenic dropped, so no bias toward the hypothesis); and the ClinVar star threshold
affects only Q1 while the frequency threshold affects only Q2, so each question has one genuinely
independent corroborating arm, not four.

### ▶ X1 · reduce dbNSFP 5.4a to the SH3 domains — **notebook ready to run**

dbNSFP arrived on 27 September, after §9 of the provenance had written it off. Nothing was blocked by
its absence, so this is an addition.

**It predicts pathogenicity, not ΔΔG**, so it is *not* an E3 competitor — that table is for stability
predictors. It is the external comparison for **E1**. dbNSFP ships its own ClinVar benchmark: on all
genes, star 1+ missense, MetaRNN reaches **AUC 0.988**, REVEL 0.976, AlphaMissense 0.964. E1 put our
stability head at rank-biserial +0.615, i.e. **AUC ≈ 0.81**.

So the question worth asking is **not** whether a folding model beats dedicated pathogenicity
predictors — it should not, and nothing in this project claims it would. It is whether **ΔΔG_fold adds
anything they do not have**, on the same variants. That would be a new program with its own
pre-registration; X1 only acquires and reduces, and deliberately computes no comparison.

Two practical notes: the release ships **no tabix index**, so the subset costs one streaming pass
(cached, paid once); and the two large files are ~100 GB together and are probably the same release
twice — X1 §1 checks that cheaply and says whether one can be deleted.

### ✅ E3 · benchmark against SaProtΔG and ESM3ΔG — **done** · [doc](E3_sota_benchmark.md)

Judged against [preregistration/E3.md](preregistration/E3.md) @ `ccd3446`. Analysis:
`results/E3_sota_benchmark/ANALYSIS_E3.md`.

| competitor | median ρ | ours | diff | p | verdict |
|---|---|---|---|---|---|
| SaProtΔG | +0.855 | +0.839 | −0.028 | 0.107 | **no clear difference** |
| ESM3ΔG | +0.792 | +0.839 | +0.033 | **0.0084** | **ours better** |

27,590 variants scored by each, **0 dropped**. **Our head is sequence-only and saw no SH3 domain in
training; both competitors receive the measured construct's experimental structure.** On that footing
we are indistinguishable from one and ahead of the other.

**Consistency is the real finding.** ESM3ΔG ranges 0.460–0.892 across domains; we range 0.754–0.934.
Our worst domain beats its fifth-worst. The 410 confident calls in B3 depend on behaving similarly
across domains, not on a good average.

**Not a claim of state of the art:** SaProtΔG is nominally ahead on 11 of 15, and 15 domains cannot
resolve a 0.03 gap — stated in the plan before any result.

**The leakage audit stands on its own:** SaProtΔG 0 of 15, ESM3ΔG 0 of 15, **ThermoMPNN 13 of 15** —
23,191 of 27,590 held-out variants inside its own train or val split.

Outstanding: ThermoMPNN (descriptive only; import fixed, now a position-offset bug, also fixed) and
Experiments 2–4. All scans are cached, so each costs only its own new work.

### ✅ E4 · independent test of the C4 specificity model — **done** · [doc](E4_specificity_independent.md)

Judged against [preregistration/E4.md](preregistration/E4.md), committed before the notebook.
Analysis: `results/E4_specificity_independent/ANALYSIS_E4.md`.

**Both verdicts are no, and the control says why.** The model scores r = **+0.023** (p = 0.91) on the
within-domain-centred main test and does not beat the domain-agnostic baseline. But the **observed**
phage-display profile — the quantity the model is trained to predict — fails identically
(r = −0.051, p = 0.80). By the reading fixed in advance, that makes this **the measurement, not the
model**: a predictor of X cannot beat X, so no improvement to C4's regression could have produced a
positive result here.

**The representation is the limit.** Collapsing a 14-position PWM to composition discards order, and
SH3 ligand classes differ by order (class I `+xΦPxΦP` vs class II `ΦPxΦPx+`) at identical composition.
Two further numbers: the model's score correlates **+0.82** with the domain-agnostic baseline and 70 %
of its spread is peptide-driven, so the predictions are also shrunk hard toward the family mean — C4's
internal verdict from another angle.

**The re-run reproduced C4 to 1.6 × 10⁻¹⁴**, so the predictions scored are exactly the ones
`validated: false` came from.

What this licenses: *44 independently measured affinities give no support to the compositional
specificity axis, and the failure is the representation rather than the fit.* What it does not: "C4's
model is wrong" — the control cannot separate that from "composition is the wrong representation".

---

## Phase 2 — labelled variants

Each is reported *beside* the original, never replacing it.

| | | Why |
|---|---|---|
| ~~**G4**~~ | ~~Redesign the F1 panel~~ | **Done, 28 Sep** — `extended/results/G4_panel/`. 10 distinct aligned positions (was 6, with 5 picks at one), 1 proline (was 4), 3 exposed picks and 5 buried controls, so the positive and negative sets no longer differ in burial as well as in predicted effect. Unblocks H2. |
| ~~**G1**~~ | ~~Signature-aware null for B5 and B6~~ | **Done, 28 Sep — mutational bias.** The depletion does not survive: 5.96 % observed vs 6.04 % expected, p = 0.40, two spectra agreeing. The frozen claim is withdrawn. Originally: GRCh38 is downloaded. Start with the *observed* trinucleotide spectrum; full signature decomposition is the interpretation layer, not a prerequisite. |
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
Phase 1 is done: X0, E1, E2, E3, E4 all reported.   X1 adds dbNSFP.

G1  ─ DONE 28 Sep. The depletion did not survive a context-matched null;
      the frozen claim is withdrawn. See extended/results/G1_mutational_context/
G4  ─ DONE 28 Sep. Panel rebuilt; H2 unblocked.
G2, G3                                              ← start here
H1, H2

optional, all cached so each costs only its own work:
E3 Experiments 2-4, and the ThermoMPNN descriptive arm
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

See also: [OUTCOMES.md](OUTCOMES.md) for what this phase changed against the frozen run,
[DATA.md](DATA.md) and [DATA_PROVENANCE.md](DATA_PROVENANCE.md) for the data, [SYNC.md](SYNC.md) for
keeping local and Drive in step.
