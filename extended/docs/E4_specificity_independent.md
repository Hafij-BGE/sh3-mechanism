# E4 — Independent test of the specificity model  *(pre-registered, notebook written)*

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
| `kazemein_jasemi_2024_TableS2_peptides.csv` | the same supplementary PDF | the 12 peptide sequences, which the Kd table does not carry |
| `pwm_profiles.csv`, `specificity_cv.csv`, `specificity_decision.json` | C4 (frozen) | the profiles, the folds and the recorded verdict |

The Kd table was extracted from Table S6 of the supplementary PDF; both the count (45) and the range
(0.2–125 µM) match the paper exactly, which is the check that the parse is right. See
`DATA_PROVENANCE.md` §8 — the publisher's download is bot-blocked and the file came from Europe PMC.

## Method

Pre-registered in [preregistration/E4.md](preregistration/E4.md), committed before the notebook was
written. Three things had to be settled first.

**The axis is compositional, not positional.** C4 collapses each 14 × 20 phage-display PWM to a single
information-content-weighted 20-vector, and the Ridge head predicts *that*. So it can say "this domain
prefers proline, tryptophan and leucine" but not "position 4 must be basic". Peptides are therefore
scored as `S(d,p) = Σ_a f_p(a)·profile_d(a)` — mean predicted log-preference per residue, no window and
no alignment. Two peptides with the same composition in a different order are indistinguishable to this
model by construction, which bounds what a positive result could mean.

**12 of the 17 measured domains are in C4's training set.** Scoring them with the final model would be
scoring the training data. E4 re-runs C4's own cross-validation — same ≥ 40 % identity clustering, same
per-fold alpha selection, verified to reproduce the recorded median centred r — and uses the
**leave-cluster-out** prediction for those 12 (37 measurements). Four domains C4 never saw (ABI1, DLG2,
NCK1-3, SORBS1-1; 7 measurements) use the final model. ARHGEF30 is excluded: it is not in our 235-gene
UniProt SH3 table, so we have no domain sequence. **44 measurements, 16 domains.**

**A control decides what a failure means.** Every experiment is repeated with the domain's own
*observed* phage-display profile. If the observed profile fails too, the honest claim is about the data
— phage-display compositional preferences do not predict these affinities — not about C4's model. That
reading is fixed in the pre-registration so it cannot be chosen after the fact.

Main test: within-domain-centred correlation over the 12 trained-on domains (df = 24), which removes
every domain-level effect and leaves only specificity. A verdict of yes needs p < 0.025 **and** a larger
|r| than the domain-agnostic average profile.

## Expected outcome, stated in advance
**Failure.** C4 failed internally, and there is no reason to expect it to pass externally. That is the
point: a second, *independent* failure is a stronger negative result than one internal failure. "The
specificity axis does not predict measured SH3 affinities" is a cleaner claim than "our specificity
axis did not pass our own threshold".

If it unexpectedly succeeds, that is a finding — and it must be reported as a **post-hoc** result,
because C4's rule was already declared and already failed.

## Scale, stated before the result exists
44 measurements across 16 domains is small. At df = 24 the main test can only detect **|r| ≥ 0.44**, and
the 8-domain sign test reaches 0.025 **only at 8/8**. So a null means "no effect large enough for 44
measurements to see", never "no effect". The negative result this program expects is worth having
because it is *independent*, not because it is precise.
