"""Quality-check HIFLD historical control-area polygons; NOT a 2024 BA boundary product."""
import argparse
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen
import geopandas as gpd
from shapely.geometry import shape
from .ba_polygon_source_audit import SOURCES,CANDIDATES,request

def verify(output):
    url=SOURCES["hifld_control_areas"]
    rows=[]
    features=[]
    for name,code in CANDIDATES.items():
        safe=name.replace("'","''")
        obj=request(url+"/query",{"f":"geojson","where":f"NAME = '{safe}'","outFields":"NAME,YEAR,SOURCE,SOURCEDATE,VAL_DATE","returnGeometry":"true","outSR":"4326"})
        items=obj.get("features",[])
        if len(items)!=1:raise ValueError(f"{code}: expected one polygon; got {len(items)}")
        item=items[0];geometry=shape(item["geometry"])
        prop=item["properties"]
        if not geometry.is_valid or geometry.is_empty:raise ValueError(f"{code}: invalid/empty polygon")
        if geometry.geom_type not in ("Polygon","MultiPolygon"):raise ValueError(f"{code}: not polygon geometry")
        if int(prop["YEAR"])!=2018:raise ValueError(f"{code}: unknown vintage")
        minx,miny,maxx,maxy=geometry.bounds
        if not (-180<minx<maxx<-60 and 15<miny<maxy<75):
            raise ValueError(f"{code}: implausible continental bounds")
        features.append({"type":"Feature","geometry":item["geometry"],"properties":{"code_candidate":code,"hifld_name":name,"year":2018}})
        rows.append({"candidate_code":code,"name":name,"valid":True,"geom_type":geometry.geom_type,
                     "area_sqkm_equalarea":round(gpd.GeoSeries([geometry],crs=4326).to_crs(5070).area.iloc[0]/1e6,1),
                     "bbox_lonlat":[round(z,4) for z in geometry.bounds],
                     "record_year":2018,"is_2024_verified":False})
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    (out/"historical_control_areas_2018_candidates.geojson").write_text(json.dumps({"type":"FeatureCollection","features":features}))
    (out/"historical_polygon_geometry_qa.json").write_text(json.dumps(rows,indent=2)+"\n")
    print(json.dumps(rows,indent=2))
def main():
    p=argparse.ArgumentParser();p.add_argument("--output",required=True);args=p.parse_args()
    verify(args.output)
if __name__=="__main__":main()
