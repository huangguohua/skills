---
name: frontend-development
description: development-orchestrator 分派后调用。按 design.md 与 ui-design.html/.pen 实现前端页面，遵循项目设计基线和前端 gotchas，支持修复 review 问题并回写状态。
triggers:
  - 开发前端
  - 还原设计稿
  - 写页面
  - 修复前端 review 问题
  - 实现页面
  - 前端开发
---

# Frontend Development Skill

## 概述

本 Skill 用于在 `requirements.md`、`design.md`、`tasks.md` 与 `ui-design.html`/`.pen` 确认后进行前端页面实现：严格遵循项目既有技术栈与设计基线，按设计稿进行高保真还原，并支持基于 `REVIEW_REPORT.md` 的问题修复与状态回写。

**职责边界**：
- ✅ 阅读 design.md 中的前端任务并逐项实现
- ✅ 按 ui-design.html/.pen 进行设计还原
- ✅ 实现路由、状态管理、样式变更
- ✅ 处理页面交互、空状态、加载态、异常态
- ✅ 修复 REVIEW_REPORT.md 中前端相关问题并回写状态为"已修复"
- ✅ 更新 CHANGELOG.md 前端条目
- ❌ 不修改后端代码（属于 backend-development）
- ❌ 不做 UI 设计决策（属于 ui-design-baseline）
- ❌ 不直接修改 REVIEW_REPORT.md 的问题状态为"已解决"（由 delivery-code-review 决定）

**阅读顺序**：`SKILL.md`（本文件）→ `references/gotchas.md` → `references/domain-rules.md` → 其余按需

---

## 读取配置

优先读取上级目录下的共享配置 `../shared-config.json`，如不存在或未填写，再读取同目录下的 `config.json`。

需要关注的配置项：
- `config.codebase.frontend_path` — 前端代码根目录
- `config.codebase.frontend_framework` — 前端技术栈
- `config.design_system.*` — 设计系统配置（样式指南、组件规则、页面模板）
- `config.development.frontend_gotchas_path` — 前端易错点文档
- `config.development.coding_standards_path` — 编码规范文档

如果关键字段未填写，**在开始开发前先询问用户**：

```
需要以下信息才能开始前端开发：
1. 前端代码路径
2. 技术栈（默认 Vue2 + ElementUI）
3. 设计稿路径（.pen 或 .html）
4. 需求文档目录（specs-mcp/<feature>/）

请提供以上信息，或确认使用 config.json 中的默认值。
```

---

## 第一步：读取任务清单

1. 读取 `specs-mcp/<feature>/tasks.md`，筛选出所有 **前端任务**
2. 读取 `specs-mcp/<feature>/design.md`，了解技术方案中的前端部分（组件拆分、路由规划、状态管理方案）
3. 若为修复模式，读取 `specs-mcp/<feature>/REVIEW_REPORT.md`，筛选出标记为"待修复"的前端问题

**输出**：前端任务列表（含优先级和依赖关系）

---

## 第二步：读取设计基线

1. 读取 `config.design_system.style_guide_path` — 色彩、字号、间距、圆角等设计变量
2. 读取 `config.design_system.component_rules_path` — 组件使用规范（哪些场景用哪个组件、禁止自定义组件的边界）
3. 读取 `config.design_system.page_templates_path` — 页面布局模板（列表页、详情页、表单页等标准结构）
4. 读取 `config.development.coding_standards_path` — 命名规范、目录结构、代码风格

> 在写任何代码之前，必须完成设计基线阅读。参见 `references/gotchas.md` G1。

---

## 第三步：读取前端 Gotchas

读取以下两份 gotchas 文件：
1. `references/gotchas.md` — 本 Skill 内置的通用前端易错点
2. `config.development.frontend_gotchas_path` — 项目级前端 gotchas（如存在）

将 gotchas 要点记入工作上下文，后续每个任务实现时逐条对照。

---

## 第四步：逐任务实现页面

按任务列表逐项开发，每个任务的实现步骤：

### 4.1 创建/修改文件结构
- 按项目目录结构创建组件文件（使用路径别名，不用相对路径，参见 G8）
- 注册路由（若为新页面）
- 注册权限标识（若涉及权限控制）

