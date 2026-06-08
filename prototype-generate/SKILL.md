---
name: prototype-generate
description: ui-design-baseline.md 已确认后调用。基于需求与设计基线，分阶段生成 ui-design.html 交互演示稿和 .pen 高保真设计稿。若 ui-design-baseline.md 不存在，应先转调 ui-design-baseline。闸门 1：用户确认 HTML；闸门 2：用户确认 .pen。
triggers:
  - 出交互稿
  - 生成 HTML 原型
  - 出高保真设计稿
  - 写 HTML 原型
  - 生成 pen
  - 基线已确认出原型
---

# Prototype Generate Skill

## 概述

本 Skill 是 UI/设计阶段的**第二步**，在 ui-design-baseline 确认后执行。

**核心职责**：基于需求文档与设计基线，分三个 Phase 生成交互原型与高保真设计稿。

**内部 Phase**：
- **Phase 1**：原型结构整理（对齐基线，确认页面范围与状态覆盖）
- **Phase 2**：生成 `ui-design.html` 交互演示稿
- **Phase 3**：在 HTML 确认后生成 `.pen` 高保真设计稿

**职责边界**：
- ✅ 生成可演示的 HTML 交互原型
- ✅ 生成高保真 .pen 设计稿
- ✅ 覆盖主路径与关键异常路径的交互状态
- ✅ 遵循 ui-design-baseline.md 的所有约束
- ❌ 不重新定义需求（已在 requirements.md 中锁定）
- ❌ 不做技术架构方案（属于 architect-design）
- ❌ 不做前端代码实现（属于 frontend-development）

**阅读顺序**：`SKILL.md`（本文件）→ `references/gotchas.md` → `references/domain-rules.md` → 其余按需

---

> **最重要的规则**：**先 HTML，再 .pen。HTML 未经用户确认前，禁止生成 .pen 设计稿。** `.pen` 必须以已确认的 HTML 为唯一事实来源。

---

## 第一步：检查前置条件

**必须存在以下文件**：

```
{config.output_dir}/{feature-name}/requirements.md         ← 已确认
{config.output_dir}/{feature-name}/prototype.md            ← 已确认
{config.output_dir}/{feature-name}/ui-design-baseline.md   ← 已确认
```

如果 ui-design-baseline.md 不存在或未确认，提示：
> "当前设计基线尚未确认，建议先运行 ui-design-baseline 并获得用户确认后再生成原型。"

优先读取 `../shared-config.json` 获取项目配置。

---

## Phase 1：原型结构整理

### 1.1 读取设计基线

从 `ui-design-baseline.md` 提取：
- page-key 列表与中文名映射
- 状态矩阵（每个页面覆盖哪些状态）
- 颜色体系与组件规范
- 扩展项与全局约束

### 1.2 读取项目设计基线

读取 `config.design_system` 指定的项目设计基线文件：
- `style_guide_path`：视觉基线（颜色、布局、动效）
- `component_rules_path`：组件规范
- `page_templates_path`：页面模板类型（列表/弹窗/报表/详情）

### 1.3 确认页面范围

将 baseline 中的页面清单与 prototype.md 交叉对比，确认：
- 所有页面都有 page-key
- 所有页面都有明确的模板类型
- 弹窗和抽屉是否需要独立状态画板

> 如发现遗漏页面，先更新 ui-design-baseline.md（需用户确认），再继续。

---

## Phase 2：生成 HTML 交互原型（强制）

### 2.1 HTML 文件拆分规范（强制）

**禁止**把全部页面塞进单一 `ui-design.html`。必须按"终端 → 功能模块/菜单"两级拆分成多个 HTML 文件。每个 HTML 是一个独立可演示的闭环用户路径。

**两级拆分规则**：

| 层级 | 拆分依据 | 命名规则 |
|---|---|---|
| 第 1 级 · 终端拆分（必须） | 前端（小程序 / H5）与后台管理端必须分开成至少两个 HTML | 小程序 / H5 文件**必须**带 `-H5` 后缀；后台文件不带 |
| 第 2 级 · 模块/菜单拆分（按需） | 后台有多个二级菜单 → 每个菜单独立成 1 个 HTML；前端有多个功能模块 → 每个模块独立成 1 个 HTML | 文件名中间段用英文/首字母缩写的模块名 |

**文件命名公式**：

```
{feature-name}[-{module}][-H5].html
```

- `feature-name` = 需求目录名（如 `payment-conversion-optimization`）
- `module` = 功能模块或二级菜单英文名 / 缩写（kebab-case；**仅一个模块时可省略**）
- `-H5` 后缀 = **小程序端 / 移动端 H5 专用**；管理端一律不加此后缀

**示例（本次需求的拆分结果）**：

