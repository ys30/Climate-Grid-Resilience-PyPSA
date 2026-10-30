"""Regression checks for portfolio claims and verified evidence provenance."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
README=ROOT/"README.md"
SUMMARY=ROOT/"reports"/"FINAL_TECHNICAL_SUMMARY.md"

def test_final_summary_is_linked_and_exists():
    text=README.read_text()
    assert "(reports/FINAL_TECHNICAL_SUMMARY.md)" in text
    assert SUMMARY.exists()

def test_final_summary_has_required_evidence_boundaries():
    text=SUMMARY.read_text()
    for required in ("EIA-930","EIA-860","ERA5","PyPSA","40994939078",
                     "41002228759","not observed", "not a calibrated"):
        assert required.lower() in text.lower(), required

def test_current_readme_does_not_claim_unsolved_pypsa():
    text=README.read_text().split("## Western US observed-load")[0]
    assert "not a solved PyPSA model" not in text
    assert "PyPSA integration is a planned extension" not in text
    assert "FINAL_TECHNICAL_SUMMARY.md" in text

def test_report_links_present():
    text=SUMMARY.read_text()
    for report in ("2024-four-season-four-ba-adequacy-verified.md",
                   "2024-azps-four-season-boundary-verified.md",
                   "2024-07-four-ba-parameter-sensitivity-verified.md"):
        assert report in text
        assert (ROOT/"reports"/report).is_file()
