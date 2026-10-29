"""Print an auditable GitHub Actions run summary from generated CSVs.

The summary never claims successful validation when a prerequisite artifact
is absent. It can run under 'if: always()' after failed pipeline steps.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import pandas as pd

def render(root="."):
    root = Path(root)
    required = {
        "inventory": root / "data/processed/eia860/inventory_audit.json",
        "coverage": root / "outputs/partial_nameplate_audit/capacity_coverage.csv",
        "partial_model": root / "outputs/eia860_partial_nameplate/metrics.csv",
        "synthetic_model": root / "outputs/matched_synthetic_reference/metrics.csv",
        "comparison": root / "outputs/model_comparison/scenario_comparison.csv",
    }
    lines = ["## Western US EIA-860 reproducibility audit", "",
             "This is a **partial year-end nameplate screening model**, not a validated",
             "2024 outage or reliability estimate.", "", "### Artifact checks", ""]
    for name, path in required.items():
        lines.append(f"- {'✅' if path.is_file() else '❌'} {name}: `{path.relative_to(root)}`")
    coverage = required["coverage"]
    if coverage.is_file():
        frame = pd.read_csv(coverage)
        lines.extend(["", "### Nameplate coverage", "", "```csv\\n" + frame.to_csv(index=False).strip() + "\\n```"])
    comparison = required["comparison"]
    if comparison.is_file():
        frame = pd.read_csv(comparison)
        lines.extend(["", "### Assumed-fleet versus EIA partial-nameplate simulations", "",
                      frame.to_markdown(index=False)])
    missing = [name for name, path in required.items() if not path.is_file()]
    lines.extend(["", f"**Missing outputs:** {', '.join(missing) if missing else 'none'}",
                  "", "Excluded storage, hypothetical transfers and generation availability",
                  "assumptions must be reviewed before interpreting the simulated shortfalls."])
    return "\n".join(lines) + "\n"

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".")
    p.add_argument("--output", default="outputs/workflow_run_summary.md")
    args = p.parse_args()
    result = render(args.root)
    dest = Path(args.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(result)
    print(result)
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as stream:
            stream.write(result)

if __name__ == "__main__":
    main()
