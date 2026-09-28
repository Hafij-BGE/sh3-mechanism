# H1 — analysis

Run 28 September 2026 on Colab, A100 40 GB. Machine numbers in `metrics_H1.json`, `RESULTS_H1.md`
and `per_domain_H1.csv`; sources and methodology in `METHODS_H1.md`; the plan they were judged
against is `phase3/docs/preregistration/H1.md`, committed before the notebook existed.

**Nothing was re-fitted.** The frozen head was applied unchanged to families it has never seen.

---

## The pipeline is the frozen one

| | |
|---|---|
| Reproduction on E2's own matched variants | **0.5660** |
| E2 published | 0.573 |
| Tolerance (Part 9.2) | ±0.02 |

768 variants over 20 domains. **The control passes**, so the features, the scalar order, the seed
ensemble and `clip = 10` are Phase 1's, and any difference below is the evaluation set rather than
the arithmetic.

## The result

| arm | domains | median \|ρ\| | vs SH3 | Δ | 95 % CI | verdict |
|---|---|---|---|---|---|---|
| **MAIN** length-matched | 35 | 0.420 | 0.623 | **−0.203** | [−0.249, −0.120] | **inconclusive** |
| SECONDARY PDZ | 31 | 0.602 | 0.623 | −0.021 | [−0.082, +0.027] | *supported*, carries no verdict |

**The main arm is inconclusive by the pre-registered rule**, and the rule is doing real work here.
The point estimate, −0.203, is worse than the −0.15 margin. The interval lies mostly below the margin
but does not exclude it, so Part 4's third row applies: *the design could not resolve it, and says
so*. It is not a licence to read the point estimate as the answer.

This is not a power failure. Part 5 predicted an interval about 0.148 wide at 35 domains; the
observed interval on the difference is **0.129** wide. The design performed as calculated — Δ simply
landed close enough to the margin that 35 domains cannot separate them.

## Length is not the barrier

This is the clean finding, and it is the whole reason PDZ was included.

**PDZ has a median construct length of 88 residues. Nothing in the training set exceeds 72.** It is
therefore 16 residues beyond any protein the model has seen, in a family it has never seen — and it
reaches **0.602 against SH3's 0.623**, with a confidence interval that comfortably includes zero
difference.

Part 6's 2 × 2 anticipated *main supported, PDZ not supported* as the informative cell, meaning the
limit was length. **The opposite happened.** PDZ carries no verdict of its own by pre-registration
and none is claimed, but as a contrast it does its job: whatever is holding the main arm back, it is
not construct length, and it is not novelty of family either — PDZ is as novel as any of them.

## The per-family split is where the difficulty is

Reported because Part 3 required it always, not because the ordering is convenient:

| Pfam | family | domains | median \|ρ\| |
|---|---|---|---|
| PF00018 | SH3 *(reference)* | 36 | **0.623** |
| PF00595 | PDZ | 31 | **0.602** |
| PF00249 | Myb/SANT | 15 | 0.507 |
| PF00628 | PHD finger | 11 | **0.376** |
| PF00643 | B-box | 9 | **0.335** |

**The two worst families are the two that coordinate zinc**, which Part 7 named in advance:

> *PHD and B-box coordinate zinc. Their stability in an abundance assay may depend on metal
> availability in a way the model cannot represent and SH3 never required. If the main arm fails,
> this is the first thing to check before concluding anything about generality.*

A pre-registered risk materialising is worth more than the same observation made afterwards. But it
is not yet an explanation, for two reasons.

**First, Myb/SANT does not fit it.** Myb/SANT binds no metal and still sits at 0.507, well below SH3
and PDZ. If zinc were the whole story it should look like them. So at most zinc accounts for part of
the gap.

**Second, the assay quality moves the same way.** Part 7 also warned that a lower ρ could reflect
noisier measurements rather than worse predictions, and the within-assay ratio says it might:

| arm | median \|fitness\| / σ |
|---|---|
| PDZ | **3.268** |
| SH3 | 2.199 |
| main | **1.863** |

The ordering of assay quality is the ordering of the result. **These two explanations cannot be
separated with the pre-registered design**, and neither can be dismissed.

This is exactly the gap Part 7 admitted could not be closed: the new families have no MegaScale
measurements **by construction** — that is why they are held out — so no between-assay noise ceiling
exists for them. E2 could say 0.600 was 85 % of what two independent assays achieve against each
other. Nothing here can make the equivalent statement.

## What H1 licenses as a claim, and what it does not

**Licensed.**

*Applied unchanged to a family it has never seen, and to constructs longer than anything in its
training data, the frozen model reaches a median per-domain |ρ| of 0.602 against 0.623 on SH3 itself
(Δ = −0.021, 95 % CI −0.082 to +0.027). Accuracy on three other unseen families is lower
(median 0.420), and the comparison against SH3 is inconclusive at the pre-registered margin.*

**Not licensed.**

- **"The method generalises."** One family matching SH3 is not generality, and three others were
  lower.
- **"The method does not generalise."** The main arm's interval does not exclude the margin, and two
  unresolved confounds sit on the same side.
- **"Zinc coordination is the limit."** Pre-registered as a risk and consistent with the two worst
  families — but Myb/SANT contradicts it and assay noise co-varies with it.
- **Anything about binding.** Phase 1's ~80-position threshold is a binding claim on PSD95-PDZ3. H1
  tested folding and says nothing about it.

## What would resolve it

In order of cost, and none of it is in this program's scope:

1. **Adjust for assay quality per domain.** `per_domain_H1.csv` has ρ per domain and the replicate
   σ is available per variant; regressing ρ on per-domain signal-to-noise would show whether the
   family ordering survives. Cheap, but **post-hoc**, so it belongs in its own pre-registration
   rather than appended here.
2. **A length-matched, non-metal-binding family with assay quality near SH3's.** The audit's
   `family_audit.csv` is the selection table; the constraint that bit here — assay quality — was not
   one of its three criteria and should be a fourth.
3. **A second assay on any of these families**, which is the only thing that would supply a real
   noise ceiling.

## Effect on the project

**Objection 3 (generality asserted from one family) moves, but not as far as hoped.** E2 already
widened the evidence to 41 SH3 domains and 32 genes. H1 adds that the model holds on an entirely
unseen family at essentially SH3's accuracy, and that **construct length is not the constraint it
might have been** — a specific, previously untested worry now retired.

It does not support a general claim across families, and the honest summary is that **one unseen
family matched and three did not, with the reason unresolved.**

For the manuscript this is a Discussion paragraph, not a Results section: the PDZ figure and the
length finding are quotable; the main arm's number must be reported with its interval and its two
confounds, or not at all.

## Status

Complete as pre-registered. The pre-registration is unsigned; Part 13-equivalent sign-off should
record that the main arm returned inconclusive and that PDZ's supporting result carries no verdict
by design.
