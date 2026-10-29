"""Use EIA-860 nameplate capacities in the PyPSA prototype; explicit availability assumptions remain."""
from pathlib import Path
import pandas as pd

def load_eia860_capacities(path, required_bas=("CISO", "AZPS", "BPAT")):
    df = pd.read_csv(path)
    if not {"ba", "technology", "capacity_mw"}.issubset(df):
        raise ValueError("Required columns: ba, technology, capacity_mw")
    if df.duplicated(["ba", "technology"]).any():
        raise ValueError("Duplicate BA-technology capacities")
    df.capacity_mw = pd.to_numeric(df.capacity_mw, errors="raise")
    if df.capacity_mw.isna().any() or (df.capacity_mw < 0).any():
        raise ValueError("Nonnegative numeric capacities required")
    absent = set(required_bas) - set(df.ba)
    if absent:
        raise ValueError(f"EIA-860 capacity lacks required BA: {sorted(absent)}")
    return {(str(r.ba), str(r.technology)): float(r.capacity_mw) for r in df.itertuples()}
