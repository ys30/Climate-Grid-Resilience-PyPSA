"""Retrieve actual EIA-930 pairwise BA exchanges for AZPS (observations only).

EIA API v2 interchange-data hourly period is UTC hour-start. Reported
exchange is NOT a rated transmission capacity. Never use observed peaks as
physical intertie ratings without independent engineering evidence.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import pandas as pd

ENDPOINT = "https://api.eia.gov/v2/electricity/rto/interchange-data/data/"

def parse_exchange(records, start, end):
    df = pd.DataFrame(records)
    required = {"period", "fromba", "toba", "value"}
    if not required.issubset(df):
        raise ValueError(f"EIA interchange schema mismatch: missing {required-set(df)}")
    df = df.rename(columns={"period":"timestamp", "fromba":"from_ba", "toba":"to_ba", "value":"reported_value"})
    df["timestamp"] = pd.to_datetime(df.timestamp, utc=True, errors="coerce")
    df["reported_value"] = pd.to_numeric(df.reported_value, errors="coerce")
    if df[["timestamp", "from_ba", "to_ba", "reported_value"]].isna().any().any():
        raise ValueError("EIA interchange includes missing values or timestamps")
    if df.duplicated(["timestamp", "from_ba", "to_ba"]).any():
        raise ValueError("Duplicate hourly directional interchange observations")
    t0, t1 = pd.Timestamp(start, tz="UTC"), pd.Timestamp(end, tz="UTC")
    df = df.loc[(df.timestamp >= t0) & (df.timestamp < t1)]
    if df.empty:
        raise ValueError("No EIA interchange records in requested window")
    return df[["timestamp", "from_ba", "to_ba", "reported_value"]].sort_values(
        ["timestamp", "from_ba", "to_ba"]).reset_index(drop=True)

def fetch(start, end, output, key=None, page_size=5000):
    key = key or os.environ.get("EIA_API_KEY")
    if not key:
        raise RuntimeError("EIA_API_KEY required")
    a, b = pd.Timestamp(start), pd.Timestamp(end)
    if a.tz is not None or b.tz is not None or a >= b:
        raise ValueError("Use UTC naive ordered start and end")
    params = {"frequency":"hourly", "data[0]":"value",
              "facets[fromba][]":"AZPS",
              "start":a.strftime("%Y-%m-%dT%H"),
              "end":(b-pd.Timedelta(hours=1)).strftime("%Y-%m-%dT%H"),
              "sort[0][column]":"period", "sort[0][direction]":"asc",
              "length":str(page_size)}
    records = []
    offset = 0
    while True:
        url = ENDPOINT+"?"+urlencode({**params,"offset":str(offset),"api_key":key},doseq=True)
        try:
            with urlopen(Request(url,headers={"Accept":"application/json"}),timeout=60) as resp:
                obj=json.load(resp)
            page=obj["response"]
            batch=page["data"]
            total=int(page["total"])
        except Exception:
            raise RuntimeError("EIA interchange request failed; check route/facets or service") from None
        records.extend(batch)
        offset += len(batch)
        if offset >= total:
            break
        if not batch or offset > 100000:
            raise RuntimeError("Unexpected EIA interchange pagination")
    frame=parse_exchange(records,start,end)
    # These are directional measurements and sign conventions require inspection.
    if not frame.from_ba.eq("AZPS").all():
        raise ValueError("API fromba facet did not constrain records to AZPS")
    out=Path(output);out.parent.mkdir(parents=True,exist_ok=True)
    frame.to_csv(out,index=False)
    summary=frame.groupby("to_ba").reported_value.agg(["count","mean","min","max"]).reset_index()
    summary.to_csv(out.parent/"azps_observed_pairwise_exchange_summary.csv",index=False)
    (out.parent/"azps_exchange_provenance.json").write_text(json.dumps({
        "source":ENDPOINT,"window_utc":[start,end],
        "unit_as_reported":"EIA value; verify metadata before converting to MW/MWh",
        "warning":"Pairwise observed flow DOES NOT imply installed transfer capacity; sign and completeness require independent validation.",
        "source_api_key_saved":False},indent=2)+"\n")
    return frame

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--start",default="2024-07-01")
    p.add_argument("--end",default="2024-07-08")
    p.add_argument("--output",default="data/processed/azps_exchange.csv")
    a=p.parse_args()
    print("AZPS hourly pairwise exchange observations:",len(fetch(a.start,a.end,a.output)))

if __name__=="__main__":
    main()
