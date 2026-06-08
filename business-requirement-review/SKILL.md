---
name: business-requirement-review
description: requirements.md 和 prototype.md 产出后调用，或用户说"需求评审""审核需求""review PRD"时调用。对需求文档进行结构化质量评审，验证完整性、一致性与可实现性，输出 business-requirement-review.md。评审通过后方可进入 UI 设计阶段。
triggers:
  - 需求评审
  - 审核需求
  - review PRD
  - 需求检查
  - 需求质量
---

# Business Requirement Review Skill

## 概述

本 Skill 是需求阶段的**质量闸门**，对 requirements.md 和 prototype.md 进行独立评审。

评审从三个维度展开：
1. **完整性**：需求是否覆盖所有场景（包括边界和异常）
2. **一致性**：requirements.md 与 prototype.md 之间、与 discovery.md 之间是否互相对齐
3. **可实现性**：需求描述是否足够清晰，开发可直接执行

**输出结论**：
- `PASS`：无问题，可进入下一阶段
- `CONDITIONAL`：仅有低优先级问题，或中优先级问题但不影响核心逻辑，可附条件通过
- `BLOCKED`：存在高优先级问题，或影响核心逻辑的中优先级问题，必须修复后重新评审

**阅读顺序**：`SKILL.md`（本文件）→ `references/gotchas.md` → `references/domain-rules.md` → 其余按需

---

> **最重要的规则（G1）**：**不得因为 discovery.md 已查过字段就跳过重新核验。** PRD 写作过程中常引入细微偏差（字段名大小写、枚举值增减），评审阶段必须独立执行 MCP 查询重新验证。

---

## 第一步：收集评审对象

读取以下文件（必须全部存在）：

```
{feature-dir}/discovery.md       ← 探索基准
{feature-dir}/requirements.md    ← 功能规格
{feature-dir}/prototype.md       ← 页面结构
```

如有任何文件缺失，停止并提示用户补充。

优先读取 `../shared-config.json` 获取共享项目配置；同目录 `config.json` 视为同步后的本地副本。数据库查询统一通过 MCP 工具 `mcp__{config.database.mcp_server}__execute_sql` 执行。

---

## 第二步：独立阅读，不带预设

按以下顺序阅读，**每份文档独立评估，不互相参照**：

1. 先读 discovery.md — 记录核心诉求和已确认的约束
2. 再读 requirements.md — 记录功能清单、业务规则、字段说明
3. 最后读 prototype.md — 记录页面清单和组件组成

独立阅读完成后，再做交叉比对（第四步）。

---

## 第三步：数据字段核验（MCP 查询）

requirements.md 中列出的所有数据字段，按"现有字段 / 新增字段"两类重新核验：

- 现有字段：通过 MCP 工具 `mcp__{config.database.mcp_server}__execute_sql` 核验字段是否存在（名称、大小写）、枚举值是否一致、必填/非空约束是否一致
- 新增字段：检查是否显式标注 `[新增字段]` 或 `[待设计]`，并确认没有被误写成"数据库已存在"

**即使 discovery.md 已经查过，现有字段也必须重新验证。** PRD 阶段的字段描述可能与探索阶段产生偏差。

核验查询模板见 `references/api.md`。

---

## 第四步：按维度评审

详细规则见 `references/domain-rules.md`，核心检查项如下：

可选择先运行 `scripts/check_consistency.py` 作为辅助参考（注意：该脚本为辅助工具，输出仅供参考，不作为自动通过/不通过的依据，人工评审不可省略）。

### 4.1 完整性检查

- [ ] 每个"用户可以..."功能是否有对应的验收标准？
- [ ] 空状态是否明确定义？（列表无数据时显示什么）
- [ ] 错误状态是否覆盖？（请求失败、网络异常、权限不足）
- [ ] 权限矩阵是否覆盖所有角色 × 操作组合？
- [ ] 状态流转图是否完整？（如果有状态机）
- [ ] "不在范围内"是否明确列出？

### 4.2 一致性检查

- [ ] requirements.md 中每个功能，在 prototype.md 中是否有对应页面/区域？
- [ ] prototype.md 中每个页面，在 requirements.md 中是否有功能支撑？
- [ ] 数据字段在两份文档中的名称是否一致？
- [ ] discovery.md 确认的约束，是否在 requirements.md 中体现？
- [ ] discovery.md 中排除的内容，是否仍然出现在 requirements.md 中？

### 4.3 可实现性检查

- [ ] 业务规则是否可以被开发精确实现？（没有"尽量""合理"等模糊词）
- [ ] 计算逻辑是否有明确公式？
- [ ] 状态流转条件是否精确？（"当 X 满足 Y 时，触发 Z"）
- [ ] 接口数据来源是否说清楚？（展示哪张表的哪个字段）

---

## 第五步：输出评审报告

使用 `assets/review-template.md` 输出到：

```
{feature-dir}/business-requirement-review.md
```

每个问题必须包含：
- **问题描述**：具体说明哪里有问题
- **优先级**：高（阻塞）/ 中（建议修复）/ 低（可忽略）
- **修复建议**：可执行的具体改法

> 不允许写"需要改进"、"描述不够清晰"等无法执行的反馈。

---

## 第六步：给出结论

根据问题优先级，给出整体结论：

| 结论 | 条件 |
|---|---|
| `PASS` | 无任何问题 |
| `CONDITIONAL` | 仅有低优先级问题，或中优先级问题但不影响核心逻辑 |
| `BLOCKED` | 存在高优先级问题，或影响核心逻辑的中优先级问题 |

**BLOCKED 时**，明确告知用户：需要修复哪些问题 → 在 requirements.md / prototype.md 中修正 → 再次触发本 Skill 评审。

---

## 第七步：记录运行日志

将评审摘要追加到 `logs/` 目录，格式参考 `logs/README.md`。

文件命名：`{YYYY-MM-DD}-{feature-name}-round{N}.md`

日志内容：日期、功能名、评审轮次、结论、问题摘要（高/中/低数量）、字段核验统计、输出文件路径。

---

## Gotchas（最高优先级阅读）

详见 `references/gotchas.md`，最关键三条：

1. **不能因为 discovery.md 查过就跳过字段核验**：PRD 写作过程中常常引入细微偏差，必须重新查。

2. **评审反馈必须可执行**：每条问题都要写"建议改为：..."，不能只写"此处不清晰"。

3. **prototype.md 缺页不是低优先级问题**：如果 requirements.md 有功能但 prototype.md 没有对应页面，这是 BLOCKED 级别的一致性问题。

---

## 文件索引

| 文件 | 用途 | 何时读取 |
|---|---|---|
| `config.json` | 项目配置（MCP 连接信息） | 第一步，必读 |
| `references/domain-rules.md` | 详细评审规则与检查清单 | 第四步 |
| `references/gotchas.md` | 常见评审错误 | 开始前必读 |
| `references/examples.md` | 示例评审报告 | 不确定格式时参考 |
| `references/api.md` | MCP 字段核验查询模板 | 第三步 |
| `assets/review-template.md` | 评审报告模板 | 第五步 |
| `assets/checklist-template.md` | 评审维度完整性自检 | 第四步前 |
| `scripts/check_consistency.py` | 自动一致性检查（辅助工具，不替代人工评审） | 第四步，辅助参考 |
| `scripts/validate_review.py` | 验证评审报告格式 | 第五步后 |
| `logs/` | 历次评审记录 | 输出前查阅 |
