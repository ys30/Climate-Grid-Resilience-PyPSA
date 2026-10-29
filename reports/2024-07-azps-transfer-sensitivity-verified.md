# AZPS transfer sensitivity — verified 2024-07-01 to 2024-07-08 UTC

## Verified workflow evidence
- GitHub Actions: https://github.com/ys30/Climate-Grid-Resilience-PyPSA/actions/runs/40937006477
- Conclusion: success; commit `bca47cbcb6fe3dd260e38dde0b309238576e7dce`
- Artifact ID: `12925975860`
- Artifact SHA-256: `e7293264c8d4dfb89ee1089ce145ebc6cbf2270a97273989d8d055e53f279ba5`
- Extracted output: `outputs/azps_transfer_sensitivity.csv`

## Observed model sensitivity

| Assumed intertie fraction | AZPS modeled unserved MWh | Peak simulated deficit MW | AZPS simulated deficit hours |
|---:|---:|---:|---:|
| 0% | 118234.291533 | 2909.573351 | 92 |
| 10% | 60358.549113 | 2108.273351 | 62 |
| 20% | 22039.092636 | 1306.973351 | 34 |
| 40% | 0 | 0 | 0 |
| 80% | 0 | 0 | 0 |

CISO and BPAT simulated unserved MWh are zero across all five link fractions.

**Interpretation:** This is deterministic scenario sensitivity to hypothetical BA-to-BA transfer constraints. The 40% fraction is not a measured thermal rating or an engineering recommendation. No observed outage inference follows. The model uses 2024 year-end EIA-860 generator-only partial nameplate, excludes storage SOC, and makes weather-availability assumptions. Actual geographic connectivity is not validated.

## Follow-up observed-data task

An independent EIA v2 interchange-data workflow has been added to retrieve hourly AZPS pairwise exchanges for this week. Its success and directional sign semantics must be audited separately. Observed interchange (MWh in an hourly period) must never be interpreted directly as physical transfer capacity.
