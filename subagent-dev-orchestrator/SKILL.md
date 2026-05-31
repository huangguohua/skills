---
name: subagent-dev-orchestrator
description: >
  architect-design 完成（design.md + tasks.md 已确认）后调用。以"主会话编排 + 子 agent 实现 + codex 复审"
  模式串行推进开发：每个任务开一个独立子 agent 会话按 design.md/tasks.md 直接实现，实现后用 codex:rescue
  做代码复审，复审问题回传同一子 agent 修复，再交 codex:rescue 复审，直到无 P0/P1 级问题才进入下一个任务。
  用户说"按子 agent 编排开发""逐任务开发""主会话编排开发""codex 把关开发"时调用。
triggers:
  - 按子 agent 编排开发
  - 逐任务开发
  - 主会话编排开发
  - codex 把关开发
  - 每个任务一个子会话
inputs:
  - specs-mcp/<feature>/design.md   # 模式 A 必需；模式 B 可缺省
  - specs-mcp/<feature>/tasks.md     # 模式 A 必需；模式 B 由本 Skill 轻量生成
  - 自由需求描述                      # 模式 B 入口：用户直接给出的需求文字
  - config.json
outputs:
  - specs-mcp/<feature>/tasks.md            # 模式 B：轻量拆解的机器可读源
  - specs-mcp/<feature>/tasks-review.html    # 模式 B：给用户确认的 HTML 确认稿（非 md）
  - specs-mcp/<feature>/CHANGELOG.md
  - logs/<date>_<feature>_task<N>.md
dependencies:
  - codex:codex-rescue   # 子代理（Agent 工具 subagent_type），非 Skill
---

# Subagent Dev Orchestrator（子 agent 串行开发 + codex 复审编排）

> **通用 Skill**：不绑定具体技术栈，所有项目相关路径/技术栈/数据库均从 `config.json` 读取，可整目录复制到其他项目，只改 `config.json` 即可用。

---

## 0 一句话定位

**主会话（你）只做编排，绝不亲手写业务代码。** 真正的编码在每个任务专属的子 agent 会话里完成；每个任务的质量由 `codex:rescue` 复审把关，形成「实现 → codex 复审 → 子 agent 修复 → codex 复审」的内循环，无 P0/P1 才放行下一个任务。

```
tasks.md（已确认）
   │
   ├─ Task 1 ──► [子 agent 会话 A] 实现 ──► codex 复审 ──┐
   │                    ▲                              │ 有 P0/P1
   │                    └────── 回传问题修复 ◄──────────┘
   │                                 │ 无 P0/P1（通过）
   │                                 ▼  更新 CHANGELOG + 任务日志
   ├─ Task 2 ──► [子 agent 会话 B] ...（同样的内循环）
   │
   └─ ...（串行，逐个任务通过后才进入下一个）
```

---

## 0.5 两种入口模式（启动时先判定）

本 Skill 支持两种需求来源，启动时按现有产物自动判定：

| 模式 | 触发条件 | 入口处理 | 复审对照基准 |
|---|---|---|---|
| **A 规格驱动** | `design.md` + `tasks.md` 已存在且经用户确认 | 直接进 Step 0 解析 tasks.md | `design.md` 契约 + 项目规范 |
| **B 描述驱动** | 没有 design.md/tasks.md，用户只给了一段需求描述 | 先做**轻量拆解**（见 Step 0-B）并经用户确认，生成最小 `tasks.md`，再进逐任务循环 | **需求描述 + 项目规范**（无 design 契约可比） |

> 何时不要用模式 B：需求复杂、涉及多模块契约/数据库建模时，应先走 `architect-design` 产出 design.md/tasks.md（模式 A）。模式 B 只适合**小到中等、契约清晰可口述**的需求。若拆解时发现需求过大或契约不明，**停下来建议用户改走 architect-design**，不要硬拆。

---

## 1 前置闸门

**模式 A**：

| 产物 | 闸门 |
|---|---|
| `specs-mcp/<feature>/design.md` | 用户已确认技术方案 |
| `specs-mcp/<feature>/tasks.md` | 用户已确认任务拆解 |

**模式 B**：无需 design.md/tasks.md，但**轻量拆解出的任务清单必须经用户确认**后才能开始编码（见 Step 0-B），这是模式 B 的闸门。给用户确认的产物是 `tasks-review.html`（排版精良的 HTML，**不是 md**）。

两种模式共同要求：本机已安装并登录 Codex CLI（`codex:codex-rescue` 依赖它）。若未就绪，提示用户运行 `/codex:setup`。

---

## 2 与 development-orchestrator 的区别（不要混用）