### 4.2 实现页面布局
- 按设计稿还原页面结构（HTML/模板层）
- 使用设计系统中的标准组件，不自创组件
- 响应式断点处理（参见 G7）

### 4.3 实现交互逻辑
- 表单验证规则
- 按钮操作（增删改查、导出、批量操作等）
- 弹窗/抽屉的打开/关闭/重置逻辑（参见 G4）
- 分页、排序、筛选联动

### 4.4 实现数据通信
- 定义 API 调用方法（确认接口路径与字段名与后端一致，参见 G3）
- 请求/响应拦截处理
- 错误处理与用户反馈

### 4.5 处理状态覆盖
- 空数据状态（Empty State）
- 加载中状态（Loading State）
- 请求失败/网络异常状态（Error State）
- 无权限状态
- 参见 G5，所有状态必须显式处理

### 4.6 样式实现
- 严格按设计稿还原颜色、字号、间距、圆角（参见 G2）
- 使用设计变量，不硬编码色值
- Scoped 样式避免全局污染

---

## 第五步：设计稿还原验证

完成实现后，逐页面对照 `.pen` 或 `.html` 设计稿：

1. **布局结构**：组件层级、排列方式是否一致
2. **视觉还原**：色彩、字号、间距、圆角是否匹配
3. **交互行为**：悬停、聚焦、点击、加载等状态是否完整
4. **响应式**：不同视口宽度下的表现

> 使用 `assets/checklist-template.md` 进行逐项检查。

---

## 第六步：自测（交互与状态）

对每个页面执行以下自测：

1. **正常流程**：完整走通主要交互路径
2. **边界输入**：空值、超长值、特殊字符
3. **状态切换**：空态 → 有数据 → 加载中 → 错误态
4. **权限场景**：不同角色看到不同的操作按钮
5. **多浏览器**：至少确认 Chrome 兼容性

---

## 第七步：更新 CHANGELOG

在 `specs-mcp/<feature>/CHANGELOG.md` 中追加前端变更记录：

```markdown
## [前端] YYYY-MM-DD

### 新增
- 新增 XXX 页面（路由：/xxx/list）
- 新增 XXX 组件（components/xxx/）

### 修改
- 修改 XXX 页面的筛选逻辑

### 修复
- 修复 XXX 弹窗未重置表单问题
```

---

## 第八步：修复模式（如适用）

当 `REVIEW_REPORT.md` 中存在标记为"待修复"的前端问题时：

1. 逐条阅读问题描述与审查意见
2. 定位相关代码并修复
3. 修复完成后，由 **本 Skill** 将该问题状态回写为"已修复"
4. 在 CHANGELOG 中记录修复内容

> 注意：状态只能从"待修复"改为"已修复"。"已修复"→"已解决"的状态流转由 delivery-code-review 负责。

---

## 第九步：记录运行日志

将本次运行摘要追加到 `logs/` 目录，格式参考 `logs/README.md`。

文件命名：`{YYYY-MM-DD}-{feature-name}.md`

日志内容：日期、功能名、实现页面列表、修复问题列表（如有）、输出文件路径。

---

## Gotchas（最高优先级阅读）

详见 `references/gotchas.md`，以下是最关键的三条：

1. **G1 — 未读设计基线就写代码**：必须先完成第二步再进入第四步。否则会导致样式不一致、组件用法错误。

2. **G2 — 设计还原偏差**：像素、颜色、间距必须与 .pen 一致。不允许"差不多"。

3. **G5 — 遗漏空/错误/加载状态**：每个数据展示区域必须有三种状态的显式处理。

---

## 文件索引

| 文件 | 用途 | 何时读取 |
|---|---|---|
| `config.json` | 项目配置 | 第一步，必读 |
| `references/gotchas.md` | 前端常见错误（8 条） | 开始前必读 |
| `references/domain-rules.md` | 页面实现规则、设计还原规则、状态覆盖规则 | 第二至六步 |
| `references/examples.md` | 示例页面实现模式 | 不确定写法时参考 |
| `references/glossary.md` | 前端术语定义 | 遇到歧义术语时查阅 |
| `assets/checklist-template.md` | 页面实现检查清单 | 第五步，设计还原验证 |
| `logs/` | 历次运行记录 | 输出前查阅，避免重复实现 |
