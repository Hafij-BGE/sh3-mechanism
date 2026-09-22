# Pipeline overview

**Thesis.** For a cancer missense mutation in a human SH3 domain: does it destabilise the fold,
or leave the fold intact and change binding? The pipeline builds the evidence in four parts.

```
RAW DATA ──► A. Initial data processing ──► B. Main task: loss of fold ──► D. Figures + verification ──► F. Follow-up
                                         └─► C. Why binding cannot be predicted ─┘
```

| Part | Program | One-line purpose |
|---|---|---|
| **A** Initial data processing | A0 | Cancer atlas from raw COSMIC + a frozen UniProt snapshot (Stage 0) |
| | A1 | Measured folding and binding energies, sign-checked in vitro (Stage 1) |
| | A2 | 1,292 features per variant; structure for validation only (Stage 2) |
| **B** Main task (subtasks) | B1 | Folding predictor, tested on SH3 families it never saw |
| | B2 | Structural check: damage follows burial, not the interface |
| | B3 | Conformal intervals and a mechanism call for every atlas variant |
| | B4 | External validation on ProteinGym: where the predictor stops working |
| | B5 | Cancer biology: does predicted damage explain where mutations fall? |
| | B6 | Virtual saturation mutagenesis of every atlas SH3 domain *(roadmap extension)* |
| **C** Why binding cannot be predicted | C1 | Across domains: fails, and why the design could not work |
| | C2 | Within one domain: PDZ3 learnable, GRB2-SH3 not; single fits are unstable |
| | C3 | Positions, not rows: about 80 positions needed, an SH3 has 56–60 |
| | C4 | An ESM-independent specificity axis from experimental PWMs *(roadmap extension)* |
| **D** | D1 | Figures, reproduction report, one-page summary |
| **F** Follow-up | F1 | Experimental validation candidates from frozen outputs *(roadmap N1–N3; optional)* |
| | F2 | Figures for the F1 panel: pick-vs-control intervals, atlas context, position on the fold |

**Run order:** A0 → A1 → A2 → B1 → B2 → C1 → C2 → C3 → B3 → C4 → B4 → B5 → B6 → D1 → (F1 → F2).
B3 comes after Part C because the choice of binding axis depends on C2. B4 needs only B1 and can run any
time after it. F1 and F2 read results only and change nothing upstream.

## Rules that hold everywhere

- **Sign convention:** positive ΔΔG = destabilising or weaker binding. MegaScale is negated on load.
- **Cross-validation groups:** UniProt accession + domain index, never gene or variant. SPTAN1 alone has
  eight MegaScale structures.
- **Files, not variables:** every program reads only files written by earlier programs, so any one can be
  re-run alone in a fresh Colab session.
- **Nothing typed by hand:** every `RESULTS_<ID>.md` is written by its notebook from that run's numbers.
- **Checks against the original run:** 187 recorded values in `reference/expected_values.json`.

## What was changed on re-checking, and why

| Finding | Where | What the new pipeline does |
|---|---|---|
| Binding CV used unshuffled `GroupKFold`, so "repeats" shared one partition | C2, C3 | Both modes run side by side: `original` reproduces the old numbers, `corrected` shuffles |
| Stage 3's cross-domain binding head stopped training on the test domain (leakage) | C1 | `original` kept for the record; `corrected` uses an inner split of the training domains |
| Seed-spread "confidence" filter passed 6,880 of 6,884 variants | B3 | Conformal intervals only; the old filter is shown as a documented failure |
| UniProt queried live, so a re-run could see a different release | A0 | Frozen 2026-09-20 snapshot, MD5-checked |
| Truncated COSMIC genome-screens copy (1.35 of 16.8 GB) | A0 | MD5 check; the compressed original is streamed, never unpacked |
| Stage 0 scripts had hard-coded and stale paths | A0 | `src/sh3_atlas.py`, all paths as arguments |
| 3e's "leverage" flag | C3 | Reported with the enrichment table, which shows it is a base-rate artefact |

Stage 0 has already been verified locally: the rebuilt atlas is **byte-identical** to
`SH3_cancer_master_v3.tsv` (MD5 `cef897f4…`), and so is the rejected-rows file.

## Found during the full Colab run (2026-09-22) and fixed

| Finding | Where | Fix |
|---|---|---|
| FoldX files use PDB numbering (GB1 +1, PDZ3 +310) but were joined by raw residue number | A1, B1 | B1 derives each offset from the wild-type residues; FoldX vs measured r 0.494 → 0.418 |
| "Beats ESM" compared absolute values, so wrong-direction correlations counted as wins | C1, C2 | signed comparison; C1 1/3 → 0/3; C2's binding decision made safe |
| Learning-curve table split one budget into two rows | C3 | grouped by positions only; the value now matches the record |
| Tolerance 10⁻⁹ on a quantity that depends on tie ordering | B3 | tolerance 10⁻⁶, reason recorded in `expected_values.json` |

## Where to read what

| You want | Read |
|---|---|
| How a program works and why | `docs/<ID>_*.md` |
| The numbers of a run | `results/<ID>_*/RESULTS_<ID>.md` (written by the notebook) |
| What the numbers mean | `results/<ID>_*/ANALYSIS_<ID>.md` (interpretation, limitations, next step) |
| The whole run on one page | `results/RESULTS_SUMMARY.md` and `results/D1_figures_and_verification/ANALYSIS_D1.md` |
| How to upload and run | `UPLOAD_GUIDE.md` |
| How to put it on GitHub | `GITHUB_GUIDE.md` |
| Which roadmap items are in | `docs/UPGRADE_ROADMAP_STATUS.md` |
