---
name: architect-design
description: requirements.md 和 UI 设计确认后调用。基于需求、原型和现有代码，进行技术方案设计、数据库设计和任务拆解。通过 config.database.mcp_server 校验数据模型。输出 design.md + tasks.md + DB 交付物。
triggers:
  - 做技术设计
  - 输出 design.md
  - 拆研发任务
  - 设计接口和库表
  - 技术方案
---

# Architect Design Skill

## 概述

本 Skill 用于在需求文档（requirements.md）和 UI 设计确认后，基于需求、原型和现有代码进行技术方案设计、数据库设计和研发任务拆解。

**职责边界**：
- ✅ 设计 API 契约（路径、方法、入参、出参、错误码）
- ✅ 设计数据库 DDL/DML，输出 ER 图
- ✅ 设计状态流转与模块边界
- ✅ 拆解研发任务（含前后端、测试）
- ❌ 不做需求分析或原型设计（属于 prd-generate / prototype-generate）
- ❌ 不做 UI 设计（属于 ui-design-baseline）
- ❌ 不写实现代码（属于 backend-development / frontend-development）
- ❌ 不做代码审查（属于 delivery-code-review）

**阅读顺序**：`SKILL.md`（本文件）→ `references/gotchas.md` → `references/domain-rules.md` → 其余按需

---

## 阶段总览

本 Skill 包含 3 个内部阶段和 2 个用户确认闸门：

```
阶段一：架构与 API 方案设计
    ↓ 输出 design.md
    ↓ 【闸门 1】用户确认 design.md
阶段二：数据库设计与交付物
    ↓ 输出 DB/schema.sql + DB/test-data.sql + DB/er-diagram.md + DB/er-diagram-text.md
    ↓ design.md 更新（补充数据库设计章节）
阶段三：任务拆解
    ↓ 输出 tasks.md
    ↓ 【闸门 2】用户确认 tasks.md
```

**强制规则**：闸门 1 未通过前不得进入阶段二；闸门 2 未通过前不得交付给后续 Skill。

---

## 第一步：检查配置与前置条件

### 1.1 读取配置

优先读取上级目录下的共享配置 `../shared-config.json`，如不存在或未填写，再读取同目录下的 `config.json`。

如果 `config.json` 为空或关键字段未填写，**在开始前先询问用户**：

```
需要以下项目信息才能开始：
1. 项目名称（用于命名输出目录）
2. MCP 服务器名（用于数据库校验）
3. 数据库名
4. 后端代码路径
5. 前端代码路径（如有）
6. 后端技术栈（如 Spring Boot + MyBatis-Plus）
7. 前端技术栈（如 Vue2 + ElementUI）
8. 输出目录（默认 specs-mcp/）

请提供以上信息，或确认使用 config.json 中的默认值。
```

收到回答后，优先更新 `../shared-config.json`，并运行 `../sync_shared_config.py` 同步到各 Skill 的 `config.json`。

### 1.2 检查前置交付物

确认以下文件已存在且已经用户确认：

```
{config.output.dir}/{feature-name}/requirements.md   ← 必须存在
{config.output.dir}/{feature-name}/prototype.md       ← 必须存在
{config.output.dir}/{feature-name}/ui-design.*        ← 推荐存在（如有 UI）
{config.output.dir}/{feature-name}/discovery.md       ← 可选（如做过探索）
```

若 requirements.md 不存在，终止并提示用户先完成需求设计。

---

## 第二步：阅读现有代码与项目结构（阶段一前置）

在做任何设计前，**必须先阅读现有代码**。详细规则见 `references/gotchas.md` G1。

### 2.1 项目结构

读取 `config.development.project_structure_path` 了解项目分层与目录结构。

### 2.2 相关模块代码

基于 requirements.md 中的功能描述，搜索以下内容：
- 相关的 Controller / Service / Mapper / Entity 文件
- 相关的前端 API 调用、页面组件
- 现有的类似功能实现（用于保持风格一致）

### 2.3 数据库现状

通过 `config.database.mcp_server` 对应的 MCP 工具查询相关表结构：

```
工具名：mcp__{config.database.mcp_server}__execute_sql
参数：{"query": "SHOW TABLES LIKE '%keyword%'"}
参数：{"query": "DESCRIBE table_name"}
参数：{"query": "SHOW CREATE TABLE table_name"}
```

查询模板详见 `references/api.md`。

---

## 第三步：架构与 API 方案设计（阶段一）

基于需求文档和代码探索结果，设计技术方案。输出格式参照 `assets/design-template.md`。

### 3.1 模块边界划分

- 识别需要新增或修改的模块
- 画出模块间的依赖关系
- 标注公共模块（如权限、日志、审计）的接入方式

### 3.2 API 契约设计

每个 API 必须包含：
- 路径、HTTP 方法
- 请求参数（Query / Body / Path）
- 响应结构（成功 + 失败）
- 错误码定义
- 权限要求

API 设计必须与现有接口风格保持一致（参考 `references/gotchas.md` G2）。

### 3.3 状态流转设计

如涉及状态变更的业务实体，必须画出状态机：
- 所有状态枚举
- 合法的状态转换路径
- 每个转换的触发条件与前置校验

参考 `references/gotchas.md` G3。

### 3.4 输出 design.md

使用 `assets/design-template.md` 模板，输出到：

```
{config.output.dir}/{feature-name}/design.md
```

### 3.5 【闸门 1】用户确认 design.md

