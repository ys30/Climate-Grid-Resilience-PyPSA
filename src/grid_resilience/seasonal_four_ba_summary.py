"""Compare PyPSA four-BA adequacy across four sampled 2024 UTC weeks.

Each seasonal output is a separate matched-demand/weather EIA-860 run;
results are descriptive deterministic sensitivity, not observed outages.
"""
import argparse
import json
from pathlib import Path
import pandas as pd
from .azps_seasonal_boundary import WINDOWS

def aggregate(root, output):
    frames=[]
    required={"scenario","ba","unserved_energy_mwh","shortage_hours"}
    for season in WINDOWS:
        path=Path(root)/season/"metrics.csv"
        df=pd.read_csv(path)
        if not required.issubset(df):
            raise ValueError(f"{season}: missing model output columns")
        if df.duplicated(["scenario","ba"]).any():
            raise ValueError(f"{season}: duplicate scenario/BA")
        if set(df.ba)!={"CISO","AZPS","BPAT","SRP"}:
            raise ValueError(f"{season}: missing or unexpected BA")
        if set(df.scenario)!={"observed_weather","heat_plus_4c","compound_heat_wind_derating"}:
            raise ValueError(f"{season}: wrong scenario set")
        for column in ("unserved_energy_mwh","shortage_hours"):
            df[column]=pd.to_numeric(df[column],errors="raise")
            if df[column].isna().any() or (df[column]<0).any():
                raise ValueError(f"{season}: invalid nonnegative model result")
        df.insert(0,"season",season)
        frames.append(df)
    result=pd.concat(frames,ignore_index=True)
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    result.to_csv(out/"seasonal_four_ba_adequacy.csv",index=False)
    azps=result.loc[result.ba=="AZPS"].copy()
    azps.to_csv(out/"seasonal_azps_adequacy.csv",index=False)
    (out/"provenance.json").write_text(json.dumps({
       "windows":WINDOWS,"interpretation":"Four sampled 168-hour weeks, NOT full seasons or annual EENS",
       "scenarios":"Fixed temperature/wind/intertie stylized stress rules applied independently to seasonal ERA5",
       "source_fleet":"2024 EIA-860 year-end capacity, not matched historic seasonal generation dispatch",
       "warning":"Hypothetical BA links, simplified nameplate, no storage; modeled shortage is not a recorded blackout."
    },indent=2)+"\n")
    return azps

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True)
    p.add_argument("--output",default="outputs/seasonal_four_ba_summary")
    a=p.parse_args()
    print(aggregate(a.root,a.output).to_string(index=False))
if __name__=="__main__":main()
