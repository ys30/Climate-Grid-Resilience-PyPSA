import pandas as pd
import pytest
from grid_resilience.azps_external_export_sensitivity import prepare_obligation

def test_only_net_exports_become_obligation(tmp_path):
    ts=pd.date_range("2024-07-01",periods=3,freq="h",tz="UTC")
    src=tmp_path/"boundary.csv"
    pd.DataFrame({"timestamp":ts,"net_import_mw_outside":[-10.,4.,-5.]}).to_csv(src,index=False)
    v=prepare_obligation(src,ts)
    assert v.tolist()==[10.,0.,5.]

def test_obligation_missing_hour_fails(tmp_path):
    ts=pd.date_range("2024-07-01",periods=2,freq="h",tz="UTC")
    src=tmp_path/"boundary.csv"
    pd.DataFrame({"timestamp":[ts[0]],"net_import_mw_outside":[-10.]}).to_csv(src,index=False)
    with pytest.raises(ValueError,match="Unmatched"):
        prepare_obligation(src,ts)
