import pytest
from grid_resilience.eia_exchange_api import parse_exchange

def test_azps_hourly_exchange_from_eia_api():
    rows=[{"period":"2024-07-01T00","fromba":"AZPS","toba":"CISO","value":"-250"},
          {"period":"2024-07-01T01","fromba":"AZPS","toba":"BPAT","value":"125"}]
    df=parse_exchange(rows,"2024-07-01","2024-07-02")
    assert len(df)==2
    assert df.reported_value.sum()==-125

def test_duplicate_pair_hour_rejected():
    row={"period":"2024-07-01T00","fromba":"AZPS","toba":"CISO","value":"100"}
    with pytest.raises(ValueError,match="Duplicate"):
        parse_exchange([row,row],"2024-07-01","2024-07-02")

def test_schema_requires_pair_ids():
    with pytest.raises(ValueError,match="schema mismatch"):
        parse_exchange([{"period":"2024-07-01T00","value":"100"}],"2024-07-01","2024-07-02")
