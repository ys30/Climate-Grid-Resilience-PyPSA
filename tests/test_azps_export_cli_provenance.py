import json
import sys
import pandas as pd
import pytest
from grid_resilience import azps_external_export_sensitivity as module


def test_cli_main_assigns_obligation_after_provenance_validation(tmp_path, monkeypatch):
    idx=pd.date_range("2024-07-01",periods=2,freq="h",tz="UTC")
    folder=tmp_path/"boundary";folder.mkdir()
    source=folder/"azps_boundary_hourly.csv"
    pd.DataFrame({"timestamp":idx,"net_import_mw_outside":[-12.,-7.]}).to_csv(source,index=False)
    (folder/"azps_boundary_summary.json").write_text(json.dumps({"modeled_neighbors":["CISO","SRP"]}))
    demand=pd.DataFrame({"CISO":[100.,100.],"AZPS":[100.,100.],
                         "BPAT":[100.,100.],"SRP":[100.,100.]},index=idx)
    monkeypatch.setattr(module,"load_eia930",lambda *a,**kw:demand)
    monkeypatch.setattr(module,"fetch_era5",lambda *a,**kw:{})
    monkeypatch.setattr(module,"load_eia860_capacities",lambda *a,**kw:{})
    def fake_experiment(d,w,c,obligation):
        assert obligation.tolist()==[12.,7.]
        return pd.DataFrame([{"scenario":"observed_weather","ba":"AZPS","modeled_unserved_mwh":0}])
    monkeypatch.setattr(module,"experiment",fake_experiment)
    destination=tmp_path/"result"
    monkeypatch.setattr(sys,"argv",["audit","--demand-csv","d.csv","--capacities","c.csv",
                      "--boundary-csv",str(source),"--output",str(destination)])
    module.main()
    assert (destination/"external_obligation_scenarios.csv").exists()
    assert (destination/"observed_hourly_external_obligation.csv").exists()


def test_cli_rejects_incorrect_boundary_scope(tmp_path,monkeypatch):
    idx=pd.date_range("2024-07-01",periods=1,freq="h",tz="UTC")
    folder=tmp_path/"boundary";folder.mkdir()
    src=folder/"hourly.csv"
    pd.DataFrame({"timestamp":idx,"net_import_mw_outside":[-5]}).to_csv(src,index=False)
    (folder/"azps_boundary_summary.json").write_text(json.dumps({"modeled_neighbors":["SRP"]}))
    monkeypatch.setattr(module,"load_eia930",lambda *a,**kw:pd.DataFrame({"AZPS":[100]},index=idx))
    monkeypatch.setattr(sys,"argv",["audit","--demand-csv","d.csv","--capacities","c.csv",
                      "--boundary-csv",str(src)])
    with pytest.raises(ValueError,match="Boundary scope"):
        module.main()
