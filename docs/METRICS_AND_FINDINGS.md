# What every number in this project means, and what was found

A reader's guide. It exists because the project reports several correlations that look comparable and
are not, and because a metric quoted without its comparator is close to meaningless.

Covers all three phases. **Phase 3 (H) results are marked provisional** — they have not been promoted
into the manuscript.

---

# Part 1 — The metrics

## 1.1 ΔΔG_fold — what the model predicts

**Change in folding free energy on mutation, in kcal/mol. Positive means destabilising.**

A variant at +3 kcal/mol is predicted to make the domain substantially less stable; one at 0 is
predicted to do nothing. The sign convention is ours: the MegaScale training data uses the opposite
sign and is negated on load.

The model is a supervised head — 1,292 → 512 → 128 → 1 — on **frozen** ESM-2 650M embeddings plus
twelve scalars. It was trained on ~361,000 non-SH3 substitutions and **never saw an SH3 domain**.

**Structure is not an input.** That is deliberate: MegaScale has no structure on any of its rows, and
a model using structure would train on one distribution and predict on another. It also keeps the
structural check (B2) independent.

## 1.2 Spearman ρ — how well the ranking matches

**A rank correlation. It asks whether the model puts variants in the right order, not whether it gets
the numbers right.**

ρ = 1 is a perfect ordering, 0 is no relationship, −1 is perfectly reversed. Rank rather than linear,
because the practical question is *"which variants should I worry about"*, not *"is the prediction
3.1 or 3.4"*.

**Per-domain** ρ is computed within one domain and then summarised across domains (usually the
median). This matters: pooling all variants from all domains inflates the correlation, because much
of the spread is *between* domains rather than within them. Per-domain is the harder and more honest
measure.

## 1.3 |ρ| — why some correlations are reported as absolute values

Against Domainome, the model correlates **negatively** by construction: a destabilising variant
(high ΔΔG) produces **low** abundance. The magnitude is the signal and the sign is bookkeeping, so
those comparisons report |ρ|.

Against MegaScale ΔG, both quantities run the same way, so ρ is reported signed and positive.

## 1.4 The three headline correlations are not comparable

**This is the single most important thing in this document.** Three numbers recur and are routinely
mistaken for one another:

| number | what it is | measured against | comparable to |
|---|---|---|---|
| **0.839** | median per-domain ρ, 15 held-out SH3 domains | **MegaScale ΔG** — the same assay type the model was trained on | other predictors on the same 15 domains (E3) |
| **0.600** | pooled \|ρ\|, 880 atlas variants | **Domainome abundance** — a different assay measuring a different quantity | the 0.709 noise ceiling |
| **0.623** | median per-domain \|ρ\|, 36 SH3 domains | **Domainome abundance**, every variant | H1's other families |

0.839 is higher than 0.600 **not because the model got worse**, but because the second compares a
folding-energy prediction to a cellular-abundance measurement from a different laboratory using a
different technique. Quoting them side by side as though the model "dropped from 0.84 to 0.60" would
be wrong.

## 1.5 The noise ceiling — the number that makes 0.600 interpretable

**How well two independent experiments agree with each other. No predictor can beat it.**

For SH3, MegaScale and Domainome agree at **|ρ| = 0.709**. So 0.600 is **85 % of the achievable
limit**, not a moderate result — and on matched variants the model reaches 90–113 % of it.

This is why H1's new families are weaker evidence: they have **no second assay**, so no ceiling
exists for them and a raw correlation cannot be placed against what is achievable.

## 1.6 Conformal intervals, `fold_lo`, and the 410

**A calibrated uncertainty, not a confidence interval in the textbook sense.**

Split-conformal prediction converts the ensemble's disagreement into an interval with a guaranteed
coverage rate. The quantile is **q90 = 6.807**, and each variant gets

```
fold_lo = predicted ΔΔG − q90 × (ensemble SD + 0.05)
```

**`fold_lo ≥ 1` is the "confidently destabilising" call**, and **410 of 6,884 atlas variants (6.0 %)**
meet it.

Two findings qualify that number, and both should travel with it:

