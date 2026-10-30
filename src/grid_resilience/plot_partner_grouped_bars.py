"""Plot audited AZPS 2024 sampled-week partner exchange as a readable grouped bar chart.

Positive means AZPS net imports; negative means AZPS net exports.
"""
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SEASONS=("winter","spring","summer","autumn")
PARTNERS=("WALC","LDWP","PNM","TEPC","PACE","WACM","IID")

def draw(csv_path, output):
    df=pd.read_csv(csv_path)
    required={"season","partner","mean_net_import_mw","reported_hours","modeled"}
    if not required.issubset(df.columns):raise ValueError("Missing exchange columns")
    out=df.loc[df.modeled.astype(str).str.lower().eq("false")].copy()
    if len(out)!=28 or out.duplicated(["season","partner"]).any():
        raise ValueError("Expected exactly 7 outside partners x 4 sampled weeks")
    if set(out.partner)!=set(PARTNERS) or set(out.season)!=set(SEASONS):
        raise ValueError("Missing/unexpected partner or season")
    if not out.reported_hours.eq(168).all():raise ValueError("Incomplete observed partner weeks")
    p=out.pivot(index="partner",columns="season",values="mean_net_import_mw").loc[list(PARTNERS),list(SEASONS)]
    fig,ax=plt.subplots(figsize=(12,6.7))
    x=np.arange(len(PARTNERS));w=.19
    colors=("#277da1","#43aa8b","#f8961e","#9b5de5")
    for j,season in enumerate(SEASONS):
        vals=p[season].to_numpy()
        ax.bar(x+(j-1.5)*w, vals, width=w, color=colors[j], label=season.title())
    ax.axhline(0,color="#293241",linewidth=1.4)
    ax.set_xticks(x,PARTNERS)
    ax.set_ylabel("Average reported net import to AZPS (MW)")
    ax.set_title("AZPS exchange by partner: four sampled 2024 weeks")
    ax.legend(ncol=4,loc="upper right")
    ax.grid(axis="y",alpha=.17)
    ax.set_axisbelow(True)
    ax.text(.01,.98,"Above zero = AZPS net IMPORT; below zero = AZPS net EXPORT",
            transform=ax.transAxes,ha="left",va="top",fontsize=9)
    fig.text(.5,.012,"Seven omitted BA partners, 168 hours per week; reported interchange, NOT physical line flow or full seasons.",ha="center",fontsize=9)
    fig.tight_layout(rect=(0,.055,1,1))
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    fig.savefig(output/"azps_partner_exchange_grouped_bars.svg",bbox_inches="tight")
    fig.savefig(output/"azps_partner_exchange_grouped_bars.png",bbox_inches="tight",dpi=180)
    plt.close(fig)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--csv",default="data/verified/seasonal_partner_exchange.csv")
    p.add_argument("--output",default="figures")
    a=p.parse_args()
    draw(a.csv,a.output)
if __name__=="__main__": main()
