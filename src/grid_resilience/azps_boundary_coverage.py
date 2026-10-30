"""Audit how much reported AZPS interchange crosses a simplified model boundary.

EIA-930 AZPS-reported directional interchange: negative=import to AZPS.
Reported bilateral interchange is not a single line's flow or capacity.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

def audit(exchange_csv, output, modeled_neighbors=("CISO","SRP")):
    x=pd.read_csv(exchange_csv)
    required={"timestamp","from_ba","to_ba","reported_value"}
    if not required.issubset(x):
        raise ValueError(f"Exchange missing columns: {sorted(required-set(x))}")
    x["timestamp"]=pd.to_datetime(x.timestamp,utc=True,errors="coerce")
    x["reported_value"]=pd.to_numeric(x.reported_value,errors="coerce")
    if x[["timestamp","from_ba","to_ba","reported_value"]].isna().any().any():
        raise ValueError("Missing or invalid hourly exchange")
    if not x.from_ba.eq("AZPS").all() or x.duplicated(["timestamp","to_ba"]).any():
        raise ValueError("Expected unique AZPS-reported directional BA pairs")
    if x.empty:
        raise ValueError("No reported exchange")
    counts=x.groupby("timestamp").size()
    expected=pd.date_range(counts.index.min(),counts.index.max(),freq="h")
    if counts.size!=len(expected) or not counts.index.equals(expected):
        raise ValueError("AZPS exchange hours must form a consecutive UTC hourly window")
    x["modeled_neighbor"]=x.to_ba.isin(modeled_neighbors)
    x["azps_net_import_mw"]=-x.reported_value
    x["abs_exchange_mw"]=x.reported_value.abs()
    hour=x.groupby(["timestamp","modeled_neighbor"]).agg(
        net_import_mw=("azps_net_import_mw","sum"),gross_exchange_mw=("abs_exchange_mw","sum")).unstack(fill_value=0)
    hour.columns=["_".join([a,"included" if b else "outside"]) for a,b in hour.columns]
    for key in ("net_import_mw_included","net_import_mw_outside","gross_exchange_mw_included","gross_exchange_mw_outside"):
        if key not in hour:hour[key]=0.
    hour["net_import_all_mw"]=hour.net_import_mw_included+hour.net_import_mw_outside
    denom=hour.gross_exchange_mw_included+hour.gross_exchange_mw_outside
    hour["outside_gross_share"]=hour.gross_exchange_mw_outside/denom.where(denom>0)
    per=x.groupby(["to_ba","modeled_neighbor"]).agg(
        reported_hours=("timestamp","size"),mean_net_import_mw=("azps_net_import_mw","mean"),
        total_abs_exchange_mwh=("abs_exchange_mw","sum")).reset_index()
    per=per.sort_values("total_abs_exchange_mwh",ascending=False)
    summary={"observed_hours":int(len(hour)),
       "modeled_neighbors":list(modeled_neighbors),
       "observed_neighbors":sorted(x.to_ba.unique().tolist()),
       "outside_neighbors":sorted(set(x.to_ba)-set(modeled_neighbors)),
       "total_reported_gross_exchange_mwh":float(x.abs_exchange_mw.sum()),
       "outside_gross_exchange_fraction":float(x.loc[~x.modeled_neighbor,"abs_exchange_mw"].sum()/x.abs_exchange_mw.sum()),
       "mean_net_import_from_outside_mw":float(hour.net_import_mw_outside.mean()),
       "mean_total_net_import_mw":float(hour.net_import_all_mw.mean()),
       "interpretation":"Boundary coverage diagnostic; gross absolute reported exchanges, not physical transfer ratings",
       "warning":"Missing model partners and their interactions can invalidate modeled shortage attribution; reported data are BA accounting."}
    target=Path(output);target.mkdir(parents=True,exist_ok=True)
    hour.rename_axis("timestamp").to_csv(target/"azps_boundary_hourly.csv")
    per.to_csv(target/"azps_boundary_neighbors.csv",index=False)
    (target/"azps_boundary_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    return summary

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--exchange-csv",required=True)
    p.add_argument("--output",default="outputs/azps_boundary_coverage")
    a=p.parse_args()
    print(json.dumps(audit(a.exchange_csv,a.output),indent=2))
if __name__=="__main__":main()
