# SH3 Mutation-Effect Project — Complete Upgrade Roadmap from the Base Notebook

## 0. Purpose

This document lists possible upgrades, extensions, validation experiments, and new research directions that can be developed from the current SH3-domain mutation-effect notebook.

The roadmap is intentionally broad. It separates:

- upgrades that improve the existing pipeline;
- experiments that test the limitations of the baseline;
- new models that add a genuine second biological mechanism;
- new biological analyses that can be built on the cancer atlas;
- larger future projects that should only be attempted after the core system is stable.

The baseline report describes a single-notebook pipeline that uses six input files, frozen ESM-2 representations, a folding prediction head, a binding-feasibility analysis, conformal uncertainty, structural checks, cancer-atlas analysis, and self-verification. The baseline folding result is Spearman rho = 0.839 across 15 held-out SH3 domains, while external stability performance drops to rho = 0.361. The binding analysis identifies an approximate positional-coverage limitation around 80 distinct mutagenized positions, while individual SH3 domains contain roughly 56–60 residues.

---

# 1. BASE NOTEBOOK: STARTING POINT

## 1.1 Current data inputs

- MegaScale / processed folding-stability measurements
- ddPCA / MoCHI measurements
- ProteinGym substitution assays
- ProteinGym assay list
- SH3 cancer mutation atlas
- Human SH3 domain boundaries
- ESM-2 protein-language-model representations
- Structural annotation for application data

## 1.2 Current feature representation

- ESM-2 residue representation
- ESM-derived mutation score / masked-marginal information
- Wild-type probability
- Positional entropy
- Relative position
- Domain length
- Hydropathy change
- Volume change
- Charge change
- BLOSUM62 score
- To-proline flag
- From-glycine flag
- To-glycine flag

## 1.3 Current folding model

- Frozen ESM-2 backbone
- MLP regression head
- Training primarily on MegaScale-derived data
- Grouped domain-level split
- Held-out SH3 domains
- Five-seed ensemble
- AdamW
- Early stopping / validation selection
- RMSE + Spearman-based evaluation

## 1.4 Current binding analysis

- ddPCA / MoCHI binding measurements
- Within-domain position-held-out cross-validation
- PCA-based feature compression
- Single-hidden-layer model
- Systematic position-coverage subsampling
- Analysis of the relationship between distinct positions and predictive signal

## 1.5 Current uncertainty model

- Split conformal prediction
- Global calibration quantile
- Prediction interval
- High-confidence destabilization calling

## 1.6 Current cancer application

- 6,884 curated SH3-domain missense variants
- 310 SH3 domains
- 235 genes
- Hypermutation-aware analysis
- Structural burial analysis
- Interface proximity analysis
- Gene enrichment
- Tumour-site enrichment
- Positional distribution tests
- Burial-matched permutation null

## 1.7 Current verification

- Input checksums
- Sign calibration
- Reproduction of headline quantities
- Multiple independent validation blocks
- Recorded-result comparison

---

# 2. UPGRADE CATEGORY A — DATA QUALITY AND DATASET ENGINEERING

## A1. Add an explicit data-quality report

Create an automatic report for every input dataset:

- number of rows
- number of unique proteins
- number of domains
- number of unique positions
- missing values
- duplicated variants
- conflicting labels
- sequence mismatches
- coordinate mismatches
- impossible amino-acid substitutions
- outlier measurements
- assay-level sample size

**Benefit:** makes the notebook auditable before training begins.

**Priority:** High

---

## A2. Add automated sequence validation

For every variant:

1. retrieve reference sequence;
2. check accession and residue numbering;
3. verify wild-type amino acid;
4. verify mutant amino acid;
5. verify domain boundaries;
6. reject or flag inconsistencies.

Create a table of:

- accepted variants
- rejected variants
- sequence mismatch reason
- coordinate mismatch reason

**Priority:** High

---

## A3. Improve isoform handling

Extend the current alternative-transcript mapping to explicitly track:

- canonical UniProt sequence;
- alternative isoform;
- transcript coordinate;
- protein coordinate;
- SH3-domain coordinate;
- confidence of mapping.

**Priority:** Medium–High

---

## A4. Version every dataset

Store:

- source URL
- source paper
- version
- repository commit
- download date
- checksum
- transformation script version

Create a machine-readable `data_manifest.yaml` or `data_manifest.json`.

**Priority:** High

---

## A5. Build a unified variant identifier

For example:

`UniProt + domain + WT residue + position + MUT residue`

Use this identifier across all datasets.

**Priority:** High

---

