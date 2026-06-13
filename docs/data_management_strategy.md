# Data Management Strategy

## Objective

The simulator should be easy to audit, safe to use with household energy data, and ready to evolve from demo inputs to field deployment telemetry.

## Data Domains

| domain | examples | owner |
| --- | --- | --- |
| Household load | Hourly kWh demand, timestamps, optional meter IDs | Customer or program partner |
| Tariff | Import price, time-of-use bands, demand response events | Utility or tariff data provider |
| Grid carbon | Hourly carbon intensity, regional grid zone | Public grid data source or utility |
| Battery asset | Capacity, chemistry, state of health, cycle life, pack source | ReVolt operations |
| Simulation output | Savings, payback, carbon impact, cycle use, backup hours | ReVolt analytics |
| Field telemetry | SOC, charge/discharge, temperature, faults | ReVolt device platform |

## Input Contract

Minimum customer-provided simulation data:

| column | required | validation |
| --- | --- | --- |
| `timestamp` | yes | Parseable datetime, sorted after ingestion. |
| `load_kwh` | yes | Numeric, non-negative. |
| `import_price_per_kwh` | no | Numeric, non-negative; tariff preset fills missing values. |
| `carbon_kg_per_kwh` | no | Numeric, non-negative; carbon preset fills missing values. |

## Data Quality Rules

- Reject negative load, price, or carbon values.
- Flag missing hours and duplicated timestamps before production use.
- Keep raw uploaded data separate from transformed simulation data.
- Store scenario assumptions with every result so outputs can be reproduced.
- Version model logic and tariff assumptions.
- Reconcile dashboard KPIs against exported hourly output.

## Privacy And Security

Household load profiles can reveal occupancy and behavior. A production deployment should:

- Minimize personally identifiable information in simulation files.
- Use account IDs instead of names or addresses in analytical datasets.
- Encrypt stored customer files and field telemetry.
- Limit access by role for operations, analytics, and support teams.
- Aggregate results for portfolio analysis unless customer-level review is required.
- Set retention windows for uploaded profiles that are not attached to active customers.

## Analytical Data Model

Recommended fact tables for production:

| table | grain | purpose |
| --- | --- | --- |
| `fact_household_load_hourly` | household-hour | Baseline load profile and tariff join. |
| `fact_battery_dispatch_hourly` | asset-hour | SOC, charge, discharge, grid import, emissions. |
| `dim_battery_asset` | asset | Capacity, source pack, grade, chemistry, warranty. |
| `dim_customer_segment` | customer | Renter, low-income program, backup-focused, other. |
| `dim_tariff` | tariff-hour band | Price bands, peak windows, utility region. |
| `fact_simulation_run` | run | Scenario assumptions, model version, KPI outputs. |

## Governance

- Assign a model version to each simulation run.
- Keep a changelog for tariff logic, dispatch logic, and emissions assumptions.
- Use schema checks in CI before accepting new sample datasets.
- Maintain asset traceability from battery source to field deployment.
- Review carbon-impact methodology before using outputs in marketing claims.

## Future Extensions

- Solar PV co-optimization.
- Demand response events and outage simulations.
- Battery degradation curves by depth of discharge and temperature.
- Equity program eligibility and subsidy modelling.
- Fleet-level supply forecast for second-life pack availability.
