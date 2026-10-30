# Climate & Grid Resilience — PyPSA-ready Portfolio

[![CI](https://github.com/ys30/Climate-Grid-Resilience-PyPSA/actions/workflows/ci.yml/badge.svg)](https://github.com/ys30/Climate-Grid-Resilience-PyPSA/actions/workflows/ci.yml)

A reproducible, visualization-first demonstration of electricity adequacy under stylized heatwave and compound climate-stress scenarios. It produces hourly shortfall profiles, unserved energy, peak shortfall, and shortage duration.

> **Current status (October 2026):** The repository now contains both the original synthetic demonstration and **successfully solved** EIA-930 demand + ERA5 weather + partial EIA-860 generator-only PyPSA experiments for a four-BA western-US subset. **The network topology, transfer limits, weather-response coefficients, generator availability and storage omissions remain illustrative.** These outputs are modeled shortfalls, not observed blackouts or validated grid-reliability forecasts. Some older sections below preserve the step-by-step development history.

## Verified research workflow and evidence (latest)

| Component | Verified GitHub Actions run | Key finding and limitations |
|---|---|---|
| Matched three-BA vs four-BA | [40946005080](https://github.com/ys30/Climate-Grid-Resilience-PyPSA/actions/runs/40946005080) | AZPS July baseline screening shortfall changed from ~60,359 to ~22,168 MWh with SRP; hypothetical link |
| SRP fleet × AZPS–SRP link, 2×2 | [40945995665](https://github.com/ys30/Climate-Grid-Resilience-PyPSA/actions/runs/40945995665) | Both SRP fleet and assumed link required for modeled AZPS reduction; artificial shortage cannot flow to neighbors |
| EIA-930 generation/demand/interchange | [40943958855](https://github.com/ys30/Climate-Grid-Resilience-PyPSA/actions/runs/40943958855) | 168 hourly AZPS accounting residuals zero; accounting identity, **not independent physical validation** |
| Model vs observed SRP exchange | [40947395649](https://github.com/ys30/Climate-Grid-Resilience-PyPSA/actions/runs/40947395649) | Model does **not** replicate observed ~4,536 MW mean SRP→AZPS interchange; link limits hypothetical |
| AZPS missing exchange partner audit | [40950313035](https://github.com/ys30/Climate-Grid-Resilience-PyPSA/actions/runs/40950313035) | Seven missing counterparties; outside-boundary AZPS exports in all 168 July hours |
| Four-season EIA-930 boundary audit | [40994479108](https://github.com/ys30/Climate-Grid-Resilience-PyPSA/actions/runs/40994479108) | 667/672 sampled hours net export to missing counterparties; **four sample weeks, not whole seasons** |
| Four-season four-BA screening | [40994939078](https://github.com/ys30/Climate-Grid-Resilience-PyPSA/actions/runs/40994939078) | 12 weather × season scenarios solved; AZPS screening shortfalls peak in sampled summer week |
| Export-obligation sensitivity (with BA scope verification) | [40995861963](https://github.com/ys30/Climate-Grid-Resilience-PyPSA/actions/runs/40995861963) | Ex-post fixed net-export diagnostic; not calibrated dispatch, external unmet demand separately counted |

**Research conclusions must distinguish:** observed EIA-930 BA reporting, official EIA-860 nameplate capacity, ERA5 historical weather, and **hypothetical dispatch/network assumptions**. The model is useful for research methodology, data provenance and structural/parameter sensitivity; it is **not** validated to predict physical interchange or actual outage rates.

### Consolidated technical summary

**[Read the verified technical research summary](reports/FINAL_TECHNICAL_SUMMARY.md)** for study scope, observed-data provenance, quantitative results, major model calibration failures and reproducibility links.

### Verified reports

- [Four-season modeled shortfalls](reports/2024-four-season-four-ba-adequacy-verified.md)
- [Four-season observed boundary exchange](reports/2024-azps-four-season-boundary-verified.md)
- [SRP fleet/link mechanism after virtual-shortfall fix](reports/2024-07-srp-mechanism-corrected-verified.md)
- [Observed/model flow mismatch](reports/2024-07-srp-flow-validation-observed-mismatch.md)
- [External-boundary obligation sensitivity](reports/2024-07-azps-external-export-sensitivity-verified.md)
- [Demand and interchange accounting review](reports/eia930-demand-interchange-accounting-review.md)
- [Four-BA link × thermal-nameplate parameter sensitivity](reports/2024-07-four-ba-parameter-sensitivity-verified.md)

### Remaining work before quantitative reliability claims

Documented physical transfer limits and other neighboring BA representation, operational generator availability and storage energy constraints, longer observation windows, and independent forecast/out-of-sample calibration are **not complete**.



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

## Historical roadmap (original synthetic phase)

The original planned extension was to add publicly licensed ERA5 weather and documented electricity demand/generation data, map temperature and wind/solar availability to physically meaningful profiles, and solve each case in PyPSA. Compare scenario outcomes with matching assumptions, explicit reliability metrics, sensitivity analysis, and regional maps. Avoid presenting scenario assumptions as measured climate impacts.

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

The EIA CSV filename above is an example only: use the actual filename the site supplies. Internet access is required to retrieve and cache ERA5. Real EIA-930 records and ERA5 responses are **not bundled**. **Historical note:** This command was originally proposed before the live GitHub Actions runs above succeeded. Consult the verified workflow table for the completed real-data results.

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

**Important:** The solver's installed MW now come from EIA-860 when supplied, but its availability curves, weather derating assumptions, marginal costs, three-node link topology and intertie transfer limits remain illustrative. Hydro, nuclear and geothermal currently enter at constant maximum output; this should be replaced by appropriate operational time series. Storage and fuel technology types not explicitly handled must be modeled separately. EIA-860 is not an hourly forced-outage or plant availability dataset. **Historical note:** The EIA-860 phase originally preceded completed validation; the current verified four-BA workflows and their limitations are summarized above.

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


## Phase 4 — end-to-end observed-demand / ERA5 screening solve

[Western US solve workflow](https://github.com/ys30/Climate-Grid-Resilience-PyPSA/actions/workflows/western-us-solve.yml) can be started manually using the existing EIA_API_KEY repository secret. The default window is July 1–8, 2024 UTC. It installs PyPSA and HiGHS, runs tests, fetches official EIA v2 hourly demand (CISO, AZPS, BPAT), fetches ERA5 weather via Open-Meteo, solves three climate stress scenarios, summarizes regional and system shortfalls, and uploads datasets, metrics, provenance and NetCDF outputs.

Outputs include hourly_unserved.csv, metrics.csv, system_metrics.csv, modeled_unserved_power.png, modeled_unserved_energy.png, solved_*.nc. The system shortage-hours measure counts hours in which *any* BA has a shortfall, unlike the sum of BA shortage hours.

**Evidence warning:** This is a weather/observed-load-driven **screening experiment**, not WECC-calibrated adequacy modeling. The workflow does not yet download EIA-860 capacity spreadsheets; if no preprocessed EIA-860 capacity file is supplied to the CLI, it runs with explicitly invented capacity shares and intertie limits. +4 °C is an illustrative counterfactual. It does not estimate actual outages or probabilities. GitHub Actions succeeding means a valid executable analysis, not external validation of model assumptions.

The EIA key remains in GitHub Actions secrets and is not printed. Weather and energy raw sources are downloaded as part of a workflow run, with outputs collected as workflow artifacts. Historical event benchmarking against observed interchange and realistic generator availability remains required.


## Phase 5 — diagnose baseline shortfalls

The successful October 29, 2026 screening run (GitHub Actions #40921634189) simulated 23,934.46 MWh of baseline unserved energy over July 1–7, 2024, under hypothetical capacity mix and interties. This is NOT observed outage evidence. The baseline shortfalls cluster into a few UTC late-day hours and may reflect lack of firm supply or dispatch flexibility rather than intrinsic climate-driven inadequacy.

The new diagnostics command is:

    python -m grid_resilience.diagnostics --input outputs/western_us/hourly_unserved.csv --output outputs/western_us/diagnostics

The new sensitivity command independently solves 12 alternative baseline models with assumed reserve margin of 18%, 30%, 45% or 60% and hypothetical intertie fractions of 0%, 10% or 20%:

    python -m grid_resilience.sensitivity --eia-csv data/processed/eia930_api_demand.csv --start 2024-07-01 --end 2024-07-08 --cache data/cache --output outputs/western_us/baseline_sensitivity.csv

Both steps are now included in the manually triggered Western US solve GitHub workflow. Changing assumptions to eliminate modeled shortages is NOT validation or calibration. For research-grade results, compare with EIA-930 measured generation and actual interchanges, connect the EIA-860 inventory, then source or justify physically credible transmission capabilities.


## Phase 6 — official 2024 EIA-860 generator inventory download

[Run the standalone inventory workflow](https://github.com/ys30/Climate-Grid-Resilience-PyPSA/actions/workflows/eia860-inventory.yml). This downloads the official 2024 EIA-860 archive directly from https://www.eia.gov/electricity/data/eia860/archive/xls/eia8602024.zip, extracts the annual operating-generator and plant workbooks, validates source SHA-256, and processes CISO/AZPS/BPAT generator data using the existing strict EIA-860 schema adapter.

    python -m grid_resilience.run_eia860

The workflow uploads the structured capacity inventory, detailed plant-unit mapping, metadata, and capacity audit. If EIA changes workbook headers, status codes, or fuel codes, it intentionally **fails with a diagnostic error rather than silently making up an inventory**. The standalone inventory workflow is independent of the weather/dispatch workflow until real file layout and totals have been validated. The EIA archive is public and requires no API key; the EIA key is still needed for the hourly RTO API.

**Interpretation:** EIA-860 2024 year-end installed nameplate is not the same as available July 2024 operating capacity; additions, retirements, storage energy capacity, dispatchable hydro, forced outages and plant-to-BA reporting all require review. 2024 EIA-860M monthly data can help correct within-year plant commissioning/retirement timing. Do not immediately compare 2024 annual nameplate to one week of EIA-930 load as though it were firm operational capacity.


### EIA-860 run #1 download repair (2026-10-29)

The first inventory Actions run failed at ZIP magic-byte validation, before Excel parsing. The original download URL omitted the `archive/` segment. The 2024 ZIP link on the EIA official index currently points to `https://www.eia.gov/electricity/data/eia860/archive/xls/eia8602024.zip`. The downloader now follows that exact official address and tolerates year-prefixed official workbook filenames. This URL change is committed but the end-to-end official inventory ETL must be rerun before claiming actual capacity totals.


## Phase 7 — observed peak versus nameplate coverage audit

The EIA-860 inventory workflow now optionally runs the official EIA API v2 hourly observed demand fetch (when repository secret EIA_API_KEY exists), then runs `python -m grid_resilience.nameplate_audit` to output `nameplate_vs_observed_load.csv` and `comparison_provenance.json`. These compare nameplate MW with the measured hourly BA peak in July 1–7, 2024, without treating installed nameplate as guaranteed dispatchable capacity. This is an inventory-coverage audit only; it is neither a WECC power-flow validation nor a physical reserve-margin estimate. The unassigned BA audit should be examined before treating generator totals as complete. The CI will execute on relevant source updates; successful real-data outputs are still subject to a completed Actions run.


## Phase 8 — generation fuel coverage and storage separation

The EIA-860 operating-generator parser now recognizes battery storage (`MWH`) and additional residual fuel codes, preserving such nameplate MW in the inventory audit instead of silently relabeling it as dispatchable thermal output. **Storage MW is NOT firm generation**; before simulation it needs EIA storage MWh, round-trip efficiency and state-of-charge constraints represented as PyPSA StorageUnit/Store. The current western_us.py generator adapter includes only thermal/wind/solar/hydro/nuclear/geothermal; any `storage` or `other` inventory capacity is not dispatched, and therefore cannot be interpreted as an exhaustive generation portfolio. Generator input coverage and unassigned-BA records must be audited first. Tests cover EIA fuel MWH classification. CI is configured on push, but only a successful workflow run with official files confirms empirical coverage.


## Phase 11 — auditable EIA-860 capacity projection

The EIA-860 CI now runs `python -m grid_resilience.capacity_projection --source data/processed/eia860/eia860_ba_technology_capacity.csv --output data/processed/eia860_projection`. It produces `modeled_nameplate_only.csv`, `excluded_nameplate_assets.csv`, and `projection_provenance.json`. The projected CSV is structurally compatible with the generator-only capacity adapter; **it is deliberately incomplete** because storage energy/SOC and uncategorized assets are not represented by the current PyPSA model. Excluded capacities and their aggregate MW are disclosed instead of silently dropped. A subsequent solve using this projection would still have assumed availability curves, simplified regional transmission links, and year-end versus summer capacity timing mismatch; it MUST be labeled a partial-nameplate sensitivity, not a calibrated historic outage estimate. The full EIA-860 empirical validation workflow must pass before interpreting any actual capacity totals.


## Phase 12 — end-to-end real *partial nameplate* scenario workflow

The workflow [Western US EIA-860 partial nameplate climate screening](https://github.com/ys30/Climate-Grid-Resilience-PyPSA/actions/workflows/eia860-partial-solve.yml) automatically (on relevant code pushes or manually): runs tests, downloads official EIA-860 2024 workbooks, audits generator coverage and excluded storage, retrieves EIA API hourly demand for 2024-07-01 through 2024-07-07 UTC, retrieves ERA5, runs three PyPSA weather stress cases with the supported annual generator-nameplate subset, then produces reports and a GitHub artifact. **This is an experimental comparison, not a validated historical reliability model.** It uses year-end installed capacities for a summer period, excludes storage and other fuel sources with an explicit record, and retains assumed weather derating, generator availability, and hypothetical BA links. Reported unmet load is a *modeled screening shortfall*, not measured outage or expected unserved energy in the probabilistic reliability sense. The workflow must finish successfully before any capacity totals or results are described as empirically verified.


## Phase 13 — matched model-input comparison

The end-to-end EIA-860 workflow now solves **two matched three-scenario model families** against identical EIA-930 hourly observations and ERA5 weather: (1) hypothetical BA peak-derived capacities and (2) the explicitly incomplete EIA-860 2024 year-end generator-nameplate projection. `model_comparison.py` validates that scenarios and balancing areas match, then writes `model_input_comparison.csv`, `scenario_comparison.csv`, and a limitations manifest. The delta is **simulation sensitivity to capacity input definitions**, NOT measured 2024 outages, a validated grid adequacy estimate or a weather-attributable causal effect. EIA-860's Operable worksheet includes operating, standby and out-of-service units; this pipeline filters operating status explicitly. <https://www.eia.gov/electricity/data/eia860/>
