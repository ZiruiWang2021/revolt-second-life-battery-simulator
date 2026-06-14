from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path

from .config import get_scenario
from .profiles import generate_household_profile, normalize_profile
from .simulator import simulate_battery_storage


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run a ReVolt second-life battery simulation. / 运行 ReVolt 二次利用电池储能仿真。"
    )
    parser.add_argument(
        "--scenario",
        choices=["renter", "low_income", "backup"],
        default="renter",
        help="Scenario preset: renter, low_income, or backup. / 场景预设：租房、低收入家庭或备电。",
    )
    parser.add_argument("--days", type=int, default=14, help="Generated profile length in days. / 生成负荷天数。")
    parser.add_argument("--input-csv", type=Path, default=None, help="Optional household load CSV. / 可选家庭负荷 CSV。")
    parser.add_argument("--output-csv", type=Path, default=None, help="Optional hourly result CSV path. / 可选小时级结果 CSV 输出路径。")
    parser.add_argument("--capacity-kwh", type=float, default=None, help="Override battery capacity in kWh. / 覆盖电池容量。")
    parser.add_argument("--efficiency", type=float, default=None, help="Override round-trip efficiency. / 覆盖往返效率。")
    args = parser.parse_args(argv)

    scenario = get_scenario(args.scenario)
    battery = scenario.battery
    if args.capacity_kwh is not None:
        battery = replace(battery, capacity_kwh=args.capacity_kwh)
    if args.efficiency is not None:
        battery = replace(battery, roundtrip_efficiency=args.efficiency)

    if args.input_csv:
        profile = normalize_profile(args.input_csv)
    else:
        profile = generate_household_profile(days=args.days, household_type=scenario.household_type)

    result = simulate_battery_storage(
        profile,
        battery=battery,
        tariff=scenario.tariff,
        charge_quantile=scenario.charge_quantile,
        discharge_quantile=scenario.discharge_quantile,
    )

    print(json.dumps(result.summary.as_dict(), indent=2))
    if args.output_csv:
        result.hourly.to_csv(args.output_csv, index=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
