# 需求复审循环日志 — <slug>

- 日期：<YYYY-MM-DD>
- 来源：discovery.md | 一段诉求
- 诉求：<用户原始描述一句话>
- 需求文档：specs-mcp/<feature>/requirements.md

## ① 现状对齐
- 信息源：<DB MCP(库名) / 现有接口 grep / discovery.md / 代码>
- 需求边界：In Scope <…> ｜ Out of Scope <…>
- 现状佐证：<真实表名/字段、现有接口路径>
- 用户确认：<是 / 时间>（高风险链路）

## ②③④ codex 复审循环
| 轮次 | 结论 | HIGH | MEDIUM | LOW/SUGGESTION | 处理 |
|---|---|---|---|---|---|
| 1 | <摘要> | <n> | <n> | <n> | <修订了哪些功能编号 / 哪些回传确认为 Out of Scope> |
| 2(--resume) | CLEAR | 0 | 0 | <n> | <遗留 LOW/SUGGESTION，不阻塞> |

- 维度命中分布：完整性 <n> ｜ 一致性 <n> ｜ 可实现性 <n> ｜ 可测试性 <n> ｜ 范围 <n>
- 最终：CLEAR（无 HIGH/MEDIUM）
- 遗留（不阻塞）：<LOW/SUGGESTION 列表，或"无">

## ⑤ 放行
- 需求状态：CLEAR（已定稿）
- 下游提示：业务评审 business-requirement-review ｜ UI 基线 ui-design-baseline ｜ 架构 architect-design
- 待用户决策项：<列出，或"无">
