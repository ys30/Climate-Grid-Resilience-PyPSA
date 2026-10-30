import pandas as pd
from grid_resilience.seasonal_four_ba_summary import aggregate
from grid_resilience.azps_seasonal_boundary import WINDOWS

def test_seasonal_four_ba_summary(tmp_path):
    for season in WINDOWS:
        directory=tmp_path/season;directory.mkdir()
        rows=[{"scenario":scenario,"ba":ba,"unserved_energy_mwh":5.,
               "peak_shortfall_mw":2.,"shortage_hours":2}
              for scenario in ("observed_weather","heat_plus_4c","compound_heat_wind_derating")
              for ba in ("CISO","AZPS","BPAT","SRP")]
        pd.DataFrame(rows).to_csv(directory/"metrics.csv",index=False)
    azps=aggregate(tmp_path,tmp_path/"summary")
    assert len(azps)==12
    assert set(azps.season)==set(WINDOWS)
    assert (tmp_path/"summary"/"seasonal_four_ba_adequacy.csv").exists()
