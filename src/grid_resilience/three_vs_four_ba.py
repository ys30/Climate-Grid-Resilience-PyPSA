"""Compare verified 3-BA and 4-BA PyPSA outputs without claiming causal grid effects."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import pandas as pd

SCENARIOS=("observed_weather","heat_plus_4c","compound_heat_wind_derating")
BAS=("CISO","AZPS","BPAT")

def compare(three_csv, four_csv, output):
    a=pd.read_csv(three_csv)
    b=pd.read_csv(four_csv)
    required={"scenario","ba","unserved_energy_mwh"}
    for label,df in (("three",a),("four",b)):
        if not required.issubset(df):
            raise ValueError(f"{label}: missing {sorted(required-set(df))}")
        if df.duplicated(["scenario","ba"]).any():
            raise ValueError(f"{label}: duplicate scenario/BA")
        df["unserved_energy_mwh"]=pd.to_numeric(df.unserved_energy_mwh,errors="raise")
        if df.unserved_energy_mwh.isna().any() or (df.unserved_energy_mwh < -1e-5).any():
            raise ValueError(f"{label}: invalid modeled deficit")
    target=pd.MultiIndex.from_product([SCENARIOS,BAS],names=["scenario","ba"])
    if not target.isin(a.set_index(["scenario","ba"]).index).all():
        raise ValueError("Three-BA experiment incomplete")
    if not target.isin(b.set_index(["scenario","ba"]).index).all():
        raise ValueError("Four-BA experiment incomplete on shared BAs")
    if not set(b.ba).issuperset({*BAS,"SRP"}):
        raise ValueError("Four-BA model missing SRP")
    left=a.set_index(["scenario","ba"]).loc[target,["unserved_energy_mwh"]].rename(
        columns={"unserved_energy_mwh":"three_ba_mwh"})
    right=b.set_index(["scenario","ba"]).loc[target,["unserved_energy_mwh"]].rename(
        columns={"unserved_energy_mwh":"four_ba_mwh"})
    result=left.join(right,validate="one_to_one").reset_index()
    result["change_mwh"]=result.four_ba_mwh-result.three_ba_mwh
    result["reduction_percent"]=result.apply(
        lambda r: (1-r.four_ba_mwh/r.three_ba_mwh)*100 if r.three_ba_mwh>0 else float("nan"),
        axis=1)
    path=Path(output);path.mkdir(parents=True,exist_ok=True)
    result.to_csv(path/"shared_ba_scenario_comparison.csv",index=False)
    metadata={
        "description":"Difference between separate 3-BA and 4-BA linear dispatch models; not measured avoided outage",
        "shared_bas":list(BAS),
        "difference_formula":"four-BA minus three-BA simulated unserved MWh",
        "caution":"Four-BA adds an assumed AZPS-SRP link, changes balancing-area model coverage; no calibrated transfer limits, storage or actual dispatch data.",
        "requirement":"Input scenarios must use matching dates, weather assumptions and EIA-860 inventory year"
    }
    (path/"comparison_provenance.json").write_text(json.dumps(metadata,indent=2)+"\n")
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--three",required=True)
    p.add_argument("--four",required=True)
    p.add_argument("--output",default="outputs/three_vs_four_ba")
    args=p.parse_args()
    print(compare(args.three,args.four,args.output).to_string(index=False))

if __name__=="__main__":
    main()
