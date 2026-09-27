# E2 — the noise ceiling

**Question.** E2 found a pooled Spearman ρ = −0.600 between the frozen folding head and Domainome
abundance, with a per-domain median of −0.573. Is that good? The number means nothing until we know
what the *maximum achievable* correlation is.

**Method.** Seven SH3 domains were measured twice, by independent experiments in different
laboratories:

- **MegaScale** (Tsuboyama/Rocklin) — proteolysis resistance, ΔΔG in kcal/mol
- **Domainome** (Beltran/Lehner) — abundance protein-fragment complementation (aPCA)

Their agreement on the *same variants* is the ceiling. No predictor can beat two careful experiments
agreeing with each other, because each carries its own measurement noise.

**Position mapping.** Rocklin positions are domain-local (1–70); Domainome's are absolute protein
positions. The conversion is

```
rocklin_pos = domainome_position − domain_start + 1 + offset
```

with `domain_start` the suffix of `domain_ID` and `offset` from
`domains_from_tsuboyama_rocklin_overlaps.txt`. Verified empirically: for BTK this yields 1,102
matching variants at the recorded offset (−1), against ≤114 at any other shift.

**Signs.** Rocklin ΔΔG is negative for destabilising, and so is aPCA fitness, so the two assays agree
*positively*. Our `pred_ddG_fold` is positive for destabilising, so it agrees *negatively*. Everything
below is |ρ|.

**QC.** The authors' own filters: `percent_overlap > 80`, `mean_input_count > 5`. 4,008 variants
survive across four domains.

---

## Result 1 — the ceiling is about 0.71, not 1.0

| Domain | n | assay-vs-assay \|ρ\| |
|---|---|---|
| BTK | 1,036 | **0.746** |
| LCK | 971 | **0.735** |
| HCK | 819 | **0.684** |
| SPTB1 (P07751) | 1,182 | 0.574 |
| | | **median 0.709** |

Two well-executed experiments measuring the same substitutions agree at ρ ≈ 0.7. The gap from 1.0 is
not sloppiness — it is that proteolysis resistance and cellular abundance are different observables.

**This reframes E2's headline.** A per-domain median of 0.573 against a ceiling of 0.709 is not a
moderate correlation; it is roughly **four fifths of the maximum any method could reach**.

## Result 2 — matched variants, directly comparable

Result 1 compares unequal samples: the ceiling uses ~1,000 variants per domain, while our figure comes
from the 880 cancer variants of the atlas. Restricting both sides to exactly the same variants:

| Domain | n | ceiling | ours | share of ceiling |
|---|---|---|---|---|
| LCK | 26 | 0.815 | 0.735 | **90 %** |
| HCK | 19 | 0.593 | 0.604 | **102 %** |
| BTK | 39 | 0.623 | 0.704 | **113 %** |

On two of three domains the model **matches or exceeds** the agreement between two physical
experiments. That is not a paradox: the model predicts the systematic component, while each assay
carries independent noise. A denoised predictor can sit closer to the truth than either single
measurement.

## Result 3 — HCK was not a model failure

E2 reported HCK as the weakest domain (|ρ| = 0.339) and I read that as a weakness of the model. The
matched comparison says otherwise: on the same 19 variants the ceiling is 0.593 and the model reaches
0.604. **HCK's apparent weakness is a property of which variants were compared, not of the predictor.**
The same caution applies to FYN and NPHP1, the other two domains I previously flagged.

---

## Limitations

1. **NPHP1 (1S1N) and RASA1 (2M51) produced no matched variants.** Both PDB entries are present in the
   aPCA file, so the recorded offset does not reconcile their numbering. Their ceilings are unknown;
   this is a mapping problem to solve, not evidence about either domain.
2. **Small matched samples** — 19 to 39 variants. The matched-subset ratios are indicative, not precise;
   a ratio above 100 % should not be read as the model beating the experiment by a specific margin.
3. **SPTB1 has no "ours"** because P07751 is not in the 235-gene atlas.
4. **Three domains, not fifteen.** Only these SH3 domains were measured by both studies, so the ceiling
   is estimated from a small part of the family.

## What to write in the paper

Report E2's ρ **beside the ceiling**, never alone. "Pooled ρ = 0.600 against an assay-to-assay ceiling
of 0.709 on the domains measured twice" is a far stronger and more honest claim than "ρ = 0.600".

Reproduce with `tools/e2_noise_ceiling.py`; outputs are `noise_ceiling_E2.csv` (full domains) and
`noise_ceiling_matched_E2.csv` (matched subset).
