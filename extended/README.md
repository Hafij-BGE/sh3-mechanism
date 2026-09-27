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
| **E1** ClinVar + gnomAD | ▶ next — data ready, no GPU needed |
| E3, E4, G1–G4, H1–H2 | planned |

## Read

| | |
|---|---|
| **[docs/PLAN.md](docs/PLAN.md)** | **the plan** — programs, order, what is done. If anything conflicts with it, it wins. |
| [docs/DATA.md](docs/DATA.md) | what the data is, where each copy lives, and the two traps in it |
| [docs/SYNC.md](docs/SYNC.md) | keeping local and Drive in step; what still needs uploading |
| [reference/domainome_column_map.md](reference/domainome_column_map.md) | decodes the headerless Domainome files and the inverted ΔΔG sign |
| [results/E2_domainome_external/ANALYSIS_E2_noise_ceiling.md](results/E2_domainome_external/ANALYSIS_E2_noise_ceiling.md) | why 0.600 is near the achievable limit |

## Check the data

```bash
md5sum -c reference/checksums_ext.md5      # expect 39 OK
```

`input/` (5.1 GB) is not committed. `docs/DATA.md` says how to obtain it.
