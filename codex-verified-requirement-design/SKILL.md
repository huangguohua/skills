---
name: codex-verified-requirement-design
description: >
  通用「需求设计 → codex 复审循环」Skill。把一段业务诉求按
  「对齐诉求与现状 → 产出结构化需求文档 → codex:rescue 分级复审 → 按 HIGH/MEDIUM 修订 →
  同一 codex 线程复核 → 直到无阻塞项」串行推进，产出经 codex 把关、可直接进入架构/开发的需求规格。
  用户说"写需求并让 codex 把关""codex 复核需求""需求设计到没问题""verified PRD""需求复审循环"时调用。
triggers:
  - 写需求并让 codex 把关
  - codex 复核需求
  - codex 把关需求
  - 需求设计到没问题
  - 需求复审循环
  - verified requirement
  - verified PRD
inputs:
  - 一段业务诉求 / 功能想法（自由文本，必需）
  - config.json（输出目录、数据库 MCP、现状信息源、复审维度与轮次）
  - 可选：已确认的 discovery.md / 相关现有代码与接口 / 数据 DDL
outputs:
  - specs/<feature>/requirements.md（结构化需求规格，经 codex 复审 CLEAR）
  - specs/<feature>/requirement-review-loop.md（每轮复审日志：对齐结论 + codex 各轮结论）
dependencies:
  - codex:codex-rescue   # 子代理（Agent 工具 subagent_type），非 Skill
---

# Codex Verified Requirement Design（需求设计 → codex 复审循环）

> **通用 Skill**：业务无关。所有项目相关路径/数据库/现状信息源/复审参数都从 `config.json` 读，
> 整目录复制到任意项目后只改 `config.json` 即可用。SKILL.md 不含任何项目硬编码。

---

## 0 一句话定位

把 `codex-verified-fix-loop` 的「**改动 → codex 复审 → 修复 → 同线程复核 → 直到 CLEAR**」内循环，
从**改代码**迁移到**写需求**。核心价值同样是 **codex 复审内循环**：每次写完/改完需求文档都交
`codex:rescue` 复审，按 HIGH/MEDIUM 修订后回到**同一 codex 线程**复核，直到无阻塞项才放行。
区别只在 codex 的**审什么**——代码审"正确性/并发"，需求审"完整性/一致性/可实现性/与现状对齐/可测试性"。

```
业务诉求
   │
   ├─ ① 对齐 ──► 需求边界 + 现状约束（查 DB DDL / 现有接口，禁止凭空假设）
   │
   ├─ ② 产出 ──► 结构化 requirements.md（功能/边界/异常流/数据/验收）
   │
   ├─ ③ codex 复审 ──► HIGH/MEDIUM/LOW/SUGGESTION 逐条（按需求质量维度）
   │        ▲                              │ 有 HIGH/MEDIUM
   │        └──── ④ 修订 + 同线程复核 ◄─────┘
   │                       │ 无 HIGH/MEDIUM（CLEAR）
   │                       ▼
   └─ ⑤ 放行 ──► 记录循环日志 + 提示下游（业务评审 / UI 设计 / 架构设计）
```

**与相邻 Skill 的关系**：
- 与 `prd-generate`：prd-generate 是"一次成稿"的需求文档生成；**本 Skill 在它基础上叠加 codex 复审内循环**，把
  `business-requirement-review` 的人工评审前移成 codex 自动把关，产出"开箱即过评审"的需求。
- 与 `codex-verified-fix-loop`：那个面向**代码缺陷/小需求改动**，主会话改代码；**本 Skill 面向需求文档本身**，主会话写文档。
- 与 `architect-design`：本 Skill 只交付**需求规格**（系统做什么），不定义 API/DDL/技术选型（那是 architect-design）。

复杂到需要多端契约、跨系统数据流的，先用本 Skill 把需求 codex 把关定稿，再转 `architect-design`。

---

## 1 入口判定

| 来源 | 判定 | ① 阶段做什么 |
|---|---|---|
| **已有 discovery.md** | `config.output_dir/<feature>/discovery.md` 存在且已确认 | 直接读探索结论作为现状输入，校正后进入 ② |
| **仅一段诉求** | 用户只给了功能想法 | 先做轻量现状对齐（查 DB/接口/代码），再进入 ② |

> 若现状高度不明、影响面未知，先转 `solution-discovery` 出 `discovery.md`，再回到本 Skill，避免在错误前提上写需求。

---

## 2 阶段细则

### ① 对齐诉求与现状

目标：在动笔前把**需求边界**和**现状约束**钉死，让后续 codex 复审有客观基准。

- **数据库**：凡涉及表/字段/真实数据口径，**必须**走 `config.database` 的 MCP 查真实 DDL 与样本数据，禁止猜表结构；
  多库按 `database.servers[].usage` 选对库（新老系统库相互独立，禁止跨库套字段）。
- **现有接口/代码**：`grep` 相关能力的现有实现，明确"哪些已有、哪些要新增、会不会与现状冲突"。
- **诉求边界**：列清 **In Scope / Out of Scope**，把模糊处向用户确认（一次问清，别在文档里留 TODO）。

产出：一段**需求边界对齐结论**（含现状佐证：表名、字段、现有接口路径）。高风险链路（见 §4）此处即与用户对齐。

### ② 产出结构化需求文档

按 `assets/requirement-doc-template.md` 写 `requirements.md`，**必须覆盖**以下要素（codex 会逐项核）：

