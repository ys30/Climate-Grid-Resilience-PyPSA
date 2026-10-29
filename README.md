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


## Phase 2: EIA-860 actual nameplate capacities (October 2026)

An EIA-860 input adapter is now available, alongside the original synthetic-capacity mode.

Official data: https://www.eia.gov/electricity/data/eia860/ (select **2024** final ZIP, unzip its operating generators and plant inventory spreadsheets). The exporter requires 3_1_Generator2024.xlsx (Operable tab) and 2___Plant2024.xlsx, with the actual downloaded file paths substituted below.

    python -m grid_resilience.eia860 --generators data/external/3_1_Generator2024.xlsx --plants data/external/2___Plant2024.xlsx --year 2024 --output data/processed/eia860

Use the resulting nameplate capacities in the existing EIA-930 + ERA5 scenario solver:

    python -m grid_resilience.western_us --eia-csv data/external/EIA930_BALANCE_2024_Jul_Dec.csv --start 2024-07-01 --end 2024-07-08 --eia860-capacities data/processed/eia860/eia860_ba_technology_capacity.csv --output outputs/western_us_real_capacity

The EIA-860 converter selects operational-status **OP** records only, joins generator and plant records using EIA plant IDs, preserves individual generator IDs, rejects duplicate rows, and exports a source-hash provenance manifest plus BA/technology nameplate totals. It **fails on unmapped fuel source codes** until the mapping has been explicitly reviewed and extended. EIA-860 spreadsheet layouts vary across editions; check actual column names and file headers before running. The converter is not a generator-location power flow model.

**Important:** The solver's installed MW now come from EIA-860 when supplied, but its availability curves, weather derating assumptions, marginal costs, three-node link topology and intertie transfer limits remain illustrative. Hydro, nuclear and geothermal currently enter at constant maximum output; this should be replaced by appropriate operational time series. Storage and fuel technology types not explicitly handled must be modeled separately. EIA-860 is not an hourly forced-outage or plant availability dataset. **No completed empirical optimization or verified CI results are claimed in this commit.**

A subsequent validation should reconcile EIA-860 BA installed MW with EIA-930 reported hourly generation and EIA-930 interchange, and replace the two hypothetical connections with licensed WECC line or interchange constraints.


## Phase 3: Historical inter-BA interchange auditing

The module `src/grid_resilience/interchange.py` processes official [EIA-930 INTERCHANGE](https://www.eia.gov/electricity/930-content/about.html) six-month records for the three pilot balancing authorities, validates duplicate BA/neighbor/hour combinations, compares opposite-direction reports, and writes observed pair summaries and provenance.

    python -m grid_resilience.interchange --interchange-csv data/external/EIA930_INTERCHANGE_2024_Jul_Dec.csv --start 2024-07-01 --end 2024-07-08 --output outputs/interchange_audit

The filename is illustrative; use the actual official download. The parser deliberately rejects unknown EIA field naming rather than making unverified assumptions. The output summary includes maximum and 95th-percentile **observed** absolute interchange, and reciprocal-report discrepancies. **These are NOT rated transmission capacities.** They cannot be plugged directly into PyPSA link `p_nom` as physical constraints. In addition, BA-to-BA reported interchange may include non-physical scheduled transactions and need not correspond one-to-one with transmission corridors.

The previous two schematic links (CISO–AZPS, CISO–BPAT) are still hypothetical. A topology validation step must confirm direct BA connectivity using EIA interconnection reference lists and/or authoritative WECC network geometry, then obtain rated intertie transfer capability from an independently sourced planning/operating dataset.

**Research-quality gate:** Do not describe a real-grid physical-resilience assessment until actual 2024 EIA-860/EIA-930/ERA5 inputs have run end-to-end, generator and transmission capacities are validated, and grid simulation outcomes are compared with held-out operational observations.


## EIA API v2 automated hourly demand (new)

The secret-safe collector in `src/grid_resilience/eia_api.py` retrieves EIA's published hourly `electricity/rto/region-data` **actual demand (type D)** for CISO, AZPS and BPAT, automatically pages beyond the 5,000-row API limit, enforces exact hourly completeness and produces a CSV consumable by the main PyPSA model.

    export EIA_API_KEY='your-key'  # local environment only; do NOT commit!
    python -m grid_resilience.eia_api --start 2024-07-01 --end 2024-07-08 --output data/processed/eia930_api_demand.csv
    python -m grid_resilience.western_us --eia-csv data/processed/eia930_api_demand.csv --start 2024-07-01 --end 2024-07-08 --output outputs/western_us

**Timestamp distinction:** EIA API `period` values indicate UTC hour beginning; raw legacy six-month BALANCE CSV files have been treated as UTC hour ending in the existing alternate importer. The API output is never shifted by one hour. Do not silently mix these conventions. Validate the source-specific semantics before combining datasets.

[Run the manual GitHub Actions EIA data workflow](https://github.com/ys30/Climate-Grid-Resilience-PyPSA/actions/workflows/eia-data.yml) after configuring repository secret `EIA_API_KEY`. This workflow produces validated observed-demand and provenance artifacts, but **does not yet perform an end-to-end PyPSA empirical solve**. No API key is committed to the repository. The API input must be used with explicitly sourced EIA-860 capacities and actual network limits before making real-grid reliability claims.

EIA API documentation: https://www.eia.gov/opendata/documentation.php
