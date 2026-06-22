# 坑点（codex-verified-requirement-design）

## 1 codex 调用方式
- **必须**用 `Agent` 工具，`subagent_type: "codex:codex-rescue"`（经 `codex:rescue` 转发）。
- **禁止** `Skill(codex:rescue)`：会重入并挂起当前会话。
- 续复核透传 `--resume`，命中同一线程保留上下文（`config.review.resume_same_thread=true`）。

## 2 codex 会跑去评代码 —— 最常见的坑
- codex（codex:rescue）默认是代码救援/复审定位，喂它需求文档它会本能地找代码、提重构。
- **对策**：复审提示词**首句**写死 `This is a REQUIREMENTS DOCUMENT review, NOT a code review`，
  resume 复核时也要**重申一遍**（resume 后它常忘记定调）。模板已内置，照抄即可。

## 3 不喂现状约束 = 复审无的放矢
- 只把 requirements.md 丢给 codex，它无法判断"可实现性/一致性"，只能挑措辞。
- **对策**：把 ① 阶段查到的**真实表/字段/现有接口/复用判断**作为 Background 一起给它。

## 4 查库一律走 MCP
- 涉及表结构/字段/数据口径，必须用 `config.database` 的 MCP 查真实 DDL，禁止猜。
- 多库按 `servers[].usage` 选对库；**新老系统库相互独立**，禁止跨库套字段假设。

## 5 阻塞线与放行
- 只有 `config.review.blocking_levels`（HIGH/MEDIUM）阻塞放行；LOW/SUGGESTION 记日志不阻塞。
- 你判定为 Out of Scope / 有意收窄的 codex finding，要在 resume 里**给理由请它确认 RESOLVED**，不要默默忽略。
- 超过 `config.review.max_rounds` 仍未 CLEAR：停下，把分歧点交用户决策，别无限循环。

## 6 职责边界（越界 codex 会判 SUGGESTION/MEDIUM）
- 本 Skill 只产出"系统做什么"的需求规格。
- 写了 API 契约 / DDL 类型 / 索引 / UI 颜色布局 / 技术选型 = 越界，删掉转给下游 Skill。

## 7 不替用户做业务决策
- 定价、风控阈值、灰度比例等业务策略，列入"待用户决策"，停下问清，不自行拍板写进需求。
