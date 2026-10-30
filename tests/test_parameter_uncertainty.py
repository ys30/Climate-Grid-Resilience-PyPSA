import pandas as pd
from grid_resilience.parameter_uncertainty import LINK_FRACTIONS,THERMAL_MULTIPLIERS,evaluate
from grid_resilience.four_ba import FOUR_BAS

def test_parameter_grid_executes_and_has_single_baseline():
    idx=pd.date_range("2024-07-01",periods=2,freq="h",tz="UTC")
    demand=pd.DataFrame({ba:[100.,100.] for ba in FOUR_BAS},index=idx)
    weather={ba:pd.DataFrame({"temperature_2m":[25.,25.],
                               "wind_speed_100m":[5.,5.],
                               "shortwave_radiation":[0.,0.]},index=idx) for ba in FOUR_BAS}
    caps={(ba,"thermal"):150. for ba in FOUR_BAS}
    data=evaluate(demand,weather,caps)
    assert len(data)==len(LINK_FRACTIONS)*len(THERMAL_MULTIPLIERS)*len(FOUR_BAS)
    assert len(data[(data.link_fraction_of_smaller_peak==.10)&
                    (data.thermal_nameplate_multiplier==1.)])==4
    assert (data.modeled_unserved_mwh>=0).all()
