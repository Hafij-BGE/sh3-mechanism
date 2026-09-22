# C2 — Analysis of the result: can binding be learned within one domain?

**Colab run:** 2026-09-22, 7.0 min on a Tesla T4, with the corrected notebook (signed ESM comparison).
**Verdict: REPRODUCED** — 21 recorded values identical; 21 values are new (the corrected procedure).
The run's own numbers are in `RESULTS_C2.md`, `metrics_C2.json`, `comparison_C2.csv`,
`within_domain_repeats.csv`, `single_fit_ci.csv`, `within_domain_summary.csv` and **`binding_decision.json`**,
which B3 reads.

---

## 1. The question

C1 showed that binding does not transfer between unrelated domains. C2 removes transfer altogether:

> **Train and test inside the same domain.** Hold out whole **positions** (every substitution at a position is
> either all in training or all in the test), and predict ΔΔG_bind at the unseen positions.

Holding out positions rather than random variants matters. With random splits, the model would see other
substitutions at the same position and only interpolate. Holding out positions asks whether it can predict
binding at a **position it has never seen**. That is what it would need to do for a new cancer variant.

**Each domain is fitted six times** (repeats with different seeds/partitions), in two modes:
- **Original:** unshuffled `GroupKFold`, as in the recorded analysis.
- **Corrected:** position partitions shuffled with a fixed seed per repeat.

The spread across the six repeats measures how stable the procedure is. A bootstrap over variants cannot
show that.

---

## 2. Results

Spearman ρ between predicted and measured ΔΔG_bind at held-out positions:

| Domain | Positions | Mode | Median of 6 repeats | Range of repeats | Crosses zero? | Zero-shot ESM |
|---|---|---|---|---|---|---|
| **PSD95-PDZ3** | **84** | original | **+0.397** | +0.363 to +0.412 | no | −0.438 |
| | | corrected | **+0.373** | +0.324 to +0.418 | no | |
| **GRB2-SH3** | **56** | original | **−0.030** | −0.109 to +0.124 | **yes** | −0.126 |
| | | corrected | **−0.020** | −0.068 to +0.022 | **yes** | |
| GB1 | 55 | original | +0.009 | −0.118 to +0.197 | yes | +0.042 |
| | | corrected | +0.053 | +0.030 to +0.212 | no | |

**Interpretation:**
- **Binding is learnable in PDZ3.** ρ is about +0.37 to +0.40 in both modes, and all 12 fits are between +0.32 and +0.42. The result is stable, and positive at every repeat.
- **Binding is not learnable in GRB2-SH3, the SH3 domain.** The median is about zero in both modes (−0.02, −0.03), and the repeats straddle zero. Holding out positions, the model cannot predict SH3 binding at all.
- **GB1 is in between but close to zero** (+0.01 to +0.05). Some corrected repeats reach +0.21, but the median is small.
- **The two modes agree on the conclusion.** The corrected mode gives a tighter spread for GRB2-SH3 (0.09 vs 0.23), so the "no signal" result becomes *more* certain, not less, once the partitioning flaw is removed.

---

## 3. The recorded "+0.124" for GRB2-SH3 was one lucky draw

The recorded analysis (Stage 3b) reported one fit on GRB2-SH3 with **ρ +0.124** and a bootstrap CI of
**+0.044 to +0.205**, which excludes zero. Taken alone, that looks like a weak but real signal.

This run reproduces that exact fit (original, seed 0: **+0.1243**, identical). The other five repeats show
what it really is:

| GRB2-SH3, original mode | ρ |
|---|---|
| Seed 0 (the recorded fit) | **+0.124**, the highest of the six |
| Median of six repeats | −0.030 |
| Lowest repeat | −0.109 |

- **The +0.124 was the best of six draws, not a result.** Its bootstrap CI looked significant because the bootstrap resamples *variants* within one fit. It cannot see that a different, equally valid partition of positions gives a completely different answer.
- **Lesson for the thesis:** with only 56 positions, a single train/test split is unreliable for binding. Repeated fits are needed, and they show no signal.

---

## 4. The decision read by B3: which binding predictor to use

`binding_decision.json`:

```
head_beats_esm:      false
grb2_median_rho:     corrected −0.020, original −0.030
grb2_esm_rho:        −0.126
predictor_of_record: esm_zero_shot
```

- **The binding axis in B3 is zero-shot ESM-2, not the trained head.**
  - Zero-shot ESM gives ρ −0.126 on GRB2-SH3. That is weak but in the correct direction; a negative log-odds means more damage.
  - The trained head gives about 0. Weak signal beats none.
- **This decision was made with the corrected, signed comparison.** Under the old absolute-value comparison, a large *negative* head ρ could have been counted as beating ESM. Here the head is about zero, so both versions would give the same decision. The fix makes the rule safe regardless.
- **In practice:** B3 ranks cancer variants on the binding axis by ESM, rank-matched, and labels it a **weak** axis. No binding claim about an individual variant is made from it.

---

## 5. Why PDZ3 works and GRB2-SH3 does not

The clearest difference is the **number of distinct positions**: PDZ3 has **84**, GRB2-SH3 **56**, GB1 **55**.
The two domains below about 60 positions fail; the one with 84 works.

Other explanations are possible:
- the domains have different binding modes;
- the SH3 dynamic range is smaller;
- only 619 GRB2-SH3 variants have reliable binding energies, against 1,221 for PDZ3.

**C3 tests these directly.** It shrinks PDZ3 to fewer positions or fewer variants and sees where the signal
disappears. If positions, not rows, are the limit, no SH3 domain (56–60 residues) can ever supply enough.

---

## 6. Limitations

- **Six repeats per mode.** Enough to show the spread, too few for precise intervals on the median.
- **One ligand per domain.** GRB2-SH3 binding was measured against one peptide. A different ligand could involve other positions.
- **Reliable binding energies only** (619 for GRB2-SH3).
- **The RESULTS summary line** quotes PDZ3 at +0.397, which is the *original* mode. The corrected median is +0.373. Both support "learnable".

---

## 7. Conclusion and next step

- **Within a domain, binding is learnable for PDZ3** (ρ about +0.37 to +0.40, stable) **but not for GRB2-SH3** (ρ about 0; repeats cross zero).
- **The recorded +0.124 for GRB2-SH3 was the luckiest of six draws.** With repeats, there is no signal.
- **The binding predictor of record for the atlas is zero-shot ESM-2,** a weak axis that is labelled as such.
- **The obvious suspect is too few positions** (56 vs 84).

**Next: C3 — is the limit rows or positions? (T4, 30–45 min).**
