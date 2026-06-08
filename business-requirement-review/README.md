# Business Requirement Review Skill

需求阶段质量闸门：对 requirements.md 和 prototype.md 进行结构化评审，验证完整性、一致性与可实现性。

## 快速开始

### 1. 前置条件

确保以下文件已存在：

```
specs-mcp/<feature-name>/discovery.md       ← 探索基准
specs-mcp/<feature-name>/requirements.md    ← 功能规格
specs-mcp/<feature-name>/prototype.md       ← 页面结构
```

### 2. 触发 Skill

```
"需求评审"
"审核需求"
"review PRD"
```

### 3. 输出

```
specs-mcp/<feature-name>/business-requirement-review.md
```

结论：PASS / CONDITIONAL / BLOCKED

---

## 阅读顺序

首次使用本 Skill 或需要了解工作流时，按以下顺序阅读：

1. **SKILL.md** — 完整工作流（7 步）
2. **references/gotchas.md** — 常见评审错误，必读
3. **references/domain-rules.md** — 详细评审规则
4. **references/api.md** — MCP 字段核验查询模板
5. 其余文件按需查阅

---

## 目录结构

```text
business-requirement-review/
├── SKILL.md                    # 主 Skill 文件（Claude 执行入口）
├── config.json                 # 共享配置的本地副本
├── references/
│   ├── gotchas.md              # 常见评审错误（必读）
│   ├── domain-rules.md         # 详细评审规则
│   ├── examples.md             # 示例评审报告
│   ├── api.md                  # MCP 字段核验查询模板
│   └── glossary.md             # 术语定义
├── assets/
│   ├── review-template.md      # 评审报告模板
│   └── checklist-template.md   # 评审自检清单
├── scripts/
│   ├── check_consistency.py    # 自动一致性检查（辅助工具）
│   └── validate_review.py      # 验证评审报告格式
├── logs/                       # 历次评审记录
└── outputs/                    # 备用输出目录
```

---

## 与其他 Skill 的关系

```
solution-discovery
    ↓ 输出 discovery.md
prd-generate
    ↓ 输出 requirements.md + prototype.md
business-requirement-review（本 Skill）
    ↓ 评审通过
...（后续阶段）
```

---

## 数据库查询方式

本项目统一使用 MCP 工具查询数据库，**不使用本地数据库直连**：

```
工具名：mcp__{config.database.mcp_server}__execute_sql
参数：{"query": "SELECT ..."}
```

详见 `references/api.md`。
