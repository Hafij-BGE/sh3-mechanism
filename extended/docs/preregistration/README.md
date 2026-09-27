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
| [E4.md](E4.md) | independent test of C4's specificity axis | **drafted 27 Sep**, unsigned |
| [E3.md](E3.md) | benchmark against current predictors | **draft — three decisions open**, see its Part 5 |

E1 is signed and its result is in. E3 and E4 have an empty `Signed off / Date / Commit` block at the
end; filling it and committing is what makes a pre-registration binding.

E4 is the one case where the pre-registration tests a pre-registration: C4's rule already returned
`validated: false`, so E4's job is to make an *independent* failure interpretable — which is why its
Part 6 declares, in advance, how to tell "the model is wrong" apart from "this data cannot answer the
question".

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

Finding these before signing is cheap. Finding them after a result exists would mean either changing
the plan retrospectively — which destroys the guarantee — or reporting a comparison that cannot
support its own conclusion.
