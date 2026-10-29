import pandas as pd
import pytest
from grid_resilience.select_capacity_bas import select
from grid_resilience.capacity_adapter import load_eia860_capacities

def test_explicit_three_ba_subset_of_four_ba(tmp_path):
    path=tmp_path/"four.csv"
    pd.DataFrame([{"ba":ba,"technology":"thermal","capacity_mw":v}
                  for ba,v in [("CISO",100),("AZPS",200),("BPAT",300),("SRP",400)]]).to_csv(path,index=False)
    out=tmp_path/"three.csv"
    selected=select(path,out,("CISO","AZPS","BPAT"))
    assert set(selected.ba)=={"CISO","AZPS","BPAT"}
    assert len(load_eia860_capacities(out))==3
    assert out.with_suffix(".provenance.json").exists()

def test_subset_missing_ba_fails(tmp_path):
    path=tmp_path/"two.csv"
    pd.DataFrame([{"ba":"CISO","technology":"thermal","capacity_mw":100}]).to_csv(path,index=False)
    with pytest.raises(ValueError,match="missing"):
        select(path,tmp_path/"out.csv",("CISO","AZPS"))
