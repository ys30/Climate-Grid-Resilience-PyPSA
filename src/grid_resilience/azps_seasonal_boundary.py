"""Summarize same-length seasonal AZPS reported interchange audits.

Each window is one complete seven-day UTC span in 2024. Observed BA
accounting, not simulated physical transmission.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

WINDOWS={
 "winter":("2024-01-15","2024-01-22"),
 "spring":("2024-04-15","2024-04-22"),
 "summer":("2024-07-01","2024-07-08"),
 "autumn":("2024-10-14","2024-10-21"),
}

def summarize(root,output):
    rows=[]
    for season,(start,end) in WINDOWS.items():
        folder=Path(root)/season
        hourly=pd.read_csv(folder/"azps_boundary_hourly.csv")
        neighbors=pd.read_csv(folder/"azps_boundary_neighbors.csv")
        t=pd.to_datetime(hourly.timestamp,utc=True,errors="coerce")
        if len(t)!=168 or t.isna().any() or t.duplicated().any():
            raise ValueError(f"{season}: expected 168 distinct timestamps")
        expected=pd.date_range(pd.Timestamp(start,tz="UTC"),periods=168,freq="h")
        if not pd.DatetimeIndex(t).equals(expected):
            raise ValueError(f"{season}: incomplete or misaligned UTC week")
        imports=pd.to_numeric(hourly.net_import_mw_outside,errors="raise")
        if imports.isna().any():
            raise ValueError(f"{season}: missing external net exchange")
        rows.append({
            "season":season,"start_utc":start,"end_exclusive_utc":end,
            "observed_hours":len(hourly),"reported_neighbors":len(neighbors),
            "mean_outside_net_import_mw":float(imports.mean()),
            "hours_outside_net_import":int((imports>0).sum()),
            "hours_outside_net_export":int((imports<0).sum()),
            "hours_outside_zero_net":int((imports==0).sum()),
            "outside_net_import_mwh":float(imports.sum()),
            "outside_net_export_mwh":float((-imports).clip(lower=0).sum()),
            "outside_net_import_positive_mwh":float(imports.clip(lower=0).sum()),
            "outside_gross_exchange_fraction":float(
                pd.to_numeric(hourly.gross_exchange_mw_outside).sum() /
                (pd.to_numeric(hourly.gross_exchange_mw_outside).sum()+
                 pd.to_numeric(hourly.gross_exchange_mw_included).sum()))
        })
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    df=pd.DataFrame(rows)
    df.to_csv(out/"seasonal_azps_boundary_summary.csv",index=False)
    (out/"provenance.json").write_text(json.dumps({
       "year":2024,"weeks":WINDOWS,"scope":"Four sampled 7-day weeks; not full seasons",
       "interpretation":"EIA-930 AZPS reported bilateral net flows to seven nonmodeled partners",
       "warning":"No physical transfer capacities inferred; neither same-week net exports nor sample weeks establish yearly reliability"
    },indent=2)+"\n")
    return df

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True)
    p.add_argument("--output",default="outputs/seasonal_azps")
    a=p.parse_args()
    print(summarize(a.root,a.output).to_string(index=False))
if __name__=="__main__":main()
