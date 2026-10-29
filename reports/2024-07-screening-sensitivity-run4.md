# Western US screening baseline sensitivity — Run #4

**Workflow:** https://github.com/ys30/Climate-Grid-Resilience-PyPSA/actions/runs/40923575645  
**Artifact:** `western-us-climate-grid-screening`, ID `12918777761`  
**Artifact SHA-256:** `1cd5a12b4a43e08267423c9df45b2215b37f1322dd8d3bbdf5ad787b3ecbe9dd`  
**Model version:** `3099a3cce932e5b9081c97e7f7c873a990d20229`  
**Period:** 2024-07-01 00:00 through 2024-07-08 00:00 UTC (end exclusive).

## Observed-source / assumed-model distinction

EIA RTO API (hourly BA demand) and ERA5 representative-point weather drive the study. Dispatch capacities, technology shares, availability functions, and two hypothetical regional interties are **unvalidated model assumptions**. All numbers below are optimized *modeled* unserved energy, **not actual interruptions, outage probabilities, or verified WECC reliability estimates**.

## Baseline reserve/intertie sensitivity — unserved energy (GWh)

| Assumed reserve margin | Link 0% | Link 10% | Link 20% |
|---|---:|---:|---:|
| 18% | 36.834 | 23.934 | 20.619 |
| 30% | 5.649 | 0.817 | 0.000 |
| 45% | 0.000 | 0.000 | 0.000 |
| 60% | 0.000 | 0.000 | 0.000 |

Source: `outputs/western_us/baseline_sensitivity.csv` from run #4. Percentages are input multipliers in the simplified model, **not measured reserve margins or physical corridor ratings**.

At fixed 10% hypothetical link fraction, increasing reserve margin from 18% to 30% lowered modeled EENS from 23,934.459 to 817.138 MWh (96.59% decrease). At fixed 18% reserve, increasing the link fraction from 10% to 20% reduced EENS to 20,619.371 MWh (13.85% decrease).

### Baseline regional results, 18% reserve / 10% link

| BA | EENS (MWh) | Max BA shortfall (MW) | BA shortage hours |
|---|---:|---:|---:|
| CISO | 18,834.714 | 3,988.213 | 9 |
| AZPS | 4,388.403 | 1,092.271 | 8 |
| BPAT | 711.342 | 711.342 | 1 |

System EENS: **23,934.459 MWh**; peak simultaneous system shortfall: **4,346.381 MW**; system shortage duration: **9 hours**. Sum of BA shortage hours is 18 BA-hours and must not be confused with the 9 distinct system hours.

### Interpretation and next validity gate

This experiment proves that the *screening model* is highly parameter-sensitive, especially to assumed firm availability/capacity. It does **not** establish the relative importance of generation and transmission to the *real* Western Interconnection. Do not tune reserve margin to eliminate baseline deficit and call the tuned network calibrated. Next: insert verified 2024 EIA-860 operating generator inventory, review temporal unit availability and hydro constraints, then validate regional modeled dispatch and exchanges against EIA-930 operational series. Obtain independently sourced network connectivity and transfer ratings before claiming grid-reliability or climate-resilience evidence.