1. **背景与目标**：要解决什么、成功度量（可量化）。
2. **In/Out of Scope**：明确边界，防止过度设计与遗漏。
3. **用户故事 / 功能点**：每条带**唯一编号**（F1、F2…），便于复审与追溯。
4. **主流程 + 异常流 + 空状态**：正常路径之外，**必须**覆盖失败、并发、空数据、无权限、超限等分支。
5. **数据字段**：名称/含义/约束（写"最长 50 字符"而非 `VARCHAR(50)`；DDL 留给 architect-design）。
6. **与现状的关系**：复用/改造/新增分别是什么，是否影响既有行为。
7. **验收标准**：每条功能给**可测试、可度量**的 Given/When/Then 或检查点。
8. **依赖与风险**：外部依赖、资质前置、高风险链路标注。

**职责边界**（越界即超范围，codex 会判 SUGGESTION/MEDIUM）：
- ❌ 不写 API 接口契约、DDL 类型、索引（→ architect-design）
- ❌ 不做 UI 颜色/布局/字体（→ prototype-generate）
- ❌ 不做技术选型（→ architect-design）

### ③ codex 复审（用 Agent 工具，不是 Skill）

通过 `codex:rescue` 触发；它内部用 `Agent` 工具 `subagent_type: "codex:codex-rescue"` 转发。
**禁止 `Skill(codex:rescue)`**（会重入并挂起会话）。

复审提示词要点（模板见 `assets/codex-review-prompt-template.md`）：
- 给 codex 看 `requirements.md` 全文 + ① 阶段的现状对齐结论；
- 要求它**按需求质量维度**审，而非代码维度（维度清单见 `config.review.dimensions`）：
  - **完整性**：异常流/空状态/权限/超限是否遗漏；功能点是否有未定义的口径。
  - **一致性**：前后是否矛盾、术语是否统一、是否与现有系统/已确认结论冲突。
  - **可实现性**：是否违反现状约束（如假设了不存在的字段/接口）、依赖是否成立。
  - **可测试性**：验收标准是否可度量、可执行，有没有"尽量""更好"这种不可验收措辞。
  - **范围**：是否过度设计、是否越界写了 API/DDL/UI、是否遗漏 In Scope 项。
- 要求按 **HIGH / MEDIUM / LOW / SUGGESTION** 分级逐条给结论，并指明**对应哪个功能编号/章节**。

> codex 默认偏代码审查，**务必在提示词里显式声明"这是需求文档评审，不要评代码"**，否则它会跑偏。

### ④ 修订 + 同线程复核（内循环）

- 按 codex 的 **HIGH / MEDIUM**（`config.review.blocking_levels`）逐条修订 `requirements.md`；LOW / SUGGESTION 记日志，不阻塞。
- 修订后**回到同一 codex 线程复核**：`codex:rescue` 透传 `--resume`（`config.review.resume_same_thread=true`），
  在提示词里说明"已按你的 X 项修订（对应功能 Fn），请复核并确认是否还有阻塞项"，让 codex 保留上下文。
- 对 codex 提的、你判断为**有意收窄/属 Out of Scope**的点，要在回传里明确说明理由请它确认，而不是默默忽略。
- 直到 codex 明确 **无 HIGH/MEDIUM（CLEAR）**；超过 `config.review.max_rounds` 仍未收敛则停下，把分歧点交用户决策。

### ⑤ 放行与下游

- 写循环日志到 `config.output.log_path`（模板 `assets/requirement-review-loop-template.md`）：对齐结论、各轮 codex 结论、遗留 LOW/SUGGESTION。
- 按 `config.handoff` 提示**下游**：业务评审（`business-requirement-review`）→ UI 设计基线（`ui-design-baseline`）→ 架构设计（`architect-design`）。
- **本 Skill 只产出需求文档与日志，不直接进入 UI/架构/开发**；下游 Skill 由用户确认后再启动（闸门见 CLAUDE.md 工作流）。

---

## 3 闸门（强制）

1. 现状未对齐前不动笔（涉及数据/接口必须先查真实 DDL 与现有实现）。
2. 有 HIGH/MEDIUM 未关闭，需求**不算定稿**，不进入下游评审/设计。
3. codex 必须用 `Agent`（`subagent_type: "codex:codex-rescue"`），永不 `Skill(codex:rescue)`。
4. 复核续用同一 codex 线程（`--resume`），保留上下文，避免重复劳动。
5. 查真实数据/DDL 一律走 `config.database` MCP，禁止猜表结构、禁止跨库套字段。
6. 复审提示词必须显式声明"需求文档评审"，约束 codex 按需求维度而非代码维度审。
7. 高风险链路（支付回调、订单状态机、用户权限、跨新老系统双端）需求边界必须在 ① 阶段与用户对齐。

---

## 4 高风险提示

支付/订单/权限/跨系统等链路的需求：① 阶段对齐结论务必带现状佐证（真实表/字段/接口）并与用户确认；
需求文档里这些功能点要**显式标注高风险**并写清边界与回滚预期，便于下游 architect-design 重点设计。
本 Skill 不替用户决策业务策略（如定价、风控阈值），遇到时停下问清。

---

## 5 可移植性

换项目只改 `config.json`：
- `output.*` → 需求文档与日志输出位置；
- `database.servers[]` → 新项目的 MCP 库与用途（无则置空，对齐时不查库）；
- `context.*` → 现状信息源（现有代码路径、领域规则文档等）；
- `review.dimensions / blocking_levels / max_rounds` → 复审维度与放行线；
- `handoff.*` → 下游衔接的 Skill 名。

SKILL.md 不含任何项目硬编码，复制即用。
