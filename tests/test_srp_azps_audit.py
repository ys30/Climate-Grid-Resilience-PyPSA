import pandas as pd
import pytest
from grid_resilience.srp_azps_audit import reconcile

def test_srp_azps_hourly_reconciliation(tmp_path):
    demand=tmp_path/"d.csv";exchange=tmp_path/"x.csv"
    pd.DataFrame({"timestamp":["2024-07-01T00:00:00Z","2024-07-01T01:00:00Z"],
                  "SRP":[600,620],"AZPS":[900,950]}).to_csv(demand,index=False)
    pd.DataFrame([{"timestamp":t,"from_ba":"AZPS","to_ba":"SRP","reported_value":-200}
                  for t in ["2024-07-01T00:00:00Z","2024-07-01T01:00:00Z"]]).to_csv(exchange,index=False)
    rows,info=reconcile(demand,exchange,tmp_path/"out")
    assert rows.azps_imports_from_srp_mw.tolist()==[200,200]
    assert info["matched_hours"]==2

def test_srp_azps_missing_exchange_rejected(tmp_path):
    demand=tmp_path/"d.csv";exchange=tmp_path/"x.csv"
    pd.DataFrame({"timestamp":["2024-07-01T00:00:00Z"],"SRP":[600],"AZPS":[900]}).to_csv(demand,index=False)
    pd.DataFrame(columns=["timestamp","from_ba","to_ba","reported_value"]).to_csv(exchange,index=False)
    with pytest.raises(ValueError,match="Incomplete"):
        reconcile(demand,exchange,tmp_path/"out")
