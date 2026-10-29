import pandas as pd
import pytest
from grid_resilience.capacity_adapter import load_eia860_capacities
from grid_resilience.eia860 import read_860

def test_real_capacity_adapter(tmp_path):
    p = tmp_path / "capacities.csv"
    pd.DataFrame([
        {"ba": ba, "technology": "thermal", "capacity_mw": 125.}
        for ba in ("CISO", "AZPS", "BPAT")
    ]).to_csv(p, index=False)
    cap = load_eia860_capacities(p)
    assert cap[("AZPS", "thermal")] == 125.

def test_real_capacity_adapter_rejects_uncovered_region(tmp_path):
    p = tmp_path / "capacities.csv"
    pd.DataFrame([{"ba": "CISO", "technology": "thermal",
                   "capacity_mw": 125.}]).to_csv(p, index=False)
    with pytest.raises(ValueError, match="required BA"):
        load_eia860_capacities(p)

def test_eia860_operable_op_only(tmp_path):
    generators = tmp_path / "3_1_Generator2024.xlsx"
    plants = tmp_path / "2___Plant2024.xlsx"
    pd.DataFrame({
        "Plant Code": [1, 1, 2, 3],
        "Generator ID": ["A", "B", "A", "A"],
        "Nameplate Capacity (MW)": [100, 20, 200, 300],
        "Energy Source 1": ["NG", "NG", "SUN", "WND"],
        "Status": ["OP", "SB", "OP", "OP"],
    }).to_excel(generators, sheet_name="Operable", index=False)
    pd.DataFrame({
        "Plant Code": [1, 2, 3],
        "Balancing Authority Code": ["CISO", "AZPS", "BPAT"],
    }).to_excel(plants, index=False)
    out = read_860(generators, plants)
    assert len(out) == 3
    assert out.capacity_mw.sum() == 600
    assert set(out.technology) == {"thermal", "solar", "wind"}


def test_eia860_ignores_blank_plant_inventory_rows(tmp_path):
    generators = tmp_path / "3_1_Generator2024.xlsx"
    plants = tmp_path / "2___Plant2024.xlsx"
    pd.DataFrame({
        "Plant Code": [1, 2], "Generator ID": ["A", "B"],
        "Nameplate Capacity (MW)": [100, 20],
        "Energy Source 1": ["NG", "NG"],
        "Status": ["OP", "SB"],
    }).to_excel(generators, sheet_name="Operable", index=False)
    pd.DataFrame({
        "Plant Code": [1, None],
        "Balancing Authority Code": ["CISO", None],
    }).to_excel(plants, index=False)
    out = read_860(generators, plants)
    assert len(out) == 1
    assert out.capacity_mw.iloc[0] == 100


def test_eia860_rejects_operating_generator_without_plant_id(tmp_path):
    generators = tmp_path / "3_1_Generator2024.xlsx"
    plants = tmp_path / "2___Plant2024.xlsx"
    pd.DataFrame({
        "Plant Code": [None], "Generator ID": ["A"],
        "Nameplate Capacity (MW)": [100],
        "Energy Source 1": ["NG"], "Status": ["OP"],
    }).to_excel(generators, sheet_name="Operable", index=False)
    pd.DataFrame({
        "Plant Code": [1], "Balancing Authority Code": ["CISO"],
    }).to_excel(plants, index=False)
    with pytest.raises(ValueError, match="Operating generators missing valid Plant Code"):
        read_860(generators, plants)


def test_eia860_quarantines_unassigned_operating_units(tmp_path):
    generators = tmp_path / "3_1_Generator2024.xlsx"
    plants = tmp_path / "2___Plant2024.xlsx"
    pd.DataFrame({
        "Plant Code": [1, 2], "Generator ID": ["A", "B"],
        "Nameplate Capacity (MW)": [100, 50],
        "Energy Source 1": ["NG", "NG"], "Status": ["OP", "OP"],
    }).to_excel(generators, sheet_name="Operable", index=False)
    pd.DataFrame({
        "Plant Code": [1, 2], "Balancing Authority Code": ["CISO", None],
    }).to_excel(plants, index=False)
    units, missing = read_860(generators, plants, return_unassigned=True)
    assert len(units) == 1
    assert len(missing) == 1
    assert int(missing.plant_id.iloc[0]) == 2
