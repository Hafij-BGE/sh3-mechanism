# Pre-registration — Phase 3

Same rules as `extended/docs/preregistration/`, carried over unchanged:

1. **Committed before the notebook is written.** Git timestamps it.
2. **Never edited after sign-off.** Changes go in a dated amendment; the original plan's results are
   still reported.
3. **One main experiment, fixed in advance.** No experiment is promoted to main after results exist.
4. **Counting is allowed before sign-off; looking at predictions is not.**
5. **Everything is reported**, including arms that return "too few to judge".

They earned their place twice in Phase 2. E3's pre-commit leakage check disqualified ThermoMPNN
before it was run, and E4's control table stopped a wrong conclusion being drawn from a correct
number. G1 then withdrew one of the project's own published claims against a threshold fixed before
any number existed — which is the case that matters most, because it was the one where a later choice
of rule would have been worth something.

## Files

| | Program | State |
|---|---|---|
| [H1.md](H1.md) | H1 · a second domain family | **drafted 28 Sep, unsigned. Nothing run.** Main arm pools three length-matched held-out families (35 domains); PDZ is a secondary arm carrying the length confound; SH3 is the reproduction control |

H1's power calculation is the part worth reading. Resampling SH3's own per-domain spread shows that
**15 domains give a 95 % interval wider than the margin it would be compared against** — a guaranteed
"inconclusive" whatever the data said. Pooling three length-matched families to 35 domains brings the
interval to 0.148, tighter than SH3's own reference arm. That is a non-result avoided by doing the
arithmetic before the experiment rather than after, which is the same failure E1 could only report in
hindsight.

The audit answered the question and changed the experiment. PDZ is absent from training, so no
retraining is needed — but it is absent because MegaScale's assay caps constructs at 72 residues and
PDZ is longer, which would have confounded *new family* with *longer than training*. Writing H1's
rule before that was known would have pre-registered the wrong experiment.
