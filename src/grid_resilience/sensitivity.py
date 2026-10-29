"""Isolate sensitivity to assumed installed capacity and intertie limits.

Uses the same observed hourly load + ERA5 weather, and varies only
unvalidated reserve-margin and transfer-capacity parameters.
"""
import argparse
from pathlib import Path
import pandas as pd
from .western_us import load_eia930, fetch_era5, build_model

def sensitivity(eia_csv, start, end, output, cache):
    load = load_eia930(eia_csv, start, end)
    weather = fetch_era5(start, end, cache)
    rows = []
    for reserve in (0.18, 0.30, 0.45, 0.60):
        for tie in (0.00, 0.10, 0.20):
            net = build_model(load, weather, "observed_weather",
                              reserve_margin=reserve, intertie_fraction=tie)
            status, termination = net.optimize(solver_name="highs")
            if (status, termination) != ("ok", "optimal"):
                raise RuntimeError(f"Sensitivity solve failed: {reserve}, {tie}")
            power = net.generators_t.p[
                [f"{ba}_unserved" for ba in load.columns]].sum(axis=1).clip(lower=0)
            rows.append({"reserve_margin_assumed": reserve,
                         "intertie_fraction_assumed": tie,
                         "baseline_modeled_eens_mwh": float(power.sum()),
                         "system_shortage_hours": int((power > 1e-4).sum()),
                         "max_shortfall_mw": float(power.max())})
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    data = pd.DataFrame(rows)
    data.to_csv(out, index=False)
    return data

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--eia-csv", required=True)
    p.add_argument("--start", default="2024-07-01")
    p.add_argument("--end", default="2024-07-08")
    p.add_argument("--cache", default="data/cache")
    p.add_argument("--output", default="outputs/western_us/baseline_sensitivity.csv")
    a = p.parse_args()
    print(sensitivity(a.eia_csv, a.start, a.end, a.output, a.cache).to_string(index=False))

if __name__ == "__main__":
    main()
