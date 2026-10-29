"""Preflight report: quantify modeled versus excluded EIA-860 capacity.

This is an input-coverage audit, not a grid reliability score.
"""
import argparse
import json
from pathlib import Path
import pandas as pd
from .capacity_adapter import load_eia860_capacities

MODELED = frozenset(("thermal", "wind", "solar", "hydro", "nuclear", "geothermal"))
EXCLUDED = frozenset(("storage", "other"))

def audit(path, output):
    capacities = load_eia860_capacities(path)
    rows = []
    for ba in ("CISO", "AZPS", "BPAT"):
        modeled = sum(mw for (b, tech), mw in capacities.items() if b == ba and tech in MODELED)
        excluded = sum(mw for (b, tech), mw in capacities.items() if b == ba and tech in EXCLUDED)
        total = modeled + excluded
        if total <= 0:
            raise ValueError("No positive installed capacity for " + ba)
        rows.append(dict(ba=ba, modeled_nameplate_mw=modeled,
                         excluded_storage_other_nameplate_mw=excluded,
                         total_reported_nameplate_mw=total,
                         modeled_share_of_reported_nameplate=modeled / total))
    df = pd.DataFrame(rows)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    df.to_csv(output / "capacity_coverage.csv", index=False)
    (output / "capacity_coverage_metadata.json").write_text(json.dumps({
        "source_csv": str(path),
        "interpretation": "annual nameplate coverage only",
        "modeled_technologies": sorted(MODELED),
        "excluded_technologies": sorted(EXCLUDED),
        "warning": "storage is not an unlimited-energy generator; no SOC or MWh inferred",
    }, indent=2) + "\n")
    return df

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--capacity-csv", required=True)
    p.add_argument("--output", default="outputs/capacity_coverage")
    a = p.parse_args()
    print(audit(a.capacity_csv, a.output).to_string(index=False))

if __name__ == "__main__":
    main()
