---
name: testing-expert
description: 前后端开发完成后调用。Phase 1 设计测试用例并输出 test-cases.md（用户确认后进入 Phase 2），Phase 2 执行测试并输出 test-report.md。测试通过后进入人工 UI 验收和 delivery-code-review。
triggers:
  - 测试
  - 设计测试用例
  - 执行测试
  - 生成测试报告
  - 回归测试
phases:
  - id: phase-1
    name: 测试用例设计
    output: test-cases.md
    gate: user-confirm
  - id: phase-2
    name: 测试执行
    output: test-report.md
    gate: pass-fail
reads:
  - config.testing.test_gotchas_path
  - config.testing.test_strategy
  - config.testing.test_env
  - config.testing.env_start_script
  - config.testing.env_status_script
  - config.database.mcp_server
---

# Testing Expert Skill

## 概述

本 Skill 是开发完成后、代码审查前的**质量闸门**，分两个阶段执行：

1. **Phase 1 — 测试用例设计**：基于 requirements.md、design.md、tasks.md 产出 test-cases.md，覆盖正向/反向/权限/边界/状态流转五个维度，用户确认后才进入 Phase 2。
2. **Phase 2 — 测试执行**：按 test-cases.md 逐条执行测试，产出 test-report.md，每个失败用例必须标注归属（后端/前端/联调/未明确），供编排 Skill 分发修复。

**通过标准**：test-report.md 中所有用例状态为 PASS 时，测试阶段通过，进入人工 UI 验收与 delivery-code-review。

**阅读顺序**：`SKILL.md`（本文件）→ `references/gotchas.md` → `references/domain-rules.md` → 其余按需

---

> **最重要的规则（G1）**：**不要只测试 happy path。** 每个功能点必须同时覆盖正向、反向、边界三类用例，缺少任一类的 test-cases.md 不得通过确认。

---

## Phase 1：测试用例设计

### 第一步：收集测试依据

读取以下文件（必须全部存在）：

```
{feature-dir}/requirements.md    ← 功能规格
{feature-dir}/design.md          ← 技术设计
{feature-dir}/tasks.md           ← 开发任务清单
```

如有任何文件缺失，停止并提示用户补充。

优先读取 `../shared-config.json` 获取共享项目配置；同目录 `config.json` 视为同步后的本地副本。数据库查询统一通过 MCP 工具 `mcp__{config.database.mcp_server}__execute_sql` 执行。

同时读取：
- `references/gotchas.md` — 常见测试陷阱，必读
- `references/domain-rules.md` — 用例格式与覆盖度规则
- `config.testing.test_gotchas_path` — 项目级测试注意事项

---

### 第二步：梳理测试范围

从 requirements.md 提取所有功能点，从 design.md 提取所有接口，从 tasks.md 确认已完成的开发内容，建立功能 → 接口 → 用例的映射关系。

每个功能点必须覆盖以下五个维度：

| 维度 | 说明 | 示例 |
|---|---|---|
| **正向测试** | 正常流程，预期成功 | 使用合法参数创建记录 |
| **反向测试** | 异常输入，预期合理失败 | 必填字段为空、非法格式 |
| **权限测试** | 不同角色的访问控制 | 普通用户访问管理员接口 |
| **边界测试** | 边界值与极端情况 | 空列表、最大长度、负数、零值 |
| **状态流转测试** | 业务状态切换的合法性 | 已完成状态不可回退为进行中 |

---

### 第三步：通过 MCP 查询确认数据模型

对 design.md 中涉及的数据表，通过 MCP 查询确认：

- 表结构与字段类型是否与设计一致
- 枚举值/状态值是否与 requirements.md 一致
- 唯一约束、非空约束是否匹配

查询模板见 `references/api.md`。

---

### 第四步：编写测试用例

使用 `assets/test-cases-template.md` 格式，按功能模块编写测试用例，输出到：

```
{feature-dir}/test-cases.md
```

每个用例必须包含：
- **用例编号**：TC-{模块缩写}-{序号}
- **测试维度**：正向/反向/权限/边界/状态流转
- **前置条件**：数据准备、用户角色
- **测试步骤**：可执行的具体操作
- **预期结果**：精确可验证的结果描述

可运行 `scripts/validate_output.py --check-cases {feature-dir}/test-cases.md` 验证格式。

---

### 第五步：覆盖度自检

使用 `assets/checklist-template.md` 逐项核对：

- [ ] 每个 requirements.md 功能点至少有一条正向用例
- [ ] 每个功能点至少有一条反向/边界用例
- [ ] 所有角色 × 操作的权限组合均有覆盖
- [ ] design.md 中每个接口至少被一条用例调用
- [ ] 状态流转的每条边均有覆盖

---

### Phase 1 闸门：用户确认

将 test-cases.md 呈现给用户，用户确认后方可进入 Phase 2。用户未确认时不得执行测试。

---

## Phase 2：测试执行

### 第六步：准备测试环境

#### 6a. 确认本地服务就绪（当 `config.testing.test_env` = `local` 时）

读取 `config.testing.env_start_script` 和 `config.testing.env_status_script`：

| 条件 | 动作 |
|---|---|
| 两个脚本路径均已配置且文件存在 | 按下方流程执行 |
| 脚本路径为空或文件不存在 | 跳过自动启动，提示用户手动准备环境后再继续 |
| `test_env` ≠ `local` | 跳过此步骤 |

