---
name: technical-design-review
description: architect-design 输出 design.md 和 tasks.md 后调用，或用户说"评审技术设计""审核架构方案""review design"时调用。从架构合理性、API 契约、数据库设计、需求对齐、任务拆解、安全性能六个维度对技术设计进行独立评审，输出 technical-design-review.md。评审通过后方可进入开发阶段。
triggers:
  - 评审技术设计
  - 审核架构方案
  - review design
  - 技术方案评审
  - 审核 design.md
  - 检查任务拆解
---

# Technical Design Review Skill

## 概述

本 Skill 是技术设计阶段的**质量闸门**，对 architect-design 产出的 design.md、tasks.md 和 DB 交付物进行独立多维度评审。

评审从六个专业维度展开：
1. **架构合理性**：模块边界、耦合度、一致性、可扩展性
2. **API 契约质量**：RESTful 规范、与现有接口一致性、完整性、错误处理
3. **数据库设计质量**：规范化、索引策略、迁移安全性、数据完整性
4. **需求-设计对齐性**：需求全覆盖、无范围蔓延、状态机完整
5. **任务拆解可执行性**：粒度合理、依赖正确、验收标准明确
6. **安全性与性能**：鉴权设计、注入防护、N+1 查询、分页策略

**输出结论**：
- `PASS`：无问题，可进入开发阶段
- `CONDITIONAL`：仅有低优先级问题，或中优先级问题但不影响核心实现，可附条件通过
- `BLOCKED`：存在高优先级问题，或影响核心实现的中优先级问题，必须修复后重新评审

**阅读顺序**：`SKILL.md`（本文件）→ `references/gotchas.md` → `references/domain-rules.md` → 其余按需

---

> **最重要的规则（G0）**：**当功能涉及前端页面时（`has_ui = true`），必须逐一核验 .pen 文件与前端任务/页面的全量映射。** 这是历史上最高频的遗漏问题——前端开发产出的页面与 .pen 设计稿对应不上、丢失页面。本 Skill 必须在评审中构建完整的映射表并逐行确认，任何缺失都是高优先级问题。纯后端功能（`has_ui = false`）跳过此检查。
>
> **第二重要的规则（G1）**：**评审必须独立于 architect-design 的设计过程。** 不得因为"设计者已考虑过"就跳过验证。设计过程中的盲点正是评审需要捕获的。

---

## 第一步：收集评审对象与上下文

### 1.1 读取配置

优先读取 `../shared-config.json`，如不存在再读取 `config.json`。

### 1.2 检查前置交付物

确认以下文件已存在：

```
{feature-dir}/requirements.md           ← 必须存在（需求基准）
{feature-dir}/prototype.md              ← 必须存在（页面基准）
{feature-dir}/design.md                 ← 必须存在（评审主对象）
{feature-dir}/tasks.md                  ← 必须存在（评审主对象）
{feature-dir}/DB/schema.sql             ← 条件必须（如涉及数据库变更）
{feature-dir}/DB/er-diagram.md          ← 推荐存在
{feature-dir}/ui-design-baseline.md     ← 条件必须（如涉及前端页面）
{feature-dir}/ui-design-{page-key}.pen  ← 条件必须（如涉及前端页面）
```

如 design.md 或 tasks.md 不存在，停止并提示用户先完成 architect-design。

### 1.3 判断功能类型：是否涉及前端 UI

检查 tasks.md 中是否包含 `type: 前端` 的任务，或 prototype.md 中是否定义了页面结构：

- **有前端页面** → 标记 `has_ui = true`，启用 .pen 全量映射检查（步骤 1.4）
- **纯后端功能**（如纯 API、定时任务、数据迁移）→ 标记 `has_ui = false`，跳过 .pen 检查

> 判断依据：tasks.md 中存在 `type: 前端` 任务，**或** feature-dir 下存在 `.pen` 文件，**或** prototype.md 中定义了页面结构 → `has_ui = true`

### 1.4 构建 .pen 文件清单（仅当 `has_ui = true` 时执行）

