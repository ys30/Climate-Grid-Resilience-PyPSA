import pandas as pd
import pytest
from grid_resilience.azps_transfer_sensitivity import run_sensitivity
from grid_resilience.western_us import BAS

def test_azps_transfer_assumption_changes_modeled_unserved_energy():
    pytest.importorskip("pypsa")
    idx = pd.date_range("2024-07-01", periods=3, freq="h", tz="UTC")
    demand = pd.DataFrame({ba: [100., 100., 100.] for ba in BAS}, index=idx)
    weather = {
        ba: pd.DataFrame({
            "temperature_2m": [28., 29., 30.],
            "wind_speed_100m": [5., 5., 5.],
            "shortwave_radiation": [0., 0., 0.],
        }, index=idx) for ba in BAS
    }
    capacities = {
        ("CISO", "thermal"): 300.,
        ("AZPS", "thermal"): 20.,
        ("BPAT", "thermal"): 100.,
    }
    result = run_sensitivity(demand, weather, capacities, fractions=(0.0, 0.5))
    assert len(result) == 6
    baseline = result.loc[(result.ba == "AZPS") & (result.intertie_fraction_assumed == 0)].modeled_unserved_mwh.iloc[0]
    augmented = result.loc[(result.ba == "AZPS") & (result.intertie_fraction_assumed == 0.5)].modeled_unserved_mwh.iloc[0]
    assert augmented < baseline

def test_fraction_outside_bounds_rejected():
    with pytest.raises(ValueError, match="fraction"):
        run_sensitivity(None, None, {}, fractions=(1.5,))
