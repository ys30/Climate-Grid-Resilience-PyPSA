import pandas as pd
import pytest
from grid_resilience.capacity_adapter import load_eia860_capacities

def test_unknown_fuel_category_rejected(tmp_path):
    file = tmp_path / "cap.csv"
    pd.DataFrame([{"ba": b, "technology": "unknown_tech", "capacity_mw": 100}
                  for b in ("CISO", "AZPS", "BPAT")]).to_csv(file, index=False)
    with pytest.raises(ValueError, match="Unknown technology"):
        load_eia860_capacities(file)