## A6. Add assay-level harmonization

Instead of simply pooling experiments, learn or estimate assay-specific offsets/scales.

Potential approaches:

- standardization within assay;
- mixed-effects models;
- assay-specific intercepts;
- assay-specific variance models;
- hierarchical Bayesian normalization.

**Priority:** Medium

---

# 3. UPGRADE CATEGORY B — BETTER ESM REPRESENTATIONS

## B1. Compare ESM-2 model sizes

Compare multiple frozen backbones:

- ESM-2 8M
- ESM-2 35M
- ESM-2 150M
- ESM-2 650M
- ESM-2 3B

Measure:

- accuracy
- GPU memory
- inference time
- storage
- generalization

**Priority:** Medium

---

## B2. Compare per-residue pooling strategies

Instead of using only the mutated residue representation, compare:

- mutated-residue token
- ±2 residue window
- ±5 residue window
- ±10 residue window
- whole-domain mean pooling
- attention pooling
- learned pooling
- mutation-centered pooling

**Priority:** High

---

## B3. Local sequence-context encoder

Add a 1D CNN or lightweight Transformer around the mutation.

Example:

`ESM residue embeddings → local window → CNN → pooling → ΔΔG`

This tests whether local sequence interactions are missing from the baseline MLP.

**Priority:** High

---

## B4. Fine-tune ESM instead of freezing it

Compare:

- frozen ESM + MLP
- last-layer fine-tuning
- top-N-layer fine-tuning
- full fine-tuning
- parameter-efficient fine-tuning

**Priority:** High, but computationally more expensive

---

## B5. LoRA / parameter-efficient fine-tuning

Use LoRA or similar adapters on a larger protein-language model.

Compare:

- parameter count
- performance
- overfitting
- external generalization

**Priority:** Medium–High

---

## B6. ESM3 / newer foundation model comparison

Use newer protein foundation models as a controlled model comparison.

Keep the data split identical to the ESM-2 baseline.

**Priority:** Medium

---

## B7. Structure-aware language model

Evaluate a structure-aware protein language model such as SaProt.

Representation idea:

`AA tokens + 3Di structural tokens → representation → mutation predictor`

**Priority:** High for a second-generation model

---

# 4. UPGRADE CATEGORY C — STRUCTURE-AWARE FOLDING PREDICTION

## C1. Add basic structural features uniformly

Only add a structural feature if it can be generated consistently for both training and application datasets.

Possible features:

- relative solvent accessibility
- residue depth
- secondary structure
- contact number
- local packing density
- residue-residue contact count
- local backbone geometry

**Priority:** High

---

## C2. Generate structures for all training domains

Potential structure sources:

- experimentally solved structures
- AlphaFold DB
- ESMFold
- another structure prediction pipeline

Then compute the same structural descriptors for all datasets.

**Priority:** High

---

## C3. Graph neural network branch

Represent the protein domain as a graph:

- node = residue
- node features = amino-acid/ESM/structural embedding
- edge = spatial contact
- edge features = distance/orientation/contact type

Possible models:

- GCN
- GAT
- message passing network
- EGNN

Then predict ΔΔGfold from the mutation-centered graph.

**Priority:** High

---

## C4. Sequence–structure fusion model

Parallel branches:

```text
ESM-2 / ESM3 sequence encoder
                ↓
           sequence z

3D structure / GNN encoder
                ↓
           structure z

sequence z + structure z
                ↓
           fusion layer
                ↓
           ΔΔGfold
```

**Priority:** Very High

---

## C5. Cross-attention between sequence and structure

Instead of concatenating embeddings, allow the sequence branch and structure branch to attend to each other.

Possible comparison:

- concatenation
- gated fusion
- cross-attention

**Priority:** Medium

---

## C6. Mutation-centered structural neighborhood

Construct a local 3D neighborhood around the mutated residue.

Input:

- mutation residue
- residues within 6 Å
- residues within 8 Å
- residues within 10 Å

Compare local-only versus whole-domain structural models.

**Priority:** High

---

# 5. UPGRADE CATEGORY D — PHYSICAL / THERMODYNAMIC CONSTRAINTS

## D1. Antisymmetric ΔΔG prediction

Impose:

`ΔΔG(WT → MUT) = -ΔΔG(MUT → WT)`

Possible implementations:

- antisymmetric prediction head
- difference of state scores
- antisymmetric loss penalty
- pairwise energy model

**Priority:** High

---

## D2. Energy-state model

Instead of directly predicting ΔΔG, learn an energy-like function:

`E(sequence, structure)`

Then calculate:

