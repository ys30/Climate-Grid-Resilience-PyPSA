"""Download EIA-930 independently reported hourly net generation (NG).

Do not infer generation from demand and net imports here. Validate the
separate EIA region-data type NG for each requested balancing authority.
"""
import argparse
import json
import os
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import pandas as pd
from .eia_api import ENDPOINT, _get

def parse_generation(records, start, end, bas):
    data=pd.DataFrame(records)
    required={"period","respondent","type","value"}
    if not required.issubset(data):
        raise ValueError(f"EIA generation schema missing {sorted(required-set(data))}")
    data=data.loc[data["type"].eq("NG") & data.respondent.isin(bas)].copy()
    data["timestamp"]=pd.to_datetime(data.period,utc=True,errors="coerce")
    data["net_generation_mw"]=pd.to_numeric(data.value,errors="coerce")
    if data.timestamp.isna().any() or data.net_generation_mw.isna().any():
        raise ValueError("Invalid independently reported net generation or timestamp")
    if data.duplicated(["timestamp","respondent"]).any():
        raise ValueError("Duplicate BA-hour generation records")
    index=pd.date_range(pd.Timestamp(start,tz="UTC"),pd.Timestamp(end,tz="UTC"),freq="h",inclusive="left")
    frame=data.pivot(index="timestamp",columns="respondent",values="net_generation_mw").reindex(
        index=index,columns=list(bas))
    if frame.isna().any().any():
        raise ValueError(f"Missing hourly net generation: {frame.isna().sum().to_dict()}")
    frame.columns.name=None
    return frame.astype(float)

def fetch_generation(start,end,output,bas=("AZPS","SRP"),key=None,page_size=5000):
    bas=tuple(bas)
    if not bas or len(bas)!=len(set(bas)):
        raise ValueError("Select unique BA codes")
    key=key or os.environ.get("EIA_API_KEY")
    if not key:
        raise RuntimeError("EIA_API_KEY missing")
    start_ts,end_ts=pd.Timestamp(start),pd.Timestamp(end)
    if start_ts.tz is not None or end_ts.tz is not None or start_ts>=end_ts:
        raise ValueError("Use naive UTC range with end after start")
    params={"frequency":"hourly","data[0]":"value",
            "facets[type][]":["NG"],"facets[respondent][]":list(bas),
            "start":start_ts.strftime("%Y-%m-%dT%H"),
            "end":(end_ts-pd.Timedelta(hours=1)).strftime("%Y-%m-%dT%H"),
            "sort[0][column]":"period","sort[0][direction]":"asc",
            "length":str(page_size)}
    records=[];offset=0
    while True:
        result=_get({**params,"offset":str(offset)},key)
        batch=result["data"]
        records.extend(batch);offset+=len(batch)
        if offset>=int(result.get("total",0)):
            break
        if not batch or offset>200000:
            raise RuntimeError("Unexpected EIA NG pagination")
    frame=parse_generation(records,start,end,bas)
    path=Path(output);path.parent.mkdir(parents=True,exist_ok=True)
    frame.rename_axis("timestamp").to_csv(path)
    path.with_suffix(".provenance.json").write_text(json.dumps({
        "source":ENDPOINT,"series_type":"NG","BA_codes":list(bas),
        "start_utc":start,"end_exclusive_utc":end,
        "description":"EIA-930 independently reported hourly net generation; not a computed power balance",
        "key_saved":False},indent=2)+"\n")
    return frame

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--start",default="2024-07-01")
    p.add_argument("--end",default="2024-07-08")
    p.add_argument("--bas",nargs="+",default=["AZPS","SRP"])
    p.add_argument("--output",default="data/processed/azps_srp_reported_ng.csv")
    a=p.parse_args()
    print(fetch_generation(a.start,a.end,a.output,tuple(a.bas)).describe().to_string())

if __name__=="__main__":
    main()
