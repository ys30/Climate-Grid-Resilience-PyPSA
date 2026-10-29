"""Select an explicitly declared BA subset from audited EIA-860 capacities.

Never silently discard extra regions: subset selection is an explicit model
comparison operation, and requires all named BA codes to exist.
"""
import argparse
import json
from pathlib import Path
import pandas as pd
from .capacity_adapter import load_eia860_capacities

def select(source, output, bas):
    if not bas or len(set(bas)) != len(bas):
        raise ValueError("Expected unique nonempty BA list")
    source_df = pd.read_csv(source)
    all_bas = tuple(sorted(source_df["ba"].dropna().unique()))
    load_eia860_capacities(source, required_bas=all_bas)
    missing = set(bas) - set(all_bas)
    if missing:
        raise ValueError(f"BA subset missing in source: {sorted(missing)}")
    subset = source_df[source_df.ba.isin(bas)].copy()
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    subset.to_csv(output, index=False)
    load_eia860_capacities(output, required_bas=bas)
    metadata = {
        "source_file": str(source), "all_source_bas": list(all_bas),
        "selected_bas": list(bas), "excluded_bas": sorted(set(all_bas)-set(bas)),
        "reason": "Explicit shared-region subset for matched three-vs-four BA model comparison"
    }
    output.with_suffix(".provenance.json").write_text(json.dumps(metadata,indent=2)+"\n")
    return subset

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--output",required=True)
    p.add_argument("--bas",nargs="+",required=True)
    a=p.parse_args()
    print(select(a.source,a.output,tuple(a.bas)).groupby("ba").capacity_mw.sum())

if __name__ == "__main__":
    main()
