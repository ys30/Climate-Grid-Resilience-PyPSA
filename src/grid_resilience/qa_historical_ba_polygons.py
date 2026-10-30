"""Quality-check HIFLD historical control-area polygons; NOT a 2024 BA boundary product."""
import argparse
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen
import geopandas as gpd
from shapely.geometry import shape
from shapely.validation import explain_validity, make_valid
from shapely.ops import unary_union
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
        original_valid=bool(geometry.is_valid)
        diagnostic=explain_validity(geometry)
        if geometry.is_empty:raise ValueError(f"{code}: empty polygon")
        repaired=geometry if original_valid else make_valid(geometry)
        parts=[]
        def collect(g):
            if g.geom_type in ("Polygon","MultiPolygon"): parts.append(g)
            elif hasattr(g,"geoms"):
                for piece in g.geoms: collect(piece)
        collect(repaired)
        repaired_poly=unary_union(parts) if parts else None
        repair_ok=bool(repaired_poly is not None and not repaired_poly.is_empty and repaired_poly.is_valid)
        if not repair_ok:raise ValueError(f"{code}: diagnostic repair failed: {diagnostic}")
        if geometry.geom_type not in ("Polygon","MultiPolygon"):raise ValueError(f"{code}: not polygon geometry")
        if int(prop["YEAR"])!=2018:raise ValueError(f"{code}: unknown vintage")
        minx,miny,maxx,maxy=geometry.bounds
        if not (-180<minx<maxx<-60 and 15<miny<maxy<75):
            raise ValueError(f"{code}: implausible continental bounds")
        if original_valid:
            features.append({"type":"Feature","geometry":item["geometry"],"properties":{"code_candidate":code,"hifld_name":name,"year":2018,"original_valid":True}})
        rows.append({"candidate_code":code,"name":name,"original_valid":original_valid,"validity_reason":diagnostic,
                     "diagnostic_repair_valid":repair_ok,
                     "diagnostic_repair_area_sqkm":round(gpd.GeoSeries([repaired_poly],crs=4326).to_crs(5070).area.iloc[0]/1e6,1),
                     "included_in_source_geometry_geojson":original_valid,"geom_type":geometry.geom_type,
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
