# A sequence-only model of folding stability for human SH3 domains matches structure-conditioned predictors and recovers clinical variant effects

**Draft manuscript.** IMRAD, biomedical/computational venue. Reference details marked *[verify]* need
completing from the primary sources before submission — only identifiers confirmed during this work are
given. Every number is traceable to a committed result table; the source is named in each Results
paragraph.

---

## Abstract

**Background.** Predicting the change in folding free energy (ΔΔG) caused by a missense substitution
is central to interpreting variants of uncertain significance, but most current predictors require a
three-dimensional structure and most are trained on the same proteolysis dataset used to evaluate
them.

**Methods.** We trained a supervised head (1,292 → 512 → 128 → 1) on frozen ESM-2 650M embeddings
plus twelve biophysical scalars, using ~361,000 non-SH3 substitutions from a mega-scale proteolysis
dataset, and held out the entire SH3 family (15 genes, 27,590 variants) with splits grouped on
UniProt accession and domain index. Calibrated uncertainty was obtained by normalised split-conformal
prediction. We then evaluated the frozen model, without re-fitting, against four independent sources:
abundance measurements from a second assay, ClinVar and gnomAD labels, two current
structure-conditioned ΔG predictors, and an independent set of binding affinities. We additionally
re-tested a previously reported depletion of destabilising substitutions among cancer variants
against a null matched to trinucleotide sequence context, and evaluated the frozen model on four
protein families absent from its training data. Decision rules for five of the six evaluations were
pre-registered and committed to version control before the analysis code existed.

**Results.** On 15 held-out domains the model reached a median per-domain Spearman ρ of 0.839. Against
880 variants measured by an independent abundance assay, pooled |ρ| was 0.600; two independent assays
agree with one another at |ρ| = 0.709, so the model reaches 90–113 % of the achievable limit on
matched variants. Predicted ΔΔG separated ClinVar pathogenic from benign variants inside SH3 domains
(median 1.67 vs 0.19 kcal mol⁻¹, Mann–Whitney p = 4.9 × 10⁻⁶, rank-biserial +0.615). Against two
structure-conditioned predictors given the experimental structure of the measured construct, the
sequence-only model showed no clear difference from SaProtΔG (median ρ 0.839 vs 0.855, paired
Wilcoxon p = 0.107) and outperformed ESM3ΔG (0.839 vs 0.792, p = 0.0084), with all 27,590 variants
scored by every model and none dropped. A third predictor was disqualified before evaluation: 13 of
our 15 held-out domains lie inside its published training split. A previously reported depletion of
destabilising substitutions among cancer variants (5.93 % observed vs 9.18 % expected) did **not**
survive a context-matched null: 5.96 % against 6.04 % expected, p = 0.40, with a second,
independently specified mutational spectrum agreeing (p = 0.92). Scope is bounded in two directions.
On deep-mutational-scanning assays outside the training dataset the supervised head does **not**
outperform zero-shot ESM-2 (median |ρ| 0.361 vs 0.406 on external stability assays; 0.400 vs 0.491 on
abundance assays). Applied to families never seen in training, it matches SH3 on PDZ (0.602 vs 0.623)
despite PDZ exceeding the 72-residue construct-length ceiling of the training assay, while three
length-matched families remain inconclusive.

**Conclusions.** A sequence-only stability model is competitive with structure-conditioned predictors
on held-out domains **of the assay it was trained on**, and recovers a substantial part of the
clinical signal without ever seeing a clinical label. Its competitiveness does not extend to other
assay types, which bounds the claim rather than qualifying it. Three negative results are reported
with equal weight: the conservative
confident-call threshold has 4.8 % sensitivity for pathogenic variants and is not a clinical filter;
an internal specificity axis failed a second, independent test, attributable to the representation
rather than the model; and a previously reported depletion of destabilising cancer variants is
withdrawn, being attributable to mutational context rather than selection.

**Keywords:** protein stability, ΔΔG, variant effect prediction, SH3 domain, protein language model,
pre-registration

---

## 1. Introduction

Most missense variants observed in human genomes have no established clinical interpretation, and a
large fraction of those that are pathogenic act by destabilising the folded protein rather than by
disrupting a specific interaction. Quantifying that destabilisation — the change in folding free
energy, ΔΔG — therefore connects sequence variation to a mechanism.

Two developments have changed what is possible. Mega-scale proteolysis experiments now provide
hundreds of thousands of directly measured folding stabilities [1], and protein language models
supply representations that transfer across families [2]. Supervised heads trained on the former
using the latter are now standard, and several recent predictors add a three-dimensional structure as
input [3,4].

Three problems recur in the evaluation of such models.

