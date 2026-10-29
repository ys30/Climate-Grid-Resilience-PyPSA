"""Compare observed AZPS<-SRP exchange to model link dispatch; no rating inference."""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from .four_ba import FOUR_BAS, FOUR_LINKS
from .western_us import build_model, fetch_era5, load_eia930
from .capacity_adapter import load_eia860_capacities

FRACTIONS=(0.0,0.05,0.10,0.20,0.40)

def compare(demand,weather,caps,observed,fractions=FRACTIONS):
    if not set(["timestamp","azps_imports_from_srp_mw"]).issubset(observed):
        raise ValueError("Expected observed SRP->AZPS exchange table")
    o=observed.copy()
    o["timestamp"]=pd.to_datetime(o.timestamp,utc=True,errors="coerce")
    if o.timestamp.isna().any() or o.timestamp.duplicated().any():
        raise ValueError("Invalid or duplicate observed timestamps")
    obs=o.set_index("timestamp").azps_imports_from_srp_mw.reindex(demand.index)
    if obs.isna().any() or not np.isfinite(obs.to_numpy(dtype=float)).all():
        raise ValueError("Observed exchange must cover every modeled hour")
    if len(set(fractions))!=len(fractions) or any(not 0<=v<=1 for v in fractions):
        raise ValueError("Distinct assumed fractions must lie in [0,1]")
    rows=[];hourly=[]
    for fraction in fractions:
        n=build_model(demand,weather,"observed_weather",capacities=caps,
                      intertie_fraction=fraction,bas=FOUR_BAS,
                      interties=FOUR_LINKS,local_shedding=True)
        status,termination=n.optimize(solver_name="highs")
        if (status,termination)!=("ok","optimal"):
            raise RuntimeError(f"Optimization did not converge for fraction={fraction}")
        # Link direction: bus0 AZPS, bus1 SRP, so negative p0 = SRP->AZPS.
        flow=-n.links_t.p0["AZPS_SRP"].to_numpy(dtype=float)
        measured=obs.to_numpy(dtype=float)
        residual=flow-measured
        shortage=n.generators_t.p["AZPS_unserved"].to_numpy(dtype=float)
        rows.append({"assumed_intertie_fraction":fraction,
                     "assumed_azps_srp_limit_mw":float(n.links.at["AZPS_SRP","p_nom"]),
                     "mean_modeled_srp_to_azps_mw":float(flow.mean()),
                     "mean_observed_srp_to_azps_mw":float(measured.mean()),
                     "mean_bias_mw":float(residual.mean()),
                     "mae_mw":float(np.abs(residual).mean()),
                     "rmse_mw":float(np.sqrt(np.mean(residual**2))),
                     "correlation":float(np.corrcoef(flow,measured)[0,1]) if np.std(flow)>1e-8 and np.std(measured)>1e-8 else float("nan"),
                     "azps_modeled_unserved_mwh":float(shortage.sum()),
                     "azps_shortage_hours":int((shortage>1e-4).sum()),
                     "observed_hours":len(flow)})
        hourly.extend({"timestamp":t.isoformat(),"assumed_intertie_fraction":fraction,
                       "modeled_srp_to_azps_mw":float(f),"observed_srp_to_azps_mw":float(y),
                       "modeled_minus_observed_mw":float(e)}
                      for t,f,y,e in zip(demand.index,flow,measured,residual))
    return pd.DataFrame(rows),pd.DataFrame(hourly)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--demand-csv",required=True)
    p.add_argument("--capacities",required=True)
    p.add_argument("--observed-csv",required=True)
    p.add_argument("--start",default="2024-07-01")
    p.add_argument("--end",default="2024-07-08")
    p.add_argument("--cache",default="data/cache")
    p.add_argument("--output",default="outputs/srp_flow_validation")
    a=p.parse_args()
    demand=load_eia930(a.demand_csv,a.start,a.end,bas=FOUR_BAS)
    weather=fetch_era5(a.start,a.end,a.cache,bas=FOUR_BAS)
    capacities=load_eia860_capacities(a.capacities,required_bas=tuple(FOUR_BAS))
    if any(tech in ("storage","other") and mw>0 for (_,tech),mw in capacities.items()):
        raise ValueError("Unsupported non-generator nameplate")
    summary,hourly=compare(demand,weather,capacities,pd.read_csv(a.observed_csv))
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    summary.to_csv(out/"link_assumption_vs_observed_exchange.csv",index=False)
    hourly.to_csv(out/"hourly_link_flow_comparison.csv",index=False)
    (out/"provenance.json").write_text(json.dumps({
        "observed_source":"EIA-930 AZPS-reported directional SRP bilateral interchange",
        "flow_sign":"positive is SRP->AZPS import, both observed and model",
        "assumed_link_capacity":"fraction * minimum of observed BA peak demands; NOT an engineered thermal rating",
        "model":"4-BA EIA-860 partial fleet, generator-only; observed-weather scenario; local unmet-demand isolation",
        "warning":"Observed dispatch cannot identify line capacity. Flow mismatch is descriptive, not a causal model validation. Model link is a hypothetical aggregation."
    },indent=2)+"\n")
    print(summary.to_string(index=False))

if __name__=="__main__":
    main()
