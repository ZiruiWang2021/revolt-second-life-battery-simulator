# 中英双语面试讲解稿 / Bilingual Interview Guide

## 30 秒中文介绍

这个项目是一个二次利用 EV 电池家庭储能模拟器。我用 Python 建了核心仿真模型，用 Streamlit 做了 Dashboard，用户可以选择租房用户、低收入家庭或备电场景，输入家庭用电曲线、电价、电池容量、效率和循环寿命，输出节省电费、回本周期、峰谷套利、碳减排和备电小时数。它展示的是我把电气工程、能源系统、商业建模和数据管理结合起来解决真实问题的能力。

## 30-Second English Pitch

This project is a Python simulator and Streamlit dashboard for second-life EV battery storage. Users can choose renter, low-income household, or backup use cases, then adjust household load, tariff, battery capacity, efficiency, and cycle life. The model outputs bill savings, payback period, peak/off-peak arbitrage, carbon reduction, and backup reserve hours. It demonstrates my ability to connect electrical engineering assumptions, energy systems, business modelling, and data management.

## 技术讲解重点 / Technical Talking Points

| 中文问题 | English question | 建议回答 / Suggested answer |
| --- | --- | --- |
| 你为什么不用黑盒优化器？ | Why not use a black-box optimizer? | 我先用透明规则建模，便于审计、解释和测试。后续可以替换为线性规划。 / I started with a transparent heuristic so the logic is auditable, explainable, and testable. It can later be replaced with linear programming. |
| 这个模型最核心的假设是什么？ | What is the core assumption? | 电池低价时充电、高价时放电，同时遵守容量、功率、效率和 reserve SOC。 / The battery charges during low-price hours and discharges during high-price hours while respecting capacity, power, efficiency, and reserve SOC. |
| 怎么计算回本？ | How is payback calculated? | 模型期节省电费年化后，用净安装成本除以年化节省。 / Model-period bill savings are annualized, then net installed cost is divided by annualized savings. |
| 碳减排一定为正吗？ | Is carbon reduction always positive? | 不一定。因为电池从电网充电，只有低价时段也更低碳时，碳结果才会更好。 / Not always. Since the battery charges from the grid, carbon results improve only when low-price charging hours are also lower-carbon hours. |
| 如何体现数据管理能力？ | How does this show data management skill? | 项目定义了输入契约、数据质量规则、隐私风险、事实表和维表设计。 / The project defines input contracts, data quality rules, privacy risks, and fact/dimension table design. |

## HR 可理解亮点 / Recruiter-Friendly Signals

- 不是只写代码，而是把能源行业问题变成可运行产品。
- 有 Dashboard 截图、安装方法、示例输入输出和测试。
- 有供应链和数据管理文档，体现商业落地思维。
- 中英双语文档方便中国和海外面试官都快速理解。

English:

- It turns an energy industry problem into a runnable product.
- It includes a dashboard screenshot, installation steps, example inputs/outputs, and tests.
- Supply chain and data strategy docs show business implementation thinking.
- Bilingual documentation helps both Chinese and international interviewers understand the project quickly.

## 后续可以主动提的改进 / Future Improvements To Mention

- 用线性规划优化 dispatch，而不是固定价格阈值。
- 加入太阳能 PV、上网电价和需求响应。
- 加入更真实的电池衰减模型，例如按放电深度、温度和 C-rate。
- 部署公开 Streamlit demo，让面试官不用本地安装也能试用。
- 接入真实区域电价和小时级电网碳强度数据。

English:

- Replace heuristic dispatch with linear programming.
- Add solar PV, export compensation, and demand response.
- Add degradation modelling by depth of discharge, temperature, and C-rate.
- Deploy a hosted Streamlit demo.
- Integrate real regional tariffs and hourly grid carbon intensity data.
