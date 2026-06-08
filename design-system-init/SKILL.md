---
name: design-system-init
description: 为项目初始化设计系统基线文件。通过分析现有前端代码（SCSS 变量、组件用法、页面结构）提取视觉基线、组件规范和页面模板，输出 style-guide.md / component-rules.md / page-templates.md 三个文件到项目 doc/design-system/ 目录。新项目接入 UI 阶段 Skill 前必须先运行此 Skill。
triggers:
  - 初始化设计系统
  - 生成设计基线
  - 项目设计规范
  - design system init
  - 提取设计变量
---

# Design System Init Skill

## 概述

本 Skill 为项目生成**设计系统基线文件**，作为 `ui-design-baseline` 和 `prototype-generate` 的前置依赖。

**核心职责**：从现有前端代码中提取视觉变量，结合人工分析组件用法和页面结构，生成三个标准化的设计基线文件。

**自动化边界**：
- ✅ **脚本自动**：从 SCSS/CSS/Less 变量文件提取颜色、间距、字体等 Design Token（`scripts/extract_tokens.py`）
- ✅ **人工归纳 + Claude 辅助**：分析组件使用模式，整理组件规范（需阅读 .vue/.jsx 文件）
- ✅ **人工归纳 + Claude 辅助**：识别页面结构类型，整理页面模板（需阅读页面文件）
- ✅ 输出标准化的设计基线文件
- ❌ 不做新的设计（只提取现有事实）
- ❌ 不做需求分析或原型生成

> **注意**：`extract_tokens.py` 只覆盖视觉变量提取。组件规范和页面模板需要 Claude 阅读现有页面代码后人工归纳，不是全自动。

**阅读顺序**：`SKILL.md`（本文件）→ `references/gotchas.md` → `references/domain-rules.md` → 其余按需

---

## 输出文件

```
{config.design_system.style_guide_path}      ← 默认 doc/design-system/style-guide.md
{config.design_system.component_rules_path}  ← 默认 doc/design-system/component-rules.md
{config.design_system.page_templates_path}   ← 默认 doc/design-system/page-templates.md
```

---

## 第一步：检查配置与代码路径

读取 `../shared-config.json` 或 `config.json`，确认：

1. `codebase.frontend_path`：前端代码路径
2. `codebase.frontend_framework`：前端框架（Vue2+ElementUI / Vue3+AntD / React+AntD 等）
3. `design_system` 输出路径配置

如配置为空，询问用户：
```
需要以下信息才能开始：
1. 前端代码根目录路径
2. 前端框架和 UI 组件库（如 Vue2 + ElementUI）
3. 设计文件输出目录（默认 doc/design-system/）
```

---

## 第二步：提取视觉变量（→ style-guide.md）

按以下顺序搜索和提取：

### 2.1 颜色体系

搜索路径（按框架调整）：
- `**/variables.scss`、`**/variables.less`、`**/variables.css`
- `**/element-variables.scss`（ElementUI 项目）
- `**/theme.js`、`**/theme.ts`（Ant Design 项目）
- `tailwind.config.js`（Tailwind 项目）

提取内容：
- 主品牌色
- 语义色（成功、警告、危险、信息）
- 背景色（页面、侧栏、卡片）
- 边框色
- 文字色（主、次、辅助）

### 2.2 布局规范

搜索路径：
- `**/layout/**`、`**/sidebar.*`、`**/navbar.*`
- CSS/SCSS 中的宽度、高度、间距变量

提取内容：
- 侧栏宽度（展开/折叠）
- 导航高度
- 页面容器内边距
- 常见间距值

### 2.3 字体与文字

搜索路径：
- 全局样式文件中的 `font-family`、`font-size`、`line-height`

### 2.4 动效

搜索路径：
- CSS 中的 `transition`、`animation` 相关值

---

## 第三步：提取组件规范（→ component-rules.md）

### 3.1 识别 UI 组件库

从 `package.json` 确认：
- `element-ui` / `element-plus` / `ant-design-vue` / `@ant-design/react` / `@mui/material` 等

### 3.2 分析组件用法

扫描页面文件（`.vue`、`.jsx`、`.tsx`），统计高频组件的使用模式：

