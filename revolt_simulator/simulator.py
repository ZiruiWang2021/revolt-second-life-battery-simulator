from __future__ import annotations

from dataclasses import asdict, dataclass
from math import inf, sqrt

import pandas as pd

from .config import BatteryConfig, TariffConfig
from .profiles import apply_time_of_use_tariff


@dataclass(frozen=True)
class SimulationSummary:
    days_modeled: float
    baseline_bill: float
    battery_bill: float
    bill_savings: float
    annualized_savings: float
    upfront_cost: float
    net_cost_after_incentives: float
    payback_years: float | None
    off_peak_charge_cost: float
    avoided_peak_cost: float
    arbitrage_value: float
    peak_energy_shifted_kwh: float
    peak_grid_reduction_pct: float
    baseline_emissions_kg: float
    battery_emissions_kg: float
    carbon_reduction_kg: float
    annualized_carbon_reduction_kg: float
    equivalent_full_cycles: float
    annualized_equivalent_full_cycles: float
    estimated_cycle_life_years: float | None
    roundtrip_losses_kwh: float
    backup_reserve_hours_at_avg_load: float
    ending_backup_hours_at_avg_load: float

    def as_dict(self) -> dict[str, float | None]:
        return asdict(self)


@dataclass(frozen=True)
class SimulationResult:
    hourly: pd.DataFrame
    summary: SimulationSummary


def simulate_battery_storage(
    load_profile: pd.DataFrame,
    battery: BatteryConfig,
    tariff: TariffConfig | None = None,
    charge_quantile: float = 0.35,
    discharge_quantile: float = 0.70,
) -> SimulationResult:
    if battery.capacity_kwh <= 0:
        raise ValueError("battery.capacity_kwh must be positive")
    if not 0 < battery.roundtrip_efficiency <= 1:
        raise ValueError("battery.roundtrip_efficiency must be within (0, 1]")
    if not 0 <= battery.reserve_fraction < 1:
        raise ValueError("battery.reserve_fraction must be within [0, 1)")
    if not 0 <= battery.initial_soc_fraction <= 1:
        raise ValueError("battery.initial_soc_fraction must be within [0, 1]")
    if not 0 <= charge_quantile <= 1 or not 0 <= discharge_quantile <= 1:
        raise ValueError("charge_quantile and discharge_quantile must be within [0, 1]")

    tariff = tariff or TariffConfig()
    df = apply_time_of_use_tariff(load_profile, tariff)
    hours_per_step = _infer_hours_per_step(df)

    charge_threshold = float(df["import_price_per_kwh"].quantile(charge_quantile))
    discharge_threshold = float(df["import_price_per_kwh"].quantile(discharge_quantile))
    charge_efficiency = sqrt(battery.roundtrip_efficiency)
    discharge_efficiency = sqrt(battery.roundtrip_efficiency)

    min_soc = battery.reserve_kwh
    soc = max(min_soc, battery.capacity_kwh * battery.initial_soc_fraction)
    soc = min(soc, battery.capacity_kwh)

    rows: list[dict[str, float | str | pd.Timestamp]] = []
    total_discharge_from_battery = 0.0
    total_charge_to_battery = 0.0

    for record in df.to_dict("records"):
        timestamp = record["timestamp"]
        load_kwh = float(record["load_kwh"])
        price = float(record["import_price_per_kwh"])
        carbon = float(record["carbon_kg_per_kwh"])

        baseline_grid_import = load_kwh
        baseline_cost = baseline_grid_import * price
        baseline_emissions = baseline_grid_import * carbon

        grid_import_for_battery = 0.0
        battery_to_load = 0.0
        charge_to_battery = 0.0
        discharge_from_battery = 0.0
        action = "idle"

        # The dispatch rule is intentionally transparent for business-model review.
        if price >= discharge_threshold and load_kwh > 0 and soc > min_soc:
            max_battery_draw = min(
                battery.max_discharge_kw * hours_per_step,
                soc - min_soc,
                load_kwh / discharge_efficiency,
            )
            if max_battery_draw > 1e-9:
                discharge_from_battery = max_battery_draw
                battery_to_load = discharge_from_battery * discharge_efficiency
                soc -= discharge_from_battery
                action = "discharge"
        elif price <= charge_threshold and soc < battery.capacity_kwh:
            max_charge = min(
                battery.max_charge_kw * hours_per_step,
                battery.capacity_kwh - soc,
            )
            if max_charge > 1e-9:
                charge_to_battery = max_charge
                grid_import_for_battery = charge_to_battery / charge_efficiency
                soc += charge_to_battery
                action = "charge"

        grid_import_for_load = max(load_kwh - battery_to_load, 0.0)
        total_grid_import = grid_import_for_load + grid_import_for_battery
        battery_cost = total_grid_import * price
        battery_emissions = total_grid_import * carbon

        total_discharge_from_battery += discharge_from_battery
        total_charge_to_battery += charge_to_battery

        rows.append(
            {
                "timestamp": timestamp,
                "load_kwh": load_kwh,
                "import_price_per_kwh": price,
                "carbon_kg_per_kwh": carbon,
                "action": action,
                "soc_kwh": soc,
                "soc_pct": soc / battery.capacity_kwh,
                "battery_to_load_kwh": battery_to_load,
                "charge_to_battery_kwh": charge_to_battery,
                "grid_import_for_battery_kwh": grid_import_for_battery,
                "grid_import_for_load_kwh": grid_import_for_load,
                "grid_import_total_kwh": total_grid_import,
                "baseline_grid_import_kwh": baseline_grid_import,
                "baseline_cost": baseline_cost,
                "battery_cost": battery_cost,
                "baseline_emissions_kg": baseline_emissions,
                "battery_emissions_kg": battery_emissions,
            }
        )

    hourly = pd.DataFrame(rows)
    summary = _build_summary(hourly, battery, hours_per_step, discharge_threshold)
    return SimulationResult(hourly=hourly, summary=summary)


