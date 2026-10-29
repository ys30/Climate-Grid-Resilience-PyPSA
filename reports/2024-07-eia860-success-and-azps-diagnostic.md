# Verified EIA-860 partial-nameplate experiment: 2024-07-01 to 2024-07-08 UTC

## Reproducibility
- EIA-860 inventory CI: https://github.com/ys30/Climate-Grid-Resilience-PyPSA/actions/runs/40936240909 — success
- End-to-end EIA-860, hourly demand, ERA5, and PyPSA: https://github.com/ys30/Climate-Grid-Resilience-PyPSA/actions/runs/40936241042 — success
- Commit: `7e4b94c9ccb35920bc9a366dd8fb5470fe9580b9`
- Original artifact `western-us-eia860-partial-nameplate` (ID 12925241732), SHA256 `9710da8d17506e25b208eb5bcf79948cb4f970260f0eb0e97193b4d385696e21`

## Annual installed nameplate and observed maximum hourly demand (MW)

| BA | 2024 EIA-860 inventory | Included in generator-only model | Excluded storage/other | EIA-930 July 1–7 peak |
| --- | ---: | ---: | ---: | ---: |
| CISO | 85634.2 | 73964.1 | 11670.1 | 42598.0 |
| AZPS | 7254.5 | 6646.5 | 608.0 | 8013.0 |
| BPAT | 27571.3 | 27539.3 | 32.0 | 8294.0 |

Observed AZPS maximum load exceeds its annual reported installed nameplate by 758.5 MW, and exceeds the modeled generator-only subset by 1366.5 MW. **These comparisons do not estimate historic shortage, reserve margin, actual net imports, or capacity adequacy.** BA mapping is incomplete: 676 nationwide operating-generator records lacked assignable BA in the audit and were excluded, so area totals are subject to coverage uncertainty.

## Simulated unserved energy (MWh, **not observed customer outages**)

| Weather scenario | Synthetic installed mix | EIA-860 partial-nameplate subset | Delta |
| --- | ---: | ---: | ---: |
| Observed 2024 week | 23934.458586 | 60358.549113 | 36424.090527 |
| Temperature +4°C | 78537.660735 | 95765.617354 | 17227.956619 |
| Compound extreme | 127439.718750 | 132114.583434 | 4674.864684 |

All unserved energy in the partial-nameplate cases is attributed to AZPS in this three-BA linear model; CISO/BPAT are zero. This pattern is **model-dependent**, especially assumed intertie strength and restricted assets. It must not be presented as real-world AZPS outages or as a national/regional power reliability score.

## Next validation
- Five-point AZPS **illustrative** intertie-fraction sensitivity (0, 0.1, 0.2, 0.4, 0.8) is now configured as an automated step, **not yet validated by its own completed run**.
- Priorities: audit observed BA electricity exchanges and actual available supply; integrate storage energy capacity/SOC when supported by source data; determine documented and suitable interregional transfer limits.
- The three sampled balancing areas are **not** the full WECC network.
