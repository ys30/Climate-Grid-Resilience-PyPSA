"""Mechanism decomposition: SRP fleet availability vs assumed AZPS-SRP link.

Four-BA topology and SRP demand stay constant. Disabling SRP generation is
a deliberately artificial stress test, not a claim about real SRP operations.
The zero-link arm checks whether SRP assets are reachable from AZPS.
"""
import argparse
import json
from pathlib import Path
import pandas as pd
from .four_ba import FOUR_BAS, FOUR_LINKS
from .western_us import build_model, fetch_era5, load_eia930
from .capacity_adapter import load_eia860_capacities

ARMS=((False,False),(True,False),(False,True),(True,True))

def decompose(demand,weather,capacity,intertie_fraction=0.10):
    records=[]
    for enable_srp_fleet, enable_srp_link in ARMS:
        caps=dict(capacity)
        if not enable_srp_fleet:
            for key in list(caps):
                if key[0]=="SRP":
                    caps[key]=0.
        links=FOUR_LINKS if enable_srp_link else [l for l in FOUR_LINKS if "SRP" not in l]
        n=build_model(demand,weather,"observed_weather",capacities=caps,
                      bas=FOUR_BAS,interties=links,
                      intertie_fraction=intertie_fraction)
        status,termination=n.optimize(solver_name="highs")
        if (status,termination)!=("ok","optimal"):
            raise RuntimeError(f"Decomposition solve failed: fleet={enable_srp_fleet} link={enable_srp_link}")
        for ba in FOUR_BAS:
            shortfall=n.generators_t.p[f"{ba}_unserved"].clip(lower=0)
            records.append({"srp_fleet_enabled":enable_srp_fleet,
                            "azps_srp_link_enabled":enable_srp_link,"ba":ba,
                            "modeled_unserved_mwh":float(shortfall.sum()),
                            "peak_shortfall_mw":float(shortfall.max()),
                            "shortage_hours":int((shortfall>1e-4).sum())})
    result=pd.DataFrame(records)
    azps=result.loc[result.ba=="AZPS"].set_index(["srp_fleet_enabled","azps_srp_link_enabled"])
    # Interaction calculated from the four modeled deficit values, not assumed additive.
    y=lambda a,b:float(azps.loc[(a,b),"modeled_unserved_mwh"])
    interaction=y(True,True)-y(True,False)-y(False,True)+y(False,False)
    return result,interaction

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--demand-csv",required=True)
    p.add_argument("--capacities",required=True)
    p.add_argument("--cache",default="data/cache")
    p.add_argument("--output",default="outputs/srp_mechanism_decomposition")
    p.add_argument("--start",default="2024-07-01")
    p.add_argument("--end",default="2024-07-08")
    a=p.parse_args()
    demand=load_eia930(a.demand_csv,a.start,a.end,bas=FOUR_BAS)
    weather=fetch_era5(a.start,a.end,a.cache,bas=FOUR_BAS)
    caps=load_eia860_capacities(a.capacities,required_bas=tuple(FOUR_BAS))
    if any(tech in ("storage","other") and mw>0 for (_,tech),mw in caps.items()):
        raise ValueError("Only generator-only projected EIA nameplate is supported")
    rows,interaction=decompose(demand,weather,caps)
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    rows.to_csv(out/"srp_factorial_model_results.csv",index=False)
    (out/"srp_mechanism_provenance.json").write_text(json.dumps({
        "AZPS_model_shortfall_interaction_mwh":interaction,
        "factorial_arms":"2x2 toggles SRP generator availability and assumed AZPS-SRP link",
        "design_caveat":"SRP demand remains in every arm. No-link scenarios necessarily isolate SRP and may generate SRP load shedding; interpret AZPS separately.",
        "not":"causal identification of actual SRP imports, empirical outages or physical transfer ratings"
    },indent=2)+"\n")
    print(rows.to_string(index=False))
    print("AZPS interaction MWh:",interaction)

if __name__=="__main__":
    main()
