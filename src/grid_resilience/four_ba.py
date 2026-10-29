"""Four-balancing-area screening experiment including SRP.

All inter-BA transfer constraints are hypothetical. The generator inventory
is EIA-860 year-end partial nameplate (storage and other assets excluded).
This is not an observed outage reconstruction or a calibrated WECC model.
"""
import argparse
import json
from pathlib import Path
import pandas as pd
from .western_us import BAS, SCENARIOS, build_model, fetch_era5, load_eia930
from .capacity_adapter import load_eia860_capacities

FOUR_BAS = {**BAS, "SRP": (33.42, -111.83)}  # Representative Phoenix-area point only
FOUR_LINKS = [("CISO", "AZPS"), ("CISO", "BPAT"), ("AZPS", "SRP")]

def solve(demand_csv, capacity_csv, start, end, output, cache,
          intertie_fraction=0.10):
    output=Path(output); output.mkdir(parents=True,exist_ok=True)
    demand=load_eia930(demand_csv,start,end,bas=FOUR_BAS)
    weather=fetch_era5(start,end,cache,bas=FOUR_BAS)
    capacities=load_eia860_capacities(capacity_csv,required_bas=tuple(FOUR_BAS))
    unsupported={(ba,tech):mw for (ba,tech),mw in capacities.items()
                 if tech in ("storage","other") and mw>0}
    if unsupported:
        raise ValueError("Four-BA solver requires explicit generator-only capacity projection")
    rows=[]
    for scenario in SCENARIOS:
        n=build_model(demand,weather,scenario,capacities=capacities,
                      intertie_fraction=intertie_fraction,
                      bas=FOUR_BAS,interties=FOUR_LINKS)
        status,termination=n.optimize(solver_name="highs")
        if (status,termination)!=("ok","optimal"):
            raise RuntimeError(f"Four-BA solver failed: {scenario}, {status}, {termination}")
        for ba in FOUR_BAS:
            series=n.generators_t.p[f"{ba}_unserved"].clip(lower=0)
            rows.append({"scenario":scenario,"ba":ba,
                         "unserved_energy_mwh":float(series.sum()),
                         "peak_shortfall_mw":float(series.max()),
                         "shortage_hours":int((series>1e-4).sum())})
        n.export_to_netcdf(output/f"solved_{scenario}.nc")
    results=pd.DataFrame(rows)
    results.to_csv(output/"metrics.csv",index=False)
    (output/"provenance.json").write_text(json.dumps({
        "network":"illustrative four-BA network: CISO, AZPS, BPAT, SRP",
        "links":FOUR_LINKS,"intertie_fraction_assumed":intertie_fraction,
        "capacity_source":"partial EIA-860 2024 year-end nameplate, excluding storage and other",
        "SRP_weather_location":"representative Phoenix-area ERA5 point, not generator-site weather",
        "warning":"Links and their limits are hypothetical, including the AZPS-SRP link. Never infer line ratings from historical EIA-930 flows.",
        "unserved_energy_interpretation":"deterministic model shortfall, not measured outages or probabilistic EENS"
    },indent=2)+"\n")
    return results

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--demand-csv",required=True)
    p.add_argument("--capacities",required=True)
    p.add_argument("--start",default="2024-07-01")
    p.add_argument("--end",default="2024-07-08")
    p.add_argument("--cache",default="data/cache")
    p.add_argument("--output",default="outputs/four_ba")
    p.add_argument("--intertie-fraction",type=float,default=0.10)
    a=p.parse_args()
    if not 0<=a.intertie_fraction<=1:
        p.error("intertie-fraction must be 0..1")
    print(solve(a.demand_csv,a.capacities,a.start,a.end,a.output,a.cache,a.intertie_fraction).to_string(index=False))

if __name__=="__main__":
    main()
