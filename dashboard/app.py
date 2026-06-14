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


TEXT = {
    "zh": {
        "title": "ReVolt 二次利用 EV 电池储能模拟器",
        "subtitle": "面向家庭电费节省、峰谷套利、碳减排和备电价值的场景 Dashboard。",
        "language": "语言 / Language",
        "use_case": "用户场景",
        "upload": "家庭用电 CSV",
        "generated_days": "生成负荷天数",
        "battery": "电池参数",
        "capacity": "容量 (kWh)",
        "efficiency": "往返效率",
        "reserve": "保留电量比例",
        "cycle_life": "循环寿命",
        "cost_per_kwh": "安装成本 ($/kWh)",
        "fixed_cost": "固定安装成本 ($)",
        "incentive": "补贴比例",
        "tariff": "电价",
        "off_peak_price": "谷时电价 ($/kWh)",
        "shoulder_price": "平时电价 ($/kWh)",
        "peak_price": "峰时电价 ($/kWh)",
        "simulation_failed": "仿真失败",
        "bill_savings": "节省电费",
        "annual_savings": "年化节省",
        "payback": "回本周期",
        "arbitrage": "套利价值",
        "carbon_reduction": "碳减排",
        "backup_reserve": "备电储备",
        "no_payback": "不可回本",
        "years": "年",
        "overview": "概览",
        "dispatch": "调度",
        "data": "数据",
        "daily_bill_comparison": "每日账单对比",
        "baseline_bill": "基准账单",
        "with_battery": "使用电池后",
        "cost_axis": "成本 ($)",
        "date_axis": "日期",
        "table_metric": "指标",
        "table_value": "数值",
        "battery_bill": "电池方案账单",
        "net_installed_cost": "补贴后净安装成本",
        "peak_energy_shifted": "高峰转移电量",
        "peak_grid_reduction": "高峰购电下降",
        "cycle_life_estimate": "循环寿命估计",
        "daily_savings": "每日节省电费",
        "savings_axis": "节省 ($)",
        "load_charge_discharge": "负荷、充电与放电",
        "energy_axis": "电量 (kWh)",
        "timestamp_axis": "时间",
        "load": "家庭负荷",
        "battery_to_load": "电池供给负荷",
        "grid_to_battery": "电网给电池充电",
        "soc_and_tariff": "电池 SOC 与电价信号",
        "soc": "电池 SOC",
        "price": "购电价格",
        "soc_axis": "SOC (kWh)",
        "price_axis": "价格 ($/kWh)",
        "equivalent_cycles": "等效完整循环",
        "annualized_cycles": "年化循环",
        "roundtrip_losses": "往返损耗",
        "ending_backup": "期末备电覆盖",
        "download": "下载小时级结果",
    },
    "en": {
        "title": "ReVolt Second-Life EV Battery Storage Simulator",
        "subtitle": "Scenario dashboard for household bill savings, arbitrage, carbon impact, and backup value.",
        "language": "Language / 语言",
        "use_case": "Use case",
        "upload": "Household load CSV",
        "generated_days": "Generated profile days",
        "battery": "Battery",
        "capacity": "Capacity (kWh)",
        "efficiency": "Round-trip efficiency",
        "reserve": "Reserve state of charge",
        "cycle_life": "Cycle life",
        "cost_per_kwh": "Installed cost ($/kWh)",
        "fixed_cost": "Fixed install cost ($)",
        "incentive": "Incentive",
        "tariff": "Tariff",
        "off_peak_price": "Off-peak price ($/kWh)",
        "shoulder_price": "Shoulder price ($/kWh)",
        "peak_price": "Peak price ($/kWh)",
        "simulation_failed": "Simulation failed",
        "bill_savings": "Bill savings",
        "annual_savings": "Annual savings",
        "payback": "Payback",
        "arbitrage": "Arbitrage value",
        "carbon_reduction": "Carbon reduction",
        "backup_reserve": "Backup reserve",
        "no_payback": "No payback",
        "years": "years",
        "overview": "Overview",
        "dispatch": "Dispatch",
        "data": "Data",
        "daily_bill_comparison": "Daily bill comparison",
        "baseline_bill": "Baseline bill",
        "with_battery": "With battery",
        "cost_axis": "Cost ($)",
        "date_axis": "Date",
        "table_metric": "Metric",
        "table_value": "Value",
        "battery_bill": "Battery bill",
        "net_installed_cost": "Net installed cost",
        "peak_energy_shifted": "Peak energy shifted",
        "peak_grid_reduction": "Peak grid reduction",
        "cycle_life_estimate": "Cycle-life estimate",
        "daily_savings": "Daily savings from battery dispatch",
        "savings_axis": "Savings ($)",
        "load_charge_discharge": "Load, charging, and discharge",
        "energy_axis": "Energy (kWh)",
        "timestamp_axis": "Timestamp",
        "load": "Load",
        "battery_to_load": "Battery to load",
        "grid_to_battery": "Grid to battery",
        "soc_and_tariff": "State of charge and tariff signal",
        "soc": "State of charge",
        "price": "Import price",
        "soc_axis": "SOC (kWh)",
        "price_axis": "Price ($/kWh)",
        "equivalent_cycles": "Equivalent full cycles",
        "annualized_cycles": "Annualized cycles",
        "roundtrip_losses": "Round-trip losses",
        "ending_backup": "Ending backup coverage",
        "download": "Download hourly results",
    },
}

