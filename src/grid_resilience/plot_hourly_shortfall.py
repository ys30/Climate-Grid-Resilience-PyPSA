"""Render truthful hourly AZPS modeled shortfall from solved PyPSA NetCDF snapshots.

Usage: python -m grid_resilience.plot_hourly_shortfall --input outputs/four_ba --output outputs/four_ba/figures
Requires PyPSA model dependencies and matplotlib; does not infer any real outages.
"""
import argparse
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pypsa

SCENARIOS={
    "observed_weather":"Observed weather",
    "heat_plus_4c":"Heat +4°C",
    "compound_heat_wind_derating":"Compound stress",
}

def plot(input_dir,output_dir,ba="AZPS"):
    input_dir=Path(input_dir)
    output_dir=Path(output_dir)
    output_dir.mkdir(parents=True,exist_ok=True)
    fig,ax=plt.subplots(figsize=(12,5))
    out=[]
    for scenario,label in SCENARIOS.items():
        network=pypsa.Network(input_dir/f"solved_{scenario}.nc")
        col=f"{ba}_unserved"
        if col not in network.generators_t.p:
            raise ValueError(f"Missing shortage generator {col} in {scenario}")
        values=network.generators_t.p[col].clip(lower=0)
        if len(values)!=168:
            raise ValueError("Expected 168 distinct hourly samples")
        ax.plot(pd.to_datetime(values.index),values.to_numpy(),label=label,linewidth=1.8)
        out.extend({"scenario":scenario,"timestamp":str(t),"modeled_shortfall_mw":float(v)}
                   for t,v in values.items())
    pd.DataFrame(out).to_csv(output_dir/f"{ba.lower()}_hourly_shortfall.csv",index=False)
    ax.set(title=f"{ba} modeled hourly unserved demand, sampled July 2024",
           ylabel="Modeled unmet load (MW)",xlabel="UTC snapshot")
    ax.grid(alpha=.25);ax.legend(frameon=False)
    fig.text(.5,.01,"Deterministic screening model; NOT measured outages or calibrated grid reliability.",ha="center",fontsize=9)
    fig.tight_layout(rect=[0,.03,1,1])
    for ext in ("svg","png"):
        fig.savefig(output_dir/f"{ba.lower()}_hourly_shortfall.{ext}",dpi=160)
    plt.close(fig)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True)
    p.add_argument("--output",required=True)
    p.add_argument("--ba",default="AZPS")
    args=p.parse_args()
    plot(args.input,args.output,args.ba)

if __name__=="__main__":
    main()
