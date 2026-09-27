# E3 — analysis (Experiment 1, base)

Run 27 September 2026. Machine numbers in `RESULTS_E3_exp1.md` and `metrics_E3_exp1.json`; the plan
they were judged against is `docs/preregistration/E3.md` @ `ccd3446`, committed before the notebook
existed.

**E3 is half done.** One of the two competitors that carry a verdict ran. See "What is still missing".

---

## The result

| | median per-domain ρ |
|---|---|
| SaProtΔG (base, 3 seeds averaged) | **+0.855** |
| ours (B1, frozen) | **+0.839** |
| median paired difference | **−0.028**, in SaProtΔG's favour |
| paired Wilcoxon, 15 domains | **p = 0.107** against α = 0.025 |

**Verdict, by the rule fixed in advance: no clear difference.**

**27,590 variants scored, 0 dropped.** Every held-out variant in the test set got a score from both
models, so this is not a comparison on a favourable subset — it is the whole thing.

## What this does and does not license

**Says:** across 15 held-out SH3 domains, no gap large enough for this test to see separates our model
from SaProtΔG. Our head is **sequence-only** and was trained on non-SH3 MegaScale variants;
SaProtΔG receives **the experimentally determined 3D structure of the exact construct that was
measured**. Being within 0.03 median Spearman of that, with no structural input at all, is the result
worth reporting.

**Does not say "we match the state of the art".** The nominal direction favours SaProtΔG on **11 of
15 domains**, and a sign test on that split gives p ≈ 0.12 — the same story as the Wilcoxon. The
pre-registration warned that 15 domains detects large gaps and not small ones; a median gap of 0.028
is exactly the size this design cannot resolve. The honest sentence is *"no clear difference, with
the competitor nominally ahead by a median 0.028"*, and Part 3 of the plan said in advance that a
competitor win would be reported plainly.

## Per-domain

| gene | n | SaProtΔG | ours | ours − SaProtΔG |
|---|---|---|---|---|
| SPTAN1 | 10,112 | 0.755 | **0.872** | **+0.116** |
| FYN | 2,187 | 0.879 | **0.934** | +0.055 |
| TEC | 1,072 | 0.830 | **0.839** | +0.009 |
| BTK | 1,060 | 0.8548 | **0.8549** | +0.0001 |
| PTK6 | 1,125 | **0.835** | 0.829 | −0.006 |
| DOCK1 | 1,208 | **0.780** | 0.774 | −0.006 |
| NPHP1 | 2,212 | **0.858** | 0.842 | −0.016 |
| OSTF1 | 1,028 | **0.874** | 0.845 | −0.030 |
| LYN | 1,014 | **0.853** | 0.822 | −0.031 |
| LCK | 983 | **0.877** | 0.837 | −0.040 |
| SORBS1 | 1,210 | **0.846** | 0.797 | −0.049 |
| PLCG1 | 1,091 | **0.832** | 0.772 | −0.060 |
| LASP1 | 1,045 | **0.915** | 0.844 | −0.071 |
| OBSCN | 1,209 | **0.865** | 0.754 | −0.111 |

Two observations, offered as observations and not promoted to findings — the pre-registration fixed
one main test and this is not it:

- **SPTAN1 is 10,112 of the 27,590 variants — 37 % of the test set — and it is SaProtΔG's worst
  domain (0.755) and one of our best (0.872).** SPTAN1 is also the domain measured across ten
  separate MegaScale constructs. Whether structure-conditioned models struggle where one domain is
  represented by many near-identical constructs is a question this run raises and does not answer.
- **Our two clear wins, SPTAN1 and FYN, are the two largest domains in the set.** The median treats
  every domain equally, which is what the plan specified; a variant-weighted comparison would look
  more favourable to us and was *not* pre-registered, so it is not reported as a result.

## The leakage audit is the more durable half of E3

| competitor | held-out domains in its published training data |
|---|---|
| SaProtΔG | 0 of 15 |
| ESM3ΔG | 0 of 15 |
| **ThermoMPNN** | **13 of 15** (12 train, 1 val) |

This stands regardless of what the comparison returns. **23,191 of 27,590 held-out variants sit in
ThermoMPNN's own training or validation split**, so a benchmark that had simply run all four
competitors would have reported a MegaScale-trained model scoring its own training data against our
held-out set. Any SH3 or MegaScale-derived benchmark needs this check before it means anything.

Scope, unchanged from Part 1: this establishes presence or absence in the **published** split, not in
whatever the released weights actually saw.

## What is still missing

| | state | why it matters |
|---|---|---|
| **ESM3ΔG** | **not run** — gated model, no `HF_TOKEN` | the second verdict. E3 is incomplete without it |
| **ThermoMPNN** | **not run** — import collision, now fixed | descriptive only; its absence costs little, since the audit already did the work |
| Experiments 2, 3, 4 | not run | augmented weights, AlphaFold structures, per-seed spread |

ThermoMPNN failed on a name collision, not on anything about the model:

```
from datasets import Mutation
ImportError: cannot import name 'Mutation' from 'datasets'
```

ThermoMPNN ships its own `datasets.py`, but `custom_inference.py` only *appends* the repo root to
`sys.path`, so Hugging Face's `datasets` package wins. Fixed by setting `PYTHONPATH`, which is
searched before site-packages.

**Every SaProtΔG scan is cached**, so completing E3 costs only ESM3ΔG's own runtime plus a few minutes
for ThermoMPNN. Nothing already computed is repeated.

## Two checks that make this run believable

- **Our own numbers were re-derived, not copied.** The notebook recomputes the 15 per-domain ρ from
  B1's frozen predictions and asserts they reproduce `folding_per_domain_ci.csv`. Median +0.839
  matches B1 exactly.
- **The sign alignment is visible, not fitted.** The unaligned median correlation was **−0.855** and
  the aligned one **+0.855**. The negation came from SaProtΔG's documented convention (ΔG on a
  higher-is-more-stable scale, so ΔΔG negative = destabilising), not from whichever direction scored
  better. Both numbers are printed so a reader can check that.

## Effect on the plan

**Objection 1 — "you only beat zero-shot ESM-2, FoldX and EVE" — is partly closed.** Against one
current supervised ΔG predictor, on 15 domains it never saw, there is no clear difference. Closing it
fully needs ESM3ΔG, which needs the licence accepted and a token set.
