# Subagent Dev Orchestrator

通用的「主会话编排 + 子 agent 实现 + codex 复审」串行开发编排 Skill。
技术栈无关，整目录复制到任意项目后只改 `config.json` 即可用。

## 核心模型

- **主会话**：只编排，不写业务代码。读 `tasks.md`，串行驱动每个任务。
- **子 agent**：每个任务一个独立会话（Agent 工具），按 `design.md`/`tasks.md` 直接实现。
- **codex:rescue**：任务级代码复审（只读），逐条标注 P0/P1/P2。
- **内循环**：实现 → codex 复审 → 同一子 agent 修复（SendMessage 续用）→ codex 复审 …… 直到无 P0/P1。
- **放行线**：无 P0/P1 即过；P2 记入 CHANGELOG 遗留项，不阻塞。

## 两种入口模式

- **模式 A 规格驱动**：已有 `design.md` + `tasks.md`（经确认）→ 直接逐任务循环。
- **模式 B 描述驱动**：只有一段需求描述 → 主会话先轻量拆解出最小 `tasks.md`，并渲染成排版精良的 **`tasks-review.html`（给用户确认的产物，非 md）**，经用户确认后再循环；codex 复审基准为"需求描述 + tasks.md 口述契约 + 项目规范"。需求复杂/契约不明时应改走 `architect-design`（模式 A）。

启动时按现有产物自动判定（`config.intake.mode = auto`）。

## 快速开始

1. 模式 A：确认 `design.md`/`tasks.md` 已确认；模式 B：直接给需求描述即可。
2. 确认本机 Codex CLI 已就绪（否则 `/codex:setup`）。
3. 触发本 Skill（关键词：按子 agent 编排开发 / 逐任务开发 / codex 把关开发）。
4. 模式 B 会先产出最小 tasks.md 并请你确认；确认后主会话逐任务循环，全部通过后提示进入测试。

## 目录结构

```
subagent-dev-orchestrator/
  SKILL.md                              # Skill 定义与编排规则（技术栈无关）
  config.json                           # 唯一需按项目修改的文件
  README.md                             # 本文件
  references/
    gotchas.md                          # 坑点（codex 调用、子会话续用、熔断等）
    examples.md                         # 一个完整任务的内循环示例
  assets/
    subagent-task-prompt-template.md    # 给子 agent 的任务实现提示词模板
    codex-review-prompt-template.md     # 给 codex:rescue 的复审提示词模板
    tasks-review-template.html          # 模式 B 给用户确认的「交互式 HTML 确认器」模板（非 md）
    codex-review-report-template.html   # 可选：codex 复审结果可视化报告模板（颜色编码+折叠）
    changelog-template.md               # CHANGELOG 模板
    task-loop-log-template.md           # 每个任务的内循环日志模板
  logs/                                 # 任务级编排日志
  outputs/                              # 预留
```

## HTML 优先（参考 Thariq《The Unreasonable Effectiveness of HTML》）

凡给人看/决策的产物一律输出自包含 HTML：AI 生成的是「界面」而非「文档」。`tasks-review.html` 是交互式确认器——颜色编码 + 折叠 + 逐项决策 + 「生成回复复制回 Claude」的用完即弃编辑器闭环。codex 复审结论也可渲染成可视化报告。详见 SKILL.md §2.5。

## 关键原则

- **只编排不编码**：主会话绝不直接改业务代码。
- **codex 用 Agent 工具调**：`subagent_type: "codex:codex-rescue"`，禁止 `Skill(codex:rescue)`（会挂起）。
- **修复续用同一子会话**：用 SendMessage 回传 codex 问题，保留上下文。
- **闸门严守**：有 P0/P1 不放行下一任务；交付级 code review 与发布永远手动触发。
- **可移植**：换项目只改 `config.json`。
