import pandas as pd
import pytest
from grid_resilience.western_us import BAS, SCENARIOS, load_eia930, build_model

def test_eia_hour_ending_and_completeness(tmp_path):
    hours = pd.date_range("2024-07-01", periods=3, freq="h", tz="UTC")
    rows = [
        {"Balancing Authority": ba, "UTC Time": (t + pd.Timedelta(hours=1)).isoformat(),
         "Demand (MW)": 1000 + i}
        for ba in BAS for i, t in enumerate(hours)
    ]
    path = tmp_path / "eia.csv"
    pd.DataFrame(rows).to_csv(path, index=False)
    demand = load_eia930(path, "2024-07-01", "2024-07-01 03:00")
    assert demand.shape == (3, 3)
    assert demand.index[0] == hours[0]
    assert demand.loc[hours[2], "CISO"] == 1002

def test_eia_missing_hour_rejected(tmp_path):
    path = tmp_path / "eia.csv"
    pd.DataFrame([{"Balancing Authority": ba, "UTC Time": "2024-07-01T01:00:00Z",
                   "Demand (MW)": 1000} for ba in BAS]).to_csv(path, index=False)
    with pytest.raises(ValueError, match="Incomplete"):
        load_eia930(path, "2024-07-01", "2024-07-01 02:00")

def test_synthetic_fixture_builds_valid_weather_driven_network():
    pytest.importorskip("pypsa")
    idx = pd.date_range("2024-07-01", periods=4, freq="h", tz="UTC")
    demand = pd.DataFrame({ba: [100, 105, 110, 120] for ba in BAS}, index=idx)
    weather = {ba: pd.DataFrame({"temperature_2m": [30, 36, 38, 32],
                                 "wind_speed_100m": [5, 6, 7, 5],
                                 "shortwave_radiation": [0, 200, 500, 0]},
                                index=idx) for ba in BAS}
    n = build_model(demand, weather, "compound_heat_wind_derating")
    assert len(n.snapshots) == 4
    assert len(n.buses) == 3
    assert len(n.links) == 2
    assert len(n.generators) == 12
    assert n.loads_t.p_set.shape == (4, 3)
    assert set(SCENARIOS) == {"observed_weather", "heat_plus_4c", "compound_heat_wind_derating"}
