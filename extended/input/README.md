# input — all data the extended study reads

One folder, three origins. Nothing here is committed to git; verify with
`md5sum -c reference/checksums_ext.md5` from the project root (47 entries, 8 checked against the
publishers' own checksums).

```
input/
├── external/   4.3 GB  new data downloaded for this study
│   ├── domainome/    Human Domainome 1.0, Zenodo v5 (CC BY 4.0)
│   │   ├── Supplementary_Table_{1,2,3,5}          tables + extracted members
│   │   ├── analysis_files/   aPCA↔kcal/mol conversion, MegaScale↔UniProt map,
│   │   │                     Tsuboyama overlaps, their gnomAD + structural tables
│   │   └── notebooks/        the R Markdown that defines those headerless columns
│   ├── stability/
│   │   ├── mgnify/           MGnify Stability ΔG (2.1 GB) + the two training-split files
│   │   └── benchmarks/       ThermoMPNN/ProteinDPO predictions, S1724 ThermoMutDB
│   ├── clinical/             ClinVar variant_summary.txt.gz
│   ├── signatures/           COSMIC v3.6 SBS96 GRCh38
│   ├── genome/               (empty) GRCh38 primary assembly, for G1
│   └── binding/              (empty) Kazemein Jasemi 2024 affinity tables
│
└── frozen/     19 MB   read-only copies of what the 2026-09-22 run produces and
                        the extended programs consume. chmod a-w on purpose.
    ├── results/   SH3_cancer_master.tsv (the atlas), atlas_predictions.parquet (B3),
    │              folding_per_domain_ci.csv (B1's 15 held-out domains),
    │              atlas_fold_predictions.parquet, heldout_predictions.parquet,
    │              models.pt (the trained head), experimental_candidates.csv (F1)
    └── reference/ expected_values.json (187 recorded values), checksums.md5,
                   data_manifest.json
```

## The third origin: the 12 original raw inputs

COSMIC, UniProt, MegaScale, ddPCA/MoCHI, ProteinGym and the PWM data — **7.5 GB, not copied here.**
They already sit on Drive at `MyDrive/sh3_repro/input/{cosmic,uniprot,datasets}` and locally on the
`DEU thesis` drive. Duplicating them would waste 7.5 GB twice over.

They are needed only by:

- **G3** — re-running A2 for the AlphaFold fragment fix
- **H1** — the PDZ family arm, which rebuilds an atlas from raw COSMIC

Phase 1 (E1–E4) touches none of them: it reads `input/frozen/` and `input/external/` only.

## Why `frozen/` is write-protected

The 2026-09-22 run reproduced 187/187 recorded values. That is the project's strongest asset and the
extended study must not be able to alter it, even accidentally. These are copies; the originals live
in `../sh3 updated/results/` and on Drive at `MyDrive/sh3_repro/`.

If you need to update a frozen copy after a deliberate re-run: `chmod u+w`, replace, `chmod a-w`, and
regenerate `reference/checksums_ext.md5`.

## Two traps in `external/`

**Sign convention.** In `domainome/analysis_files/K50_dG_Dataset1_Dataset2_in_aPCA.csv`, negative
ΔΔG means destabilising — the opposite of our convention. Negate before comparing with anything from
B1 or B3. See `reference/domainome_column_map.md`.

**Headerless files.** Four files in `analysis_files/` have no header row. Column meanings come from
the R notebooks in `domainome/notebooks/`, not from guessing.
