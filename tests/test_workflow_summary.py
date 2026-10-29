from grid_resilience.workflow_summary import render

def test_summary_marks_missing_outputs_without_crashing(tmp_path):
    result = render(tmp_path)
    assert "Missing outputs:" in result
    assert "inventory" in result
    assert "❌" in result

def test_summary_includes_complete_comparison(tmp_path):
    import pandas as pd
    coverage = tmp_path / "outputs/partial_nameplate_audit"
    comparison = tmp_path / "outputs/model_comparison"
    coverage.mkdir(parents=True)
    comparison.mkdir(parents=True)
    pd.DataFrame([{"ba": "CISO", "modeled_nameplate_mw": 100}]).to_csv(coverage / "capacity_coverage.csv", index=False)
    pd.DataFrame([{"scenario": "observed_weather", "unserved_energy_mwh_delta": 5}]).to_csv(comparison / "scenario_comparison.csv", index=False)
    result = render(tmp_path)
    assert "CISO" in result
    assert "observed_weather" in result
