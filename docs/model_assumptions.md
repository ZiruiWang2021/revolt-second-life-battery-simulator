# 模型假设 / Model Assumptions

## Dispatch 逻辑 / Dispatch Logic

模拟器使用透明的价格阈值策略：

- 当购电价格低于或等于低价分位数时，电池从电网充电。
- 当购电价格高于或等于高价分位数时，电池向家庭负荷放电。
- 电池必须保持在配置的 reserve state of charge 之上。
- 当前版本只服务家庭负荷，不建模上网售电收入。

English:

The simulator uses a transparent price-threshold dispatch policy:

- Charge when the import price is at or below the selected low-price quantile.
- Discharge when the import price is at or above the selected high-price quantile.
- Keep the battery above the configured reserve state of charge.
- Serve only household load; export revenue is not modelled in this version.

## 效率 / Efficiency

往返效率被平均拆分为充电效率和放电效率：

```text
charge_efficiency = sqrt(roundtrip_efficiency)
discharge_efficiency = sqrt(roundtrip_efficiency)
```

这样可以保持计算简单，同时仍然体现能量损耗。

English:

Round-trip efficiency is split evenly into charge and discharge efficiency. This keeps the accounting simple while still capturing energy losses.

## 回本周期 / Payback

回本周期基于年化电费节省：

```text
annualized_savings = model_period_savings * 365 / days_modelled
payback_years = net_installed_cost / annualized_savings
```

如果年化节省为 0 或负数，则回本周期显示为不可用。

English:

Payback is based on annualized bill savings. If annualized savings are zero or negative, payback is reported as unavailable.

## 碳影响 / Carbon

碳影响比较两种情况下的电网购电排放：

1. Baseline：家庭所有负荷都直接从电网购买。
2. Battery case：电池在低价时段充电，在高价时段放电来抵消家庭负荷。

因为当前版本的电池从电网充电，所以碳减排取决于低价时段是否也对应更低碳强度。如果低价时段电网并不低碳，碳结果可能不显著甚至变差。

English:

Carbon impact compares baseline grid import emissions against battery-assisted grid import emissions. Because this version charges from the grid, carbon reduction depends on whether the tariff's low-price hours are also lower-carbon hours.

## 循环寿命 / Cycle Life

等效完整循环通过“进入电池的总能量 / 标称容量”估算：

```text
equivalent_full_cycles = total_charged_to_battery_kwh / capacity_kwh
```

这个指标适合商业规划和场景比较，但不能替代完整的电化学衰减模型。

English:

Equivalent full cycles are estimated from total energy charged into the battery divided by nominal capacity. This is suitable for business planning but does not replace a full degradation model.

## 适用范围 / Intended Use

适合使用本模型的场景：

- 项目演示、课程展示或产品初步评估。
- 比较租房、低收入家庭和备电三类用户的价值差异。
- 快速测试电价、容量、效率、补贴和安装成本对回本周期的影响。
- 解释二次利用储能为什么需要同时考虑技术、商业和运营约束。

不适合直接使用本模型的场景：

- 精确设备选型。
- 安全认证或质保定价。
- 电化学寿命预测。
- 真实客户账单承诺。
- 正式碳减排声明。

English:

The model is intended for project demos, scenario comparison, early product evaluation, and business planning. It is not intended for final equipment sizing, safety certification, warranty pricing, electrochemical lifetime prediction, customer billing guarantees, or formal carbon claims.
