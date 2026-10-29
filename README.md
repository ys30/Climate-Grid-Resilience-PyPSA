# Climate & Grid Resilience — PyPSA-ready Portfolio

[![CI](https://github.com/ys30/Climate-Grid-Resilience-PyPSA/actions/workflows/ci.yml/badge.svg)](https://github.com/ys30/Climate-Grid-Resilience-PyPSA/actions/workflows/ci.yml)

A reproducible, visualization-first demonstration of electricity adequacy under stylized heatwave and compound climate-stress scenarios. It produces hourly shortfall profiles, unserved energy, peak shortfall, and shortage duration.

> **Evidence boundary:** All demand, supply and stress factors are **synthetic assumptions**. This is not a climate projection, a real-grid resilience assessment, or a solved PyPSA model. PyPSA integration is a planned extension.

## Research questions

1. How might increased demand and derated available supply affect hourly electricity adequacy?
2. How do peak shortfall, total unserved energy and shortage duration differ between stylized scenarios?
3. Which assumptions would need real weather, generator, and network data to support credible resilience claims?

## Reproduce

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
python -m grid_resilience --output outputs
jupyter lab
```

Outputs: `outputs/shortfall_profiles.png`, `outputs/unserved_energy.png`, `outputs/hourly_scenarios.csv`, `outputs/resilience_metrics.csv`. The CI workflow saves generated figures as an artifact.

## Methodology and limitations

A 24-hour synthetic baseline load profile is scaled by a demand multiplier. Available supply is a constant 165 MW scaled by a supply-availability multiplier. Scenario assumptions are Baseline (1.00, 1.00), Heatwave (1.25, 0.90), and Compound stress (1.35, 0.72). Unserved power = max(demand − available supply, 0), in MW. For hourly intervals, summed unserved MW values correspond to MWh of unserved energy. These calculations are **simple adequacy arithmetic**, not optimal dispatch or a physical power-flow simulation. There are no transmission constraints, contingencies, storage, generator ramp rates, probabilities, or climate-attribution statements.

## Next research phase

Add publicly licensed ERA5 weather and documented electricity demand/generation data, map temperature and wind/solar availability to physically meaningful profiles, and solve each case in PyPSA. Compare scenario outcomes with matching assumptions, explicit reliability metrics, sensitivity analysis, and regional maps. Avoid presenting scenario assumptions as measured climate impacts.

## Repository contents

- `src/grid_resilience/analysis.py`: synthetic stress scenarios, metrics, plots
- `notebooks/01_analysis.ipynb`: interactive execution
- `tests/`: regression and figure-generation checks
- `.github/workflows/ci.yml`: automated tests and plot artifacts

## Interpretation

The plots demonstrate a **research workflow**. They are not empirical evidence of grid failures under actual climate extremes.
