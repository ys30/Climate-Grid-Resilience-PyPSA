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


## Western US observed-load / ERA5 PyPSA experiment (experimental)

New module: src/grid_resilience/western_us.py. The prototype models a **three-BA western-US subset** (California ISO CISO, Arizona Public Service AZPS, Bonneville BPAT), NOT a calibrated WECC-wide network.

- **Measured demand:** [EIA-930 Hourly Electric Grid Monitor](https://www.eia.gov/electricity/gridmonitor/), Download Data > Six-Month Files > Balance. Download the July–December 2024 CSV. EIA hour-ending UTC timestamps are shifted to hour-start; missing BA/hour values are rejected.
- **Historical weather:** [Open-Meteo ERA5 archive](https://open-meteo.com/en/docs/historical-weather-api), hourly air temperature, 100-m wind speed and shortwave radiation at one documented representative point per BA. Downloaded at runtime and cached locally.
- **Model assumptions, NOT real WECC data:** illustrative 3-node interties, capacity sized from observed peak multiplied by 1.18, 70/20/10 thermal/wind/solar generation mix, heat impacts, unit operating costs and transfer limits. Links approximate exchange limits, not validated transmission electrical physics.

### Reproduce

    python -m pip install -e '.[model,dev]'
    # First download official EIA-930 BALANCE 2024 Jul-Dec CSV from the website above.
    python -m grid_resilience.western_us --eia-csv data/external/EIA930_BALANCE_2024_Jul_Dec.csv --start 2024-07-01 --end 2024-07-08 --output outputs/western_us
    python -m pytest -q

The EIA CSV filename above is an example only: use the actual filename the site supplies. Internet access is required to retrieve and cache ERA5. Real EIA-930 records and ERA5 responses are **not bundled**. No claim of a completed real-data optimization is made until the command succeeds.

Three experiments: observed_weather; heat_plus_4c; compound_heat_wind_derating (assumed +4°C, -30% wind, -35% intertie capability). Output is computed only after input validation and successful HiGHS optimization: scenario metrics, hourly hypothetical unserved demand, the aligned source inputs, provenance.json, and solved NetCDF networks. Unserved energy is modeled inadequacy, **not real outages**.

This is intentionally a **screening model**. Upgrade to EIA-860 generator inventory and sourced WECC transmission constraints before making actual reliability claims. Pointwise BA weather is not spatially representative of large territories.

### Relationship to companion LUT-to-PyPSA repository

[The LUT repository](https://github.com/ys30/lut-to-pypsa) extracts five-continent annual energy-service demand for 2020–2050, not BA-level measured hourly load. Do not join those tables directly to this 2024 regional hourly model. A research-quality multi-year coupling requires a justified continent-to-BA allocation, a calibrated hourly load profile and an annual-energy conservation test.
