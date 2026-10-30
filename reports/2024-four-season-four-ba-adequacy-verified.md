# Verified four-season four-BA PyPSA robustness screening (2024)

## Evidence
- [GitHub Actions run 40994939078](https://github.com/ys30/Climate-Grid-Resilience-PyPSA/actions/runs/40994939078): success; associated CI passed.
- Artifact ID **12950828249** (`four-season-four-ba-screening`); SHA256 `bb9b43e852483a238ac9a50d0881eebeea30569013d8b7574211dadeca628f13`.
- Verified directly from archive `outputs/seasonal_four_ba_summary/seasonal_azps_adequacy.csv` and full four-BA adequacy CSV.
- One sampled 168-hour UTC week per season: winter Jan 15–21, spring Apr 15–21, summer Jul 1–7, autumn Oct 14–20, 2024.

## AZPS modeled unserved energy (MWh)

| Season | Observed weather | +4 °C stylized stress | Compound stress |
|---|---:|---:|---:|
| Winter | 0 | 0 | 0 |
| Spring | 0 | 0 | 0 |
| Summer | 22168.292636 | 45640.989698 | 90343.955485 |
| Autumn | 0 | 0 | 687.252729 |

AZPS modeled shortage hours: summer 34/51/72 for observed/+4°C/compound; autumn compound **4 hours**; all other combinations **0**. CISO, BPAT and SRP modeled shortages were zero across all 12 seasonal weather scenarios (36 BA-scenario rows), per the full output.

## Interpretation

Under fixed 2024 EIA-860 **year-end** generator-only nameplate, identical hypothetical inter-BA link rules and season-specific EIA-930 demand and ERA5 weather, the largest simulated adequacy stress is concentrated in the sampled summer week. This does not establish that summer is the most vulnerable season for the actual grid, nor that winter/spring are outage-free. These are **four individual weeks, not full-season estimates**.

Separately, observed AZPS reported exchange with the seven non-modeled counterparties is net export in 667 of 672 sampled hours, but this model **does not physically represent these obligations**, so adequacy estimates remain materially scope-sensitive. Summer ex-post export obligation stress increased AZPS modeled local shortage from ~22,168 to ~42,611 MWh; this diagnostic carries possible BA accounting double-counting risks.

**Not a calibrated electricity reliability prediction:** no physical transmission constraints, real unit commitment, storage state-of-charge, comprehensive WECC topology, actual forced outage probabilities, or climate-projection attribution. Avoid calling simulated energy not served actual historical outages.

## Remaining steps
1. Check demand/exchange accounting definitions and potential double counting.
2. Publish a consolidated input and simulation limitation table in README.
3. Expand to full-season or monthly windows, and quantify parameter uncertainty before any journal-grade numerical reliability claims.
