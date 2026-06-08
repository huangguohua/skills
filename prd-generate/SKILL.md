---
name: prd-generate
description: discovery.md 确认后调用，或用户说"写需求文档""出 PRD""写 requirements"时调用。基于已确认的探索结论，产出结构化 requirements.md（功能规格）和 prototype.md（页面结构）。不做 UI 设计，不定义 API 字段，只明确功能边界与页面组成。
triggers:
  - 写需求文档
  - 出 PRD
  - 需求规格
  - requirements
  - prototype
  - 功能说明
---

# PRD Generate Skill

## 概述

本 Skill 将 discovery.md 中的探索结论转化为两份可执行的规格文档：

- `requirements.md`：功能需求规格，面向开发团队，描述"系统做什么"
- `prototype.md`：页面结构说明，面向 UI 设计，描述"有哪些页面、哪些组件"

**职责边界**：
- ✅ 功能需求描述（用户故事、验收标准、边界条件）
- ✅ 页面清单与组件组成（逻辑结构，无 UI 细节）
- ✅ 数据字段说明（名称、含义、约束；写"最长 50 字符"而非 DDL 类型定义如 VARCHAR(50)）
- ❌ 不定义 API 接口或数据库 DDL（属于 architect-design）
- ❌ 不做 UI 布局、颜色、字体设计（属于 prototype-generate）
- ❌ 不做技术方案选型（属于 architect-design）

**阅读顺序**：`SKILL.md`（本文件）→ `references/gotchas.md` → `references/domain-rules.md` → 其余按需

---

## 第一步：检查前置条件

**必须存在以下文件，否则停止并告知用户：**

```
{config.output_dir}/{feature-name}/discovery.md  ← 已确认状态
```

如果 discovery.md 未确认，提示：
> "当前 discovery.md 尚未确认，建议先运行 solution-discovery 并获得用户确认后再生成 PRD。"

### discovery.md 预期结构

本 Skill 需要从 discovery.md 中提取以下信息（由 `solution-discovery` Skill 产出）：

| 章节 | 提取内容 |
|---|---|
| 背景与目标 | 核心诉求、使用者 |
| 系统现状 | 相关代码、数据库表、接口 |
| 约束与风险 | 技术/数据/业务约束 |
| 方案方向 | 用户选定的方向（或待选择的多个方向） |
| 待确认项 | 需在 PRD 中继续标注为 [待确认] 的内容 |

优先读取 `../shared-config.json` 获取项目配置；同目录 `config.json` 视为同步后的本地副本。如配置未填写，参考 solution-discovery 的引导方式向用户询问（输出目录默认 `specs-mcp/`）。

---

## 第二步：理解探索结论

完整阅读 `discovery.md`，提取：

1. **核心诉求**：功能要解决什么问题
2. **使用者**：谁在用这个功能（影响权限设计）
3. **已确认的约束**：技术、数据、业务约束
4. **选定的方案方向**：如果用户已选择，以此为基准；如未选择，询问用户

> 如果用户在 discovery.md 中没有明确选择方向，先问用户选哪个方向，再开始写 PRD。

---

## 第三步：编写 requirements.html 与 requirements.md（含字段验证）

**同时输出两个文件**，内容完全一致，格式不同：
- `requirements.html`：使用 `assets/spec-template.html` 模板，可在浏览器直接打开
- `requirements.md`：使用 `assets/spec-template.md` 模板，章节结构与 HTML 完全对应

### 写作基调：面向产品与业务，而非开发

**这份文档的第一读者是产品经理、业务负责人、运营，不是后端工程师。** 遵守以下规则：

| ❌ 不该出现在正文中 | ✅ 正确写法 |
|---|---|
| `coupon_user.source='OA_FOLLOW'` | 来源标记为「关注服务号」 |
| `DB/schema.sql:17–36` | （仅在字段核验附录里引用，正文删除） |
| `P99 ≤ 200ms`（技术性能指标） | 用户在正常网络下无感知延迟 |
| 幂等 key = `(user_id, qrcode_id)` | 每张二维码对每个用户只弹出一次 |
| `trade_status=SUCCESS` | 支付成功后 |
| `eligible=true` / `reason=OUT_OF_STOCK` | 有可领的券 / 券已发完 |

**正文写作要求：**
1. **业务语言**：用"用户点击后看到…""系统自动…""运营可以…"描述，不出现接口路径、字段名、枚举值代码。
2. **用户视角**：功能清单每条用"用户可以…"句式；业务规则从用户感受/业务结果出发描述。
3. **状态流转**：用中文描述状态名（"已领取·未使用"），不用枚举值（`AVAILABLE`）。
4. **数字用业务单位**：金额写"20 元"不写"2000 分"；时长写"7 天"不写"604800 秒"。
5. **技术细节隔离**：数据库字段名、枚举值、DDL 来源只允许出现在「数据字段规范」表格和「字段核验附录」中，正文业务描述里一律不出现。
6. **待确认项**：用 callout-warn（HTML）或 `> ⚠️`（MD）标注，注明确认截止日期。

### 字段验证规则（仅影响「数据字段规范」表格内容）

