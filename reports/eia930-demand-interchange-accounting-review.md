# EIA-930 demand, generation, interchange accounting — official definition review

## Official sources

- EIA, About the EIA-930 data: https://www.eia.gov/electricity/930-content/about.html
- EIA-930 reporting instructions: https://omb.report/icr/202112-1905-001/doc/117324000
- PUDL EIA-930 field provenance and adjustments: https://data.catalyst.coop/preview/pudl/out_eia930__hourly_operations

## Accounting and sign

EIA defines hourly balancing-authority **Demand** as a calculated load from metered net generation less total net metered interchange, where positive net interchange means **exports** from the BA. Thus:

`D = NG - net_exports = NG + net_imports`.

EIA explicitly notes generation and interchange are measured/reportable fields, while demand is normally calculated; zero residuals of the three series in 168 hours confirm reported *internal accounting identity*, NOT independent third-party validation or accuracy of a PyPSA dispatch prediction.

Physical tie-line measurements and adjusted accounting for pseudo-ties/dynamic scheduling require care; the same BA exchange may be present in multiple differently represented source series and can undergo EIA adjustments.

## Implication for 2024 AZPS external-boundary sensitivity

The 2024-07-01 to 2024-07-08 UTC week has 159,756 MWh of reported net exports across seven AZPS exchange counterparties excluded from the four-BA graph. Because EIA-930 reported BA Demand is normally calculated **net of export flow**, these exports are not inherently included as native BA demand. An **isolated net export obligation** can therefore be a meaningful *ex-post boundary-load stress* for a simplified resource model that excludes those partners.

However this experiment is **not** automatically calibrated, accurate, or free from double-counting:

1. Carefully separate the exchange to **modeled** CISO and SRP links from exports to **nonmodeled** partners, and never add the same modeled transfer a second time.
2. The observed bilateral exchange profile is a *historical operation outcome*, not a fixed transmission path capacity, and cannot be assumed to remain unchanged in extreme-weather counterfactuals.
3. Physical metering and EIA adjustment for pseudo-ties/dynamic scheduling can change apparent demand and exchange allocation.
4. If a later model includes WALC, LDWP and other BA loads/interconnections, remove the corresponding external export sink; otherwise their load would be represented twice.
5. Unmet native load and unmet hypothetical export obligations have separate meanings and must never be combined or called measured outages.

## Research decision

**Retain** the July boundary-export sensitivity as a *diagnostic upper-level network-boundary stress*, subject to these caveats. Do **not** treat its +20,442 MWh native shortfall change as empirical avoided energy not served, or make an unqualified claim that adding reported exports is physically validated.

Priority: add model-bus/topology scope checks to avoid count duplication if additional partners enter the simulation; follow with generator availability uncertainty and final portfolio documentation.