`ΔΔG = E(mutant) - E(wild type)`

This automatically creates a consistent forward/reverse difference.

**Priority:** Very High as an advanced model

---

## D3. Stabilizing-vs-destabilizing ranking loss

Add a ranking component to the regression objective.

Example:

`L = L_RMSE + λ L_rank`

Possible ranking metrics/losses:

- pairwise ranking loss
- Spearman-oriented loss
- NDCG-style loss

**Priority:** Medium–High

---

## D4. Magnitude-aware loss

Weight severe mutations differently from near-neutral variants.

Possible methods:

- Huber loss
- weighted MSE
- uncertainty-weighted loss
- distribution-aware loss

**Priority:** Medium

---

# 6. UPGRADE CATEGORY E — BINDING FREE-ENERGY PREDICTION

## E1. Keep the current position-coverage experiment

This becomes an important baseline and data-sufficiency result.

Continue measuring:

- number of rows
- number of unique positions
- number of domains
- predictive correlation

**Priority:** Required baseline

---

## E2. Multi-domain binding training

Pool multiple compatible ddPCA/domain datasets.

Possible training strategy:

`domain A + domain B + domain C → shared encoder → ΔΔGbind`

Then evaluate:

- within-domain prediction
- cross-domain prediction
- family-level prediction

**Priority:** High

---

## E3. Family-aware versus cross-family training

Compare:

1. SH3 only
2. SH3 + closely related interaction modules
3. SH3 + PDZ + WW
4. domain-family-specific adapters

Do not assume cross-family pooling improves performance; test it explicitly.

**Priority:** Medium

---

## E4. Position-conditioned binding model

Input:

- mutation position
- local sequence context
- domain identity embedding
- ESM representation
- optional structure

Predict:

`ΔΔGbind`

**Priority:** High

---

## E5. Epistatic binding model

Use an attention architecture to learn residue-residue dependencies.

Possible models:

- Transformer
- pairwise interaction network
- low-rank bilinear model
- bounded attention model

**Priority:** Medium

---

# 7. UPGRADE CATEGORY F — TRUE BINDING-SPECIFICITY / REWIRING MODEL

## F1. Build an SH3 specificity predictor from experimental PWMs

Use published SH3 specificity profiles as the training target.

Input:

`SH3 sequence`

Output:

`peptide preference PWM`

Potential architecture:

`ESM / sequence encoder → specificity head → PWM`

**Priority:** Very High

---

## F2. Wild-type versus mutant specificity comparison

Predict:

`PWM_WT`

and

`PWM_MUT`

Then calculate:

- KL divergence
- Jensen–Shannon divergence
- cosine distance
- Earth mover's distance
- position-specific entropy change

**Priority:** Very High

---

## F3. Specificity rewiring score

Define an experimentally motivated score such as:

`Rewiring = distance(PWM_WT, PWM_MUT)`

This produces a second biological axis that is not the same as ESM mutation likelihood.

**Priority:** Very High

---

## F4. Peptide-ranking model

Instead of directly predicting a PWM, train the model to rank peptides:

`SH3 + peptide → binding score`

Use:

- pairwise ranking loss
- contrastive learning
- triplet loss

**Priority:** High

---

## F5. Mutation-induced peptide preference change

For each cancer mutation:

1. predict WT peptide preference;
2. predict mutant peptide preference;
3. measure gained preferences;
4. measure lost preferences;
5. identify motif rewiring.

Potential outputs:

- lost motif
- gained motif
- specificity broadening
- specificity narrowing
- preference shift

**Priority:** Very High

---

# 8. UPGRADE CATEGORY G — CANCER MUTATION ANALYSIS

## G1. Improved mutational-opportunity null

Current positional tests can be improved by matching mutations on:

- trinucleotide context
- nucleotide substitution type
- codon
- gene mutation burden
- genomic context
- tumour type

**Priority:** Very High

---

## G2. Mutational-signature correction

Incorporate known cancer mutational processes, for example:

- APOBEC-related processes
- UV-related processes
- CpG deamination
- mismatch-repair-associated processes

Test whether structural enrichment remains after correcting for mutational opportunity.

**Priority:** High

---

## G3. Rare-variant prioritization model

Combine:

- predicted ΔΔGfold
- specificity rewiring score
- conservation
- structural position
- cancer recurrence
- mutational opportunity
- functional annotations

Output a mechanism-oriented prioritization score.

Do not treat this score as a clinical diagnosis without independent validation.

**Priority:** High

---

## G4. Pan-SH3 structural hotspot analysis

