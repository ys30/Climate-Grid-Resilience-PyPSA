# AZPS ex-post boundary-export stress test — verified

## Execution record

- Successful [GitHub Actions run 40964011759](https://github.com/ys30/Climate-Grid-Resilience-PyPSA/actions/runs/40964011759)
- CI: success
- Artifact: `azps-ex-post-external-export-sensitivity` (ID 12937930391)
- Artifact SHA-256: `d7105ecadf4584f31fae565aacc69bac24cc4e77f15126780a52d8db5d3df0ef`
- Read and checked `azps_external_export_sensitivity/external_obligation_scenarios.csv` inside ZIP.
- 168 hours: 2024-07-01 to 2024-07-08 UTC (exclusive)

## Modeled AZPS outputs

| Scenario | Baseline native unserved (MWh) | Native unserved with ex-post exports (MWh) | Native increase (MWh) | Separate unmet external export (MWh) | Native shortage hours (base → export) |
|---|---:|---:|---:|---:|---|
| observed_weather | 22168.292636 | 42610.743053 | 20442.450418 | 26059 | 34 → 69 |
| heat_plus_4c | 45640.989698 | 66196.489192 | 20555.499493 | 42904 | 51 → 84 |
| compound_heat_wind_derating | 90343.955485 | 114709.397706 | 24365.442221 | 64867 | 72 → 116 |

The imposed **159,756 MWh** is the total observed *net exports to missing AZPS exchange counterparties*, separately evaluated as a fixed ex-post network-boundary obligation. The external obligation is represented by a one-way physical-supply link feeding an independent demand bus. Unmet external exports are a separate artificial generator on this bus and are **not** added to the native AZPS shortage metric.

## What is and is not identified

- Holding EIA-860 generator-only nameplate, ERA5 weather, BA demand, illustrative link assumptions and scenario definitions fixed, this controlled stress shows sensitivity to an omitted external-boundary demand obligation.
- **Caution:** BA demand and interchange may already share accounting conventions; applying ex-post exports as an added demand can produce double counting. No independent operational load allocation or physical power-flow validation establishes that a separately imposed export obligation is the correct representation.
- These are **counterfactual screening results**, not observed outages, calibrated adequacy or empirical expected energy not served.
- Unserved external obligations do not automatically correspond to real contract violations or customer blackouts.
- A future expanded network must model additional BAs and direction/time-varying transfers consistently rather than overlaying historical flow as physical line capacity.

## Next priorities

1. Check EIA-930 demand accounting definitions and prevent the same exports from being counted twice in boundary-flow and regional load representation.
2. Expand the 168-hour evaluation to multiple seasons to see if the boundary flow signs and capacity sensitivities persist.
3. Strengthen constraints with documented transfer-capacity data; treat the current 10%-of-peak BA intertie as hypothetical.
4. Quantify uncertainty in generator availability and climate stress response, plus archive reproducible input checksums.
