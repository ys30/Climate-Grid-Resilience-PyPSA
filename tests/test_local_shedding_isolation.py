import pandas as pd
import pytest
from grid_resilience.western_us import build_model
from grid_resilience.four_ba import FOUR_BAS,FOUR_LINKS

def test_unserved_generation_cannot_be_exported_across_srp_link():
    pytest.importorskip("pypsa")
    idx=pd.date_range("2024-07-01",periods=2,freq="h",tz="UTC")
    demand=pd.DataFrame({ba:[100.,100.] for ba in FOUR_BAS},index=idx)
    weather={ba:pd.DataFrame({"temperature_2m":[25.,25.],
                              "wind_speed_100m":[5.,5.],
                              "shortwave_radiation":[0.,0.]},index=idx) for ba in FOUR_BAS}
    caps={(ba,"thermal"):200. for ba in FOUR_BAS}
    caps[("SRP","thermal")]=0.
    caps[("AZPS","thermal")]=0.
    net=build_model(demand,weather,"observed_weather",capacities=caps,bas=FOUR_BAS,
                    interties=FOUR_LINKS,intertie_fraction=0.5,local_shedding=True)
    status,termination=net.optimize(solver_name="highs")
    assert (status,termination)==("ok","optimal")
    assert net.links.at["SRP_supply_to_load","p_min_pu"]==0
    assert net.generators.at["SRP_unserved","bus"]=="SRP_load_bus"
    # With SRP and AZPS having no physical generation, neither may supply
    # another BA using its artificial local shortage generator.
    assert net.links_t.p0["AZPS_SRP"].abs().max() < 1e-5
    assert net.generators_t.p["SRP_unserved"].sum()>0