**当功能涉及前端页面时，必须在评审开始前完成 .pen 文件盘点。** 这是本 Skill 最重要的前置动作之一。

1. 扫描 `{feature-dir}/` 目录下所有 `.pen` 文件，列出完整清单
2. 从 `prototype.md` 中提取所有 page-key（页面标识）
3. 从 `ui-design-baseline.md` 中提取所有 page-key（如存在）
4. 构建**五列映射表**：

```
| page-key | prototype.md 页面 | .pen 文件 | tasks.md 前端任务 | design.md API |
|----------|------------------|-----------|------------------|---------------|
| tag-list | ✅ 标签列表页     | ✅ ui-design-tag-list.pen | ✅ T5 | ✅ GET /api/tags |
| tag-edit | ✅ 标签编辑弹窗   | ❌ 缺失    | ✅ T6 | ✅ PUT /api/tags/{id} |
```

**任何一列出现 ❌，都是高优先级问题。** 特别是 .pen 文件缺失——这直接导致前端开发无设计基准，产出页面必然与设计不符。

> **纯后端功能不执行此步骤**，评审报告中映射表附录标注"本功能无前端页面，跳过 .pen 映射检查"。

### 1.4 阅读需求基准

按以下顺序独立阅读：
1. `requirements.md` — 记录功能清单、业务规则、权限矩阵
2. `prototype.md` — 记录页面结构、交互流，**逐页记录 page-key**
3. `ui-design-baseline.md`（如存在）— 记录 UI 约束，**逐页记录 page-key**
4. 逐个打开 `.pen` 文件 — 确认每个 .pen 的页面内容与 prototype.md 对应页面一致

**阅读完成后再开始评审 design.md，不要边读需求边看设计。**

---

## 第二步：阅读现有代码与数据库现状

### 2.1 项目代码

读取 `config.development.project_structure_path` 了解现有分层。

基于 design.md 中涉及的模块，搜索现有代码：
- 相关 Controller / Service / Mapper / Entity
- 现有 API 接口的命名和响应格式
- 已有的公共抽象（BaseEntity、通用 Result 包装等）

### 2.2 数据库现状

通过 MCP 工具 `mcp__{config.database.mcp_server}__execute_sql` 查询：
- design.md 中涉及的现有表结构（`SHOW CREATE TABLE`）
- 现有索引策略（`SHOW INDEX FROM`）
- 外键关联关系
- 相关枚举值的实际存储方式

查询模板详见 `references/api.md`。

---

## 第三步：按维度评审

详细规则见 `references/domain-rules.md`，核心检查项如下：

### 3.1 架构合理性

- [ ] 模块边界是否与现有项目分层一致（Controller/Service/Repository）？
- [ ] 新模块与已有模块的依赖方向是否合理（不出现循环依赖）？
- [ ] 是否复用了已有的公共抽象（BaseEntity、通用 Result、分页封装等），而非重新发明？
- [ ] 模块间通信方式（直接调用 / 事件 / 消息）是否与现有风格一致？
- [ ] 设计是否对未来扩展留有余地，但不过度设计？

### 3.2 API 契约质量

- [ ] URL 路径命名是否遵循现有项目的 RESTful 风格？
- [ ] HTTP 方法选择是否正确（GET 查询 / POST 创建 / PUT 更新 / DELETE 删除）？
- [ ] 请求参数是否完整（每个前端页面需要的字段都有来源）？
- [ ] 响应结构是否与现有接口的 Result 包装格式一致？
- [ ] 错误码是否定义完整（参数校验失败、业务规则冲突、权限不足、资源不存在）？
- [ ] 分页接口是否使用项目统一的分页参数风格？
- [ ] 是否有遗漏的接口（prototype.md 中每个操作都有对应 API）？

### 3.3 数据库设计质量