**Structure availability is assumed.** Predictors that require a structure cannot be applied where
none exists, and comparisons that supply an experimental structure to one model and a sequence to
another are rarely reported as such.

**Training and test data share a source.** Most current ΔΔG predictors are trained on the same
mega-scale dataset used to benchmark them. Unless the published splits are checked, a benchmark can
report a model scoring its own training data.

**Evaluation is internal.** A model evaluated only against held-out variants from the assay it was
trained on has not been tested against an independent measurement, a clinical label, or a competing
method.

We addressed these in a single protein family. The SH3 domain is small, abundant in the human
proteome, and measured in multiple independent assays, which makes external validation tractable.
Having previously trained and frozen a sequence-only model on non-SH3 data, we here evaluate it
without re-fitting against four independent sources, with the decision rules committed in advance.

Our contributions are: (i) a benchmark against two current structure-conditioned predictors in which
the competitors receive the experimental structure of the exact measured construct and the model does
not; (ii) a leakage audit that disqualifies a widely used predictor from this benchmark; (iii)
external validation against a second measurement assay, interpreted against the agreement between the
two assays; (iv) clinical evaluation against ClinVar with the sensitivity of the confident-call
threshold stated; and (v) an independent negative result on a specificity axis, with a control that
identifies the representation rather than the model as the cause.

## 2. Methods

### 2.1 Model and training (previously reported, unchanged here)

The predictor is a feed-forward head of 1,292 → 512 → 128 → 1 units over frozen features: the 1,280
dimensional ESM-2 650M (`facebook/esm2_t33_650M_UR50D`) embedding of the mutated residue concatenated
with twelve biophysical scalars. It was trained on approximately 361,000 **non-SH3** single
substitutions from the mega-scale proteolysis dataset [1], across five random seeds, with validation
on whole held-out domains. Splits were grouped on UniProt accession and domain index, so no domain
appears on both sides. The entire SH3 family — 15 genes, 27,590 variants — was held out.

Throughout, **positive ΔΔG denotes destabilising**; the proteolysis dataset ships the opposite sign
and is negated on load.

Uncertainty was calibrated by normalised split-conformal prediction, giving a 90 % lower bound
`fold_lo`. A variant is called confidently destabilising when `fold_lo ≥ 1` kcal mol⁻¹.

**All evaluations below read this model's recorded outputs.** Nothing was re-fitted, re-trained or
re-tuned. The stored artefacts are write-protected, and each evaluation re-derives the previously
published per-domain correlations from them and asserts agreement before proceeding.

### 2.2 External data

| Source | Content | Used for |
|---|---|---|
| Human Domainome 1.0 [5] | aPCA abundance for 45 SH3 domains | §3.2 |
| ClinVar (`variant_summary`, retrieved 26 Sep 2026) | clinical significance, review status | §3.3 |
| gnomAD v4 (GraphQL API, 235 gene queries) | population frequency, popmax | §3.3 |
| SaProtΔG, ESM3ΔG [3] | structure-conditioned ΔG predictors | §3.4 |
| ThermoMPNN [4] | ΔΔG predictor (audited, then excluded) | §3.4 |
| Kazemein Jasemi et al. [6] | 45 dissociation constants, 17 SH3 domains | §3.5 |
| dbNSFP 5.4a [7] | every possible in-domain missense SNV, with genomic coordinates | §3.6 (null pool); ~50 pathogenicity predictors reserved for future work |
| GRCh38 primary assembly [11] | trinucleotide sequence context | §3.6 |
| COSMIC SBS v3.6 [12] | 96-channel reference mutational signatures | §3.6 |
| ProteinGym v1.3 [13] | 28 deep-mutational-scanning assays, ≤ 1,500 variants each | §3.7 |
| Human Domainome 1.0 [5] | 102 domains in five Pfam families, for the cross-family evaluation | §3.7 |

Every input was verified by MD5 before use; where the publisher publishes a checksum, ours is compared
against theirs rather than only against a locally recorded value. External sources were acquired and
reduced once, in two dedicated programs whose outputs every evaluation reads, so that no analysis
re-downloads or re-filters: one for the clinical, population and abundance data, and one for dbNSFP.
Both assert that joining external data onto the frozen predictions leaves the atlas row count
unchanged at 6,884 — an assertion that caught three separate join defects, including 3,856 rows
duplicated by dual Pfam annotation of the same domain.

The dbNSFP reduction is reported with its coverage compared against the publisher's own published
figures for each predictor. That external comparison is the only check available on a reduction with
no ground truth of its own, and it caught a defect in which every predictor column was correctly
populated but mislabelled, the file otherwise being complete and internally consistent.

