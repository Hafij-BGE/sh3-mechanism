# G3 — scoping: the AlphaFold gap is not a fragment bug, and the fix recovers a third of what was claimed

Run 28 September 2026. **Nothing was re-run and nothing was fetched into the project.** This is a
scoping study of a planned task, done because that task was the only remaining item that would have
touched frozen outputs and cost about two hours.

**Recommendation: do not run G3 as scoped.** Record the gap as a limitation instead.

---

## What the plan said

> **G3 · AlphaFold fragment fix.** Recovers 219 variants in nine large proteins, including TRIO
> Q2579R. Re-runs A2 and everything downstream (~2 h).

Three claims, and the first two are wrong.

## 1. It is not a fragment problem

A2 fetches `https://alphafold.ebi.ac.uk/files/AF-{acc}-F1-model_{v}.cif`, trying v6, v5 then v4, and
logs `not available` when all three fail. All nine proteins are logged **`not available`** — so the
download failed outright, and the residue filter that would have produced an empty frame never ran.

Probed directly, every one of those URLs returns **404 for F1 and F2, on both v4 and v6.** The
AlphaFold DB API explains why:

| gene | accession | AlphaFold model entity | model spans to |
|---|---|---|---|
| DSP | P15924 | **`AF-P15924-2-F1`** | 2272 |
| DST | Q03001 | **`AF-Q03001-3-F1`** | 2649 |
| TRIO | O75962 | **`AF-O75962-5-F1`** | 2563 |
| KALRN | O60229 | **`AF-O60229-6-F1`** | 1257 |
| MYO15A | Q9UKN7 | **`AF-Q9UKN7-2-F1`** | 797 |
| OBSCN | Q5VST9 | *none* | — |
| PLEC | Q15149 | *none* | — |
| NEB | P20929 | *none* | — |
| MACF1 | Q9UPN3 | *none* | — |

Two distinct causes, neither of which is fragmentation:

- **Four proteins have no AlphaFold model at all.** OBSCN (7,968 aa), NEB (8,525), PLEC (4,684) and
  MACF1 (7,388) are absent from the database. No code change recovers them.
- **Five are keyed to an isoform-suffixed entity id** — `P15924-2`, not `P15924` — so the canonical
  accession 404s. A2 never tried the suffixed form.

**This is the third isoform-numbering defect in this project.** X1's ClinVar shortfall and G1's null
pool were both traced to the same class of problem: an identifier that looks canonical, resolving to
an isoform with different numbering. It is worth naming as a pattern rather than fixing three times.

## 2. It would recover 72 variants, not 219

A model existing is not the same as a model covering the SH3 domain. The atlas numbers residues
against the **canonical** sequence; these models are of **isoforms**, and their spans are short.

| gene | domain | residues | variants | model reaches | recoverable |
|---|---|---|---|---|---|
| TRIO | d1 | 1656–1721 | 28 | 2563 | **yes** |
| DSP | d1 | 458–515 | 22 | 2272 | **yes** |
| DST | d1 | 887–944 | 22 | 2649 | **yes** |
| TRIO | d2 | 2551–2616 | 26 | 2563 | no — covers 13 of 66 residues |
| OBSCN | d1 | 5600–5667 | 38 | — | no model |
| PLEC | d1 | 941–998 | 27 | — | no model |
| MYO15A | d1 | 2867–2953 | 26 | 797 | far too short |
| NEB | d1 | 8466–8525 | 12 | — | no model |
| MACF1 | d1 | 868–925 | 10 | — | no model |
| KALRN | d1, d2 | 1646–1711, 2321–2386 | 8 | 1257 | too short |

**72 of 219 variants (33 %)**, in three domains of the eleven — and only after aligning each isoform
model to the canonical sequence to transfer the domain coordinates. That alignment is exactly the step
that has produced three defects already.

The plan also names **TRIO Q2579R** as the motivating case. It sits at residue 2579, inside TRIO
domain 2, which is one of the domains the model does **not** cover. The specific variant the task was
justified by is not recoverable.

## 3. It would change no prediction

A2 is explicit about this, by design:

> **Why structure is not a model feature.** MegaScale has no structure on any of its 389,068 rows,
> while the atlas has it on 96.8 %. A model using structure would train on one distribution and
> predict on another. Keeping structure out also makes B2 an independent test.

The 1,292 features are 1,280 ESM-2 embedding dimensions plus twelve scalars, none structural.
Structure enters as **annotation only**: `rsasa`, `buried`, `interface`, B2's structural check, B6's
family map, and G4's panel selection.

So "re-runs A2 and everything downstream (~2 h)" is doubly misleading. **No ΔΔG, no `fold_lo`, no
conformal interval and no count of 410 would move by a single digit.** What would change is burial
annotation on at most 72 of 6,884 variants — **1.0 % of the atlas.**

## What the gap actually costs, today

| | |
|---|---|
| Atlas variants without structure | 219 of 6,884 (**3.2 %**) |
| Domains affected | 11 of 310 |
| Of those variants, destabilising | 18 |
| Destabilising **and** non-hypermutated (G4's pool) | **5** |
| In the G4 panel | **1** — OBSCN L5623Q |

The one concrete, present cost is that **OBSCN L5623Q sits in the experimental panel with no burial
annotation**, so it cannot contribute to G4's buried-versus-exposed contrast. OBSCN has no AlphaFold
model at all, so G3 would not have fixed it either.

## Recommendation

**Drop G3 as scoped.** Replace it with:

1. **A stated limitation.** 3.2 % of the atlas has no structural annotation because AlphaFold DB has
   no model for those proteins, or only an isoform model too short to reach the domain. That is a
   fact about the database, not a defect in A2 — and it belongs in the manuscript's limitations
   rather than on a task list.
2. **One real defect to record.** A2 does not try isoform-suffixed model entity ids. That is a genuine
   bug, worth a line in `ANALYSIS_A2.md`, and it caps out at 72 variants of annotation.
3. **If the 72 are ever wanted**, the work is an isoform-to-canonical alignment per protein, with the
   same verification G1 ended up needing: confirm the residue at each mapped position matches the
   canonical sequence before trusting a single coordinate. Three defects in this project came from
   skipping that check.

Nothing here justifies re-running A2, and re-running it would break the property that every extended
program has held so far: **the frozen run is read-only and no published number has been recomputed.**

## Status

Complete as a scoping study. No file was fetched, no result re-run, no frozen output touched. The
AlphaFold DB queries were metadata reads (HTTP HEAD and the public prediction API).
