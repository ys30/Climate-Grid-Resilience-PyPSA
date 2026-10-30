# Verified 3 × 3 link-capacity / thermal-nameplate sensitivity (July 2024)

## Reproducibility

- Successful workflow: https://github.com/ys30/Climate-Grid-Resilience-PyPSA/actions/runs/41002228759
- Same-run CI: successful
- Artifact: `four-ba-parameter-uncertainty` (12954037098)
- SHA-256: `e5e009f697bdcdbbd5d680dfa440818420172171bfc745c6bd8c6559dc3b57df`
- Read directly: `link_thermal_3x3.csv`, 36 rows (9 parameter settings × 4 BAs), `provenance.json`.
- Conditions: 2024-07-01 to 2024-07-08 UTC, EIA-930 observed BA demand, ERA5 historical weather, partial 2024 EIA-860 year-end generator-only nameplate; hypothetical inter-BA links.

## Modeled AZPS unserved energy, MWh

| Link limit assumed as fraction of smaller BA peak demand | Thermal nameplate ×0.8 | ×1.0 | ×1.2 |
|---|---:|---:|---:|
| 0.05 | 130830.874 | 60476.349 | 19665.627 |
| 0.10 | 70468.756 | **22168.293** | 1826.037 |
| 0.20 | 8731.155 | 0 | 0 |

Shortage hours for the same three rows: (101,62,34), (63,34,10), (18,0,0).

The response is strongly dependent on both assumed parameters. At baseline 10% links, lowering all thermal nameplate by 20% increases AZPS modeled shortfall by 48,300.463 MWh (~3.18× baseline); raising by 20% sharply lowers the shortfall. At low thermal capacity, CISO has nonzero modeled shortfall (2868.715 MWh at 5% link, 1143.160 MWh at 10% link). BPAT and SRP have zero modeled shortage in this 3×3 experiment.

## Research interpretation

**Neither 0.8–1.2 nameplate multipliers nor 5%–20% link fractions are probability distributions, calibrated seasonal availability, independent outage probabilities or actual transmission line ratings.** No confidence interval or statistical reliability estimate is implied. These outputs demonstrate structural and parameter sensitivity only, not empirical outages or physical adequacy forecasting.

Limitations remain: omitted seven AZPS counterparties (persistent observed net exports in sampled weeks), absent storage dispatch and state-of-charge, actual unit availability, generator-site weather spatial detail, physical grid transfer limits and cross-season/out-of-sample model calibration.
