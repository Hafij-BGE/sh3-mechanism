# B6 — Analysis of the result: virtual saturation mutagenesis

**Colab run:** 2026-09-22, 1.9 min on CPU. **New program:** there are no recorded values to compare. It ran
without errors on first use.
The run's own numbers are in `RESULTS_B6.md`, `metrics_B6.json` and `comparison_B6.csv`, plus the per-domain
landscape tables. The per-variant table stays on Drive.

---

## 1. The question

The atlas holds only the 6,884 substitutions that happened to be reported in COSMIC. B6 predicts **every
possible single amino-acid substitution** in all 310 SH3 domains of the atlas, with the same B1 model and B3
intervals. This gives:
1. **a resource:** a predicted folding landscape for every human SH3 domain in the atlas;
2. **a proper background:** are the observed cancer variants more or less damaging than what *could* have occurred in the same domains?

**Single-nucleotide reachability.** Most cancer missense mutations change one DNA base. Each substitution is
flagged by whether one base change in some codon of the wild-type amino acid can produce it, from the genetic
code. The comparison then uses only reachable substitutions: a like-for-like background.

---

## 2. Consistency check

| | |
|---|---|
| Virtual substitutions predicted | **366,168** (310 domains × every position × 19 alternatives) |
| Max difference from B1 for the 6,884 observed variants | **9.5 × 10⁻⁷** kcal/mol |

The observed variants, predicted again inside the virtual scan, match B1 to below 10⁻⁶. That is float
rounding. The scan uses exactly the same model and features as the rest of the pipeline.

---

## 3. Observed cancer variants against every possible substitution

Destabilising = lower 90 % interval bound ≥ 1 kcal/mol (as in B3).

| Set | Substitutions | Destabilising | Median predicted ΔΔG_fold |
|---|---|---|---|
| All possible | 366,168 | **12.1 %** | 0.77 |
| Single-nucleotide-reachable | 150,040 (41 %) | **9.2 %** | 0.65 |
| **Observed in cancer** | 6,884 | **6.0 %** | 0.55 |

**Interpretation:**
- **Reachable substitutions are milder than all possible ones** (9.2 % vs 12.1 %). The genetic code places many chemically drastic changes two or three bases away. For example, a hydrophobic residue often cannot reach a charged one in one step. This is why the fair background is the reachable set.
- **Observed cancer variants are milder still** (6.0 %) than the reachable background (9.2 %).

---

## 4. Domain-matched test: are observed variants depleted of damage?

Each draw takes random reachable substitutions from the **same domains**, in the same numbers, as the observed
cancer variants. There are 1,000 draws.

| | Destabilising |
|---|---|
| Observed reachable cancer variants | **5.93 %** |
| Random reachable substitutions, same domains (median of 1,000 draws) | **9.18 %** |
| One-sided p (observed depleted) | **0.001**, the smallest possible with 1,000 draws |

**Interpretation — the most interesting new result, and one to state carefully:**
- **Cancer variants are *less* often fold-breaking than chance predicts** (about a third fewer: 5.9 % vs 9.2 %). This holds within the same domains and among single-base changes. None of the 1,000 random draws was as mild as the observed set.
- **Two explanations are possible, and this test cannot separate them:**
  1. **Weak purifying selection.** Fold-breaking SH3 variants may harm the tumour cell (many SH3 proteins are needed for signalling and the cytoskeleton), so they are seen less often.
  2. **Mutational bias.** The processes that dominate the atlas (A0: C>T from UV and mismatch-repair deficiency) favour particular codon changes. If those changes happen to produce milder substitutions or hit exposed positions more often, observed variants would look milder without any selection. **Codon usage and trinucleotide context are not modelled here.**
- **It agrees with B5 in direction:** cancer variants are somewhat less frequent at buried positions (ρ −0.18), and their counts do not follow predicted damage. **B5 found no *enrichment*** (no selection *for* loss of fold). **B6 finds *depletion***, which, if it is selection at all, points the opposite way: against loss of fold.
- **How the thesis should report it:** "Observed SH3 cancer variants are depleted of predicted fold-breaking substitutions relative to a domain-matched, single-nucleotide background (5.9 % vs 9.2 %, p ≤ 0.001). This is consistent with weak purifying selection, but mutational context was not modelled, and a trinucleotide-aware null is needed before claiming selection."