SCENARIOS = {
    "zh": {
        "renter": {
            "label": "租房用户",
            "audience": "公寓和小户型可使用的便携式或租赁式电池系统。",
        },
        "low_income": {
            "label": "低收入家庭",
            "audience": "通过补贴降低前期成本，重点评估电费减负和高峰负担下降。",
        },
        "backup": {
            "label": "备电韧性场景",
            "audience": "保留更高 SOC，用于停电时支撑关键家庭负荷。",
        },
    },
    "en": {
        "renter": {
            "label": "Renter",
            "audience": "Portable or lease-style battery system for apartments and small homes.",
        },
        "low_income": {
            "label": "Low-income household",
            "audience": "Incentive-supported system focused on bill savings and peak burden reduction.",
        },
        "backup": {
            "label": "Backup use case",
            "audience": "Larger battery with protected reserve for outage resilience.",
        },
    },
}

LANGUAGE_OPTIONS = {"zh": "中文", "en": "English"}

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


def format_years(value: float | None, copy: dict[str, str]) -> str:
    if value is None:
        return copy["no_payback"]
    return f"{value:.1f} {copy['years']}"


presets = scenario_presets()

with st.sidebar:
    language = st.radio(
        "语言 / Language",
        options=list(LANGUAGE_OPTIONS.keys()),
        format_func=lambda key: LANGUAGE_OPTIONS[key],
        horizontal=True,
    )
    copy = TEXT[language]

st.title(copy["title"])
st.caption(copy["subtitle"])

with st.sidebar:
    scenario_name = st.selectbox(
        copy["use_case"],
        options=list(presets.keys()),
        format_func=lambda key: SCENARIOS[language][key]["label"],
    )
    scenario = get_scenario(scenario_name)
    st.caption(SCENARIOS[language][scenario_name]["audience"])

    uploaded = st.file_uploader(copy["upload"], type=["csv"])
    days = st.slider(copy["generated_days"], min_value=2, max_value=60, value=14, step=1)

    st.divider()
    st.subheader(copy["battery"])
    capacity = st.slider(copy["capacity"], 2.0, 25.0, scenario.battery.capacity_kwh, 0.5)
    efficiency = st.slider(copy["efficiency"], 0.70, 0.98, scenario.battery.roundtrip_efficiency, 0.01)
    reserve = st.slider(copy["reserve"], 0.0, 0.75, scenario.battery.reserve_fraction, 0.01)
    cycle_life = st.slider(copy["cycle_life"], 1000, 8000, scenario.battery.cycle_life, 100)
    cost_per_kwh = st.slider(copy["cost_per_kwh"], 50.0, 300.0, scenario.battery.installed_cost_per_kwh, 5.0)
    fixed_cost = st.slider(copy["fixed_cost"], 0.0, 3000.0, scenario.battery.fixed_installation_cost, 50.0)
    incentive = st.slider(copy["incentive"], 0.0, 0.75, scenario.battery.incentive_fraction, 0.01)

    st.divider()
    st.subheader(copy["tariff"])
    off_peak_price = st.slider(copy["off_peak_price"], 0.05, 0.40, scenario.tariff.off_peak_price, 0.01)
    shoulder_price = st.slider(copy["shoulder_price"], 0.08, 0.55, scenario.tariff.shoulder_price, 0.01)
    peak_price = st.slider(copy["peak_price"], 0.12, 0.90, scenario.tariff.peak_price, 0.01)

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
    st.error(f"{copy['simulation_failed']}: {exc}")
    st.stop()

summary = result.summary
hourly = result.hourly.copy()
hourly["date"] = hourly["timestamp"].dt.date

metric_cols = st.columns(6)
metric_cols[0].metric(copy["bill_savings"], format_money(summary.bill_savings))
metric_cols[1].metric(copy["annual_savings"], format_money(summary.annualized_savings))
metric_cols[2].metric(copy["payback"], format_years(summary.payback_years, copy))
metric_cols[3].metric(copy["arbitrage"], format_money(summary.arbitrage_value))
metric_cols[4].metric(copy["carbon_reduction"], f"{summary.carbon_reduction_kg:,.1f} kg")
metric_cols[5].metric(copy["backup_reserve"], f"{summary.backup_reserve_hours_at_avg_load:,.1f} h")

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

