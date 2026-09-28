# G4 — Rebuild the experimental panel

**Why it is needed.** F1 proposed ten destabilising variants and ten controls for bench validation.
It selected `stable_pool.head(10)` sorted by confidence, with no diversity constraint of any kind.
Confidence is highest exactly where the prediction is easiest, so the panel collapsed onto one
structural position and one substitution class — **5 of 10 picks at domain position 8, all five
wild-type alanine.** Five of the ten assays would have measured the same substitution.

**What it does not do.** It re-fits nothing and predicts nothing. `fold_lo ≥ 1` is still the call and
the numbers are the frozen ones. G4 is a *selection*, and carries no verdict.

**Urgency.** This had to happen before anyone synthesised anything, and H2 was explicitly blocked on
it.

## Inputs

| | |
|---|---|
| `atlas_predictions.parquet` (B3) | predictions, plus `ref_pos`, `rsasa`, `buried` |
| `SH3_cancer_master.tsv` | `n_samples_nonhyper`, tumour sites |

## What was wrong

| | F1 |
|---|---|
| Picks at domain position 8 | **5 of 10**, all wild-type alanine: `A98D` `A851P` `A297D` `A547P` `A1600P` |
| To proline / to aspartate | 4 / 4 |
| Distinct aligned positions | 6 |
| Buried picks | 8 of 10 |

A panel that repeats a position cannot separate *the model is right* from *the model has learned one
rule*. "Proline in a β-barrel core destabilises" is not a finding, and neither is "aspartate in a
hydrophobic core".

**A second flaw was less visible.** F1's controls sat at termini and exposed loops while its picks
were 8/10 buried, so the positive and negative sets differed in **burial** as much as in predicted
effect. An experiment on that panel cannot separate *the model predicts stability* from *the model
reports burial*.

## Method

Greedy by confidence, subject to constraints:

| constraint | value |
|---|---|
| one pick per aligned position (GRB2 frame) | enforced, asserted |
| one pick per gene | enforced, asserted |
| to proline | ≤ 1, asserted |
| any single mutant residue | ≤ 2 |
| exposed picks reserved | ≥ 3 |

A first pass fills the exposed quota, because exposed destabilising calls carry lower confidence and
a pure ranking always excludes them. Controls take one tolerated variant per picked domain,
**preferring buried positions**.

## Outcome

| | F1 | G4 |
|---|---|---|
| Distinct aligned positions | 6 | **10** |
| Max picks at one position | 5 | **1** |
| To proline | 4 | **1** |
| Distinct mutant residues | 5 | **7** |
| Exposed picks | 2 | **3** |
| Buried controls | 0 | **5** |
| Controls from a picked domain | 10 | 10 |

Four of F1's ten survive — RIMBP2 I906N, SORBS1 V820D, SPTA1 V982D, NOXO1 R282P — which is the right
outcome: the strongest and most distinctive predictions were always worth testing.

**The three exposed picks are the point.** A buried hydrophobic-to-charged substitution is called
destabilising by any method, including none at all. `FYN R123G`, `NOXO1 R282P` and `SH3TC2 T224I`
are exposed and predicted at 2.9–4.6 kcal/mol — those are the calls that can fail. The single
retained proline is also the exposed one, since a proline in a core tests nothing.

**Diversity costs confidence**, and the trade is stated: the least confident pick has a lower bound
of 1.87 against F1's floor of 2.47. It buys an experiment whose result means something either way.

## Outputs

| | |
|---|---|
| `panel_destabilising_G4.csv`, `panel_control_G4.csv` | the panels |
| `metrics_G4.json` | the diversity summary |
| `ANALYSIS_G4.md` | the interpretation and limitations |

F1's `experimental_candidates.csv` stands as the record of what was originally proposed, and is
superseded by these.

## Known limitations

- **OBSCN L5623Q has no structure**, so it is neither buried nor exposed and cannot contribute to the
  burial contrast.
- **Two controls fall outside the aligned reference frame** (`ref_pos` null).
- **Four of ten controls are to glutamine** — the mutant-residue cap applies to picks only, because
  controls are constrained first by domain matching and burial and the pool thins quickly.
- The pool is 121 variants over 38 aligned positions, so a panel of twenty would strain the
  one-per-position rule.

## Runtime

Under a second, on CPU. `python3 tools/g4_panel.py --root . --out results/G4_panel`
