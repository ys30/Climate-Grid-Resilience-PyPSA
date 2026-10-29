"""Validated EIA-860 generator inventory -> BA/technology installed capacities.

Use EIA 2024 final operating-generator spreadsheet (Operable tab) and plant
spreadsheet; never infer availability from nameplate alone. No hourly dispatch.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import pandas as pd

BA_CODES = ("CISO", "AZPS", "BPAT")
FUEL_TECH = {
    "SUN": "solar", "WND": "wind", "WAT": "hydro",
    "NUC": "nuclear", "BIT": "thermal", "SUB": "thermal",
    "LIG": "thermal", "RC": "thermal", "NG": "thermal",
    "DFO": "thermal", "RFO": "thermal", "JF": "thermal",
    "KER": "thermal", "PC": "thermal", "WO": "thermal",
    "BFG": "thermal", "OG": "thermal", "OBG": "thermal",
    "LFG": "thermal", "MSW": "thermal", "GEO": "geothermal",
    "MWH": "storage", "PUR": "other", "WH": "hydro",
    "BLQ": "thermal", "SLW": "thermal", "TDF": "thermal",
    "AB": "thermal", "OBS": "thermal", "WDS": "thermal",
    "OTH": "other", "OT": "other", "PG": "thermal",
}
# These are source codes, not an exhaustive or physically exact technology taxonomy.
# Unmapped fuel categories fail closed instead of being silently dropped.


def _find(df, *names):
    keys = {str(k).strip().casefold().replace("_", " "): k for k in df.columns}
    for name in names:
        k = name.casefold().replace("_", " ")
        if k in keys:
            return keys[k]
    raise ValueError(f"Required EIA-860 column absent: {names}. Available: {list(df.columns)}")


def read_860(operable_xlsx, plant_xlsx, year=2024, return_unassigned=False):
    """Read extracted official EIA-860 generator and plant workbooks.

    EIA Excel files sometimes contain one metadata row before actual headings.
    Reject any layout not recognized; never aggregate unvalidated rows.
    """
    def excel(path):
        for skip in (0, 1, 2):
            df = pd.read_excel(path, sheet_name="Operable" if "generator" in Path(path).name.lower() else 0, skiprows=skip)
            try:
                _find(df, "Plant Code", "Plant Id")
                return df
            except ValueError:
                pass
        raise ValueError(f"Could not identify EIA-860 table header: {path}")
    g = excel(operable_xlsx)
    p = excel(plant_xlsx)
    plant_g = _find(g, "Plant Code", "Plant Id")
    plant_p = _find(p, "Plant Code", "Plant Id")
    ba_p = _find(p, "Balancing Authority Code", "Balancing Authority")
    cap_g = _find(g, "Nameplate Capacity (MW)", "Nameplate Capacity")
    fuel_g = _find(g, "Energy Source 1", "Energy Source Code")
    status_g = _find(g, "Status", "Operational Status")
    gen_id_g = _find(g, "Generator ID", "Generator Id")
    rows = g[[plant_g, gen_id_g, cap_g, fuel_g, status_g]].copy()
    rows.columns = ["plant_id", "generator_id", "capacity_mw", "fuel", "status"]
    plants = p[[plant_p, ba_p]].copy()
    plants.columns = ["plant_id", "ba"]
    # Official spreadsheets may contain trailing blank rows, metadata and inactive
    # records without plant IDs. Never discard genuine OP records silently.
    plants = plants.dropna(how="all").copy()
    rows = rows.dropna(how="all").copy()
    rows["status"] = rows.status.astype("string").str.strip().str.upper()
    rows = rows.loc[rows.status.eq("OP").fillna(False)].copy()
    plants["plant_id"] = pd.to_numeric(plants.plant_id, errors="coerce")
    rows["plant_id"] = pd.to_numeric(rows.plant_id, errors="coerce")
    if rows.plant_id.isna().any():
        raise ValueError(f"Operating generators missing valid Plant Code: {int(rows.plant_id.isna().sum())}")
    # Null plant IDs in the plant inventory cannot identify a plant; exclude,
    # but require every operating generator in the chosen BAs to be mapped.
    plants = plants.dropna(subset=["plant_id"]).copy()
    if ((plants.plant_id % 1) != 0).any() or ((rows.plant_id % 1) != 0).any():
        raise ValueError("Noninteger EIA Plant Code detected")
    plants["plant_id"] = plants.plant_id.astype("int64")
    rows["plant_id"] = rows.plant_id.astype("int64")
    if plants.plant_id.duplicated().any():
        raise ValueError("Duplicated plant ID in plant spreadsheet")
    rows = rows.merge(plants, on="plant_id", how="left", validate="many_to_one")
    unassigned = rows.loc[rows.ba.isna()].copy()
    # BA assignment can be missing in a nationwide plant workbook. Never
    # assign such rows to a western BA by guesswork or count their capacity.
    rows = rows.loc[rows.ba.astype("string").str.strip().isin(BA_CODES).fillna(False)].copy()
    rows["ba"] = rows.ba.astype("string").str.strip().str.upper()
    rows["capacity_mw"] = pd.to_numeric(rows.capacity_mw, errors="raise")
    if rows.capacity_mw.isna().any() or (rows.capacity_mw <= 0).any():
        raise ValueError("Operating generator capacity must be positive")
    if rows.duplicated(["plant_id", "generator_id"]).any():
        raise ValueError("Duplicate active plant/generator pairs")
    rows["fuel"] = rows.fuel.astype(str).str.strip().str.upper()
    unknown = sorted(set(rows.fuel) - set(FUEL_TECH))
    if unknown:
        raise ValueError(f"Unmapped EIA energy-source codes; extend mapping explicitly: {unknown}")
    rows["technology"] = rows.fuel.map(FUEL_TECH)
    rows["data_year"] = int(year)
    rows = rows.sort_values(["ba", "plant_id", "generator_id"]).reset_index(drop=True)
    return (rows, unassigned) if return_unassigned else rows


def export_860(operable_xlsx, plant_xlsx, output, year=2024):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    units, unassigned = read_860(operable_xlsx, plant_xlsx, year, return_unassigned=True)
    capacities = units.groupby(["ba", "technology"], as_index=False).capacity_mw.sum()
    missing = set(BA_CODES) - set(capacities.ba)
    if missing:
        raise ValueError(f"No operating generation in requested BAs: {sorted(missing)}")
    units.to_csv(output / "eia860_operating_units.csv", index=False)
    unassigned.to_csv(output / "eia860_unassigned_ba_audit.csv", index=False)
    capacities.to_csv(output / "eia860_ba_technology_capacity.csv", index=False)
    metadata = {
        "source": "https://www.eia.gov/electricity/data/eia860/",
        "year": int(year),
        "operable_generator_xlsx_sha256": hashlib.sha256(Path(operable_xlsx).read_bytes()).hexdigest(),
        "plant_xlsx_sha256": hashlib.sha256(Path(plant_xlsx).read_bytes()).hexdigest(),
        "status_filter": "OP only; standby and out-of-service excluded",
        "unassigned_operating_generator_count": int(len(unassigned)),
        "ba_assignment_complete_nationwide": bool(unassigned.empty),
        "coverage_warning": "Unassigned units excluded; coverage of target BAs cannot be guaranteed without resolving them" if len(unassigned) else None,
        "storage_warning": "Storage nameplate MW is not dispatchable energy; energy capacity, efficiency, and SOC must be separately sourced",
        "capacity_metric": "EIA-860 nameplate MW, NOT hourly available power",
        "scope": list(BA_CODES),
        "technology_mapping": FUEL_TECH,
        "known_limitations": [
            "EIA-860 is a snapshot and may not match 2024 hourly commissioning/retirement",
            "Fuel grouping is coarse and requires domain review",
            "Storage needs separate energy-capacity/duration treatment",
            "Plant BA memberships may differ from EIA-930 reporting boundaries",
            "Generator plant BA is a reporting association, not a transmission connectivity map"
        ]
    }
    (output / "eia860_provenance.json").write_text(json.dumps(metadata, indent=2) + "\n")
    return capacities


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--generators", required=True, help="Official EIA-860 3_1_Generator2024.xlsx workbook")
    p.add_argument("--plants", required=True, help="Official EIA-860 2___Plant2024.xlsx workbook")
    p.add_argument("--year", type=int, default=2024)
    p.add_argument("--output", default="data/processed/eia860")
    a = p.parse_args()
    print(export_860(a.generators, a.plants, a.output, a.year).to_string(index=False))


if __name__ == "__main__":
    main()
