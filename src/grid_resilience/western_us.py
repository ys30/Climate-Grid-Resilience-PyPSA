"""Western US climate-grid resilience experiment with observed load and ERA5 weather.

Demand: user-supplied official EIA-930 six-month BALANCE CSV.
Weather: Open-Meteo ERA5 archive API (downloaded at runtime).
Grid: explicitly illustrative three-BA intertie topology and capacity assumptions.
No claim that this is a calibrated WECC power-flow or outage forecast.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import time
import socket
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

import numpy as np
import pandas as pd

BAS = {
    "CISO": (36.17, -119.75),  # California ISO, representative central CA coordinate
    "AZPS": (33.45, -112.07),  # Arizona Public Service, Phoenix
    "BPAT": (45.52, -122.68),  # Bonneville Power Administration, Portland
}
WEATHER = ("temperature_2m", "wind_speed_100m", "shortwave_radiation")
INTERTIES = [("CISO", "AZPS"), ("CISO", "BPAT")]
SCENARIOS = {
    "observed_weather": (0.0, 0.0, 1.0),
    "heat_plus_4c": (4.0, 0.0, 1.0),
    "compound_heat_wind_derating": (4.0, 0.30, 0.65),
}
# (temperature increment [°C], wind availability penalty, intertie rating multiplier)


def _column(df, *possibilities):
    normalized = {str(c).strip().lower().replace("_", " "): c for c in df.columns}
    for name in possibilities:
        if name.lower() in normalized:
            return normalized[name.lower()]
    raise ValueError(f"Required field missing; expected one of {possibilities}; got {list(df.columns)}")


def load_eia930(path, start, end, bas=BAS):
    """Read EIA-930 BALANCE records, using UTC *hour ending* timestamps.

    EIA's published table may carry multiple submissions; duplicate BA/time values
    are rejected rather than choosing one silently.
    """
    data = pd.read_csv(path, low_memory=False)
    if {"timestamp", *bas}.issubset(data.columns):
        dates = pd.to_datetime(data["timestamp"], utc=True, errors="raise")
        if dates.duplicated().any():
            raise ValueError("Duplicate hourly timestamps in API file")
        frame = data[list(bas)].apply(pd.to_numeric, errors="raise")
        frame.index = dates
        idx = pd.date_range(pd.Timestamp(start, tz="UTC"),
                            pd.Timestamp(end, tz="UTC"), freq="h", inclusive="left")
        result = frame.reindex(idx)
        if result.isna().any().any() or (result <= 0).any().any():
            raise ValueError("Incomplete or invalid EIA API load series")
        return result
    ba = _column(data, "Balancing Authority", "Balancing Authority Code", "ba")
    t = _column(data, "UTC Time", "datetime_utc", "timestamp")
    demand = _column(data, "Demand (MW)", "demand_mw", "Demand")
    x = data[[ba, t, demand]].copy()
    x.columns = ["ba", "hour_ending_utc", "demand_mw"]
    x = x[x.ba.isin(bas)]
    x["timestamp"] = pd.to_datetime(x.hour_ending_utc, utc=True, errors="coerce") - pd.Timedelta(hours=1)
    x["demand_mw"] = pd.to_numeric(x.demand_mw, errors="coerce")
    start, end = pd.Timestamp(start, tz="UTC"), pd.Timestamp(end, tz="UTC")
    x = x[(x.timestamp >= start) & (x.timestamp < end)]
    if x[["timestamp", "demand_mw"]].isna().any().any() or (x.demand_mw <= 0).any():
        raise ValueError("Missing, nonnumeric or nonpositive EIA demand; inspect source and corrections")
    if x.duplicated(["ba", "timestamp"]).any():
        raise ValueError("Duplicate BA/hour records found; select a validated EIA-930 publication")
    expected = pd.date_range(start, end, freq="h", inclusive="left", tz="UTC")
    out = x.pivot(index="timestamp", columns="ba", values="demand_mw").reindex(index=expected, columns=list(bas))
    if out.isna().any().any():
        missing = out.isna().sum()
        raise ValueError(f"Incomplete observed BA load; missing hourly records: {missing.to_dict()}")
    return out.astype(float)


def fetch_era5(start, end, cache_dir, bas=BAS):
    """Open-Meteo archive ERA5, with UTC hourly timestamps and local source cache."""
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    end_inclusive = (pd.Timestamp(end) - pd.Timedelta(hours=1)).date().isoformat()
    start_day = pd.Timestamp(start).date().isoformat()
    frames = {}
    for ba, (lat, lon) in bas.items():
        path = cache_dir / f"era5_{ba}_{start_day}_{end_inclusive}.json"
        if not path.exists():
            params = dict(latitude=lat, longitude=lon, start_date=start_day,
                          end_date=end_inclusive, hourly=",".join(WEATHER),
                          models="era5", timezone="GMT")
            url = "https://archive-api.open-meteo.com/v1/archive?" + urlencode(params)
            last_error = None
            for attempt in range(1, 5):
                try:
                    with urlopen(url, timeout=120) as response:
                        blob = response.read()
                    candidate = json.loads(blob)
                    if "hourly" not in candidate:
                        raise ValueError(f"ERA5 {ba}: missing hourly data in API response")
                    # Write only a complete, valid response to the reusable cache.
                    temporary = path.with_suffix(".json.tmp")
                    temporary.write_bytes(blob)
                    temporary.replace(path)
                    last_error = None
                    break
                except (OSError, TimeoutError, socket.timeout) as exc:
                    last_error = exc
                    if attempt < 4:
                        time.sleep(min(2 ** attempt, 12))
            if last_error is not None:
                raise RuntimeError(f"ERA5 {ba}: 4 attempts failed; last transport error: {last_error}") from last_error
        obj = json.loads(path.read_text())
        if "hourly" not in obj:
            raise ValueError(f"ERA5 response missing hourly data for {ba}: {obj}")
        frame = pd.DataFrame(obj["hourly"])
        frame["timestamp"] = pd.to_datetime(frame["time"], utc=True)
        frame = frame.set_index("timestamp").drop(columns=["time"])
        for variable in WEATHER:
            if variable not in frame or frame[variable].isna().any():
                raise ValueError(f"ERA5 {ba}: missing {variable}")
        frames[ba] = frame.loc[:, list(WEATHER)]
    return frames


def build_model(demand, weather, scenario, reserve_margin=0.18, intertie_fraction=0.10, capacities=None, bas=BAS, interties=INTERTIES, local_shedding=False):
    """PyPSA linear dispatch with load shedding and illustrative links.

    Thermal capacities are explicitly *inferred* from each BA's observed peak,
    not taken from generator inventories. Weather-based wind and solar production
    factors and thermal derating coefficients are assumptions, not calibration.
    """
    import pypsa

    temp_add, wind_penalty, link_mult = SCENARIOS[scenario]
    timestamps = demand.index
    n = pypsa.Network()
    n.set_snapshots(timestamps.tz_convert(None))
    for ba in bas:
        series = weather[ba].reindex(timestamps)
        if series.isna().any().any():
            raise ValueError(f"Weather timestamps do not cover demand for {ba}")
        temp = series.temperature_2m.to_numpy(dtype=float) + temp_add
        wind = series.wind_speed_100m.to_numpy(dtype=float)
        solar = series.shortwave_radiation.to_numpy(dtype=float)
        # Stress-response coefficients are experimental assumptions.
        load_factor = 1 + 0.012 * np.maximum(temp - 30.0, 0)
        observed_demand = demand[ba].to_numpy(dtype=float)
        # Relative to observed weather baseline to avoid double counting heat load:
        base_temp = series.temperature_2m.to_numpy(dtype=float)
        reference = 1 + 0.012 * np.maximum(base_temp - 30.0, 0)
        load = observed_demand * load_factor / reference
        peak = float(demand[ba].max())
        capacity = peak * (1 + reserve_margin)
        n.add("Bus", ba)
        if local_shedding:
            # Isolate unmet demand behind a one-way supply-to-load link.
            # Virtual unserved generation cannot flow back into the BA grid.
            n.add("Bus", f"{ba}_load_bus")
            n.add("Link", f"{ba}_supply_to_load", bus0=ba, bus1=f"{ba}_load_bus",
                  p_nom=peak * 20, p_min_pu=0, efficiency=1.0)
        n.add("Load", f"{ba}_demand", bus=f"{ba}_load_bus" if local_shedding else ba, p_set=load)
        # illustrative capacity mix (70% thermal, 20% wind, 10% solar)
        thermal_avail = np.clip(1 - 0.012 * np.maximum(temp - 35, 0), 0.40, 1.0)
        wind_avail = np.clip((wind - 3) / 12, 0, 1) * (1 - wind_penalty)
        solar_avail = np.clip(solar / 900, 0, 1)
        for tech, share, cost, availability in [
            ("thermal", 0.7, 75.0, thermal_avail),
            ("wind", 0.2, 3.0, wind_avail),
            ("solar", 0.1, 1.0, solar_avail),
        ]:
            p_nom = capacity * share if capacities is None else capacities.get((ba, tech), 0.0)
            n.add("Generator", f"{ba}_{tech}", bus=ba,
                  p_nom=p_nom, marginal_cost=cost,
                  p_max_pu=availability)
        if capacities is not None:
            for tech, marginal_cost in [("hydro", 20), ("nuclear", 15), ("geothermal", 25)]:
                nameplate = capacities.get((ba, tech), 0.0)
                if nameplate > 0:
                    n.add("Generator", f"{ba}_{tech}", bus=ba,
                          p_nom=nameplate, marginal_cost=marginal_cost)
        n.add("Generator", f"{ba}_unserved", bus=f"{ba}_load_bus" if local_shedding else ba, p_nom=peak * 10,
              marginal_cost=10000.0)
    # Illustrative capacity-limited exchange, not measured electrical line parameters.
    for a, b in interties:
        cap = min(float(demand[a].max()), float(demand[b].max()))
        n.add("Link", f"{a}_{b}", bus0=a, bus1=b,
              p_nom=cap * intertie_fraction * link_mult, p_min_pu=-1,
              efficiency=1, marginal_cost=0.01)
    return n


def run(eia_csv, start, end, output="outputs/western_us", cache="data/cache",
        reserve_margin=0.18, intertie_fraction=0.10, eia860_capacities=None, local_shedding=False):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    demand = load_eia930(eia_csv, start, end)
    weather = fetch_era5(start, end, cache)
    source_sha = hashlib.sha256(Path(eia_csv).read_bytes()).hexdigest()
    capacities = None
    if eia860_capacities:
        from .capacity_adapter import load_eia860_capacities
        capacities = load_eia860_capacities(eia860_capacities)
    if capacities is not None:
        unsupported = {(ba, tech): mw for (ba, tech), mw in capacities.items()
                       if tech in {"storage", "other"} and mw > 0}
        if unsupported:
            raise ValueError("EIA-860 includes storage/other capacity that this dispatch model cannot represent; implement storage energy/SOC and review other fuel sources before solving: " + str(unsupported))
    rows = []
    profiles = []
    for name in SCENARIOS:
        n = build_model(demand, weather, name, reserve_margin, intertie_fraction, capacities, local_shedding=local_shedding)
        status, termination = n.optimize(solver_name="highs")
        if status != "ok" or termination != "optimal":
            raise RuntimeError(f"Optimization failed for {name}: {status} / {termination}")
        for ba in BAS:
            shortfall = n.generators_t.p[f"{ba}_unserved"].to_numpy(dtype=float)
            profiles.extend(dict(scenario=name, ba=ba, timestamp=t.isoformat(),
                                 unserved_mw=float(v)) for t, v in zip(demand.index, shortfall))
            rows.append(dict(scenario=name, ba=ba,
                             unserved_energy_mwh=float(shortfall.sum()),
                             peak_shortfall_mw=float(shortfall.max()),
                             shortage_hours=int((shortfall > 1e-4).sum())))
        n.export_to_netcdf(output / f"solved_{name}.nc")
    pd.DataFrame(rows).to_csv(output / "metrics.csv", index=False)
    pd.DataFrame(profiles).to_csv(output / "hourly_unserved.csv", index=False)
    demand.rename_axis("timestamp").to_csv(output / "eia930_demand_aligned.csv")
    pd.concat(weather, axis=1).to_csv(output / "era5_weather_aligned.csv")
    manifest = {
        "region": "CISO+AZPS+BPAT illustrative 3-BA western-US subnetwork (NOT all WECC)",
        "source_eia930": "https://www.eia.gov/electricity/gridmonitor/",
        "source_eia930_sha256": source_sha,
        "source_weather": "Open-Meteo archive ERA5 (models=era5)",
        "start_utc": start, "end_exclusive_utc": end,
        "hour_ending_to_hour_start": "CSV BALANCE only; EIA API timestamp is already hour-start",
        "grid_parameters": "hypothetical topology, capacities, mix, operating costs",
        "reserve_margin_assumed": reserve_margin,
        "intertie_fraction_assumed": intertie_fraction,
        "climate_scenarios": SCENARIOS,
        "capacity_source": "EIA-860 nameplate" if capacities is not None else "synthetic peak + reserve margin",
        "eia860_capacity_csv": str(eia860_capacities) if eia860_capacities else None,
        "analysis_type": "linear capacity-constrained electricity adequacy experiment",
        "local_shedding_isolated": local_shedding,
        "not": ["actual WECC AC/DC power flow", "outage probability estimate",
                "validated generator/network capacity", "ERA5 climate-change projection"]
    }
    (output / "provenance.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return pd.DataFrame(rows)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--eia-csv", required=True,
                   help="Official EIA-930 six-month BALANCE CSV (local path)")
    p.add_argument("--start", default="2024-07-01")
    p.add_argument("--end", default="2024-07-08", help="UTC, exclusive")
    p.add_argument("--output", default="outputs/western_us")
    p.add_argument("--cache", default="data/cache")
    p.add_argument("--eia860-capacities", default=None, help="Processed EIA-860 BA/technology capacity CSV")
    p.add_argument("--reserve-margin", type=float, default=0.18)
    p.add_argument("--intertie-fraction", type=float, default=0.10)
    p.add_argument("--local-shedding", action="store_true", help="One-way load-bus structure prevents exports of unmet demand")
    a = p.parse_args()
    if not 0 <= a.reserve_margin <= 2 or not 0 <= a.intertie_fraction <= 1:
        p.error("reserve-margin must be 0..2; intertie-fraction must be 0..1")
    print(run(a.eia_csv, a.start, a.end, a.output, a.cache,
              a.reserve_margin, a.intertie_fraction, a.eia860_capacities, a.local_shedding).to_string(index=False))


if __name__ == "__main__":
    main()
