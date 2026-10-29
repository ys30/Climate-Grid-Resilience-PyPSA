"""Audit actual AZPS hourly observed exchange and demand, without inferring link ratings.

For EIA-930 pairwise interchange, positive is an export from fromba,
negative is an import into fromba. Data are hourly average MW-equivalent.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import pandas as pd
from .western_us import load_eia930

def balance(exchange_csv, demand_csv, start, end, output):
    x = pd.read_csv(exchange_csv, parse_dates=["timestamp"])
    needed = {"timestamp", "from_ba", "to_ba", "reported_value"}
    if not needed.issubset(x):
        raise ValueError(f"Exchange file missing: {sorted(needed-set(x))}")
    if not x.from_ba.eq("AZPS").all():
        raise ValueError("This diagnostic expects AZPS-reported exchanges only")
    if x.duplicated(["timestamp", "from_ba", "to_ba"]).any():
        raise ValueError("Duplicate AZPS pairwise exchange record")
    x["timestamp"] = pd.to_datetime(x.timestamp, utc=True, errors="coerce")
    x["reported_value"] = pd.to_numeric(x.reported_value, errors="coerce")
    if x[["timestamp", "reported_value"]].isna().any().any():
        raise ValueError("Invalid exchange MW or hour")
    d = load_eia930(demand_csv, start, end)["AZPS"].rename("observed_demand_mw")
    hourly = x.groupby("timestamp").reported_value.sum().rename("net_export_mw").reindex(d.index)
    if hourly.isna().any():
        raise ValueError("AZPS reported exchanges do not cover all demand hours")
    result = pd.concat([d, hourly], axis=1)
    result["net_import_mw"] = -result.net_export_mw
    result["implied_net_generation_mw"] = result.observed_demand_mw - result.net_import_mw
    # Conservation identity: demand = generation + net imports; generation
    # here is inferred from two reported fields, not an independent measurement.
    if (result.implied_net_generation_mw < 0).any():
        raise ValueError("Negative derived generation; investigate reported data/sign conventions")
    result.index.name = "timestamp"
    out = Path(output);out.mkdir(parents=True,exist_ok=True)
    result.to_csv(out/"azps_hourly_demand_import_balance.csv")
    by_neighbor = x.groupby("to_ba").agg(
        observed_hours=("reported_value", "count"),
        mean_net_export_mw=("reported_value", "mean"),
        minimum_net_export_mw=("reported_value", "min"),
        maximum_net_export_mw=("reported_value", "max")).reset_index()
    by_neighbor["mean_net_import_mw"] = -by_neighbor.mean_net_export_mw
    by_neighbor.to_csv(out/"azps_neighbor_import_summary.csv",index=False)
    info = {
        "period_start_utc":start,"period_end_exclusive_utc":end,
        "observed_hours":len(result),"distinct_neighbors":int(len(by_neighbor)),
        "mean_net_import_mw":float(result.net_import_mw.mean()),
        "min_net_import_mw":float(result.net_import_mw.min()),
        "max_net_import_mw":float(result.net_import_mw.max()),
        "net_import_mwh":float(result.net_import_mw.sum()),
        "mean_implied_net_generation_mw":float(result.implied_net_generation_mw.mean()),
        "formula":"reported demand = implied net generation + observed net imports",
        "scope":"EIA-930 reported BA operations; not independently validated generation",
        "limits":["No independent EIA NG reconciliation yet",
                  "No direct conversion from observed interchange to transmission capacity",
                  "EIA-860 annual nameplate and EIA-930 BA accounting have differing populations",
                  "Observed interchange is not an optimization input in this audit"]
    }
    (out/"azps_balance_provenance.json").write_text(json.dumps(info,indent=2)+"\n")
    return result, by_neighbor, info

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--exchange-csv",required=True)
    p.add_argument("--demand-csv",required=True)
    p.add_argument("--start",default="2024-07-01")
    p.add_argument("--end",default="2024-07-08")
    p.add_argument("--output",default="outputs/azps_observed_balance")
    a=p.parse_args()
    _,_,info=balance(a.exchange_csv,a.demand_csv,a.start,a.end,a.output)
    print(json.dumps(info,indent=2))

if __name__=="__main__":
    main()