| 分析项 | 搜索方式 |
|---|---|
| 表格 | `el-table` / `a-table` / `Table` 组件的常见 props |
| 表单 | `el-form` / `a-form` 的 size、label-width |
| 弹窗 | `el-dialog` / `a-modal` 的 width、footer |
| 按钮 | 主按钮/文本按钮的使用模式 |
| 状态标签 | `el-tag` / `a-tag` 的 type 映射 |
| 开关 | `el-switch` 的场景 |

### 3.3 提取交互约定

- 按钮顺序（取消→确定 还是 确定→取消）
- 危险操作是否有二次确认
- 表单校验方式

---

## 第四步：提取页面模板（→ page-templates.md）

### 4.1 识别页面类型

扫描现有页面文件，按结构分类：
- **列表页**：有表格 + 分页 + 筛选区
- **表单弹窗**：有 dialog + form
- **报表页**：有日期选择 + 数据表/图表
- **详情页**：有描述列表 + 返回按钮
- **配置页**：有 tabs + form

### 4.2 提取模板结构

对每类页面取 2-3 个典型代表，提取：
- 页面区域组成
- 各区域包含的组件
- 参考文件路径

---

## 第五步：生成文件并用户确认

按 `assets/` 目录下的模板生成三个文件。

输出后提示用户确认：
```
已生成设计系统基线：
1. {style_guide_path}（视觉基线：颜色、布局、字体、动效）
2. {component_rules_path}（组件规范：表格、表单、弹窗、按钮）
3. {page_templates_path}（页面模板：列表/弹窗/报表/详情）

请审阅后确认，后续 UI 阶段 Skill 将以此为底座。
```

---

## 第六步：更新 shared-config.json

确认后，检查 `shared-config.json` 中 `design_system` 配置是否正确指向生成的文件路径。如果未配置，自动补充：

```json
{
  "design_system": {
    "style_guide_path": "doc/design-system/style-guide.md",
    "component_rules_path": "doc/design-system/component-rules.md",
    "page_templates_path": "doc/design-system/page-templates.md",
    "design_language": "{从代码分析得出}",
    "component_system": "{从 package.json 得出}",
    "layout_mode": "{从布局分析得出}"
  }
}
```

运行 `../sync_shared_config.py` 同步到各 Skill。

---

## 第七步：记录运行日志

将运行摘要追加到 `logs/` 目录。

文件命名：`{YYYY-MM-DD}-init.md`

日志内容：日期、项目名、前端框架、提取的颜色数量、组件数量、模板数量、输出文件路径。

---

## 降级策略

如果项目没有现成的前端代码（新项目从零开始）：

1. 询问用户选择技术栈（Vue2+ElementUI / Vue3+AntD / React+AntD 等）
2. 基于所选技术栈生成一份**最小可用基线**：
   - style-guide.md：使用组件库默认色值 + 标准布局
   - component-rules.md：使用组件库推荐实践
   - page-templates.md：使用组件库典型页面结构
3. 标注所有值为 `[默认值]`，用户可后续修改

---

## Gotchas（最高优先级阅读）

详见 `references/gotchas.md`，最关键三条：

1. **只提取事实，不做设计**：从代码中读到什么就写什么，不凭经验补充"应该有"的值。

2. **颜色必须从变量文件提取**：不能从页面截图或 DevTools 反推，因为可能有 CSS 覆盖。

3. **每个值必须标注来源文件**：方便后续维护时追溯和更新。

---

## 文件索引

| 文件 | 用途 | 何时读取 |
|---|---|---|
| `config.json` | 项目配置（代码路径 + 输出路径） | 第一步，必读 |
| `references/domain-rules.md` | 提取规则与文件格式规范 | 第二~四步 |
| `references/gotchas.md` | 常见错误 | 开始前必读 |
| `references/examples.md` | 不同技术栈的示例输出 | 不确定格式时参考 |
| `references/glossary.md` | 术语定义 | 遇到歧义时查阅 |
| `assets/style-guide-template.md` | style-guide.md 模板 | 第五步 |
| `assets/component-rules-template.md` | component-rules.md 模板 | 第五步 |
| `assets/page-templates-template.md` | page-templates.md 模板 | 第五步 |
| `scripts/extract_tokens.py` | 从 SCSS/CSS 提取变量 | 第二步，辅助工具 |
| `scripts/init_design_system.sh` | 初始化输出目录 | 第一步（可选） |
| `logs/` | 历次运行记录 | 输出前查阅 |
