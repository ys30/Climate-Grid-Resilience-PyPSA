# AZPS EIA-930 observed interchange: audited 2024-07-01 to 2024-07-08 UTC

## Evidence

Official EIA pairwise interchange run **40937412695** completed successfully: https://github.com/ys30/Climate-Grid-Resilience-PyPSA/actions/runs/40937412695

Artifact ID `12925761681`; SHA256 `75aefe9e2194b340900643c6d2e9f97cb073203734dd3466c27a8ee50fae9091`.

The downloaded artifact includes 1,512 records: 168 UTC hours for each of 9 AZPS neighboring BAs (CISO, IID, LDWP, PACE, PNM, SRP, TEPC, WACM and WALC). All hours had an observation for each of those nine pairs.

**Sign interpretation:** EIA-930: negative interchange means electricity entering the respondent BA; positive means electricity leaving it. EIA reference: https://www.eia.gov/electricity/930-content/about.html

| Partner BA | Mean AZPS-reported interchange MW | Interpretation |
| --- | ---: | --- |
| SRP | -4536.45 | AZPS imports from SRP |
| WACM | -35.15 | AZPS imports from WACM |
| IID | -13.15 | AZPS imports from IID |
| PACE | +2.32 | AZPS exports to PACE (mean) |
| PNM | +19.29 | AZPS exports to PNM (mean) |
| TEPC | +69.52 | AZPS exports to TEPC (mean) |
| LDWP | +325.43 | AZPS exports to LDWP (mean) |
| WALC | +582.67 | AZPS exports to WALC (mean) |
| CISO | +719.52 | AZPS exports to CISO (mean) |

Total hourly net interchange averaged **-2866.0 MW**, i.e. average AZPS net imports **2866.0 MW**. Hourly net imports ranged **1966 to 4368 MW**. Summed over 168 hours, net imported energy was **481488 MWh** (assuming EIA hourly MW-average reporting). These are observed interchange, NOT physical transfer limits or deliverable reserve capacity.

A new automatically triggered `eia-azps-exchange.yml` step pairs these reported exchange observations with EIA-930 observed demand, computes *implied* generation via `generation = demand - net imports`, and records data provenance. That derived generation is **not independently validated**; the independent EIA-930 net generation series is a future reconciliation target.

## Limitations and significance

EIA-860 nameplate is annual, not available summer capacity. EIA-930 interchange is observed, not optimal or thermal rating. Commercial pseudo-ties and geographic reporting definitions may affect comparisons. A three-BA model omits SRP, the largest observed importer-to-AZPS relationship. Therefore, the simulated AZPS shortfalls from simplified CISO/AZPS/BPAT links are highly sensitive to omitted neighbor topology. Do not interpret simulated shortfalls as real outages.
