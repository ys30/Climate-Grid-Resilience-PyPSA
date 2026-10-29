import pandas as pd
import pytest
from grid_resilience.interchange import audit_interchange

def test_interchange_audits_reciprocal_reports(tmp_path):
    source = tmp_path / "interchange.csv"
    pd.DataFrame([
        {"Balancing Authority": "CISO", "Interconnected BA": "AZPS",
         "UTC Time": "2024-07-01T01:00Z", "Interchange (MW)": -200.0},
        {"Balancing Authority": "AZPS", "Interconnected BA": "CISO",
         "UTC Time": "2024-07-01T01:00Z", "Interchange (MW)": 200.0},
    ]).to_csv(source, index=False)
    report = audit_interchange(source, "2024-07-01", "2024-07-02", tmp_path / "out")
    assert len(report) == 1
    assert report.n_reciprocal.iloc[0] == 1
    assert report.max_opposite_discrepancy_mw.iloc[0] == 0
    assert (tmp_path / "out" / "observed_interchange_pairs.csv").exists()

def test_interchange_duplicate_rejected(tmp_path):
    source = tmp_path / "interchange.csv"
    row = {"Balancing Authority": "CISO", "Interconnected BA": "AZPS",
           "UTC Time": "2024-07-01T01:00Z", "Interchange (MW)": 2}
    pd.DataFrame([row, row]).to_csv(source, index=False)
    with pytest.raises(ValueError, match="Duplicate"):
        audit_interchange(source, "2024-07-01", "2024-07-02", tmp_path / "out")
