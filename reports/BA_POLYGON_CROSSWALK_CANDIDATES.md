# Candidate BA polygon name-to-code crosswalk (schema-verified, NOT temporally validated)

## Source and evidence

GIS source inventory: successful [Actions 41082148478](https://github.com/ys30/Climate-Grid-Resilience-PyPSA/actions/runs/41082148478), artifact `ba-polygon-source-inventory`, ID 12989328781. Its HIFLD polygon layer has a `NAME` field with institution names, **not** EIA-930 codes. Therefore the audit's `exact_code_matches=[]` is *not* evidence that AZPS, CISO, BPAT, and SRP polygons are absent.

| EIA-930 BA | Observed HIFLD NAME | Crosswalk status |
|---|---|---|
| AZPS | ARIZONA PUBLIC SERVICE COMPANY | Candidate |
| CISO | CALIFORNIA INDEPENDENT SYSTEM OPERATOR | Candidate |
| BPAT | BONNEVILLE POWER ADMINISTRATION | Candidate |
| SRP | SALT RIVER PROJECT | Candidate |
| LDWP | LOS ANGELES DEPARTMENT OF WATER AND POWER | Candidate |
| PNM | PUBLIC SERVICE COMPANY OF NEW MEXICO | Candidate |
| TEPC | TUCSON ELECTRIC POWER COMPANY | Candidate |
| PACE | PACIFICORP - EAST | Candidate |
| IID | IMPERIAL IRRIGATION DISTRICT | Candidate |
| WALC | WESTERN AREA POWER ADMINISTRATION - DESERT SOUTHWEST REGION | **Requires verified BA-code/organization reconciliation** |
| WACM | WESTERN AREA POWER ADMINISTRATION - ROCKY MOUNTAIN REGION | **Requires verified BA-code/organization reconciliation** |

CEC California feature-service names provide supporting contextual matches, including `CALISO`, `LADWP`, `IID`, and `WALC`; these are **not automatically equivalent EIA BA reporting codes** without an explicit mapping review.

## Current limitations and decision

- The HIFLD schema includes `SOURCEDATE`, `VAL_DATE`, `YEAR`, `SOURCE`, `VAL_METHOD`. The inventory only fetched the layer schema and distinct names; it did **not** fetch the feature-level field values, spatial geometry, temporal effective dates or full 2024 coverage.
- No geographic boundary is yet certified to represent the BA boundary of 2024.
- Do not assume overlaps between different BA polygons are invalid without reviewing whether geospatial data represent control areas, utilities, or service territories.
- **No new BA polygon map will be published as verified** until the feature-level source dates, code mapping and geometry diagnostics are checked.
- The older AI-colored infographic depicting WALC as Washington Area and TEPC in Mexico remains rejected (see [accuracy audit](MAP_ACCURACY_AUDIT.md)).

Next step: query the actual feature-level `NAME, SOURCE, SOURCEDATE, VAL_DATE, YEAR` fields for all candidates; check whether the source layer's vintage and method are sufficient to claim a 2024 boundary; only then extract geometries for plotting.
