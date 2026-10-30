"""Data-derived seasonal AZPS partner-exchange heatmap (NO invented BA polygons)."""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .azps_seasonal_boundary import WINDOWS

def build(root, output):
    rows=[]
    for season in WINDOWS:
        p=Path(root)/season/"azps_boundary_neighbors.csv"
        df=pd.read_csv(p)
        for col in ("to_ba","modeled_neighbor","mean_net_import_mw","reported_hours"):
            if col not in df:raise ValueError(f"{season}: missing {col}")
        if df.to_ba.duplicated().any():raise ValueError(f"{season}: duplicate partners")
        if (pd.to_numeric(df.reported_hours)<=0).any():raise ValueError("invalid hours")
        for _,r in df.iterrows():
            rows.append({"season":season,"partner":r.to_ba,
                "mean_net_import_mw":float(r.mean_net_import_mw),
                "reported_hours":int(r.reported_hours),
                "modeled":str(r.modeled_neighbor).lower()=="true"})
    data=pd.DataFrame(rows)
    if data.empty:raise ValueError("No partner observations")
    outside=data.loc[~data.modeled].copy()
    if outside.empty:raise ValueError("No external partners")
    labels=list(WINDOWS)
    partners=sorted(outside.partner.unique())
    matrix=outside.pivot(index="partner",columns="season",values="mean_net_import_mw").reindex(index=partners,columns=labels)
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    data.to_csv(output/"seasonal_partner_exchange.csv",index=False)
    fig,ax=plt.subplots(figsize=(10,6.5))
    maxabs=max(float(np.nanmax(np.abs(matrix.to_numpy(dtype=float)))),1.)
    im=ax.imshow(np.ma.masked_invalid(matrix.values),cmap="RdBu",vmin=-maxabs,vmax=maxabs,aspect="auto")
    ax.set_xticks(range(len(labels)),[x.title() for x in labels])
    ax.set_yticks(range(len(partners)),partners)
    for i in range(len(partners)):
        for j in range(len(labels)):
            v=matrix.iloc[i,j]
            text="N/A" if pd.isna(v) else f"{v:+,.0f}"
            ax.text(j,i,text,ha="center",va="center",fontsize=10,
                    color="white" if pd.notna(v) and abs(v)>maxabs*.6 else "#111827")
    ax.set_title("AZPS reported exchange by omitted BA partner, 2024 sampled weeks")
    cb=fig.colorbar(im,ax=ax,shrink=.75)
    cb.set_label("Mean net import to AZPS (MW): + import / - export")
    fig.text(.5,.015,"Individual directional EIA-930 BA reports; NOT physical line flow or BA boundaries. Four sampled weeks only.",ha="center",fontsize=9)
    fig.tight_layout(rect=[0,.045,1,1])
    fig.savefig(output/"azps_partner_exchange_heatmap.svg",bbox_inches="tight")
    fig.savefig(output/"azps_partner_exchange_heatmap.png",bbox_inches="tight",dpi=180)
    plt.close(fig)
    return data

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    print(build(a.root,a.output).to_string(index=False))
if __name__=="__main__":main()
