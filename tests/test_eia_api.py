import pandas as pd
import pytest
from grid_resilience.eia_api import parse_rto
from grid_resilience.western_us import load_eia930

def _records():
    return [{"period": f"2024-07-01T{hour:02d}", "respondent": ba,
             "type": "D", "value": str(1000 + hour)}
            for hour in range(3) for ba in ("CISO", "AZPS", "BPAT")]

def test_parse_eia_hour_beginning_no_shift():
    out = parse_rto(_records(), "2024-07-01", "2024-07-01 03:00")
    assert out.shape == (3, 3)
    assert out.iloc[0]["CISO"] == 1000
    assert out.index[0] == pd.Timestamp("2024-07-01T00:00Z")

def test_api_csv_accepted_directly(tmp_path):
    data = parse_rto(_records(), "2024-07-01", "2024-07-01 03:00")
    path = tmp_path / "data.csv"
    data.rename_axis("timestamp").to_csv(path)
    loaded = load_eia930(path, "2024-07-01", "2024-07-01 03:00")
    pd.testing.assert_frame_equal(loaded, data, check_freq=False)

def test_api_missing_rejected():
    with pytest.raises(ValueError, match="Missing BA"):
        parse_rto(_records()[:-1], "2024-07-01", "2024-07-01 03:00")

def test_api_duplicate_rejected():
    with pytest.raises(ValueError, match="Duplicated"):
        parse_rto(_records() + [_records()[0]], "2024-07-01", "2024-07-01 03:00")
