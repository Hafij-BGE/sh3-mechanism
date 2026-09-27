# E1 — analysis

Run 27 September 2026. Machine numbers in `RESULTS_E1.md` and `metrics_E1.json`; the plan they were
judged against is `docs/preregistration/E1.md` @ `07d2b81`, amended `e9b509e`, both committed before
this notebook existed.

---

## The pre-registered question passes, and it passes on the primary test

| | pathogenic | benign |
|---|---|---|
| n (1+ star, in an SH3 domain, scored) | 21 | 101 |
| median predicted ΔΔG_fold | **1.67** kcal/mol | **0.19** kcal/mol |

Mann–Whitney p = **4.9 × 10⁻⁶** against α = 0.025; rank-biserial **+0.615**, meaning a randomly
chosen disease-causing variant is predicted more destabilising than a randomly chosen harmless one
about 81 % of the time. Dropping the star filter (arm 3, 28 vs 106) gives p = 1.2 × 10⁻⁶ and +0.582.

The head was trained on proteolysis and abundance measurements and has never seen a clinical label.
Nine-fold separation in median ΔΔG between ClinVar's two ends is the strongest external evidence in
the project that the predictions carry biological meaning rather than assay-specific structure.

**Why this is not a lucky choice of test.** Part 6.3 fixed the continuous comparison as primary and
the rate comparison as secondary *before any result existed*. That decision decided the outcome — see
the next section — and it was made for a stated reason (21 events cannot support a proportion test),
not after seeing which one worked.

## The published *call* flags almost none of it — and that is the finding

| | destabilising by `fold_lo ≥ 1` |
|---|---|
| pathogenic | 4.8 % (1 / 21) |
| benign | 1.0 % (1 / 101) |
| whole atlas, for scale | 6.0 % (410 / 6,884) |

Fisher p = 0.32. No verdict, and none at 0+ stars either (7.1 % vs 0.9 %, p = 0.11).

Beltran et al. report that about **60 %** of pathogenic missense variants reduce abundance. We flag
**4.8 %**. The gap is not a disagreement about biology; it is what `fold_lo ≥ 1` means. That call is
the *lower end of a 90 % conformal interval*, so it answers "is this variant certainly destabilising"
and deliberately refuses everything it cannot be sure of. At the pathogenic rate of ~5 %, 21 variants
can produce one event; the test has no power by construction.

Two things follow, and both belong in the paper rather than being smoothed over:

1. **The ranking is informative; the binary call is not a clinical filter.** Reporting ΔΔG with an
   interval is defensible. Reporting `fold_lo ≥ 1` as "predicted pathogenic" is not, at this
   threshold.
2. **The conservative call is doing its job.** It was built to make a small number of high-confidence
   claims, and the one pathogenic variant it flags is the kind of claim it was designed for. Its low
   sensitivity is a property, not a bug — but it must be stated as sensitivity, not hidden.

## Q2 — the germline depletion points the right way and does not reach significance

| arm | n common | observed destabilising | expected (B6 null) | p |
|---|---|---|---|---|
| 1 — MAIN, popmax > 1 % | 35 | **0.0 %** | 9.63 % | 0.0289 |
| 6 — atlas only, popmax > 1 % | 30 | 0.0 % | 9.43 % | 0.0513 |
| 4 — popmax > 5 % | 19 | 0.0 % | 9.36 % | no verdict, n < 20 |

Zero of 35 against 3.4 expected. **p = 0.0289 is above the pre-registered α = 0.025, so the verdict
is no.** The threshold is missed by 0.004, and the honest statement is the one the rule forces:
*consistent with depletion, not established.* Pre-registering α is worth nothing if it is reinterpreted
when a result lands just outside it.

**This does not triangulate B6, and the plan should stop saying it might.** The germline arm existed
to attack objection 2 — that B6's 5.9 %-against-9.2 % depletion in cancer could be mutational bias
rather than selection — without depending on a signature model. It cannot: at popmax > 1 % there are
35 scored germline variants inside SH3 domains, and even a *perfect* depletion to zero cannot clear
0.025 at that n. The arm is reported for what it is, and **G1 (the signature-aware null) is now the
only live route to objection 2.**

## Where the numbers differ from the pre-registration

The plan recorded 21 / 126 at the main setting; the run has 21 / **101**.

The pre-registration counted variants by domain position alone. The notebook additionally requires
that the wild-type residue actually exist at that position in the UniProt canonical sequence B6
scored — a substitution with no wild type cannot have a prediction. That drops **25 benign and 0
pathogenic**:

| gene | dropped | | gene | dropped |
|---|---|---|---|---|
| OBSCN | 9 | | SH3D19 | 1 |
| MCF2L | 3 | | DST | 1 |
| MACF1 | 2 | | ARHGEF9 | 1 |
| SORBS2 | 2 | | KALRN | 1 |

Every one is a large multi-isoform protein where ClinVar's chosen transcript numbers residues
differently from UniProt canonical — the same class of problem as G3's AlphaFold fragment offsets.
**The drop cannot bias the result toward the hypothesis**: these variants have no prediction at all,
so nothing about their ΔΔG could have influenced whether they were kept. The notebook now prints the
count instead of losing it silently.

## Two arms are not independent corroboration

The ClinVar star threshold enters only Q1; the allele-frequency threshold enters only Q2. So:

- In **Q1**, arm 4 is numerically identical to arm 1 — same 21 / 101, same p to every digit.
- In **Q2**, arms 1, 2 and 3 are the same test — same 35 variants, same p.

`RESULTS_E1.md` for this run says "every arm with enough data agrees", which overstates it. Q1 has
exactly **one** independent corroborating arm (arm 3, the star threshold relaxed) and Q2 exactly
**one** (arm 6, restricted to atlas positions). Both agree, which is worth having, but it is two
checks and not five. The generator now excludes duplicate arms from that claim and names them.

## Effect on the plan

| Objection | Was | Now |
|---|---|---|
| 4 — nothing was measured | E2 done, E1 pending | **closed for the ranking**: E2 gives measured abundance, E1 gives clinical labels, both external and both positive |
| 2 — depletion could be mutational bias | G1, triangulated by E1 | **G1 only.** E1's germline arm is underpowered by roughly an order of magnitude |

## What to fix before this is written up

1. **Re-run with the patched notebook** so `RESULTS_E1.md` stops quoting 126 and stops claiming five
   agreeing arms. No test statistic changes.
2. **Report sensitivity explicitly** wherever `fold_lo ≥ 1` appears: 4.8 % of pathogenic variants at
   a 1.0 % benign rate. A reader comparing us with Beltran's 60 % needs the threshold definition in
   the same sentence.
3. **Do not quote the Q2 p-value without its verdict.** 0 of 35 with p = 0.029 against a 0.025 bar is
   a single sentence, and the sentence includes "not established".
