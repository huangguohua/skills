# Frontend Development Skill

development-orchestrator 分派后调用，按 design.md 与 ui-design.html/.pen 实现前端页面，遵循设计基线和前端 gotchas，支持修复 review 问题并回写状态。

## 快速开始

### 1. 配置项目信息

优先编辑共享配置 `../shared-config.json`（已预填 AD 项目默认值）：

```json
{
  "project": { "name": "AD海外广告系统" },
  "codebase": {
    "frontend_path": "frontend",
    "frontend_framework": "Vue2 + ElementUI"
  },
  "design_system": {
    "style_guide_path": "doc/design-system/style-guide.md",
    "component_rules_path": "doc/design-system/component-rules.md"
  }
}
```

修改后运行 `python ../sync_shared_config.py` 同步到各 Skill 的本地 `config.json`。

### 2. 触发 Skill

由 development-orchestrator 自动分派，或直接描述：

> "开发前端页面"
> "还原设计稿"
> "写广告列表页面"
> "修复前端 review 问题"

### 3. 输出

- 前端代码文件（组件、路由、API 调用、样式）
- `specs-mcp/<feature>/CHANGELOG.md` 前端变更条目
- `specs-mcp/<feature>/REVIEW_REPORT.md` 状态更新（修复模式时）

---

## 阅读顺序

首次使用本 Skill 或需要了解工作流时，按以下顺序阅读：

1. **SKILL.md** — 完整工作流（9 步）
2. **references/gotchas.md** — 前端常见错误，必读
3. **references/domain-rules.md** — 页面实现规则、设计还原规则
4. **references/examples.md** — 示例页面实现模式
5. 其余文件按需查阅

---

## 目录结构

```text
skills/
├── shared-config.json              # 多 Skill 共享配置源
├── sync_shared_config.py           # 同步共享配置到各 Skill
└── frontend-development/
    ├── SKILL.md                    # 主 Skill 文件（Claude 执行入口）
    ├── config.json                 # 共享配置的本地副本
    ├── README.md                   # 本文件
    ├── references/
    │   ├── gotchas.md              # 前端常见错误（必读）
    │   ├── domain-rules.md         # 页面实现与设计还原规则
    │   ├── examples.md             # 示例页面实现模式
    │   └── glossary.md             # 前端术语定义
    ├── assets/
    │   └── checklist-template.md   # 页面实现检查清单
    ├── logs/                       # 历次运行记录
    ├── outputs/                    # 备用输出目录
    └── scripts/                    # 辅助脚本（预留）
```

---

## 与其他 Skill 的关系

```
ui-design-baseline
    ↓ 输出 ui-design.html / ui-design.pen
architect-design
    ↓ 输出 design.md + tasks.md
development-orchestrator
    ↓ 分派前端任务
frontend-development（本 Skill）
    ↓ 输出前端代码 + CHANGELOG
testing-expert（下一步）
    ↓ 接口与页面测试
delivery-code-review
    ↓ 代码审查（手动触发）
```

---

## 输入依赖

本 Skill 启动前，以下文件必须已存在且通过确认：

| 文件 | 来源 Skill |
|---|---|
| `specs-mcp/<feature>/requirements.md` | prd-generate |
| `specs-mcp/<feature>/design.md` | architect-design |
| `specs-mcp/<feature>/tasks.md` | architect-design |
| `specs-mcp/<feature>/ui-design.html` | ui-design-baseline |
| `specs-mcp/<feature>/ui-design.pen`（可选） | ui-design-baseline |
