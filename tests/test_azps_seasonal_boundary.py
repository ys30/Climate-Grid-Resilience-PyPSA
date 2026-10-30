import pandas as pd
import pytest
from grid_resilience.azps_seasonal_boundary import WINDOWS,summarize

def test_four_season_sample_week_summary(tmp_path):
    for season,(start,end) in WINDOWS.items():
        out=tmp_path/season;out.mkdir()
        dates=pd.date_range(start,periods=168,freq="h",tz="UTC")
        pd.DataFrame({"timestamp":dates,"net_import_mw_outside":[-10.]*168,
          "gross_exchange_mw_outside":[10.]*168,
          "gross_exchange_mw_included":[30.]*168}).to_csv(out/"azps_boundary_hourly.csv",index=False)
        pd.DataFrame({"to_ba":["SRP","WALC"]}).to_csv(out/"azps_boundary_neighbors.csv",index=False)
    result=summarize(tmp_path,tmp_path/"summary")
    assert len(result)==4
    assert (result.hours_outside_net_export==168).all()
    assert (result.outside_gross_exchange_fraction==0.25).all()
    assert (result.outside_net_export_mwh==1680).all()
