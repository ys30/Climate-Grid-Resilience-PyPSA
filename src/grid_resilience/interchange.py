"""Audit EIA-930 interchange observations before using them as *calibration*.

Measured exchange is a net-flow observation, NOT a physical thermal transfer
capacity. Do not infer intertie ratings directly from recorded maximum flow.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

BAS = {"CISO", "AZPS", "BPAT"}

def _col(df, candidates):
    lookup = {str(c).lower().strip().replace("_", " "): c for c in df}
    for c in candidates:
        if c.lower().replace("_", " ") in lookup:
            return lookup[c.lower().replace("_", " ")]
    raise ValueError(f"Missing interchange field {candidates}. Found: {list(df.columns)}")

def audit_interchange(path, start, end, out):
    raw = pd.read_csv(path, low_memory=False)
    source = _col(raw, ["Balancing Authority", "Balancing Authority Code", "ba",
                        "balancing_authority_code_eia"])
    neighbor = _col(raw, ["Directly Interconnected Balancing Authority",
                          "Interconnected Balancing Authority", "Interconnected BA",
                          "Directly Interconnected BA", "ba_to", "neighbor"])
    stamp = _col(raw, ["UTC Time", "datetime_utc", "timestamp"])
    value = _col(raw, ["Interchange (MW)", "Interchange", "interchange_mw"])
    frame = raw[[source, neighbor, stamp, value]].copy()
    frame.columns = ["source", "neighbor", "hour_ending_utc", "reported_mw"]
    frame = frame[frame.source.isin(BAS) & frame.neighbor.isin(BAS)]
    frame["timestamp"] = pd.to_datetime(frame.hour_ending_utc, utc=True, errors="coerce") - pd.Timedelta(hours=1)
    frame["reported_mw"] = pd.to_numeric(frame.reported_mw, errors="coerce")
    frame = frame[(frame.timestamp >= pd.Timestamp(start, tz="UTC")) &
                  (frame.timestamp < pd.Timestamp(end, tz="UTC"))]
    if frame.timestamp.isna().any() or frame.reported_mw.isna().any():
        raise ValueError("Invalid timestamp / interchange MW")
    if frame.duplicated(["source", "neighbor", "timestamp"]).any():
        raise ValueError("Duplicate interchange edges; inspect publication revisions")
    forward = frame.rename(columns={"source": "a", "neighbor": "b", "reported_mw": "mw_ab"})
    reverse = frame.rename(columns={"source": "b", "neighbor": "a", "reported_mw": "mw_ba"})
    paired = forward.merge(reverse[["a", "b", "timestamp", "mw_ba"]],
                           on=["a", "b", "timestamp"], how="left", validate="one_to_one")
    paired = paired[paired.a < paired.b].copy()
    paired["opposite_report_discrepancy_mw"] = paired.mw_ab + paired.mw_ba
    edges = paired.groupby(["a", "b"], as_index=False).agg(
        n_observed=("mw_ab", "size"),
        n_reciprocal=("mw_ba", "count"),
        p95_absolute_observed_mw=("mw_ab", lambda x: float(x.abs().quantile(.95))),
        maximum_absolute_observed_mw=("mw_ab", lambda x: float(x.abs().max())),
        max_opposite_discrepancy_mw=("opposite_report_discrepancy_mw",
                                     lambda x: float(x.abs().max()) if x.notna().any() else float("nan")))
    output = Path(out); output.mkdir(parents=True, exist_ok=True)
    paired.to_csv(output / "observed_interchange_pairs.csv", index=False)
    edges.to_csv(output / "observed_interchange_summary.csv", index=False)
    (output / "interchange_provenance.json").write_text(json.dumps({
        "source": "EIA-930 INTERCHANGE six-month file",
        "window_utc": [start, end],
        "metric_interpretation": "observed interchange MW; NOT physical line rating",
        "sign_convention": "as published, reverse reports should approximately cancel",
        "use": "network coverage, consistency and model-vs-observation validation only",
        "important": "absence of CISO/AZPS/BPAT directly reported pairs does not imply no electrical connectivity",
    }, indent=2) + "\n")
    return edges

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--interchange-csv", required=True)
    parser.add_argument("--start", default="2024-07-01")
    parser.add_argument("--end", default="2024-07-08")
    parser.add_argument("--output", default="outputs/interchange_audit")
    a = parser.parse_args()
    print(audit_interchange(a.interchange_csv, a.start, a.end, a.output).to_string(index=False))

if __name__ == "__main__":
    main()
