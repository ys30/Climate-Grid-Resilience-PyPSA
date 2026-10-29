import pandas as pd
import pytest
from grid_resilience.srp_mechanism_decomposition import ARMS,decompose
from grid_resilience.four_ba import FOUR_BAS

def test_srp_two_factorial_arms_isolate_fleet_and_link():
    pytest.importorskip("pypsa")
    idx=pd.date_range("2024-07-01",periods=2,freq="h",tz="UTC")
    demand=pd.DataFrame({ba:[100.,100.] for ba in FOUR_BAS},index=idx)
    weather={ba:pd.DataFrame({"temperature_2m":[25.,25.],
                              "wind_speed_100m":[5.,5.],
                              "shortwave_radiation":[0.,0.]},index=idx) for ba in FOUR_BAS}
    caps={(ba,"thermal"):150. for ba in FOUR_BAS}
    caps[("AZPS","thermal")]=30.
    rows,interaction=decompose(demand,weather,caps,intertie_fraction=0.5)
    assert len(rows)==4*len(FOUR_BAS)
    assert len(ARMS)==4
    assert isinstance(interaction,float)
    azps=rows.loc[rows.ba=="AZPS"].set_index(["srp_fleet_enabled","azps_srp_link_enabled"])
    assert azps.loc[(True,True),"modeled_unserved_mwh"] <= azps.loc[(True,False),"modeled_unserved_mwh"] + 1e-5