- **E1: sensitivity is 4.8 %** on known pathogenic variants. A 90 % *lower bound* is deliberately
  conservative — it is a shortlisting tool, not a clinical filter.
- **G2: coverage is 90 % on average, not per domain.** It runs 83.3 % (LYN) to 95.0 % (FYN), and the
  per-domain quantile varies by a factor of **1.79**. The **aggregate count is robust** (410, with a
  resampled band of 378–421); the **per-variant claim is not**.

## 1.7 Effect sizes and thresholds

| | |
|---|---|
| **Rank-biserial** | effect size for a group comparison. **+0.615** for pathogenic vs benign ≈ AUC 0.81: pick one of each at random and the pathogenic one scores higher 81 % of the time |
| **α** | the significance threshold, Bonferroni-corrected per analysis over the comparisons carrying a verdict — 0.025 with two, 0.0167 with three, 0.0125 with two co-primary arms |
| **Margin (−0.15)** | H1 tests *non-inferiority*, not significance. "Comparable accuracy" cannot be shown by failing to reject a null, so a margin is required. −0.15 is one SD of SH3's own domain-to-domain spread |
| **Percentage points (pp)** | differences between two percentages. 5.96 % vs 6.04 % is a gap of 0.08 **pp**, not 0.08 % |

## 1.8 Assay quality (H1.3) — and what it is not

`median(|fitness| / replicate σ)` per domain: how large a measurement is relative to its own
reproducibility. **It is not a noise ceiling.** It compares a measurement to itself, not to an
independent experiment, so a family with consistent, precise and systematically *wrong* measurements
scores well.

---

# Part 2 — The findings

## 2.1 What holds

| finding | number | where |
|---|---|---|
| **Per-domain folding accuracy on held-out SH3** | median ρ **0.839**, 15 domains | Phase 1, re-derived in E3 |
| **Beats zero-shot ESM-2** | 15 of 15 domains | Phase 1 |
| **Level with a current structure-conditioned predictor** | SaProtΔG 0.855 vs ours 0.839, p = 0.107 | E3 |
| **Better than another** | ESM3ΔG 0.792 vs 0.839, **p = 0.0084** | E3 |
| **Agrees with an independent abundance assay** | pooled \|ρ\| **0.600**, 85 % of the 0.709 ceiling | E2 |
| **Separates clinical labels it never saw** | median ΔΔG 1.67 vs 0.19, **p = 4.9 × 10⁻⁶** | E1 |
| **Confident calls are robust in aggregate** | 410, band 378–421 | G2 |

**Both competitors in E3 receive the experimental structure of the measured construct. Ours is
sequence-only and saw no SH3 domain in training.** Consistency is the real difference: ESM3ΔG ranges
0.460–0.892 across domains, ours 0.754–0.934 — our worst domain beats its fifth-worst.

## 2.2 What was withdrawn

**The cancer-variant depletion.** Phase 1 reported 5.93 % destabilising against 9.18 % expected
(p = 0.001) and offered it as consistent with purifying selection — while stating that a
trinucleotide-aware null was needed first.

G1 built that null. **The effect vanishes**: 5.96 % observed against 6.04 % expected, **p = 0.40**,
with a second independently specified mutational spectrum agreeing (p = 0.92). Decomposed:

| null | rate | change | p |
|---|---|---|---|
| Phase 1, amino-acid-pair reachability | 0.0923 | — | 0.001 |
| codon reachability | 0.0860 | −0.64 pp | 0.0001 |
| + reachability multiplicity | 0.0788 | −0.71 pp | 0.0001 |
| **+ trinucleotide context** | **0.0604** | **−1.84 pp** | **0.401** |

**The depletion survives both reachability corrections and dies on sequence context alone** — the
exact test the original report said was missing. **The claim was mutational bias, and it is
withdrawn.**

## 2.3 What was never supported

**The binding-specificity axis.** It failed its own pre-registered rule internally (C4), and E4
tested it against 44 independently measured affinities: model r = **+0.023** (p = 0.91).

