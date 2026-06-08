# Architect Design Skill

基于已确认的需求文档与 UI 设计，进行技术方案设计、数据库设计与研发任务拆解。

## 快速开始

### 1. 配置项目信息

优先编辑共享配置 `../shared-config.json`（已预填 AD 项目默认值）：

```json
{
  "project": { "name": "AD海外广告系统" },
  "database": {
    "type": "mcp",
    "mcp_server": "{从 shared-config.json 同步}",
    "database_name": "{从 shared-config.json 同步}"
  },
  "codebase": {
    "backend_path": "backend",
    "frontend_path": "frontend"
  }
}
```

修改后运行 `python ../sync_shared_config.py` 同步到各 Skill 的本地 `config.json`。

### 2. 前置条件

本 Skill 要求以下文件已存在且已用户确认：

- `specs-mcp/<feature>/requirements.md`（必须）
- `specs-mcp/<feature>/prototype.md`（必须）
- `specs-mcp/<feature>/ui-design.*`（推荐）

### 3. 触发 Skill

直接描述你的设计需求：

> "做技术设计"
> "输出 design.md"
> "设计接口和库表"
> "拆研发任务"

### 4. 输出

设计完成后输出以下文件：

```
specs-mcp/<feature-name>/
├── design.md
├── tasks.md
└── DB/
    ├── schema.sql
    ├── test-data.sql
    ├── er-diagram.md
    └── er-diagram-text.md
```

---

## 阅读顺序

首次使用本 Skill 或需要了解工作流时，按以下顺序阅读：

1. **SKILL.md** -- 完整工作流（7 步、3 阶段、2 闸门）
2. **references/gotchas.md** -- 常见错误，必读
3. **references/domain-rules.md** -- design.md / tasks.md / DB 交付物格式规范
4. **references/api.md** -- MCP 查询模板
5. 其余文件按需查阅

---

## 目录结构

```text
skills/
├── shared-config.json          # 多 Skill 共享配置源（已预填 AD 项目值）
├── sync_shared_config.py       # 同步共享配置到各 Skill
└── architect-design/
    ├── SKILL.md                # 主 Skill 文件（Claude 执行入口）
    ├── config.json             # 共享配置的本地副本
    ├── README.md               # 本文件
    ├── references/
    │   ├── gotchas.md          # 常见错误（必读）
    │   ├── domain-rules.md     # 输出格式规范
    │   ├── examples.md         # 示例 design.md 和 tasks.md 片段
    │   ├── api.md              # MCP 查询模式速查
    │   └── glossary.md         # 术语定义
    ├── assets/
    │   ├── design-template.md  # design.md 输出模板
    │   ├── tasks-template.md   # tasks.md 输出模板
    │   └── checklist-template.md # 输出自检清单
    ├── scripts/
    │   ├── validate_output.py  # 验证输出完整性
    │   └── init_spec.sh        # 初始化输出目录
    └── logs/                   # 历次运行记录
```

---

## 与其他 Skill 的关系

```
prd-generate
    ↓ 输出 requirements.md + prototype.md
prototype-generate（可选）
    ↓ 输出 prototype.md
ui-design-baseline（可选）
    ↓ 输出 ui-design.*
architect-design（本 Skill）
    ↓ 输出 design.md + tasks.md + DB/*
development-orchestrator（下一步）
    ↓ 编排前后端开发
backend-development / frontend-development
    ↓ 代码实现
testing-expert
    ↓ 测试验收
delivery-code-review
    ↓ 代码审查
project-release-deploy
    ↓ 部署发布
```

---

## 数据库查询方式

本项目统一使用 MCP 工具查询数据库，**不使用本地数据库直连**：

```
工具名：mcp__{config.database.mcp_server}__execute_sql
参数：{"query": "SELECT ..."}
```

详见 `references/api.md`。
