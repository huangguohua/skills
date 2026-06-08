---
name: ui-design-baseline
description: 需求评审通过后调用，或用户说"定设计基线""统一设计规范""给 UI 建规则"时调用。基于 requirements.md 和 prototype.md，定义本次需求的视觉与交互基线，明确 page-key、组件规范、状态集合，对齐当前项目设计语言。输出 ui-design-baseline.md，作为 prototype-generate 的前置约束。
triggers:
  - 定设计基线
  - 设计基线
  - 统一设计规范
  - 给 UI 建规则
  - 设计规则
  - UI 基线
---

# UI Design Baseline Skill

## 概述

本 Skill 是 UI/设计阶段的**第一步**，在 business-requirement-review 通过后、prototype-generate 之前执行。

**核心职责**：为本次需求建立统一的设计规则基线，确保后续原型与高保真设计稿风格一致、命名统一、状态完整。

**职责边界**：
- ✅ 定义页面清单与 page-key 命名
- ✅ 锁定颜色体系、布局密度、组件风格
- ✅ 明确状态集合（加载/空态/错误/禁用）
- ✅ 建立命名规范（HTML 属性、.pen 文件、画板）
- ✅ 校验字段口径（通过 MCP 查询）
- ❌ 不直接产出原型页面或设计稿（属于 prototype-generate）
- ❌ 不做技术设计或前端实现
- ❌ 不修改 requirements.md 或 prototype.md

**阅读顺序**：`SKILL.md`（本文件）→ `references/gotchas.md` → `references/domain-rules.md` → 其余按需

---

> **最重要的规则**：**设计基线必须以项目设计基线文件（`config.design_system.*`）为底座，不得另起一套视觉体系。** 所有扩展必须在现有基线上做最小增量。如基线文件不存在，先运行 `design-system-init`。

---

## 第一步：检查前置条件

**必须存在以下文件**：

```
{config.output_dir}/{feature-name}/requirements.md    ← 已确认
{config.output_dir}/{feature-name}/prototype.md       ← 已确认
```

如果 business-requirement-review 未通过，提示用户先完成需求评审。

优先读取 `../shared-config.json` 获取项目配置。

---

## 第二步：读取项目设计基线

**必须先读取当前项目配置指定的设计基线文件**：

1. 从 `config.design_system.style_guide_path` 读取视觉基线（颜色、布局、动效）
2. 从 `config.design_system.component_rules_path` 读取组件规范
3. 从 `config.design_system.page_templates_path` 读取页面模板

> 如果上述文件不存在，提示用户先运行 `design-system-init` Skill 生成项目设计基线。

至少锁定以下基线项：

| 基线项 | 来源 |
|---|---|
| 主色体系（主色、语义色） | style-guide.md |
| 布局规范（侧栏、导航、容器） | style-guide.md |
| 组件风格（表格、表单、弹窗） | component-rules.md |
| 动效节奏 | style-guide.md |
| 页面模板（列表/弹窗/报表） | page-templates.md |

> 本次需求若有超出基线的设计需要（如新色彩、新布局模式），必须明确记录为"扩展项"并说明理由。

---

## 第三步：提取页面清单与 page-key

从 `requirements.md` 和 `prototype.md` 提取：

### 3.1 页面清单

| page-key | 中文名 | 页面类型 | 模板类型 | 权限 |
|---|---|---|---|---|
| `{kebab-case}` | {中文页面名} | 新增/改造 | 列表/弹窗/报表/详情 | {角色列表} |

**page-key 命名规则**（强制）：
- 使用 kebab-case，如 `plugin-manage`、`ad-source`
- 与 prototype.md 中页面语义一致
- 后续 HTML `data-page`、`.pen` 文件名必须使用相同 page-key
- 禁止中文、驼峰、下划线

### 3.2 状态矩阵

每个页面必须定义以下状态的覆盖情况：

| page-key | 默认 | 加载 | 空态 | 错误 | 禁用 | 弹窗 | 抽屉 |
|---|---|---|---|---|---|---|---|
| `{key}` | ✅ | ✅/-/[后续] | ✅/-/[后续] | ✅/-/[后续] | ✅/-/[后续] | ✅/-/[后续] | ✅/-/[后续] |

**标记值说明**（与 `references/domain-rules.md` 2.3 节一致）：
- `✅`：本次需要设计此状态
- `-`：不适用，需在矩阵下方说明原因
- `[后续]`：本期不做，计划后续迭代

