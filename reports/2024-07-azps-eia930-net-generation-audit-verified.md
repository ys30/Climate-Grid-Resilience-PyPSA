# Verified AZPS EIA-930 reported net-generation balance, July 1–7, 2024 UTC

## Data and reproducibility
- GitHub Actions: https://github.com/ys30/Climate-Grid-Resilience-PyPSA/actions/runs/40943958855
- Status: success (this data workflow; a separate CI unit test at this commit failed and was subsequently fixed)
- Output archive: `azps-observed-eia930-bilateral-exchanges`, artifact ID `12928242785`, SHA256 `1a86c4252a7eabb8812b4e1466a77cf3e02f70fb6e0863ec5072ef4710667f81`
- Observed EIA datasets: region-data hourly D (demand), region-data hourly NG (reported net generation), interchange-data AZPS directional bilateral flows.

## Verified hourly audit

| Quantity | Result |
| --- | ---: |
| UTC hours aligned | 168 |
| Mean independently downloaded AZPS NG | 3102.154761904762 MW |
| Mean NG implied by demand minus net imports | 3102.154761904762 MW |
| Mean hourly balance residual | 0 MW |
| Maximum absolute hourly residual | 0 MW |
| 95th percentile absolute hourly residual | 0 MW |

The identity here is `D - net imports - NG = 0`, where AZPS-reported bilateral interchange sign is reversed to obtain net imports. The 168 hourly zero residuals establish **internal accounting consistency** for these EIA-930 reported fields. They do **not** establish that NG was physically measured independently of the demand/interchange values; reported NG may be calculated from the same inputs or adjusted under the same reporting conventions. They also do not validate installed EIA-860 firm capacity or physical AZPS-SRP transfer ratings.

## Implications

AZPS substantially depends on exchanges with SRP in this week. The simplified model's three-BA versus four-BA simulated shortages are therefore sensitive to omitted neighbor representation. These simulation shortfalls are not historical outages.

## Next research-grade checks

- Quantify whether adding the SRP generator fleet versus increasing assumed AZPS-SRP transfers drives the four-BA model improvement.
- Identify EIA-930 field definitions and whether respondent NG is calculated or directly supplied.
- Acquire engineering transfer limits from a documented source, not the maximum observed hourly flow; add storage only with energy capacity and state-of-charge constraints.
