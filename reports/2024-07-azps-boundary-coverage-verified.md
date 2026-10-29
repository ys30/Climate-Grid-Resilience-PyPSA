# AZPS EIA-930 boundary-coverage audit — verified (2024-07-01 through 2024-07-07 UTC)

## Provenance
- Successful run: https://github.com/ys30/Climate-Grid-Resilience-PyPSA/actions/runs/40949763446
- Artifact: `azps-observed-eia930-bilateral-exchanges` (12931810294), SHA-256 `c08f260c4c463969b86ad5e905ae8675c0396642deff90e6e21803aea86f3c37`
- 168 consecutive hours, nine AZPS-reported bilateral counterparties.
- Current four-BA model includes AZPS connections to SRP and CISO; seven other AZPS reported exchange counterparties are outside the modeled boundary.

## Observed bilateral accounting
**Positive means net imports TO AZPS.** Values below are mean reported EIA-930 bilateral interchange during 168 hours. Gross exchange aggregates absolute hourly values, NOT physical line capacity or identifiable electrical paths.

| Counterparty | Represented in current four-BA topology | Mean net import to AZPS (MW) | Reported gross exchange (MWh) |
|---|:---:|---:|---:|
| SRP | Yes | +4536.4524 | 762124 |
| CISO | Yes | −719.5238 | 124340 |
| WALC | No | −582.6726 | 97889 |
| LDWP | No | −325.4345 | 54673 |
| PNM | No | −19.2857 | 25200 |
| TEPC | No | −69.5179 | 15501 |
| PACE | No | −2.3214 | 11018 |
| WACM | No | +35.1548 | 10028 |
| IID | No | +13.1488 | 3303 |

Observed gross exchange: **1,104,076 MWh**; omitted counterparties account for **19.709875% of gross exchange**. Reported overall AZPS mean net import: **+2866 MW**; net import from omitted counterparties: **−950.928571 MW**, i.e. the omitted partners collectively account for net AZPS exports. These are BA accounting averages and do not define geographic power paths or rated transfer.

## Modeling consequences
- The four-BA graph omits 7/9 reported counterparties, but omitted flows are **not seven missing import sources**. Five omitted partners have negative mean AZPS net import (net AZPS export); only WACM and IID have positive mean values.
- A model missing observed **exports** may underrepresent demand on modeled generation and misattribute available generation to AZPS load. Merely adding import capacity cannot remedy this.
- The mean reported +4536 MW from SRP cannot be compared directly to a 798 MW illustrative aggregated PyPSA link as if they were identical physical facilities or thermal limits.
- Current scenario outcomes remain **screening sensitivity**, not calibrated adequacy/observed outage estimates.

## Next verification priorities
1. Preserve directional hourly outside-boundary exchanges separately from inside counterparties; audit negative versus positive hourly flows (not only mean sign).
2. Evaluate transparent observed-boundary-accounting counterfactual *diagnostics* for AZPS while explicitly separating external observed exchanges from assumed dispatch/line capacity.
3. For physical model expansion, prioritize consistent BA demand and generation data for WALC and LDWP, and study their connectivity rather than adding fictitious links. Validate all new boundary constraints with external engineering documentation.
4. Extend beyond a 168-hour week before generalizing seasonal reliability.
