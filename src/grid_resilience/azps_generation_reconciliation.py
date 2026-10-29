"""Reconcile independently reported EIA net generation with observed demand/imports."""
import argparse
import json
from pathlib import Path
import pandas as pd

def reconcile(balance_csv, generation_csv, output):
    b=pd.read_csv(balance_csv)
    g=pd.read_csv(generation_csv)
    if not {"timestamp","observed_demand_mw","net_import_mw","implied_net_generation_mw"}.issubset(b):
        raise ValueError("AZPS balance input missing required columns")
    if not {"timestamp","AZPS"}.issubset(g):
        raise ValueError("Independent EIA NG file lacks AZPS")
    for frame in (b,g):
        frame["timestamp"]=pd.to_datetime(frame.timestamp,utc=True,errors="coerce")
        if frame.timestamp.isna().any() or frame.timestamp.duplicated().any():
            raise ValueError("Invalid or duplicate hourly timestamps")
    joined=b.merge(g[["timestamp","AZPS"]].rename(columns={"AZPS":"reported_net_generation_mw"}),
                   on="timestamp",how="left",validate="one_to_one")
    if joined.reported_net_generation_mw.isna().any():
        raise ValueError("Independent AZPS NG missing at required hours")
    joined["balance_residual_mw"]=(joined.observed_demand_mw-
        joined.net_import_mw-joined.reported_net_generation_mw)
    target=Path(output);target.mkdir(parents=True,exist_ok=True)
    joined.to_csv(target/"azps_independent_generation_residual.csv",index=False)
    metrics={
        "hours":len(joined),
        "mean_reported_generation_mw":float(joined.reported_net_generation_mw.mean()),
        "mean_implied_generation_mw":float(joined.implied_net_generation_mw.mean()),
        "mean_balance_residual_mw":float(joined.balance_residual_mw.mean()),
        "maximum_absolute_residual_mw":float(joined.balance_residual_mw.abs().max()),
        "p95_absolute_residual_mw":float(joined.balance_residual_mw.abs().quantile(.95)),
        "identity":"demand - net imports - independently reported net generation",
        "interpretation":"Residual may include accounting adjustment/losses/reporting timing; not automatically model error",
        "warning":"This is observed EIA-930 BA accounting, not independently validated physical line rating or an observed outage"}
    (target/"azps_generation_reconciliation.json").write_text(json.dumps(metrics,indent=2)+"\n")
    return joined,metrics

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--balance-csv",required=True)
    p.add_argument("--generation-csv",required=True)
    p.add_argument("--output",default="outputs/azps_generation_reconciliation")
    a=p.parse_args()
    _,m=reconcile(a.balance_csv,a.generation_csv,a.output)
    print(json.dumps(m,indent=2))

if __name__=="__main__":
    main()