> 脚本路径相对于**项目根目录**，执行时必须先 `cd` 到项目根目录。

**执行流程**（先检查，按需启动）：

```
1. cd {项目根目录}
2. bash {config.testing.env_status_script}
3. 如果退出码 = 0 → 环境已就绪，跳到 6b
4. 如果退出码 ≠ 0 → 执行 bash {config.testing.env_start_script}
5. 等待 5 秒
6. bash {config.testing.env_status_script}（再次检查）
7. 如果退出码 = 0 → 环境就绪，继续
8. 如果退出码 ≠ 0 → 停止测试，输出脚本日志，提示用户排查
```

**安全约束**：
- **不执行 stop 脚本**：避免关掉用户正在调试的环境
- **启动失败不降级**：环境未就绪时禁止继续执行测试，直接中止并报告

#### 6b. 确认测试策略与数据库状态

确认测试策略（读取 `config.testing.test_strategy`）：

- `api-first`：优先通过 API 接口执行测试，配合 MCP 查询验证数据库状态
- `manual`：生成手动测试步骤，人工执行并记录结果

通过 MCP 查询确认数据库环境状态（如测试数据是否就绪）。

---

### 第七步：逐条执行测试

按 test-cases.md 逐条执行：

1. **准备前置数据**：根据用例的前置条件准备
2. **执行测试步骤**：按用例步骤操作
3. **验证结果**：对比预期结果与实际结果
4. **验证数据库状态**：写操作后通过 MCP 查询确认 DB 变更（参考 G3）
5. **记录结果**：PASS / FAIL / BLOCKED / SKIP

---

### 第八步：失败归属标注

对每个 FAIL 用例，必须标注失败归属：

| 归属 | 判断标准 |
|---|---|
| **后端** | 接口返回错误、数据库状态不符、业务逻辑错误 |
| **前端** | 页面渲染异常、交互逻辑错误、字段展示不正确 |
| **联调** | 前后端接口对接不一致（字段名、数据格式、枚举值） |
| **未明确** | 无法判断归属，需进一步排查 |

> 不标注归属的失败用例将导致编排 Skill 无法正确分发修复任务。

---

### 第九步：输出测试报告

使用 `assets/test-report-template.md` 格式，输出到：

```
{feature-dir}/test-report.md
```

报告必须包含：
- 测试概要（总数/通过/失败/阻塞/跳过）
- 每条用例的执行结果
- 失败用例的详细信息（实际结果、截图/日志、归属标注）
- 整体结论（PASS / FAIL）

可运行 `scripts/validate_output.py --check-report {feature-dir}/test-report.md` 验证格式。

---

### Phase 2 闸门：通过/失败

| 结论 | 条件 | 后续 |
|---|---|---|
| **PASS** | 所有用例状态为 PASS 或 SKIP（SKIP 需说明理由） | 进入人工 UI 验收 → delivery-code-review |
| **FAIL** | 存在任何 FAIL 用例 | 按归属分发给对应开发 Skill 修复，修复后重新执行 Phase 2 |

---

## 第十步：记录运行日志

将测试摘要追加到 `logs/` 目录，格式参考 `logs/README.md`。

文件命名：`{YYYY-MM-DD}-{feature-name}-round{N}.md`

日志内容：日期、功能名、测试轮次、Phase 1/Phase 2 结论、用例统计（总数/通过/失败）、失败归属分布、输出文件路径。

---

## Gotchas（最高优先级阅读）

详见 `references/gotchas.md`，最关键四条：

1. **只测试 happy path（G1）**：每个功能点必须同时覆盖正向、反向、边界三类用例。

2. **写操作后不验证数据库状态（G3）**：API 返回成功不代表数据正确，必须通过 MCP 查询确认。

3. **失败用例不标注归属（G6）**：test-report.md 中每个 FAIL 必须有 `归属: 后端/前端/联调/未明确`。

4. **本地服务未启动就开始测试（G9）**：`test_env=local` 时，Phase 2 必须先通过第六步确认环境就绪，未就绪禁止执行测试。

---

## 文件索引

| 文件 | 用途 | 何时读取 |
|---|---|---|
| `config.json` | 项目配置（MCP 连接、测试策略） | 第一步，必读 |
| `references/gotchas.md` | 常见测试陷阱 | 开始前必读 |
| `references/domain-rules.md` | 用例格式、报告格式、归属标注规则 | Phase 1 第四步、Phase 2 第八步 |
| `references/examples.md` | 示例 test-cases.md 与 test-report.md 片段 | 不确定格式时参考 |
| `references/api.md` | MCP 数据库验证查询模板 | 第三步、第七步 |
| `references/glossary.md` | 术语定义 | 按需查阅 |
| `assets/test-cases-template.md` | 测试用例模板 | Phase 1 第四步 |
| `assets/test-report-template.md` | 测试报告模板（含归属标签） | Phase 2 第九步 |
| `assets/checklist-template.md` | 测试覆盖度自检清单 | Phase 1 第五步 |
| `scripts/validate_output.py` | 验证输出文件格式 | Phase 1 / Phase 2 完成后 |
| `logs/` | 历次测试记录 | 输出前查阅 |
