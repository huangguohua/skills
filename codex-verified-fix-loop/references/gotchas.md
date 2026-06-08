# Gotchas — Codex Verified Fix Loop

## codex 调用

- **必须用 `Agent` 工具**：`subagent_type: "codex:codex-rescue"`，把原始诉求作为 prompt 转发。
- **禁止 `Skill(codex:rescue)`**：那会重入当前命令并挂起会话。`codex:rescue` 是 skill 入口，但它内部要求转发到 `codex:codex-rescue` 子代理。
- 首次复审前可先跑 `task-resume-candidate --json` 判断是否有可续线程；若 `available:false` 则新开线程。
- Codex 缺失/未登录时停下，提示用户 `/codex:setup`。

## 同线程复核

- 复核续用同一 codex 线程：透传 `--resume`，提示词里说明"已按你的 X 项修复，请复核"。
- 对你判断为"既有设计/有意为之"的 codex 提点，回传里**明确给理由请它确认**，而不是默默忽略——否则下一轮它可能重复提。
- 超过 `config.review.max_rounds` 仍未收敛：停下，把分歧点交给用户决策，别无限循环。

## 分级口径

- codex 的严重度用 **HIGH / MEDIUM / LOW / SUGGESTION**（与 P0/P1/P2 不同，注意 `config.review.severity_levels` 对齐）。
- 阻塞线 = `config.review.blocking_levels`（默认 HIGH + MEDIUM）。LOW / SUGGESTION 记日志，不阻塞收尾。

## 定位（缺陷）

- **大日志**：先 `grep -n <关键词> <log>` 拿行号，再 `awk 'NR>=a && NR<=b' <log>` 取窗口；
  终端色码用 `sed 's/\x1b\[[0-9;]*m//g'` 去掉再读。
- **SSH 拉日志**：用 `config.diagnostics.prod_log_access`；身份文件走 `~/.ssh`，加 `-o BatchMode=yes -o StrictHostKeyChecking=no`。
  注意：不要把多行 ssh 命令塞进 shell 变量再 `$VAR` 执行（zsh 会当成单个文件名报 127）；直接写完整命令。
- **等待服务起来**：用 `until <check>; do sleep 2; done` 轮询，不要 `sleep N &&`（会被拦）。

## 查库（必走 MCP）

- 涉及表结构/字段/真实数据，先用 `config.database` 的 MCP 查真实 DDL 与数据，**禁止猜表结构**。
- 多库时按 `database.servers[].usage` 选对库；新老系统库相互独立，禁止跨库套字段。

## 最小改动

- 只改必需处，不顺手重构、不全量格式化、不迁移返回体。
- 改完用 Edit 精确替换；codex 复审基准是"本次改动"，范围越窄越容易 CLEAR。

## 高风险链路

- 支付回调 / 订单状态机 / 用户权限 / 跨新老系统双端 / 改生产数据：定位结论带数据佐证并与用户对齐后再改。
- 生产数据变更由用户执行或显式授权后再做，附回滚预案。
- 收尾下游（发布）默认只提示不自动跑；`handoff.high_risk_requires_user_confirm=true` 时须用户确认或已设目标。
