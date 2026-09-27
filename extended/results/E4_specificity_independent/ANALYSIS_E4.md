# E4 — analysis

Run 27 September 2026. Machine numbers in `RESULTS_E4.md` and `metrics_E4.json`; the plan they were
judged against is `docs/preregistration/E4.md`, committed before the notebook existed.

---

## The result

Both experiments carrying a verdict return **no**.

| Experiment 1 (MAIN), within-domain-centred | r | p |
|---|---|---|
| **model**, leave-cluster-out | **+0.023** | 0.91 |
| average profile, domain-agnostic baseline | −0.043 | 0.84 |
| **observed** phage-display profile (control) | **−0.051** | 0.80 |

n = 37 over 12 domains, df = 24. Negative was the direction declared in advance. The model does not
reach it, does not approach significance, and **does not beat the domain-agnostic baseline** — the
second condition the pre-registration required. Experiment 2 agrees: 3 of 8 domains in the predicted
direction, sign test p = 0.73.

## The control is the finding, not a footnote

**The observed profile fails too.** That is the row that decides what E4 is allowed to claim, and the
reading was fixed in Part 6 before any number existed:

> observed fails **and** model fails → *the measurement, not the model.*

The observed phage-display profile is the quantity C4's head is trained to predict. It is the ceiling
here in exactly the sense the noise ceiling is in E2: **a predictor of X cannot outperform X.** Since
X itself carries no within-domain relationship to measured affinity (r = −0.051, p = 0.80), no
improvement to C4's regression could have produced a positive E4. The failure is in the
representation, not in the fit.

So E4 does **not** convict C4's model, and writing it up as though it did would be wrong.

## Why the representation cannot work here

C4 collapses each 14 × 20 PWM to one information-content-weighted 20-vector, so the axis knows
composition and not order. SH3 ligand classes are defined by order:

```
class I    +xΦPxΦP        basic residue N-terminal to the PxxP core
class II   ΦPxΦPx+        basic residue C-terminal to it
```

Two peptides of opposite class can have **identical amino-acid composition** and are therefore the
same vector to this model. Discarding position discards the thing that distinguishes SH3 specificity.
This was recorded in Part 1 of the pre-registration, before any score was computed, precisely so it
could not be produced afterwards as an excuse.

## How much domain-specific information the prediction actually carries

Measured on the 37 scored pairs:

| | correlation with the domain-agnostic average score | share of score spread driven by peptide rather than domain |
|---|---|---|
| model prediction | **+0.82** | **70 %** |
| observed profile | +0.59 | 46 % |
| average profile | 1.00 by definition | 100 % |

Two separate problems, and the order matters:

1. **The predictions are shrunk hard toward the family mean.** Two-thirds of the model score's
   variance is shared with a score that does not know which domain it is looking at. This is C4's own
   internal verdict seen from a different angle — it beat the average profile on 55 of 115 domains —
   and it is a modelling limitation that could in principle be improved.
2. **The measured profile is genuinely more domain-specific (54 % of its spread) and still does not
   predict affinity.** So fixing (1) cannot rescue this. (2) is the binding constraint.

## The only hint of signal is the kind that is not specificity

Experiment 3 — pooled, no domain centring — gives ρ = **−0.267** (p = 0.080, n = 44). Right direction,
largest effect anywhere in E4, and **given no verdict in advance for exactly this reason**: without
centring, the number is dominated by which peptide is being measured. It says "peptides that look more
like a generic SH3 ligand bind everything a little more tightly". That is the domain-agnostic effect
the average-profile baseline exists to absorb. It is the opposite of specificity, and promoting it now
would be the post-hoc move the pre-registration was written to prevent.

## Per-domain detail — reported, not to be read into

| domain | n | ρ | | domain | n | ρ |
|---|---|---|---|---|---|---|
| GRB2-1 | 5 | −0.70 | | ARHGAP12 | 4 | +0.80 |
| GRB2-2 | 5 | −0.70 | | ITSN1-1 | 3 | +1.00 |
| ABL2 | 3 | −0.50 | | ITSN1-5 | 3 | +0.87 |
| | | | | BIN1 | 3 | +0.50 |
| | | | | SH3PXD2A-1 | 3 | +0.50 |

The two best-sampled domains both sit at −0.70, which is tempting. It is also what three to five
measurements per domain produce by chance: at n = 3 the only attainable values are ±0.5 and ±1.0.
Nothing here is promoted.

## The verification that makes the rest meaningful

The re-run of C4's cross-validation reproduced its recorded median centred r **to 1.6 × 10⁻¹⁴** —
floating-point identical, not merely close:

```
C4 recorded   0.2884351199911039
E4 re-run     0.28843511999112015
```

Same clustering, same per-fold alpha selection, same embeddings. So the leave-cluster-out predictions
scored here are, without qualification, the ones C4's `validated: false` was computed from. Had this
assertion failed the notebook would have stopped, and everything below it would have been worthless.

## What E4 licenses as a claim, and what it does not

**Licensed.** *44 independently measured SH3–peptide affinities give no support to the compositional
specificity axis. Neither the model's prediction nor the measured phage-display profile it targets
predicts affinity within a domain, so the result is a limit of the compositional representation rather
than of the regression.* Paired with C4's own `validated: false`, this closes the axis honestly: two
failures, one internal and one external, with the external one correctly attributed.

**Not licensed.**

- "C4's model is wrong." The data cannot separate that from "composition is the wrong representation",
  and the control says the latter is at least sufficient to explain the result.
- Anything built on Experiment 3.
- Any claim from the four never-trained domains: 7 measurements, ρ = +0.036, declared unjudgeable in
  advance.

## What would actually test the idea

A different program, not a repair to this one: keep the positional PWM instead of collapsing it, score
peptides with a sliding window, and use ligands spanning both SH3 classes rather than nine
proline-rich fragments of one protein. Part 8 of the pre-registration admitted the narrow compositional
range in advance; E4's result is consistent with that admission, which is why the negative is reported
as bounded rather than sweeping.

## Effect on the plan

The rewiring axis was already unused — no claim in the project rests on it — and that does not change.
What changes is the strength and the framing of the negative: it is now independent, and it is
correctly attributed to the representation rather than to the fit. Objection 3 (generality) is
untouched; H1 remains the route to it.
