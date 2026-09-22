# B4 — Analysis of the result: external validation on ProteinGym

**Colab run:** 2026-09-22, 11.4 min on a Tesla T4. **Verdict: REPRODUCED** — 12 of 12 values identical.
The run's own numbers are in `RESULTS_B4.md`, `metrics_B4.json`, `comparison_B4.csv` and
`proteingym_results.csv`.

---

## 1. The question

B1 showed that the folding head works on SH3 domains it never saw, but those tests came from the same
experiment (MegaScale). B4 asks: **does the head also work on other proteins, measured by other labs, with
other assays?** It is scored on ProteinGym v1.3 deep-mutational-scanning assays, in three blocks.

- **Primary (3 assays): external stability assays.** Assays that measure stability, not from MegaScale, and not proteins used in training.
- **Secondary (15 assays): abundance/expression assays.** These measure how much protein survives in cells, which follows stability only loosely.
- **Sanity (10 assays): Tsuboyama 2023 (MegaScale) domains inside ProteinGym.** Same assay as training; this block checks that the pipeline is wired correctly.

Up to 1,500 variants per assay. The model's ρ is negative when it works, because it predicts damage and
ProteinGym scores fitness. The comparison therefore uses |ρ|.

---

## 2. Results by block

| Block | Assays | Head, median \|ρ\| | Zero-shot ESM-2, median \|ρ\| | Head wins |
|---|---|---|---|---|
| Sanity (MegaScale domains) | 10 | **0.940** | 0.580 | 10 / 10 |
| **Primary (external stability)** | 3 | 0.361 | **0.406** | 2 / 3 |
| **Secondary (abundance)** | 15 | 0.400 | **0.491** | 6 / 15 |

**Interpretation:**
- **The wiring is correct.** On MegaScale-type domains the head reaches 0.94 and wins all 10.
  - Seven of these domains are from the training data (HECD1, POLG, UBE4B, MYO3, CSN4, AMFR, SDA).
  - Three are SH3 domains held out in B1 (SPTN1, OBSCN, DOCK1). Their values (0.947, 0.756, 0.772) agree with B1's held-out results (SPTAN1 0.872 over all backgrounds; OBSCN 0.754; DOCK1 0.774). So even the "sanity" block partly confirms B1 independently.
- **On external stability assays, the head is close to ESM but not better overall.** The medians are 0.36 vs 0.41, though the head wins 2 of 3 (PRKN 0.455 vs 0.406; ESTA 0.340 vs 0.325; loses AACC1 0.361 vs 0.493). With 3 assays, no firm conclusion is possible.
- **On abundance assays, ESM is better** (0.49 vs 0.40; head wins 6 of 15). Abundance in cells depends on degradation, folding chaperones and expression, not only on thermodynamic stability. A stability-trained head does not capture those effects.

---

## 3. How much is lost outside the training regime

| Block | Head: drop from its SH3 result (0.839) | ESM: drop from its SH3 result (0.617) | Ratio |
|---|---|---|---|
| Primary | 0.478 | 0.211 | 2.3× |
| Secondary | 0.439 | 0.126 | 3.5× |

**The head loses 2–3.5 times more than ESM when it leaves its regime.** ESM-2 is a general model and degrades
gracefully. The head is specialised: excellent on small single domains measured by proteolysis, and much less
so on large proteins in cellular assays.

---

## 4. Is sequence length the explanation?

| Length (primary + secondary) | Assays | Head | ESM |
|---|---|---|---|
| > 250 residues | 11 | **0.450** | 0.406 |
| ≤ 250 residues | 7 | 0.340 | **0.493** |

One suspicion was that the ESM window truncates long proteins. The data say otherwise: the head does
*better* on the long proteins, where it beats ESM. The drop is therefore not a window artefact. More likely
it reflects **assay type and protein context** (multi-domain proteins, membrane proteins, cellular
abundance).

**Caveat:** only 18 assays, and length is mixed up with assay type, so this table only rules out one
explanation.

---

## 5. What the thesis can and cannot claim

- **Can claim:** a **domain-scale** folding predictor, validated for small single domains like SH3. This is exactly the regime of the cancer atlas: every atlas variant sits in a 50–87-residue SH3 domain, scored on the isolated domain sequence.
- **Cannot claim:** a general protein stability predictor. Outside its regime, zero-shot ESM-2 is as good or better.
- **Why this does not weaken the thesis:** the thesis applies the head only inside its validated regime. B4 documents the boundary honestly.

---

## 6. Limitations

- **Only 3 primary assays.** External stability DMS data that is not from MegaScale is rare.
- **Abundance is only a proxy for stability.**
- **ProteinGym assays are subsampled to 1,500 variants** where larger.
- **The |ρ| comparison is valid here** because every head ρ has the correct (negative) sign and every ESM ρ the correct (positive) sign.

---

## 7. Conclusion

- **The head is a specialist.** On SH3-scale domains it is the best predictor (B1, B2). On large proteins and cellular abundance assays, zero-shot ESM-2 does as well or better.
- **The cancer atlas lies entirely inside the validated regime.**
