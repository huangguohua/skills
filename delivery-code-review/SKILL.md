---
name: delivery-code-review
description: 测试通过且人工 UI 验收后手动触发。对实现代码做结构化审查，读取项目编码规范作为审查标准，产出 REVIEW_REPORT.md 和 recurring-issues.md。永远手动触发，不由编排自动调用。
triggers:
  - 做 code review
  - 审核这轮开发
  - 复审已修复问题
  - 代码审查
manual_only: true
---

# Delivery Code Review Skill

## 概述

本 Skill 在测试通过且人工 UI 验收完成后**手动触发**，对本轮实现代码进行结构化审查。

**核心输出**：
- `REVIEW_REPORT.md`：本轮审查报告，包含每个问题的位置、描述、修复建议、所有权归属
- `recurring-issues.md`：长期知识库，出现 2 次及以上的问题被提升至此

**强制规则**：
- 本 Skill **永远手动触发**，不由编排 Skill 自动调用
- REVIEW_REPORT.md 状态机：`待修复` -> `已修复`（由开发 Skill 回写） -> `已解决` / 退回`待修复`（由本 Skill 判定）
- 每个问题必须包含：位置（location）、描述（description）、修复建议（fix suggestion）、所有权归属（ownership：后端/前端/结构性）

**阅读顺序**：`SKILL.md`（本文件） -> `references/gotchas.md` -> `references/domain-rules.md` -> 其余按需

---

## 第一步：Pre-review Hook — 检查前置条件

**必须满足以下条件，否则停止并告知用户：**

1. **test-report.md 存在且通过**：
   ```
   {config.output_dir}/{feature-name}/test-report.md
   ```
   检查 test-report.md 中是否包含"全部通过"或"PASS"等结论性状态。如不存在或未通过：
   > "测试报告不存在或未全部通过，请先完成测试阶段再触发代码审查。"

2. **ui-acceptance.md 存在**（如涉及前端）：
   如果本轮开发涉及前端页面，检查人工 UI 验收记录是否存在。

3. **读取项目编码规范**：
   从 `config.development.coding_standards_path` 读取编码规范作为审查标准。如路径未配置，警告用户并使用通用最佳实践。

优先读取 `../shared-config.json` 获取项目配置；同目录 `config.json` 视为同步后的本地副本。

---

## 第二步：收集变更范围

1. 识别本轮开发涉及的所有文件变更（通过 tasks.md、CHANGELOG.md 或 git diff）
2. 按模块分类：后端、前端、配置、数据库脚本
3. 列出变更文件清单，作为审查范围

---

## 第三步：读取审查标准

从以下来源加载审查标准（优先级由高到低）：

1. `config.development.coding_standards_path` — 项目编码规范
2. `config.development.backend_gotchas_path` — 后端常见问题
3. `config.development.frontend_gotchas_path` — 前端常见问题
4. `config.development.project_structure_path` — 项目结构规范

如果某路径文件不存在，跳过并记录警告，不中断审查。

---

## 第四步：逐文件 / 逐模块审查

对每个变更文件进行结构化审查，检查维度包括但不限于：

### 通用维度
- 命名规范（变量、函数、类、文件）
- 代码重复（是否有可抽取的公共逻辑）
- 错误处理（异常捕获、边界检查、空值防护）
- 安全性（SQL 注入、XSS、权限校验）
- 性能（N+1 查询、不必要的循环、大数据量处理）

### 后端维度
- 分层是否清晰（Controller / Service / Repository）
- 事务边界是否正确
- API 接口是否符合 RESTful 规范
- 数据库操作是否使用参数化查询

### 前端维度
- 组件拆分是否合理
- 状态管理是否清晰
- 是否遵循既有项目的 UI 框架用法
- 国际化 / 本地化处理

### 结构性维度
- 模块间依赖是否合理
- 配置是否外部化
- 是否有硬编码的魔法值

---

## 第五步：产出 REVIEW_REPORT.md

使用 `assets/review-report-template.md` 作为模板，输出到：

```
{config.output_dir}/{feature-name}/REVIEW_REPORT.md
```

### 问题格式（每个问题必须包含）

