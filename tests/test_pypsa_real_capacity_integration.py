"""Integration checks ensuring EIA nameplate is honored in PyPSA models.

No external weather download is needed. These are structural model tests, not
validation of real-world generator availability.
"""
import pandas as pd
import pytest
from grid_resilience.western_us import BAS, build_model

def _fixtures():
    idx = pd.date_range("2024-07-01", periods=3, freq="h", tz="UTC")
    demand = pd.DataFrame({ba: [100, 110, 105] for ba in BAS}, index=idx)
    weather = {
        ba: pd.DataFrame({
            "temperature_2m": [30., 37., 34.],
            "wind_speed_100m": [4., 6., 8.],
            "shortwave_radiation": [0., 700., 200.],
        }, index=idx) for ba in BAS
    }
    return demand, weather

def test_actual_capacity_path_never_uses_synthetic_capacity_mix():
    pytest.importorskip("pypsa")
    demand, weather = _fixtures()
    capacities = {
        ("CISO", "thermal"): 170., ("CISO", "wind"): 45.,
        ("CISO", "solar"): 30., ("CISO", "hydro"): 28.,
        ("AZPS", "thermal"): 85., ("AZPS", "solar"): 60.,
        ("BPAT", "hydro"): 210., ("BPAT", "wind"): 33.,
        ("BPAT", "nuclear"): 15.,
    }
    n = build_model(demand, weather, "observed_weather", capacities=capacities)
    for (ba, tech), value in capacities.items():
        assert n.generators.at[f"{ba}_{tech}", "p_nom"] == pytest.approx(value)
    assert n.generators.at["CISO_thermal", "p_nom"] != pytest.approx(110*1.18*.7)
    assert n.generators.at["AZPS_wind", "p_nom"] == 0
    assert not any("storage" in gen for gen in n.generators.index)
    assert len(n.snapshots) == 3

def test_synthetic_reference_and_inventory_have_different_generator_mw():
    pytest.importorskip("pypsa")
    demand, weather = _fixtures()
    n_ref = build_model(demand, weather, "observed_weather")
    n_data = build_model(demand, weather, "observed_weather",
        capacities={(ba, "thermal"): 40. for ba in BAS})
    assert n_ref.generators.at["CISO_thermal", "p_nom"] > 40
    assert n_data.generators.at["CISO_thermal", "p_nom"] == 40
