import pandas as pd
from grid_resilience.capacity_projection import project

def test_projection_never_dispatches_storage_as_generator(tmp_path):
    src = tmp_path / "inventory.csv"
    pd.DataFrame([
        {"ba": ba, "technology": tech, "capacity_mw": mw}
        for ba in ("CISO", "AZPS", "BPAT")
        for tech, mw in (("thermal", 100.), ("storage", 40.))
    ]).to_csv(src, index=False)
    modeled, omitted = project(src, tmp_path / "processed")
    assert set(modeled.technology) == {"thermal"}
    assert set(omitted.technology) == {"storage"}
    assert omitted.capacity_mw.sum() == 120
    assert (tmp_path / "processed" / "projection_provenance.json").exists()
