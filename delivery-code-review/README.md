# Delivery Code Review Skill

测试通过且人工 UI 验收后手动触发，对实现代码做结构化审查，产出 REVIEW_REPORT.md 和 recurring-issues.md。

## 快速开始

### 1. 前置条件

确保以下文件已存在且状态正确：

```
specs-mcp/<feature-name>/test-report.md   <- 测试全部通过
specs-mcp/<feature-name>/ui-acceptance.md <- 人工 UI 验收通过（如涉及前端）
```

### 2. 触发 Skill

**永远手动触发，不由编排 Skill 自动调用。**

```
"做 code review"
"审核这轮开发"
"复审已修复问题"
"代码审查"
```

### 3. 输出

```
specs-mcp/<feature-name>/REVIEW_REPORT.md
specs-mcp/recurring-issues.md（如有更新）
```

---

## 阅读顺序

首次使用本 Skill 或需要了解工作流时，按以下顺序阅读：

1. **SKILL.md** -- 完整工作流（10 步）
2. **references/gotchas.md** -- 常见审查错误，必读
3. **references/domain-rules.md** -- REVIEW_REPORT 格式与状态机规则
4. **references/examples.md** -- 示例报告片段
5. 其余文件按需查阅

---

## 目录结构

```text
delivery-code-review/
├── SKILL.md                           # 主 Skill 文件（Claude 执行入口）
├── config.json                        # 共享配置的本地副本
├── README.md                          # 本文件
├── references/
│   ├── gotchas.md                     # 常见审查错误（必读）
│   ├── domain-rules.md                # REVIEW_REPORT 格式与状态机
│   ├── examples.md                    # 示例报告片段
│   └── glossary.md                    # 术语定义
├── assets/
│   ├── review-report-template.md      # REVIEW_REPORT.md 模板
│   ├── recurring-issues-template.md   # recurring-issues.md 模板
│   └── checklist-template.md          # 审查完整性自检清单
├── scripts/
│   └── validate_output.py             # 自动完整性检查
├── logs/                              # 历次运行记录
└── outputs/                           # 备用输出目录
```

---

## 与其他 Skill 的关系

```
testing-expert
    ↓ 输出 test-report.md（全部通过）
人工 UI 验收
    ↓ 输出 ui-acceptance.md（验收通过）
delivery-code-review（本 Skill，手动触发）
    ↓ 输出 REVIEW_REPORT.md
    ↓ 如有"待修复"问题 → 开发 Skill 修复 → 回写"已修复"
    ↓ 用户再次手动触发本 Skill 进行复审
    ↓ 全部"已解决" → 进入部署阶段
```

---

## 状态机

```
待修复 ──(开发 Skill 修复)──> 已修复 ──(本 Skill 复审)──> 已解决
                                                      └──> 待修复（退回）
```

---

## 数据库查询方式

本项目统一使用 MCP 工具查询数据库，**不使用本地数据库直连**：

```
工具名：mcp__{config.database.mcp_server}__execute_sql
参数：{"query": "SELECT ..."}
```
