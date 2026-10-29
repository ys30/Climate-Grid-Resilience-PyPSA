"""Fetch hourly EIA API v2 RTO demand into a validated model-ready CSV.

Requires EIA_API_KEY environment variable. No key is logged, saved or echoed.
EIA API periods are UTC hour-beginning: no hour-ending shift is applied here.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd

ENDPOINT = "https://api.eia.gov/v2/electricity/rto/region-data/data/"
BAS = ("CISO", "AZPS", "BPAT")


def parse_rto(records, start, end, bas=BAS):
    data = pd.DataFrame(records)
    needed = {"period", "respondent", "type", "value"}
    if not needed.issubset(data):
        raise ValueError(f"EIA API response missing columns {sorted(needed - set(data))}")
    data = data.loc[data["type"].eq("D") & data.respondent.isin(bas)].copy()
    data["timestamp"] = pd.to_datetime(data.period, utc=True, errors="coerce")
    data["demand_mw"] = pd.to_numeric(data.value, errors="coerce")
    if data.timestamp.isna().any() or data.demand_mw.isna().any() or (data.demand_mw <= 0).any():
        raise ValueError("Invalid EIA demand or UTC time")
    if data.duplicated(["timestamp", "respondent"]).any():
        raise ValueError("Duplicated EIA respondent/time")
    idx = pd.date_range(pd.Timestamp(start, tz="UTC"), pd.Timestamp(end, tz="UTC"),
                        freq="h", inclusive="left")
    out = data.pivot(index="timestamp", columns="respondent", values="demand_mw")
    out = out.reindex(index=idx, columns=list(bas))
    if out.isna().any().any():
        raise ValueError(f"Missing BA/hour observations: {out.isna().sum().to_dict()}")
    out.columns.name = None  # stable CSV round-trip schema
    return out.astype(float)


def _get(params, key, opener=urlopen):
    url = ENDPOINT + "?" + urlencode({**params, "api_key": key}, doseq=True)
    # Never include URL or exception body in messages: they might contain api_key.
    try:
        with opener(Request(url, headers={"Accept": "application/json"}), timeout=45) as response:
            payload = json.load(response)
    except Exception as exc:
        raise RuntimeError("EIA API request failed; check network, key, and EIA status") from None
    if not isinstance(payload, dict) or "response" not in payload or "data" not in payload["response"]:
        raise RuntimeError("Unexpected EIA API response; verify route and facets")
    return payload["response"]


def fetch_rto(start, end, output, key=None, page_size=5000, opener=urlopen, bas=BAS):
    bas = tuple(bas)
    if not bas or len(set(bas)) != len(bas) or any(not str(b).isalnum() for b in bas):
        raise ValueError("Invalid or duplicate BA identifiers")
    key = key or os.environ.get("EIA_API_KEY")
    if not key:
        raise RuntimeError("Set EIA_API_KEY in environment or GitHub Actions secrets")
    if not 1 <= page_size <= 5000:
        raise ValueError("EIA page_size must be 1..5000")
    a = pd.Timestamp(start)
    b = pd.Timestamp(end)
    if a.tzinfo is not None or b.tzinfo is not None or a >= b:
        raise ValueError("Use naive UTC start/end with end > start")
    end_hour = (b - pd.Timedelta(hours=1)).strftime("%Y-%m-%dT%H")
    params = {
        "frequency": "hourly",
        "data[0]": "value",
        "facets[type][]": ["D"],
        "facets[respondent][]": list(bas),
        "start": a.strftime("%Y-%m-%dT%H"),
        "end": end_hour,
        "sort[0][column]": "period",
        "sort[0][direction]": "asc",
        "length": str(page_size),
    }
    records = []
    offset = 0
    while True:
        result = _get({**params, "offset": str(offset)}, key, opener)
        total = int(result.get("total", 0))
        batch = result["data"]
        if not batch:
            break
        records.extend(batch)
        offset += len(batch)
        if offset >= total:
            break
        if len(records) > 200_000:
            raise RuntimeError("Unexpected oversized EIA download; restrict date window")
    demand = parse_rto(records, start, end, bas=bas)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    demand.rename_axis("timestamp").to_csv(output)
    (output.parent / (output.stem + "_provenance.json")).write_text(
        json.dumps({"source": ENDPOINT, "start_utc": start, "end_exclusive_utc": end,
                    "BA_codes": list(bas), "series_type": "D",
                    "timestamp_convention": "EIA API hourly period starts; UTC",
                    "rows": len(records), "key_saved": False}, indent=2) + "\n")
    return demand


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="2024-07-01")
    parser.add_argument("--end", default="2024-07-08")
    parser.add_argument("--output", default="data/processed/eia930_api_demand.csv")
    parser.add_argument("--bas", nargs="+", default=list(BAS), help="BA respondents (e.g. CISO AZPS BPAT SRP)")
    args = parser.parse_args()
    df = fetch_rto(args.start, args.end, args.output, bas=args.bas)
    print(f"Validated {len(df)} hourly rows for {len(args.bas)} BAs: {args.output}")


if __name__ == "__main__":
    main()
