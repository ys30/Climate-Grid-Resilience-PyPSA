import pandas as pd
from grid_resilience.diagnostics import diagnose

def test_shortfall_baseline_audit(tmp_path):
    input_file = tmp_path / "hourly.csv"
    pd.DataFrame([
      {"scenario": "observed_weather", "ba": "CISO", "timestamp": "2024-07-01T00:00Z", "unserved_mw": 5.0},
      {"scenario": "observed_weather", "ba": "AZPS", "timestamp": "2024-07-01T00:00Z", "unserved_mw": 2.0},
      {"scenario": "observed_weather", "ba": "CISO", "timestamp": "2024-07-01T01:00Z", "unserved_mw": 0.0},
      {"scenario": "observed_weather", "ba": "AZPS", "timestamp": "2024-07-01T01:00Z", "unserved_mw": 0.0},
    ]).to_csv(input_file, index=False)
    regions, peak = diagnose(input_file, tmp_path / "out")
    assert regions.modeled_unserved_energy_mwh.sum() == 7
    assert len(peak) == 1
    assert peak.unserved_mw.iloc[0] == 7
