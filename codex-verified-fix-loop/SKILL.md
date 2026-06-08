---
name: codex-verified-fix-loop
description: >
  通用「定位 → 修复 → codex 复审循环」Skill。无论是修复线上缺陷还是实现一个小需求，
  都按「查找问题/明确需求 → 实施改动 → codex:rescue 复审 → 按 HIGH/MEDIUM 问题修复 →
  同一 codex 线程复核 → 直到无阻塞项」串行推进，最后可选衔接编译/测试/发布。
  用户说"查并修复""codex 把关修复""排查并修复""codex 复核到没问题""verified fix"时调用。
triggers:
  - 查找问题并修复
  - 排查并修复
  - codex 把关修复
  - codex 复核到没问题
  - codex review 循环
  - verified fix
inputs:
  - 一段缺陷描述 / 需求描述（自由文本，必需）
  - config.json（项目路径、数据库 MCP、日志获取、复审参数）
  - 可选：现有报错日志 / 复现步骤 / 相关代码位置
outputs:
  - 修复/实现后的代码改动（最小改动）
  - logs/<date>_<slug>_fixloop.md（每轮循环日志：定位结论 + codex 各轮结论）
dependencies:
  - codex:codex-rescue   # 子代理（Agent 工具 subagent_type），非 Skill
---

# Codex Verified Fix Loop（定位 → 修复 → codex 复审循环）

> **通用 Skill**：技术栈无关。所有项目相关路径/数据库/日志获取/复审参数都从 `config.json` 读，
> 整目录复制到任意项目后只改 `config.json` 即可用。

---

## 0 一句话定位

把"**查找问题 → 解决问题 → codex review → 修复 → codex 复核 → …… 直到全部解决**"这套人工实践
固化为可复用闭环。核心价值是 **codex 复审内循环**：每次改完代码都交 `codex:rescue` 复审，
按 HIGH/MEDIUM 修复后回到**同一 codex 线程**复核，直到无阻塞项才收尾。

```
缺陷/需求描述
   │
   ├─ ① 定位/对齐 ──► 根因结论（缺陷）或 需求边界（需求）
   │
   ├─ ② 实施改动 ──► 最小改动落地
   │
   ├─ ③ codex 复审 ──► HIGH/MEDIUM/LOW/SUGGESTION 逐条
   │        ▲                              │ 有 HIGH/MEDIUM
   │        └──── ④ 修复 + 同线程复核 ◄─────┘
   │                       │ 无 HIGH/MEDIUM（CLEAR）
   │                       ▼
   └─ ⑤ 收尾 ──► 记录日志 + 提示可选编译/测试/发布
```

与 `subagent-dev-orchestrator` 的区别：那个面向"多任务 design.md/tasks.md 全量开发，子 agent 写代码"；
**本 Skill 面向单一缺陷或小需求，主会话亲自定位与改代码**，只把 codex 当质量闸门，轻量、随手可用。

---

## 1 入口判定（两种来源，处理略有差异）

| 来源 | 判定 | ① 阶段做什么 | codex 复审基准 |
|---|---|---|---|
| **缺陷修复** | 用户给的是"报错/异常/线上不符合预期" | 查日志 + 查数据库 + 读代码，定位**根因**（不是表象） | 根因是否真被消除 + 项目规范 |
| **小需求** | 用户给的是"加一个能力/改一处行为" | 明确**需求边界与影响面**，找到落点 | 需求是否满足 + 不破坏既有行为 + 项目规范 |

复杂、跨多文件、契约不明的需求，应转 `architect-design` → `subagent-dev-orchestrator`，不要硬塞进本 Skill。

---

## 2 阶段细则

### ① 定位 / 对齐

**缺陷修复**——按需取用 `config.diagnostics` 的信息源，禁止凭空猜：
- **生产日志**：用 `config.diagnostics.prod_log_access` 的 ssh 模板拉日志（凭证走本机 `~/.ssh`，不写进配置）。
  大日志用 `grep -n <关键词>` 锁定行号，再 `awk 'NR>=a && NR<=b'` 取上下文；终端色码用 `sed 's/\x1b\[[0-9;]*m//g'` 去除。