将 design.md 呈现给用户，等待确认：

```
design.md 已输出，请确认以下内容：
1. 模块边界是否合理
2. API 契约是否完整
3. 状态流转是否覆盖所有场景
4. 是否有遗漏的边界情况

请回复"确认"或提出修改意见。
```

**未确认前，禁止进入阶段二。**

---

## 第四步：数据库设计与交付物（阶段二）

### 4.1 通过 MCP 校验现有表结构

在编写 DDL 前，必须先查询现有表结构（参考 `references/gotchas.md` G4）：

```sql
-- 查看是否已有同名表
SHOW TABLES LIKE '%target%';

-- 查看已有表结构（如需修改已有表）
SHOW CREATE TABLE existing_table;

-- 查看索引
SHOW INDEX FROM existing_table;

-- 查看外键关联
SELECT TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = DATABASE()
  AND REFERENCED_TABLE_NAME = 'existing_table';
```

### 4.2 输出数据库交付物

在 `{config.output.dir}/{feature-name}/DB/` 目录下输出以下文件：

| 文件 | 内容 |
|---|---|
| `schema.sql` | 完整 DDL（CREATE TABLE / ALTER TABLE），含注释、索引、字符集 |
| `test-data.sql` | 测试数据 DML（INSERT 语句），覆盖正常、边界、异常场景 |
| `er-diagram.md` | Mermaid 格式的 ER 图（可渲染） |
| `er-diagram-text.md` | 纯文本描述的表关系说明（无图形渲染时使用） |

DDL 与 DML 格式规范见 `references/domain-rules.md`。

### 4.3 更新 design.md

将数据库设计章节补充到 design.md 中（表结构摘要、关键字段说明、索引策略）。

---

## 第五步：任务拆解（阶段三）

### 5.1 拆解原则

参考 `references/gotchas.md` G5，任务粒度遵循以下标准：

- **单个任务**应在 2-8 小时内可完成
- 任务之间的依赖关系必须明确
- 前后端任务分开列出
- 每个任务有明确的验收标准

### 5.2 输出 tasks.md

使用 `assets/tasks-template.md` 模板，输出到：

```
{config.output.dir}/{feature-name}/tasks.md
```

### 5.3 【闸门 2】用户确认 tasks.md

将 tasks.md 呈现给用户，等待确认：

```
tasks.md 已输出，请确认以下内容：
1. 任务粒度是否合适（不过粗也不过细）
2. 依赖关系是否正确
3. 验收标准是否明确
4. 是否有遗漏的任务

请回复"确认"或提出修改意见。
```

**未确认前，不得将任务交付给后续开发 Skill。**

---

## 第六步：自检与交付

### 6.1 执行自检

使用 `assets/checklist-template.md` 对输出进行完整性检查。

可选运行验证脚本：
```bash
python scripts/validate_output.py --dir {config.output.dir}/{feature-name}
```

### 6.2 最终交付物清单

确认以下文件全部输出：

```
{config.output.dir}/{feature-name}/
├── design.md              ← 技术方案（已用户确认）
├── tasks.md               ← 任务拆解（已用户确认）
└── DB/
    ├── schema.sql          ← DDL
    ├── test-data.sql       ← 测试数据
    ├── er-diagram.md       ← ER 图（Mermaid）
    └── er-diagram-text.md  ← ER 图（纯文本）
```

---

## 第七步：记录运行日志

将本次运行摘要追加到 `logs/` 目录，格式参考 `logs/README.md`。

文件命名：`{YYYY-MM-DD}-{feature-name}.md`

日志内容：日期、功能名、设计摘要（API 数量、新增表数量、任务总数）、闸门通过情况、输出文件路径。

---

## Gotchas（最高优先级阅读）

详见 `references/gotchas.md`，以下是最关键的三条：

1. **G1 — 先读代码再设计**：不读现有代码就开始设计，是最常见的错误。会导致接口风格不一致、重复造轮子、忽略已有抽象。

2. **G4 — DDL 前先查表**：不通过 MCP 查询现有表结构就写 CREATE TABLE，可能与已有表冲突，或忽略已有字段。

3. **G5 — 任务粒度**：任务太粗（"实现后端"）或太细（"创建 UserDTO 类"）都会导致开发效率低下。单个任务 2-8 小时为宜。

---

## 文件索引

| 文件 | 用途 | 何时读取 |
|---|---|---|
| `config.json` | 项目配置（MCP 连接、代码路径） | 第一步，必读 |
| `references/gotchas.md` | 常见错误与规避方式 | 开始前必读 |
| `references/domain-rules.md` | design.md / tasks.md / DB 交付物格式规范 | 第三、四、五步 |
| `references/examples.md` | 示例 design.md 和 tasks.md 片段 | 不确定格式时参考 |
| `references/api.md` | MCP 查询模式速查 | 第二、四步 |
| `references/glossary.md` | 术语定义 | 遇到歧义术语时查阅 |
| `assets/design-template.md` | design.md 输出模板 | 第三步 |
| `assets/tasks-template.md` | tasks.md 输出模板 | 第五步 |
| `assets/checklist-template.md` | 输出自检清单 | 第六步 |
| `scripts/validate_output.py` | 验证输出完整性 | 第六步，输出后执行 |
| `scripts/init_spec.sh` | 初始化输出目录 | 第一步，可选执行 |
| `logs/` | 历次运行记录 | 输出前查阅，避免重复设计 |
