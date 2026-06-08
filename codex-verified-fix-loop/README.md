# Codex Verified Fix Loop

通用的「定位 → 修复 → codex 复审循环」Skill。技术栈无关，整目录复制到任意项目后只改 `config.json` 即可用。

## 核心模型

把人工实践「查找问题 → 解决 → codex review → 修复 → codex 复核 → …… 直到全部解决」固化为闭环：

- **主会话**：亲自定位（查日志/查 DB MCP/读代码）并做**最小改动**。
- **codex:rescue**：每次改完做只读复审，按 HIGH/MEDIUM/LOW/SUGGESTION 分级。
- **内循环**：改 → codex 复审 → 按 HIGH/MEDIUM 修复 → **同一 codex 线程**（`--resume`）复核 → 直到 CLEAR。
- **放行线**：无 HIGH/MEDIUM 即过；LOW/SUGGESTION 记日志不阻塞。
- **收尾**：写循环日志，按 `config.handoff` 提示可选的编译/测试/发布，不自动执行高风险步骤。

## 与 subagent-dev-orchestrator 的区别

| | codex-verified-fix-loop | subagent-dev-orchestrator |
|---|---|---|
| 适用 | 单一缺陷 / 小需求 | 多任务全量开发（design.md + tasks.md） |
| 谁写代码 | **主会话亲自** | 每任务一个子 agent |
| codex 角色 | 质量闸门（同左） | 任务级质量闸门 |
| 重量 | 轻，随手可用 | 重，规格驱动 |

需求复杂/跨多文件/契约不明 → 转 `architect-design` → `subagent-dev-orchestrator`。

## 快速开始

1. 给一段缺陷描述或小需求描述。
2. 确认本机 Codex CLI 就绪（否则 `/codex:setup`）。
3. 触发本 Skill（关键词：查找问题并修复 / codex 把关修复 / codex 复核到没问题）。
4. 主会话定位→改动→codex 复审循环；全部 CLEAR 后提示可选编译/测试/发布。

## 目录结构

```
codex-verified-fix-loop/
  SKILL.md                              # Skill 定义与闭环规则（技术栈无关）
  config.json                           # 唯一需按项目修改的文件（含数据库 MCP / 日志获取 / 复审参数）
  README.md                             # 本文件
  references/
    gotchas.md                          # 坑点（codex 调用方式、续线程、大日志处理、MCP 查库等）
    examples.md                         # 一个完整缺陷修复的内循环实例（优惠券锁案例）
  assets/
    codex-review-prompt-template.md     # 给 codex:rescue 的复审提示词模板
    codex-recheck-prompt-template.md    # 同线程复核（--resume）提示词模板
    fix-loop-log-template.md            # 每次循环的日志模板
  logs/                                 # 循环日志输出
```

## 关键原则

- **codex 用 Agent 工具调**：`subagent_type: "codex:codex-rescue"`，禁止 `Skill(codex:rescue)`（会挂起）。
- **复核续用同一线程**：`--resume` 保留上下文。
- **HIGH/MEDIUM 不放行**：未关闭不进收尾/下游。
- **查库走 MCP**：禁止猜表结构。
- **高风险停下确认**：支付/订单/权限/生产数据改动前与用户对齐，发布前先编译+测试。
- **可移植**：换项目只改 `config.json`。