Map all 310 SH3 domains onto a shared family reference or structural alignment.

Test for:

- recurrent structural positions
- family-wide mutation clusters
- interface hotspots
- buried-core hotspots
- candidate functional hotspots

**Priority:** High

---

## G5. 3D mutation clustering

Use domain structures to test whether cancer mutations cluster in:

- core
- interface
- loops
- functional surfaces
- spatial neighborhoods

Compare against matched null simulations.

**Priority:** High

---

## G6. Gene-level analysis

Compare predicted mechanism distributions across genes.

For each gene:

- number of variants
- destabilizing fraction
- specificity-change fraction
- dual-mechanism fraction
- confidence intervals

Control for low sample size.

**Priority:** Medium

---

## G7. Tumour-type analysis

Compare mechanism distributions across tumour types.

Potential questions:

- Which tumour types contain more SH3 variants?
- Are mutations concentrated in certain structural regions?
- Are particular mutational mechanisms associated with particular tumour types?

Use multiple-testing correction and exposure/mutational-opportunity controls.

**Priority:** Medium

---

# 9. UPGRADE CATEGORY H — ALLOSTERY AND DISTAL EFFECTS

## H1. Interface versus distal mutation classification

Divide mutations into:

- direct interface
- near-interface
- distal
- buried core
- surface

Compare predicted functional effects between classes.

**Priority:** High

---

## H2. Stability-independent functional score

Estimate whether a variant's predicted functional effect exceeds what is expected from its predicted stability effect.

Conceptual model:

`functional residual = functional effect - expected stability contribution`

Treat the residual as a hypothesis-generating score, not proof of allostery.

**Priority:** Very High

---

## H3. Contact-network propagation

Build residue contact graphs and measure whether mutation effects propagate through:

- short paths
- high-betweenness residues
- community boundaries
- allosteric networks

**Priority:** High

---

## H4. Graph-based allosteric predictor

Input:

- residue contact graph
- mutation location
- sequence representation
- structural features

Output:

- predicted distal functional effect

**Priority:** Advanced

---

# 10. UPGRADE CATEGORY I — UNCERTAINTY AND CALIBRATION

## I1. Stratified/Mondrian conformal prediction

Current method uses a global calibration quantile.

Possible strata:

- buried
- surface
- interface
- secondary structure
- domain family
- prediction-confidence bin

Measure:

- empirical coverage
- interval width
- coverage by structural class

**Priority:** Medium–High

---

## I2. Adaptive prediction intervals

Compare:

- global conformal
- stratified conformal
- locally weighted conformal
- quantile regression + conformal calibration

**Priority:** Medium

---

## I3. Calibration curves

Plot:

- nominal coverage vs empirical coverage
- confidence vs observed error
- interval width vs error
- confidence vs structural context

**Priority:** High

---

## I4. Prediction-rejection curve

Ask:

> If the model only reports its highest-confidence 5%, 10%, 20%, etc., how accurate are those predictions?

This is useful for experimental prioritization.

**Priority:** High

---

# 11. UPGRADE CATEGORY J — EVALUATION AND BENCHMARKING

## J1. Homology-aware splitting

Cluster homologous proteins/domains first, then split by cluster.

Compare:

- random split
- domain split
- sequence-identity cluster split
- strict homology split

**Priority:** Very High

---

## J2. Leave-one-domain-family-out validation

Train on other domain families and test on SH3 where scientifically appropriate.

This tests transferability rather than memorization.

**Priority:** Medium

---

## J3. Per-domain reporting

Do not report only pooled correlation.

Report:

- median per-domain Spearman
- median absolute correlation
- interquartile range
- worst-domain performance
- best-domain performance

**Priority:** Required

---

## J4. Error decomposition

Break error down by:

- amino-acid substitution type
- position
- structural class
- secondary structure
- buried/interface status
- domain family
- effect magnitude

**Priority:** High

---

## J5. Calibration versus extrapolation test

Measure performance separately on:

- well-represented mutations
- rare amino-acid substitutions
- unseen substitution types
- unseen positions
- unseen domains
- unseen homologs

**Priority:** Very High

---

## J6. External benchmark panel

Where phenotype definitions are compatible, compare with appropriate methods such as:

- ESM zero-shot baselines
- EVE-like evolutionary models
- FoldX-like structural energy models
- ThermoMPNN-like structural predictors
- newer sequence–structure predictors

Always compare the same phenotype and disclose differences in assay type.

**Priority:** High

---

# 12. UPGRADE CATEGORY K — ABLATION STUDIES

## K1. Feature ablation

