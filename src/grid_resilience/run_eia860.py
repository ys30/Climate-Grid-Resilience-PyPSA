"""Run official EIA-860 2024 ingestion and write an explicit audit."""
from pathlib import Path
import argparse
import json
from .download_eia860 import obtain
from .eia860 import export_860

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", default="data/external/eia860_2024")
    parser.add_argument("--output", default="data/processed/eia860")
    args = parser.parse_args()
    manifest = obtain(args.raw)
    files = manifest["extraction"]
    caps = export_860(files["generators"], files["plants"], args.output, year=2024)
    audit = {"year": 2024, "n_ba_technology": int(len(caps)),
             "capacity_totals_mw": {str(k): float(v) for k, v in
                 caps.groupby("ba").capacity_mw.sum().items()},
             "limitations": "EIA year-end nameplate; weather derates, hourly outages, imports and storage unvalidated"}
    out = Path(args.output)
    (out / "inventory_audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    print(json.dumps(audit, indent=2))

if __name__ == "__main__":
    main()
