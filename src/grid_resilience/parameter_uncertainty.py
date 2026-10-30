"""July four-BA parameter uncertainty screening (not a probabilistic forecast).

Vary two assumed parameters independently while holding historical demand,
weather, EIA-860 year-end partial nameplate, and topology fixed.
"""
import argparse
import json
from pathlib import Path
import pandas as pd
from .four_ba import FOUR_BAS, FOUR_LINKS
from .western_us import build_model, fetch_era5, load_eia930
from .capacity_adapter import load_eia860_capacities

LINK_FRACTIONS=(0.05,0.10,0.20)
THERMAL_MULTIPLIERS=(0.8,1.0,1.2)

def evaluate(demand,weather,capacity):
    rows=[]
    for link in LINK_FRACTIONS:
        for thermal_factor in THERMAL_MULTIPLIERS:
            modified={k:(v*thermal_factor if k[1]=="thermal" else v) for k,v in capacity.items()}
            n=build_model(demand,weather,"observed_weather",capacities=modified,
                          bas=FOUR_BAS,interties=FOUR_LINKS,
                          intertie_fraction=link,local_shedding=True)
            status,termination=n.optimize(solver_name="highs")
            if (status,termination)!=("ok","optimal"):
                raise RuntimeError(f"Non-optimal solve: link={link}, thermal={thermal_factor}")
            for ba in FOUR_BAS:
                s=n.generators_t.p[f"{ba}_unserved"].clip(lower=0)
                rows.append({"link_fraction_of_smaller_peak":link,
                             "thermal_nameplate_multiplier":thermal_factor,
                             "ba":ba,"modeled_unserved_mwh":float(s.sum()),
                             "shortage_hours":int((s>1e-4).sum())})
    return pd.DataFrame(rows)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--demand-csv",required=True)
    p.add_argument("--capacities",required=True)
    p.add_argument("--start",default="2024-07-01")
    p.add_argument("--end",default="2024-07-08")
    p.add_argument("--cache",default="data/cache")
    p.add_argument("--output",default="outputs/parameter_uncertainty")
    a=p.parse_args()
    demand=load_eia930(a.demand_csv,a.start,a.end,bas=FOUR_BAS)
    weather=fetch_era5(a.start,a.end,a.cache,bas=FOUR_BAS)
    caps=load_eia860_capacities(a.capacities,required_bas=tuple(FOUR_BAS))
    if any(t in ("storage","other") and v>0 for (_,t),v in caps.items()):
        raise ValueError("Use explicit generator-only EIA-860 projection")
    result=evaluate(demand,weather,caps)
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    result.to_csv(out/"link_thermal_3x3.csv",index=False)
    (out/"provenance.json").write_text(json.dumps({
        "method":"3x3 deterministic parameter sensitivity, 9 solves",
        "link_fractions":LINK_FRACTIONS,
        "thermal_nameplate_multipliers":THERMAL_MULTIPLIERS,
        "warning":"Thermal installed-nameplate scaling is a stylized capacity sensitivity, NOT observed unit availability. No probability weights, confidence intervals or calibrated physical transfer limits. Outputs are hypothetical dispatch shortages, NOT actual outages."
    },indent=2)+"\n")
    print(result[result.ba=="AZPS"].to_string(index=False))
if __name__=="__main__": main()