Train separate models with:

- ESM only
- ESM + biochemical scalars
- ESM + local sequence
- ESM + structure
- all features

**Priority:** Very High

---

## K2. Model ablation

Compare:

- linear regression
- ridge/lasso
- random forest
- XGBoost
- MLP
- CNN
- Transformer
- GNN
- sequence–structure fusion

**Priority:** High

---

## K3. Backbone ablation

Compare different protein foundation models under identical preprocessing.

**Priority:** Medium

---

## K4. Structural-feature ablation

Test which individual structural variables matter:

- RSA
- contact number
- distance to interface
- secondary structure
- local packing
- graph embedding

**Priority:** High

---

# 13. UPGRADE CATEGORY L — INTERPRETABILITY

## L1. Mutation-attribution analysis

Identify which sequence tokens or residues drive a prediction.

Methods:

- integrated gradients
- occlusion
- attention analysis
- SHAP for compact heads

**Priority:** High

---

## L2. Structural attribution map

Map model attribution onto the 3D structure.

Output:

- hot residues
- predicted destabilization hotspots
- predicted specificity hotspots

**Priority:** Very High

---

## L3. Counterfactual mutations

For one residue, evaluate all 19 possible substitutions.

Create a full mutation landscape:

`20 amino acids × each SH3 position`

This can generate a computational DMS map.

**Priority:** Very High

---

## L4. In silico saturation mutagenesis

For every SH3 domain:

1. mutate every residue to every amino acid;
2. predict folding effect;
3. predict specificity effect;
4. assign uncertainty;
5. produce a functional landscape.

**Priority:** Very High

---

# 14. UPGRADE CATEGORY M — NEW COMPUTATIONAL BIOLOGY PRODUCTS

## M1. SH3 mutation atlas browser

Build a web/local dashboard showing:

- gene
- SH3 domain
- mutation
- folding prediction
- specificity prediction
- confidence
- burial
- interface distance
- tumour type

**Priority:** High

---

## M2. Interactive 3D mutation viewer

For each selected variant:

- WT structure
- mutant structure/model
- mutation location
- buried/interface status
- predicted effect
- confidence interval

**Priority:** High

---

## M3. SH3 sequence-to-mechanism tool

Input:

`protein sequence + mutation`

Output:

- predicted ΔΔGfold
- predicted specificity change
- confidence
- structural context
- mechanism category

**Priority:** High after validation

---

## M4. Experimental prioritization tool

Rank variants for experimental testing based on:

- effect magnitude
- confidence
- novelty
- mechanism uncertainty
- assay feasibility

**Priority:** High

---

# 15. UPGRADE CATEGORY N — EXPERIMENTAL FOLLOW-UP

## N1. Validate top predicted destabilizing variants

Candidate assays:

- thermal denaturation
- proteolysis-based stability assay
- abundance assay
- ddPCA

**Priority:** Very High

---

## N2. Validate specificity-rewiring variants

For selected variants:

- choose WT-preferred peptides;
- choose predicted mutant-preferred peptides;
- test gain/loss of binding.

Possible experimental approaches:

- phage display
- peptide array
- fluorescence polarization
- ITC
- SPR
- yeast/cell-based binding assays

**Priority:** Very High

---

## N3. Dual validation

Select variants predicted to be:

- destabilizing only
- specificity-changing only
- both
- neutral

Then experimentally compare all four groups.

This would directly test the mechanistic model.

**Priority:** Extremely High for a later research project

---

# 16. UPGRADE CATEGORY O — MULTI-MUTATION / EPISTASIS

## O1. Double-mutant prediction

Train or evaluate pairwise mutations.

Questions:

- additive or non-additive?
- suppressor mutations?
- compensatory mutations?
- synergistic destabilization?

**Priority:** Medium

---

## O2. Pairwise residue interaction model

Model:

`effect(i,j) ≠ effect(i) + effect(j)`

Use:

- pairwise bilinear layers
- attention
- graph networks

**Priority:** Medium

---

## O3. Compensatory mutation discovery

Search for mutations that reverse another mutation's predicted destabilization.

Potential output:

`primary mutation → predicted suppressor mutations`

**Priority:** Advanced

---

# 17. UPGRADE CATEGORY P — KNOWLEDGE TRANSFER TO OTHER DOMAINS

## P1. PDZ extension

PDZ domains are especially useful because the available datasets can provide a different domain-size regime.

Test whether the positional-coverage relationship generalizes.

**Priority:** High as a second-domain-family study

---

## P2. SH2 / WW extension

