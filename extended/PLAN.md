# SH3 extended — research plan

**Goal.** Take the completed study in `sh3 updated` (187/187 recorded values reproduced, 2026-09-22) from
"a good thesis" to "a paper a specialist journal will accept", by closing the four objections a reviewer
will raise, using data that already exists and is public.

**Non-goal.** Improving the folding head's ρ. 0.839 with 15/15 wins is enough, and an unchanged value is
what makes the reproduction convincing.

---

## The governing rule

> **The 2026-09-22 run is frozen. Nothing in this project modifies it.**

The extended study imports three things as **immutable inputs** — the atlas
(`SH3_cancer_master.tsv`, MD5 `cef897f4dd25f9cd56f2c40bb7ec0b08`), the trained folding head, and
`reference/expected_values.json` — and never rebuilds them. Every new program writes its own results
folder, its own metrics file and its own recorded values.

Two corollaries that decide what goes in which phase:

- **Evaluation-only additions change no headline number.** New test sets, new baselines, new external
  labels. These are safe and they are Phase 1.
- **Training or null-model changes do change headline numbers.** These run as clearly labelled variants
  *beside* the original, never in place of it. Phase 2 and 3.

---

## Phase 1 — evaluation only (nothing you already published can move)

### E1 · External validation against ClinVar and gnomAD
**Inputs:** frozen atlas + B3 destabilising calls; dbNSFP v5.4a or (ClinVar `variant_summary` + gnomAD API).

Join the 410 confidently destabilising calls, and the full 6,884-variant atlas, to ClinVar significance
and gnomAD allele frequency at the protein-position level.

Report:
- Of ClinVar pathogenic/likely-pathogenic missense variants inside human SH3 domains, how many are called
  confidently destabilising (recall), and of benign/likely-benign, how many are not (specificity).
- The predicted ΔΔG distribution for pathogenic vs benign vs gnomAD-common (AF > 0.1 %) vs COSMIC.
- Compare your pathogenic-destabilising rate against the 60 % reported by Beltran et al. 2025.

**Pre-register before running:** the ClinVar star-rating floor (recommend ≥ 2 stars, i.e. multiple
submitters, no conflicts) and the gnomAD AF threshold. Write them down first. The C4 lesson applies:
a rule chosen after seeing the answer is not a rule.

**This is the single best value-for-effort item in the whole plan** — days of work, no new model, and it
converts 410 predictions into a validated set.

### E2 · Human Domainome as an external test set
**Inputs:** frozen head; Zenodo 11493742 Supplementary Tables 1, 2, 5.

**Gate:** only proceed if Supplementary Table 1 contains SH3 domains. Check this first; it is 792 bytes.

If it does:
- Predict with the frozen head on every Domainome SH3 variant, correlate against the aPCA fitness score
  per domain. These are *human* domains, so this is a genuinely out-of-distribution test of a model
  trained on MegaScale.
- **The conformal test, which is the real prize:** what fraction of Domainome measurements fall inside
  the 90 % intervals? This is the first actual test of the exchangeability assumption behind Limitation 3.
  Report observed coverage against the promised 90 %.
- Free extra baselines: Supplementary Table 5 already carries EVE, popEVE and Tranception scores for the
  same variants.

State plainly that aPCA measures abundance, not ΔΔG in kcal/mol, and that B4 showed the head is weaker on
abundance assays. Treat it as a rank test.

### E3 · Benchmark against the state of the art
**Inputs:** frozen head + 15 held-out SH3 domains; SaProtΔG and ESM3ΔG weights; ESMtherm.

Run each predictor on the same 15 held-out domains and report per-domain ρ side by side with 0.839.

**Do the leakage audit first and report it whatever it says.** The MGnify Stability dataset contains SH3
domains (CATH 2.30.30.40). If SaProtΔG or ESM3ΔG saw any of your 15 test domains in training, the
comparison is void for those domains and you say so in the table.

Possible outcome: they beat you. That is fine and you report it. Your contribution is the mechanism
separation and the positional-coverage limit, not the leaderboard position — and a better folding
predictor makes the 410 calls better, so E1's validation improves either way.

### E4 · Independent test of the C4 specificity model
**Inputs:** C4 model; Kazemein Jasemi 2024 supplementary tables (45 measured pairs, 25 SH3 domains).

C4 failed its own pre-registered rule (centred r +0.288, 55/115 wins) and was validated only against the
PWM data it was built from. 45 independent affinity measurements across 25 domains is a real external
check. Predict, correlate, report. Expect it to fail again; a second independent failure is a *stronger*
negative result than one internal failure, and that is the honest headline.

---

## Phase 2 — labelled variants (headline numbers may move; both versions are reported)

### G1 · Signature-aware null for B5 and B6
**Inputs:** COSMIC SBS signatures; GRCh38 FASTA for trinucleotide context; existing virtual saturation scan.

Replace the single-nucleotide-reachability null with one that weights each possible substitution by
trinucleotide context and codon usage, weighted by the mutational signatures active in the tumours each
variant came from. Re-run B5 and B6 **beside** the current null, never instead of it.

This decides whether the 5.9 % vs 9.2 % depletion — your most interesting biological finding — is
purifying selection or mutational bias. Right now the claim must stay hedged, and a reviewer will say so.

Triangulate with E1's gnomAD arm: germline-tolerated variants give a second, model-free handle on the
same question.

### G2 · Per-domain (Mondrian) conformal intervals
Coverage currently ranges 83.3 % (LYN) to 95.0 % (FYN), and 86.9 % above 2 kcal/mol. Calibrate per domain
with a fallback to the global quantile for small domains. The destabilising count will shift; report it
beside the global 410, and use E2's Domainome coverage as the external check.

