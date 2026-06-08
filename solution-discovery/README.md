# Solution Discovery Skill

系统性探索现有系统现状，为新功能需求提供事实依据与方案方向。

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

### 2. 触发 Skill

直接描述你的功能想法：

> "我想给用户加一个标签功能"
> "需要一个订单导出功能"
> "调研一下现有的通知系统"

### 3. 输出

探索完成后输出 `specs-mcp/<feature-name>/discovery.md`

---

## 阅读顺序

首次使用本 Skill 或需要了解工作流时，按以下顺序阅读：

1. **SKILL.md** — 完整工作流（7 步）
2. **references/gotchas.md** — 常见错误，必读
3. **references/domain-rules.md** — 探索规则与约束清单
4. **references/api.md** — MCP 查询模板
5. 其余文件按需查阅

---

## 目录结构

```text
skills/
├── shared-config.json          # 3 个 Skill 的共享配置源（已预填 AD 项目值）
├── sync_shared_config.py       # 同步共享配置到各 Skill
└── solution-discovery/
    ├── SKILL.md                # 主 Skill 文件（Claude 执行入口）
    ├── config.json             # 共享配置的本地副本
    ├── references/
    │   ├── gotchas.md          # 常见错误（必读）
    │   ├── domain-rules.md     # 探索规则与约束识别清单
    │   ├── examples.md         # 示例 discovery 输出
    │   ├── api.md              # MCP 查询模式速查
    │   └── glossary.md         # 术语定义
    ├── assets/
    │   ├── spec-template.md    # discovery.md 输出模板
    │   └── checklist-template.md
    ├── scripts/
    │   ├── collect_context.py  # 收集代码库上下文
    │   ├── check_schema.py     # 生成 DB Schema 查询 SQL（通过 MCP 执行）
    │   ├── validate_output.py  # 验证 discovery.md 完整性
    │   └── init_spec.sh        # 初始化输出目录
    ├── logs/                   # 历次运行记录
    └── outputs/                # 备用输出目录
```

---

## 与其他 Skill 的关系

```
solution-discovery（本 Skill）
    ↓ 输出 discovery.md
prd-generate（下一步）
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