Apply the same framework to other interaction modules.

**Priority:** Medium

---

## P3. Cross-domain universal interaction model

Build a general model for modular protein–protein interaction domains.

Potential inputs:

- domain sequence
- structure
- peptide
- mutation
- domain family

Outputs:

- stability
- binding
- specificity

**Priority:** Long-term

---

# 18. UPGRADE CATEGORY Q — FOUNDATION-MODEL / MULTIMODAL RESEARCH

## Q1. Sequence + structure + peptide model

Three branches:

```text
sequence → sequence encoder
structure → graph encoder
peptide → peptide encoder
              ↓
         cross-attention
              ↓
        interaction score
```

**Priority:** Advanced

---

## Q2. Protein–peptide co-folding as a validation module

Use modern biomolecular complex models only for selected high-priority variants.

Do not make complex prediction the primary source of binding truth unless experimentally supported.

**Priority:** Advanced

---

## Q3. Structure-conditioned inverse folding features

Use inverse-folding models as structural representations or auxiliary objectives.

Potential applications:

- mutation compatibility
- structural plausibility
- interface redesign

**Priority:** Medium–Advanced

---

# 19. UPGRADE CATEGORY R — CANCER GENOMICS EXTENSIONS

## R1. Mutational signature-aware background model

Estimate mutation probability from extended DNA sequence context and known mutational processes.

Then ask whether a variant is unusual relative to its expected background.

**Priority:** High

---

## R2. Selection-aware SH3 analysis

Combine:

- mutation opportunity
- observed counts
- protein effect prediction
- structural context

Test whether rare structural damaging variants occur more often than expected.

**Priority:** High

---

## R3. Pan-cancer mechanism comparison

Group by:

- tumour type
- gene
- SH3 domain
- structural class
- mutation mechanism

**Priority:** Medium

---

## R4. Driver/passenger hypothesis generation

Use the protein-level model only as a functional prioritization layer.

Do not treat the output as a validated cancer-driver classifier without independent evidence.

**Priority:** High

---

# 20. UPGRADE CATEGORY S — STATISTICAL / MACHINE-LEARNING ANALYSIS

## S1. Mixed-effects model baseline

Model domain-level and assay-level variation explicitly.

Example:

`effect ~ mutation_features + (1 | domain) + (1 | assay)`

Compare with the neural network.

**Priority:** Medium

---

## S2. Bayesian uncertainty model

Compare conformal intervals with:

- Bayesian neural network
- deep ensembles
- Monte Carlo dropout
- heteroscedastic regression

**Priority:** Medium

---

## S3. Heteroscedastic regression

Predict:

- expected effect
- prediction variance

simultaneously.

**Priority:** High

---

## S4. Quantile regression

Predict multiple quantiles directly:

- 5%
- 25%
- 50%
- 75%
- 95%

Then compare with conformal calibration.

**Priority:** Medium

---

# 21. UPGRADE CATEGORY T — REPRODUCIBILITY / ENGINEERING

## T1. Split notebook into modules

Convert the single notebook into:

```text
01_data_validation.ipynb
02_feature_generation.ipynb
03_folding_model.ipynb
04_binding_model.ipynb
05_specificity_model.ipynb
06_cancer_analysis.ipynb
07_validation.ipynb
08_figures.ipynb
```

**Priority:** High

---

## T2. Command-line pipeline

Create:

`python run_pipeline.py --config config.yaml`

**Priority:** Medium

---

## T3. Experiment tracking

Record:

- seed
- model
- hyperparameters
- data version
- split
- metrics
- checkpoint
- execution time

Tools could include a lightweight CSV/JSON log or MLflow/W&B if desired.

**Priority:** Medium

---

## T4. Unit tests

Test:

- sequence mapping
- sign convention
- mutation parsing
- feature dimensions
- model output shape
- conformal interval calculation
- atlas filtering
- result-verification functions

**Priority:** High

---

## T5. Continuous reproducibility check

Every full run should automatically produce:

- metrics JSON
- hashes
- model configuration
- version information
- result verification table

**Priority:** High

---

# 22. UPGRADE CATEGORY U — NEW KINDS OF SCIENTIFIC WORK DERIVED FROM THE NOTEBOOK

These are not merely improvements to the existing model. They can become separate research questions or future papers/projects.

## U1. SH3 mutation language / functional landscape

Generate complete computational saturation maps for all SH3 domains.

Research question:

> Are there family-wide conserved structural patterns governing mutation tolerance?

---

## U2. Universal SH3 mechanism map

Map every SH3 position into:

