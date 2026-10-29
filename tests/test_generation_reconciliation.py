import pandas as pd
import pytest
from grid_resilience.eia_net_generation import parse_generation
from grid_resilience.azps_generation_reconciliation import reconcile

def test_independent_generation_ng_schema_and_alignment():
    records=[{"period":"2024-07-01T00","respondent":"AZPS","type":"NG","value":"90"},
             {"period":"2024-07-01T00","respondent":"SRP","type":"NG","value":"110"}]
    df=parse_generation(records,"2024-07-01","2024-07-01 01:00",("AZPS","SRP"))
    assert df.loc[pd.Timestamp("2024-07-01",tz="UTC"),"AZPS"]==90

def test_ng_omitted_hour_rejected():
    with pytest.raises(ValueError,match="Missing hourly"):
        parse_generation([], "2024-07-01","2024-07-01 01:00",("AZPS",))

def test_independent_generation_reconciliation(tmp_path):
    a=tmp_path/"balance.csv";n=tmp_path/"ng.csv"
    pd.DataFrame([{"timestamp":"2024-07-01T00:00:00Z",
                   "observed_demand_mw":150,"net_import_mw":60,
                   "implied_net_generation_mw":90}]).to_csv(a,index=False)
    pd.DataFrame([{"timestamp":"2024-07-01T00:00:00Z","AZPS":88}]).to_csv(n,index=False)
    frame,metrics=reconcile(a,n,tmp_path/"out")
    assert frame.balance_residual_mw.iloc[0]==2
    assert metrics["maximum_absolute_residual_mw"]==2