| 终端 | 模块 | 文件名 |
|---|---|---|
| 小程序 | 结果页转化链路 | `payment-conversion-optimization-result-H5.html` |
| 小程序 | 支付链路 | `payment-conversion-optimization-payment-H5.html` |
| 管理端 | 发券场景规则 | `payment-conversion-optimization-scene-rules.html` |
| 管理端 | 服务号配置 | `payment-conversion-optimization-oa-config.html` |
| 管理端 | 转化看板 | `payment-conversion-optimization-dashboard.html` |
| 管理端 | 运营下发 | `payment-conversion-optimization-issue.html` |
| 管理端 | 首页横幅 | `payment-conversion-optimization-banner.html` |

**禁止**：
- 单个 `ui-design.html` 塞下双端所有页面（旧规范，已废弃）
- 管理端多菜单塞进一个 HTML（即使都是后台）
- 模块名使用中文、驼峰、下划线
- `-H5` 出现在管理端文件名

### 2.2 真实用户路径规范（强制）

原型必须**模拟真实用户操作路径**，不能做成"左侧导航 → 平铺所有页面"的开发者视角目录。

**必须遵循**：

1. **单 HTML = 单入口闭环**：每个 HTML 从一个真实用户进入点开始（小程序首页、后台登录后侧栏点击某菜单），按用户操作顺序自然触达所有页面/状态。
2. **跳转逻辑要真实**：
   - 小程序：首页创建 → 生码 → 结果页 → 点击 CTA → 支付页；返回按钮、分享、保存等动作按真实用户意图触发。
   - 管理端：顶栏 + 侧栏 + 面包屑必须按项目管理端（`config.design_system.layout_mode`）真实布局渲染；侧栏可点击展开/收起；点击菜单进入对应页面；点击表格操作唤起对应弹窗。
3. **状态切换入口要自然**：
   - 生产可见的主路径通过"用户动作"触发（点击按钮、填写表单、返回操作）。
   - 仅开发调试用的状态（如空态 / 加载 / 异常降级）可放在**右下角浮动调试面板**，视觉弱化，明确标注「调试」字样，不放进主内容区。
4. **跨 HTML 跳转**：当用户路径需要跳到另一个 HTML 文件时（如小程序结果页 → 支付页），用 `window.location.href` 直接跳转同目录下对应 `.html` 文件；禁止用 alert 或 console.log 替代。
5. **保留 page-key 机制**：HTML 内部每个独立页面/组件节点仍必须有 `data-page="{page-key}"` 与 baseline 对齐；一个 HTML 文件可以包含多个 page-key 节点（因为一个模块可能涵盖多个页面）。

**禁止**：
- 左侧"全部页面导航"平铺点击
- 通过 URL hash 或 tab 直接跳任意页面（这是开发目录，不是用户路径）
- 主内容区把多个互斥状态堆在一起展示

### 2.3 HTML 内部命名规范（保留原规则）

| 元素 | 规范 | 示例 |
|---|---|---|
| 页面切换属性 | `data-page="{page-key}"` | `data-page="generator-result"` |
| 页面节点 ID | `id="page-{page-key}"` | `id="page-generator-result"` |
| page-key 格式 | kebab-case，与 baseline 完全一致 | `generator-result`、`coupon-scene-rules` |
| HTML 内路由函数 | `navigate(toPageKey)` | 同一 HTML 内的页面切换必须走路由函数，不得直接 display:none / block |

### 2.4 自检

输出后自行走查关键交互流程，确保：
- [ ] HTML 文件拆分符合「终端 + 模块」两级规则，命名正确
- [ ] 每个 HTML 有真实用户入口点（小程序首页 / 后台侧栏 + 菜单）
- [ ] 页面跳转由用户动作驱动，不是平铺导航
- [ ] 调试面板（如有）视觉弱化，不污染主路径演示
- [ ] 表单校验提示正确
- [ ] 弹窗打开/关闭正常
- [ ] 空态、错误态能通过自然路径或调试面板触发
- [ ] 分页/筛选联动正常
- [ ] 跨 HTML 跳转用 `window.location.href` 真实跳转

可执行 `scripts/validate_output.py` 辅助检查。

### 2.5 闸门 1：用户确认 HTML（强制）

所有 HTML 文件输出后提示用户确认。

**确认前禁止**：
- 生成 .pen 设计稿
- 进入技术设计或代码实现

---

## Phase 3：生成 .pen 高保真设计稿

**前置条件**：用户已确认 `ui-design.html`。

### 3.1 .pen 产出规则

基于已确认的 HTML，逐个交互页面输出高保真设计稿。

**输出形式**：统一按页面拆分多个 .pen 文件（如 `ui-design-plugin.pen`、`ui-design-app.pen`），每个 page-key 对应一个 .pen 文件。

> 不再支持单文件 `ui-design.pen` 模式，因为单文件无法通过脚本自动校验 page-key 覆盖率。

