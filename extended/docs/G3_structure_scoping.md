# G3 — Scoping the AlphaFold structural gap

**Status: scoped 28 September 2026, and dropped.** The premise did not survive.

**Why it was scoped first.** G3 was the last Phase-2 item and the only one that would have re-run a
frozen output — about two hours, re-running A2 and everything downstream. Every extended program so
far has held the property that the frozen run is read-only, so the cost of breaking it deserved a
check before it was paid.

**What it does not do.** Nothing was re-run, and nothing was fetched into the project. The AlphaFold
DB queries were metadata reads — HTTP HEAD on the file URLs and the public prediction API.

## What the plan claimed

> **G3 · AlphaFold fragment fix.** Recovers 219 variants in nine large proteins, including TRIO
> Q2579R. Re-runs A2 and everything downstream (~2 h).

Three claims. The first two are wrong and the third is misleading.

## Inputs

| | |
|---|---|
| `alphafold_log.csv` (A2) | A2's own record of why each fetch failed |
| `atlas_predictions.parquet` | `has_structure`, per variant |
| `SH3_cancer_master.tsv` | domain boundaries, protein lengths |
| AlphaFold DB API | `alphafold.ebi.ac.uk/api/prediction/{acc}` — metadata only |

## What it found

### 1. It is not a fragment problem

A2 logs **all nine proteins as `not available`**, meaning the download failed outright and the
residue filter that would have produced an empty frame never ran. Probed directly, `AF-{acc}-F1`
returns **404 for F1 and F2, on both v4 and v6**, for every one.

The API gives two causes, neither of them fragmentation:

- **Four proteins have no AlphaFold model at all** — OBSCN (7,968 aa), NEB (8,525), PLEC (4,684),
  MACF1 (7,388). No code change recovers them.
- **Five are keyed to an isoform-suffixed entity id** — `AF-P15924-2-F1`, `AF-O75962-5-F1`,
  `AF-Q03001-3-F1`, `AF-O60229-6-F1`, `AF-Q9UKN7-2-F1`. A2 only ever tries the canonical accession.

**The missing isoform suffix is the one genuine defect**, and it is the third isoform-numbering bug in
this project: X1's ClinVar shortfall and G1's null pool were both the same class — an identifier that
looks canonical resolving to an isoform with different numbering.

### 2. It would recover 72 variants, not 219

A model existing is not a model covering the domain.

| recoverable | TRIO d1 (28), DSP (22), DST (22) | **72** |
|---|---|---|
| model stops short | TRIO d2 (26), MYO15A (26), KALRN d1+d2 (8) | 60 |
| no model at all | OBSCN (38), PLEC (27), NEB (12), MACF1 (10) | 87 |

And the 72 are reachable only after an isoform-to-canonical alignment — the step that produced the
three defects above.

**TRIO Q2579R, the variant the task was justified by, sits at residue 2579 in TRIO domain 2, which the
model does not cover.**

### 3. It would change no prediction

A2 keeps structure out of the model deliberately, and says so: *"A model using structure would train
on one distribution and predict on another. Keeping structure out also makes B2 an independent
test."* The 1,292 features are 1,280 ESM-2 embedding dimensions plus twelve non-structural scalars.

**No ΔΔG, no `fold_lo`, no conformal interval and no count of 410 would move.** What would change is
burial annotation on at most **1.0 %** of the atlas.

## What the gap costs today

| | |
|---|---|
| Atlas variants without structure | 219 of 6,884 (**3.2 %**), 11 domains |
| Of those, destabilising | 18 |
| Destabilising **and** non-hypermutated | 5 |
| In the G4 experimental panel | **1** — OBSCN L5623Q |

OBSCN has no AlphaFold model at all, so G3 would not have fixed the one case that currently costs
anything.

## Outputs

| | |
|---|---|
| `results/G3_structure_scoping/ANALYSIS_G3.md` | the full scoping study |
| correction at the top of `results/A2_features/ANALYSIS_A2.md` | its stated diagnosis was the wrong one |

## Decision

**Dropped.** Recorded as a limitation instead: 3.2 % of the atlas has no structural annotation because
AlphaFold DB has no model for those proteins, or only an isoform model too short to reach the domain.
That is a fact about the database, not a task.

If the 72 are ever wanted, the work is an isoform-to-canonical alignment per protein, with the
verification G1 ended up needing — confirm the residue at each mapped position matches the canonical
sequence before trusting a coordinate.

## Runtime

Minutes, entirely in metadata queries. **Phase 2 closes without any frozen output having been
recomputed.**
