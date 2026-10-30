# Geographic visualization provenance and limits

## Data source and reproducibility

- **Official geographic layer:** US Census Bureau, 2024 cartographic boundary state shapefile at 1:500k: https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_state_500k.zip
- **Generation:** `python -m grid_resilience.plot_census_geography --output figures` after installing `geopandas>=1.0 matplotlib pandas pyogrio` in an environment with outbound internet access for the Census ZIP.
- **Verified Actions workflow:** [41075180785](https://github.com/ys30/Climate-Grid-Resilience-PyPSA/actions/runs/41075180785) (success).
- **Inputs held in code:** The four BA *weather-proxy points* are CISO (36.17,-119.75), AZPS (33.45,-112.07), BPAT (45.52,-122.68), SRP (33.42,-111.83). These are not official BA polygons or validated substations.
- **Schematic network:** CISO–AZPS, CISO–BPAT and AZPS–SRP. Straight segments do not represent real transmission lines, their capacities, actual dispatch routes, or legal BA adjacency.
- **Reported exchange counterparts omitted by four-BA model:** WALC, LDWP, PNM, TEPC, PACE, WACM, IID. For these areas, no nonverified centroid is plotted.
- **Seasonal external net export annotation:** winter ~1,492 MW, spring ~972 MW, summer ~951 MW, autumn ~749 MW mean. These represent four separately sampled 168-hour weeks, not entire seasons. Their geographic routing is unspecified, so a line thickness / directional physical-flow map would be misleading.

## Permanent outputs

| SVG | Meaning | Evidence limitations |
|---|---|---|
| [four_ba_census_states_map.svg](../figures/four_ba_census_states_map.svg) | US western state background and four-BA *model graph* | Not official BA boundary map |
| [azps_boundary_coverage_census_map.svg](../figures/azps_boundary_coverage_census_map.svg) | Model inclusion compared to observed reported BA partner set | Seven omitted BA positions intentionally not invented |
| [azps_four_season_census_maps.svg](../figures/azps_four_season_census_maps.svg) | Four-week sample outside net exchange comparison | No flow assignment to physical paths |
| [azps_hourly_shortfall.svg](../figures/azps_hourly_shortfall.svg) | Solved PyPSA hourly simulated native shortage | Not historical outages |

All SVGs are versioned in the Git repository. Their existence is independently checked by the associated publishing and CI workflows.

## Next scientifically stronger geographic phase

Acquire official BA geometry *with an authoritative polygon source and clearly established vintage*, then validate join keys and nonoverlap/coverage; do not assume BA territory polygons correspond to Census state borders. For true network-flow mapping, separately acquire licensed line topology and electrical transfer ratings. A physical geography calibration phase is **not** required for portfolio visualization completeness but **is** required before making spatial physical-grid claims.
