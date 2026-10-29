# Verified matched three-BA vs four-BA experiment (July 2024)

## Reproducibility

- GitHub Actions run: https://github.com/ys30/Climate-Grid-Resilience-PyPSA/actions/runs/40942716312
- Conclusion: **success**, commit `2f3e1a416300de4f78f7d209ddcf95526724fcfb`
- Artifact `matched-three-vs-four-ba-results`, ID `12927313071`
- Artifact SHA256: `ec403c63a747e6aba6b1bc2948f2adf93f06b286cad2d1d08e2e3b2866ccd71f`
- Primary result: `outputs/three_vs_four_ba/shared_ba_scenario_comparison.csv`

| Weather scenario | Three BA: AZPS modeled unserved MWh | Four BA: AZPS modeled unserved MWh | Reduction |
| --- | ---: | ---: | ---: |
| Observed | 60358.54911333331 | 22168.292635555554 | 63.2723% |
| Heat +4 °C | 95765.6173537859 | 45640.98969803186 | 52.3409% |
| Compound heat, wind derating and link reduction | 132114.58343394828 | 90343.95548492989 | 31.6170% |

The common BA regions CISO and BPAT have **zero** simulated shortages in both configurations for all scenarios.

## Model comparison design

Both solves use identical 2024-07-01 to 2024-07-08 UTC demand period, EIA-860 2024 partial generator-only year-end nameplate source, ERA5 weather procedure, and scenario definitions. The three-BA reference uses **explicitly selected** CISO, AZPS, BPAT capacities from the four-BA source, while the expanded model includes SRP as well.

Critically, the expanded model **adds a hypothetical AZPS–SRP intertie with assumed 10% capacity fraction of smaller peak load**. Its topology and limitations have **not** been calibrated to actual transmission ratings. The result is a *structural sensitivity* experiment, NOT a causal estimate of additional transfer capacity or avoided customer outages. Storage state-of-charge, actual unit commitment, actual line limits, and full WECC representation are absent.

## Next study

1. Add *observed interchange* as an out-of-sample model diagnostic (not as line ratings).
2. Reconcile actual reported net generation with net imports/exports before attributing shortfalls to installed capacity.
3. Test sensitivity to the new SRP link **separately** from adding SRP generation capacity and demand.
