"""Synthetic climate-stress sensitivity; NOT real weather, grid data, or PyPSA dispatch."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HOURS=np.arange(24)
SCENARIOS={"Baseline":(1.0,1.0),"Heatwave":(1.25,0.9),"Compound stress":(1.35,0.72)}

def scenario_data():
    rows=[]
    for scenario,(demand_mult,supply_mult) in SCENARIOS.items():
        for hour in HOURS:
            base_demand=110+20*np.sin((hour-7)*np.pi/12)**2
            demand=base_demand*demand_mult
            available=165*supply_mult
            shortfall=max(demand-available,0.)
            rows.append((scenario,int(hour),demand,available,shortfall))
    return pd.DataFrame(rows,columns=["scenario","hour","demand_mw","available_supply_mw","unserved_mw"])

def metrics(df):
    return df.groupby("scenario",sort=False).agg(unserved_energy_mwh=("unserved_mw","sum"),peak_shortfall_mw=("unserved_mw","max"),hours_with_shortfall=("unserved_mw",lambda x:int((x>0).sum())))

def analyze(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    df=scenario_data();m=metrics(df)
    df.to_csv(output/"hourly_scenarios.csv",index=False);m.to_csv(output/"resilience_metrics.csv")
    fig,ax=plt.subplots(figsize=(9,5))
    for name,group in df.groupby("scenario",sort=False):
        ax.plot(group.hour,group.unserved_mw,label=name)
    ax.set(xlabel="Hour of illustrative day",ylabel="Unserved power (MW)",title="Synthetic supply-demand stress test");ax.legend();fig.tight_layout();fig.savefig(output/"shortfall_profiles.png",dpi=170);plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,4.5));m.unserved_energy_mwh.plot.bar(ax=ax,rot=0)
    ax.set(ylabel="Unserved energy (MWh)",title="Illustrative climate-stress scenarios");fig.tight_layout();fig.savefig(output/"unserved_energy.png",dpi=170);plt.close(fig)
    return m.to_dict(orient="index")
