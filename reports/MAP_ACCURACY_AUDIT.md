# Geographic map accuracy audit — 2026-10-30

## Decision

**Do NOT use the generated colorful infographic with filled, invented BA regions and seven outward arrows as a factual GIS map.** It was an illustrative AI-generated image, **not** derived from a validated GIS dataset; it has material mistakes and must not be used in a research figure.

## Verified against official references

1. **WALC means Western Area Power Administration — Lower Colorado**, not “Washington Area”. [WAPA operations](https://www.wapa.gov/transmission/functions/) and [FERC BA dictionary](https://www.ferc.gov/sites/default/files/2020-06/E-6_4.pdf).
2. **TEPC is Tucson Electric Power Company**; locating its BA territory in Mexico or showing an invented polygon is not supported. [FERC BA dictionary](https://www.ferc.gov/sites/default/files/2020-06/E-6_4.pdf).
3. **AZPS is not the entire state of Arizona**. Census state boundaries are state boundaries, not BA service territories.
4. **Directions per partner not substantiated by an aggregate**: sampled-week outside-boundary exchange net is the sum across seven excluded BA partners. A *positive total net export* does **not** establish exports to each partner. A seven-arrow export map is unsupported, even though the seven reported partner names are correct.
5. **Official state boundaries** from the [US Census 2024 Cartographic Boundary Files](https://www.census.gov/geographies/mapping-files/2024/geo/carto-boundary-file.html) are appropriate for a western US *background*. They are not BA polygons. The four model dots are recorded ERA5 weather-proxy locations, not BA footprints.
6. Three lines (CISO–BPAT, CISO–AZPS, AZPS–SRP) in the original four-BA PyPSA graph are *assumed computational links*, NOT observed physical connections, rated transfer paths or actual plotted transmission lines.
7. The four-sampled-week values **winter 1491.923, spring 971.601, summer 950.929, autumn 748.869 MW** agree (rounding) with the previously verified `seasonal_azps_boundary_summary.csv`, **reported outside seven neighbors combined**, not individual partner flows. The 667/672 net-export hours are also the **aggregate** time series, not seven partner-by-partner export results.

## Audit by map artifact

| Figure | State boundaries | Four BA node coordinates | Real BA polygons | Actual physical routes | Directionality | Release status |
|---|---|---|---|---|---|---|
| `four_ba_topology_schematic.svg` | None, lon-lat guide | Weather-proxy dots | No | No | Assumed bidirectional links | **Valid schematic only** |
| `four_ba_census_states_map.svg` | Real Census 2024 outlines | Weather-proxy dots | No | No | Assumed links only | **Acceptable clearly labeled model location map** |
| `azps_boundary_coverage_census_map.svg` | Real Census 2024 outlines | AZPS/CISO/SRP proxies | No | No | No directions to omitted partners | **Acceptable scope illustration** |
| `azps_four_season_census_maps.svg` | Real Census 2024 outlines | AZPS proxy | No | No | Combined net export annotation only | **Numerically valid but weak thematic cartography** |
| `azps_four_season_shortfall.svg` | Not a map | N/A | N/A | N/A | N/A | **Verified model chart; not spatial geography** |
| AI-generated colorful partner-region infographic | Unverified rendered base | Stylized positions | Invented | Invented | Seven aggregate-to-partner arrows unjustified | **REJECT — incorrect** |

## Corrections and publication rules

- Do not label any AI-painted BA polygon as official, nor show a region called “Washington Area (WALC)”.
- Do not put TEPC in Mexico or color the whole of Arizona as AZPS territory.
- Do not show arrows to each of seven counterparties unless a separate verified `to_ba`-level sign analysis supports each arrow and period; distinguish imports, exports and near-zero exchange in each sampled period.
- Do not relabel combined **net exports** as *gross* individual line flows or capacity.
- Do not show fake scale bars for an invented region map.
- A publication-quality polygon map requires independently sourced, vintage-matched, officially described BA boundary GIS geometry; the California Energy Commission publishes a [California BA areas map](https://gis.data.ca.gov/documents/CAEnergy%3A%3Abalancing-authority-areas/about), but this alone does not establish a complete 2024 western US BA polygon coverage.

**Current recommendation:** Keep the verified Census-state-background illustrations (with disclaimers), use a separate quantitative bar chart for sampled-week outside-net-export statistics, and flag AI-drawn polygons/arrows as rejected pending authoritative boundary and partner-by-partner data.
