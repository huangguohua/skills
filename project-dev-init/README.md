# Project Dev Init Skill

为项目初始化工程规范文档：编码规范、项目结构、前后端 gotchas、测试 gotchas、部署手册。

## 快速开始

### 1. 前置条件

- 项目有后端和/或前端代码
- 或：新项目需要从零建立开发规范

### 2. 触发 Skill

```
"初始化开发规范"
"生成项目规范"
"提取编码规范"
```

### 3. 输出

```
doc/development/coding-standards.md     ← 编码规范
doc/development/project-structure.md    ← 项目结构
doc/development/backend-gotchas.md      ← 后端常见坑
doc/development/frontend-gotchas.md     ← 前端常见坑
doc/testing/test-gotchas.md             ← 测试常见坑
doc/deployment/deploy-runbook.md        ← 部署手册
doc/deployment/rollback-runbook.md      ← 回滚手册
```

---

## 与其他 Skill 的关系

```
project-dev-init（本 Skill）
    ↓ 输出 doc/development/ + doc/testing/ + doc/deployment/
    ↓ 更新 shared-config.json development/testing/deployment 配置
backend-development     → 读取 coding-standards + backend-gotchas + project-structure
frontend-development    → 读取 coding-standards + frontend-gotchas
testing-expert          → 读取 test-gotchas
delivery-code-review    → 读取 coding-standards
project-release-deploy  → 读取 deploy-runbook + rollback-runbook
```

---

## 与 design-system-init 的关系

| Skill | 域 | 输出目录 |
|---|---|---|
| `design-system-init` | 设计域 | `doc/design-system/` |
| `project-dev-init` | 工程域 | `doc/development/` + `doc/testing/` + `doc/deployment/` |

新项目接入时两个都需要运行。
