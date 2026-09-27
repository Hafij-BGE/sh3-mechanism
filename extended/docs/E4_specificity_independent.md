# E4 — Independent test of the specificity model  *(planned)*

**Why it is needed.** C4 built a specificity axis from 154 phage-display PWM profiles and failed its
own pre-registered rule (median centred r = +0.288; better than the family-average profile on only
55 of 115 domains). That failure was measured against the same data the model came from. E4 tests it
against affinities measured by a different group, by a different method.

**What it does not do.** It does not attempt to rescue C4. The pre-registered rule already returned
`validated: false`, and no rewiring claim rests on it.

## Inputs
| File | From | Used for |
|---|---|---|
| `kazemein_jasemi_2024_TableS6_Kd.csv` | Kazemein Jasemi et al. 2024, *Cells* | **45 dissociation constants, 17 SH3 domains, 0.2–125 µM** |
| C4's specificity model | C4 (frozen) | the predicted axis |

The Kd table was extracted from Table S6 of the supplementary PDF; both the count (45) and the range
(0.2–125 µM) match the paper exactly, which is the check that the parse is right. See
`DATA_PROVENANCE.md` §8 — the publisher's download is bot-blocked and the file came from Europe PMC.

## Method
Predict the specificity axis for the 17 domains, correlate against the measured affinities, and
report. The peptides are SOS1-derived proline-rich motifs plus two reference peptides, so the
comparison is domain-level specificity against measured binding, not a like-for-like PWM test.

## Expected outcome, stated in advance
**Failure.** C4 failed internally, and there is no reason to expect it to pass externally. That is the
point: a second, *independent* failure is a stronger negative result than one internal failure. "The
specificity axis does not predict measured SH3 affinities" is a cleaner claim than "our specificity
axis did not pass our own threshold".

If it unexpectedly succeeds, that is a finding — and it must be reported as a **post-hoc** result,
because C4's rule was already declared and already failed.

## Scale
45 measurements across 17 domains is small. It cannot support a positive claim on its own; it can
support a negative one, which is what is expected.
