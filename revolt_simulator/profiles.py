from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .config import TariffConfig

REQUIRED_COLUMNS = {"timestamp", "load_kwh"}


def normalize_profile(profile: pd.DataFrame | str | Path) -> pd.DataFrame:
    if isinstance(profile, (str, Path)):
        df = pd.read_csv(profile)
    else:
        df = profile.copy()

    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"Load profile is missing required columns: {missing_list}")

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="raise")
    df["load_kwh"] = pd.to_numeric(df["load_kwh"], errors="raise")
    if (df["load_kwh"] < 0).any():
        raise ValueError("load_kwh cannot contain negative values")

    for optional_col in ["import_price_per_kwh", "carbon_kg_per_kwh"]:
        if optional_col in df.columns:
            df[optional_col] = pd.to_numeric(df[optional_col], errors="raise")

    return df.sort_values("timestamp").reset_index(drop=True)


def apply_time_of_use_tariff(profile: pd.DataFrame, tariff: TariffConfig) -> pd.DataFrame:
    df = normalize_profile(profile)
    hours = df["timestamp"].dt.hour

    if "import_price_per_kwh" not in df.columns:
        df["import_price_per_kwh"] = [tariff.price_for_hour(int(hour)) for hour in hours]
    else:
        df["import_price_per_kwh"] = df["import_price_per_kwh"].fillna(
            pd.Series([tariff.price_for_hour(int(hour)) for hour in hours], index=df.index)
        )

    if "carbon_kg_per_kwh" not in df.columns:
        df["carbon_kg_per_kwh"] = [tariff.carbon_for_hour(int(hour)) for hour in hours]
    else:
        df["carbon_kg_per_kwh"] = df["carbon_kg_per_kwh"].fillna(
            pd.Series([tariff.carbon_for_hour(int(hour)) for hour in hours], index=df.index)
        )

    return df


def generate_household_profile(
    days: int = 14,
    household_type: str = "renter",
    start: str = "2026-01-01",
    seed: int = 42,
) -> pd.DataFrame:
    if days <= 0:
        raise ValueError("days must be positive")

    household_type = household_type.lower().replace("-", "_")
    config = {
        "renter": {"base": 0.32, "morning": 0.35, "evening": 0.78, "weekend": 1.06},
        "low_income": {"base": 0.48, "morning": 0.52, "evening": 1.04, "weekend": 1.09},
        "backup": {"base": 0.62, "morning": 0.68, "evening": 1.22, "weekend": 1.12},
    }.get(household_type)
    if config is None:
        raise ValueError("household_type must be one of: renter, low_income, backup")

    rng = np.random.default_rng(seed)
    timestamps = pd.date_range(start=start, periods=days * 24, freq="h")
    hour = timestamps.hour.to_numpy()
    day_of_week = timestamps.dayofweek.to_numpy()

    morning_peak = config["morning"] * np.exp(-0.5 * ((hour - 7) / 2.2) ** 2)
    evening_peak = config["evening"] * np.exp(-0.5 * ((hour - 19) / 2.7) ** 2)
    midday = 0.12 * np.exp(-0.5 * ((hour - 13) / 3.8) ** 2)
    weekend_multiplier = np.where(day_of_week >= 5, config["weekend"], 1.0)
    noise = rng.normal(0.0, config["base"] * 0.035, size=len(timestamps))

    load = (config["base"] + morning_peak + evening_peak + midday + noise) * weekend_multiplier
    load = np.clip(load, 0.08, None)

    return pd.DataFrame(
        {
            "timestamp": timestamps,
            "load_kwh": np.round(load, 3),
        }
    )
