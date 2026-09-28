# Pre-registration

A pre-registration fixes the analysis **before** the result exists: which comparison decides the
answer, what counts as a yes, and how the table will be read. It is committed to git first, so the
timestamp proves the order. Only then is the notebook written.

## Why this project does it

C4. It built a specificity axis, tested it, and returned `validated: false` — median centred
r = +0.288, better than the family-average profile on only 55 of 115 domains. That verdict is
trustworthy **because the rule was declared first**:

```json
"rule": "CI of median centred r above 0 AND sign test vs average profile p < 0.05"
```

Had the threshold been chosen afterwards, +0.288 could have been written up as a modest success. The
same discipline is why C2 carries `binding_decision.json`.

Every program in this phase with a pass/fail verdict gets the same treatment.

## The rules

1. **Committed before the notebook is written.** Git timestamps it.
2. **Never edited after sign-off.** Changes go in a dated amendment; the original plan's results are
   still reported.
3. **One main experiment, fixed in advance.** The others are sensitivity checks. No experiment is
   promoted to main after results are seen.
4. **Counting is allowed before sign-off; looking at predictions is not.** Group sizes decide whether
   a test is even possible, so they are filled in first.
5. **Everything is reported**, including arms that return "too few to judge".

## Files

| | Program | State |
|---|---|---|
| [E1.md](E1.md) | ClinVar and gnomAD | **signed, run, reported.** Decisions in Part 6, amendment in Part 7; result in `results/E1_clinvar_gnomad/` |
| [E4.md](E4.md) | independent test of C4's specificity axis | **run and reported.** Both verdicts no; the Part 6 control attributes the failure to the representation, not the model |
| [E3.md](E3.md) | benchmark against current predictors | **decisions taken (Part 6), unsigned.** The pre-commit leakage check disqualified ThermoMPNN |
| [G1.md](G1.md) | trinucleotide-aware null for the cancer depletion | **drafted 28 Sep, unsigned. Nothing run.** The only route to objection 2 |

E1 is signed and its result is in. E3 and G1 have empty `Signed off / Date / Commit` blocks; filling
them is what makes a pre-registration binding.

G1 is the one that can cost the project a published claim. It re-tests the frozen run's 5.93 % vs
9.18 % depletion against a null that knows the sequence context each mutation arose in — which is
what B6 itself said was needed before calling the result selection. Part 4 fixes all three outcomes in
advance, including the one where the claim is withdrawn, and Part 5 establishes that a null result
would be informative rather than ambiguous: at n = 6,456 the test can see a gap a fifth the size of
the one B6 reported. That matters because "underpowered" was the honest verdict on E1's attempt at the
same objection, and it does not carry over.

E4 is the one case where the pre-registration tests a pre-registration: C4's rule already returned
`validated: false`, so E4's job was to make an *independent* failure interpretable — which is why its
Part 6 declared, in advance, how to tell "the model is wrong" apart from "this data cannot answer the
question".

**That control earned its place.** Both of E4's verdicts came back no, and without Part 6 the obvious
write-up would have been "the specificity axis fails an independent test". The control shows the
*observed* phage-display profile fails the same test, so the honest claim is narrower and better
founded: composition is the wrong representation, and no improvement to the model could have changed
the result. A rule written afterwards could not have made that distinction credibly.

## What the 27 Sep review changed

Both drafts were checked against the data before signing — which is the point of the counting rule,
and it caught three things that would otherwise have surfaced *after* a result existed:

- **E1's group sizes are small.** 21 disease-causing variants at the main setting, 4 at the stricter
  one, 3 in the atlas-only arm. Experiments 2 and 6 cannot return a verdict, and **the stated
  fallback (Experiment 6) cannot answer Question 1 at all**.
- **E1's primary definition of "common" cannot be computed** — popmax is not in X0's gnomAD export,
  so the fallback would fire every time.
- **E3 assumed ThermoMPNN and ProteinDPO predictions were in hand.** They cover 26 proteins with
  **zero overlap** with our 15 held-out domains.

And the follow-up check that decision forced, run before E3's Part 6 was committed, found something
larger: **13 of our 15 held-out domains sit in ThermoMPNN's own published training or validation
split.** Running it as a competitor would have scored its training data against our held-out set. It
is now reported descriptively on the 2 clean domains, with no verdict, and the audit itself is
reported as a result.

Finding these before signing is cheap. Finding them after a result exists would mean either changing
the plan retrospectively — which destroys the guarantee — or reporting a comparison that cannot
support its own conclusion.
