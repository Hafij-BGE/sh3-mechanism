# SH3 extended — phase 2

Extension of the run in `../` (A0–D1, F1, F2; 187/187 recorded values reproduced, 2026-09-22).
That run is **frozen**: this phase reads it and never writes back.

Purpose: close the four objections between that work and a journal submission, using public data
that already exists.

## Status

| | |
|---|---|
| **X0** acquire external data | ✅ done |
| **E2** validation against measured human abundance | ✅ done — 880 atlas cancer variants measured; \|ρ\| 0.600 against a noise ceiling of 0.709 |
| **E1** ClinVar + gnomAD | ▶ next — data ready, no GPU |
| **E3** SaProtΔG / ESM3ΔG / ThermoMPNN | leakage audit done and clean |
| **E4** independent specificity test | 45 Kd measurements in hand |
| G1–G4, H1–H2 | planned |

## Documentation

| | |
|---|---|
| **[docs/PLAN.md](docs/PLAN.md)** | **the plan** — programs, order, what is done. If anything conflicts with it, it wins. |
| [docs/DATA.md](docs/DATA.md) | what the data is, where each copy lives, the two traps in it |
| [docs/DATA_PROVENANCE.md](docs/DATA_PROVENANCE.md) | **how each dataset was obtained**, including the routes that failed |
| [docs/SYNC.md](docs/SYNC.md) | local vs Drive; what still needs uploading |
| [docs/preregistration/](docs/preregistration/) | **rules fixed before the result exists** — E1 and E3 drafted, both with open decisions |

One document per program, same convention as `../docs/`:

[X0](docs/X0_acquire_external_data.md) · [E1](docs/E1_clinvar_gnomad.md) ·
[E2](docs/E2_domainome_external.md) · [E3](docs/E3_sota_benchmark.md) ·
[E4](docs/E4_specificity_independent.md)

Technical references: [domainome_column_map.md](reference/domainome_column_map.md) decodes the
headerless files and the inverted ΔΔG sign.

## Check the data

```bash
md5sum -c reference/checksums_ext.md5      # expect 39 OK
```

`input/` (5.1 GB) is not committed. `docs/DATA_PROVENANCE.md` says how to rebuild it.
