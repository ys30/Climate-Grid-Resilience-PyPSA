# Figure release policy: verified versus illustrative geography

This is a release gate, not a claim that a new 2024 balancing-authority polygon dataset has been discovered.

| Artifact | Publish as | Evidence and caveat |
|---|---|---|
| `figures/four_ba_census_states_map.svg` | Geographic **model schematic** | US Census 2024 state outlines only; representative ERA5 points; hypothetical PyPSA links |
| `figures/azps_boundary_coverage_census_map.svg` | Model-boundary **coverage schematic** | Partner names verified from AZPS EIA-930; unmodeled areas have no invented locations |
| `figures/azps_four_season_census_maps.svg` | Sampled-week **aggregate annotated map** | Four 168-hour windows; no physical routing; no BA polygons |
| `figures/azps_partner_exchange_heatmap.svg` | **Verified observational comparison** | Published CSV `data/verified/seasonal_partner_exchange.csv`; + import to AZPS, - export from AZPS |
| `figures/azps_four_season_shortfall.svg` | **PyPSA simulation result** | Not real observed electricity outages |
| HIFLD 2018 BA candidate polygons | **Historical diagnostic only** | 7/11 originals invalid; CISO repaired method disagreement 12,628 km²; no demonstrated 2024 validity |
| Generated colorful AI partner-area infographic | **Rejected** | Incorrect WALC geography and fabricated individual export arrows/BA polygons |

## Prepublication checks

1. Geography: explicitly cite layer provider and source vintage; ensure state borders are not labeled BA boundaries.
2. Identity: BA code ↔ organization name matched and independently verified; especially WALC/WACM.
3. Direction: per-partner EIA-930 reported interchange, not aggregate net exports, required for partner arrows.
4. Time: four sampled weeks must never be called full seasons; 2018 HIFLD cannot silently represent 2024.
5. Geometry: do not silently substitute Shapely `make_valid` or `buffer(0)` geometry; audit both area and shape changes.
6. Physical interpretation: never label a schematic link as a transmission line or observed electric flow.
7. Reliability interpretation: simulated unserved energy is a scenario output, not actual grid outage evidence.

The release policy is intentionally conservative: prefer accurate statistical graphics over invented cartography.
