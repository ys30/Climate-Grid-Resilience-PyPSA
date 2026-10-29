import pandas as pd
import pytest
from grid_resilience.srp_flow_validation import compare
from grid_resilience.four_ba import FOUR_BAS

def test_flow_sign_and_zero_link_behavior():
    idx=pd.date_range("2024-07-01",periods=2,freq="h",tz="UTC")
    demand=pd.DataFrame({ba:[100.,100.] for ba in FOUR_BAS},index=idx)
    weather={ba:pd.DataFrame({"temperature_2m":[25.,25.],
                              "wind_speed_100m":[5.,5.],
                              "shortwave_radiation":[0.,0.]},index=idx) for ba in FOUR_BAS}
    caps={(ba,"thermal"):200. for ba in FOUR_BAS}
    obs=pd.DataFrame({"timestamp":idx,"azps_imports_from_srp_mw":[20.,20.]})
    summary,hourly=compare(demand,weather,caps,obs,fractions=(0.,))
    assert summary.iloc[0].mean_modeled_srp_to_azps_mw==pytest.approx(0,abs=1e-5)
    assert summary.iloc[0].mae_mw==pytest.approx(20,abs=1e-5)
    assert len(hourly)==2

def test_incomplete_observed_exchange_rejected():
    idx=pd.date_range("2024-07-01",periods=2,freq="h",tz="UTC")
    demand=pd.DataFrame({ba:[100.,100.] for ba in FOUR_BAS},index=idx)
    obs=pd.DataFrame({"timestamp":[idx[0]],"azps_imports_from_srp_mw":[20.]})
    with pytest.raises(ValueError,match="cover every"):
        compare(demand,{}, {},obs,fractions=(0.,))
