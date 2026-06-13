# Building a Second-Life EV Battery Storage Simulator

GitHub link: `https://github.com/ZiruiWang2021/revolt-second-life-battery-simulator`

## Problem

Second-life EV batteries are attractive because they can reduce the cost of residential storage while extending the useful life of battery materials. The hard question is whether a reused battery actually creates enough value for a household after installation cost, efficiency losses, limited cycle life, and user needs are considered.

I built a Python simulator and dashboard to answer that question for three use cases:

- renters who need a smaller and more portable system
- low-income households where incentives and bill savings matter most
- backup-focused households that value reserve energy during outages

## Why It Matters

Residential battery storage is usually discussed as a technical product, but adoption depends on economics and trust. A household wants to know whether the system saves money, how long payback takes, what happens during peak pricing, and whether the battery still has enough life to be worth installing.

For a second-life battery company, the same model also supports product strategy:

- which customer segment has the strongest value proposition
- how installation cost changes payback
- how much reserve SOC should be protected for backup use
- whether carbon claims are credible under grid charging
- where supply chain and data quality risks affect the business case

## My Approach

I designed the project as a small but complete engineering product:

1. A core Python package handles the simulation.
2. A CLI produces JSON output for repeatable scenario runs.
3. A Streamlit dashboard lets users adjust battery, tariff, and scenario assumptions.
4. Unit tests verify the key accounting logic.
5. Documentation explains model assumptions, supply chain strategy, and data management.
6. GitHub Actions runs the tests automatically.

The model is intentionally transparent. Instead of hiding the logic inside a black-box optimizer, it uses a readable hourly dispatch rule:

- charge during low-price hours
- discharge during high-price hours
- respect battery capacity, power limits, efficiency, and reserve state of charge

That makes the simulator easier to explain in an interview and easier to improve later.

## Technical Implementation

The project is split into a few modules:

| component | responsibility |
| --- | --- |
| `config.py` | Battery, tariff, and scenario dataclasses. |
| `profiles.py` | Load profile generation, CSV validation, tariff enrichment. |
| `simulator.py` | Hourly dispatch, cost accounting, emissions accounting, KPI summary. |
| `dashboard/app.py` | Streamlit controls, KPI cards, Plotly charts, CSV download. |
| `tests/` | Unit tests for scenario availability, bill reconciliation, and backup reserve behavior. |

The simulator compares two worlds:

1. Baseline: the household imports all load from the grid.
2. Battery case: the household still imports load, but the battery charges during cheaper hours and discharges during expensive hours.

Each hour tracks:

- household load
- import price
- carbon intensity
- battery state of charge
- battery energy delivered to the load
- grid energy used to charge the battery
- baseline cost and battery-assisted cost
- baseline emissions and battery-assisted emissions

The summary outputs include:

- bill savings
- annualized savings
- payback period
- arbitrage value
- peak energy shifted
- peak grid reduction
- carbon reduction
- equivalent full cycles
- estimated cycle-life years
- backup reserve hours

## Results / Demo

For a 7-day renter scenario, the simulator produced:

```json
{
  "baseline_bill": 34.62,
  "battery_bill": 32.47,
  "bill_savings": 2.15,
  "annualized_savings": 112.17,
  "payback_years": 9.14,
  "arbitrage_value": 2.15,
  "peak_energy_shifted_kwh": 51.48,
  "peak_grid_reduction_pct": 22.76,
  "carbon_reduction_kg": 2.25
}
```

The dashboard turns those outputs into a more interview-friendly demo. A user can choose the scenario, adjust capacity and efficiency, change tariff assumptions, upload a household load CSV, and download hourly dispatch results.

## Limitations

This is a planning simulator, not a full battery physics model.

Current limitations:

- no solar PV co-optimization
- no export revenue
- no demand charges
- no stochastic outage modelling
- no detailed thermal or electrochemical degradation model
- no market-specific permitting or interconnection cost
- no real-time utility API integration

The carbon estimate is also simplified. It is useful for comparing assumptions, but production carbon claims would need region-specific hourly grid intensity data and careful review.

## What I Learned

The most important lesson was that second-life storage is not just a battery engineering problem. It is a system design problem involving:

- technical constraints like efficiency, power limits, and cycle life
- customer constraints like affordability and backup expectations
- market constraints like tariff structure and incentives
- operational constraints like pack sourcing, grading, warranty, and data traceability

I also learned that a good engineering portfolio project should have two layers. A recruiter should understand the value in under a minute, while a technical interviewer should be able to inspect the code and see real modelling decisions.

## GitHub Link

`https://github.com/ZiruiWang2021/revolt-second-life-battery-simulator`