| 维度 | `development-orchestrator`（旧） | 本 Skill（`subagent-dev-orchestrator`） |
|---|---|---|
| 并发模型 | 前后端两个 Agent 并行 | **每个任务一个独立子 agent，串行推进** |
| 代码实现 | 触发 backend/frontend 开发 Skill | 子 agent 直接按 design.md/tasks.md 实现 |
| 代码审查 | 不触发，留给手动 code review | **每个任务内置 `codex:rescue` 复审循环** |
| 放行条件 | 任务开发完即可 | **codex 复审无 P0/P1 才进入下一任务** |

两者择一使用；本 Skill 适合"想要每个任务都被 codex 严格把关、逐个收口"的场景。

---

## 2.5 HTML 产物原则（参考 Thariq《The Unreasonable Effectiveness of HTML》）

凡是**给人看 / 让人决策**的产物，一律输出**自包含 HTML**，不用 md。核心理念：**AI 生成的是「界面」而非「文档」，人类从编写者变成审查者/使用者**。落到本 Skill：

| 原则 | 做法 |
|---|---|
| **颜色编码 + 严重度标记** | 任务状态、P0/P1/P2 用颜色 + 徽章区分，一眼分辨轻重 |
| **轻量 JS 交互** | 折叠面板、筛选、分段选择器等纯 vanilla JS，无外部依赖，浏览器直接打开 |
| **打破扁平化** | 用卡片 / Grid 空间化呈现任务、契约、依赖，而非线性长文 |
| **用完即弃编辑器闭环** | 用户在 HTML 里逐项决策（通过/需修改/删除 + 意见）→ 一键「生成回复」→ 复制回 Claude 继续。形成「AI 出界面 → 人类操作 → 导回 AI」闭环 |

适用产物：模式 B 的 `tasks-review.html`（确认器，模板 `assets/tasks-review-template.html`）、可选的 codex 复审报告 `tasks-review` 视图（模板 `assets/codex-review-report-template.html`）。**给用户确认/审阅的内容禁止只甩 md。**

---

## 3 严重级别与放行标准（硬约束）

codex 复审结论按以下级别归类，**通过线 = 无 P0 且无 P1**：

| 级别 | 含义 | 处置 |
|---|---|---|
| **P0** | 阻断性：编译/构建失败、功能不可用、数据错误、安全漏洞、契约破坏 | **必须修复**，否则不放行 |
| **P1** | 严重：明显逻辑错误、与 design.md 契约不符、重大规范违背、边界缺陷 | **必须修复**，否则不放行 |
| **P2** | 次要：可读性、命名、非阻断优化建议 | **可延后**：记入 `CHANGELOG.md` 的"遗留项"，不阻塞放行 |

> 让 codex 在复审输出里**显式标注每条问题的级别**（见 `assets/codex-review-prompt-template.md`）。主会话据此判定是否放行。

---

## 4 主流程（主会话执行）

### Step 0：准备任务清单

先读 `config.json` 得到项目路径/技术栈/规范文档/输出目录，再按模式取得任务清单。

**Step 0-A（模式 A）**：读取 `specs-mcp/<feature>/tasks.md`，提取任务列表、编号、依赖、验收标准。

**Step 0-B（模式 B：从需求描述轻量拆解）**：
1. 通读用户的需求描述，必要时用 AskUserQuestion 澄清 1–3 个关键边界（范围、依赖系统、验收口径）。
2. 在 `config.database` 指定的 MCP 上做**最小事实校验**（涉及的表/字段是否存在），避免拆出脱离现状的任务。
3. 产出一份**最小 tasks.md**写入 `specs-mcp/<feature>/tasks.md`（机器可读源，供子 agent/codex 消费），每个任务含：编号、目标、**验收标准**、依赖、关键契约口述（接口/字段/错误码，能写多细写多细——它将充当模式 B 下 codex 复审的对照基准）。
4. **生成确认稿（HTML，非 md）**：用 `assets/tasks-review-template.html` 渲染出 `specs-mcp/<feature>/tasks-review.html`，把占位符填充为本次拆解内容（每个任务复制一段 `<article class="task">` 卡片）。**给用户确认的产物必须是这份 HTML**——可读性远好于 md，禁止只甩 md 给用户确认。
5. **闸门**：把 `tasks-review.html` 的路径交给用户（提示其在浏览器打开）。该页是**交互式确认器**——用户逐任务选「通过/需修改/删除」并填意见，点「生成回复」得到一段结构化文本复制回对话（用完即弃编辑器闭环）。**未确认不得进入编码**；用户提修改 → 同步更新 tasks.md 并重新渲染 HTML。
6. 拆解中若发现需求过大、跨多模块契约、需要正式数据建模 → 停下，建议改走 `architect-design`（模式 A）。

