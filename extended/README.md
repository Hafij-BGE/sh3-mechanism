# SH3 extended

Extension of the SH3 cancer-variant study in `../sh3 updated`, whose 2026-09-22 run reproduced
187/187 recorded values and is **frozen**. Nothing here modifies it.

Purpose: close the four objections that stand between that study and a journal submission, using
public data that already exists.

| Read | For |
|---|---|
| [PLAN.md](PLAN.md) | the programs, phases, dependencies, and what each closes |
| [DOWNLOADS.md](DOWNLOADS.md) | every data source: link, size, licence, login, and the disk-space rule |

**Disk, checked 26 September 2026:** 60 GB free on `/` (ext4 — put `input_new/` here), 55 GB on
`/mnt/E6CEDEF1CEDEB8CF`, 19 GB on the `DEU thesis` drive. Do not use `/mnt/1CD47885D47862C6`; it is the
Windows system partition. Phase 1 needs ~10–15 GB, so only dbNSFP (~50 GB) has to be filtered per
chromosome rather than stored whole. See DOWNLOADS.md.

**Start here:** Zenodo **v5** (record 14356805), Supplementary Table 2 (29.3 MB) — does the Human
Domainome contain SH3 domains? Match UniProt accessions against `reference/sh3_genes_uniprot.tsv`.
That one answer decides whether program E2 is in the plan. Supplementary Table 1 has already been
checked and does not answer it.