- [ ] DDL 中的表名/字段名是否遵循现有命名规范（下划线命名、前缀等）？
- [ ] 新增字段类型是否与已有表中同含义字段一致（如 status 字段统一用 tinyint 还是 varchar）？
- [ ] 索引策略是否覆盖了高频查询场景（列表查询、关联查询的 WHERE/JOIN 字段）？
- [ ] 是否有冗余索引或缺失索引？
- [ ] 外键/关联关系是否与 ER 图一致？
- [ ] ALTER TABLE 对现有数据的兼容性（NOT NULL 字段是否有默认值？）
- [ ] 字符集和排序规则是否与项目统一？
- [ ] test-data.sql 是否覆盖了正常、边界、异常数据？

### 3.4 需求-设计对齐性 ⚠️ 最高权重维度

> **本维度是评审重点中的重点。** 历史上最频繁的问题是：前端开发产出的页面与 .pen 设计稿对应不上、丢失页面。根因在于技术设计阶段未做全量映射核验，导致遗漏在开发阶段被放大。

#### 3.4.1 .pen 文件全量映射检查（仅当 `has_ui = true` 时执行，BLOCKING 级别）

> 如果步骤 1.3 判定 `has_ui = false`（纯后端功能），跳过此子项，在评审报告中标注"本功能无前端页面，跳过 .pen 映射检查"。

**当功能涉及前端页面时，此子项为最高优先级检查项，必须第一个执行。**

基于第一步 1.4 构建的五列映射表，逐行核验：

- [ ] prototype.md 中每个页面（含弹窗、抽屉、Tab 子页面）是否都有对应的 `.pen` 文件？
- [ ] 每个 `.pen` 文件的 page-key 是否与 prototype.md 中的 page-key 完全一致（命名、数量）？
- [ ] tasks.md 中每个 `type: 前端` 任务是否都关联了对应的 `.pen` 文件（通过 **设计稿** 字段或描述中的明确引用）？
- [ ] 是否有 `.pen` 文件在 tasks.md 中无任何前端任务关联（设计稿产出了但没人开发）？
- [ ] 是否有前端任务没有关联任何 `.pen` 文件（凭空开发，无设计基准）？
- [ ] design.md 中的每个前端相关 API，是否都能关联到至少一个 `.pen` 文件的页面？

**判定规则**：
- `.pen` 文件缺失 → **HIGH / BLOCKED**（无设计基准，前端无法正确还原）
- 前端任务未关联 `.pen` → **HIGH / BLOCKED**（开发将脱离设计稿）
- `.pen` 存在但无前端任务 → **MED**（设计稿产出了但可能被遗忘）
- page-key 命名不一致 → **MED**（会导致开发时找错文件）

> **注意**：如果 tasks.md 使用的是不包含"设计稿"字段的旧版模板，且前端任务描述中也未引用 .pen 文件，评审应将此标记为 **MED** 并建议 architect-design 在任务描述中补充 .pen 引用，而非直接 BLOCKED。待 architect-design 的 tasks-template 升级后再升格为 BLOCKED。

#### 3.4.2 需求功能全覆盖

- [ ] requirements.md 中每个功能点是否都有对应的设计落地（API + 数据模型 + 状态流转）？
- [ ] design.md 中是否有超出 requirements.md 范围的设计（范围蔓延）？
- [ ] 权限矩阵中的每个角色权限是否在 API 设计中有对应的鉴权逻辑？
- [ ] 状态流转设计是否覆盖了 requirements.md 中定义的所有状态转换？
- [ ] 业务规则（如数量限制、计算公式）是否在设计中有明确的实现位置？
- [ ] prototype.md 中每个页面的数据展示字段，是否都能通过已设计的 API 获取？

### 3.5 任务拆解可执行性

- [ ] 每个任务是否在 2-8 小时可完成的粒度？
- [ ] 任务之间的依赖关系是否正确且无环？
- [ ] 后端任务是否先于依赖它的前端任务？
- [ ] 每个任务是否有明确的验收标准（不是"完成开发"，而是"API 返回正确响应"）？
- [ ] 是否有遗漏的任务（如数据库迁移任务、配置变更任务）？
- [ ] 前后端任务标注是否正确（`type: backend` / `type: frontend`）？
- [ ] 依赖标注是否正确（`depends: backend` 对应的后端任务是否真正存在）？

