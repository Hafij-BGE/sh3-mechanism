# H1.3 — Is H1's family ordering assay quality?

*(Drafted 28 September 2026. Awaiting sign-off. **Nothing has been run:** no relationship between
per-domain accuracy and per-domain assay quality has been computed or displayed.)*

## What this file is for

H1 returned **inconclusive** on its main arm (Δ = −0.203, 95 % CI −0.249 to −0.120 against a −0.15
margin) and found PDZ matching SH3 (Δ = −0.021). Its Part 7 named two explanations for the gap and
said neither could be separated by that design:

1. **Zinc coordination** — PHD and B-box, the two worst families, bind zinc.
2. **Assay quality** — a lower |ρ| may reflect noisier measurements rather than worse predictions.

H1.3 addresses the second, which is the one that can be tested with data already in hand.

> **Does the difference between arms survive matching on assay quality?**

This is explicitly a **post-hoc follow-up**. It is pre-registered because it is post-hoc, not despite
it: the question arose from H1's result, so the rule for answering it has to be fixed before the
answer exists.

---

## Part 1 — What is already known, and what is not

Stated plainly because the attestation depends on it.

**Known.** H1's per-family median |ρ| (SH3 0.623, PDZ 0.602, Myb/SANT 0.507, PHD 0.376, B-box 0.335)
and its **variant-weighted** assay ratio by arm (PDZ 3.268, SH3 2.199, main 1.863). That the two
orderings agree at arm level is the observation prompting this file.

**Counted for this file, 28 September 2026** — assay quality only, with no prediction involved:

| arm | domains (n ≥ 20) | min | 25 % | median | 75 % | max |
|---|---|---|---|---|---|---|
| main | 35 | 0.98 | 1.62 | **1.88** | 2.44 | 3.16 |
| pdz | 31 | 0.95 | 2.27 | **3.48** | 5.25 | 10.52 |
| sh3 | 36 | 1.12 | 1.59 | **2.09** | 2.94 | 5.17 |

**This already qualifies H1's framing.** Per domain, main and SH3 overlap heavily — medians 1.88
against 2.09, interquartile ranges 1.62–2.44 against 1.59–2.94. The arm-level gap H1 reported was
variant-weighted and overstated the separation. **PDZ is the outlier**, not the main arm.

**Not known.** No correlation, regression or comparison between per-domain |ρ| and per-domain assay
quality has been computed. `per_domain_H1.csv` (which holds ρ) has not been joined to the assay
table.

## Part 2 — The data

| | |
|---|---|
| Accuracy | `results/H1_generality/per_domain_H1.csv` — per-domain \|ρ\|, from H1, unchanged |
| Assay quality | Domainome Table 2, `median(\|normalized_fitness\| / normalized_fitness_sigma)` per domain |
| Eligibility | the same domains H1 used: ≥ 20 scored variants |

No prediction is recomputed. H1's numbers are read, not regenerated.

## Part 3 — The comparison

**Matching band**, fixed now: from the **10th percentile of the main arm** to the **90th percentile
of SH3** — 1.28 to 3.80 on the ratio above. It is defined by the two arms in the primary comparison,
not by the result, and it is deliberately generous because the distributions overlap.

Counted before sign-off:

| arm | inside the band |
|---|---|
| main | **31 of 35** |
| sh3 | **30 of 36** |
| pdz | 18 of 31 |

**Matching costs the primary comparison almost nothing** — 31 against 30 domains, versus 35 and 36
unmatched. Power is therefore essentially H1's, and Part 5 of H1 established that 35 domains give an
interval about 0.148 wide.

## Part 4 — The questions

| | question | verdict? |
|---|---|---|
| **Q1 — PRIMARY** | does the main-vs-SH3 gap survive matching on assay quality? | **yes** |
| Q2 | is PDZ's parity with SH3 explained by its higher assay quality? | no — reported |
| Q3 | across all 102 domains, how strongly does \|ρ\| track assay quality? | no — reported |

Q2 and Q3 carry no verdict because PDZ carried none in H1 and because Q3 is descriptive. One verdict
means no multiplicity adjustment.

### The statistic

Identical to H1's, so the two are comparable: **median per-domain |ρ|**, Δ against SH3, 95 % CI from
**4,000 bootstrap resamples over domains**, margin **−0.15**.

### The rule for Q1

| outcome | condition | reading |
|---|---|---|
| **assay quality explains the gap** | matched Δ CI includes 0 | the family ordering is measurement noise, and H1's main arm says nothing about the model |
| **it does not** | matched Δ CI upper bound < 0 **and** the matched Δ is within 0.05 of H1's −0.203 | the gap is a property of the predictions, not the measurements |
| **partly** | matched Δ CI upper bound < 0, and the matched Δ is more than 0.05 closer to zero than −0.203 | both contribute; the shift is reported as the size of the assay contribution |
| **inconclusive** | none of the above | said plainly |

**0.05 is a third of the margin**, chosen because H1 established that this design cannot resolve
differences of that size — so a shift smaller than 0.05 is not a shift this method can claim.

### Minimum

Fewer than **20 domains** in either matched arm → numbers printed, **no verdict**. (31 and 30 are in
hand, so this will not bind.)

## Part 5 — What this cannot settle

- **Zinc is untouched.** H1's other explanation is not tested here, and Q1 returning "assay quality
  does not explain it" does **not** promote zinc by elimination — Myb/SANT binds no metal and is
  also low, so a third cause is possible and unnamed.
- **The ratio is a within-assay quantity**, not a noise ceiling. It compares a measurement to its own
  replicate error, not to an independent assay. A family could have consistent, precise and
  systematically wrong measurements and score well on it.
- **Matching is not adjustment.** Restricting to a common band removes the gross difference in assay
  quality; it does not remove any residual relationship within the band, which is what Q3 reports and
  does not correct for.
- **This is post-hoc.** The design followed the result. Everything it produces is weaker than the
  same finding from a pre-planned experiment, and the write-up must say so.

## Part 6 — Attestation

The work before this file: reading H1's published per-family and per-arm numbers, which are in
`metrics_H1.json`, and computing **per-domain assay quality alone** — a function of
`normalized_fitness` and `normalized_fitness_sigma`, with no prediction involved, saved without any
ρ column.

**`per_domain_H1.csv` has not been joined to the assay table**, and no statistic relating accuracy to
assay quality has been computed or displayed.

One caveat, stated rather than glossed: the arm-level agreement between the two orderings is what
prompted this file and is necessarily known. The guarantee is that the **per-domain** relationship —
which is what Q1 through Q3 test — does not yet exist.

---

**Signed off:** ______  **Date:** ______  **Commit:** ______
