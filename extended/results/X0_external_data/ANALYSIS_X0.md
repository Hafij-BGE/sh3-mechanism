# X0 — analysis

Run 27 September 2026. Machine numbers in `RESULTS_X0.md` and `metrics_X0.json`.

X0 acquires; it makes no claim. What follows is what the acquisition established and what it cost to
establish it, because three of the four downstream programs depend on decisions taken here.

---

## What came out

| | rows | feeds |
|---|---|---|
| `clinvar_sh3.csv` | 74,116 | E1 |
| `gnomad_sh3_missense.csv` | 431,959 | E1, G1 |
| `domainome_sh3_variants.csv` | 46,128 | E2 |
| `domainome_atlas_matched.csv` | 880 | E2 |
| `atlas_with_external.csv` | **6,884** | everything |

**The row count is the check.** The atlas has 6,884 variants and `atlas_with_external.csv` has 6,884.
A left join that changes the row count has silently duplicated something, and this one did — twice —
before it was made to assert.

## The join defects, which are the real content of X0

Three separate ways the external data expanded the atlas:

- **45 Domainome rows with a null key** — fitness present, position absent. Dropped.
- **3,856 rows collapsed on dual Pfam annotation.** One domain can carry two Pfam entries at the same
  start, so ITSN1 appears as both `PF00018_1003` and `PF07653_1003`. Joining on Pfam id multiplies
  those rows. Collapsed per source.
- **249 ClinVar keys with contradictory submissions.** Resolved by highest star rating, then by
  severity — a decision that E1 inherited and that its pre-registration had to restate.

Without `assert len(out) == n` after every merge, all three would have produced a larger, plausible
atlas and nobody would have looked again.

## Two things that were nearly wrong

**The wrong Zenodo version.** The Domainome record has five. v3 (June 2024) was downloaded first; the
Nature paper is January 2025 and matches **v5**. v5 also renames the files, so a script written
against v3 fails loudly — which is the only reason this was caught rather than producing subtly
different numbers. Cited by the concept DOI so the version is explicit.

**gnomAD's failure path cached failures as success.** Eight concurrent workers hit `HTTP 429`, and an
empty result was written to the cache — indistinguishable from "this gene has no variants". ARHGEF4
and DLG4 were skipped and would never have been retried; ARHGEF4 in fact has 8,140 variants. Fixed by
never caching a failure, honouring `Retry-After`, three workers instead of eight, and purging empty
entries on startup.

That one matters beyond X0: a silent gap in the gnomAD table would have propagated into E1's Q2 and
into G1's null model, in both cases as an under-count that looks like a result.

## What X0 decided that later programs could not revisit

| decision | consequence |
|---|---|
| ClinVar conflicts collapsed by star then severity | E1's group definitions had to match, and its pre-registration says so |
| 235 genes from the UniProt SH3 table | ARHGEF30 has no domain sequence, so E4 lost one measurement |
| gnomAD via the API, not the 200 GB VCFs | popmax was absent at first and E1 was blocked until X0 was re-run |
| `genename` kept as ClinVar spells it (`GeneSymbol`) | E1's first run died on a `KeyError` |

The last two are the pattern worth naming: **an acquisition program's column choices are an interface,
and they were not treated as one.** Both were cheap to fix and both cost a run.

## What is not here, deliberately

`atlas_with_external.csv` is the complete atlas with extra columns, so it stays out of git —
republishing it is republishing the atlas. The large public exports (gnomAD 39 MB, ClinVar 17 MB,
Domainome 9 MB) stay out for size, not licence; X0 regenerates them. Derived analysis tables carrying
no COSMIC identifiers, counts, sites or coordinates are committed.

## Status

Complete and re-run once (27 Sep, 04:46) to add gnomAD `popmax`. The re-run returned **431,959 rows,
identical to the first**, with 431,944 carrying popmax — so the re-fetch lost nothing, which is the
only way to know the fix did not quietly change the dataset.
