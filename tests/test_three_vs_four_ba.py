import pandas as pd
import pytest
from grid_resilience.three_vs_four_ba import compare,SCENARIOS,BAS

def test_compare_shared_ba_and_srp_excluded(tmp_path):
    three=tmp_path/"three.csv";four=tmp_path/"four.csv"
    rows=[{"scenario":s,"ba":ba,"unserved_energy_mwh":100. if ba=="AZPS" else 0.} for s in SCENARIOS for ba in BAS]
    pd.DataFrame(rows).to_csv(three,index=False)
    more=[{**r,"unserved_energy_mwh":50. if r["ba"]=="AZPS" else 0.} for r in rows]
    more += [{"scenario":s,"ba":"SRP","unserved_energy_mwh":0.} for s in SCENARIOS]
    pd.DataFrame(more).to_csv(four,index=False)
    actual=compare(three,four,tmp_path/"out")
    assert len(actual)==9
    assert actual.loc[actual.ba=="AZPS","reduction_percent"].tolist()==[50.]*3
    assert (tmp_path/"out"/"comparison_provenance.json").is_file()

def test_missing_four_ba_scenario_rejected(tmp_path):
    three=tmp_path/"three.csv";four=tmp_path/"four.csv"
    data=[{"scenario":s,"ba":ba,"unserved_energy_mwh":0} for s in SCENARIOS for ba in BAS]
    pd.DataFrame(data).to_csv(three,index=False)
    pd.DataFrame(data[:-1]).to_csv(four,index=False)
    with pytest.raises(ValueError,match="incomplete"):
        compare(three,four,tmp_path/"out")