def _infer_hours_per_step(df: pd.DataFrame) -> float:
    if len(df) < 2:
        return 1.0
    deltas = df["timestamp"].sort_values().diff().dropna().dt.total_seconds() / 3600
    median_delta = float(deltas.median())
    return median_delta if median_delta > 0 else 1.0


def _build_summary(
    hourly: pd.DataFrame,
    battery: BatteryConfig,
    hours_per_step: float,
    discharge_threshold: float,
) -> SimulationSummary:
    periods = len(hourly)
    days_modeled = max(periods * hours_per_step / 24.0, 1.0 / 24.0)
    annualization = 365.0 / days_modeled

    baseline_bill = float(hourly["baseline_cost"].sum())
    battery_bill = float(hourly["battery_cost"].sum())
    bill_savings = baseline_bill - battery_bill
    annualized_savings = bill_savings * annualization

    peak_mask = hourly["import_price_per_kwh"] >= discharge_threshold
    peak_baseline_import = float(hourly.loc[peak_mask, "baseline_grid_import_kwh"].sum())
    peak_battery_import = float(hourly.loc[peak_mask, "grid_import_total_kwh"].sum())
    peak_energy_shifted = float(hourly.loc[peak_mask, "battery_to_load_kwh"].sum())
    peak_reduction_pct = (
        (peak_baseline_import - peak_battery_import) / peak_baseline_import
        if peak_baseline_import > 0
        else 0.0
    )

    off_peak_charge_cost = float(
        (
            hourly["grid_import_for_battery_kwh"]
            * hourly["import_price_per_kwh"]
        ).sum()
    )
    avoided_peak_cost = float(
        (
            hourly["battery_to_load_kwh"]
            * hourly["import_price_per_kwh"]
        ).sum()
    )
    arbitrage_value = avoided_peak_cost - off_peak_charge_cost

    baseline_emissions = float(hourly["baseline_emissions_kg"].sum())
    battery_emissions = float(hourly["battery_emissions_kg"].sum())
    carbon_reduction = baseline_emissions - battery_emissions
    annualized_carbon_reduction = carbon_reduction * annualization

    discharged = float(hourly["battery_to_load_kwh"].sum())
    charged_from_grid = float(hourly["grid_import_for_battery_kwh"].sum())
    equivalent_full_cycles = float(hourly["charge_to_battery_kwh"].sum()) / battery.capacity_kwh
    annual_cycles = equivalent_full_cycles * annualization
    cycle_life_years = battery.cycle_life / annual_cycles if annual_cycles > 0 else None
    roundtrip_losses = max(charged_from_grid - discharged, 0.0)

    payback = battery.net_cost / annualized_savings if annualized_savings > 0 else None
    avg_hourly_load = max(float(hourly["load_kwh"].mean()), 1e-9)
    reserve_hours = battery.reserve_kwh * sqrt(battery.roundtrip_efficiency) / avg_hourly_load
    ending_soc = float(hourly["soc_kwh"].iloc[-1]) if len(hourly) else battery.reserve_kwh
    ending_backup_hours = ending_soc * sqrt(battery.roundtrip_efficiency) / avg_hourly_load

    return SimulationSummary(
        days_modeled=round(days_modeled, 2),
        baseline_bill=round(baseline_bill, 2),
        battery_bill=round(battery_bill, 2),
        bill_savings=round(bill_savings, 2),
        annualized_savings=round(annualized_savings, 2),
        upfront_cost=round(battery.upfront_cost, 2),
        net_cost_after_incentives=round(battery.net_cost, 2),
        payback_years=None if payback is None or payback == inf else round(payback, 2),
        off_peak_charge_cost=round(off_peak_charge_cost, 2),
        avoided_peak_cost=round(avoided_peak_cost, 2),
        arbitrage_value=round(arbitrage_value, 2),
        peak_energy_shifted_kwh=round(peak_energy_shifted, 2),
        peak_grid_reduction_pct=round(peak_reduction_pct * 100, 2),
        baseline_emissions_kg=round(baseline_emissions, 2),
        battery_emissions_kg=round(battery_emissions, 2),
        carbon_reduction_kg=round(carbon_reduction, 2),
        annualized_carbon_reduction_kg=round(annualized_carbon_reduction, 2),
        equivalent_full_cycles=round(equivalent_full_cycles, 3),
        annualized_equivalent_full_cycles=round(annual_cycles, 1),
        estimated_cycle_life_years=None if cycle_life_years is None else round(cycle_life_years, 1),
        roundtrip_losses_kwh=round(roundtrip_losses, 2),
        backup_reserve_hours_at_avg_load=round(reserve_hours, 2),
        ending_backup_hours_at_avg_load=round(ending_backup_hours, 2),
    )