---

## 5. Family map: where the SH3 fold is most fragile

The 15 aligned positions (GRB2-SH3 frame) with the highest mean predicted damage over all domains:

| Ref. position | Domains | Mean predicted ΔΔG | Destabilising | Observed cancer variants | Buried | Interface |
|---|---|---|---|---|---|---|
| 19 | 304 | 2.52 | 52.5 % | 63 | yes | no |
| 25 | 307 | 2.35 | 48.9 % | 74 | yes | no |
| 47 | 309 | 2.31 | 50.6 % | 88 | yes | no |
| 5 | 310 | 2.23 | 42.8 % | 127 | yes | no |
| 27 | 308 | 2.15 | 44.0 % | 96 | yes | no |
| 38 | 310 | 1.98 | 28.2 % | 146 | yes | no |
| 9 | 310 | 1.95 | 31.4 % | 85 | yes | yes |
| 17 | 307 | 1.94 | 39.0 % | 49 | yes | no |
| 45 | 309 | 1.92 | 21.8 % | 123 | yes | no |
| 36 | 310 | 1.92 | 33.3 % | 83 | yes | no |
| 22 | 306 | 1.88 | 25.0 % | 155 | no | no |
| 52 | 303 | 1.84 | 29.1 % | 107 | yes | no |
| 51 | 304 | 1.78 | 20.0 % | 78 | no | yes |
| 3 | 309 | 1.73 | 25.0 % | 101 | yes | no |
| 35 | 310 | 1.62 | 14.9 % | 85 | no | yes |

**Interpretation:**
- **12 of the 15 most fragile positions are buried.** Across all aligned positions, family-wide predicted damage follows burial at **ρ +0.775**. That is even stronger than B2's +0.712, which used only the observed variants. The whole-family scan confirms the structural logic of B2 without relying on which variants COSMIC happened to record.
- **At the top positions, about half of all possible substitutions are confidently destabilising** (positions 19, 25, 47: 49–53 %). All three are buried (relative accessibility 0–0.06), so they are likely part of the SH3 hydrophobic core.
- **Observed cancer variants at these positions** range from 49 to 155. Cancer variants do occur at fragile positions, but not preferentially (B5, and Section 4 above).

---

## 6. The resource

For every one of the 310 SH3 domains in the atlas, B6 provides:
- the predicted ΔΔG_fold of all 19 substitutions at every position, with a 90 % interval and a destabilising call;
- a single-nucleotide-reachability flag;
- the position in the common GRB2-SH3 frame.

A future cancer or germline variant in any of these domains can therefore be looked up without re-running the
model. **Per-domain summaries can go to GitHub. The full per-variant table stays on Drive**, like all
per-variant tables, to keep the repository light. The virtual variants are not COSMIC data, but they are keyed
to COSMIC-derived domains.

---

## 7. Limitations

- **The mutational null is simplified:** single-nucleotide reachability, but no codon usage, trinucleotide context or mutational signatures. The depletion in Section 4 needs a context-aware null before it can be called selection.
- **The same model limits apply as in B1/B3:** compression of severe effects, weakest on glycine and proline, isolated-domain scoring.
- **Binding is not predicted** (Part C). The landscape covers folding only.
- **3 of the 15 top positions (22, 51 and 35) are exposed.** Their high predicted damage may reflect backbone or turn roles, which burial alone does not capture.

---

## 8. Conclusion and next step

- **366,168 substitutions predicted:** a complete folding landscape for all 310 atlas SH3 domains, consistent with B1 to within 10⁻⁶.
- **Observed cancer variants are depleted of fold-breaking substitutions** against a domain-matched single-nucleotide background (5.9 % vs 9.2 %, p ≤ 0.001). This is consistent with weak purifying selection, but mutational context is not modelled.
- **The fragile core of the SH3 fold is mapped;** family-wide damage follows burial at ρ +0.78.

**Next:** run `D1_figures_and_verification` on CPU (about 1 min). It draws the figures and builds the full
reproduction table.
