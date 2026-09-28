# G4 — analysis

Run 28 September 2026, locally, on CPU in under a second. Machine numbers in `metrics_G4.json`;
the panels are `panel_destabilising_G4.csv` and `panel_control_G4.csv`.

G4 selects; it computes nothing and carries no verdict. **No prediction was re-fitted, no threshold
moved.** `fold_lo ≥ 1` is still the call and the numbers are the frozen ones. What changes is *which
ten variants go to the bench*.

---

## Why F1's panel had to be rebuilt

F1 took `stable_pool.head(10)` sorted by confidence, with no diversity constraint of any kind.
Confidence is highest exactly where the prediction is easiest, so the panel collapsed:

| | F1 |
|---|---|
| Picks at domain position 8 | **5 of 10** — and all five wild-type **alanine** |
| | `A98D` `A851P` `A297D` `A547P` `A1600P` |
| To proline | 4 of 10 |
| To aspartate | 4 of 10 |
| Buried | 8 of 10 |
| Distinct aligned positions | 6 |

**Five of the ten assays would have measured the same substitution.** A panel that repeats a position
cannot distinguish *the model is right* from *the model has learned one rule*, and "proline in a
β-barrel core destabilises" is not a finding — neither is "aspartate in a hydrophobic core".

There was a second problem, less visible. F1's controls sat at termini and exposed loops (positions
2, 3, 13, 15, 15, 17, 37, 58, 61, 69), while its picks were 8/10 buried. **The positive and negative
sets therefore differed in burial as much as in predicted effect.** An experiment on that panel
cannot separate "the model predicts stability" from "the model reports burial", which is the first
thing a reviewer would say.

## The rebuilt panel

| | F1 | **G4** |
|---|---|---|
| Distinct aligned positions | 6 | **10 of 10** |
| Max picks at one position | 5 | **1** |
| To proline | 4 | **1** |
| Distinct mutant residues | 5 | **7** |
| Max of any one mutant residue | 4 | **2** |
| Exposed picks | 2 | **3** |
| Distinct genes | 10 | 10 |
| Controls from a picked domain | 10 | **10** |
| Buried controls | 0 | **5** |

### Destabilising picks

| Gene | Variant | Aligned pos | Buried | ΔΔG | lower 90 % |
|---|---|---|---|---|---|
| RIMBP2 | I906N | 47 | yes | 4.62 | 3.81 |
| SORBS1 | V820D | 25 | yes | 4.11 | 3.39 |
| SPTA1 | V982D | 3 | yes | 4.26 | 3.11 |
| NOXO1 | R282P | 43 | **no** | 4.63 | 2.68 |
| OBSCN | L5623Q | 19 | *no structure* | 3.45 | 2.33 |
| SNX18 | E25G | 23 | yes | 3.13 | 2.30 |
| SH3TC2 | T224I | 46 | **no** | 3.26 | 2.29 |
| ITSN1 | G1126S | 45 | yes | 3.78 | 2.12 |
| FYN | R123G | 37 | **no** | 2.93 | 2.07 |
| LASP1 | Y213N | 9 | yes | 2.71 | 1.87 |

Four of F1's ten survive — RIMBP2 I906N, SORBS1 V820D, SPTA1 V982D and NOXO1 R282P — which is the
right outcome: the strongest, most distinctive predictions were always worth testing, and it was the
five alanines and their duplicates that were not.

### The exposed picks are the ones that matter

**A buried hydrophobic-to-charged substitution is predicted destabilising by any method, including
none at all.** A prediction of 2–3 kcal/mol at a *solvent-exposed* position is the one that can fail,
and it is the one that distinguishes this model from a burial lookup table:

- **FYN R123G** — exposed arginine to glycine, 2.93 kcal/mol
- **NOXO1 R282P** — exposed arginine to proline, 4.63 kcal/mol
- **SH3TC2 T224I** — exposed threonine to isoleucine, 3.26 kcal/mol

These carry lower confidence than the buried picks (2.07–2.68 against up to 3.81), which is exactly
why a pure confidence ranking excluded them and why `MIN_EXPOSED` reserves places. **If these three
come back as tolerated, the model's exposed-position calls are wrong, and that is worth knowing.**

The single retained proline is `NOXO1 R282P`, which is also exposed — the most informative proline
available, since a proline in a core is not a test of anything.

### Controls now contrast with the picks on effect, not on burial

All ten controls come from the same domains as the picks, so each domain can be tested as its own
positive and negative. Five are buried, against none in F1.

A tolerated variant at an exposed terminus is a weak negative: nothing predicted it would break. A
tolerated variant **in the core**, in the same domain as a destabilising pick, is the control that
carries information — it says the model discriminates within a structural context rather than
reporting the context.

## Limitations, stated

- **OBSCN L5623Q has no structure**, so it is neither buried nor exposed and is counted as neither.
  It is retained because it satisfies every other constraint, but it cannot contribute to the
  burial contrast.
- **Two controls fall outside the aligned reference frame** (SORBS1 M795L, SPTA1 G978A, `ref_pos`
  null). Controls are not position-constrained, so this is tolerable, but they cannot be described in
  the family frame.
- **Four of the ten controls are to glutamine.** The mutant-residue cap is applied to the picks, not
  the controls, because controls are constrained first by domain matching and burial and the pool
  thins quickly. Worth noting rather than fixing.
- **The pool is 121 variants over 38 aligned positions**, so ten distinct positions is comfortable
  but not lavish; a panel of twenty would begin to strain the one-per-position rule.
- **G4 does not make these variants more likely to be destabilising.** It makes the *result*
  interpretable. Diversity costs confidence: the least confident pick has a lower bound of 1.87
  against F1's floor of 2.47.

## What this unblocks

**H2 (bench validation) was explicitly blocked on G4** and is now unblocked. The plan's pilot advice
still stands: try three domains first, because domains excised from SPTA1, DLG5 and RIMBP2 may not
fold in isolation — and SPTA1 and RIMBP2 are both still in the panel.

## Status

Complete. The panel is a selection from frozen predictions; it changes nothing upstream and no
recorded value moved. F1's `experimental_candidates.csv` remains as the record of what was
originally proposed, and is superseded by this one.
