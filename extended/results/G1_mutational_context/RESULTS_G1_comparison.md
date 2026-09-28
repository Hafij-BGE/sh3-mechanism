# G1 — does the conclusion depend on the spectrum?

Machine-written by `tools/g1_compare.py`. Judged by the rules in `docs/preregistration/G1.md` Part 9.4, fixed before either notebook ran.

Both notebooks ran `g1_core.py` `110d1f534f6b2931…`, the same 6,456 eligible variants, and the same seed. The uniform control is identical in both, which is how that is known rather than assumed.

## Where the null rate comes from

| step | null rate | change |
|---|---|---|
| B6, published | 0.0923 | — |
| 3a uniform over substitutions | 0.0860 | -0.64 pp vs B6 |
| 3b uniform over base changes | 0.0788 | -0.71 pp — reachability multiplicity |
| **1 observed spectrum** | **0.0604** | -1.84 pp — context |
| **2 COSMIC SBS1+SBS5** | **0.0558** | -2.31 pp — context |

## The result under each spectrum

| | observed | null median | gap (pp) | p | α | verdict |
|---|---|---|---|---|---|---|
| **observed spectrum** | 0.0596 | 0.0604 | +0.08 | 0.40096 | 0.0125 | **vanishes** |
| **COSMIC SBS1+SBS5** | 0.0596 | 0.0558 | -0.39 | 0.91771 | 0.0125 | **vanishes** |

**The two spectra agree: vanishes** — consistent with mutational bias alone.

Agreement is what Part 9.4 calls robustness, and it is the outcome that settles the awkward part of this design: the observed spectrum's dependence on the test set stops mattering when an externally fixed spectrum reaches the same verdict.

## Fit and support

COSMIC SBS1+SBS5 reaches **cosine 0.6877** against the observed 96-channel distribution. The observed spectrum reaches 1.0 by construction, so that number is not a contest — what matters is how far COSMIC is from it, because a close fit means the non-independence of the observed spectrum is buying very little.

The observed spectrum rests on **96 of 96 channels**. Channels with little support make it noisy, and that weakens the observed arm specifically.

## What this comparison does not do

It does not rank the two spectra by p-value, and no such ranking appears above. Part 9.4 fixed that before any number existed, because whichever spectrum gave the smaller p would otherwise have an argument waiting for it.

