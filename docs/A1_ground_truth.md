# A1 — Ground truth: folding and binding energies (Stage 1)

**Purpose.** Load the measured effects every model learns from, and check before any training
that they mean what we think (sign and scale).

## Inputs
- **`Data.zip`** (Faure et al. 2022): MoCHI fits for GRB2-SH3, PSD95-PDZ3 and GB1, with bootstraps,
  in vitro measurements, the solved complexes, and FoldX/EVE/MSA baselines.
- **`Processed_K50_dG_datasets.zip`** (Tsuboyama et al. 2023): cDNA-display proteolysis
  stabilities.
- **`sh3_domains_human.tsv`**, used to find which MegaScale domains are SH3s.

## Steps
1. **ddPCA.** MoCHI decomposes each variant's effect into ΔΔG_fold and ΔΔG_bind. A binding
   coefficient is **reliable** only if |ΔΔG_bind| ≤ 4 kcal/mol and its bootstrap SD ≤ 0.5. For a
   variant too unstable to fold, the binding number is meaningless, and training on it would teach
   the binding model to predict folding.
2. **Sign and scale check.**
   - *Folding:* compared with Φ-value kinetics of GRB2-SH3 (Troilo 2018; ΔΔG = −RT ln(K/K_WT)).
   - *Binding:* compared with double-mutant-cycle ΔΔG of PSD95-PDZ3 (Chi 2008). Chi numbers residues
     on full-length DLG4, so the offset (310) is **derived** by maximising wild-type agreement, not
     assumed.
   - Both correlations must be positive or the notebook stops.
3. **MegaScale.** Single substitutions only. ΔΔG is **negated**, because the dataset uses the
   opposite convention. A domain is SH3 if it is ≥ 50 % identical to a human SH3 domain: 26
   structures of 15 genes.
4. **The premise in measured data.** GRB2-SH3 variants are grouped by burial (RSA < 0.25) and by
   interface (< 5 Å from the peptide in 2VWF). No model is involved.
5. **Baselines.** FoldX, EVE and MSA conservation are extracted for B1.

## Outputs
`ddpca_ground_truth.parquet`, `megascale_singles.parquet`, `megascale_sh3_matches.csv`,
`calibration.csv`, `separation_table.csv`, `baseline_*.csv`, `RESULTS_A1.md`.

## How to read the result
- **The separation table is the empirical premise of the thesis.**
  - Buried, non-interface residues cost about 3.6 kcal/mol of folding energy and almost no binding
    energy.
  - Buried interface residues cost about 2.9 kcal/mol of binding energy.
- **Binding data is the bottleneck:**
  - 2,840 reliable binding energies in 3 domains, of which only GRB2-SH3 (619) is an SH3.
  - Against that, 389,068 folding stabilities in 412 domains.