- stability-sensitive
- specificity-sensitive
- dual-sensitive
- tolerant

Research question:

> Do SH3 domains share a conserved functional architecture despite sequence divergence?

---

## U3. Mutation-induced interaction rewiring

Predict which peptides are:

- lost
- gained
- weakened
- strengthened

Research question:

> Can cancer mutations change the partner repertoire without destabilizing the domain?

---

## U4. Allosteric communication maps

Build residue-network models connecting distal positions to the peptide interface.

Research question:

> Which apparently non-interface mutations can propagate functional effects to the interaction surface?

---

## U5. Experimental design optimization

Use active learning to choose the next DMS positions/domains.

Instead of measuring every mutation, choose experiments that maximize:

- positional diversity
- uncertainty reduction
- mechanism diversity
- domain diversity

Research question:

> What is the smallest new experiment required to make SH3 binding prediction learnable?

---

## U6. Cross-domain transfer learning

Train on SH3 and evaluate on another interaction-domain family.

Research question:

> Which principles of mutation-induced stability and interaction change transfer between protein domain families?

---

## U7. Cancer-specific interaction network model

Combine predicted mutation effects with a protein–protein interaction network.

Potential pipeline:

`mutation → domain mechanism → affected interaction → pathway → cancer context`

Research question:

> Which signalling pathways could be perturbed by mechanism-specific SH3 mutations?

---

## U8. Mechanism-aware cancer variant prioritization

Create separate evidence axes rather than a single black-box score:

- stability evidence
- specificity evidence
- cancer-selection evidence
- structural evidence
- uncertainty

Research question:

> Can rare cancer variants be prioritized by mechanism rather than recurrence alone?

---

## U9. Generative suppressor-mutation design

Given a destabilizing SH3 mutation, search for candidate compensatory mutations predicted to restore stability.

Research question:

> Can the model propose sequence changes that rescue structural damage?

This should remain a computational design hypothesis until experimentally validated.

---

## U10. Variant-level virtual mutational scanning

For each cancer-relevant SH3 domain:

- perform all 19 substitutions at every position;
- predict stability;
- predict specificity;
- map uncertainty;
- compare with observed cancer mutations.

This produces a virtual DMS resource.

---

# 23. RECOMMENDED EXPERIMENTAL MATRIX

Do not implement everything at once. The strongest scientific comparison would be:

| Experiment | Model | Main question |
|---|---|---|
| E0 | Current ESM-2 + MLP | Baseline |
| E1 | ESM + local CNN/Transformer | Does local context help? |
| E2 | ESM + antisymmetric head | Does physical constraint help? |
| E3 | ESM + structure | Does structure reduce generalization gap? |
| E4 | Sequence + structure multimodal | Do modalities complement each other? |
| E5 | SH3 specificity model | Can binding specificity be learned independently? |
| E6 | WT/MUT PWM comparison | Can rewiring be quantified? |
| E7 | Homology-aware split | Is performance robust to sequence similarity? |
| E8 | Better conformal calibration | Can uncertainty be improved? |
| E9 | Mutation-opportunity null | Are cancer patterns beyond mutational bias? |
| E10 | Mechanism atlas | What mechanisms occur in cancer SH3 variants? |

---

# 24. PRIORITY TIERS

## Tier 1 — Do first

1. Correct the binding terminology in the current poster/report.
2. Keep the current ESM-2 model as the baseline.
3. Add homology-aware splitting.
4. Add stronger external baselines.
5. Add antisymmetric ΔΔG prediction.
6. Build the SH3 specificity/PWM model.
7. Calculate WT-versus-mutant specificity change.
8. Create a two-axis mechanism map.
9. Improve cancer mutation null modeling.
10. Add structural attribution and counterfactual mutation maps.

## Tier 2 — Strong thesis extensions

1. Sequence + structure multimodal model.
2. GNN structural branch.
3. Structure-aware protein language model.
4. Stratified conformal calibration.
5. Allosteric/distal-effect analysis.
6. 3D family-wide SH3 hotspot analysis.
7. In silico saturation mutagenesis.
8. Experimental prioritization framework.

## Tier 3 — Larger research projects

1. Multi-domain binding model.
2. Cross-family transfer (SH3/PDZ/WW/etc.).
3. Epistatic Transformer.
4. Multi-mutation prediction.
5. Cancer mutational-signature model.
6. Active learning for DMS design.
7. SH3 interaction-network integration.
8. Generative suppressor design.

## Tier 4 — Long-term / collaborative work

