# HIFLD BA polygon feature-level vintage audit

Successful [feature-level GitHub Actions audit 41082549254](https://github.com/ys30/Climate-Grid-Resilience-PyPSA/actions/runs/41082549254), artifact `ba-polygon-source-inventory`.

## Verified findings

Each of these eleven HIFLD `NAME` candidates matches **one feature**: ARIZONA PUBLIC SERVICE COMPANY (AZPS), CALIFORNIA INDEPENDENT SYSTEM OPERATOR (CISO), BONNEVILLE POWER ADMINISTRATION (BPAT), SALT RIVER PROJECT (SRP), LOS ANGELES DEPARTMENT OF WATER AND POWER (LDWP), PUBLIC SERVICE COMPANY OF NEW MEXICO (PNM), TUCSON ELECTRIC POWER COMPANY (TEPC), PACIFICORP - EAST (PACE), IMPERIAL IRRIGATION DISTRICT (IID), WESTERN AREA POWER ADMINISTRATION - DESERT SOUTHWEST REGION (WALC candidate), and WESTERN AREA POWER ADMINISTRATION - ROCKY MOUNTAIN REGION (WACM candidate).

**Every one of these feature records contains the same provenance metadata**:

| Field | Retrieved value |
|---|---|
| `YEAR` | `2018` |
| `SOURCEDATE` | 2019-06-20 UTC (Unix milliseconds 1560988800000) |
| `VAL_DATE` | 2020-05-15 UTC (Unix milliseconds 1589500800000) |
| `VAL_METHOD` | `OTHER` |
| `SOURCE` | FERC 714, EIA 860, EIA 861, TIGER/Line Shapefiles - U.S. Census |

The listed names are candidate BA-to-polygon correspondences; the Western Area organizational names require independent verification before asserting equivalence to EIA-930 `WALC` and `WACM`. This phase retrieves **metadata**, not geometries: no topology validation, geographical overlap test, feature-year validity for 2024, or actual line routes has been performed.

## Decision

**Do not show these candidate features as verified 2024 BA boundaries.** They may be displayed only as **historical HIFLD reference geography (YEAR=2018; source/validation 2019–2020)** with visible date and source annotation, and still must pass geometry QA. Their polygons must not be combined with 2024 EIA-930 exchange statistics in a way that implies that the boundaries are synchronized to those observations.

For a 2024 map, obtain geometry with proven 2024 vintage (or demonstrate temporal stability), confirm codes and origin, validate geometry, and inspect whether BA areas overlap or leave gaps.

[Previous candidate crosswalk](BA_POLYGON_CROSSWALK_CANDIDATES.md) | [Map accuracy audit](MAP_ACCURACY_AUDIT.md)
