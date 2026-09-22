# B2 — Structural check

**Purpose.** An independent test that B1 learned *folding*.

**Logic.** A folding predictor's damage should follow burial and ignore the binding interface. A
binding predictor would do the opposite. Structure was never a model input, so the test cannot be
circular.

## Steps
1. Place every atlas variant on the 56-position GRB2-SH3 frame and average the predicted ΔΔG_fold at
   each position (positions with ≥ 10 variants).
2. Correlate that average with burial (1 − RSA) and with proximity to the peptide
   (−distance, from 2VWF).
3. Show the measured separation tables from A1 and A2 next to it: the same premise in experimental
   data.

## Expected result
Burial ρ **+0.712**; interface ρ **+0.037**. The burial signal is about 19 times the interface
signal.

## Limitation
There is only one reference frame (GRB2-SH3), so positions that align poorly to it are dropped.
