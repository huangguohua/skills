# PRD Generate Skill

基于已确认的 discovery.md，产出结构化 requirements.md（功能规格）和 prototype.md（页面结构）。

## 快速开始

### 1. 前置条件

确保以下文件已存在且已确认：

```
specs-mcp/<feature-name>/discovery.md  ← 由 solution-discovery 产出
```

### 2. 触发 Skill

```
"写需求文档"
"出 PRD"
"开始写 requirements"
```

### 3. 输出

```
specs-mcp/<feature-name>/requirements.md
specs-mcp/<feature-name>/prototype.md
```

---

## 阅读顺序

首次使用本 Skill 或需要了解工作流时，按以下顺序阅读：

1. **SKILL.md** — 完整工作流（7 步）
2. **references/gotchas.md** — 常见错误，必读
3. **references/domain-rules.md** — 需求写作规则与页面结构规则
4. **references/api.md** — MCP 字段验证查询模板
5. 其余文件按需查阅

---

## 目录结构

```text
prd-generate/
├── SKILL.md                    # 主 Skill 文件（Claude 执行入口）
├── config.json                 # 共享配置的本地副本
├── references/
│   ├── gotchas.md              # 常见错误（必读）
│   ├── domain-rules.md         # 需求写作规则
│   ├── examples.md             # 示例文档片段
│   ├── api.md                  # MCP 字段验证查询模板
│   └── glossary.md             # 术语定义
├── assets/
│   ├── spec-template.md        # requirements.md 模板
│   ├── prototype-template.md   # prototype.md 模板
│   └── checklist-template.md   # 输出自检清单
├── scripts/
│   ├── validate_output.py      # 自动完整性检查
│   └── init_spec.sh            # 初始化输出目录和文件
├── logs/                       # 历次运行记录
└── outputs/                    # 备用输出目录
```

---

## 与其他 Skill 的关系

```
solution-discovery
    ↓ 输出 discovery.md（本 Skill 的输入）
prd-generate（本 Skill）
    ↓ 输出 requirements.md + prototype.md
business-requirement-review
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