1. Experimental validation of selected predictions.
2. Multi-domain ddPCA experiments.
3. Large-scale specificity mapping.
4. Protein–peptide co-folding validation.
5. Universal protein-interaction-domain mutation predictor.

---

# 25. RECOMMENDED FINAL RESEARCH ARCHITECTURE

The most coherent upgraded project is:

```text
                         SH3 CANCER MUTATION
                                  |
                    +-------------+-------------+
                    |                           |
              FOLDING AXIS                FUNCTION AXIS
                    |                           |
           ESM / Structure              SH3 specificity model
                    |                           |
               ΔΔGfold                    ΔPWM / rewiring
                    |                           |
                    +-------------+-------------+
                                  |
                          uncertainty model
                                  |
                    +-------------+-------------+
                    |             |             |
                 stability    specificity    possible
                  effect          shift      distal/allosteric
                    |             |             |
                    +-------------+-------------+
                                  |
                           CANCER ATLAS
                                  |
              +-------------------+-------------------+
              |                   |                   |
        mutation context     structural context    tumour context
              |                   |                   |
              +-------------------+-------------------+
                                  |
                           final mechanism map
```

---

# 26. WHAT SHOULD NOT BE DONE FIRST

Avoid implementing all of the following simultaneously:

- ESM3 + SaProt + ProteinMPNN + EGNN + Transformer + LoRA + conformal + MutFormer + complex co-folding.

That creates too many moving parts to identify which component actually improves the model.

The project should be upgraded incrementally with matched splits, controlled ablations, and identical evaluation protocols.

---

# 27. BEST CORE UPGRADE FOR A MASTER'S THESIS

If the goal is to make the current notebook substantially more novel without turning it into an unmanageable multi-year project, the most coherent route is:

### Stage 1

**Baseline ESM-2 folding model**

### Stage 2

**ESM + structure folding model**

### Stage 3

**Independent SH3 specificity model from experimental PWM profiles**

### Stage 4

**WT-vs-mutant rewiring score**

### Stage 5

**Stability + specificity + uncertainty mechanism map**

### Stage 6

**Cancer-context and mutational-opportunity analysis**

This produces a clear scientific narrative:

> sequence-based folding effects → multimodal folding → independent interaction specificity → mechanism-resolved cancer mutation analysis.

---

# 28. PROPOSED ENDPOINTS / OUTPUTS

The final upgraded pipeline should ideally produce:

1. `folding_model.pt`
2. `specificity_model.pt`
3. `cancer_variant_predictions.tsv`
4. `sh3_virtual_dms.tsv`
5. `mechanism_map.tsv`
6. `prediction_intervals.tsv`
7. `domain_level_metrics.tsv`
8. `benchmark_results.tsv`
9. `ablation_results.tsv`
10. `structural_attribution_maps/`
11. `figures/`
12. `data_manifest.json`
13. `run_config.yaml`
14. `verification_report.json`

---

# 29. FINAL RESEARCH QUESTIONS

The upgrade program can be organized around these questions:

### RQ1
Can protein-language-model representations predict SH3 mutation-induced folding changes under strict domain- and homology-aware evaluation?

### RQ2
Does structural information improve mutation-effect prediction beyond sequence-only representations?

### RQ3
Can experimental SH3 specificity profiles be learned from domain sequence and used to predict mutation-induced interaction rewiring?

### RQ4
Can folding and specificity effects be separated into independent mechanistic axes?

### RQ5
Can distal mutations be identified as candidates for allosteric functional effects after accounting for folding stability?

### RQ6
Do cancer-associated SH3 mutations show structural or functional enrichment after controlling for mutational opportunity?

### RQ7
How much experimental positional diversity is required before binding-effect prediction becomes reliable?

### RQ8
Can active-learning strategies identify the most informative new SH3 experiments for reducing this uncertainty?

---

# 30. SOURCE BASIS

This roadmap was derived primarily from the uploaded baseline SH3 report and the uploaded enhancement-strategy document.

Baseline report: **Mechanism-resolved prediction of cancer mutation effects in human SH3 domains**.

Enhancement document: **Comprehensive Enhancement Strategies for Mechanism-Resolved Mutation Effect Predictions in Human Interaction Domains**.

Important baseline limitations that motivate the roadmap include:

- external stability generalization loss;
- the binding positional-coverage limit;
- dependence of both atlas axes on ESM-derived information;
- unmodeled mutational opportunity in the positional cancer test;
- global rather than stratified conformal calibration;
- limited experimental binding data.

These limitations should be treated as hypotheses to address experimentally or computationally, not as assumptions that an upgraded model will automatically solve them.
