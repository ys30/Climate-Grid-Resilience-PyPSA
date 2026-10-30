"""Quantify how much diagnostic geometry repairs alter historical HIFLD BA features.

Historical 2018 reference only. Does not generate a 2024 BA map.
"""
import argparse
import json
from pathlib import Path
import geopandas as gpd
from shapely.geometry import shape
from shapely.validation import explain_validity, make_valid
from shapely.ops import unary_union
from .ba_polygon_source_audit import SOURCES, CANDIDATES, request

def polygonal(g):
    parts=[]
    def collect(x):
        if x.geom_type in ("Polygon","MultiPolygon"):parts.append(x)
        elif hasattr(x,"geoms"):
            for item in x.geoms:collect(item)
    collect(g)
    return unary_union(parts) if parts else None

def audit(output):
    rows=[]
    url=SOURCES["hifld_control_areas"]+"/query"
    for name,code in CANDIDATES.items():
        data=request(url,{"f":"geojson","where":"NAME = '"+name.replace("'","''")+"'",
                          "outFields":"NAME,YEAR","outSR":"4326","returnGeometry":"true"})
        features=data.get("features",[])
        if len(features)!=1:raise ValueError(f"{code}: {len(features)} features")
        raw=shape(features[0]["geometry"])
        repaired=polygonal(make_valid(raw))
        if repaired is None or not repaired.is_valid or repaired.is_empty:
            raise ValueError(f"{code}: repaired polygon not valid")
        def area(g):
            return float(gpd.GeoSeries([g],crs=4326).to_crs(5070).area.iloc[0]/1e6)
        raw_area=area(raw);new_area=area(repaired)
        # Symmetric difference requires valid inputs; we use a zero-distance buffer
        # ONLY as a comparison geometry, not as truth.
        alternative=polygonal(raw.buffer(0))
        if alternative is None or alternative.is_empty:
            raise ValueError(f"{code}: buffer comparison geometry unavailable")
        symmetric=area(alternative.symmetric_difference(repaired))
        rows.append({"candidate":code,"original_valid":bool(raw.is_valid),
            "validity_reason":explain_validity(raw),"original_area_sq_km":round(raw_area,3),
            "make_valid_area_sq_km":round(new_area,3),
            "make_valid_area_change_pct":round((new_area/raw_area-1)*100,4),
            "buffer0_area_sq_km":round(area(alternative),3),
            "buffer0_vs_makevalid_symmetric_difference_sq_km":round(symmetric,3),
            "material_area_change_gt_1pct":abs(new_area/raw_area-1)>.01,
            "historical_source_year":2018,"certified_2024_boundary":False})
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    (out/"repair_topology_comparison.json").write_text(json.dumps(rows,indent=2)+"\n")
    print(json.dumps(rows,indent=2))
def main():
    p=argparse.ArgumentParser();p.add_argument("--output",required=True);args=p.parse_args()
    audit(args.output)
if __name__=="__main__":main()
