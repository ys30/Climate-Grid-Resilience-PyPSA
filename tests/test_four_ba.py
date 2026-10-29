import pandas as pd
import pytest
from grid_resilience.four_ba import FOUR_BAS, FOUR_LINKS
from grid_resilience.western_us import build_model, load_eia930

def test_four_ba_model_has_srp_and_explicit_azps_srp_link():
    pytest.importorskip("pypsa")
    idx=pd.date_range("2024-07-01",periods=3,freq="h",tz="UTC")
    demand=pd.DataFrame({ba:[100.,110.,105.] for ba in FOUR_BAS},index=idx)
    weather={ba:pd.DataFrame({
        "temperature_2m":[30.,32.,35.],
        "wind_speed_100m":[6.,6.,6.],
        "shortwave_radiation":[0.,300.,0.]},index=idx) for ba in FOUR_BAS}
    caps={(ba,"thermal"):120. for ba in FOUR_BAS}
    n=build_model(demand,weather,"observed_weather",capacities=caps,
                  bas=FOUR_BAS,interties=FOUR_LINKS)
    assert set(n.buses.index)==set(FOUR_BAS)
    assert len(n.loads)==4
    assert "AZPS_SRP" in n.links.index
    assert n.generators.at["SRP_thermal","p_nom"]==120.
    assert "CISO_AZPS" in n.links.index

def test_four_ba_api_csv_is_not_truncated_to_three_bas(tmp_path):
    p=tmp_path/"four.csv"
    pd.DataFrame({"timestamp":["2024-07-01T00:00:00Z"],
                  **{ba:[100.] for ba in FOUR_BAS}}).to_csv(p,index=False)
    frame=load_eia930(p,"2024-07-01","2024-07-01 01:00",bas=FOUR_BAS)
    assert set(frame.columns)==set(FOUR_BAS)
