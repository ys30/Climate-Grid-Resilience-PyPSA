import pandas as pd
from grid_resilience.plot_seasonal_partner_exchange import build
from grid_resilience.azps_seasonal_boundary import WINDOWS

def test_partner_signs_are_preserved(tmp_path):
    for season in WINDOWS:
        d=tmp_path/season;d.mkdir()
        pd.DataFrame([
          {"to_ba":"WALC","modeled_neighbor":False,"mean_net_import_mw":-100,"reported_hours":168},
          {"to_ba":"IID","modeled_neighbor":False,"mean_net_import_mw":20,"reported_hours":168},
          {"to_ba":"SRP","modeled_neighbor":True,"mean_net_import_mw":500,"reported_hours":168}
        ]).to_csv(d/"azps_boundary_neighbors.csv",index=False)
    data=build(tmp_path,tmp_path/"output")
    assert len(data)==12
    assert data.loc[data.partner=="WALC","mean_net_import_mw"].lt(0).all()
    assert data.loc[data.partner=="IID","mean_net_import_mw"].gt(0).all()
    assert (tmp_path/"output"/"azps_partner_exchange_heatmap.svg").exists()
