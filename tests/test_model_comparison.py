import pandas as pd
import pytest
from grid_resilience.model_comparison import compare

def _metrics(value):
    return pd.DataFrame([{
        "scenario": scenario, "ba": ba,
        "unserved_energy_mwh": value,
        "peak_shortfall_mw": value/2,
        "shortage_hours": 1,
    } for scenario in ("observed_weather", "heat_plus_4c")
      for ba in ("CISO", "AZPS", "BPAT")])

def test_matching_scenarios_compare(tmp_path):
    a, b = tmp_path / "a.csv", tmp_path / "b.csv"
    _metrics(10).to_csv(a, index=False)
    _metrics(14).to_csv(b, index=False)
    rows, summary = compare(a, b, tmp_path / "out")
    assert len(rows) == 6
    assert (rows.unserved_energy_mwh_delta == 4).all()
    assert (summary.unserved_energy_mwh_delta == 12).all()
    assert (tmp_path / "out" / "comparison_provenance.json").exists()

def test_mismatched_region_coverage_rejected(tmp_path):
    a, b = tmp_path / "a.csv", tmp_path / "b.csv"
    _metrics(10).to_csv(a, index=False)
    _metrics(14).iloc[:-1].to_csv(b, index=False)
    with pytest.raises(ValueError, match="coverage differ"):
        compare(a, b, tmp_path / "out")
