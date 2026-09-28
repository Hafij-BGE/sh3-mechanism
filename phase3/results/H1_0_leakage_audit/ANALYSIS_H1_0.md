# H1.0 — leakage audit: is PDZ in the training set?

Run 28 September 2026, locally, minutes on CPU. Machine numbers in `metrics_H1_0.json`,
`family_audit.csv` and `megascale_family_map.csv`.

**No model was run and no prediction was made.** This is the question E3 taught us to ask before
writing a notebook rather than after, and the answer changes what H1 should be.

---

## The answer

**PDZ is not in the training set — and the reason it is absent is a problem.**

| | |
|---|---|
| MegaScale training domains | **412**, 389,068 substitutions |
| Their construct length | **32–72 residues**, median 51. **None longer than 72** |
| PDZ (PF00595) in Domainome | **43 domains**, 70–97 residues, median 88 |
| PDZ domains found in MegaScale | **0** |
| PDZ domains that would even fit MegaScale's assay | **1 of 43 (2.3 %)** |

So the frozen model can be applied to PDZ directly — no retraining, which is the cheap branch the
plan hoped for. But PDZ is held out **because it is longer than anything in training**, not because
it was set aside. The model has never seen a domain above 72 residues, and PDZ's median is 88.

**A PDZ evaluation therefore confounds two things: a new family, and an extrapolation in length.** If
accuracy drops, nothing in the design says which caused it — and "the method does not generalise
across families" is precisely the wrong conclusion to draw from a length effect.

This is not a flaw in MegaScale. Tsuboyama's proteolysis assay works on small domains, so the
ceiling is a property of the measurement. It is a flaw in choosing PDZ as the second family.

## The audit checks itself

The matching is validated on the one family known to be in training:

| | |
|---|---|
| MegaScale domains flagged `is_sh3` | 26 |
| Matched to Domainome SH3 (PF00018) at ≥ 50 % identity | **27** |
| Plus SH3_9 (PF14604) | 1 |

The method recovers SH3 and assigns it the right Pfam, which is the assertion the tool makes before
reporting anything else.

100 of 412 MegaScale domains matched a Domainome family at all. The other 312 are de novo designs
(`rockdoms` and similar) or natural domains of families Domainome does not cover. **That does not
weaken the result**, because the question is not "what is every MegaScale domain" but "are the
Domainome domains we would evaluate on present in MegaScale" — and the match runs in that direction.

## Better second families exist

Families absent from training, with ≥ 15 domains in Domainome, whose lengths sit **inside** the
training distribution:

| Pfam | domains | median length | in training | length-matched |
|---|---|---|---|---|
| **PF00249** Myb/SANT | 22 | **52** | no | **yes** — MegaScale's median is 51 |
| **PF00628** PHD finger | 23 | **55** | no | **yes** |
| PF00643 B-box zinc finger | 17 | 45 | no | yes |
| PF00013 KH domain | 17 | 72 | no | at the ceiling |
| PF00096 C2H2 zinc finger | 112 | 22 | no | **no — far below** MegaScale's 32 minimum |
| — | | | | |
| PF00595 **PDZ** | 43 | 88 | no | **no — above** MegaScale's 72 maximum |

**PF00249 (Myb/SANT) is the cleanest available comparison.** 22 domains, median length 52 against
MegaScale's 51, genuinely absent from training. PF00628 (PHD finger) is nearly as good with 23
domains at median 55.

PF00096 is the largest family by count but fails the same test in the other direction: at a median of
22 residues it is far shorter than MegaScale's 32-residue minimum, so it carries the identical
confound with the sign reversed.

## What this means for H1

The plan named PDZ for a reason worth keeping: PSD95-PDZ3 carries Phase 1's ~80-position binding
threshold, so PDZ connects to an existing claim. That argues for including it, not for making it the
main arm.

**Recommendation: run two families, and let the contrast do the work.**

| arm | family | length | what it isolates |
|---|---|---|---|
| **main** | PF00249 Myb/SANT (or PF00628 PHD) | matched | a clean family-holdout test |
| **secondary** | PF00595 PDZ | 88 vs ≤ 72 | family *plus* length extrapolation |

If the length-matched family holds up and PDZ does not, the difference is evidence that the limit is
**construct length, not family** — which is a more useful and more defensible finding than either arm
alone, and it is available at the cost of one extra evaluation because neither requires retraining.

If both hold up, generality is supported more strongly than a single family could support it.

## What is still unestablished

- **This audit covers folding, not binding.** Phase 1's ~80-position threshold is a claim about
  binding on PSD95-PDZ3. Nothing here tests it, and H1 as scoped should not be read as doing so.
- **Absence from Domainome-matched MegaScale is not absence from MegaScale.** For 312 unmatched
  training domains the family is unknown. The conclusion is sound for the evaluation set, which is
  what matters, but "PF00249 appears nowhere in MegaScale" is stronger than the evidence.
- **Domainome measures abundance, not ΔΔG.** The comparison is E2's, with the same interpretation
  and the same need for a noise ceiling — not a direct ΔΔG benchmark.
- **No pre-registration exists yet**, and none could have been written before this answer. It comes
  next, and it now has a main arm to name.

## Status

Complete. `docs/PLAN.md` is updated; H1's pre-registration is the next step and can now be written
against a decided design.