**两模式汇合**：用 TaskCreate 把每个任务登记为一条 todo，按依赖关系排出**串行执行顺序**（被依赖者先行）。

### Step 1：逐任务循环（对每个任务 N 执行 4.A → 4.D）

#### 4.A 开子 agent 实现任务
用 **Agent 工具**新开一个子 agent 会话（`subagent_type: general-purpose`，或 `claude`），传入精准上下文。提示词参见 `assets/subagent-task-prompt-template.md`，至少包含：
- 本任务编号、目标、验收标准（摘自 tasks.md）；
- **契约来源**：模式 A 取 `design.md` 中与本任务相关的 API 契约 / 数据模型 / 模块边界；模式 B 取 tasks.md 里口述的接口/字段/错误码 + 需求描述原文；
- `config.json` 给出的代码库路径、技术栈、编码规范/坑点文档路径；
- **明确边界**：只实现本任务，不擅自改动其他任务的范围；完成后用一两句汇报"改了哪些文件、关键决策"。

> 记下该子 agent 的 ID/名称——后续修复要用 **SendMessage 续用同一会话**，保留其上下文。

#### 4.B codex:rescue 复审
任务实现产出后，用 **Agent 工具**调用 `codex:codex-rescue`（`subagent_type: "codex:codex-rescue"`，**非 Skill**，切勿 `Skill(codex:rescue)`）。
- 复审提示按 `assets/codex-review-prompt-template.md` 组织：**只读复审，不要改代码**，聚焦本任务改动的文件，对照**复审基准**（模式 A = design.md 契约；模式 B = 需求描述 + tasks.md 口述契约）与项目规范，**逐条给出问题 + 级别(P0/P1/P2) + 文件:行 + 修复建议**。
- 可在请求里给出本任务改动的文件清单/diff 范围，让 codex 聚焦。
- codex 子代理会原样返回 Codex 输出；主会话解析其中的级别标注。
- **（可选）可视化复审报告**：当用户想直观查看本轮复审结论时，用 `assets/codex-review-report-template.html` 渲染成 `specs-mcp/<feature>/review-T<N>-round<R>.html`（颜色编码 + 严重度徽章 + 折叠面板）。纯展示，不改变"无 P0/P1 才放行"的判定。

#### 4.C 判定与修复内循环
- **无 P0/P1** → 该任务通过，转 4.D。
- **有 P0/P1** → 用 **SendMessage 把 codex 的问题清单回传给 4.A 的同一子 agent**，要求逐条修复并复述"如何修的"。修复完成后**回到 4.B 重新 codex 复审**。
- 重复 4.B↔4.C，直到无 P0/P1。
- **熔断**：同一任务复审超过 `config.review.max_rounds`（默认 3）轮仍有 P0/P1，**停下来报告用户**，不要无限循环。

#### 4.D 收口本任务
- 更新 `specs-mcp/<feature>/CHANGELOG.md`（模板 `assets/changelog-template.md`）：本任务改了什么、codex 复审轮次、遗留的 P2 项。
- 写任务日志 `logs/<date>_<feature>_task<N>.md`（模板 `assets/task-loop-log-template.md`）。
- TaskUpdate 标记该任务 completed。
- 进入下一个任务，回到 4.A。

### Step 2：全部任务通过后
- 汇总 CHANGELOG，提示用户："全部任务已逐个通过 codex 复审，建议进入测试阶段（`testing-expert`）。"
- **绝不**自动触发独立交付级 code review（`delivery-code-review` / `ad-code-review-expert`）——那始终由用户手动触发。codex 复审是任务级把关，不替代交付级审查。

---

## 5 禁止事项

| 编号 | 禁止 | 原因 |
|---|---|---|
| P1 | 主会话亲手写/改业务代码 | 编排层只调度，编码归子 agent |
| P2 | 用 `Skill(codex:rescue)` 调 codex | 那会重入命令并挂起会话；必须用 Agent 工具 `subagent_type: "codex:codex-rescue"` |
| P3 | 跳过 codex 复审或在有 P0/P1 时放行下一任务 | 破坏质量闸门 |
| P4 | 每次修复都新开子 agent | 丢失上下文；修复必须 SendMessage 续用原会话 |
| P5 | 多个任务并行硬塞 | 本 Skill 是串行收口模型；如需并行请改用 development-orchestrator |
| P6 | 自动触发交付级 code review / 发布 | 始终人工触发 |

---

## 6 复制到其他项目

1. 整目录复制 `subagent-dev-orchestrator/` 到目标项目的 skills 目录。
2. 只改 `config.json`（项目名、代码库路径、技术栈、规范文档路径、输出目录、复审参数）。
3. SKILL.md / references / assets 全部技术栈无关，无需改动。

详见 `README.md` 与 `references/gotchas.md`。
