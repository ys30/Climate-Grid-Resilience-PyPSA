"""Census state-basemap maps. Proxy positions are NOT actual BA footprints."""
import argparse
from pathlib import Path
from urllib.request import urlretrieve
import zipfile
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import geopandas as gpd

CENSUS="https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_state_500k.zip"
BA={"BPAT":(-122.68,45.52),"CISO":(-119.75,36.17),"AZPS":(-112.07,33.45),"SRP":(-111.83,33.42)}
LINKS=[("CISO","BPAT"),("CISO","AZPS"),("AZPS","SRP")]
# Other partner BA point coordinates are deliberately NOT invented.
SEASONS={"Winter":1491.923,"Spring":971.601,"Summer":950.929,"Autumn":748.869}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",default="figures")
    p.add_argument("--cache",default="data/cache/census")
    a=p.parse_args()
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    cache=Path(a.cache);cache.mkdir(parents=True,exist_ok=True)
    path=cache/"cb_2024_us_state_500k.zip"
    if not path.is_file():urlretrieve(CENSUS,path)
    with zipfile.ZipFile(path) as z:
        z.extractall(cache/"states")
    states=gpd.read_file(next((cache/"states").glob("*.shp")))
    states=states.to_crs(4326)
    states=states[states.STUSPS.isin(["WA","OR","CA","ID","NV","UT","AZ","NM","CO","WY","MT"])]
    def base(ax):
        states.plot(ax=ax,facecolor="#edf2f7",edgecolor="#8192a5",linewidth=.75)
        ax.set_xlim(-125,-104);ax.set_ylim(31,49);ax.set_aspect("equal")
        ax.set_xlabel("Longitude");ax.set_ylabel("Latitude")
        ax.grid(alpha=.15)
    fig,ax=plt.subplots(figsize=(12,8));base(ax)
    for x,y in LINKS:
        a0,b0=BA[x],BA[y]
        ax.plot([a0[0],b0[0]],[a0[1],b0[1]],c="#ea580c",linewidth=2.4,linestyle="--",zorder=3)
    for name,(lon,lat) in BA.items():
        ax.scatter([lon],[lat],s=80,c="#155e9b",edgecolor="white",zorder=4)
        ax.annotate(name,(lon,lat),xytext=(8,10 if name=="AZPS" else -12),textcoords="offset points",weight="bold")
    ax.set_title("Four-BA PyPSA graph on official 2024 US state boundaries")
    fig.text(.5,.015,"US Census 2024 states; points are ERA5 proxies; lines are hypothetical model links, NOT physical lines or BA boundaries.",ha="center",fontsize=9)
    fig.savefig(out/"four_ba_census_states_map.svg",bbox_inches="tight")
    fig.savefig(out/"four_ba_census_states_map.png",bbox_inches="tight",dpi=180)
    plt.close(fig)
    fig,ax=plt.subplots(figsize=(12,8));base(ax)
    az=BA["AZPS"]
    for name in ["CISO","SRP"]:
        pt=BA[name]
        ax.plot([az[0],pt[0]],[az[1],pt[1]],color="#ea580c",linewidth=2.5,linestyle="--",zorder=3)
        ax.scatter([pt[0]],[pt[1]],s=65,color="#155e9b",zorder=4)
        ax.annotate(name,pt,xytext=(7,8),textcoords="offset points")
    ax.scatter([az[0]],[az[1]],s=100,color="#155e9b",zorder=4)
    ax.annotate("AZPS",az,xytext=(7,-16),textcoords="offset points",weight="bold")
    ax.text(-123,44,"7 additional reported partners excluded:\nWALC, LDWP, PNM, TEPC, PACE, WACM, IID",fontsize=11,bbox={"boxstyle":"round","facecolor":"white","alpha":.85})
    ax.set_title("Model coverage vs reported AZPS exchange partners")
    fig.text(.5,.015,"Census state lines only; unmodeled partner locations intentionally omitted to avoid implying unsupported BA coordinates.",ha="center",fontsize=9)
    fig.savefig(out/"azps_boundary_coverage_census_map.svg",bbox_inches="tight")
    fig.savefig(out/"azps_boundary_coverage_census_map.png",bbox_inches="tight",dpi=180)
    plt.close(fig)
    fig,axs=plt.subplots(2,2,figsize=(12,9),sharex=True,sharey=True)
    for ax,(season,mw) in zip(axs.flat,SEASONS.items()):
        base(ax)
        ax.scatter([az[0]],[az[1]],c="#155e9b",s=75,zorder=5)
        ax.annotate("AZPS",(az[0],az[1]),xytext=(5,7),textcoords="offset points")
        ax.set_title(f"{season}: outside net export {mw:,.0f} MW avg")
    fig.suptitle("Four sampled 2024 weeks: reported AZPS net exports to omitted partners",fontsize=14)
    fig.text(.5,.01,"Magnitude describes reported combined BA interchange; NOT a geographic line flow. Four sample weeks only.",ha="center",fontsize=9)
    fig.savefig(out/"azps_four_season_census_maps.svg",bbox_inches="tight")
    fig.savefig(out/"azps_four_season_census_maps.png",bbox_inches="tight",dpi=180)
    plt.close(fig)
if __name__=="__main__":main()
