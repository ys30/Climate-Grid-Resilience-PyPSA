import pandas as pd
from grid_resilience.report import summarize

def test_system_summary_distinguishes_ba_hours_from_system_hours(tmp_path):
    metrics = pd.DataFrame([
        {"scenario":"baseline","ba":"CISO","unserved_energy_mwh":10,
         "peak_shortfall_mw":10,"shortage_hours":1},
        {"scenario":"baseline","ba":"AZPS","unserved_energy_mwh":5,
         "peak_shortfall_mw":5,"shortage_hours":1},
    ])
    hourly = pd.DataFrame([
        {"scenario":"baseline","ba":"CISO","timestamp":"2024-07-01T00:00Z","unserved_mw":10},
        {"scenario":"baseline","ba":"AZPS","timestamp":"2024-07-01T00:00Z","unserved_mw":5},
    ])
    metrics.to_csv(tmp_path / "metrics.csv", index=False)
    hourly.to_csv(tmp_path / "hourly_unserved.csv", index=False)
    out = summarize(tmp_path)
    assert out.iloc[0].unserved_energy_mwh == 15
    assert out.iloc[0].system_peak_shortfall_mw == 15
    assert out.iloc[0].system_shortage_hours == 1
    assert out.iloc[0].ba_shortage_hours == 2
    assert (tmp_path / "modeled_unserved_energy.png").exists()
