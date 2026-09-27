# E3 — analysis (Experiment 1, base)

Run 27 September 2026, 15:53. Machine numbers in `RESULTS_E3_exp1.md` and `metrics_E3_exp1.json`;
the plan they were judged against is `docs/preregistration/E3.md` @ `ccd3446`, committed before the
notebook existed.

**Both verdicts are in.** ThermoMPNN, which carries no verdict by design, still has not run.

---

## The result

| competitor | median per-domain ρ | ours | median paired diff | Wilcoxon p | verdict |
|---|---|---|---|---|---|
| **SaProtΔG** | +0.855 | +0.839 | −0.028 | 0.107 | **no clear difference** |
| **ESM3ΔG** | +0.792 | +0.839 | **+0.033** | **0.0084** | **ours better** |

α = 0.025 (0.05 across the two competitors carrying a verdict). **27,590 variants scored by each, 0
dropped** — the entire held-out set, not a favourable subset.

**The asymmetry is what makes this worth reporting.** Our head is sequence-only and saw no SH3 domain
in training. Both competitors receive the experimentally determined 3D structure of the exact
construct that was measured. On that footing we are indistinguishable from one and ahead of the other.

## ESM3ΔG — a pre-registered win, and a fragile competitor

Ours is better on **12 of 15 domains**:

| gene | n | ESM3ΔG | ours | ours − ESM3ΔG |
|---|---|---|---|---|
| DOCK1 | 1,208 | 0.460 | 0.774 | **+0.314** |
| PTK6 | 1,125 | 0.515 | 0.829 | **+0.314** |
| SPTAN1 | 10,112 | 0.683 | 0.872 | +0.189 |
| TEC | 1,072 | 0.684 | 0.839 | +0.156 |
| FYN | 2,187 | 0.841 | 0.934 | +0.093 |
| OBSCN | 1,209 | 0.665 | 0.754 | +0.089 |
| BTK | 1,060 | 0.768 | 0.855 | +0.087 |
| OSTF1 | 1,028 | 0.812 | 0.845 | +0.033 |
| HCK | 1,034 | 0.823 | 0.845 | +0.021 |
| SORBS1 | 1,210 | 0.777 | 0.797 | +0.020 |
| NPHP1 | 2,212 | 0.831 | 0.842 | +0.010 |
| LYN | 1,014 | 0.820 | 0.822 | +0.002 |
| LCK | 983 | **0.843** | 0.837 | −0.007 |
| PLCG1 | 1,091 | **0.792** | 0.772 | −0.020 |
| LASP1 | 1,045 | **0.892** | 0.844 | −0.048 |

**The spread is the story, not the median.** ESM3ΔG ranges **0.460 to 0.892**; we range 0.754 to
0.934. At its best it beats us (LASP1 0.892); at its worst it collapses (DOCK1 0.460, PTK6 0.515).
Our worst domain is better than ESM3ΔG's fifth-worst.

That is a consistency claim, and it is the more useful one for the project. The 410 confident calls in
B3 depend on the head behaving similarly across domains, not on a good average.

## SaProtΔG — no clear difference, competitor nominally ahead

Nominally ahead on 11 of 15 domains, median gap 0.028, p = 0.107. The pre-registration warned that 15
domains detects large gaps and not small ones, so this is *"no clear difference, with SaProtΔG
nominally ahead"* — not parity, and not a win for us. Part 3 said a competitor win would be reported
plainly, and this is as close as the data comes to one.

Notably, **SaProtΔG and ESM3ΔG disagree with each other more than either disagrees with us on
average.** SaProtΔG holds 0.755–0.915 while ESM3ΔG swings 0.460–0.892, on identical inputs. Whatever
ESM3ΔG is doing on DOCK1 and PTK6, SaProtΔG is not doing it (0.780 and 0.835 there).

## What the two together license

*On 15 SH3 domains held out from training, a sequence-only ΔΔG head is statistically indistinguishable
from SaProtΔG and significantly better than ESM3ΔG, with both competitors given the measured
construct's experimental structure and 27,590 variants scored by all three with none dropped.*

That closes objection 1 — "you only beat zero-shot ESM-2, FoldX and EVE" — against two current
supervised predictors, one of them by a pre-registered test.

**What it does not license.** Not "state of the art": SaProtΔG is nominally ahead, and 15 domains
cannot resolve a 0.03 gap. Not a claim about ESM3 the base model — ESM3ΔG is a LoRA stability head on
top of it, and its failure on DOCK1 is a property of that head on that domain, not of ESM3.

## The leakage audit, which stands independently

| competitor | held-out domains in its published training data |
|---|---|
| SaProtΔG | 0 of 15 |
| ESM3ΔG | 0 of 15 |
| **ThermoMPNN** | **13 of 15** (12 train, 1 val) |

**23,191 of 27,590 held-out variants sit in ThermoMPNN's own train or validation split.** A benchmark
that had simply run all four competitors would have reported a MegaScale-trained model scoring its own
training data against our held-out set. Scope, unchanged: this is the *published* split, not whatever
the released weights saw.

## Two checks that make the run believable

- **Our numbers were re-derived, not copied.** The notebook recomputes the 15 per-domain ρ from B1's
  frozen predictions and asserts they reproduce `folding_per_domain_ci.csv`. Median +0.839, exact.
- **Sign alignment is visible, not fitted.** Unaligned medians were −0.855 and −0.792; aligned, +0.855
  and +0.792. The negation came from each source's documented convention, and both numbers are printed.

Added during the run and worth recording: the scan was batched 16-wide after proving it reproduces the
library's batch-1 result to 1.6 × 10⁻⁵, and every scan is cached per construct — which is why adding
ESM3ΔG cost only ESM3ΔG's own time.

## Still outstanding

**ThermoMPNN.** The `datasets` import collision is fixed and it now runs, but it fails on position
mapping: *no consistent offset for 1A0N.pdb_L7S*. The offset search tried 0, +1 and −1, assuming its
positions index the parsed chain; for 1A0N chain B they are PDB author numbering, which starts far
from any of those. Now derived from the data — every index carrying the first wild-type residue gives
a candidate offset, each tested against all positions — rather than guessed. Descriptive arm only, so
nothing in the table above depends on it.

**Experiments 2, 3 and 4** — augmented weights, AlphaFold structures, per-seed spread. All scans
cached, so each costs only its own new work.