### 2.3 Pre-registration

Decision rules for the ClinVar/gnomAD, benchmark, specificity and mutational-context analyses were
written as documents, committed to version control **before the corresponding analysis code existed**,
and are reproduced in the supplement. Each states the main comparison, the significance threshold, the minimum group size,
and how the results table would be read. Group sizes were counted before sign-off; model predictions
were not consulted.

Significance thresholds were set per analysis by Bonferroni correction over the comparisons carrying a
verdict within that analysis (α = 0.025 with two, 0.0167 with three, 0.0125 with two co-primary
spectra in §3.6). For §3.6 the analysis code reads the committed pre-registration at run time to set
its own threshold, so the choice between one primary arm and two co-primary arms could not be made
after a *p*-value existed.

### 2.4 Statistical analysis

Per-domain agreement is Spearman ρ. Paired comparisons between models across domains use the Wilcoxon
signed-rank test on per-domain correlations. Group comparisons of predicted ΔΔG use Mann–Whitney U
with rank-biserial correlation as the effect size. Rate comparisons use Fisher's exact test; depletion
against a null uses an exact binomial test. Within-domain associations pool values centred on their
own domain mean, with df = n − k − 1 for k domains.

For every predictor, the sign convention was aligned using each source's **documented** definition,
never by whichever direction correlated better; unaligned correlations are reported alongside.

## 3. Results

### 3.1 The frozen model, and what was previously established

On the 15 held-out SH3 domains the model reached a **median per-domain Spearman ρ of 0.839** and
exceeded the zero-shot ESM-2 score it is built on for 15 of 15 domains. Conformal calibration gave
q₉₀ = 6.807 in normalised units with 89.9 % empirical coverage, yielding **410 confidently
destabilising calls among 6,884 cancer-derived variants (6.0 %)**. A virtual saturation scan of all
366,168 possible substitutions in 310 domains found 12.1 % destabilising overall and 9.2 % among
single-nucleotide-reachable substitutions, against 6.0 % of observed cancer variants; a
domain-matched null gave 5.93 % observed versus 9.18 % expected (p = 0.001) — a claim Section 3.6
retracts. An independently
constructed specificity axis failed its own pre-registered rule (median centred r = +0.288;
`validated: false`).

These are the prior results. Section 3.2 onward tests them against external data; none was re-fitted,
and the median ρ of 0.839 was re-derived from the stored predictions in every downstream analysis and
asserted to match.

### 3.2 Agreement with an independent abundance assay, relative to the assay ceiling

Of the 6,884 atlas variants, **880 have a direct abundance measurement** in an independent
aPCA dataset [5], spanning 41 domains and 32 genes. Pooled agreement was **|ρ| = 0.600**
(p = 4.1 × 10⁻⁸⁷), with a per-domain median of 0.573; all 21 domains with sufficient sampling
correlated in the expected direction. Variants called confidently destabilising had markedly lower
measured abundance than tolerated variants (median fitness −0.748 vs −0.106, Mann–Whitney
p = 2.3 × 10⁻²²; n = 63 and 817).

A correlation of 0.600 is uninterpretable without knowing what is achievable. Seven SH3 domains have
been measured by **both** proteolysis and abundance, in different laboratories by different methods;
**four** could be reconciled between the two position-numbering schemes and yielded a ceiling. On
shared variants those two assays agree at a median **|ρ| = 0.709** (n ≈ 800–1,200 variants per
domain). The model
therefore reaches **85 % of the between-assay agreement** on the pooled comparison, and on variants
matched to the same subsets used for the ceiling it reaches **90 %, 102 % and 113 %** for LCK
(n = 26), HCK (n = 19) and BTK (n = 39) respectively (Figure 1B).

A ratio above 100 % does not mean the model exceeds the experiment; it means the model and the
ceiling are indistinguishable at these sample sizes. The matched ceilings rest on 19–39 variants and
are indicative, not precise.

### 3.3 Clinical labels: the ranking separates, the binary call does not

Inside SH3 domain boundaries, 21 ClinVar pathogenic or likely-pathogenic and 101 benign or
likely-benign variants (review status ≥ 1 star) carried a prediction. Predicted ΔΔG separated them
clearly: **median 1.67 vs 0.19 kcal mol⁻¹, Mann–Whitney p = 4.9 × 10⁻⁶, rank-biserial +0.615**,
corresponding to a probability of approximately 0.81 that a randomly chosen pathogenic variant is
predicted more destabilising than a randomly chosen benign one. Relaxing the review-status filter gave
p = 1.2 × 10⁻⁶ with an effect size of +0.582. The model has never seen a clinical label.

