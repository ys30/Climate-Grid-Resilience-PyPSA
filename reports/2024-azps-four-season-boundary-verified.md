# Verified 2024 AZPS seasonal missing-boundary exchange audit

## Provenance

- GitHub Actions successful run: https://github.com/ys30/Climate-Grid-Resilience-PyPSA/actions/runs/40994479108
- Artifact: `azps-2024-four-season-boundary`, ID 12950707601
- SHA256: `607c5102e87585f42dd003c6019d950932b41bed323263e20f26401b8a9d8666`
- Primary CSV: `seasonal_azps/seasonal_azps_boundary_summary.csv`
- Four independent *168-hour sampled UTC weeks* of EIA-930 reported bilateral interchange.

| Window | Outside net-import mean MW (negative denotes AZPS export) | Outside-export hours | Outside-import hours | Total outside net export MWh | Outside gross bilateral exchange share |
|---|---:|---:|---:|---:|---:|
| Winter, Jan 15–21 | −1491.922619 | 168 | 0 | 250643 | 34.4397% |
| Spring, Apr 15–21 | −971.601190 | 168 | 0 | 163229 | 33.4478% |
| Summer, Jul 1–7 | −950.928571 | 168 | 0 | 159756 | 19.7099% |
| Autumn, Oct 14–20 | −748.869048 | 163 | 5 | 125810 | 30.3433% |

Autumn includes **126,302 MWh** positive outside-boundary export hours offset by **492 MWh** of imports during 5 hours; net exports total **125,810 MWh**.

Aggregate: **667 of 672 hours show net AZPS exports to missing counterparties**. The outside-boundary exchange sign is persistent across the sampled weeks. Results do not generalize to all hours of 2024 without additional validation.

The missing AZPS bilateral counterparties are IID, LDWP, PACE, PNM, TEPC, WACM, WALC. The four-BA model includes AZPS links to CISO and SRP only. Gross absolute reported interchange is not physical power flow on a specific line or an engineered transfer limit.

## Research significance and limits

Existing four-BA models omit material exchange obligations in each sampled season, potentially affecting simulated available energy. This is **a model-domain inadequacy diagnostic**, not evidence of empirical outages. Sampled-week seasonal variation can be confounded by week-specific dispatch, temperature, imports, holidays and interchange reporting. Avoid presenting these four weeks as full-season means.

Next checks: extend to full months or longer independent weeks, reconcile EIA BA demand definitions to avoid double-counted exports in modeled load, and test cross-season *model* adequacy results with identical structural assumptions.
