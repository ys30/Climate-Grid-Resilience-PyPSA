import pandas as pd
import pytest
from grid_resilience.azps_boundary_coverage import audit

def test_boundary_gross_and_net_are_separate(tmp_path):
    idx=pd.date_range("2024-07-01",periods=168,freq="h",tz="UTC")
    rows=[{"timestamp":str(t),"from_ba":"AZPS","to_ba":n,"reported_value":v}
          for t in idx for n,v in (("SRP",-20.),("CISO",5.),("PNM",-15.))]
    csv=tmp_path/"exchange.csv";pd.DataFrame(rows).to_csv(csv,index=False)
    summary=audit(csv,tmp_path/"output")
    assert summary["observed_hours"]==168
    assert summary["outside_neighbors"]==["PNM"]
    assert summary["outside_gross_exchange_fraction"]==pytest.approx(15/40)
    assert summary["mean_net_import_from_outside_mw"]==pytest.approx(15.)
    assert summary["mean_total_net_import_mw"]==pytest.approx(30.)

def test_reject_duplicate_hour_neighbor(tmp_path):
    t="2024-07-01T00:00:00Z"
    csv=tmp_path/"dup.csv"
    pd.DataFrame([{"timestamp":t,"from_ba":"AZPS","to_ba":"SRP","reported_value":-5}]*2).to_csv(csv,index=False)
    with pytest.raises(ValueError,match="unique"):
        audit(csv,tmp_path/"out")