**The binary call behaves differently and the difference matters.** The pre-registered threshold
`fold_lo ≥ 1` flagged **4.8 % of pathogenic variants (1 of 21) against 1.0 % of benign (1 of 101)**;
Fisher's exact p = 0.32, no verdict. Published estimates place the fraction of pathogenic missense
variants that reduce abundance near 60 % [5]. This is not a disagreement about biology: `fold_lo` is
the lower bound of a 90 % conformal interval and therefore answers "is this variant *certainly*
destabilising", refusing everything it cannot resolve. At a ~5 % event rate, 21 variants cannot
support a proportion test. The pre-registration designated the continuous comparison as primary for
exactly this reason, before any result existed.

**Population depletion did not reach the pre-registered threshold.** Of 35 variants common in healthy
populations (popmax > 1 %), **none** was called destabilising, against 9.63 % expected under the
domain-matched null — an exact binomial p = 0.0289 against α = 0.025. The direction is as predicted
and the threshold is missed by 0.004. Because the rule was fixed in advance, the result is reported as
*consistent with depletion, not established*. With 35 variants, even perfect depletion could not clear
the threshold; this analysis was underpowered by roughly an order of magnitude and cannot corroborate
the previously reported depletion among cancer variants. Section 3.6 tests that depletion directly,
with adequate power, and does not support it.

### 3.4 Benchmark against structure-conditioned predictors

#### 3.4.1 Leakage audit

Before any comparison, each competitor's published training split was searched for our 15 held-out
domains. SaProtΔG and ESM3ΔG [3] contained **0 of 15**. ThermoMPNN [4] contained **13 of 15** — 12 in
its training split and one in validation — covering **23,191 of 27,590 held-out variants**
(Figure 1D). Only two domains survive, and only because their constructs are background point mutants
absent from every split.

ThermoMPNN was therefore **excluded from the comparison before it was run**, and the significance
threshold was fixed at α = 0.025 over the two remaining competitors. This exclusion is a fact about
training data established prior to any prediction, not a post-hoc adjustment. A benchmark that had
simply run all competitors would have reported a model scoring its own training data.

This establishes presence or absence in the *published* split, not in whatever the released weights
were ultimately trained on.

#### 3.4.2 Comparison

Both competitors were given the experimentally determined structure of the exact construct that was
measured; ours receives sequence only. All 27,590 held-out variants were scored by all three models
and **none was dropped**.

| Model | Median per-domain ρ | Median paired difference | Wilcoxon p | Verdict |
|---|---|---|---|---|
| Ours (sequence only) | 0.839 | — | — | — |
| SaProtΔG (base, 3 seeds) | 0.855 | −0.028 | 0.107 | no clear difference |
| ESM3ΔG (base, 3 seeds) | 0.792 | +0.033 | **0.0084** | ours better |

Against ESM3ΔG the model was better on 12 of 15 domains, meeting the pre-registered threshold.
Against SaProtΔG no clear difference was established; SaProtΔG was nominally ahead on 11 of 15
domains, and with 15 domains this design cannot resolve a median gap of 0.028. We therefore do **not**
claim parity with the best current predictor.

**Consistency differed more than central tendency.** Across domains, ESM3ΔG ranged from **0.460 to
0.892** while our model ranged from **0.754 to 0.934** (Figure 1A). ESM3ΔG's two weakest domains,
DOCK1 (0.460) and PTK6 (0.515), are handled by SaProtΔG at 0.780 and 0.835 on identical inputs,
indicating a property of that model's stability head on those domains rather than of the underlying
language model. For an application that issues a small number of high-confidence calls, behaviour at
the worst domain matters more than the median.

### 3.5 Independent test of the specificity axis: a negative result attributed to the representation

An axis intended to capture binding specificity had previously failed its own pre-registered rule
(median centred r = +0.288; not validated). We tested it against **44 dissociation constants across
16 SH3 domains** measured by another group with a different method [6]. Twelve of the 17 domains lie
in the axis's training set, so leave-cluster-out predictions were used for those, and the final model
only for the four it had never seen; the re-run reproduced the original verdict to 1.6 × 10⁻¹⁴.

The axis showed no association with measured affinity (within-domain-centred r = **+0.023**,
p = 0.91) and did not exceed a domain-agnostic baseline (r = −0.043).

**A pre-registered control determines the interpretation.** We repeated the analysis using each
domain's *observed* experimental profile — the quantity the model is trained to predict, and therefore
an upper bound on what any predictor of it could achieve. It failed identically (**r = −0.051**,
p = 0.80; Figure 1C). Since a predictor of X cannot outperform X, no improvement to the regression
could have produced a positive result here. The failure lies in the **representation**: the axis
collapses a positional profile to amino-acid composition, and SH3 ligand classes are distinguished by
the *order* of residues at identical composition.

