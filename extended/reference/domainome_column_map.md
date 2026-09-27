# Column map — `K50_dG_Dataset1_Dataset2_in_aPCA.csv`

The file has **no header row**; the first line is data. Column meanings below were decoded from
`02_validation.Rmd` (chunk `tsuboyama domains`) in `files_to_reproduce_analyses.tar.gz`, then verified
against the data. Columns are referred to by position, as the R code does (`V1` = column 1).

| Column | Meaning | Verified how |
|---|---|---|
| `V1` | name; `pdb_id` is everything before `.pdb` | R: `strsplit(string,".pdb")[[1]][1]` |
| `V2` | DNA sequence | inspection |
| `V27` | full construct sequence, with `SAGGSAGG…` linkers | inspection |
| `V28` | trimmed domain sequence | inspection |
| `V29` | **mutation code**, e.g. `Q5R`; also `wt`, or containing `ins`/`del` | R parses wt_aa/pos/mut_aa from it |
| `V30` | PDB name, used as the grouping key | R: `by="V30"` |
| `V34` | **ΔG** (absolute folding free energy, kcal/mol) | wild-type rows sit at 3.3–4.0 |
| `V35` | **ΔΔG** (kcal/mol) | 226 wt rows mean **+0.003**; 54,136 mutant rows mean **−1.400** |

## ⚠ Sign convention is opposite to ours

In this file **negative ΔΔG = destabilising** (mutant mean −1.400). Our pipeline uses
**positive = destabilising** — the MegaScale proteolysis sign is negated on load. **Negate `V35`
before comparing with anything from B1/B3.** Getting this wrong is the same class of error as the
FoldX residue-numbering bug.

## Joining Rocklin/MegaScale to Domainome

`domains_from_tsuboyama_rocklin_overlaps.txt` has no header either. The R code names the columns:

```
pdb_id  uniprot_ID  dom_ID  aa_seq_aPCA  aa_seq_Rocklin  overlap  offset  percent_overlap
```

The join, as the authors do it:

1. Drop rows where `V29` is `wt` or contains `ins`/`del`.
2. Parse `wt_aa`, `pos`, `mut_aa` from `V29`.
3. `pos_offset = pos + offset` (offset from the overlaps file, per `pdb_id`).
4. Key on `dom_ID` + `wt_aa || pos_offset || mut_aa`, matching the Domainome's own
   `wt_aa || pos || mut_aa`.

## Fraction folded, for comparing energies with abundance

```
fraction_folded = 1 / (1 + exp(-dG / (0.001987 * 303)))
```

R = 0.001987 kcal·mol⁻¹·K⁻¹, T = 303 K. This is the Boltzmann conversion that puts ΔG on the same
footing as an abundance readout, so it is the route from aPCA fitness to something comparable with our
kcal/mol predictions and conformal intervals.

## Their QC filters — adopt or override deliberately

The authors keep only: `percent_overlap > 80`, growth-rate range (5th–95th percentile) `> 0.075`,
and `mean_count > 5`. Domains duplicated in Tsuboyama (different boundaries or backgrounds) are
aggregated by `dom_ID` after correlating by `V30`.

If we reuse these thresholds, say so; if we set our own, pre-register them before looking at the result.
