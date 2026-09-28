# Literature review

**Scope.** The work this repository supports asks, for a cancer missense mutation in a human SH3
domain: does it destabilise the fold, or leave the fold intact and change binding? This review covers
the five bodies of work that question sits inside — the stability-as-disease-mechanism premise,
mega-scale stability measurement, ΔΔG prediction, SH3 binding specificity, and the cancer-genomic
null — and states where the pipeline agrees with, extends, or is anticipated by published work.

**Sources.** Searches were run against PubMed (via the NCBI E-utilities MCP server) and Consensus
(Semantic Scholar / PubMed / Scopus / arXiv, ~220 M papers) on 2026-09-23. Search strings and result
counts are recorded in [§7](#7-search-strategy-as-run) so the review can be reproduced or extended.
Records retrieved from PubMed carry their DOI; records retrieved from Consensus carry a Consensus
link, since that API does not return DOIs.

---

## 1. Is the premise sound? Stability as a mechanism of variant pathogenicity

The pipeline's central bet is that "does it break the fold?" is a question worth asking of a cancer
variant at all. That bet is well supported, and recently quantified.

[Site-saturation mutagenesis of 500 human protein domains](https://consensus.app/papers/details/a9650f9f207e5d7686d428c3c8058f9b/?utm_source=claude_code)
(Beltran et al., 2024, *Nature*, 111 citations) measured the effect of >500,000 variants on the
abundance of >500 human protein domains and reports that **60 % of pathogenic missense variants
reduce protein stability**. Two further findings bear directly on this project:

- the contribution of stability to fitness **varies by protein and by disease**, and is strongest in
  recessive disorders — a caution against reading a destabilising call as a pathogenicity call;
- **"mutational effects on stability are largely conserved in homologous domains, enabling accurate
  stability prediction across entire protein families using energy models."**

That second sentence partly anticipates B1's headline claim. The thesis should cite Beltran
explicitly and say what is *new* here: B1 holds out the SH3 family **as a family**, not
domain-by-domain, and reports calibrated per-domain intervals rather than a pooled correlation. The
novelty is the held-out-family protocol and the conformal calibration, not the observation that
stability generalises within a fold.

[Functionally constrained human proteins are less prone to mutational instability from single amino
acid substitutions](https://consensus.app/papers/details/fd2905c15fdb58438e13c0e458a51eb8/?utm_source=claude_code)
(May et al., 2025, *Nature Communications*, 12 citations) is the closest published frame for **B6's
depletion result**. They report that the most functionally constrained proteins are **depleted of both
destabilising and overly-stabilising variation in disease-free populations**, and that constrained
proteins are intrinsically less susceptible to large stability changes — mechanistically, via greater
intrinsic disorder and higher B-factors. B6 observes 5.9 % fold-breaking substitutions against a
9.2 % domain-matched expectation and currently hedges between purifying selection and mutational
bias. May et al. provide both a precedent for reading this as constraint **and** a confounder the
current null does not model: constrained proteins are *structurally* less mutable in stability terms,
independent of selection.

According to PubMed, a worked single-gene example of the same logic is Blackburn et al. (2024,
*Ann Neurol*), where loss-of-function *CUL3* variants act through protein-homeostasis perturbation
([DOI](https://doi.org/10.1002/ana.27077)) — useful as an illustration, not as evidence for the
general claim.

**Verdict.** The premise is sound and the literature is more specific than the thesis currently
acknowledges. Beltran (2024) should be cited in A1/B1; May (2025) should be cited in B6 and used to
sharpen the hedge.

---

## 2. Where the training data comes from: mega-scale folding stability

According to PubMed, the MegaScale dataset the pipeline trains on is
**Tsuboyama et al. (2023), *Nature* 620:434–444, "Mega-scale experimental analysis of protein folding
stability in biology and design"** ([DOI](https://doi.org/10.1038/s41586-023-06328-6)). cDNA display
proteolysis yields ~776,000 curated folding stabilities covering all single amino acid variants and
selected double mutants of 331 natural and 148 designed domains, 40–72 residues long. The 40–72
residue window is why SH3 (56–60 residues) is in scope at all, and the small-domain restriction is a
real external-validity limit that B4's weak ProteinGym transfer is probably detecting.

According to PubMed, that dataset now has a much larger successor. **Cho et al. (2026), bioRxiv,
"Accurate protein stability prediction for small domains using mega-scale experiments"**
([DOI](https://doi.org/10.64898/2026.05.19.726285)) applies the same method to **1.8 million domains
of 60–80 residues from MGnify, spanning >200,000 sequence families**. This is the single most
important paper for this project that the repository does not currently cite. It is directly
actionable: it is roughly an order of magnitude more training data, in the right length range, with
far broader family coverage — which is exactly what Recommendation #6 (hold out whole folds) and B4's
transfer problem call for.

---

## 3. Predicting ΔΔG: where B1 actually sits

Cho et al. also release predictors — **SaProtΔG and ESM3ΔG** — reporting **Spearman ρ 0.88 and RMSE
0.8 kcal/mol over a 6 kcal/mol range** for absolute folding stability of small domains.

**These numbers are not directly comparable to B1's, and the thesis must say so rather than invite the
comparison.** Three differences:

| | Cho et al. 2026 | B1 (this work) |
|---|---|---|
| Target | absolute ΔG of folding | ΔΔG of substitution |
| Split | sequence-family based | **whole SH3 family held out** |
| Reported | pooled ρ 0.88, RMSE 0.8 | per-domain median ρ 0.839, pooled RMSE 0.672 |

A pooled correlation over a 6 kcal/mol range of absolute stabilities and a per-domain rank correlation
within one small family are different quantities; the second is generally the harder number to move.
B1's honest claim is the **held-out-family protocol plus calibrated intervals**, not a state-of-the-art
accuracy claim. Stating this pre-emptively is stronger than having an examiner raise it.

According to PubMed, **Li & Luo (2025), bioRxiv, "Rewiring protein sequence and structure generative
models to enhance protein stability prediction" (SPURS)** ([DOI](https://doi.org/10.1101/2025.02.13.638154))
is the nearest methodological neighbour: it rewires ProteinMPNN per-residue structure representations
into ESM's attention layers and trains supervised on MegaScale, reporting state-of-the-art results
across 12 benchmarks. SPURS is the natural head-to-head baseline for B1 and is currently absent. Note
the contrast in design philosophy: SPURS *injects* structure; B1 deliberately withholds it, which is
what makes B2's burial-vs-interface dissociation (ρ +0.712 vs +0.037) interpretable at all. That
contrast is an argument in the thesis's favour and should be made explicitly.

---

## 4. The zero-shot baseline, and what beating it means

B1 benchmarks against zero-shot ESM-2. The surrounding literature has moved on, which affects how
strong "beats ESM-2 on 15/15" sounds.

According to PubMed:

- **Cheng et al. (2023), *Science* 381:eadg7492, AlphaMissense** ([DOI](https://doi.org/10.1126/science.adg7492))
  — AlphaFold fine-tuned on population frequency data, classifying 89 % of human missense variants as
  likely benign or likely pathogenic, with predictions released for every possible human substitution.
  Since the atlas is human and the calls are per-variant, an examiner will ask how B3's 410
  confidently-destabilising calls compare to AlphaMissense on the same variants. This is a cheap,
  high-value addition: the predictions are precomputed and downloadable.
- **Schubach et al. (2024), *Nucleic Acids Research* 52:D1143–D1154, CADD v1.7**
  ([DOI](https://doi.org/10.1093/nar/gkad989)) — now integrates ESM-1v protein language model scores and
  is evaluated on 31 ProteinGym DMS datasets. Relevant to B4 as a transfer reference point.
- **Kantroo et al. (2024), bioRxiv, "Pseudo-perplexity in One Fell Swoop for Protein Fitness
  Estimation"** ([DOI](https://doi.org/10.1101/2024.07.09.602754)) — a cheaper ESM-2 pseudo-perplexity
  estimate that sets state of the art on the ProteinGym Indels benchmark. Worth noting because it
  shows the zero-shot ESM-2 baseline is itself a moving target: *how* you score with ESM-2 matters as
  much as *whether* you do.

**Caveat the thesis should keep.** B1's ESM-2 comparison is signed, correctly — the recorded per-domain
ESM values are all strongly *negative* (median −0.617), i.e. the zero-shot score runs the wrong way
against measured ΔΔG under the convention used. "Beats ESM-2 15/15" is therefore true but partly
reflects a sign/convention failure of the baseline rather than a narrow margin of skill. The absolute-
value bug that was caught and fixed during the Colab run is exactly this hazard; the fix should be
described in the thesis text, not only in the results log.

---

## 5. Binding: two independent reasons SH3 resists prediction

This is where the review most changes the argument.

### 5.1 The data the pipeline uses

The GRB2-SH3 and PSD95-PDZ3 binding data underpinning C1–C3 come from
[Mapping the energetic and allosteric landscapes of protein binding domains](https://consensus.app/papers/details/ef7e4c4e657951448178aad99c7591e0/?utm_source=claude_code)
(Faure et al., 2022, *Nature*, 212 citations). Their ddPCA design infers causal biophysical effects of
mutations by measuring **binding and abundance in multiple genetic backgrounds** and fitting
thermodynamic models with neural networks — producing separate folding and binding energies. Two of
their findings are load-bearing for Part C and should be cited there: allosteric ("edgetic")
mutations are **abundant**, and mutations are **more likely to be allosteric closer to binding
interfaces**. If a large fraction of the binding signal is allosteric rather than interfacial, a model
given only sequence has a genuinely harder target than "learn the interface".

The methodological ancestor is
[Biophysical Inference of Epistasis and the Effects of Mutations on Protein Stability and
Function](https://consensus.app/papers/details/038c723b28a05d0db140cacf509e0efc/?utm_source=claude_code)
(Otwinowski, 2018, *Molecular Biology and Evolution*, 92 citations), which fits a three-state
(bound / unbound / unfolded) thermodynamic model to GB1–IgG-Fc data to infer distinct folding and
binding energies per mutation. GB1 appears in C2 and in the B1 ablations, so this is a direct
citation. Otwinowski's central point — **binding assays do not distinguish whether mutations affect
the binding interface or the overall fold** — is the thesis's own framing, stated six years earlier,
and citing it strengthens rather than weakens the contribution.

### 5.2 The reason the thesis gives

C3 argues predictability requires ~80 distinct mutated positions and an SH3 domain provides 56–60, so
the limit is **positional coverage**, and the fix is more domains rather than more mutations.

### 5.3 A second, independent reason the thesis does not currently give

[Protein context shapes the specificity of SH3 domain-mediated interactions in vivo](https://consensus.app/papers/details/b44df19ad8b3516eaf75cdea38cc949a/?utm_source=claude_code)
(Dionne et al., 2021, *Nature Communications*, 47 citations) deleted, mutated, swapped and shuffled
SH3 domains in yeast and found that **most SH3 domains do not dictate interaction specificity
independently of their host protein in vivo**. The identity of the host protein and the **position of
the domain within it** are critical — for specificity, for cellular function, and for phase
separation.

This is important. It says that even with unlimited positional coverage, a model that sees only the
isolated SH3 domain sequence may be predicting something that is not, in cells, determined by that
sequence alone. That is a *biological* ceiling sitting above C3's *statistical* one, and the thesis is
currently making only the statistical argument. Adding it makes Part C's negative result considerably
more robust: the claim becomes "insufficient data, and reason to doubt the target is well-posed from
domain sequence alone," which is much harder to dismiss as a modelling failure.

### 5.4 Specificity determinants and PWMs (context for C4)

According to PubMed, prior work on what encodes SH3 specificity:

- **Teyra, Sidhu & Kim (2012), *FEBS Letters* 586:2631–2637** ([DOI](https://doi.org/10.1016/j.febslet.2012.05.043))
  — review of large-scale specificity data and prediction algorithms for SH3 and PDZ domains;
  the direct ancestor of C4's PWM approach.
- **Longshore-Neate et al. (2024), *Frontiers in Molecular Biosciences* 11:1487276**
  ([DOI](https://doi.org/10.3389/fmolb.2024.1487276)) — the RT and nSrc loops govern Class I
  specificity, and a single position following a conserved Trp (the "WX motif") modulates nSrc loop
  conformation. Relevant to C4's failure: if specificity is set by a **few loop positions and their
  conformations**, collapsing each PWM into one 20-number profile (the acknowledged suspect in
  Recommendation #8) is very likely the wrong representation. Longshore-Neate gives a principled,
  pre-registerable alternative: model the RT/nSrc loop positions specifically.
- **Liu, Engelmann & Nash (2012), *Proteomics* 12:1527–1546** ([DOI](https://doi.org/10.1002/pmic.201100599))
  — survey of high-throughput peptide-binding-module analysis, including a proposed set of standards
  for validating large-scale interaction datasets. Useful for justifying C4's pre-registered decision
  rule, which is good practice the thesis should claim credit for.

---

## 6. The cancer-genomic null, and uncertainty

### 6.1 Selection vs mutational opportunity (B5, B6)

[Estimation of neutral mutation rates and quantification of somatic variant selection using
cancereffectsizeR](https://consensus.app/papers/details/36c117e240dd5dfc9d4dcd4f83c277da/?utm_source=claude_code)
(Mandell et al., 2022, *Cancer Research*, 26 citations) is an off-the-shelf implementation of exactly
what Recommendation #2 proposes building: it estimates **site-specific neutral mutation rates** from
mutational signatures and tests models of selection, from single nucleotides up to whole genes.
Adopting it rather than writing a bespoke signature-aware null would be faster, and — more
importantly — would make B6's depletion result comparable to a published, validated method instead of
resting on an in-house background model. They also report that cancer effect size predicts pathogenic
status better than variant prevalence or functional-impact scores, which is a useful independent check
on B5's null finding.

For signature estimation itself, [Flexible model-based non-negative matrix factorization with
application to mutational signatures](https://consensus.app/papers/details/629134e492475075ae97aa6bc4c459ed/?utm_source=claude_code)
(Laursen et al., 2024, *Statistical Applications in Genetics and Molecular Biology*) argues that
**di-nucleotide** interaction models often beat both mono- and tri-nucleotide parametrisations on the
fit/overfit trade-off. If a signature-aware null is built, this is worth reading before defaulting to
trinucleotide context.

### 6.2 Conformal intervals (B3)

According to PubMed, **Fannjiang et al. (2022), *PNAS* 119:e2204569119, "Conformal prediction under
feedback covariate shift for biomolecular design"** ([DOI](https://doi.org/10.1073/pnas.2204569119))
is the reference for conformal prediction in exactly this setting: confidence sets with finite-sample
guarantees for any regression model, for predicted protein fitness, specifically motivated by the cost
of wet-lab validation. Two points for the thesis:

1. It **justifies B3's design choice** over the seed-spread filter that was discarded — worth citing,
   since the thesis presents that replacement as a correction rather than as an alignment with
   established practice.
2. Its subject is **feedback covariate shift** — training and test data becoming statistically
   dependent because the model chose what to test next. F1 selects 10 bench candidates using B3's own
   intervals. If those results ever feed back into the model, Fannjiang's correction is the relevant
   machinery, and B3's marginal guarantee would no longer hold as stated.

---

## 7. Search strategy, as run

Reproducible per PRISMA-style reporting. Date: 2026-09-23.

| # | Database | Query | Results |
|---|---|---|---|
| 1 | PubMed | `SH3 domain peptide binding specificity human family proteome` | 27 (12 screened) |
| 2 | PubMed | `mega-scale deep mutational scanning protein folding stability ddG prediction` | 0 — over-specified |
| 3 | PubMed | `protein language model zero-shot variant effect prediction benchmark` | 3 |
| 4 | PubMed | `cancer missense mutation protein stability destabilization driver passenger` | 0 — over-specified |
| 5 | PubMed | `ProteinGym` | 11 |
| 6 | PubMed | `protein stability mega-scale folding`, from 2022 | 7 |
| 7 | PubMed | `protein stability loss Mendelian disease variants`, from 2020 | 25 (low precision) |
| 8 | PubMed | `conformal prediction uncertainty quantification proteins` | 10 |
| 9 | PubMed | `AlphaMissense proteome-wide missense variant pathogenicity` | 1 |
| 10 | PubMed | `COSMIC catalogue somatic mutations cancer`, from 2018 | 253 (not screened) |
| 11 | Consensus | decomposing mutational effects into folding stability and binding affinity | 3 |
| 12 | Consensus | SH3 domain somatic cancer mutations signaling rewiring | 3 |
| 13 | Consensus | trinucleotide mutational signature background model negative selection | 3 |
| 14 | Consensus | loss of protein stability as mechanism for pathogenic missense variants | 3 |

**Method note.** Queries 2 and 4 returned zero results: PubMed's automatic term mapping ANDs every
expanded concept, so long multi-concept strings over-constrain. Both were recovered by decomposing
into 2–3 core concepts (queries 5, 6) or by moving to Consensus, which handles natural-language
queries. This is the documented "overly long query" failure mode and is recorded here because anyone
re-running these searches will hit it.

**Known gaps.** (a) Consensus returns a maximum of 3 results per query on the free tier, so coverage
in queries 11–14 is shallow and should be extended. (b) arXiv and Google Scholar were not searched;
several relevant ML methods papers (ESM-2, ProteinGym, ProteinMPNN) are arXiv/NeurIPS-primary and are
cited here only where a PubMed-indexed version exists. (c) Query 10 (COSMIC) was not screened —
the canonical COSMIC citation should be taken from the version of the database actually used in A0.

---

## 8. What this means for the thesis

Ordered by how much each changes the argument.

1. **Add Dionne et al. (2021) to Part C.** It supplies a second, independent, *biological* reason SH3
   binding may not be predictable from domain sequence — sitting above C3's statistical
   data-sufficiency argument. This is the single largest strengthening available, and it costs one
   paragraph.
2. **Cite Faure et al. (2022) as the data source in C1–C3, and use their allostery result.** Abundant
   allosteric variants, enriched near interfaces, explain *why* the target is hard in biophysical
   terms rather than only statistical ones.
3. **Cite Beltran et al. (2024) in A1/B1 and differentiate.** They already showed stability effects
   generalise within homologous families. B1's contribution is the held-out-*family* protocol and
   calibrated intervals — say that plainly.
4. **Address Cho et al. (2026) directly in B1 and B4.** State that ρ 0.88 and ρ 0.839 measure different
   things, and treat the MGnify Stability dataset as the obvious route to Recommendation #6.
5. **Use May et al. (2025) to sharpen B6.** It gives both a precedent for the depletion reading and a
   structural confounder the current null misses.
6. **Consider cancereffectsizeR (Mandell et al., 2022) instead of a bespoke null for Recommendation #2.**
   Faster, and comparable to published work.
7. **Add AlphaMissense as a per-variant comparator in B3.** Precomputed, human-proteome-wide, cheap.
8. **Add SPURS (Li & Luo, 2025) as a B1 baseline,** and use the structure-injected vs structure-free
   contrast to argue for B2's interpretability.
9. **Cite Fannjiang et al. (2022) in B3,** and note the feedback-covariate-shift caveat for F1.
10. **Use Longshore-Neate et al. (2024) to design C4's second attempt** around RT/nSrc loop positions
    rather than a collapsed 20-number profile.

---

## References

Retrieved from PubMed (DOI links as required by the source database):

- Blackburn, P.R. et al. (2024). Loss-of-Function Variants in CUL3 Cause a Syndromic Neurodevelopmental Disorder. *Annals of Neurology*. [10.1002/ana.27077](https://doi.org/10.1002/ana.27077)
- Cheng, J. et al. (2023). Accurate proteome-wide missense variant effect prediction with AlphaMissense. *Science* 381:eadg7492. [10.1126/science.adg7492](https://doi.org/10.1126/science.adg7492)
- Cho, Y. et al. (2026). Accurate protein stability prediction for small domains using mega-scale experiments. *bioRxiv*. [10.64898/2026.05.19.726285](https://doi.org/10.64898/2026.05.19.726285)
- Fannjiang, C. et al. (2022). Conformal prediction under feedback covariate shift for biomolecular design. *PNAS* 119:e2204569119. [10.1073/pnas.2204569119](https://doi.org/10.1073/pnas.2204569119)
- Kantroo, P. et al. (2024). Pseudo-perplexity in One Fell Swoop for Protein Fitness Estimation. *bioRxiv*. [10.1101/2024.07.09.602754](https://doi.org/10.1101/2024.07.09.602754)
- Li, Z. & Luo, Y. (2025). Rewiring protein sequence and structure generative models to enhance protein stability prediction. *bioRxiv*. [10.1101/2025.02.13.638154](https://doi.org/10.1101/2025.02.13.638154)
- Liu, B.A., Engelmann, B.W. & Nash, P.D. (2012). High-throughput analysis of peptide-binding modules. *Proteomics* 12:1527–1546. [10.1002/pmic.201100599](https://doi.org/10.1002/pmic.201100599)
- Longshore-Neate, F. et al. (2024). The conformation of the nSrc specificity-determining loop in the Src SH3 domain is modulated by a WX conserved sequence motif. *Frontiers in Molecular Biosciences* 11:1487276. [10.3389/fmolb.2024.1487276](https://doi.org/10.3389/fmolb.2024.1487276)
- Schubach, M. et al. (2024). CADD v1.7: using protein language models, regulatory CNNs and other nucleotide-level scores. *Nucleic Acids Research* 52:D1143–D1154. [10.1093/nar/gkad989](https://doi.org/10.1093/nar/gkad989)
- Teyra, J., Sidhu, S.S. & Kim, P.M. (2012). Elucidation of the binding preferences of peptide recognition modules: SH3 and PDZ domains. *FEBS Letters* 586:2631–2637. [10.1016/j.febslet.2012.05.043](https://doi.org/10.1016/j.febslet.2012.05.043)
- Tsuboyama, K. et al. (2023). Mega-scale experimental analysis of protein folding stability in biology and design. *Nature* 620:434–444. [10.1038/s41586-023-06328-6](https://doi.org/10.1038/s41586-023-06328-6)

Retrieved via Consensus (no DOI returned by that API; links are to the Consensus record):

- Beltran, A. et al. (2024). [Site-saturation mutagenesis of 500 human protein domains](https://consensus.app/papers/details/a9650f9f207e5d7686d428c3c8058f9b/?utm_source=claude_code). *Nature*.
- Dionne, U. et al. (2021). [Protein context shapes the specificity of SH3 domain-mediated interactions in vivo](https://consensus.app/papers/details/b44df19ad8b3516eaf75cdea38cc949a/?utm_source=claude_code). *Nature Communications*.
- Faure, A.J. et al. (2022). [Mapping the energetic and allosteric landscapes of protein binding domains](https://consensus.app/papers/details/ef7e4c4e657951448178aad99c7591e0/?utm_source=claude_code). *Nature*.
- Laursen, R. et al. (2024). [Flexible model-based non-negative matrix factorization with application to mutational signatures](https://consensus.app/papers/details/629134e492475075ae97aa6bc4c459ed/?utm_source=claude_code). *Statistical Applications in Genetics and Molecular Biology*.
- Mandell, J.D. et al. (2022). [Estimation of neutral mutation rates and quantification of somatic variant selection using cancereffectsizeR](https://consensus.app/papers/details/36c117e240dd5dfc9d4dcd4f83c277da/?utm_source=claude_code). *Cancer Research*.
- May, M. et al. (2025). [Functionally constrained human proteins are less prone to mutational instability from single amino acid substitutions](https://consensus.app/papers/details/fd2905c15fdb58438e13c0e458a51eb8/?utm_source=claude_code). *Nature Communications*.
- Otwinowski, J. (2018). [Biophysical Inference of Epistasis and the Effects of Mutations on Protein Stability and Function](https://consensus.app/papers/details/038c723b28a05d0db140cacf509e0efc/?utm_source=claude_code). *Molecular Biology and Evolution*.

Literature retrieved from PubMed; citations include DOIs as required by that database's terms of use.
