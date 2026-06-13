"""ReVolt second-life EV battery storage simulator."""

from .config import BatteryConfig, ScenarioPreset, TariffConfig, get_scenario, scenario_presets
from .profiles import apply_time_of_use_tariff, generate_household_profile, normalize_profile
from .simulator import SimulationResult, SimulationSummary, simulate_battery_storage

__all__ = [
    "BatteryConfig",
    "ScenarioPreset",
    "SimulationResult",
    "SimulationSummary",
    "TariffConfig",
    "apply_time_of_use_tariff",
    "generate_household_profile",
    "get_scenario",
    "normalize_profile",
    "scenario_presets",
    "simulate_battery_storage",
]
