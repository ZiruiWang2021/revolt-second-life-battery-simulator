from __future__ import annotations

import unittest

from revolt_simulator import generate_household_profile, get_scenario, scenario_presets, simulate_battery_storage


class SimulatorTests(unittest.TestCase):
    def test_scenario_presets_are_available(self) -> None:
        presets = scenario_presets()
        self.assertEqual({"renter", "low_income", "backup"}, set(presets))

    def test_scenario_presets_have_bilingual_labels(self) -> None:
        presets = scenario_presets()

        self.assertIn("租房", presets["renter"].label)
        self.assertIn("Renter", presets["renter"].label)
        self.assertIn("低收入", presets["low_income"].label)
        self.assertIn("Low-income", presets["low_income"].label)
        self.assertIn("备电", presets["backup"].label)
        self.assertIn("Backup", presets["backup"].label)

    def test_simulation_summary_reconciles_bill_savings(self) -> None:
        scenario = get_scenario("renter")
        profile = generate_household_profile(days=7, household_type=scenario.household_type)
        result = simulate_battery_storage(
            profile,
            battery=scenario.battery,
            tariff=scenario.tariff,
            charge_quantile=scenario.charge_quantile,
            discharge_quantile=scenario.discharge_quantile,
        )

        self.assertGreater(result.summary.baseline_bill, 0)
        self.assertGreater(result.summary.battery_bill, 0)
        expected_savings = round(result.summary.baseline_bill - result.summary.battery_bill, 2)
        self.assertEqual(expected_savings, result.summary.bill_savings)
        self.assertIn("soc_kwh", result.hourly.columns)
        self.assertIn("battery_to_load_kwh", result.hourly.columns)

    def test_backup_scenario_keeps_reserve(self) -> None:
        scenario = get_scenario("backup")
        profile = generate_household_profile(days=3, household_type=scenario.household_type)
        result = simulate_battery_storage(profile, scenario.battery, scenario.tariff)

        self.assertGreaterEqual(result.hourly["soc_kwh"].min(), scenario.battery.reserve_kwh - 1e-6)
        self.assertGreater(result.summary.backup_reserve_hours_at_avg_load, 0)


if __name__ == "__main__":
    unittest.main()
