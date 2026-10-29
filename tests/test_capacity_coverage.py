import pandas as pd
import pytest
from grid_resilience.capacity_coverage import audit

def test_coverage_separates_storage_without_counting_as_firm_mw(tmp_path):
    p = tmp_path / "capacity.csv"
    pd.DataFrame([
        {"ba": ba, "technology": tech, "capacity_mw": mw}
        for ba in ("CISO", "AZPS", "BPAT")
        for tech, mw in (("thermal", 80), ("storage", 20))
    ]).to_csv(p, index=False)
    result = audit(p, tmp_path / "out")
    assert (result.modeled_nameplate_mw == 80).all()
    assert (result.excluded_storage_other_nameplate_mw == 20).all()
    assert (result.modeled_share_of_reported_nameplate == 0.8).all()

def test_coverage_requires_positive_capacity(tmp_path):
    p = tmp_path / "capacity.csv"
    pd.DataFrame([{"ba": ba, "technology": "thermal", "capacity_mw": 0}
                  for ba in ("CISO", "AZPS", "BPAT")]).to_csv(p, index=False)
    with pytest.raises(ValueError, match="No positive"):
        audit(p, tmp_path / "out")