tab_overview, tab_dispatch, tab_detail = st.tabs([copy["overview"], copy["dispatch"], copy["data"]])

with tab_overview:
    left, right = st.columns([1.15, 0.85])
    with left:
        fig_cost = go.Figure()
        fig_cost.add_bar(name=copy["baseline_bill"], x=daily["date"], y=daily["baseline_cost"])
        fig_cost.add_bar(name=copy["with_battery"], x=daily["date"], y=daily["battery_cost"])
        fig_cost.update_layout(
            title=copy["daily_bill_comparison"],
            barmode="group",
            yaxis_title=copy["cost_axis"],
            xaxis_title=copy["date_axis"],
            legend_title_text="",
            height=420,
        )
        st.plotly_chart(fig_cost, width="stretch")
    with right:
        summary_table = pd.DataFrame(
            [
                {copy["table_metric"]: copy["baseline_bill"], copy["table_value"]: format_money(summary.baseline_bill)},
                {copy["table_metric"]: copy["battery_bill"], copy["table_value"]: format_money(summary.battery_bill)},
                {
                    copy["table_metric"]: copy["net_installed_cost"],
                    copy["table_value"]: format_money(summary.net_cost_after_incentives),
                },
                {
                    copy["table_metric"]: copy["peak_energy_shifted"],
                    copy["table_value"]: f"{summary.peak_energy_shifted_kwh:,.1f} kWh",
                },
                {
                    copy["table_metric"]: copy["peak_grid_reduction"],
                    copy["table_value"]: f"{summary.peak_grid_reduction_pct:,.1f}%",
                },
                {
                    copy["table_metric"]: copy["cycle_life_estimate"],
                    copy["table_value"]: format_years(summary.estimated_cycle_life_years, copy),
                },
            ]
        )
        st.table(summary_table)

    fig_savings = px.bar(
        daily,
        x="date",
        y="savings",
        title=copy["daily_savings"],
        labels={"date": copy["date_axis"], "savings": copy["savings_axis"]},
    )
    fig_savings.update_layout(height=330)
    st.plotly_chart(fig_savings, width="stretch")

with tab_dispatch:
    fig_dispatch = go.Figure()
    fig_dispatch.add_trace(go.Scatter(x=hourly["timestamp"], y=hourly["load_kwh"], name=copy["load"], mode="lines"))
    fig_dispatch.add_trace(
        go.Scatter(x=hourly["timestamp"], y=hourly["battery_to_load_kwh"], name=copy["battery_to_load"], mode="lines")
    )
    fig_dispatch.add_trace(
        go.Scatter(
            x=hourly["timestamp"],
            y=hourly["grid_import_for_battery_kwh"],
            name=copy["grid_to_battery"],
            mode="lines",
        )
    )
    fig_dispatch.update_layout(
        title=copy["load_charge_discharge"],
        yaxis_title=copy["energy_axis"],
        xaxis_title=copy["timestamp_axis"],
        legend_title_text="",
        height=420,
    )
    st.plotly_chart(fig_dispatch, width="stretch")

    fig_soc = go.Figure()
    fig_soc.add_trace(go.Scatter(x=hourly["timestamp"], y=hourly["soc_kwh"], name=copy["soc"], mode="lines"))
    fig_soc.add_trace(
        go.Scatter(
            x=hourly["timestamp"],
            y=hourly["import_price_per_kwh"],
            name=copy["price"],
            mode="lines",
            yaxis="y2",
        )
    )
    fig_soc.update_layout(
        title=copy["soc_and_tariff"],
        yaxis=dict(title=copy["soc_axis"]),
        yaxis2=dict(title=copy["price_axis"], overlaying="y", side="right"),
        xaxis_title=copy["timestamp_axis"],
        legend_title_text="",
        height=420,
    )
    st.plotly_chart(fig_soc, width="stretch")

with tab_detail:
    detail_cols = st.columns(4)
    detail_cols[0].metric(copy["equivalent_cycles"], f"{summary.equivalent_full_cycles:,.2f}")
    detail_cols[1].metric(copy["annualized_cycles"], f"{summary.annualized_equivalent_full_cycles:,.0f}")
    detail_cols[2].metric(copy["roundtrip_losses"], f"{summary.roundtrip_losses_kwh:,.1f} kWh")
    detail_cols[3].metric(copy["ending_backup"], f"{summary.ending_backup_hours_at_avg_load:,.1f} h")

    st.download_button(
        copy["download"],
        data=hourly.drop(columns=["date"]).to_csv(index=False),
        file_name="revolt_hourly_results.csv",
        mime="text/csv",
    )
    st.dataframe(hourly.tail(168), width="stretch", hide_index=True)
