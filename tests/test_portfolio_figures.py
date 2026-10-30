"""Figures should be present, parseable and labeled as screening outputs."""
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
FIGURES=(
 "figures/azps_four_season_shortfall.svg",
 "figures/azps_parameter_sensitivity.svg",
 "figures/four_ba_topology_schematic.svg",
)

def test_verifiable_figures_embedded_in_readme_and_report():
    readme=(ROOT/"README.md").read_text()
    report=(ROOT/"reports/FINAL_TECHNICAL_SUMMARY.md").read_text()
    for path in FIGURES:
        image=ROOT/path
        assert image.is_file()
        root=ET.parse(image).getroot()
        assert root.tag.endswith("svg")
        assert int(root.attrib["viewBox"].split()[-1])>0
        assert f"({path})" in readme
        assert f"(../{path})" in report

def test_charts_have_screening_and_geography_disclaimers():
    seasonal=(ROOT/FIGURES[0]).read_text()
    uncertainty=(ROOT/FIGURES[1]).read_text()
    geography=(ROOT/FIGURES[2]).read_text()
    assert "90,344" in seasonal
    assert "130,831" in uncertainty
    assert "not actual outages" in seasonal
    assert "not BA borders" in geography
    for name in ("BPAT","CISO","AZPS","SRP"):
        assert name in geography
