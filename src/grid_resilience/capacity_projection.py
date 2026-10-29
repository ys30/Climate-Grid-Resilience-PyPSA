"""Explicit EIA-860 nameplate projection for limited generator-only PyPSA scenarios.

Never implicitly treat storage nameplate as unlimited generation. The projection
is NOT a complete regional fleet; excluded capacities are documented.
"""
import argparse
import json
from pathlib import Path
import pandas as pd
from .capacity_adapter import load_eia860_capacities

SUPPORTED = {"thermal", "wind", "solar", "hydro", "nuclear", "geothermal"}
EXCLUDED = {"storage", "other"}

def project(source, output):
    values = load_eia860_capacities(source)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    modeled = []
    omitted = []
    for (ba, tech), mw in sorted(values.items()):
        row = {"ba": ba, "technology": tech, "capacity_mw": mw}
        (modeled if tech in SUPPORTED else omitted).append(row)
    if not modeled:
        raise ValueError("No supported generator nameplate assets")
    included_df = pd.DataFrame(modeled)
    excluded_df = pd.DataFrame(omitted, columns=["ba", "technology", "capacity_mw"])
    for ba in ("CISO", "AZPS", "BPAT"):
        if not (included_df.ba == ba).any():
            raise ValueError("No modeled capacity for " + ba)
    included_df.to_csv(output / "modeled_nameplate_only.csv", index=False)
    excluded_df.to_csv(output / "excluded_nameplate_assets.csv", index=False)
    metadata = {
      "origin": str(source),
      "interpretation": "Partial EIA-860 generator-only NAMEPLATE projection",
      "supported": sorted(SUPPORTED),
      "excluded": sorted(EXCLUDED),
      "excluded_total_mw": float(excluded_df.capacity_mw.sum()),
      "warning": "Exclusion is deliberate and published; model has NO storage charging/discharging/SOC and no validated WECC transfer limits. Year-end EIA-860 capacity is not July firm availability. Results are NOT empirical outage estimates."
    }
    (output / "projection_provenance.json").write_text(json.dumps(metadata, indent=2) + "\n")
    return included_df, excluded_df

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True)
    p.add_argument("--output", default="data/processed/eia860_projection")
    a = p.parse_args()
    included, excluded = project(a.source, a.output)
    print("Modeled nameplate rows:", len(included),
          "excluded rows:", len(excluded),
          "excluded MW:", float(excluded.capacity_mw.sum()))

if __name__ == "__main__":
    main()
