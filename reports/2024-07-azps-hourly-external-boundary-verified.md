# Verified hourly outside-boundary AZPS audit, 2024-07-01 to 2024-07-08 UTC

## Source

- GitHub Actions successful run: https://github.com/ys30/Climate-Grid-Resilience-PyPSA/actions/runs/40950313035
- ZIP artifact ID: 12929434600
- Artifact digest: sha256:5ef8bf8870f081e693bed05d52564b3449e37266ba7dc8d77193ba8e2bc8d2a0
- Reproducible input: `data/processed/azps_exchange.csv` and independent hourly EIA-930 demand data
- Output: `outputs/azps_outside_boundary/azps_outside_boundary_diagnostic.json` and `azps_outside_boundary_hourly_diagnostic.csv`

## Verified results

| Quantity | Value |
|---|---:|
| Hourly observations | 168 |
| Outside-boundary net importing hours | 0 |
| Outside-boundary net exporting hours | 168 |
| Zero net exchange hours | 0 |
| Outside net imported energy | 0 MWh |
| Outside net exported energy | 159,756 MWh |
| Mean net imports from outside | −950.9285714285714 MW |
| Maximum hourly net imports from outside | 0 MW |
| Maximum hourly net exports to outside | 1713 MW |
| Accounting identity maximum absolute residual | 0 MW |

**Interpretation:** across the seven AZPS reported exchange counterparties missing from the four-BA graph, aggregated hourly net interchange is an **AZPS export in all 168 hours**. This does not mean every individual missing neighbor is an importer, nor that the same power physically traversed one identified line. This is a BA-level directional net accounting result.

**Modeling consequence:** the existing four-BA optimizer does not represent these missing net export obligations; its installed-nameplate generator-only adequacy analysis could overstate supplies available for native AZPS load. The impact cannot be computed by simply subtracting an observed 951 MW constant from historical demand; any subsequent model stress test must use aligned hourly values, separate genuine external demand from modeled cross-border flows, and clearly label the experiment as an ex-post accounting boundary sensitivity rather than a forecast.

## Validation next steps

1. Construct a **diagnostic ex-post load-adjustment scenario** for AZPS based on observed hourly net exports to outside partners, with no claim that this is a physically feasible counterfactual dispatch.
2. Verify the sign and energy accounting of that adjustment and compare *identical* generator capacities, weather, and assumed links.
3. Broaden observation windows and compare seasonal export profiles.
4. Move to explicit BA representation only with matching load/generation data and documented interconnection topology.
