"""Compare screening outputs from synthetic and partial-nameplate dispatch models.

Both experiments use the same observations and weather scenarios. The delta
isolates model-input sensitivity, not observed outage risk.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import pandas as pd

KEYS = ["scenario", "ba"]
METRICS = ["unserved_energy_mwh", "peak_shortfall_mw", "shortage_hours"]

def compare(synthetic_csv, nameplate_csv, output):
    left = pd.read_csv(synthetic_csv)
    right = pd.read_csv(nameplate_csv)
    for label, frame in (("synthetic", left), ("partial_nameplate", right)):
        needed = set(KEYS + METRICS)
        if not needed.issubset(frame.columns):
            raise ValueError(f"{label} missing columns: {sorted(needed - set(frame.columns))}")
        if frame.duplicated(KEYS).any() or frame[KEYS].isna().any().any():
            raise ValueError(f"{label} has duplicate or null scenario/BA keys")
        for metric in METRICS:
            frame[metric] = pd.to_numeric(frame[metric], errors="raise")
            if frame[metric].isna().any() or (frame[metric] < 0).any():
                raise ValueError(f"{label} invalid metric: {metric}")
    joined = left.merge(right, on=KEYS, how="outer",
                        suffixes=("_synthetic", "_partial_nameplate"),
                        validate="one_to_one", indicator=True)
    if not joined._merge.eq("both").all():
        raise ValueError("Scenarios/BA coverage differ between experiments")
    joined = joined.drop(columns="_merge")
    for metric in METRICS:
        joined[metric + "_delta"] = (joined[metric + "_partial_nameplate"]
                                     - joined[metric + "_synthetic"])
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    joined.sort_values(KEYS).to_csv(output / "model_input_comparison.csv", index=False)
    summary = joined.groupby("scenario", as_index=False)[[
        "unserved_energy_mwh_synthetic",
        "unserved_energy_mwh_partial_nameplate",
        "unserved_energy_mwh_delta"
    ]].sum()
    summary.to_csv(output / "scenario_comparison.csv", index=False)
    (output / "comparison_provenance.json").write_text(json.dumps({
        "synthetic_metrics": str(synthetic_csv),
        "partial_nameplate_metrics": str(nameplate_csv),
        "meaning": "difference in simulated shortfall under different assumed fleets, NOT estimated real outages",
        "limitations": [
            "EIA-860 2024 year-end inventory is not July 2024 available power",
            "Battery storage and unclassified generators are excluded from partial-nameplate model",
            "Both models retain hypothetical transfers and weather availability coefficients",
            "Comparison is deterministic screening, not a probabilistic EENS estimate"
        ]
    }, indent=2) + "\n")
    return joined, summary

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--synthetic", required=True)
    p.add_argument("--partial-nameplate", required=True)
    p.add_argument("--output", default="outputs/model_comparison")
    a = p.parse_args()
    _, summary = compare(a.synthetic, a.partial_nameplate, a.output)
    print(summary.to_string(index=False))

if __name__ == "__main__":
    main()
