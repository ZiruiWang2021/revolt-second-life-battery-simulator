# 数据管理策略 / Data Management Strategy

## 目标 / Objective

这个模拟器不仅要能跑 demo，也要让输入、假设和输出可审计、可复现，并且为未来接入真实家庭用电数据和现场设备遥测做好准备。

English:

The simulator should be easy to audit, safe to use with household energy data, and ready to evolve from demo inputs to field deployment telemetry.

## 数据域 / Data Domains

| domain | 中文示例 | English examples | owner |
| --- | --- | --- | --- |
| Household load | 小时级用电量、时间戳、可选电表 ID | Hourly kWh demand, timestamps, optional meter IDs | Customer or program partner |
| Tariff | 购电价格、分时电价、需求响应事件 | Import price, time-of-use bands, demand response events | Utility or tariff data provider |
| Grid carbon | 小时级碳强度、区域电网 | Hourly carbon intensity, regional grid zone | Public grid data source or utility |
| Battery asset | 容量、化学体系、SOH、循环寿命、来源 | Capacity, chemistry, state of health, cycle life, pack source | ReVolt operations |
| Simulation output | 节省电费、回本、碳影响、循环使用、备电小时 | Savings, payback, carbon impact, cycle use, backup hours | ReVolt analytics |
| Field telemetry | SOC、充放电、温度、故障码 | SOC, charge/discharge, temperature, faults | ReVolt device platform |

## 输入契约 / Input Contract

最小客户输入 / Minimum customer-provided simulation data:

| column | required | 中文校验 | English validation |
| --- | --- | --- | --- |
| `timestamp` | yes | 可解析为时间，导入后排序 | Parseable datetime, sorted after ingestion |
| `load_kwh` | yes | 数值型、非负 | Numeric, non-negative |
| `import_price_per_kwh` | no | 数值型、非负；缺失时用电价预设补齐 | Numeric, non-negative; tariff preset fills missing values |
| `carbon_kg_per_kwh` | no | 数值型、非负；缺失时用碳强度预设补齐 | Numeric, non-negative; carbon preset fills missing values |

## 数据质量规则 / Data Quality Rules

- 拒绝负的负荷、电价或碳强度。
- 生产环境中应标记缺失小时和重复时间戳。
- 原始上传数据与转换后的仿真数据分开保存。
- 每次输出都保存场景假设，保证结果可复现。
- 对模型逻辑、电价假设和碳假设做版本管理。
- 将 Dashboard KPI 与导出的小时级结果做 reconciliation。

English:

- Reject negative load, price, or carbon values.
- Flag missing hours and duplicated timestamps before production use.
- Keep raw uploaded data separate from transformed simulation data.
- Store scenario assumptions with every result so outputs can be reproduced.
- Version model logic, tariff assumptions, and carbon assumptions.
- Reconcile dashboard KPIs against exported hourly output.

## 隐私与安全 / Privacy And Security

家庭负荷曲线可能暴露居住习惯和行为模式。生产部署应当：

- 尽量减少 simulation files 中的个人身份信息。
- 在分析数据集中使用 account ID，而不是姓名或地址。
- 对存储的客户文件和现场遥测加密。
- 按运营、分析、客服等角色限制访问权限。
- 做组合分析时优先使用聚合结果，除非确实需要 customer-level review。
- 对未绑定活跃客户的上传文件设置保留期限。

English:

Household load profiles can reveal occupancy and behavior. A production deployment should minimize personally identifiable information, encrypt stored files, limit access by role, aggregate results where possible, and define retention windows for uploaded profiles.

## 分析数据模型 / Analytical Data Model

Recommended fact and dimension tables for production:

| table | grain | 中文用途 | English purpose |
| --- | --- | --- | --- |
| `fact_household_load_hourly` | household-hour | 基准负荷曲线和电价 join | Baseline load profile and tariff join |
| `fact_battery_dispatch_hourly` | asset-hour | SOC、充电、放电、购电、排放 | SOC, charge, discharge, grid import, emissions |
| `dim_battery_asset` | asset | 容量、来源 pack、等级、化学体系、质保 | Capacity, source pack, grade, chemistry, warranty |
| `dim_customer_segment` | customer | 租房、低收入、备电等客户分层 | Renter, low-income, backup-focused, other |
| `dim_tariff` | tariff-hour band | 电价带、高峰窗口、utility 区域 | Price bands, peak windows, utility region |
| `fact_simulation_run` | run | 场景假设、模型版本、KPI 输出 | Scenario assumptions, model version, KPI outputs |

## 治理 / Governance

- 每次仿真分配 model version。
- 对电价逻辑、dispatch 逻辑和排放假设维护 changelog。
- 在 CI 中加入 sample dataset 的 schema checks。
- 维护从电池来源到现场部署的资产追踪。
- 在用作营销碳减排声明前，审查 carbon-impact methodology。

English:

- Assign a model version to each simulation run.
- Keep a changelog for tariff logic, dispatch logic, and emissions assumptions.
- Use schema checks in CI before accepting new sample datasets.
- Maintain asset traceability from battery source to field deployment.
- Review carbon-impact methodology before using outputs in marketing claims.

## 后续扩展 / Future Extensions

- Solar PV co-optimization / 光伏协同优化
- Demand response events and outage simulations / 需求响应和停电仿真
- Battery degradation curves by depth of discharge and temperature / 按放电深度和温度建模衰减
- Equity program eligibility and subsidy modelling / 公平能源项目资格和补贴建模
- Fleet-level supply forecast for second-life pack availability / 二次利用电池包供应预测