- 现有字段：通过 MCP 工具 `mcp__{config.database.mcp_server}__execute_sql` 查询验证字段名、枚举值、约束，必须使用数据库中的实际名称
- 新增字段：不能伪装成已存在字段，必须显式标注 `[新增字段][待设计]`
- 未能确认的字段标注 `[待确认]`，不能写假值

查询模板见 `references/api.md`。

### 结构要点（8 章，与模板一一对应）

1. **S1 项目背景与目标**：背景一段话（面向非技术读者）+ 目标对比表（现状 vs 目标 vs 衡量指标）
2. **S2 用户与角色**：角色表（角色名、描述、核心诉求、关键操作）
3. **S3 功能清单与优先级**：功能 ID + 模块 + 功能点 + 优先级 badge + 需求类型 badge
4. **S4 功能需求（用户故事）**：每个角色 2~4 张故事卡，格式"作为…我希望…以便…" + 验收标准
5. **S5 功能详细描述**：每个功能块含"业务规则 + 交互说明 + 边界与异常 + 数据字段规范"，其中业务规则和交互说明用业务语言，字段规范表可含字段名
6. **S6 非功能需求**：性能、安全、可扩展性等，用业务可感知的指标表述
7. **S7 风险与依赖**：风险表 + 待确认事项
8. **S8 版本变更记录**：版本号、日期、变更人、变更内容

> 详细规则见 `references/domain-rules.md`

---

## 第四步：编写 prototype.md

使用 `assets/prototype-template.md` 作为模板：

### 结构要点

每个页面描述：
- 页面名称与路径（预估）
- 是否新增或改造现有页面
- 包含哪些区域/区块（不是组件代码，是逻辑区域）
- 每个区域的核心功能
- 涉及哪些操作（按钮、表单、弹窗）
- 数据来源（展示什么数据）

> **禁止**：颜色、字体、间距、像素——这些是 prototype-generate 的职责

---

## 第五步：一致性自检

输出前执行 `scripts/validate_output.py`，检查：
- requirements.md 与 prototype.md 的页面范围是否一致
- 功能清单中的每条功能是否在 prototype.md 中有对应页面/区域
- 所有数据字段是否有来源说明

同时对照 `assets/checklist-template.md` 做人工自检。

---

## 第六步：输出文件

输出路径：
```
{config.output_dir}/{feature-name}/requirements.html   ← HTML 格式，参照 spec-template.html
{config.output_dir}/{feature-name}/requirements.md     ← Markdown 格式，参照 spec-template.md，章节结构与 HTML 完全对应
{config.output_dir}/{feature-name}/prototype.md
```

> HTML 与 MD 内容完全一致，只是呈现格式不同。先写好其中一份，再转换另一份，避免内容出现分歧。

输出完成后：
1. 提示用户确认两份文档
2. 确认后方可进入 `business-requirement-review`

---

## 第七步：记录运行日志

将运行摘要追加到 `logs/` 目录，格式参考 `logs/README.md`。

文件命名：`{YYYY-MM-DD}-{feature-name}.md`

日志内容：日期、功能名、字段核验摘要（核验/通过/待确认数量）、主要决策、输出文件路径、状态。

---

## Gotchas（最高优先级阅读）

详见 `references/gotchas.md`，最关键四条：

1. **requirements 不是 discovery.md 的复述**：Discovery 描述现状，PRD 描述目标。不要把探索结论直接粘贴进来。

2. **正文必须用业务语言，技术细节隔离**：接口路径、字段名、枚举值代码只允许出现在「数据字段规范」表格和「字段核验附录」中。正文写"券已发完"，不写 `reason=OUT_OF_STOCK`；写"每张二维码只弹一次"，不写"幂等 key = (user_id, qrcode_id)"。

3. **prototype.md 描述逻辑结构，不描述视觉**：写"筛选区"而非"左侧带蓝色边框的筛选面板"。

4. **字段枚举值必须查数据库，不能凭记忆写**：哪怕你 95% 确定，也要查。

---

## 文件索引

| 文件 | 用途 | 何时读取 |
|---|---|---|
| `config.json` | 项目配置（MCP 连接信息） | 第一步，必读 |
| `references/domain-rules.md` | 需求写作规则与页面结构规则 | 第三、四步 |
| `references/gotchas.md` | 常见错误 | 开始前必读 |
| `references/examples.md` | 示例文档片段 | 不确定格式时参考 |
| `references/api.md` | MCP 字段验证查询模板 | 第三步，编写字段时 |
| `references/glossary.md` | 术语定义 | 遇到歧义时查阅 |
| `assets/spec-template.html` | requirements.html 模板（HTML 风格） | 第三步 |
| `assets/spec-template.md` | requirements.md 模板（Markdown，章节与 HTML 完全对应） | 第三步 |
| `assets/prototype-template.md` | prototype.md 模板 | 第四步 |
| `assets/checklist-template.md` | 输出自检清单 | 第五步 |
| `scripts/validate_output.py` | 自动完整性检查 | 第五步 |
| `scripts/init_spec.sh` | 初始化输出目录和文件 | 第一步（可选） |
| `logs/` | 历次运行记录 | 输出前查阅 |
