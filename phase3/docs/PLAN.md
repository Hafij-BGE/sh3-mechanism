# Phase 3 — plan

Written 28 September 2026, after Phase 2 closed. Two programs: **H1** generality, **H2** bench.

Phase 1 established a sequence-only ΔΔG model on SH3. Phase 2 tested it against external data and it
held, with one claim withdrawn (the cancer depletion, G1). Both phases are about **one family**.
Phase 3 asks whether that matters.

---

## Why H1 is the one that changes the paper

Two central claims currently rest on single domains:

| claim | rests on |
|---|---|
| binding needs ~80 distinct mutated positions | PSD95-PDZ3, one domain |
| every SH3 binding statement | GRB2-SH3, one domain |

And the headline result — median per-domain ρ 0.839 on held-out SH3 — rests on **one held-out
family.** A reviewer's first question is whether the number is about the method or about SH3.

H1 converts *"we saw this in one family"* into *"we saw it in two"*. Nothing else available does that.

## H1 · a second domain family

### The question

**Does a family-holdout model reach comparable per-domain accuracy on a family it has never seen,
when that family is PDZ rather than SH3?**

### What must be settled first, before any model runs

**Is PDZ in the training set?** The frozen model held out SH3 and trained on everything else in
MegaScale, so *every other family was in training*. Applying the frozen model to PDZ would measure
generalisation to unseen **domains of a seen family** — a different and much weaker claim.

This is E3's lesson, which cost nothing because it was asked first: the ThermoMPNN comparison was
disqualified when 13 of our 15 held-out domains turned out to sit inside its published training
split. **H1 asks the equivalent question before writing a notebook, not after.**

**Answered, 28 September 2026 — `results/H1_0_leakage_audit/`.**

**PDZ is absent from training, so no retraining is needed — but it is absent for the wrong reason.**
MegaScale's 412 training domains are 32–72 residues (median 51) because the proteolysis assay caps
construct length there. PDZ runs 70–97 (median 88), and only 1 of 43 would even fit. So a PDZ
evaluation confounds *new family* with *longer than anything in training*, and a drop in accuracy
could not be attributed to either.

The audit validates itself on SH3: 27 MegaScale domains match PF00018 against the 26 flagged
`is_sh3`, so the matching recovers the one family known to be in training.

**Better families exist**, absent from training and length-matched:

| Pfam | domains | median length | |
|---|---|---|---|
| **PF00249** Myb/SANT | 22 | **52** | MegaScale's median is 51 |
| **PF00628** PHD finger | 23 | 55 | |
| PF00643 B-box | 17 | 45 | |
| PF00595 **PDZ** | 43 | 88 | above the 72 ceiling |

### What the evaluation would be

The design mirrors E2 and E3, so the two families are compared on like terms rather than on separate
conventions:

**Two arms, so the contrast separates family from length:**

| arm | family | what it isolates |
|---|---|---|
| **main** | PF00249 Myb/SANT (or PF00628 PHD) | a clean family-holdout test |
| **secondary** | PF00595 PDZ | family *plus* length extrapolation |

If the length-matched family holds and PDZ does not, the limit is **construct length, not family** —
a more useful finding than either arm alone, and available for one extra evaluation since neither
requires retraining.

1. **Per-domain Spearman ρ** on the held-out family, against the SH3 figure of 0.839.
2. **An external measured comparison.** Domainome aPCA covers PDZ heavily — **75,023 annotated rows,
   the largest family in the dataset, ahead of SH3's 57,949** — so the E2 design transfers directly,
   noise ceiling included.
3. **A conformal recalibration**, reported per domain from the start rather than globally, since G2
   showed the global quantile hides a 1.79× spread.

### What would count as a result

To be fixed in a pre-registration before the notebook, not here. The shape:

- **Generality supported** if per-domain ρ on PDZ is comparable to SH3's, with the comparison stated
  as an interval rather than a point.
- **Generality not supported** if it is materially worse, and the report says so — the same treatment
  G1's negative received.
- **Not judgeable** below a stated minimum number of domains.

### Known risks, stated now

- **PDZ binds C-terminal peptides through a groove; SH3 binds polyproline through a surface.** If
  accuracy differs, the cause could be the fold, the family's position in MegaScale, or the assay —
  and a single comparison cannot separate them. The claim H1 can support is narrower than "the method
  generalises".
- **Retraining is not free of the frozen run.** If H1 retrains, its model is *not* the frozen model,
  and no number from it may be quoted beside a Phase 1 number without saying so.
- **PSD95-PDZ3's ~80-position threshold is a Phase 1 claim about binding**, not folding. H1 as scoped
  tests folding. Extending it to binding is a separate question and should not be smuggled in.

## H2 · bench validation

**Unblocked by G4**, which rebuilt the panel so that the positive and negative sets differ in
predicted effect rather than in burial.

- 20 constructs: 10 predicted destabilising, 10 tolerated controls from the same domains.
- DSF to screen, CD on anything discordant.
- **Pre-register the success criterion**, including what a partial result means.
- **Pilot three domains first.** Domains excised from SPTA1 and RIMBP2 may not fold in isolation, and
  both are in the panel.
- Needs a collaborator and bench time; it is not a compute task.

**The three exposed picks are the point** — `FYN R123G`, `NOXO1 R282P`, `SH3TC2 T224I`. A buried
hydrophobic-to-charged substitution is called destabilising by any method; an exposed prediction at
2–3 kcal/mol is the one that can fail.

## Order of work

```
H1.0  leakage audit                              DONE 28 Sep. PDZ absent, but for the
                                                 wrong reason; main arm is now Myb/SANT
H1.1  pre-registration                           DONE 28 Sep, unsigned. docs/preregistration/H1.md
H1.2  the evaluation                             DONE 28 Sep. Reproduction passed
                                                 (0.566 vs 0.573). MAIN inconclusive
                                                 (delta -0.203, CI -0.249..-0.120);
                                                 PDZ matches SH3 (0.602 vs 0.623), so
                                                 LENGTH IS NOT THE LIMIT.
                                                 results/H1_generality/
H2    bench, in parallel and on someone else's clock
```

## What Phase 3 must not do

Restated from the README because it is the thing most easily lost: **nothing here writes to
`results/`, `extended/` or the repository-root `docs/`**, and no Phase 1 or Phase 2 number is
recomputed. A Phase 3 finding is promoted into the manuscript only once it stands on its own.
