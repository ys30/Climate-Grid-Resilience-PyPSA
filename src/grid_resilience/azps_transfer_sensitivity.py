"""Sensitivity of AZPS shortfalls to HYPOTHETICAL interstate transfer capacity.

Uses observed EIA demand, ERA5 weather, and the EIA-860 generator-only projection,
but varies only assumed link limits. Values are NOT physical transfer ratings.
"""
import argparse
from pathlib import Path
import pandas as pd
from .capacity_adapter import load_eia860_capacities
from .western_us import BAS, build_model, fetch_era5, load_eia930

def run_sensitivity(demand, weather, capacities, fractions=(0.0, 0.1, 0.2, 0.4, 0.8)):
    records = []
    for fraction in fractions:
        if not 0 <= fraction <= 1:
            raise ValueError("Intertie fraction must be in [0,1]")
        net = build_model(demand, weather, "observed_weather",
                          intertie_fraction=fraction, capacities=capacities)
        status, termination = net.optimize(solver_name="highs")
        if (status, termination) != ("ok", "optimal"):
            raise RuntimeError(f"Intertie sensitivity failed at {fraction}: {status} {termination}")
        p = net.generators_t.p
        for ba in BAS:
            shortfall = p[f"{ba}_unserved"].clip(lower=0)
            records.append({
                "intertie_fraction_assumed": fraction,
                "ba": ba,
                "modeled_unserved_mwh": float(shortfall.sum()),
                "peak_shortfall_mw": float(shortfall.max()),
                "shortage_hours": int((shortfall > 1e-4).sum()),
            })
    return pd.DataFrame(records)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--eia-csv", required=True)
    p.add_argument("--capacities", required=True)
    p.add_argument("--start", default="2024-07-01")
    p.add_argument("--end", default="2024-07-08")
    p.add_argument("--cache", default="data/cache")
    p.add_argument("--output", default="outputs/azps_transfer_sensitivity.csv")
    a = p.parse_args()
    demand = load_eia930(a.eia_csv, a.start, a.end)
    weather = fetch_era5(a.start, a.end, a.cache)
    capacities = load_eia860_capacities(a.capacities)
    if any(tech in {"storage", "other"} and mw > 0 for (_, tech), mw in capacities.items()):
        raise ValueError("Supply projected generator-only capacity CSV, not full storage inventory")
    results = run_sensitivity(demand, weather, capacities)
    out = Path(a.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(out, index=False)
    print(results.to_string(index=False))

if __name__ == "__main__":
    main()
