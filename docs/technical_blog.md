# 构建二次利用 EV 电池储能模拟器 / Building a Second-Life EV Battery Storage Simulator

GitHub link: `https://github.com/ZiruiWang2021/revolt-second-life-battery-simulator`

## Problem / 问题

二次利用 EV 电池的机会很清晰：退役电动车电池仍然保有一定容量，如果能安全分级并用于家庭储能，就可以降低储能系统成本，并延长电池材料的使用寿命。

真正难的问题是：在安装成本、效率损耗、循环寿命、备电需求和用户电价结构都考虑进去之后，这块二手电池对家庭用户到底有没有经济价值？

English:

Second-life EV batteries are attractive because they can reduce the cost of residential storage while extending the useful life of battery materials. The hard question is whether a reused battery creates enough household value after installation cost, efficiency losses, limited cycle life, and user needs are considered.

I built a Python simulator and dashboard for three use cases:

- 租房用户 / renters who need a smaller and more portable system
- 低收入家庭 / low-income households where incentives and bill savings matter most
- 备电场景 / backup-focused households that value reserve energy during outages

## Why It Matters / 为什么重要

家庭储能不只是电池技术问题，也是用户经济性和信任问题。用户关心的不是“电池参数好不好看”，而是：

- 能不能真的省电费
- 回本周期多长
- 高峰电价时能不能减少购电
- 停电时能撑多久
- 二次利用电池是否安全、可追踪、可质保

English:

Residential battery storage is often discussed as a technical product, but adoption depends on economics and trust. A household wants to know whether the system saves money, how long payback takes, what happens during peak pricing, and whether the battery still has enough life to be worth installing.

For a second-life battery company, the same model also supports product strategy:

- which customer segment has the strongest value proposition
- how installation cost changes payback
- how much reserve SOC should be protected for backup use
- whether carbon claims are credible under grid charging
- where supply chain and data quality risks affect the business case

## My Approach / 我的方法

我把这个项目设计成一个小而完整的工程产品，而不是单个 Notebook：

1. 核心 Python package 负责仿真逻辑。
2. CLI 输出 JSON，方便复现实验。
3. Streamlit Dashboard 允许用户调节电池、电价和场景假设。
4. 单元测试验证关键成本和备电逻辑。
5. 文档解释模型假设、供应链策略和数据管理策略。
6. GitHub Actions 自动运行测试。

English:

I designed the project as a small but complete engineering product:

1. A core Python package handles the simulation.
2. A CLI produces JSON output for repeatable scenario runs.
3. A Streamlit dashboard lets users adjust battery, tariff, and scenario assumptions.
4. Unit tests verify the key accounting logic.
5. Documentation explains model assumptions, supply chain strategy, and data management.
6. GitHub Actions runs the tests automatically.

The model is intentionally transparent. Instead of hiding the logic inside a black-box optimizer, it uses a readable hourly dispatch rule:

- charge during low-price hours
- discharge during high-price hours
- respect battery capacity, power limits, efficiency, and reserve state of charge

这种设计让业务价值、工程假设和 KPI 计算路径都可以被直接追踪，也便于后续替换成更复杂的优化模型。

## Technical Implementation / 技术实现

项目拆成几个模块：

| component | 中文职责 | English responsibility |
| --- | --- | --- |
| `config.py` | 电池、电价和场景 dataclass | Battery, tariff, and scenario dataclasses |
| `profiles.py` | 生成负荷曲线、CSV 校验、电价补全 | Load generation, CSV validation, tariff enrichment |
| `simulator.py` | 小时级 dispatch、成本核算、碳排核算、KPI 汇总 | Hourly dispatch, cost accounting, emissions accounting, KPI summary |
| `dashboard/app.py` | 双语控件、KPI 卡片、Plotly 图表、CSV 下载 | Bilingual controls, KPI cards, Plotly charts, CSV download |
| `tests/` | 单元测试 | Unit tests |

The simulator compares two worlds:

1. Baseline: the household imports all load from the grid.
2. Battery case: the battery charges during cheaper hours and discharges during expensive hours to offset household load.

每个小时追踪 / Each hour tracks:

- household load / 家庭负荷
- import price / 购电价格
- carbon intensity / 电网碳强度
- battery state of charge / 电池 SOC
- battery energy delivered to load / 电池供给负荷的电量
- grid energy used to charge the battery / 电网给电池充电的电量
- baseline and battery-assisted cost / 基准成本和电池辅助后的成本
- baseline and battery-assisted emissions / 基准排放和电池辅助后的排放

The summary outputs include:

- bill savings / 节省电费
- annualized savings / 年化节省
- payback period / 回本周期
- arbitrage value / 峰谷套利价值
- peak energy shifted / 高峰转移电量
- peak grid reduction / 高峰购电下降比例
- carbon reduction / 碳减排
- equivalent full cycles / 等效完整循环
- estimated cycle-life years / 预计循环寿命年限
- backup reserve hours / 备电小时数

## Results / Demo / 结果演示

For a 7-day renter scenario, the simulator produced:

```json
{
  "baseline_bill": 34.62,
  "battery_bill": 32.47,
  "bill_savings": 2.15,
  "annualized_savings": 112.17,
  "payback_years": 9.14,
  "arbitrage_value": 2.15,
  "peak_energy_shifted_kwh": 51.48,
  "peak_grid_reduction_pct": 22.76,
  "carbon_reduction_kg": 2.25
}
```

中文解读：在这个示例里，二次利用电池可以降低高峰时段购电，7 天节省约 2.15 美元，年化约 112 美元，回本约 9.14 年。这个结果说明模型不是简单宣传“电池一定赚钱”，而是把成本、效率和使用场景放在一起评估。

English:

The dashboard turns those outputs into an interactive demo. A user can choose the scenario, adjust capacity and efficiency, change tariff assumptions, upload a household load CSV, and download hourly dispatch results.

## Limitations / 局限性

This is a planning simulator, not a full battery physics model.

当前限制 / Current limitations:

- no solar PV co-optimization / 暂无光伏协同优化
- no export revenue / 暂不上网售电收入
- no demand charges / 暂无需量电费
- no stochastic outage modelling / 暂无随机停电建模
- no detailed thermal or electrochemical degradation model / 暂无热管理或电化学衰减模型
- no market-specific permitting or interconnection cost / 暂无地区级许可和并网成本
- no real-time utility API integration / 暂无实时 utility API 集成

The carbon estimate is simplified. It is useful for comparing assumptions, but production carbon claims would need region-specific hourly grid intensity data and careful review.

## What I Learned / 我的收获

二次利用储能不是单纯的电池工程问题，而是一个系统设计问题：

- 技术约束：效率、功率限制、循环寿命、SOC 储备
- 用户约束：可负担性、备电预期、租房场景安装限制
- 市场约束：分时电价、补贴、安装成本
- 运营约束：电池包来源、检测分级、质保、数据追踪

English:

The most important lesson was that second-life storage is not just a battery engineering problem. It is a system design problem involving technical constraints, customer constraints, market constraints, and operational constraints.

I also learned that a strong engineering project needs two layers: the value proposition should be understandable quickly, while the implementation should still expose real modelling decisions, test coverage, and limitations.

## GitHub Link / 项目链接

`https://github.com/ZiruiWang2021/revolt-second-life-battery-simulator`
