# 坑点（Gotchas）

## codex:rescue 的调用方式

- **必须**用 Agent 工具：`subagent_type: "codex:codex-rescue"`，把复审请求作为 prompt 传入。
- **禁止** `Skill(codex:rescue)` 或 `Skill(codex:codex-rescue)`：前者会重入 `/codex:rescue` 命令并挂起会话，后者根本不是 Skill。
- codex-rescue 是"薄转发器"：它只把请求转发给本机 Codex CLI 并原样返回 stdout，自己不读文件、不分析。所以**复审所需的全部信息（要看哪些文件、对照什么契约、按什么级别归类）都要写进 prompt**。
- 复审要**只读**：在 prompt 里明确"只复审、不要修改代码、不要 --write"。codex-rescue 默认会带 `--write`，除非请求里明确表示只做 review/诊断/只读。
- 若 codex 未安装或未登录，codex-rescue 会返回空；此时提示用户运行 `/codex:setup`，不要把空输出当作"复审通过"。

## 子 agent 会话的续用

- 任务实现和后续修复**必须是同一个子 agent 会话**：第一次用 Agent 工具新建，记下它的 ID/名称；修复时用 **SendMessage** 把 codex 问题回传给它。
- 每轮修复都新开子 agent = 丢失实现上下文 + 重复踩坑。这是最常见的错误。

## 串行，不是并行

- 本 Skill 是"逐任务收口"模型：任务 N 没通过 codex（无 P0/P1）之前，不开任务 N+1 的子 agent。
- 需要前后端并行、各自独立推进时，改用 `development-orchestrator`，不要混用。

## 放行判定

- 放行线是 **无 P0 且无 P1**，不是"零问题"。P2 允许延后，但必须写进 CHANGELOG 的"遗留项"，否则会被悄悄丢失。
- 依赖 codex 在输出里**显式标注级别**。若 codex 输出没有清晰级别，主会话要追问/重新请求一次带级别归类的复审，不要自行猜测放行。

## 熔断与上报

- 同一任务复审超过 `config.review.max_rounds`（默认 3）轮仍有 P0/P1：停下来，把卡点、codex 历次结论、子 agent 修复尝试汇总给用户，由用户决策。不要无限循环烧 token。

## 边界与范围蔓延

- 给子 agent 的 prompt 要圈定"只做本任务"，并要求完成后汇报改了哪些文件。防止一个子 agent 顺手改了其他任务的范围，导致后续任务的 codex 复审范围错乱。

## 模式 B（描述驱动）专属坑点

- 模式 B 没有 design.md 契约，codex 复审与子 agent 实现都以"需求描述 + tasks.md 口述契约"为基准——所以拆解时 tasks.md 里的接口/字段/错误码要尽量写细，否则 codex 无从对照，P0/P1 判定会失真。
- 模式 B 的闸门是"用户确认拆解结果"，不能省。未确认就开子 agent = 跑偏了还不自知。
- **给用户确认的产物必须是 `tasks-review.html`（排版精良的 HTML），不是 md**。md 可读性差，禁止只甩 tasks.md 让用户确认。tasks.md 仅作为子 agent/codex 消费的机器可读源，两者同步更新：用户提修改 → 先改 tasks.md，再重渲染 HTML。
- HTML 模板自包含（内联 CSS/JS、无外部依赖），渲染后把路径交给用户在浏览器打开即可。
- `tasks-review.html` 是**交互式确认器**，不是静态页：每个任务必须带 `data-tid` / `data-title` 属性（JS 靠它汇总「生成回复」文本），渲染时别漏。
- 用户走「生成回复」复制回来的文本是**确认信号 + 修改意见**的结构化结果，按它更新 tasks.md；用户也可能直接口头确认，两种都接受。
- codex 复审报告 HTML（`codex-review-report-template.html`）是**纯展示**，不改变"无 P0/P1 才放行"的判定逻辑——别把"渲染了报告"误当成"通过"。
- 拆解阶段务必在 MCP 上核对涉及的表/字段是否真实存在，别拆出脱离现状的任务。
- 发现需求过大、跨多模块契约、需要正式数据建模 → 停下转 `architect-design`（模式 A），不要在模式 B 里硬拆大需求。

## 与交付级 code review 的关系

- codex 复审是**任务级**把关，快速、聚焦单任务 diff。
- 它**不替代**交付级 `delivery-code-review` / `ad-code-review-expert`——后者覆盖跨任务一致性、整体架构，且始终由用户手动触发。
- 本 Skill 跑完只提示"建议进入测试"，绝不自动触发交付级审查或发布。
