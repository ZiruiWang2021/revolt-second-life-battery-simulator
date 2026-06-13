# Model Assumptions

## Dispatch Logic

The simulator uses a transparent price-threshold dispatch policy:

- Charge when the import price is at or below the selected low-price quantile.
- Discharge when the import price is at or above the selected high-price quantile.
- Keep the battery above the configured reserve state of charge.
- Serve only household load; export revenue is not modelled in this version.

## Efficiency

Round-trip efficiency is split evenly into charge and discharge efficiency:

```text
charge_efficiency = sqrt(roundtrip_efficiency)
discharge_efficiency = sqrt(roundtrip_efficiency)
```

This keeps the accounting simple while still capturing energy losses.

## Payback

Payback is based on annualized bill savings:

```text
annualized_savings = model_period_savings * 365 / days_modelled
payback_years = net_installed_cost / annualized_savings
```

If annualized savings are zero or negative, payback is reported as unavailable.

## Carbon

Carbon impact compares baseline grid import emissions against battery-assisted grid import emissions. Because this version charges from the grid, carbon reduction depends on whether the tariff's low-price hours are also lower-carbon hours.

## Cycle Life

Equivalent full cycles are estimated from total energy charged into the battery divided by nominal capacity. This is suitable for business planning but does not replace a full degradation model.
