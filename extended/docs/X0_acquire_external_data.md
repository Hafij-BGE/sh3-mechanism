# X0 — Acquire the external data

**Why it is needed.** Every program in this phase compares the frozen run against something outside
it. X0 is the one place that fetches those external sources, verifies them, restricts them to the
235 SH3 genes and joins them onto the frozen predictions. Doing it once means E1–E4 start from the
same verified tables rather than each re-downloading and re-filtering.

**What it does not do.** It trains nothing, predicts nothing and draws no conclusion. It reads the
frozen atlas and the B3 predictions and never writes to them. Running it cannot change any number in
A0–D1.

## Inputs
| File | From | Used for |
|---|---|---|
| Domainome v5 Tables 1, 2, 5 | Zenodo 14356805 | measured human abundance, and free EVE/popEVE/Tranception scores |
| `variant_summary.txt.gz` | ClinVar FTP | pathogenic / benign labels and review status |
| gnomAD v4 | the GraphQL API, 235 gene queries | germline allele frequencies |
| `SH3_cancer_master.tsv` | A0 (frozen) | the 235 genes, and protein positions for the join |
| `atlas_predictions.parquet` | B3 (frozen) | `pred_ddG_fold`, `fold_lo`, the destabilising call |

Optional under `PROFILE='full'`: the 4 GB Domainome analysis archive and the GRCh38 assembly.

## Method
1. **Fetch and verify.** Each file is downloaded to the Colab VM, MD5-checked against the
   publisher's published value where one exists, and only then copied to Drive. Writing gigabytes
   straight through the Drive FUSE mount is slow and fails unpredictably.
2. **Filter to the 235 genes** and write one small CSV per source.
3. **Deduplicate every source on its join key** — see below.
4. **Join onto the frozen predictions**, asserting the row count never changes.
5. **Report**: `RESULTS_X0.md`, `metrics_X0.json`, `data_manifest_X0.csv`, `checksums_X0.md5`.

## The five defects this program exists to not repeat
Found after the first run produced 6,993 rows from a 6,884-row atlas.

1. **45 Domainome rows** carry a fitness value but a null position. They cannot join and are dropped.
2. **3,856 rows are duplicated** because one physical domain can hold two Pfam annotations at the
   same start — ITSN1 has both `PF00018_1003` and `PF07653_1003`. `drop_duplicates()` does not catch
   this, because `domain_ID` differs. Collapsed by best `quality_rank`.
3. **249 ClinVar keys carry contradictory submissions** (ABL1 F311L is both *Pathogenic* with no
   assertion criteria and *Uncertain* from a single submitter). Collapsed for the join by highest
   star rating, ties broken by severity. **This is a pre-registered rule, not a merge detail.** The
   full record set with conflicts intact is still exported.
4. **gnomAD** showed no duplicate protein changes when tested, but is aggregated defensively anyway:
   summed AC, max AN, and a visible `gnomad_alleles` count.
5. **`safe_merge()` asserts the row count is unchanged** after every join. A merge that silently
   grows is how all of the above stayed invisible.

## Outputs
| File | Rows |
|---|---|
| `domainome_sh3_variants.csv` | 46,128 across 44 domains |
| `clinvar_sh3.csv` | 74,116 |
| `gnomad_sh3_missense.csv` | 431,959 |
| `domainome_atlas_matched.csv` | 880 — atlas variants with a measurement |
| `atlas_with_external.csv` | 6,884 — **not committed**, it is the complete atlas |

## Runtime
CPU is enough; the GPU does nothing here. High-RAM helps for the 4 GB ClinVar parse. Downloads run
in parallel, gnomAD at three workers (eight triggers HTTP 429). Fully resumable: a file already on
Drive with the right MD5 is not refetched, and the gnomAD cache lives on Drive.

See `DATA_PROVENANCE.md` for how each source was obtained, including the routes that failed.
