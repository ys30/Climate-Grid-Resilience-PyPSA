"""Inventory candidate authoritative BA polygon feature services without drawing unverified geography.

This explicitly checks source schema and coverage but does NOT assume historical
2024 validity, consistent territory polygons, or physical transmission paths.
"""
import argparse
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

SOURCES={
  "hifld_control_areas":"https://services5.arcgis.com/HDRa0B57OVrv2E1q/ArcGIS/rest/services/Control_Areas/FeatureServer/0",
  "california_ba":"https://services3.arcgis.com/bWPjFyq029ChCGur/arcgis/rest/services/Balancing_Authority/FeatureServer/0",
}
REQUIRED={"CISO","AZPS","BPAT","SRP","WALC","LDWP","PNM","TEPC","PACE","WACM","IID"}

CANDIDATES={
  "ARIZONA PUBLIC SERVICE COMPANY":"AZPS",
  "CALIFORNIA INDEPENDENT SYSTEM OPERATOR":"CISO",
  "BONNEVILLE POWER ADMINISTRATION":"BPAT",
  "SALT RIVER PROJECT":"SRP",
  "LOS ANGELES DEPARTMENT OF WATER AND POWER":"LDWP",
  "PUBLIC SERVICE COMPANY OF NEW MEXICO":"PNM",
  "TUCSON ELECTRIC POWER COMPANY":"TEPC",
  "PACIFICORP - EAST":"PACE",
  "IMPERIAL IRRIGATION DISTRICT":"IID",
  # Candidate organizational names require independent BA identification.
  "WESTERN AREA POWER ADMINISTRATION - DESERT SOUTHWEST REGION":"WALC",
  "WESTERN AREA POWER ADMINISTRATION - ROCKY MOUNTAIN REGION":"WACM",
}

def request(url,params):
    address=url+"?"+urlencode(params)
    with urlopen(address,timeout=50) as response:
        obj=json.load(response)
    if "error" in obj:
        raise RuntimeError(f"ArcGIS error: {obj['error'].get('message')}")
    return obj

def inventory():
    result={}
    for source,url in SOURCES.items():
        layer=request(url,{"f":"json"})
        fields=[f["name"] for f in layer.get("fields",[])]
        name_field=next((x for x in ("BA_CODE","BA_ID","NAME","BA_NAME","CONTROL_AR") if x in fields),None)
        if layer.get("geometryType")!="esriGeometryPolygon":
            raise ValueError(f"{source}: not polygon geometry")
        if not name_field:
            raise ValueError(f"{source}: no BA name/code field; manually review {fields}")
        ids=request(url+"/query",{"f":"json","where":"1=1","returnGeometry":"false",
            "outFields":name_field,"returnDistinctValues":"true"})
        raw=sorted({str(f.get("attributes",{}).get(name_field,"")).strip()
                    for f in ids.get("features",[]) if f.get("attributes",{}).get(name_field)})
        metadata=[]
        if source=="hifld_control_areas":
            selected=list(CANDIDATES)
            for name in selected:
                escaped=name.replace("'","''")
                match=request(url+"/query",{"f":"json","where":f"NAME = '{escaped}'",
                    "returnGeometry":"false","outFields":"NAME,SOURCE,SOURCEDATE,VAL_DATE,YEAR,VAL_METHOD"})
                attrs=[f.get("attributes",{}) for f in match.get("features",[])]
                metadata.append({"requested_code":CANDIDATES[name],"name":name,
                    "matched_features":len(attrs),"feature_metadata":attrs,
                    "mapping_status":"candidate_not_2024_verified"})
        result[source]={
          "candidate_feature_metadata":metadata,
          "source":url,
          "name_field":name_field,
          "schema_fields":fields,
          "distinct_values":raw,
          "exact_code_matches":sorted(set(raw)&REQUIRED),
          "missing_exact_codes":sorted(REQUIRED-set(raw)),
          "note":"No geographic features published; exact code checks insufficient to prove BA mapping, polygon integrity, or 2024 temporal alignment."
        }
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",default="outputs/ba_polygon_source_audit")
    args=p.parse_args()
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    findings=inventory()
    (out/"ba_source_inventory.json").write_text(json.dumps(findings,indent=2)+"\n")
    for name,row in findings.items():
        print(name,"field",row["name_field"],"exact matches",row["exact_code_matches"],
              "missing",row["missing_exact_codes"])
if __name__=="__main__":
    main()
