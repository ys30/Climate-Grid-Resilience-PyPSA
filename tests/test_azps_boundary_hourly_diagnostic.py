import pandas as pd
import pytest
from grid_resilience.azps_boundary_hourly_diagnostic import diagnose

def test_outside_boundary_signed_hours(tmp_path):
    ts=pd.date_range("2024-07-01",periods=3,freq="h",tz="UTC")
    b=pd.DataFrame({"timestamp":ts,"net_import_mw_included":[20,20,20],
                     "net_import_mw_outside":[-10,5,0],
                     "net_import_all_mw":[10,25,20]})
    d=pd.DataFrame({"timestamp":ts,"observed_demand_mw":[100,100,100],
                     "net_import_mw":[10,25,20],
                     "implied_net_generation_mw":[90,75,80]})
    bf=tmp_path/"boundary.csv";df=tmp_path/"demand.csv"
    b.to_csv(bf,index=False);d.to_csv(df,index=False)
    result=diagnose(bf,df,tmp_path/"out")
    assert result["hours_outside_net_import"]==1
    assert result["hours_outside_net_export"]==1
    assert result["hours_outside_net_zero"]==1
    assert result["outside_export_mwh"]==pytest.approx(10)
    assert result["outside_import_mwh"]==pytest.approx(5)
    assert result["identity_max_abs_residual_mw"]==pytest.approx(0)
