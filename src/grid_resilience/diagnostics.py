"""Diagnose observed-weather baseline shortfalls and their timing.

All quantities are MODEL OUTPUTS, not observed outages or grid reliability
ratings. Input: successful PyPSA screening workflow's hourly_unserved.csv.
"""
import argparse
from pathlib import Path
import pandas as pd

def diagnose(path, output):
    x = pd.read_csv(path)
    required = {"scenario", "ba", "timestamp", "unserved_mw"}
    if not required.issubset(x):
        raise ValueError(f"Missing fields: {sorted(required - set(x))}")
    x = x[x.scenario == "observed_weather"].copy()
    if x.empty:
        raise ValueError("No observed_weather baseline rows")
    x["timestamp"] = pd.to_datetime(x.timestamp, utc=True, errors="raise")
    x["unserved_mw"] = pd.to_numeric(x.unserved_mw, errors="raise")
    if x.duplicated(["ba", "timestamp"]).any() or x.unserved_mw.isna().any():
        raise ValueError("Duplicate or missing baseline BA-hour results")
    if (x.unserved_mw < -1e-4).any():
        raise ValueError("Unexpected negative modeled shortfall")
    x["unserved_mw"] = x.unserved_mw.clip(lower=0)
    x["utc_hour"] = x.timestamp.dt.hour
    # Diagnostic in UTC to avoid pretending that the three BAs share a timezone.
    peak_hours = (x.groupby("timestamp", as_index=False).unserved_mw.sum()
                   .query("unserved_mw > 0.0001").sort_values("unserved_mw", ascending=False))
    region = (x.groupby("ba", as_index=False).agg(
        modeled_unserved_energy_mwh=("unserved_mw", "sum"),
        max_shortfall_mw=("unserved_mw", "max"),
        hours_with_shortfall=("unserved_mw", lambda s: int((s > 0.0001).sum()))))
    hour = x.groupby(["ba", "utc_hour"], as_index=False).unserved_mw.sum()
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    peak_hours.to_csv(output / "baseline_system_shortfall_hours.csv", index=False)
    region.to_csv(output / "baseline_regional_shortfall.csv", index=False)
    hour.to_csv(output / "baseline_utc_hour_pattern.csv", index=False)
    if abs(peak_hours.unserved_mw.sum() - region.modeled_unserved_energy_mwh.sum()) > 1e-3:
        raise ValueError("Mismatch in independently aggregated baseline shortfall")
    return region, peak_hours

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default="outputs/western_us/hourly_unserved.csv")
    p.add_argument("--output", default="outputs/western_us/diagnostics")
    a = p.parse_args()
    regions, hours = diagnose(a.input, a.output)
    print("Baseline modeled shortfall by BA:\n", regions.to_string(index=False))
    print("Top system hours (UTC):\n", hours.head(15).to_string(index=False))

if __name__ == "__main__":
    main()
