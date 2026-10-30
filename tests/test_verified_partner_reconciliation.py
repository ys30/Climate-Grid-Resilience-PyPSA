"""Protect observed partner-level signs and reconciliation against published sampled-week totals."""
import csv
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CSV=ROOT/"data/verified/seasonal_partner_exchange.csv"
FIG=ROOT/"figures/azps_partner_exchange_heatmap.svg"
EXPECTED={
    "winter":-1491.922619047619,
    "spring":-971.6011904761904,
    "summer":-950.9285714285714,
    "autumn":-748.8690476190476,
}
OUTSIDE={"WALC","LDWP","PNM","TEPC","PACE","WACM","IID"}

def test_partner_totals_reconcile_with_audited_boundary():
    with CSV.open(newline="") as f:
        rows=list(csv.DictReader(f))
    for season,total in EXPECTED.items():
        block=[r for r in rows if r["season"]==season and r["modeled"]=="False"]
        assert set(r["partner"] for r in block)==OUTSIDE
        assert all(int(r["reported_hours"])==168 for r in block)
        actual=sum(float(r["mean_net_import_mw"]) for r in block)
        assert abs(actual-total)<1e-6,(season,actual,total)

def test_directionality_cannot_be_drawn_as_all_exports():
    with CSV.open(newline="") as f:
        rows=list(csv.DictReader(f))
    outside=[r for r in rows if r["modeled"]=="False"]
    assert any(float(r["mean_net_import_mw"])>0 for r in outside)
    assert any(float(r["mean_net_import_mw"])<0 for r in outside)
    assert FIG.is_file() and FIG.stat().st_size>1000
    for document in ("README.md","reports/FINAL_TECHNICAL_SUMMARY.md"):
        assert "azps_partner_exchange_heatmap.svg" in (ROOT/document).read_text()