The defensible claim is therefore narrower and better supported than "the axis fails": *compositional
profiles derived from this assay do not predict these affinities.* Reported as a post-hoc distinction
would have been unconvincing; the reading was fixed in advance.

### 3.6 The reported depletion of destabilising cancer variants does not survive a context-matched null

The frozen model's virtual saturation scan reported that observed cancer variants are depleted of
predicted fold-breaking substitutions: 5.93 % destabilising against 9.18 % expected from a
domain-matched null over single-nucleotide-reachable substitutions (p = 0.001). That null weights
every reachable substitution equally. Because mutation rates vary by more than an order of magnitude
with trinucleotide context, a uniform null will report depletion whenever the substitutions that are
common are also the ones that are mild, with no selection involved.

Genomic coordinates were recovered for 6,456 of 6,884 atlas variants (93.8 %) by joining to dbNSFP on
gene, residue and substitution; all 6,456 carry the expected GRCh38 reference base. The null pool
comprises 154,708 in-domain missense base changes over 115,742 distinct substitutions, each with its
trinucleotide context read from GRCh38. Draws are domain-matched to the observed set, 10,000 per arm,
weighted by the 96-channel spectrum.

Two spectra were specified in advance: the observed 96-channel distribution of the atlas variants
themselves, and an equal mixture of COSMIC SBS1 and SBS5. Neither was designated primary before the
run, so both were treated as co-primary at α = 0.0125 (Bonferroni, family-wise 0.025).

**Neither supports the depletion** (Table 4).

| Null | Expected | Observed | Difference | *p* |
|---|---|---|---|---|
| Observed atlas spectrum | 6.04 % | 5.96 % | +0.08 pp | 0.401 |
| COSMIC SBS1 + SBS5 | 5.58 % | 5.96 % | −0.39 pp | 0.918 |

The effect is recovered stepwise (Table 5). Correcting the reachability definition reduces the
expected rate but leaves the depletion significant; adding trinucleotide context removes it.

| Null model | Expected | Change | *p* |
|---|---|---|---|
| As previously reported (amino-acid-pair reachability) | 9.23 % | — | 0.001 |
| Codon-level reachability | 8.60 % | −0.64 pp | 0.0001 |
| + reachability multiplicity | 7.88 % | −0.71 pp | 0.0001 |
| + trinucleotide context | **6.04 %** | **−1.84 pp** | **0.401** |

Two properties of the previously used null were identified in the course of this analysis. First,
reachability was assessed at the amino-acid level — whether a substitution is attainable by one base
change from *any* codon of the wild-type residue — rather than from the codon present at that
position. Across 150 amino-acid pairs with *n* ≥ 100, the fraction attainable from the codon present
correlates with the genetic-code prediction at r = +0.955 (mean absolute deviation 0.05), and the
substitutions thereby excluded are more often destabilising than those retained (11.2 % versus
8.6 %). Second, one amino-acid substitution may be reachable by several distinct base changes with
different sequence contexts; drawing at the amino-acid level treats these as a single candidate.

The null result is not a power limitation. The Monte-Carlo standard deviation of the drawn fraction
was 0.00295, against a binomial estimate of 0.00296 computed before the analysis; the smallest
difference detectable at α = 0.0125 is 0.66 pp, and the observed difference is 0.08 pp. The observed
rate lies near the centre of the null distribution (95 % interval 5.48–6.63 %).

The two spectra describe the mutational process differently — cosine similarity 0.688, with C>T at
CpG accounting for 19.3 % of the observed distribution against 47.2 % for the COSMIC mixture — and
agree on the conclusion nonetheless. This addresses the principal limitation of the first arm, whose
spectrum is estimated from the variants under test.

### 3.7 Scope: where the model is competitive, and where it is not

Two results bound the claim, and both are negative in part. They are reported here rather than in the
limitations because they are findings, not caveats.

**Across assays.** The model was scored on ProteinGym deep-mutational-scanning assays in three
blocks (Table 6). On the ten assays drawn from the same proteolysis dataset used for training it
reaches a median |ρ| of 0.940 against 0.580 for zero-shot ESM-2, winning all ten. On three external
stability assays and fifteen abundance assays it does **not**: 0.361 against 0.406 and 0.400 against
0.491 respectively, winning 2 of 3 and 6 of 15. Moving off the training assay costs the supervised
head 2.27× more than it costs zero-shot ESM-2 on the primary block and 3.49× more on the secondary.

