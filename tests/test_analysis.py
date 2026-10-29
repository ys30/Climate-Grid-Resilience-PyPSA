from grid_resilience.analysis import scenario_data,metrics,analyze

def test_no_negative_shortfall():
    assert (scenario_data().unserved_mw>=0).all()

def test_scenario_ordering():
    m=metrics(scenario_data())
    assert m.loc["Baseline","unserved_energy_mwh"]==0
    assert m.loc["Compound stress","unserved_energy_mwh"]>m.loc["Heatwave","unserved_energy_mwh"]

def test_metric_consistency():
    df=scenario_data();m=metrics(df)
    for name,g in df.groupby("scenario"):
        assert abs(m.loc[name,"unserved_energy_mwh"]-g.unserved_mw.sum())<1e-9

def test_figures(tmp_path):
    analyze(tmp_path)
    assert all((tmp_path/f).is_file() for f in ["shortfall_profiles.png","unserved_energy.png","resilience_metrics.csv"])