> 标准状态集共 7 项：默认 / 加载 / 空态 / 错误 / 禁用 / 弹窗 / 抽屉。详见 `references/domain-rules.md` 2.1 节。

---

## 第四步：校验字段口径（MCP 查询）

对 prototype.md 中列出的展示字段，通过 `config.database.mcp_server` 配置的 MCP 工具校验：

- 字段是否存在
- 枚举值是否与需求一致
- 统计口径是否明确（如聚合方式、时间范围）

查询模板见 `references/api.md`。

> 口径不明确的字段必须标注 `[待确认]`，不能在设计基线中写假值。

---

## 第五步：定义组件规范

基于项目组件规范（`config.design_system.component_rules_path`），针对本次需求锁定：

### 5.1 复用组件

列出本次需求直接复用的现有组件（不需要额外设计）：

| 组件 | 场景 | 参考页面 |
|---|---|---|
| {项目表格组件} | 列表页 | {项目现有列表页路径} |
| {项目弹窗+表单组件} | 编辑弹窗 | {项目现有弹窗页路径} |

### 5.2 扩展组件

列出需要在基线上扩展的组件（需要额外设计）：

| 组件 | 扩展内容 | 理由 |
|---|---|---|
| {组件名} | {扩展说明} | {为什么基线不够用} |

### 5.3 全局约束

从项目组件规范中继承以下全局约束（具体值见 `config.design_system.component_rules_path`）：

- 弹窗宽度范围
- 表单标签宽度范围
- 操作列/时间列宽度
- 按钮顺序约定

---

## 第六步：输出 ui-design-baseline.md

使用 `assets/spec-template.md` 作为模板，输出到：

```
{config.output_dir}/{feature-name}/ui-design-baseline.md
```

对照 `assets/checklist-template.md` 完成自检。

---

## 第七步：用户确认闸门

输出完成后提示用户确认设计基线。

**确认前禁止**：
- 进入 prototype-generate（生成 HTML 或 .pen）
- 进入技术设计

**确认后**：基线锁定，后续 prototype-generate 必须以此为约束。

---

## 第八步：记录运行日志

将运行摘要追加到 `logs/` 目录。

文件命名：`{YYYY-MM-DD}-{feature-name}.md`

日志内容：日期、功能名、页面数量、page-key 列表、扩展项数量、字段校验结果摘要。

---

## Gotchas（最高优先级阅读）

详见 `references/gotchas.md`，最关键三条：

1. **不得另起视觉体系**：必须以项目设计基线文件（`config.design_system.style_guide_path`）为底座，扩展项需标注理由。如基线文件不存在，先运行 `design-system-init`。

2. **page-key 必须在基线阶段锁定**：后续 HTML、.pen、前端路由都依赖此命名，改动成本极高。

3. **状态集合不能遗漏**：每个页面至少覆盖默认态 + 空态 + 错误态，否则设计稿会遗漏、前端会自行发挥。

---

## 文件索引

| 文件 | 用途 | 何时读取 |
|---|---|---|
| `config.json` | 项目配置（MCP 连接 + design_system 路径） | 第一步，必读 |
| `{config.design_system.style_guide_path}` | 项目视觉基线（颜色、布局、动效） | 第二步，必读 |
| `{config.design_system.component_rules_path}` | 项目组件规范 | 第二步 |
| `{config.design_system.page_templates_path}` | 项目页面模板 | 第二步 |
| `references/domain-rules.md` | page-key 命名规则、状态矩阵规则、组件规范规则 | 第三~五步 |
| `references/gotchas.md` | 常见错误 | 开始前必读 |
| `references/examples.md` | 示例基线文档片段 | 不确定格式时参考 |
| `references/api.md` | MCP 字段校验查询模板 | 第四步 |
| `references/glossary.md` | 术语定义 | 遇到歧义时查阅 |
| `assets/spec-template.md` | ui-design-baseline.md 输出模板 | 第六步 |
| `assets/checklist-template.md` | 基线完整性检查清单 | 输出前自检 |
| `scripts/validate_output.py` | 验证 baseline 完整性 | 第六步，输出后执行 |
| `scripts/init_spec.sh` | 初始化输出文件 | 第一步（可选） |
| `logs/` | 历次运行记录 | 输出前查阅 |
