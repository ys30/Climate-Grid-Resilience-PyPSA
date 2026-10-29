"""Figures and aggregate scenario comparison for the western-US screening model."""
from pathlib import Path
import argparse
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def summarize(folder):
    folder = Path(folder)
    metrics = pd.read_csv(folder / "metrics.csv")
    series = pd.read_csv(folder / "hourly_unserved.csv", parse_dates=["timestamp"])
    required = {"scenario", "ba", "unserved_energy_mwh", "peak_shortfall_mw", "shortage_hours"}
    if not required.issubset(metrics):
        raise ValueError("Missing scenario metrics")
    if (metrics["unserved_energy_mwh"] < -1e-5).any():
        raise ValueError("Negative unserved energy")
    combined = metrics.groupby("scenario", as_index=False).agg(
        unserved_energy_mwh=("unserved_energy_mwh", "sum"),
        peak_ba_shortfall_mw=("peak_shortfall_mw", "max"),
        ba_shortage_hours=("shortage_hours", "sum"),
    )
    total = series.groupby(["scenario", "timestamp"], as_index=False).unserved_mw.sum()
    system_peak = total.groupby("scenario").unserved_mw.max().rename("system_peak_shortfall_mw")
    duration = total.assign(shortage=total.unserved_mw.gt(1e-4)).groupby("scenario").shortage.sum().rename("system_shortage_hours")
    combined = combined.merge(system_peak, on="scenario").merge(duration, on="scenario")
    combined.to_csv(folder / "system_metrics.csv", index=False)
    fig, ax = plt.subplots(figsize=(10, 4.5))
    for label, group in total.groupby("scenario"):
        ax.plot(group.timestamp, group.unserved_mw, label=label)
    ax.set(xlabel="UTC time", ylabel="Modeled unserved power (MW)",
           title="Screening model, illustrative network (not observed outages)")
    ax.legend(fontsize=8)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(folder / "modeled_unserved_power.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    combined.plot.bar(x="scenario", y="unserved_energy_mwh", ax=ax, legend=False)
    ax.set(ylabel="Modeled unserved energy (MWh)",
           title="Scenario comparison — assumed transfer limits and availability")
    ax.tick_params(axis="x", labelrotation=15)
    fig.tight_layout()
    fig.savefig(folder / "modeled_unserved_energy.png", dpi=160)
    plt.close(fig)
    return combined

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", default="outputs/western_us")
    a = p.parse_args()
    print(summarize(a.output).to_string(index=False))

if __name__ == "__main__":
    main()
