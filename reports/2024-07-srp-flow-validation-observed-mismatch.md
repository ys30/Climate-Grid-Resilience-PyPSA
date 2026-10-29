# Verified AZPS–SRP modeled-versus-observed interchange diagnostic

## Execution provenance

GitHub Actions run [40947395649](https://github.com/ys30/Climate-Grid-Resilience-PyPSA/actions/runs/40947395649) completed successfully; its CI passed. Artifact `srp-observed-modeled-flow-sensitivity`, ID `12929588383`, SHA-256 `5c4ab498bbf2e6859d4a51d3332adb8c0cf428faf74530819b26ee11f00aa9d7`. CSV `outputs/srp_flow_validation/link_assumption_vs_observed_exchange.csv` was inspected.

## Quantitative results: 168 hourly records, observed-weather scenario

EIA-930 mean reported AZPS imports from SRP: **4536.452381 MW**. Positive flow below means SRP→AZPS. Model transfer limit is a hypothetical fraction of the smaller BA peak historical demand, **not an engineered physical rating**.

| Assumed capacity fraction | Assumed AZPS–SRP transfer limit (MW) | Mean modeled SRP→AZPS (MW) | Mean bias (MW) | MAE (MW) | AZPS modeled unserved (MWh) | Shortage hours |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0% | 0 | 0 | −4536.45 | 4536.45 | 118234.29 | 92 |
| 5% | 398.75 | 398.75 | −4137.70 | 4137.70 | 60476.35 | 62 |
| 10% | 797.50 | 797.50 | −3738.95 | 3738.95 | 22168.29 | 34 |
| 20% | 1595.00 | 1595.00 | −2941.45 | 2941.45 | 0 | 0 |
| 40% | 3190.00 | 2772.11 | −1764.34 | 1764.34 | 0 | 0 |

The simulated flow saturates the assumed limit in the 5%, 10%, and 20% runs; these scenarios have no informative hourly variation of simulated flow (correlation undefined). At 40%, model-vs-observed hourly correlation is only **0.14587**. Descriptive flow discrepancy is large even when simulated shortage becomes zero.

## Interpretation

- The four-BA simplified model does **not reproduce the observed regional exchange magnitude and dynamics**. This is a model scope/network limitation, not a failure of EIA data alignment.
- EIA-930 bilateral BA exchange is reported operational interchange and must not be treated as a single interconnector's physical power flow or as an engineered transfer rating; the model's AZPS–SRP link aggregates a complex inter-area network.
- The generator-only representation omits storage, constraints from actual grid topology, unit commitment and nonmodeled neighboring BA transactions; availability coefficients and costs are not calibrated.
- Earlier 63.3% structural scenario reduction is a *hypothetical network sensitivity*, not empirical avoided energy-not-served.
- Do not choose an assumed link limit by matching historical reported exchange maxima: doing so would confuse *dispatch observations* with *transfer capabilities*.

## Next priorities

1. Make observed dispatch/exchange comparison a required, documented **failed-calibration criterion**, not merely a completed workflow indicator.
2. Introduce further neighboring BAs and a defensible external-balance or boundary representation.
3. Replace hypothetical capacity fractions with sourced transfer constraints, if feasible, or label experiments clearly as dimensionless sensitivity.
4. Expand validation beyond one July week and audit time-varying generation/renewable dispatch.