### G3 · AlphaFold fragment fix
Fetch the fragment containing the SH3 domain, not only fragment F1. Recovers 219 variants in nine large
proteins (TRIO, OBSCN, PLEC, MYO15A, DSP, DST, NEB, MACF1, KALRN), including TRIO Q2579R, one of the most
recurrent non-hypermutated variants. Re-runs A2 (~25 min) and everything downstream, so schedule it as a
block. Small changes to B2/B5 coverage.

### G4 · Redesign the experimental panel
Cap the panel at one pick per aligned position and one substitution to proline. The current panel puts
4 of 10 picks at aligned position 5, covers 6 of 56 positions, is 8/10 buried and 4/10 to proline — a
reviewer will call it stacked, and "proline in a β-barrel core is destabilising" is not a finding.

Minutes of compute. **Do it before anyone synthesises anything**, because the panel you order is the panel
you are stuck with.

---

## Phase 3 — generality (the expensive one)

### H1 · A second domain family
Run the pipeline end to end on PDZ. Two central claims currently rest on single domains: the ~76–82
position threshold comes from PSD95-PDZ3 alone, and every SH3 binding statement comes from GRB2-SH3 with
one ligand. Two separate *n* = 1s.

PDZ is the right choice because PSD95-PDZ3 already has both ddPCA folding *and* binding energies in data
you hold, and it is the domain C3 was calibrated on.

The code is more portable than it looks: `src/sh3_common.py` is already family-agnostic (one mention of
SH3, in the docstring). The family-specific logic sits in the atlas builder — the UniProt domain table
(an input file, so swappable), the ≥ 50 % identity match to MegaScale structures, and the ddPCA domain
names — plus the family-holdout split in the B-series. Parameterise two notebooks, then pay compute time
for a full A2 embedding run and retraining.

What it converts: *"we saw a threshold in one domain"* → *"positional coverage is the binding-learnability
bottleneck across families, at a scale of order 80 positions."* The second is a law, and the law is what
makes a negative result worth publishing well.

### H2 · Bench validation of the redesigned panel
Needs a collaborator. 30 constructs (10 wild-type, 10 picks, 10 same-domain controls), DSF to screen, CD
on anything discordant. Pre-register the success criterion before measuring. Pilot 3 domains first —
domains excised from SPTA1, DLG5 and RIMBP2 may not express or fold in isolation.

This is the only item that changes the *kind* of evidence the paper rests on.

---

## Dependencies

```
E1 ─┐
E2 ─┼─→ all independent, run in any order, all evaluation-only
E3 ─┤
E4 ─┘
        G1 ← needs COSMIC signatures; triangulates with E1's gnomAD arm
        G2 ← external check comes from E2
        G3 ← re-runs A2 and everything downstream; schedule as a block
        G4 ← independent, minutes, do it early
                H1 ← independent of everything above, biggest compute
                H2 ← needs G4 done and a collaborator
```

---

## How each item maps to the four publication blockers

| Blocker | Closed by |
|---|---|
| Baseline is a strawman (only zero-shot ESM-2, FoldX, EVE) | **E3** |
| Depletion confounded by mutational bias | **G1**, triangulated by **E1** |
| Generality asserted from *n* = 1, twice | **H1**; partly **E2** |
| Nothing was measured | **E1** and **E2** (computational validation), **H2** (actual measurement) |

---

## Conventions carried over from the original project

Unchanged, because they are what made the first run defensible:

- One folder per program under `results/`, named in `PROGRAM_DIRS`.
- Each program writes `RESULTS_<ID>.md` (machine-written, no hand-typed numbers),
  `metrics_<ID>.json` (metrics + run metadata), `comparison_<ID>.csv` (this run vs recorded), and a
  hand-written `ANALYSIS_<ID>.md` (what it means, limitations, what was fixed, what is next).
- Every input verified by MD5 before use; the notebook stops if a file does not match.
- Recorded values in `reference/expected_values_ext.json` so the extended run is itself reproducible.
- Pre-registered decision rules written down **before** the run, for every program that has a pass/fail
  verdict. C4 is the reason this rule exists.
- COSMIC-derived per-variant tables are never committed or published.

## Folder layout

```
SH3 extended/
├── PLAN.md               this file
├── DOWNLOADS.md          verified sources, sizes, licences, the disk-space rule
├── notebooks/            generated Colab notebooks, one per program
├── src/                  sh3_common.py (imported unchanged) + extensions
├── tools/                nb_E.py, nb_G.py, nb_H.py — notebook definitions
├── reference/            checksums_ext.md5, data_manifest_ext.json, expected_values_ext.json
├── input_new/            downloads; gitignored, never committed
│   ├── stability/        Domainome, MGnify
│   ├── clinical/         ClinVar, gnomAD, dbNSFP, GENIE
│   ├── signatures/       COSMIC SBS, GRCh38 context
│   └── binding/          Kazemein Jasemi tables
├── results/              one folder per program
└── docs/                 per-program documentation, the extended report
```

Drive layout for Colab mirrors it at `MyDrive/sh3_extended/`, with the frozen atlas and head read from
the original `MyDrive/sh3_repro/results/`.

---

## Suggested order

1. **G4** — minutes, and it unblocks any conversation with a wet lab.
2. **E1** — days, best value in the plan, no new model.
3. **E2** — gated on the 792-byte Supplementary Table 1 check.
4. **E3** — the leakage audit is the slow part, not the inference.
5. **G1** — the hedge that most weakens the paper.
6. **G2**, **G3**, **E4**.
7. **H1**, then **H2** if a collaborator materialises.

Phase 1 alone, plus rewriting the report as a paper rather than a reproduction record, is enough for a
credible submission. Phases 2 and 3 are what move it up a tier.
