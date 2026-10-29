# Corrected SRP supply/link mechanism — VERIFIED

## Verification
- SRP 2×2 mechanism: https://github.com/ys30/Climate-Grid-Resilience-PyPSA/actions/runs/40945995665 (**success**)
- Matched 3-BA/4-BA: https://github.com/ys30/Climate-Grid-Resilience-PyPSA/actions/runs/40946005080 (**success**)
- Four-BA reference: https://github.com/ys30/Climate-Grid-Resilience-PyPSA/actions/runs/40946013218 (**success**)
- Fix: local load shedding is isolated behind a one-way BA load connection; synthetic shortfall generation cannot export into adjacent BAs.

## Historical weather — 2×2 controlled experiment

All 4 cases retain SRP's **actual observed demand**, with SRP generator capability and its **hypothetical** AZPS link toggled separately. Both other BAs and the data window remain unchanged.

| SRP generation enabled | AZPS–SRP assumed link enabled | AZPS modeled unserved MWh | SRP modeled unserved MWh |
|:---:|:---:|---:|---:|
| No | No | 60358.549113 | 1003455 (approximately) |
| Yes | No | 60358.549113 | 0 |
| No | Yes | 60358.549113 | 927003 (approximately) |
| Yes | Yes | 22168.292636 | 0 |

**Finding:** AZPS shortfall only improves in the jointly enabled arm. Link-only improvement previously seen was an invalid artifact of allowing virtual unmet-demand generators to export. The approximately 38,190 MWh joint change is a structural simulation result, not a measured improvement in grid reliability or a causal effect of an actually built interconnection.

## Corrected matched three-/four-BA experiment

| Scenario | Three-BA AZPS unserved MWh | Four-BA AZPS unserved MWh | Reduction |
|---|---:|---:|---:|
| Observed | 60358.549113 | 22168.292636 | 63.272324% |
| Heat +4 °C | 95765.617354 | 45640.989698 | 52.340943% |
| Compound | 132114.583434 | 90343.955485 | 31.616970% |

Other shared modeled BAs show zero unserved energy in all compared cases.

## Interpretation and limitations

- This is an **illustrative, deterministic, generator-only** PyPSA dispatch model. Real-time flow feasibility, actual transfer ratings, unit commitment and batteries' state of charge are not calibrated.
- The observed mean AZPS exchange with SRP is **not** a valid proxy for maximum line rating.
- The temporary SRP-fleet-disabled experiments impose artificial energy scarcity at SRP, which is visible in SRP's own loss-of-load statistics. Interpret effects at AZPS separately.
- The non-exportable shortfall implementation is required for physically interpretable regional shortage attribution.
- Do **not** use older 2×2 results implying SRP link alone reduces AZPS unserved energy.
