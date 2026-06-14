from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TariffConfig:
    """Simple time-of-use tariff and paired grid carbon assumptions."""

    off_peak_price: float = 0.16
    shoulder_price: float = 0.27
    peak_price: float = 0.44
    off_peak_carbon: float = 0.24
    shoulder_carbon: float = 0.38
    peak_carbon: float = 0.53
    off_peak_start_hour: int = 0
    off_peak_end_hour: int = 6
    peak_start_hour: int = 16
    peak_end_hour: int = 21

    def price_for_hour(self, hour: int) -> float:
        if self.off_peak_start_hour <= hour < self.off_peak_end_hour:
            return self.off_peak_price
        if self.peak_start_hour <= hour < self.peak_end_hour:
            return self.peak_price
        return self.shoulder_price

    def carbon_for_hour(self, hour: int) -> float:
        if self.off_peak_start_hour <= hour < self.off_peak_end_hour:
            return self.off_peak_carbon
        if self.peak_start_hour <= hour < self.peak_end_hour:
            return self.peak_carbon
        return self.shoulder_carbon


@dataclass(frozen=True)
class BatteryConfig:
    capacity_kwh: float = 8.0
    roundtrip_efficiency: float = 0.9
    cycle_life: int = 3000
    max_charge_kw: float = 3.0
    max_discharge_kw: float = 3.0
    reserve_fraction: float = 0.15
    initial_soc_fraction: float = 0.50
    installed_cost_per_kwh: float = 125.0
    fixed_installation_cost: float = 650.0
    incentive_fraction: float = 0.0

    @property
    def reserve_kwh(self) -> float:
        return self.capacity_kwh * self.reserve_fraction

    @property
    def upfront_cost(self) -> float:
        variable_cost = self.capacity_kwh * self.installed_cost_per_kwh
        return variable_cost + self.fixed_installation_cost

    @property
    def net_cost(self) -> float:
        return self.upfront_cost * (1.0 - self.incentive_fraction)


@dataclass(frozen=True)
class ScenarioPreset:
    name: str
    label: str
    audience: str
    household_type: str
    battery: BatteryConfig
    tariff: TariffConfig
    charge_quantile: float = 0.35
    discharge_quantile: float = 0.70


def scenario_presets() -> dict[str, ScenarioPreset]:
    base_tariff = TariffConfig()
    return {
        "renter": ScenarioPreset(
            name="renter",
            label="租房用户 / Renter",
            audience="面向公寓和小户型的便携式或租赁式电池系统。 / Portable or lease-style battery system for apartments and small homes.",
            household_type="renter",
            battery=BatteryConfig(
                capacity_kwh=5.0,
                roundtrip_efficiency=0.88,
                cycle_life=2400,
                max_charge_kw=2.0,
                max_discharge_kw=2.0,
                reserve_fraction=0.12,
                initial_soc_fraction=0.45,
                installed_cost_per_kwh=135.0,
                fixed_installation_cost=350.0,
            ),
            tariff=base_tariff,
            charge_quantile=0.35,
            discharge_quantile=0.70,
        ),
        "low_income": ScenarioPreset(
            name="low_income",
            label="低收入家庭 / Low-income household",
            audience="面向电费减负和高峰负担降低的补贴型系统。 / Incentive-supported system focused on bill savings and peak burden reduction.",
            household_type="low_income",
            battery=BatteryConfig(
                capacity_kwh=9.0,
                roundtrip_efficiency=0.90,
                cycle_life=3000,
                max_charge_kw=3.5,
                max_discharge_kw=3.5,
                reserve_fraction=0.18,
                initial_soc_fraction=0.50,
                installed_cost_per_kwh=110.0,
                fixed_installation_cost=600.0,
                incentive_fraction=0.40,
            ),
            tariff=base_tariff,
            charge_quantile=0.35,
            discharge_quantile=0.68,
        ),
        "backup": ScenarioPreset(
            name="backup",
            label="备电韧性场景 / Backup use case",
            audience="保留更高 SOC 的大容量系统，用于停电韧性。 / Larger battery with protected reserve for outage resilience.",
            household_type="backup",
            battery=BatteryConfig(
                capacity_kwh=14.0,
                roundtrip_efficiency=0.88,
                cycle_life=2600,
                max_charge_kw=5.0,
                max_discharge_kw=5.0,
                reserve_fraction=0.50,
                initial_soc_fraction=0.80,
                installed_cost_per_kwh=125.0,
                fixed_installation_cost=1000.0,
                incentive_fraction=0.20,
            ),
            tariff=base_tariff,
            charge_quantile=0.35,
            discharge_quantile=0.75,
        ),
    }


def get_scenario(name: str) -> ScenarioPreset:
    presets = scenario_presets()
    key = name.lower().replace("-", "_")
    if key not in presets:
        available = ", ".join(sorted(presets))
        raise KeyError(f"Unknown scenario '{name}'. Available scenarios: {available}")
    return presets[key]