| Block | Assays | Head, median \|ρ\| | Zero-shot ESM-2 | Head wins |
|---|---|---|---|---|
| Same assay as training | 10 | **0.940** | 0.580 | 10 / 10 |
| External stability | 3 | 0.361 | **0.406** | 2 / 3 |
| Abundance | 15 | 0.400 | **0.491** | 6 / 15 |

The first row establishes that the pipeline is wired correctly and establishes nothing else. **The
competitive claim is therefore specific to proteolysis-derived stability data of the kind the model
was trained on, and to the abundance assay evaluated in Section 3.2 within SH3.**

**Across families.** The training data caps construct length at 72 residues, because the proteolysis
assay does; all 412 training domains fall in 32–72 residues, median 51. SH3 (54–67) sits inside that
range and most human domain families do not, so length and family novelty are confounded for any
second family that is longer.

Applied unchanged to four families absent from training, the model reached a median per-domain |ρ| of
0.602 on PDZ against 0.623 recomputed for SH3 on the same assay and pipeline (Δ = −0.021, 95 % CI
−0.082 to +0.027) — **notwithstanding PDZ's median construct length of 88 residues, 16 beyond
anything in training.** On three length-matched families it reached 0.420, and the comparison against
SH3 is inconclusive at a pre-specified non-inferiority margin of −0.15 (Δ = −0.203, CI −0.249 to
−0.120). Matching the arms on within-assay measurement quality moves that difference only to −0.187,
and the family with the *best* measurements among the three (Myb/SANT, better than SH3's) is also
below SH3 in accuracy — so the deficit is not explained by noise.

**Construct length is therefore not the constraint it might have been, and measurement quality is not
either.** What limits accuracy on those three families is not identified here.


## 4. Discussion

### 4.1 Principal findings

A sequence-only stability model, trained without any SH3 domain, is statistically indistinguishable
from a structure-conditioned predictor and significantly better than another, on 15 domains neither
had trained on, with the competitors given the experimental structure of the measured construct. It
agrees with an independent abundance assay at 85 % of the agreement between two such assays, and
separates ClinVar pathogenic from benign variants at p = 4.9 × 10⁻⁶ without having seen a clinical
label.

Two boundaries limit that statement and are established here rather than assumed. The model's
advantage over zero-shot ESM-2 does not survive a change of assay: on deep-mutational-scanning data
outside the training dataset it is no better, and it degrades two to three times faster than the
zero-shot baseline does. And the training data never contains a domain longer than 72 residues, a
property of the proteolysis assay rather than a modelling choice — although a family well beyond that
ceiling performs as well as SH3, so length is not the operative constraint.

The same evaluation retracts one of our own previously reported results. A depletion of destabilising
substitutions among observed cancer variants, which had been offered as consistent with weak
purifying selection, does not survive a null matched to trinucleotide context and is attributable to
the mutational process. The original report identified this limitation and named the test that would
resolve it; performing that test is what withdrew the claim. We regard reporting it as no less a
result than the four that were supported.

### 4.2 What the confident-call threshold is for

The most consequential negative result is the 4.8 % sensitivity of `fold_lo ≥ 1` among pathogenic
variants. A 90 % conformal lower bound is deliberately conservative; it is suited to selecting a small
number of experimentally testable claims, not to triaging variants of uncertain significance.
Reporting ΔΔG with its interval is defensible; presenting the thresholded call as a clinical filter,
without stating that sensitivity in the same sentence, is not. We recommend the former.

### 4.3 Leakage as a routine requirement

Thirteen of our fifteen held-out domains lay inside one competitor's published training split. This
was not an unusual case: most current ΔΔG predictors are trained on the same mega-scale dataset that
supplies most held-out evaluation sets. Any benchmark drawn from that dataset should publish a leakage
audit alongside its results, and we suggest it be treated as a reporting requirement rather than an
optional check.

### 4.4 Comparison with previous internal results

| Previously reported | Value | Status after external evaluation |
|---|---|---|
| Per-domain folding accuracy | median ρ 0.839 | **Supported** — re-derived exactly; competitive with two current predictors |
| Exceeds zero-shot ESM-2 | 15/15 domains | **Supported**, and extended to supervised predictors |
| Conformal calls | 410 of 6,884 (6.0 %) | **Supported, with sensitivity now quantified** at 4.8 % |
| Cancer variants depleted of damage | 5.93 % vs 9.18 % (p = 0.001) | **Not supported** — under a trinucleotide-matched null the effect disappears (5.96 % vs 6.04 %, p = 0.40) |
| Specificity axis | r = +0.288, not validated | **Independently confirmed as failed**, and attributed to the representation |
| Exceeds zero-shot ESM-2 *on other assays* | not previously claimed | **Not supported** — off the training assay the head is no better (§3.7) |
| Generality beyond SH3 | asserted from the training procedure | **Partially demonstrated** — one unseen family matches, three inconclusive (§3.7) |

One previously reported result was contradicted: the depletion of destabilising substitutions among
observed cancer variants. The remaining four were supported, and two claims that had been implicit
rather than reported are now bounded — the advantage over zero-shot ESM-2 is specific to the training
assay, and generality beyond SH3 is partial. The depletion rested on a null that
weighted every single-nucleotide-reachable substitution equally; matching the background to
trinucleotide context removes it entirely, and two independently specified spectra agree. The
original report named this limitation itself and identified the test that would resolve it.

### 4.5 Limitations

1. **Fifteen domains detect large differences only.** The benchmark cannot resolve a median gap of
   0.03; "no clear difference" is not equivalence.
2. **One family for the primary results, and a partial answer beyond it.** Sections 3.2–3.6 concern
   SH3 domains only. Section 3.7 extends to four unseen families: one matches SH3, three are
   inconclusive, and the reason is unresolved.
3. **A 72-residue ceiling on the training data.** The proteolysis assay used for training caps
   construct length, so the model has never seen a domain longer than 72 residues. SH3 sits inside
   that range; most human domain families do not. PDZ at 88 residues performs as well as SH3
   (Section 3.7), which bounds the concern without removing it.
4. **Competitiveness is assay-specific.** Off the training assay the head does not beat zero-shot
   ESM-2 (Section 3.7). The benchmark in Section 3.4 is MegaScale-derived, and its result should not
   be read as a general claim.
5. **Small clinical groups.** 21 pathogenic and 101 benign variants support a large-effect comparison
   and nothing finer; the null in the rate analysis is ambiguous between absence of effect and absence
   of power.
6. **Asymmetric inputs, in our favour to state.** Competitors received structures; if they had won,
   part of the reason might have been that extra information. They did not, which strengthens the
   conclusion but does not make the comparison symmetric.
7. **The assay ceiling rests on four domains.** Seven were measured by both assays; two could not be
   reconciled between the position-numbering schemes, which is a mapping defect rather than a property
   of those domains. The matched-subset comparisons use 19–39 variants and are indicative only.
8. **The binding dataset is narrow.** Nine proline-rich peptides from a single protein give a narrow
   compositional range, which works against any compositional model.
9. **Leakage audits establish absence from published splits**, not from the data the released weights
   actually saw.
10. **The confident-call interval is calibrated marginally, not conditionally.** Empirical coverage
    is 89.9 % overall but ranges 83.3 % to 95.0 % across held-out domains, and the per-domain
    conformal quantile varies by a factor of 1.79. Resampling per-domain quantiles places the count
    of confident calls at 400 (95 % interval 378–421), so the aggregate figure is robust while a
    per-variant 90 % claim is not.

### 4.6 Pre-registration in computational method evaluation

Five analyses had their rules committed before the analysis code existed. This changed three
outcomes.
The pre-commit leakage check disqualified a competitor that would otherwise have been benchmarked on
its own training data. The pre-registered control in the specificity analysis prevented a correct
number from supporting a wrong conclusion: without it, the natural report would have been "the axis
fails an independent test", when in fact the measured profile fails the same test. And the power
calculation required before the cross-family evaluation showed that the originally planned single
family would have returned "inconclusive" whatever the data contained, because the confidence
interval at that sample size is wider than the margin it would have been compared against; the arm
was enlarged before any model was run.

Both are cheap, and neither depends on the result. We suggest that computational evaluations with a
pass/fail character adopt the practice.

### 4.7 An experimental panel that can distinguish the model from its context

Predictions of this kind are usually followed by a small bench panel, and the selection rule matters
more than it appears. Ranking candidates by confidence alone concentrates them where the prediction
is easiest: our first panel placed five of ten picks at a single aligned position, all five replacing
alanine, with four substitutions to proline. Five assays would have measured one substitution, and a
panel that repeats a position cannot separate a correct model from a model that has learned one rule.

The same ranking also confounded the comparison. The destabilising picks were 8/10 buried while the
tolerated controls sat at termini and exposed loops, so the two sets differed in burial as much as in
predicted effect — an experiment unable to distinguish a stability prediction from a burial lookup.

The panel was rebuilt under explicit constraints: one variant per aligned position, one per gene, at
most one substitution to proline, and reserved places for **solvent-exposed** destabilising calls,
with controls drawn preferentially from buried positions in the same domains. This yields ten
distinct aligned positions and seven distinct substituted residues, with five buried controls.

Exposed predictions are the informative ones. A buried hydrophobic-to-charged substitution is called
destabilising by any method; a prediction of 2–3 kcal mol⁻¹ at an exposed position is a claim that can
fail. Diversity costs confidence — the least confident pick has a lower 90 % bound of 1.87 rather than
2.47 kcal mol⁻¹ — which is the correct trade when the purpose is to learn something from the result.

## 5. Conclusions

A sequence-only ΔΔG model for SH3 domains is competitive with structure-conditioned predictors on
domains none had trained on, agrees with an independent abundance assay at close to the limit set by
assay-to-assay agreement, and recovers clinical variant effects it was never trained on. Its
conservative confident-call threshold has low sensitivity and should be reported as such. A
specificity axis built alongside it fails independently, and a pre-registered control locates the
failure in the representation. The one internal claim lacking external support — depletion of
destabilising substitutions among observed cancer variants — was tested against a mutation-context-aware
null and did not survive; it is withdrawn.

The scope within which these statements hold is narrower than the method's framing might suggest, and
is stated rather than left to the reader: competitive on proteolysis-derived stability data and on an
abundance assay within SH3, not demonstrated on other assay types, and partially demonstrated across
protein families.

---

## Data and code availability

All analysis code, pre-registration documents, machine-written result tables and hand-written analyses
are in the project repository. Input datasets are obtained from their original sources; checksums for
every input, and the provenance of each including routes that failed, are recorded in the repository.
The complete cancer-variant atlas is not redistributed because it is derived from a licensed database;
derived analysis tables carrying no licensed identifiers are included.

## References

*Identifiers below were confirmed during this work. Entries marked [verify] require full bibliographic
details before submission.*

1. Tsuboyama K, *et al.* Mega-scale experimental analysis of protein folding stability. **2023**.
   Dataset: `Tsuboyama2023_Dataset2_Dataset3_20230416`. [verify full citation]
2. Lin Z, *et al.* Language models of protein sequences. Model: `facebook/esm2_t33_650M_UR50D`.
   [verify full citation]
3. Cho Y, *et al.* Absolute protein stability prediction (SaProtΔG, ESM3ΔG). bioRxiv, PMC13228446.
   Weights: Hugging Face `Yehlin/absolute-stability`. Code:
   `github.com/yehlincho/absolute-stability-predictor`. [verify full citation]
4. Dieckhaus H, *et al.* Transfer learning to leverage larger datasets for improved prediction of
   protein stability changes. *PNAS* **2024**. doi:10.1073/pnas.2314853121. Code:
   `github.com/Kuhlman-Lab/ThermoMPNN`.
5. Beltran A, *et al.* Human Domainome 1.0. *Nature* **2025**. doi:10.1038/s41586-024-08370-4.
   Data: Zenodo v5, record 14356805; concept DOI 10.5281/zenodo.11043642.
6. Kazemein Jasemi NS, *et al.* *Cells* **2024**;13(2):195. doi:10.3390/cells13020195.
7. Liu X, *et al.* dbNSFP v5.4a. [verify full citation]
8. Landrum MJ, *et al.* ClinVar. NCBI, `variant_summary.txt.gz`, retrieved 26 September 2026.
   [verify full citation]
9. gnomAD v4. Broad Institute GraphQL API. [verify full citation]
10. Faure AJ, *et al.* ddPCA / MoCHI: separating folding and binding free energies. **2022**.
    [verify full citation]
11. Ensembl. *Homo sapiens* GRCh38 primary assembly,
    `Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz`, 881,964,081 bytes. [verify release number]
12. COSMIC Mutational Signatures v3.6, SBS, 96-context, GRCh38. Wellcome Sanger Institute.
    [verify full citation]
13. Notin P, *et al.* ProteinGym: large-scale benchmarks for protein fitness prediction and design.
    v1.3. [verify full citation]

---

## Figure legend

**Figure 1. External evaluation of a frozen, sequence-only ΔΔG model.**
**(A)** Per-domain Spearman ρ against measured ΔΔG for the 15 held-out SH3 domains; each row is one
domain, showing our model and the two structure-conditioned predictors, which received the
experimental structure of the measured construct. 27,590 variants, none dropped.
**(B)** Model agreement as a share of the between-assay ceiling on matched variants; the ceiling is
the agreement of two independent assays on the same variants. n per domain as shown.
**(C)** Specificity axis (44 measurements, 16 domains): the model's prediction, a domain-agnostic
baseline, and the observed experimental profile. Shaded region marks effects smaller than 44
measurements can resolve (|r| < 0.44). All three fall inside it, including the observed profile.
**(D)** Leakage audit: held-out domains present in each competitor's published training split.
Colour-vision-safe palette throughout; generated from the committed result tables.