**The control is what makes E4 useful.** The *observed* phage-display profile — the quantity the
model is trained to predict — fails identically (r = −0.051). A predictor of X cannot beat X, so no
improvement to the regression could have helped. The verdict is *the representation, not the model*:
collapsing a 14-position matrix to composition discards order, and SH3 ligand classes differ by order
at identical composition.

## 2.4 What Phase 3 found — provisional

| | |
|---|---|
| **PDZ, never seen, longer than anything in training** | 0.602 vs SH3's 0.623 (Δ −0.021) |
| Three other unseen families | 0.420 — **inconclusive** at the margin |
| Is it measurement quality? | **No.** Matched, Δ moves only −0.203 → −0.187 |
| Is it construct length? | **No.** PDZ's median is 88 residues against a training maximum of 72 |

**The 72-residue ceiling is a limitation of the method that had never been stated.** MegaScale's
proteolysis assay caps constructs there, so the model has never seen a longer domain. SH3 (54–67)
sits comfortably inside; most human domain families do not.

**Myb/SANT is the informative case:** better measurements than SH3 (2.535 vs 2.086) and lower
accuracy (0.507 vs 0.623). Whatever limits the main arm, it is neither length nor noise — and it is
not yet named.

---

# Part 3 — Is this good research?

An honest assessment, including where it is weak.

## 3.1 What is genuinely strong

**Pre-registration that cost something.** Six programs had their decision rule committed to git
before the analysis code existed. It was not decorative:

- **E3** disqualified ThermoMPNN *before* running it — 13 of our 15 held-out domains sat in its
  published training split.
- **E4's** control table stopped a wrong conclusion being drawn from a correct number.
- **G1** overturned one of the project's own headline claims against a threshold fixed beforehand,
  with the outcome labels — including "the claim is withdrawn" — written in advance.
- **H1's** power calculation showed the original 15-domain design would have returned "inconclusive"
  whatever the data said, and the arm was redesigned before running.

**A frozen run that was never touched.** Every evaluation reads the 22 September outputs and asserts
they reproduce. 187/187 recorded values still hold. No number was re-fitted to make anything work.

**Negative results reported at the same weight as positive ones.** The specificity axis, the 4.8 %
sensitivity, the withdrawn depletion, and H1's inconclusive arm are all in the record with their
numbers.

**Checks that caught real defects.** Four position-index bugs, a mislabelled predictor table, a
cached-failure bug in data acquisition, a join that silently lost 97 % of its rows. Each produced a
*smaller, plausible, internally consistent* result rather than an error — which is exactly the class
that survives to publication when nobody asserts anything.

## 3.2 Where it is weak

**One family, mostly.** Phases 1 and 2 are entirely SH3. H1 begins to address this and the answer is
partial.

**Abundance is not ΔΔG.** The external validation measures cellular abundance, which is a proxy.

**Small clinical numbers.** E1 rests on 21 pathogenic and 101 benign variants — enough for a large
effect and nothing finer.

**No wet-lab validation.** The panel exists (G4) and is ready; nothing has been measured at the
bench.

**Some structural annotation is missing.** 3.2 % of the atlas, because AlphaFold DB has no model for
nine very large proteins.

## 3.3 The verdict

**Yes — with the scope stated honestly.**

This is not a breakthrough method. It is a **carefully validated, competitive one**, and the
validation is the contribution. A sequence-only model matching structure-conditioned predictors on
held-out domains is a real result. Reaching 85 % of the assay-to-assay ceiling is a real result.

**What raises it above a competent methods paper is the discipline**: a leakage audit that
disqualified a competitor before it ran, a control that reinterpreted a negative result correctly, and
a pre-registered test that killed one of its own claims. Very few computational papers do the last
one, and it is the most persuasive thing in the record — because a reader who sees you retract your
own headline has reason to believe the ones you kept.

**The honest framing is:** *a sequence-only stability predictor, validated against four independent
external sources, competitive with structure-conditioned methods, with one prior claim withdrawn and
its limits mapped.* That is publishable and defensible. It is not "we solved variant effect
prediction", and the write-up should not drift toward that.

---

*Phase 3 results are provisional and not in the manuscript. Everything else is in
`extended/docs/OUTCOMES.md` and `extended/docs/MANUSCRIPT.md`.*
