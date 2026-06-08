# Technical Design Review Skill

技术设计阶段质量闸门：对 architect-design 输出的 design.md、tasks.md 和 DB 交付物进行多维度独立评审。

## 快速开始

### 1. 前置条件

确保以下文件已存在：

```
specs-mcp/<feature-name>/requirements.md           ← 必须存在（需求基准）
specs-mcp/<feature-name>/prototype.md              ← 必须存在（页面基准）
specs-mcp/<feature-name>/design.md                 ← 必须存在（评审主对象）
specs-mcp/<feature-name>/tasks.md                  ← 必须存在（评审主对象）
specs-mcp/<feature-name>/DB/schema.sql             ← 条件必须（如涉及数据库变更）
specs-mcp/<feature-name>/ui-design-baseline.md     ← 条件必须（如涉及前端页面）
specs-mcp/<feature-name>/ui-design-{page-key}.pen  ← 条件必须（如涉及前端页面）
```

> **纯后端功能**（无前端页面）不要求 .pen 和 ui-design-baseline.md。
> **涉及前端页面时**，.pen 文件全量映射检查是最高优先级检查项。

### 2. 触发 Skill

```
"评审技术设计"
"审核架构方案"
"review design"
"技术方案评审"
```

### 3. 输出

```
specs-mcp/<feature-name>/technical-design-review.md
```

结论：PASS / CONDITIONAL / BLOCKED

---

## 六个评审维度

1. **架构合理性** — 模块边界、耦合度、一致性、可扩展性
2. **API 契约质量** — RESTful 规范、与现有接口一致性、完整性
3. **数据库设计质量** — 规范化、索引策略、迁移安全性
4. **需求-设计对齐性** ⚠️ **最高权重** — 需求全覆盖、.pen 映射、无范围蔓延
5. **任务拆解可执行性** — 粒度合理、依赖正确、验收标准明确
6. **安全性与性能** — 鉴权设计、注入防护、N+1 查询

---

## 阅读顺序

1. **SKILL.md** — 完整工作流（7 步）
2. **references/gotchas.md** — 常见评审错误，必读
3. **references/domain-rules.md** — 详细评审规则
4. **references/api.md** — MCP 数据库查询模板
5. 其余文件按需查阅

---

## 目录结构

```text
technical-design-review/
├── SKILL.md                    # 主 Skill 文件（Claude 执行入口）
├── config.json                 # 共享配置的本地副本
├── references/
│   ├── gotchas.md              # 常见评审错误（必读）
│   ├── domain-rules.md         # 详细评审规则
│   ├── examples.md             # 示例评审报告
│   ├── api.md                  # MCP 查询模板
│   └── glossary.md             # 术语定义
├── assets/
│   ├── review-template.md      # 评审报告模板
│   └── checklist-template.md   # 评审自检清单
├── scripts/
│   └── validate_review.py      # 验证评审报告格式
├── logs/                       # 历次评审记录
└── outputs/                    # 备用输出目录
```

---

## 与其他 Skill 的关系

```
architect-design
    ↓ 输出 design.md + tasks.md + DB/
technical-design-review（本 Skill）
    ↓ 评审通过
development-orchestrator
    ↓ 编排前后端开发
```

---

## 数据库查询方式

本项目统一使用 MCP 工具查询数据库，**不使用本地数据库直连**：

```
工具名：mcp__{config.database.mcp_server}__execute_sql
参数：{"query": "SELECT ..."}
```

详见 `references/api.md`。