### 3.6 安全性与性能

- [ ] 涉及用户输入的接口是否有参数校验设计？
- [ ] 权限校验是否在 Service 层而非仅在 Controller 层？
- [ ] 批量操作是否有数量限制防护？
- [ ] 列表查询是否有分页设计？是否防止了无条件全表扫描？
- [ ] 关联查询是否存在 N+1 问题？
- [ ] 涉及金额或关键状态变更的操作是否设计了事务边界？
- [ ] 文件上传（如有）是否有大小/类型限制？
- [ ] 敏感数据（密码、token）是否有脱敏或加密设计？

---

## 第四步：输出评审报告

使用 `assets/review-template.md` 输出到：

```
{feature-dir}/technical-design-review.md
```

每个问题必须包含：
- **问题描述**：具体说明哪里有问题
- **评审维度**：属于六个维度中的哪一个
- **优先级**：高（阻塞）/ 中（建议修复）/ 低（可忽略）
- **修复建议**：可执行的具体改法
- **依据**：来自需求文档 / 现有代码 / 数据库查询的具体引用

> 不允许写"设计不够合理"、"建议优化"等无法执行的反馈。

---

## 第五步：给出结论

根据问题优先级，给出整体结论：

| 结论 | 条件 |
|---|---|
| `PASS` | 无任何问题 |
| `CONDITIONAL` | 仅有低优先级问题，或中优先级问题但不影响核心实现 |
| `BLOCKED` | 存在高优先级问题，或影响核心实现的中优先级问题 |

**BLOCKED 时**，明确告知用户：需要修复哪些问题 → 在 design.md / tasks.md / DB 交付物中修正 → 再次触发本 Skill 评审。

修复后重新评审时，由 architect-design 修改设计文档，再触发本 Skill 复审。

---

## 第六步：完整性自检

使用 `assets/checklist-template.md` 对评审进行完整性自检。

可选运行验证脚本：
```bash
python scripts/validate_review.py --dir {feature-dir}
```

---

## 第七步：记录运行日志

将评审摘要追加到 `logs/` 目录，格式参考 `logs/README.md`。

文件命名：`{YYYY-MM-DD}-{feature-name}-round{N}.md`

日志内容：日期、功能名、评审轮次、结论、各维度问题数量、输出文件路径。

---

## Gotchas（最高优先级阅读）

详见 `references/gotchas.md`，最关键四条：

1. **G0 — .pen 文件全量映射是第一优先级** ⚠️：历史上最高频的致命问题。prototype.md 的每个页面必须有 .pen 文件，每个 .pen 文件必须被 tasks.md 的前端任务引用。任何断裂都是 BLOCKED 级别。**评审报告必须包含完整映射表。**

2. **G1 — 必须独立评审**：不能因为设计者"已经考虑过"就跳过检查。设计盲点正是评审的价值所在。

3. **G3 — DDL 必须重新查表验证**：不能只看 schema.sql 的语法正确性，必须通过 MCP 查询现有表结构，确认 ALTER TABLE 和新表不与现有结构冲突。

4. **G5 — 需求-设计对齐必须双向检查**：不仅要检查"需求是否被设计覆盖"，还要检查"设计是否超出需求范围"。

---

## 文件索引

| 文件 | 用途 | 何时读取 |
|---|---|---|
| `config.json` | 项目配置（MCP 连接、代码路径） | 第一步，必读 |
| `references/gotchas.md` | 常见评审错误 | 开始前必读 |
| `references/domain-rules.md` | 详细评审规则与检查清单 | 第三步 |
| `references/examples.md` | 示例评审报告 | 不确定格式时参考 |
| `references/api.md` | MCP 查询模板 | 第二步 |
| `references/glossary.md` | 术语定义 | 遇到歧义术语时查阅 |
| `assets/review-template.md` | 评审报告模板 | 第四步 |
| `assets/checklist-template.md` | 评审完整性自检清单 | 第六步 |
| `scripts/validate_review.py` | 验证评审报告格式 | 第六步 |
| `logs/` | 历次评审记录 | 输出前查阅 |