**每个页面须覆盖**：
- 主态（默认状态）
- 关键状态（根据 baseline 状态矩阵）
- 弹窗/抽屉（如有）

### 3.2 .pen 命名规范（强制）

| 规范项 | 规则 | 示例 |
|---|---|---|
| 文件名 | `ui-design-{page-key}.pen` | `ui-design-plugin.pen` |
| page-key | kebab-case，与 HTML `data-page` 完全一致 | `ad-source` |
| 画板命名 | `{页面中文名}-{状态}` | `插件管理-默认`、`插件管理-弹窗` |
| 状态集 | 默认/加载/空态/错误/禁用/弹窗/抽屉 | 固定用词，不用别名 |
| 文件位置 | `specs-mcp/{feature}/` 根目录 | 不新建子目录 |

**禁止**：
- 含糊命名（`方案1`、`最终版`、`新版页面`）
- 与 HTML page-key 不同的语义别名
- 单画板塞入多个页面

### 3.3 降级条款（可选）

若满足以下**全部条件**，经用户确认可跳过 .pen：
1. 目标页面为管理端**已有页面的局部扩展**（如增加字段、增加列）
2. 无新增独立页面或独立弹窗
3. 用户明确声明"跳过 .pen"

**执行约束**：
- 必须创建 `ui-design-notes.md` 记录字段映射与降级理由
- 前端以 `ui-design.html` 为还原基准
- 不满足任一条件时，回到完整 .pen 流程

### 3.4 闸门 2：用户确认 .pen（强制）

所有 .pen 输出后提示用户确认。

**确认前禁止**：
- 进入技术设计（design.md）
- 进入代码实现

---

## 变更回写规则

用户确认后若提出改动：

| 改动类型 | 处理方式 |
|---|---|
| 交互流程/页面结构变更 | 先更新 HTML → 再同步 .pen → 重新触发确认 |
| 仅视觉细节改动 | 同步更新 .pen 与 HTML → 重新触发确认 |
| page-key 变更 | 更新 baseline → HTML → .pen → 重新触发确认 |

> 禁止 HTML 与 .pen 出现双轨漂移（内容不一致）。

---

## 记录运行日志

将运行摘要追加到 `logs/` 目录。

文件命名：`{YYYY-MM-DD}-{feature-name}.md`

日志内容：日期、功能名、Phase 完成状态、页面数量、.pen 文件列表、是否使用降级条款。

---

## Gotchas（最高优先级阅读）

详见 `references/gotchas.md`，最关键五条：

1. **HTML 未确认就生成 .pen**：这是最常见的流程违规。.pen 以已确认的 HTML 为唯一事实来源，先出 .pen 会导致后续结构性返工。

2. **page-key 在 HTML 和 .pen 之间不一致**：HTML 用 `adsource`，.pen 用 `source`——前端实现时会错位。必须与 baseline 中锁定的 page-key 完全一致。

3. **遗漏关键状态**：只做了默认态就交付，空态/错误态留给前端自行发挥。baseline 状态矩阵中标记为 ✅ 的状态必须全部覆盖。

4. **把所有页面塞进单一 HTML**：双端一锅烩 + 多模块平铺导航 = 开发者视角目录，不是演示稿。必须按「终端 + 模块/菜单」两级拆分，文件命名含 `-H5` 区分前端。

5. **平铺式导航掩盖真实交互缺陷**：用户点左栏切页面看到的"一切都在"是假象；按真实用户路径走一遍，漏做的空态、返回栈、跨模块跳转才会暴露。原型必须模拟"用户从入口开始逐步操作"，调试用状态切换要放浮动调试面板而非主内容区。

---

## 文件索引

| 文件 | 用途 | 何时读取 |
|---|---|---|
| `config.json` | 项目配置（MCP 连接信息） | 第一步，必读 |
| `{config.design_system.*}` | 项目设计基线文件（style-guide / component-rules / page-templates） | Phase 1，必读 |
| `references/domain-rules.md` | HTML 产出规则、.pen 命名规则、状态覆盖规则 | Phase 2~3 |
| `references/gotchas.md` | 常见错误 | 开始前必读 |
| `references/examples.md` | 示例 HTML 结构与 .pen 命名 | 不确定格式时参考 |
| `references/api.md` | MCP 字段校验查询模板 | 字段口径不确定时 |
| `references/glossary.md` | 术语定义 | 遇到歧义时查阅 |
| `assets/checklist-template.md` | 输出完整性检查清单 | 每个 Phase 完成后自检 |
| `scripts/validate_output.py` | 验证 HTML 结构与 .pen 命名 | Phase 2~3，输出后执行 |
| `scripts/init_spec.sh` | 初始化输出文件 | 第一步（可选） |
| `logs/` | 历次运行记录 | 输出前查阅 |
