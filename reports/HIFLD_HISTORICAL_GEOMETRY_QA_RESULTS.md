# HIFLD Historical Control-Area Geometry QA — verified audit

**Audit:** [GitHub Actions 41085221862](https://github.com/ys30/Climate-Grid-Resilience-PyPSA/actions/runs/41085221862) completed successfully. Source: real downloaded `historical_polygon_geometry_qa.json` from `historical-hifld-ba-polygon-qa`.

**Historical boundary YEAR=2018. No geometry is certified as a 2024 BA footprint.** Original geometry validity is a computational test, not legal/electrical boundary validation.

| BA candidate | Original geometry | Make-valid diagnostic area change | Interpretation |
|---|---|---:|---|
| AZPS | Invalid: nested shells | approximately 0.00% | Source geometry invalid; close area agreement does not prove repaired topology |
| CISO | Invalid: ring self-intersection | **-7.08%** | **Material change: do not publish repair as boundary** |
| BPAT | Invalid: nested shells | -1.36% | Requires manual QA |
| SRP | Valid | 0% | Eligible for clearly labeled historical illustrative polygon only |
| LDWP | Invalid: nested shells | -1.81% | Requires manual QA |
| PNM | Invalid: nested shells | approximately 0.00% | Close area agreement does not prove repaired topology |
| TEPC | Valid | 0% | Eligible for clearly labeled historical illustrative polygon only |
| PACE | Valid | 0% | Eligible for clearly labeled historical illustrative polygon only |
| IID | Valid | 0% | Eligible for clearly labeled historical illustrative polygon only |
| WALC | Invalid: nested shells | -1.20% | Plus organizational-to-BA identity validation |
| WACM | Invalid: nested shells | -2.50% | Plus organizational-to-BA identity validation |

**Counts:** 11 feature candidates; 4 originally valid; 7 originally invalid; diagnostic `make_valid` results reported valid for all. Original valid polygon geometries only are exported to the QA artifact GeoJSON; invalid source geometries and diagnostic repairs are deliberately withheld from geographic publication.

**Action required before official-style figure:** A temporally matching authoritative BA polygon source; manual review of CISO's 7.08% change; spatial overlap/coverage diagnostics; reconciliation of Western Area HIFLD organizational names with EIA BA codes. The project shall continue using official Census state outlines for geographic context and the audited 2024 EIA-930 BA partner-direction heatmap for electricity accounting.
