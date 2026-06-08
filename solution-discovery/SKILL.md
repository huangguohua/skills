---
name: solution-discovery
description: 当用户描述一个新功能想法、业务问题或改进点时调用。通过查询现有代码、数据库、接口，探索系统现状与约束，输出结构化 discovery.md，为后续需求设计提供事实依据。不做方案细节设计，只做现状探索与方向收敛。
triggers:
  - 新需求
  - 新功能
  - 业务问题
  - 方案探索
  - 现状分析
  - 这个功能怎么做
  - 调研一下
---

# Solution Discovery Skill

## 概述

本 Skill 用于在需求设计启动前，系统性地探索现有系统现状，收集事实依据，形成可行的方案方向。

**职责边界**：
- ✅ 探索现有代码结构与实现
- ✅ 查询数据库验证数据模型
- ✅ 识别技术约束与业务边界
- ✅ 提出 2-3 个方向级方案（不含细节设计）
- ❌ 不输出 API 设计或数据库 DDL（属于 architect-design）
- ❌ 不输出 UI 原型（属于 prototype-generate）
- ❌ 不做任何代码修改

**阅读顺序**：`SKILL.md`（本文件）→ `references/gotchas.md` → `references/domain-rules.md` → 其余按需

---

## 第一步：检查配置

优先读取上级目录下的共享配置 `../shared-config.json`，如不存在或未填写，再读取同目录下的 `config.json`。

如果 `config.json` 为空或关键字段未填写，**在开始探索前先询问用户**：

```
需要以下项目信息才能开始：
1. 项目名称（用于命名输出目录）
2. MCP 服务器名（读取 config.database.mcp_server）
3. 数据库名（读取 config.database.database_name）
4. 后端代码路径
5. 前端代码路径（如有）
6. 输出目录（默认 specs-mcp/）

请提供以上信息，或确认使用 config.json 中的默认值。
```

收到回答后，优先更新 `../shared-config.json`，并运行 `../sync_shared_config.py` 同步到各 Skill 的 `config.json`。
本 Skill 同目录下的 `config.json` 仅作为共享配置的本地副本。

---

## 第二步：理解问题

向用户确认以下信息（如未在初始描述中提及）：

1. **核心诉求**：这个功能/改进解决什么问题？
2. **使用者**：谁在用这个功能？
3. **成功标准**：怎样算做好了？
4. **已知约束**：有时间、性能、兼容性要求吗？

> 不要一次问所有问题。根据用户描述的详细程度，只问缺失的部分。

---

## 第三步：系统性探索

按以下顺序探索，每步记录关键发现。详细探索规则见 `references/domain-rules.md`。

### 3.1 代码现状
- 搜索与需求相关的现有模块、类、接口
- 识别可复用的代码路径
- 记录关键文件位置（格式：`path/to/file.java:行号`）

### 3.2 数据库现状
- 通过 MCP 工具 `mcp__{config.database.mcp_server}__execute_sql` 查询相关表的结构（字段名、类型、约束）
- 查询现有数据量级与分布（抽样）
- 识别缺失字段或需要新增的表

> 所有数据库查询统一通过 MCP 工具执行，查询模板见 `references/api.md`。结果要记录原始 SQL 和返回值。

### 3.3 接口现状
- 列出现有相关 API 端点
- 确认入参/出参结构
- 识别复用 vs 新建的判断

### 3.4 外部依赖
- 是否依赖第三方服务、SDK、外部 API？
- 是否有权限、配额、稳定性风险？

---

## 第四步：识别约束与风险

参考 `references/domain-rules.md` 中的约束识别清单，记录：
- 技术约束（框架限制、性能瓶颈、兼容性要求）
- 数据约束（现有数据迁移、字段格式、枚举值）
- 业务约束（权限模型、多租户隔离、审计要求）

---

## 第五步：提出方案方向

基于探索结论，提出 **2-3 个方向级方案**，每个方案说明：
- 核心思路（1-2 句）
- 主要改动范围
- 主要风险点
- 粗略复杂度（低/中/高）
- 推荐倾向（可选，需说明理由；但最终决策是用户的职责）

**不要在此阶段输出 API 设计、DDL、UI 原型。** 那是后续 Skill 的职责。

---

## 第六步：输出 discovery.md

使用 `assets/spec-template.md` 作为模板，输出到：

```
{config.output_dir}/{feature-name}/discovery.md
```

---

## 第七步：记录运行日志

将本次运行摘要追加到 `logs/` 目录，格式参考 `logs/README.md`。

文件命名：`{YYYY-MM-DD}-{feature-name}.md`

日志内容：日期、功能名、探索摘要（查询了哪些表、关键发现）、方向结论、输出文件路径。

---

## Gotchas（最高优先级阅读）

详见 `references/gotchas.md`，以下是最关键的三条：

1. **禁止经验性假设**：所有关于现有系统的陈述，必须有代码行或 SQL 查询结果作为依据。不能写"通常这类系统会..."。

2. **不要过早收敛到单一方案**：Discovery 阶段的产出是方向选项，不是决策。给用户选择空间。

3. **数据库查询结果要记录原始值**：不能只说"表中有用户信息"，要写明查了什么、返回了什么。

---

## 文件索引

| 文件 | 用途 | 何时读取 |
|---|---|---|
| `config.json` | 项目配置（MCP 连接信息） | 第一步，必读 |
| `references/domain-rules.md` | 探索规则与约束识别清单 | 第三、四步 |
| `references/gotchas.md` | 常见错误与规避方式 | 开始前必读 |
| `references/examples.md` | 示例 discovery 输出 | 不确定格式时参考 |
| `references/glossary.md` | 术语定义 | 遇到歧义术语时查阅 |
| `references/api.md` | MCP 查询模式速查 | 第三步 |
| `assets/spec-template.md` | discovery.md 输出模板 | 第六步 |
| `assets/checklist-template.md` | 探索完整性检查清单 | 输出前自检 |
| `scripts/collect_context.py` | 收集代码库上下文 | 第三步，可选执行 |
| `scripts/check_schema.py` | 生成 DB Schema 查询 SQL | 第三步，生成 SQL 后通过 MCP 执行 |
| `scripts/validate_output.py` | 验证 discovery.md 完整性 | 第六步，输出后执行 |
| `logs/` | 历次运行记录 | 输出前查阅，避免重复探索 |
