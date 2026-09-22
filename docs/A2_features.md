# A2 — Features (Stage 2)

**Purpose.** Turn each variant into numbers, and attach structure for later validation.

## Steps
1. **One variant table:** 389,068 MegaScale, 3,688 ddPCA and 6,884 atlas variants, each with the
   **wild-type** sequence of its domain.
   - MegaScale's `aa_seq` is the *mutant* sequence (this was a first-run bug in the original
     project), so the wild type is rebuilt from it.
   - Every row passes a residue check. A dropped row stops the notebook: silent row loss was the
     most dangerous bug type in the original run.
2. **ESM-2 650M, one pass per wild-type domain** (725 domains). This gives the 1,280-number
   representation of each residue, plus masked-marginal log-odds for every amino acid at every
   position (Meier et al. 2021).
   - Variant features become lookups: 5 min instead of hours, 97 MB instead of 2 GB.
   - The log-odds are also saved for the virtual scan in B6.
3. **Scalars:**
   - *Five from ESM:* score, wild-type log-probability, positional entropy, relative position,
     domain length.
   - *Seven for chemistry:* Δhydropathy (Kyte–Doolittle), Δvolume, Δcharge, BLOSUM62, to-proline,
     from-glycine, to-glycine.
   - Total per variant: **1,292 numbers**.
4. **Structure, as annotation only:**
   - The three solved ddPCA complexes, with the PDB→construct offset derived by sliding (GRB2 0,
     PSD95 310, GB1 1).
   - AlphaFold DB models for the atlas proteins, downloaded once and **cached on Drive**
     (v6 → v5 → v4).
   - RSA by Shrake–Rupley. The maximum-accessibility table used to normalise it is widely
     circulated, but its primary source could not be confirmed, so it is left unattributed.
5. **Family frame.** Every atlas domain is aligned to GRB2-SH3, the one domain with both a solved
   complex and measured binding energies. This places each residue on a shared 56-position frame.

## Why structure is not a model feature
MegaScale has no structure on any of its 389,068 rows, while the atlas has it on 96.8 %. A model
using structure would train on one distribution and predict on another. Keeping structure out also
makes B2 an **independent** test.

## How to read the result
- **Zero-shot ESM-2 tracks folding (ρ −0.40) better than binding (ρ −0.26).** That gap is what the
  thesis is about. The negative sign is correct: a low ESM score means a damaging mutation.
- **The cross-fold separation table** (GRB2 + PSD95) replicates A1's pattern across two folds.

## Limitations
- 11 very large proteins have no AlphaFold model, because only fragment F1 is requested.
- AlphaFold models are predictions, not solved structures.
