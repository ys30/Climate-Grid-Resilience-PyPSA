"""Compare official EIA-860 nameplate capacity with EIA API observed load.

This is a data-coverage and scale diagnostic, NOT an adequacy calibration.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import pandas as pd
from .western_us import BAS, load_eia930

def compare(capacity_csv, demand_csv, start, end, output):
    caps = pd.read_csv(capacity_csv)
    expected = {"ba", "technology", "capacity_mw"}
    if not expected.issubset(caps):
        raise ValueError(f"Missing capacity columns: {expected - set(caps)}")
    if caps.duplicated(["ba", "technology"]).any():
        raise ValueError("Duplicate capacity technology records")
    caps["capacity_mw"] = pd.to_numeric(caps.capacity_mw, errors="raise")
    if caps.capacity_mw.isna().any() or (caps.capacity_mw < 0).any():
        raise ValueError("Invalid nameplate MW")
    loads = load_eia930(demand_csv, start, end)
    counts = caps.groupby("ba").capacity_mw.sum()
    missing = set(BAS) - set(counts.index)
    if missing:
        raise ValueError(f"Missing EIA-860 BA inventories: {sorted(missing)}")
    records = []
    for ba in BAS:
        peak = float(loads[ba].max())
        installed = float(counts[ba])
        records.append({"ba": ba, "nameplate_mw": installed,
                        "observed_peak_load_mw": peak,
                        "nameplate_to_peak_load_ratio": installed / peak,
                        "observed_load_mwh": float(loads[ba].sum()),
                        "hours": len(loads)})
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(records)
    df.to_csv(out / "nameplate_vs_observed_load.csv", index=False)
    (out / "comparison_provenance.json").write_text(json.dumps({
        "eia860_capacity_input": str(capacity_csv),
        "eia930_demand_input": str(demand_csv),
        "start_utc": start, "end_exclusive_utc": end,
        "interpretation": "Nameplate-to-load scale audit ONLY, not a reserve margin or firm capacity measure",
        "warnings": ["2024 year-end plant inventory vs July 2024 demand",
                     "No forced outages, maintenance, storage duration or seasonal hydro constraints",
                     "BA capacity mapping may be incomplete, review unassigned BA audit",
                     "No physically validated regional transfer limits"]
    }, indent=2) + "\n")
    return df

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--capacity-csv", required=True)
    p.add_argument("--demand-csv", required=True)
    p.add_argument("--start", default="2024-07-01")
    p.add_argument("--end", default="2024-07-08")
    p.add_argument("--output", default="outputs/nameplate_audit")
    a = p.parse_args()
    print(compare(a.capacity_csv, a.demand_csv, a.start, a.end, a.output).to_string(index=False))

if __name__ == "__main__":
    main()
