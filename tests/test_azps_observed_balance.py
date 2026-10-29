import pandas as pd
from grid_resilience.azps_observed_balance import balance

def test_azps_negative_exchange_means_import(tmp_path):
    exchange=tmp_path/"exchange.csv";demand=tmp_path/"demand.csv"
    rows=[{"timestamp":f"2024-07-01T0{i}:00:00Z","from_ba":"AZPS",
           "to_ba":"SRP","reported_value":-60} for i in range(2)]
    pd.DataFrame(rows).to_csv(exchange,index=False)
    pd.DataFrame({"timestamp":["2024-07-01T00:00:00Z","2024-07-01T01:00:00Z"],
                  "CISO":[100,100],"AZPS":[150,155],"BPAT":[100,100]}).to_csv(demand,index=False)
    hourly, neighbors, meta=balance(exchange,demand,"2024-07-01","2024-07-01 02:00",tmp_path/"out")
    assert hourly.net_import_mw.tolist()==[60,60]
    assert hourly.implied_net_generation_mw.tolist()==[90,95]
    assert meta["net_import_mwh"]==120
    assert neighbors.loc[0,"mean_net_import_mw"]==60