```markdown
### Issue-{N}: {简要标题}

- **位置**：`文件路径:行号` 或 `文件路径#方法名`
- **严重程度**：Critical / Major / Minor / Suggestion
- **所有权**：后端 / 前端 / 结构性
- **描述**：具体问题是什么，为什么是问题
- **建议修复**：建议如何修复（给出具体方向或代码片段）
- **状态**：待修复
```

### 状态机规则

| 当前状态 | 操作者 | 可转移到 |
|---|---|---|
| 待修复 | 开发 Skill（后端/前端） | 已修复 |
| 已修复 | 本 Skill（复审时） | 已解决 / 待修复（退回） |
| 已解决 | — | 终态 |

> 本 Skill 仅负责 `已修复 -> 已解决` 或 `已修复 -> 待修复（退回）` 的状态变更。
> 开发 Skill 负责 `待修复 -> 已修复` 的状态回写。

---

## 第六步：维护 recurring-issues.md

审查完成后，扫描历史 REVIEW_REPORT 和当前报告：

1. 如果某类问题（按描述相似度判断）出现 **2 次及以上**，提升到 `recurring-issues.md`
2. recurring-issues.md 路径：
   ```
   {config.output_dir}/recurring-issues.md
   ```
3. 使用 `assets/recurring-issues-template.md` 作为模板
4. 每条记录包含：问题模式、出现次数、涉及功能、建议的团队级改进措施

---

## 第七步：复审流程（Re-review）

当开发 Skill 将问题状态回写为"已修复"后，用户手动触发本 Skill 进行复审：

1. 读取 REVIEW_REPORT.md 中状态为"已修复"的问题
2. 逐一检查修复代码是否**真正解决了问题**（不只是改了代码，而是问题确实不再存在）
3. 判定结果：
   - 修复有效 -> 状态改为 `已解决`
   - 修复无效或引入新问题 -> 状态退回 `待修复`，补充退回理由
4. **追加**新的 Re-review 轮次记录到 REVIEW_REPORT.md 末尾（不覆盖原有内容）

---

## 第八步：完整性自检

输出前执行 `scripts/validate_output.py`，检查：
- REVIEW_REPORT.md 是否包含必要章节
- 每个问题是否都有所有权归属标签
- 问题状态是否为合法值

同时对照 `assets/checklist-template.md` 做审查完整性自检。

---

## 第九步：输出文件

输出路径：
```
{config.output_dir}/{feature-name}/REVIEW_REPORT.md
{config.output_dir}/recurring-issues.md（如有更新）
```

输出完成后：
1. 汇总审查结论：Critical / Major / Minor / Suggestion 各多少个
2. 如有 Critical 或 Major 问题，提示用户需要开发 Skill 修复后再复审
3. 如全部为 Minor / Suggestion 或无问题，提示可进入部署阶段

---

## 第十步：记录运行日志

将运行摘要追加到 `logs/` 目录，格式参考 `logs/README.md`。

文件命名：`{YYYY-MM-DD}-{feature-name}.md`

日志内容：日期、功能名、审查轮次（首审/复审第 N 轮）、问题统计、状态变更摘要、输出文件路径。

---

## Gotchas（最高优先级阅读）

详见 `references/gotchas.md`，最关键三条：

1. **永远手动触发**：本 Skill 不由编排 Skill 自动调用，必须由用户显式触发。

2. **不要给模糊反馈**：每个问题必须有具体位置、具体描述、具体修复建议。"需要改进"不是有效反馈。

3. **复审时必须验证修复有效性**：不能只看代码改了就标"已解决"，要确认问题确实不再存在。

---

## 文件索引

| 文件 | 用途 | 何时读取 |
|---|---|---|
| `config.json` | 项目配置（编码规范路径等） | 第一步，必读 |
| `references/gotchas.md` | 常见审查错误 | 开始前必读 |
| `references/domain-rules.md` | REVIEW_REPORT 格式与状态机规则 | 第五步 |
| `references/examples.md` | 示例 REVIEW_REPORT 片段 | 不确定格式时参考 |
| `references/glossary.md` | 术语定义 | 遇到歧义时查阅 |
| `assets/review-report-template.md` | REVIEW_REPORT.md 模板 | 第五步 |
| `assets/recurring-issues-template.md` | recurring-issues.md 模板 | 第六步 |
| `assets/checklist-template.md` | 审查完整性自检清单 | 第八步 |
| `scripts/validate_output.py` | 自动完整性检查 | 第八步 |
| `logs/` | 历次运行记录 | 输出前查阅 |