- **数据库**：涉及表结构/字段/真实数据时，**必须**走 `config.database` 的 MCP（如 `tools-server`），先查真实 DDL 与数据，禁止猜表结构；多库按 `database.servers[].usage` 选对库。
- **代码**：`grep` 报错文案/异常类名定位抛出点，读懂调用链与状态机。

产出：一句话**根因**（点到具体文件:行 + 触发条件 + 数据佐证）。先与用户对齐根因再动手改（高风险链路尤其要停下确认，见 §4）。

**小需求**——读相关代码与规范，明确改动落点和影响面，必要时同样查 DB/日志确认现状。

### ② 实施改动

- **最小改动原则**：只改解决问题/满足需求所必需的，不顺手重构、不全量格式化。
- 遵循 `config.diagnostics` 里的 coding-standards / gotchas。
- 改完简述改了什么、为什么。

### ③ codex 复审（用 Agent 工具，不是 Skill）

通过 `codex:rescue` 触发；它内部用 `Agent` 工具 `subagent_type: "codex:codex-rescue"` 转发。
**禁止 `Skill(codex:rescue)`**（会重入并挂起会话）。

复审提示词要点（模板见 `assets/codex-review-prompt-template.md`）：
- 给**背景**（什么缺陷/需求、根因、改了什么）；
- 指明**只审本次改动**，不要无关重构；
- 要求按 **HIGH / MEDIUM / LOW / SUGGESTION** 分级逐条给结论。

### ④ 修复 + 同线程复核（内循环）

- 按 codex 的 **HIGH / MEDIUM**（`config.review.blocking_levels`）逐条修复；LOW / SUGGESTION 记日志，不阻塞。
- 修复后**回到同一 codex 线程复核**：`codex:rescue` 透传 `--resume`（`config.review.resume_same_thread=true`），
  在提示词里说明"已按你的 X 项修复，请复核并确认是否还有阻塞项"，让 codex 保留上下文。
- 对 codex 提的、你判断为**既有设计/有意为之**的点，要在回传里明确说明理由，请它确认，而不是默默忽略。
- 直到 codex 明确 **无 HIGH/MEDIUM（CLEAR）**；超过 `config.review.max_rounds` 仍未收敛则停下，向用户汇报分歧点由人决策。

### ⑤ 收尾

- 写循环日志到 `config.output.log_dir`（模板 `assets/fix-loop-log-template.md`）：根因/需求、改动、codex 各轮结论、遗留 LOW/SUGGESTION。
- 按 `config.handoff` 提示**可选**下游：编译验证 → 测试 → 发布（发布走 `handoff.suggest_deploy_skill`）。
- **本 Skill 不自动执行高风险步骤**（发布、改生产数据等）；`handoff.high_risk_requires_user_confirm=true` 时必须经用户确认或用户已设目标后再做。

---

## 3 闸门（强制）

1. 根因未对齐前不改代码（缺陷）；需求边界不清前不动手（需求）。
2. 有 HIGH/MEDIUM 未关闭，不算通过，不进入收尾/下游。
3. codex 必须用 `Agent`（`subagent_type: "codex:codex-rescue"`），永不 `Skill(codex:rescue)`。
4. 复核续用同一 codex 线程（`--resume`），保留上下文，避免重复劳动。
5. 查真实数据/DDL 一律走 `config.database` MCP，禁止猜表结构。
6. 高风险链路（支付回调、订单状态机、用户权限、跨新老系统双端、改生产数据）改动前停下与用户确认。

---

## 4 高风险提示

支付/订单/权限/生产数据等链路：①阶段定位结论务必带数据佐证并与用户对齐；②改动属高风险，发布前最少编译 + 现有测试通过；③生产数据变更（如修脏数据）由用户执行或显式授权后再做，并附回滚预案。

---

## 5 可移植性

换项目只改 `config.json`：
- `codebase.*` → 新项目各端路径与技术栈；
- `database.servers[]` → 新项目的 MCP 库与用途（无则置空，定位时不查库）；
- `diagnostics.prod_log_access` → 新项目日志获取方式（无则 null）；
- `review.*` → 复审分级与轮次上限。

SKILL.md 不含任何项目硬编码，复制即用。
