---
name: development-orchestrator
description: >
  architect-design 完成后调用。读取 tasks.md 判断前后端依赖，按序触发
  backend-development 和 frontend-development，维护 CHANGELOG.md，
  管理修复轮次分派。
triggers:
  - 开始开发
  - 按 tasks.md 编排
  - 启动前后端开发
  - 分派修复任务
inputs:
  - requirements.md
  - prototype.md
  - design.md
  - tasks.md
outputs:
  - CHANGELOG.md
dependencies:
  - backend-development
  - frontend-development
---

# Development Orchestrator

> **定位**：轻量编排层——只读取任务、判断依赖、触发子 Skill、汇总变更日志、分派修复，**绝不直接编写业务代码**。

---

## 1 前置条件

在启动编排前，必须确认以下产物已通过各自闸门：

| 产物 | 闸门说明 |
|---|---|
| `requirements.md` | 用户已确认需求 |
| `prototype.md` | 用户已确认原型 |
| `design.md` | 用户已确认技术方案 |
| `tasks.md` | 用户已确认任务拆解 |

若任意产物缺失或未经用户确认，**禁止进入编排阶段**，应提示用户先完成上游流程。

---

## 2 最小编排契约

以下三种场景覆盖绝大多数编排需求：

| 场景 | 条件 | 编排策略 |
|---|---|---|
| **纯后端** | `tasks.md` 中仅含后端任务 | 仅触发 `backend-development`，完成后直接进入 CHANGELOG 汇总 |
| **纯前端** | `tasks.md` 中仅含前端任务 | 仅触发 `frontend-development`，完成后直接进入 CHANGELOG 汇总 |
| **前后端并行** | `tasks.md` 中同时包含前后端任务 | 先判断依赖关系：若前端依赖后端接口，则后端优先；若无依赖，可并行触发 |

> **判断依赖的方法**：读取 `tasks.md` 中每个前端任务的"依赖"字段，若引用了后端任务编号，则该前端任务须在对应后端任务完成后才能启动。

---

## 3 修复轮分派协议

当 `test-report.md` 或 `REVIEW_REPORT.md` 中存在待修复问题时，编排层负责分派修复任务。

| 步骤 | 动作 | 说明 |
|---|---|---|
| R1 | 读取问题清单 | 从 `test-report.md` 或 `REVIEW_REPORT.md` 提取所有"待修复"条目 |
| R2 | 分类归属 | 根据问题描述判断属于后端还是前端 |
| R3 | 生成修复任务 | 为每个问题创建修复任务描述 |
| R4 | 分派到对应 Skill | 后端问题 → `backend-development`，前端问题 → `frontend-development` |
| R5 | 等待修复完成 | 修复完成后由对应 Skill 将问题状态回写为"已修复" |
| R6 | 更新 CHANGELOG | 记录本轮修复内容 |
| R7 | 确认闭环 | 检查是否仍有"待修复"条目；若有则回到 R1 开始新一轮 |

---

## 4 编排步骤（主流程）

### Step 1：读取 tasks.md

- 解析 `specs-mcp/<feature>/tasks.md`
- 提取所有任务条目，识别每个任务的类型（后端/前端）、优先级、依赖关系
- 汇总任务状态

### Step 2：确定执行顺序

- 根据依赖关系构建执行顺序
- 无依赖的后端和前端任务可并行
- 有依赖的前端任务排在其依赖的后端任务之后

### Step 3：触发子 Skill

- 按照确定的顺序触发 `backend-development` 和/或 `frontend-development`
- 向子 Skill 传递：功能目录路径、任务列表、相关规范文档路径

### Step 4：收集变更日志

- 每个子 Skill 完成一轮开发后，汇总其变更内容
- 更新 `specs-mcp/<feature>/CHANGELOG.md`
- CHANGELOG 格式参见 `assets/changelog-template.md`

### Step 5：提示进入测试

- 当所有任务开发完成后，提示用户：
  - "前后端开发已完成，建议进入测试阶段（触发 `testing-expert`）"
- **绝不**自动触发 `delivery-code-review`（代码审查始终由用户手动触发）

---

## 5 禁止事项

| 编号 | 禁止行为 | 原因 |
|---|---|---|
| P1 | 直接编写或修改业务代码 | 编排层只做调度，代码实现由子 Skill 负责 |
| P2 | 自动触发 `delivery-code-review` | 代码审查必须由用户手动触发 |
| P3 | 跳过未完成的任务直接进入测试 | 必须确保所有任务完成或明确标记为"延期" |
| P4 | 修改 `REVIEW_REPORT.md` 的问题状态 | 问题状态由对应开发 Skill 在修复后回写 |

---

## 6 编排日志记录

每次编排执行都应在 `logs/` 目录下记录运行日志，格式如下：

```
文件名：YYYY-MM-DD_<feature>_round<N>.md

内容：
- 编排时间
- 功能名称
- 本轮触发的子 Skill 及任务编号
- 各任务完成状态
- CHANGELOG 更新摘要
- 下一步建议
```

日志用于追溯编排过程，便于问题排查和流程审计。
