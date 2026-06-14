# 供应链策略 / Supply Chain Strategy

## 目标 / Objective

ReVolt 使用二次利用 EV 电池包来降低家庭储能成本，同时延长电池材料的有效使用寿命。供应链策略的核心是稳定来源、安全检测、透明分级、可追踪资产 ID 和负责任的回收路径。

English:

ReVolt uses second-life EV battery packs to lower residential storage cost while extending the useful life of battery materials. The supply chain strategy is built around predictable sourcing, safe diagnostics, transparent grading, traceable asset IDs, and responsible end-of-life routing.

## 供应链流程 / Supply Chain Flow

1. 从车队运营商、经销商、拆解商、保险渠道和 OEM 回收伙伴获取退役 EV 电池包。
2. 筛查电池化学体系、来源、召回状态、物理损伤和历史使用条件。
3. 根据产品结构和安全要求，拆解到 pack、module 或 cell 层级。
4. 测试剩余容量、内阻、热行为和自放电。
5. 将 module 分为不同住宅储能等级：
   - Grade A：主力家庭储能。
   - Grade B：偏备电或低功率应用。
   - Reject：进入合规材料回收或退回处理。
6. 集成 BMS 控制、外壳、逆变器接口和安全断开装置。
7. 部署时记录安装信息、质保条款和可追踪资产 ID。
8. 监控现场性能，将退化单元导向维修、二次部署或回收。

English:

1. Source retired EV packs from fleet operators, dealerships, dismantlers, insurers, and OEM recycling partners.
2. Screen packs for chemistry, provenance, safety recalls, physical damage, and prior service conditions.
3. Disassemble into pack, module, or cell-level units depending on product architecture and safety requirements.
4. Test remaining capacity, internal resistance, thermal behavior, and self-discharge.
5. Grade modules into residential storage classes: Grade A, Grade B, or Reject.
6. Integrate BMS controls, enclosure, inverter interface, and safety disconnects.
7. Deploy with installation records, warranty terms, and traceable asset IDs.
8. Monitor field performance and route degraded units to repair, redeployment, or recycling.

## 关键伙伴 / Key Partners

| partner type | 中文角色 | English role |
| --- | --- | --- |
| EV fleet operators | 提供来源稳定、历史记录更完整的电池包 | Predictable supply of packs with better service records |
| Dismantlers and recyclers | 电池回收、物流、安全处理和最终回收兜底 | Pack recovery, logistics, safety handling, recycling fallback |
| Test labs | 容量、安全和认证支持 | Capacity, safety, and certification support |
| Installers | 现场评估、电气施工和调试 | Site assessment, electrical work, commissioning |
| Community energy programs | 低收入家庭部署和补贴协调 | Low-income household deployment and subsidy coordination |
| Utilities | 分时电价、需求响应和韧性项目 | Time-of-use tariffs, demand response, resilience programs |

## 质量门 / Quality Gates

- 验证 pack 身份、化学体系和召回状态。
- 拒绝物理损伤、进水或热失控风险明显的电池包。
- 为每个产品等级设置最低剩余容量门槛。
- 集成前记录 module 级测试结果。
- 验证 BMS 通信、绝缘电阻、温度传感器和断开机制。
- 保持从进厂电池包到部署系统的 serial-level traceability。

English:

- Verify pack identity, chemistry, and recall status.
- Reject physically damaged, water-exposed, or thermally stressed packs.
- Require a minimum remaining capacity threshold for each product class.
- Record module-level test results before integration.
- Validate BMS communication, isolation resistance, temperature sensors, and disconnect behavior.
- Maintain serial-level traceability from incoming pack to deployed system.

## 风险登记 / Risk Register

| risk | 中文缓解措施 | English mitigation |
| --- | --- | --- |
| Unpredictable supply volume | 使用多渠道来源，优先签车队合同 | Use multiple sourcing channels and prioritize fleet contracts |
| Inconsistent pack formats | 先标准化少数 module family | Standardize around a small number of module families first |
| Safety or warranty exposure | 保守分级、认证外壳、明确质保边界 | Use conservative grading, certified enclosures, and clear warranty boundaries |
| Logistics cost | 在电池来源附近做区域化检测和集成 | Regionalize testing and integration near pack supply |
| Regulatory changes | 按市场跟踪运输、储存和回收法规 | Track battery transport, storage, and recycling rules by market |
| Customer trust | 公开测试方法、质保条款和回收路径 | Publish testing method, warranty terms, and recycling pathway |

## 商业影响 / Business Implications

二次利用电池可以提高可负担性，但前提是检测、物流、集成和质保成本低于新电池系统节省下来的成本。模拟器通过以下参数把供应链问题转化为可测试的商业假设：

- installed cost per kWh / 每 kWh 安装成本
- fixed installation cost / 固定安装成本
- incentive level / 补贴比例
- cycle life / 循环寿命
- backup reserve requirement / 备电 SOC 要求

English:

Second-life packs can improve affordability, but only if testing, logistics, integration, and warranty costs stay below the savings versus new battery systems. The simulator exposes this through installed cost per kWh, fixed installation cost, incentive level, cycle life, and backup reserve requirements.
