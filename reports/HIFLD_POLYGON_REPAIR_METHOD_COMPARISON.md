# Historical HIFLD BA geometry repair comparison — independently reproduced

## Evidence

[GitHub Actions 41086699871](https://github.com/ys30/Climate-Grid-Resilience-PyPSA/actions/runs/41086699871) completed successfully; `hifld-ba-geometry-repair-comparison` artifact contains `repair_topology_comparison.json`. The code compared Shapely `make_valid` with `buffer(0)` for eleven historical `YEAR=2018` HIFLD control-area polygon candidates. These are **algorithm-dependent topology transformations**, not measured electrical service-area changes.

| EIA BA candidate | Original geometry | Make-valid area change (%) | `buffer(0)` vs `make_valid` symmetric difference (km²) |
|---|---|---:|---:|
| AZPS | Invalid, nested shells | approximately 0 | consult artifact (small) |
| CISO | Invalid, ring self-intersection | -7.0758 | 12,628.473 |
| BPAT | Invalid, nested shells | -1.3566 | 4,886.448 |
| SRP | Valid | 0 | 0 |
| LDWP | Invalid, nested shells | -1.8100 | 56.350 |
| PNM | Invalid, nested shells | approximately 0 | 0.006 |
| TEPC | Valid | 0 | 0 |
| PACE | Valid | 0 | 0 |
| IID | Valid | 0 | 0 |
| WALC | Invalid, nested shells | -1.1968 | 4,074.130 |
| WACM | Invalid, nested shells | -2.4982 | 10,513.315 |

CISO specifically: original computational area **356,976.823 km²** (invalid topology); `make_valid` **331,717.778 km²**; `buffer(0)` **344,346.251 km²**. Although the repaired geometries pass validity checks, their **12,628.473 km²** symmetric difference shows that selecting a repair algorithm materially changes the displayed territory.

### Interpretation limits

1. An invalid polygon's reported raw area may not be a meaningful authoritative area. Thus percent changes are **diagnostics**, not real territorial loss.
2. `buffer(0)` is an alternative computational interpretation, **not ground truth**.
3. Neither method establishes the historical source's correct coverage, BA identity, or 2024 temporal validity.
4. WALC/WACM organizational name crosswalks remain candidates subject to validation.
5. **Do not overlay these historical repaired polygons as verified 2024 boundaries**, and do not add physical electricity-flow arrows based solely on positive or negative combined exchange.

### Next evidence gate

Locate better-vintaged authoritative polygons (or direct authoritative source shapes for the given year). For material geometry disagreements, compare raw ring structure and polygons against original source documentation; preserve both diagnostics separately and do not automatically replace the raw geometry. The current repository's verified display remains Census state outlines plus separate EIA-930 partner-direction heatmap.
