# C1 — Analysis of the result: can binding be learned across domains?

**Colab run:** 2026-09-22, 0.8 min on a Tesla T4. **Verdict: REPRODUCED** — the 9 recorded values are
identical; 15 values are new (the corrected procedure).
The run's own numbers are in `RESULTS_C1.md`, `metrics_C1.json`, `comparison_C1.csv` and `lodo_results.csv`.

> **One problem was found in the summary logic (Section 4). It was fixed and C1 re-run (2026-09-22 13:44, 1.1 min).**
> The correlations were identical in the re-run; only the "beats ESM" column changed, to False for all six rows.

---

## 1. The question

Part C starts here. Folding is predictable (Part B). **Is binding?**

The first and simplest design is **leave-one-domain-out**:
- train a binding head on two of the three ddPCA domains (GB1, GRB2-SH3, PSD95-PDZ3);
- predict ΔΔG_bind for the third;
- repeat for each domain.

For SH3, this asks whether binding rules learned on GB1 and PDZ3 transfer to GRB2-SH3.

**Two versions are run side by side:**
- **Original:** as in the recorded analysis. It used the **held-out domain for early stopping**, so information from the test domain leaked into training.
- **Corrected:** early stopping on an internal validation split of the training domains only. No test-domain information is used.

---

## 2. Results

Spearman ρ between predicted and measured ΔΔG_bind on the held-out domain (reliable binding energies only),
with 95 % bootstrap CIs. A working head should give **positive** ρ; zero-shot ESM should give **negative** ρ.

| Held-out domain | n | Head, original | Head, **corrected** (95 % CI) | Zero-shot ESM |
|---|---|---|---|---|
| GB1 | 1,000 | −0.090 | **−0.151** (−0.216 to −0.086) | +0.042 |
| **GRB2-SH3** | 619 | +0.097 | **−0.042** (−0.120 to +0.036) | −0.126 |
| PSD95-PDZ3 | 1,221 | +0.112 | **+0.132** (+0.076 to +0.188) | −0.438 |

**Interpretation:**
- **Binding does not transfer between domains.**
  - **GRB2-SH3, the SH3 case:** the corrected head gives ρ −0.04. That is indistinguishable from zero, with the wrong sign.
  - **GB1:** the head is significantly *anti*-correlated (−0.15). Rules learned on the other two domains point the wrong way here.
  - **PDZ3:** the head gets a weak +0.13.
- **The leak mattered for GRB2-SH3.** The original +0.097 had a CI (0.017–0.176) just above zero. The corrected value −0.042 has a CI that includes zero. The small positive result in the recorded analysis came from test-domain information leaking in through early stopping.
- **Zero-shot ESM is also weak on binding, but it is better than the head everywhere** in the correct direction: −0.13 on GRB2-SH3 and −0.44 on PDZ3. On GB1 it is essentially zero.

---

## 3. Why it fails: the design was wrong, not the model

The three domains bind **completely different partners in different ways**:
- GB1 binds an antibody Fc region.
- GRB2-SH3 binds a proline-rich peptide in a groove.
- PSD95-PDZ3 binds a C-terminal peptide in a β-strand addition.

A residue that matters for one binding mode says nothing about another. **Binding rules are specific to each
binding mode**, so no amount of model tuning can make them transfer across unrelated folds. With only one SH3
in the data, there is no second SH3 to learn from.

**Leave-one-domain-out is therefore the wrong design for binding.** It is kept in the thesis, and labelled as
such, because it shows *why* the next step (C2) must remove transfer altogether: train and test inside the
same domain.

---

## 4. The problem found and fixed: counting "wins" by absolute value

The notebook summary said *"the head beats ESM on 1/3 held-out domains"*. That one "win" is GB1, where the
head's ρ is **−0.151** and ESM's is **+0.042**. Both are in the *wrong* direction. The code compared |ρ|
values, so a wrong-direction correlation of the head counted as a win.

**Correct count (signed, head ρ > −ESM ρ):** the head beats ESM on **0 / 3** domains, in both the original and
the corrected version.

**The fix (in `tools/nb_C.py`, notebooks regenerated):**
- C1: `beats_esm = rho > −esm`.
- **C2: the same fix.** C2 uses this comparison to write `binding_decision.json` ("trained head" vs "ESM zero-shot" as the binding predictor of record). B3 reads that file. With the old logic, a large *negative* head ρ on GRB2-SH3 would wrongly have made the trained head the binding predictor.
- B1 (all signs correct) and B4 (all signs correct, see its analysis) are not affected.

---

## 5. Limitations

- **Only three domains,** each with a different binding mode. The test cannot say whether binding transfers *within* the SH3 family, because no second SH3 has ddPCA binding data. C4 addresses the family with an independent specificity dataset.
- **Reliable binding energies only.** 619 variants for GRB2-SH3.

---

## 6. Conclusion and what to do now

- **Binding does not transfer between unrelated domains.** GRB2-SH3 corrected ρ is −0.04, with a CI containing zero. The small positive recorded result came from leakage.
- **The head beats zero-shot ESM on 0 of 3 domains,** not 1 of 3 as the notebook text said.
- **Next question (C2):** can binding be learned *within* one domain, predicting positions that were held out?

**Next:** run C2 (`C2_binding_within_domain`, T4, about 15 min) using the new notebook.
