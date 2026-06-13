from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from revolt_simulator import generate_household_profile, get_scenario, scenario_presets, simulate_battery_storage


st.set_page_config(
    page_title="ReVolt Second-Life Battery Simulator",
    page_icon="battery",
    layout="wide",
)


@st.cache_data(show_spinner=False)
def load_uploaded_profile(uploaded_file) -> pd.DataFrame:
    return pd.read_csv(uploaded_file)


def format_money(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"${value:,.0f}"


def format_years(value: float | None) -> str:
    if value is None:
        return "No payback"
    return f"{value:.1f} years"


presets = scenario_presets()

st.title("ReVolt Second-Life EV Battery Storage Simulator")

with st.sidebar:
    scenario_name = st.selectbox(
        "Use case",
        options=list(presets.keys()),
        format_func=lambda key: presets[key].label,
    )
    scenario = get_scenario(scenario_name)
    st.caption(scenario.audience)

    uploaded = st.file_uploader("Household load CSV", type=["csv"])
    days = st.slider("Generated profile days", min_value=2, max_value=60, value=14, step=1)

    st.divider()
    st.subheader("Battery")
    capacity = st.slider("Capacity (kWh)", 2.0, 25.0, scenario.battery.capacity_kwh, 0.5)
    efficiency = st.slider("Round-trip efficiency", 0.70, 0.98, scenario.battery.roundtrip_efficiency, 0.01)
    reserve = st.slider("Reserve state of charge", 0.0, 0.75, scenario.battery.reserve_fraction, 0.01)
    cycle_life = st.slider("Cycle life", 1000, 8000, scenario.battery.cycle_life, 100)
    cost_per_kwh = st.slider("Installed cost ($/kWh)", 50.0, 300.0, scenario.battery.installed_cost_per_kwh, 5.0)
    fixed_cost = st.slider("Fixed install cost ($)", 0.0, 3000.0, scenario.battery.fixed_installation_cost, 50.0)
    incentive = st.slider("Incentive", 0.0, 0.75, scenario.battery.incentive_fraction, 0.01)

    st.divider()
    st.subheader("Tariff")
    off_peak_price = st.slider("Off-peak price ($/kWh)", 0.05, 0.40, scenario.tariff.off_peak_price, 0.01)
    shoulder_price = st.slider("Shoulder price ($/kWh)", 0.08, 0.55, scenario.tariff.shoulder_price, 0.01)
    peak_price = st.slider("Peak price ($/kWh)", 0.12, 0.90, scenario.tariff.peak_price, 0.01)

battery = replace(
    scenario.battery,
    capacity_kwh=capacity,
    roundtrip_efficiency=efficiency,
    reserve_fraction=reserve,
    cycle_life=cycle_life,
    installed_cost_per_kwh=cost_per_kwh,
    fixed_installation_cost=fixed_cost,
    incentive_fraction=incentive,
)
tariff = replace(
    scenario.tariff,
    off_peak_price=off_peak_price,
    shoulder_price=shoulder_price,
    peak_price=peak_price,
)

try:
    if uploaded is not None:
        profile = load_uploaded_profile(uploaded)
    else:
        profile = generate_household_profile(days=days, household_type=scenario.household_type)

    result = simulate_battery_storage(
        profile,
        battery=battery,
        tariff=tariff,
        charge_quantile=scenario.charge_quantile,
        discharge_quantile=scenario.discharge_quantile,
    )
except Exception as exc:
    st.error(f"Simulation failed: {exc}")
    st.stop()

summary = result.summary
hourly = result.hourly.copy()
hourly["date"] = hourly["timestamp"].dt.date

metric_cols = st.columns(6)
metric_cols[0].metric("Bill savings", format_money(summary.bill_savings))
metric_cols[1].metric("Annual savings", format_money(summary.annualized_savings))
metric_cols[2].metric("Payback", format_years(summary.payback_years))
metric_cols[3].metric("Arbitrage value", format_money(summary.arbitrage_value))
metric_cols[4].metric("Carbon reduction", f"{summary.carbon_reduction_kg:,.1f} kg")
metric_cols[5].metric("Backup reserve", f"{summary.backup_reserve_hours_at_avg_load:,.1f} h")

daily = (
    hourly.groupby("date", as_index=False)
    .agg(
        baseline_cost=("baseline_cost", "sum"),
        battery_cost=("battery_cost", "sum"),
        load_kwh=("load_kwh", "sum"),
        battery_to_load_kwh=("battery_to_load_kwh", "sum"),
        grid_import_total_kwh=("grid_import_total_kwh", "sum"),
    )
)
daily["savings"] = daily["baseline_cost"] - daily["battery_cost"]

tab_overview, tab_dispatch, tab_detail = st.tabs(["Overview", "Dispatch", "Data"])

with tab_overview:
    left, right = st.columns([1.15, 0.85])
    with left:
        fig_cost = go.Figure()
        fig_cost.add_bar(name="Baseline bill", x=daily["date"], y=daily["baseline_cost"])
        fig_cost.add_bar(name="With battery", x=daily["date"], y=daily["battery_cost"])
        fig_cost.update_layout(
            title="Daily bill comparison",
            barmode="group",
            yaxis_title="Cost ($)",
            xaxis_title="Date",
            legend_title_text="",
            height=420,
        )
        st.plotly_chart(fig_cost, width="stretch")
    with right:
        summary_table = pd.DataFrame(
            [
                {"Metric": "Baseline bill", "Value": format_money(summary.baseline_bill)},
                {"Metric": "Battery bill", "Value": format_money(summary.battery_bill)},
                {"Metric": "Net installed cost", "Value": format_money(summary.net_cost_after_incentives)},
                {"Metric": "Peak energy shifted", "Value": f"{summary.peak_energy_shifted_kwh:,.1f} kWh"},
                {"Metric": "Peak grid reduction", "Value": f"{summary.peak_grid_reduction_pct:,.1f}%"},
                {"Metric": "Cycle-life estimate", "Value": format_years(summary.estimated_cycle_life_years)},
            ]
        )
        st.table(summary_table)

    fig_savings = px.bar(
        daily,
        x="date",
        y="savings",
        title="Daily savings from battery dispatch",
        labels={"date": "Date", "savings": "Savings ($)"},
    )
    fig_savings.update_layout(height=330)
    st.plotly_chart(fig_savings, width="stretch")

with tab_dispatch:
    fig_dispatch = go.Figure()
    fig_dispatch.add_trace(go.Scatter(x=hourly["timestamp"], y=hourly["load_kwh"], name="Load", mode="lines"))
    fig_dispatch.add_trace(
        go.Scatter(x=hourly["timestamp"], y=hourly["battery_to_load_kwh"], name="Battery to load", mode="lines")
    )
    fig_dispatch.add_trace(
        go.Scatter(x=hourly["timestamp"], y=hourly["grid_import_for_battery_kwh"], name="Grid to battery", mode="lines")
    )
    fig_dispatch.update_layout(
        title="Load, charging, and discharge",
        yaxis_title="Energy (kWh)",
        xaxis_title="Timestamp",
        legend_title_text="",
        height=420,
    )
    st.plotly_chart(fig_dispatch, width="stretch")

    fig_soc = go.Figure()
    fig_soc.add_trace(go.Scatter(x=hourly["timestamp"], y=hourly["soc_kwh"], name="State of charge", mode="lines"))
    fig_soc.add_trace(
        go.Scatter(
            x=hourly["timestamp"],
            y=hourly["import_price_per_kwh"],
            name="Import price",
            mode="lines",
            yaxis="y2",
        )
    )
    fig_soc.update_layout(
        title="State of charge and tariff signal",
        yaxis=dict(title="SOC (kWh)"),
        yaxis2=dict(title="Price ($/kWh)", overlaying="y", side="right"),
        xaxis_title="Timestamp",
        legend_title_text="",
        height=420,
    )
    st.plotly_chart(fig_soc, width="stretch")

with tab_detail:
    detail_cols = st.columns(4)
    detail_cols[0].metric("Equivalent full cycles", f"{summary.equivalent_full_cycles:,.2f}")
    detail_cols[1].metric("Annualized cycles", f"{summary.annualized_equivalent_full_cycles:,.0f}")
    detail_cols[2].metric("Round-trip losses", f"{summary.roundtrip_losses_kwh:,.1f} kWh")
    detail_cols[3].metric("Ending backup coverage", f"{summary.ending_backup_hours_at_avg_load:,.1f} h")

    st.download_button(
        "Download hourly results",
        data=hourly.drop(columns=["date"]).to_csv(index=False),
        file_name="revolt_hourly_results.csv",
        mime="text/csv",
    )
    st.dataframe(hourly.tail(168), width="stretch", hide_index=True)
