# E4 - independent test of the specificity axis

Run 2026-09-27 05:29. Machine-written. Plan fixed in advance: `docs/preregistration/E4.md`.

C4 built this axis and failed its own pre-registered rule (`validated: false`, median centred r +0.288). The cross-validation is re-run here and reproduces it at +0.288, so the predictions scored below are the ones that verdict came from.

44 of 45 measurements over 16 of 17 domains; ARHGEF30 excluded for want of a domain sequence. The axis is compositional, so peptides are scored by amino-acid frequency.

## Experiment 1 - MAIN: within-domain-centred correlation

| profile | r | p | verdict |
|---|---|---|---|
| **model** (leave-cluster-out) | +0.023 | 0.911 | **no** |
| average profile (domain-agnostic) | -0.043 | 0.835 | baseline |
| observed phage-display profile | -0.051 | 0.804 | control |

n = 37 over k = 12 domains, df = 24. Negative r is the direction predicted in advance. A verdict of yes needed p < 0.025 and a larger |r| than the average profile; beats the average: False.

## Experiment 2 - per-domain sign test

| model | 3/8 in the predicted direction | sign test p 0.727 | median rho +0.500 [-0.600, +0.866] | **no** |
| observed | 3/8 | p 0.727 | median rho +0.350 | control |

## Reported without a verdict

- **Exp 3**, pooled with no domain centring: rho -0.267 (p 0.0797, n 44). Peptide identity dominates this number, which is why it was given no verdict in advance.
- **Exp 4**, the 4 domains C4 never saw: 7 measurements, rho +0.036. Too few for any verdict, declared in advance.
- **Exp 5a**, dropping RP1 (nested in P3): r +0.246 (p 0.296).
- **Exp 5b**, within-domain ranks: r -0.150 (p 0.466).

## Reading, by the rule fixed in advance

**the measurement, not the model: compositional profiles do not predict these affinities**

Power, stated before the result existed: df = 24 detects only |r| >= 0.44, and the 8-domain sign test reaches 0.025 only at 8/8. A null here means no effect large enough for 44 measurements to see - not no effect.