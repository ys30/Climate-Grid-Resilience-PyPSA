import pandas as pd
import pytest
from grid_resilience.nameplate_audit import compare

def test_inventory_vs_observed_load_audit(tmp_path):
    cap = tmp_path / "capacity.csv"
    demand = tmp_path / "demand.csv"
    pd.DataFrame([{"ba": b, "technology": "thermal", "capacity_mw": 200}
                  for b in ("CISO", "AZPS", "BPAT")]).to_csv(cap, index=False)
    pd.DataFrame([
        {"timestamp": "2024-07-01T00:00:00Z", "CISO": 100, "AZPS": 120, "BPAT": 80},
        {"timestamp": "2024-07-01T01:00:00Z", "CISO": 150, "AZPS": 100, "BPAT": 90},
    ]).to_csv(demand, index=False)
    result = compare(cap, demand, "2024-07-01", "2024-07-01 02:00", tmp_path / "out")
    assert len(result) == 3
    assert result.loc[result.ba.eq("CISO"), "nameplate_to_peak_load_ratio"].iloc[0] == pytest.approx(200/150)
    assert (tmp_path / "out" / "comparison_provenance.json").exists()
