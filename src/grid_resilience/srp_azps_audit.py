"""Observed SRP-AZPS hourly demand/exchange alignment, without inventing transfer ratings."""
import argparse
import json
from pathlib import Path
import pandas as pd

def reconcile(demand_csv, exchange_csv, output):
    demand=pd.read_csv(demand_csv)
    needed={"timestamp","SRP","AZPS"}
    if not needed.issubset(demand):
        raise ValueError(f"Missing demand columns: {needed-set(demand)}")
    demand["timestamp"]=pd.to_datetime(demand.timestamp,utc=True,errors="coerce")
    if demand.timestamp.isna().any() or demand.timestamp.duplicated().any():
        raise ValueError("Invalid or duplicate demand timestamps")
    exchange=pd.read_csv(exchange_csv)
    required={"timestamp","from_ba","to_ba","reported_value"}
    if not required.issubset(exchange):
        raise ValueError(f"Missing exchange columns: {required-set(exchange)}")
    pair=exchange.loc[exchange.from_ba.eq("AZPS")&exchange.to_ba.eq("SRP")].copy()
    pair["timestamp"]=pd.to_datetime(pair.timestamp,utc=True,errors="coerce")
    pair["reported_value"]=pd.to_numeric(pair.reported_value,errors="coerce")
    if pair.timestamp.isna().any() or pair.reported_value.isna().any() or pair.timestamp.duplicated().any():
        raise ValueError("Invalid or duplicate AZPS-to-SRP exchange hours")
    joined=demand[["timestamp","AZPS","SRP"]].merge(
        pair[["timestamp","reported_value"]],on="timestamp",how="left",validate="one_to_one")
    if joined.reported_value.isna().any() or joined[["SRP","AZPS"]].isna().any().any():
        raise ValueError("Incomplete SRP demand or AZPS exchange alignment")
    joined["azps_imports_from_srp_mw"]=-joined.reported_value
    joined["srp_demand_mw"]=pd.to_numeric(joined.SRP,errors="raise")
    joined["azps_demand_mw"]=pd.to_numeric(joined.AZPS,errors="raise")
    if (joined[["srp_demand_mw","azps_demand_mw"]] <= 0).any().any():
        raise ValueError("Observed BA demand must be positive")
    result=joined[["timestamp","srp_demand_mw","azps_demand_mw","azps_imports_from_srp_mw"]]
    dest=Path(output);dest.mkdir(parents=True,exist_ok=True)
    result.to_csv(dest/"srp_azps_observed_hourly.csv",index=False)
    meta={
        "matched_hours":len(result),
        "mean_srp_demand_mw":float(result.srp_demand_mw.mean()),
        "mean_azps_imports_from_srp_mw":float(result.azps_imports_from_srp_mw.mean()),
        "source_interpretation":"EIA-930 from AZPS perspective, negative denotes imports",
        "warning":"Observed transfers do not establish SRP generator capacity or physical line ratings; no model topology has been calibrated"}
    (dest/"srp_azps_provenance.json").write_text(json.dumps(meta,indent=2)+"\n")
    return result,meta

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--demand-csv",required=True)
    p.add_argument("--exchange-csv",required=True)
    p.add_argument("--output",default="outputs/srp_azps")
    a=p.parse_args()
    _,summary=reconcile(a.demand_csv,a.exchange_csv,a.output)
    print(json.dumps(summary,indent=2))

if __name__=="__main__":
    main()
