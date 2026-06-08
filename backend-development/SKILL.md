---
name: backend-development
description: >
  development-orchestrator 分派后调用。按 design.md 和 tasks.md 实现后端功能，
  遵循项目编码规范和后端 gotchas，支持修复 review 问题并回写状态。
triggers:
  - 开发后端
  - 实现接口
  - 修复后端 review 问题
inputs:
  - requirements.md
  - design.md
  - tasks.md
  - REVIEW_REPORT.md（修复轮次时）
outputs:
  - 后端代码变更
  - SQL 变更脚本
  - CHANGELOG.md（后端条目）
  - REVIEW_REPORT.md（状态回写）
reads:
  - config.codebase.backend_framework
  - config.development.coding_standards_path
  - config.development.backend_gotchas_path
  - config.development.project_structure_path
dependencies:
  - development-orchestrator（上游编排）
---

# Backend Development

> **定位**：后端功能实现层——根据 `design.md` 和 `tasks.md` 中的后端任务，编写符合项目编码规范的后端代码，并在修复轮次中处理 review 问题后回写状态。

---

## 1 前置条件

在开始后端开发前，必须确认以下产物已就绪：

| 产物 | 闸门说明 |
|---|---|
| `requirements.md` | 用户已确认需求 |
| `design.md` | 用户已确认技术方案（含接口定义、数据模型） |
| `tasks.md` | 用户已确认任务拆解，本 Skill 只处理其中的后端任务 |

若处于修复轮次，还需要：

| 产物 | 说明 |
|---|---|
| `REVIEW_REPORT.md` | 包含"待修复"的后端问题条目 |

---

## 2 核心开发流程

### Step 1：读取任务

- 解析 `specs-mcp/<feature>/tasks.md`，提取分派给本 Skill 的后端任务列表
- 确认每个任务的优先级、依赖关系、验收标准

### Step 2：读取编码规范

- 读取 `config.development.coding_standards_path` 指向的编码规范文档
- 了解命名约定、分层结构、异常处理规范、日志规范等
- **重点**：后端框架为 `config.codebase.backend_framework`，必须严格遵循其分层约定

### Step 3：读取后端陷阱清单

- 读取 `config.development.backend_gotchas_path` 指向的陷阱文档
- 同时参考本 Skill 的 `references/gotchas.md`
- 在编码过程中逐条对照，避免踩坑

### Step 4：读取项目结构

- 读取 `config.development.project_structure_path` 了解目录布局
- 确认新代码应放置的模块和包路径
- 检查是否有可复用的现有组件

### Step 5：逐任务实现

对每个后端任务，按以下顺序执行：

| 子步骤 | 动作 | 说明 |
|---|---|---|
| 5.1 | 阅读 `design.md` 中对应接口定义 | 明确入参、出参、异常码 |
| 5.2 | 检查现有代码 | 避免重复实现，确认可复用的 Service / Mapper |
| 5.3 | 编写代码 | 按分层结构：Controller → Service → ServiceImpl → Mapper → XML |
| 5.4 | 编写 SQL 变更 | 若涉及表结构变更，先查看现有表结构再编写 DDL/DML |
| 5.5 | 权限配置 | 新接口必须配置对应的权限标识 |
| 5.6 | 最小化验证 | 检查编译通过、接口定义与 `design.md` 一致 |

### Step 6：更新 CHANGELOG

- 在 `specs-mcp/<feature>/CHANGELOG.md` 中追加后端变更条目
- 格式参见 `references/examples.md` 中的 CHANGELOG 条目示例
- 必须包含：变更类型、涉及文件、变更摘要

### Step 7：修复轮次处理（仅在修复场景）

当由编排层分派修复任务时，执行以下额外步骤：

| 子步骤 | 动作 | 说明 |
|---|---|---|
| 7.1 | 读取 `REVIEW_REPORT.md` | 提取所有"待修复"的后端问题 |
| 7.2 | 逐问题分析 | 理解问题原因，定位涉及代码 |
| 7.3 | 实施修复 | 按编码规范修复，确保不引入新问题 |
| 7.4 | 验证修复 | 确认修复后编译通过、逻辑正确 |
| 7.5 | 回写状态 | 将对应问题在 `REVIEW_REPORT.md` 中标记为"已修复"，附修复说明 |
| 7.6 | 更新 CHANGELOG | 记录本轮修复内容 |

---

## 3 编码约束

| 编号 | 约束 | 说明 |
|---|---|---|
| C1 | 严格遵循分层结构 | 不在 Controller 层写业务逻辑，不在 Service 层写 SQL |
| C2 | 接口契约不可擅自变更 | 若 `design.md` 定义的接口需要调整，必须先与用户确认 |
| C3 | 事务边界明确 | 涉及多表写操作必须加 `@Transactional`，只读操作使用 `readOnly=true` |
| C4 | SQL 注入防护 | 禁止字符串拼接 SQL，必须使用参数化查询 |
| C5 | 权限检查必配 | 新增接口必须配置权限标识，不可裸露 |
| C6 | 异常统一处理 | 使用项目统一的异常处理机制，不吞异常 |

---

## 4 禁止事项

| 编号 | 禁止行为 | 原因 |
|---|---|---|
| P1 | 未读编码规范就开始编码 | 极易违反项目约定，后续 review 返工 |
| P2 | 擅自修改已有接口的入参/出参 | 破坏前后端契约，导致前端联调失败 |
| P3 | 标记"已修复"但未实际修改代码 | 虚假闭环，review 时会被打回 |
| P4 | 修改前端代码 | 后端 Skill 的职责边界仅限后端代码 |
| P5 | 跳过 CHANGELOG 更新 | 变更不可追溯，编排层无法汇总 |

---

## 5 日志记录

每次执行都应在 `logs/` 目录下记录运行日志：

```
文件名：YYYY-MM-DD_<feature>_backend_round<N>.md

内容：
- 执行时间
- 功能名称
- 处理的任务编号列表
- 每个任务的完成状态
- 涉及的文件变更清单
- SQL 变更清单（如有）
- CHANGELOG 更新摘要
- 修复问题列表及状态（修复轮次时）
- 遇到的问题与解决方案
```

日志用于追溯开发过程，便于编排层汇总和问题排查。
