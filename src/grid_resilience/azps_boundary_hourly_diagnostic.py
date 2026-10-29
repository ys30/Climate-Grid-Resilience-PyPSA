"""Analyze hourly missing-boundary exchange signs without treating them as capacities."""
import argparse
import json
from pathlib import Path
import pandas as pd

def diagnose(boundary_csv, balance_csv, output):
    b=pd.read_csv(boundary_csv)
    d=pd.read_csv(balance_csv)
    need_b={"timestamp","net_import_mw_included","net_import_mw_outside","net_import_all_mw"}
    need_d={"timestamp","observed_demand_mw","net_import_mw","implied_net_generation_mw"}
    if not need_b.issubset(b) or not need_d.issubset(d):
        raise ValueError("Missing required boundary or demand accounting fields")
    for x in (b,d):
        x["timestamp"]=pd.to_datetime(x.timestamp,utc=True,errors="coerce")
        if x.timestamp.isna().any() or x.timestamp.duplicated().any():
            raise ValueError("Invalid/duplicate hourly timestamps")
    result=d.merge(b,on="timestamp",how="inner",validate="one_to_one").sort_values("timestamp")
    if len(result)!=len(d) or len(result)!=len(b):
        raise ValueError("Incomplete boundary-demand hourly alignment")
    for col in ("net_import_mw_included","net_import_mw_outside","net_import_all_mw",
                "observed_demand_mw","net_import_mw","implied_net_generation_mw"):
        result[col]=pd.to_numeric(result[col],errors="raise")
        if result[col].isna().any():
            raise ValueError(f"Missing hourly {col}")
    diff=result.net_import_all_mw-result.net_import_mw
    if diff.abs().max()>1e-6:
        raise ValueError("Boundary sum does not match AZPS complete reported net interchange")
    result["outside_import_mw"]=result.net_import_mw_outside.clip(lower=0)
    result["outside_export_mw"]=(-result.net_import_mw_outside).clip(lower=0)
    result["inside_only_implied_generation_mw"]=result.observed_demand_mw-result.net_import_mw_included
    result["omitted_boundary_accounting_delta_mw"]=result.inside_only_implied_generation_mw-result.implied_net_generation_mw
    # This is merely an accounting alternative; not actual dispatch or missing generator capacity.
    metrics={
        "hours":int(len(result)),
        "hours_outside_net_import":int((result.net_import_mw_outside>0).sum()),
        "hours_outside_net_export":int((result.net_import_mw_outside<0).sum()),
        "hours_outside_net_zero":int((result.net_import_mw_outside==0).sum()),
        "outside_import_mwh":float(result.outside_import_mw.sum()),
        "outside_export_mwh":float(result.outside_export_mw.sum()),
        "outside_net_import_mwh":float(result.net_import_mw_outside.sum()),
        "mean_outside_net_import_mw":float(result.net_import_mw_outside.mean()),
        "max_outside_import_mw":float(result.outside_import_mw.max()),
        "max_outside_export_mw":float(result.outside_export_mw.max()),
        "identity_max_abs_residual_mw":float(diff.abs().max()),
        "interpretation":"Reported exchange boundary accounting only; NOT physical transmission capability or modeled generation availability.",
        "limitation":"Signed net imports can mask simultaneous exchanges with different counterparties; use original bilateral CSV for gross-flow analyses."
    }
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    result.to_csv(out/"azps_outside_boundary_hourly_diagnostic.csv",index=False)
    (out/"azps_outside_boundary_diagnostic.json").write_text(json.dumps(metrics,indent=2)+"\n")
    return metrics

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--boundary-csv",required=True)
    p.add_argument("--balance-csv",required=True)
    p.add_argument("--output",default="outputs/azps_outside_boundary")
    a=p.parse_args()
    print(json.dumps(diagnose(a.boundary_csv,a.balance_csv,a.output),indent=2))
if __name__=="__main__": main()
