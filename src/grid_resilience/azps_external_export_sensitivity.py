"""Ex-post AZPS outside-boundary export obligation sensitivity.

A separate fixed export load is attached to AZPS supply bus. This is a
diagnostic and not a calibrated electricity network or causal counterfactual.
"""
import argparse
import json
from pathlib import Path
import pandas as pd
from .four_ba import FOUR_BAS,FOUR_LINKS
from .western_us import SCENARIOS,build_model,fetch_era5,load_eia930
from .capacity_adapter import load_eia860_capacities

def prepare_obligation(boundary_csv,index):
    df=pd.read_csv(boundary_csv)
    if not {"timestamp","net_import_mw_outside"}.issubset(df):
        raise ValueError("Missing boundary accounting fields")
    df["timestamp"]=pd.to_datetime(df.timestamp,utc=True,errors="coerce")
    if df.timestamp.isna().any() or df.timestamp.duplicated().any():
        raise ValueError("Invalid boundary timestamps")
    values=pd.to_numeric(df.set_index("timestamp").net_import_mw_outside,errors="raise").reindex(index)
    if values.isna().any():
        raise ValueError("Unmatched boundary hours")
    # Take only *net* export obligation, no conversion into fictitious supply.
    return (-values).clip(lower=0)

def experiment(demand,weather,caps,obligation):
    if len(obligation)!=len(demand):
        raise ValueError("Obligation must match modeled snapshots")
    rows=[]
    for scenario in SCENARIOS:
        for enabled in (False,True):
            n=build_model(demand,weather,scenario,capacities=caps,
                          bas=FOUR_BAS,interties=FOUR_LINKS,local_shedding=True)
            if enabled:
                # Fixed observed export to nonmodeled partners. Attached on AZPS
                # physical supply bus, not its private unmet-demand bus.
                n.add("Bus","AZPS_external_obligation_bus")
                n.add("Link","AZPS_external_supply",bus0="AZPS",bus1="AZPS_external_obligation_bus",p_nom=max(float(obligation.max())*2,1.),p_min_pu=0,efficiency=1.0)
                n.add("Load","AZPS_external_observed_net_export_diagnostic",bus="AZPS_external_obligation_bus",p_set=obligation.to_numpy(dtype=float))
                n.add("Generator","AZPS_external_unserved",bus="AZPS_external_obligation_bus",p_nom=max(float(obligation.max())*2,1.),marginal_cost=10000.0)
            status,termination=n.optimize(solver_name="highs")
            if (status,termination)!=("ok","optimal"):
                raise RuntimeError(f"Solver failed: {scenario}, boundary={enabled}")
            for ba in FOUR_BAS:
                shortage=n.generators_t.p[f"{ba}_unserved"].clip(lower=0)
                rows.append({"scenario":scenario,"boundary_obligation_enabled":enabled,
                             "external_obligation_unserved_mwh":float(n.generators_t.p["AZPS_external_unserved"].sum()) if enabled and ba=="AZPS" else 0.,
                             "ba":ba,"modeled_unserved_mwh":float(shortage.sum()),
                             "shortage_hours":int((shortage>1e-4).sum()),
                             "observed_outside_net_export_obligation_mwh":float(obligation.sum()) if enabled else 0.})
    return pd.DataFrame(rows)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--demand-csv",required=True)
    p.add_argument("--capacities",required=True)
    p.add_argument("--boundary-csv",required=True)
    p.add_argument("--cache",default="data/cache")
    p.add_argument("--start",default="2024-07-01")
    p.add_argument("--end",default="2024-07-08")
    p.add_argument("--output",default="outputs/azps_external_export_sensitivity")
    a=p.parse_args()
    demand=load_eia930(a.demand_csv,a.start,a.end,bas=FOUR_BAS)
    obligation=prepare_obligation(a.boundary_csv,demand.index)
    weather=fetch_era5(a.start,a.end,a.cache,bas=FOUR_BAS)
    caps=load_eia860_capacities(a.capacities,required_bas=tuple(FOUR_BAS))
    if any(t in ("storage","other") and mw>0 for (_,t),mw in caps.items()):
        raise ValueError("Use projected generator-only capacities")
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    results=experiment(demand,weather,caps,obligation)
    results.to_csv(out/"external_obligation_scenarios.csv",index=False)
    obligation.rename("external_net_export_obligation_mw").rename_axis("timestamp").to_csv(out/"observed_hourly_external_obligation.csv")
    (out/"provenance.json").write_text(json.dumps({
        "period":[a.start,a.end],"treatment":"fixed ex-post positive net export to nonmodeled neighbors, on AZPS supply bus",
        "total_external_export_mwh":float(obligation.sum()),
        "important":"This is a screening sensitivity, not a physically validated BA dispatch counterfactual; historical BA demand and exchanges may share accounting conventions, and applying observed exports as extra load can double-count obligations depending on demand definitions.",
        "no_claim":"NOT measured avoided outages, calibrated firm exports or historical network thermal limits",
        "constraint":"One-way local shedding prevents export of virtual unmet-demand generation. Unmet external obligations are modeled with separate isolated shortage and excluded from native AZPS shortage."
    },indent=2)+"\n")
    print(results.to_string(index=False))

if __name__=="__main__":main()
