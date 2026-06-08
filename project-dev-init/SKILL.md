---
name: project-dev-init
description: 为项目初始化工程规范文档。通过分析现有代码结构、技术栈、构建配置和部署环境，提取编码规范、项目结构说明、后端/前端 gotchas、测试策略、部署手册，输出到项目 doc/ 目录。新项目接入开发阶段 Skill 前必须先运行此 Skill。
triggers:
  - 初始化开发规范
  - 生成项目规范
  - 提取编码规范
  - 项目工程初始化
  - project dev init
  - 整理技术规范
---

# Project Dev Init Skill

## 概述

本 Skill 为项目生成**工程规范文档**，作为 `backend-development`、`frontend-development`、`testing-expert`、`delivery-code-review`、`project-release-deploy` 的前置依赖。

与 `design-system-init`（设计域）对称，本 Skill 覆盖**工程域**：开发规范、测试规范、部署手册。

**自动化边界**：
- ✅ **脚本辅助**：扫描项目目录结构、识别技术栈和构建工具、提取配置模式
- ✅ **人工归纳 + Claude 辅助**：从现有代码中归纳编码规范、常见 gotchas、部署步骤
- ❌ 不做新的规范设计（只提取现有事实和已有约定）
- ❌ 不做代码实现或部署操作

**阅读顺序**：`SKILL.md`（本文件）→ `references/gotchas.md` → `references/domain-rules.md` → 其余按需

---

## 输出文件（3 个域、7 个文件）

### 开发域（`doc/development/`）

| 文件 | 用途 | 消费方 |
|---|---|---|
| `coding-standards.md` | 编码规范（命名、分层、异常处理、日志等） | backend/frontend-development、delivery-code-review |
| `project-structure.md` | 项目目录结构说明 | backend/frontend-development |
| `backend-gotchas.md` | 后端常见坑（事务、SQL、权限、状态流转等） | backend-development |
| `frontend-gotchas.md` | 前端常见坑（还原偏差、口径、路由、组件复用等） | frontend-development |

### 测试域（`doc/testing/`）

| 文件 | 用途 | 消费方 |
|---|---|---|
| `test-gotchas.md` | 测试常见坑（数据准备、环境差异、边界遗漏等） | testing-expert |

### 部署域（`doc/deployment/`）

| 文件 | 用途 | 消费方 |
|---|---|---|
| `deploy-runbook.md` | 部署操作手册（构建→替换→重启→冒烟） | project-release-deploy |
| `rollback-runbook.md` | 回滚操作手册（回滚条件→步骤→验证） | project-release-deploy |

---

## 第一步：检查配置与代码路径

读取 `../shared-config.json` 或 `config.json`，确认：

1. `codebase.backend_path`：后端代码路径
2. `codebase.frontend_path`：前端代码路径
3. `codebase.backend_framework`：后端框架
4. `codebase.frontend_framework`：前端框架
5. `deployment.platform`：部署平台

如配置为空，询问用户：
```
需要以下信息才能开始：
1. 后端代码根目录和框架（如 Spring Boot / Django / Express）
2. 前端代码根目录和框架（如 Vue2+ElementUI / React+AntD）
3. 部署平台（如 ECS / K8s / Docker / Vercel）
4. 输出目录（默认 doc/）
```

---

## 第二步：提取项目结构（→ project-structure.md）

### 2.1 目录树

扫描后端和前端代码根目录，生成带注释的目录树：

```
{backend_path}/
├── src/main/java/...
│   ├── controller/    ← API 入口层
│   ├── service/       ← 业务逻辑层
│   ├── domain/        ← 实体层
│   └── repository/    ← 数据访问层
└── src/main/resources/
    └── mapper/        ← MyBatis XML
```

### 2.2 技术栈清单

从 `pom.xml` / `package.json` / `build.gradle` 等构建文件提取：
- 框架版本
- 核心依赖
- 构建工具

### 2.3 模块边界

识别项目的模块划分方式（按业务域 / 按技术层 / 单体等）。

---

## 第三步：提取编码规范（→ coding-standards.md）

从现有代码中归纳（不是发明）：

### 3.1 后端规范

| 提取项 | 分析方式 |
|---|---|
| 命名约定 | 扫描类名、方法名、变量名的命名模式 |
| 分层结构 | Controller → Service → Repository 的调用规范 |
| 异常处理 | 搜索 try-catch / @ExceptionHandler / 全局异常处理 |
| 日志规范 | 搜索 log.info / log.error 的使用模式 |
| 事务边界 | 搜索 @Transactional 的使用模式 |
| API 风格 | REST 路径命名、入参/出参格式 |

### 3.2 前端规范

| 提取项 | 分析方式 |
|---|---|
| 文件组织 | 页面/组件/API/store 的目录约定 |
| 组件命名 | PascalCase / kebab-case |
| 状态管理 | Vuex / Pinia / Redux 的使用模式 |
| API 调用 | 封装方式（统一 request 层 / 直接 axios） |
| 权限控制 | 路由守卫 / 指令 / 组件内判断 |

---

## 第四步：提取 Gotchas（→ backend-gotchas.md + frontend-gotchas.md）

从现有代码的"坑"中归纳。**Gotchas 不是规范，是"踩过的坑和规避方式"。**

### 4.1 后端 Gotchas 方向

| 类别 | 示例 |
|---|---|
| 事务边界 | 嵌套事务传播、异步方法丢失事务 |
| SQL / 索引 | 全表扫描、N+1 查询、索引失效 |
| 权限 / 状态流转 | 越权访问、非法状态转换 |
| 数据迁移 | 历史数据兼容、枚举值变更 |
| 并发 | 乐观锁/悲观锁、重复提交 |

### 4.2 前端 Gotchas 方向

| 类别 | 示例 |
|---|---|
| 页面还原 | 设计稿与组件库默认样式冲突 |
| API 字段口径 | 前后端字段名不一致、枚举值映射 |
| 交互 | 弹窗关闭后表单未重置、列表刷新时机 |
| 权限 / 路由 | 菜单权限与 API 权限不同步 |
| 性能 | 大列表渲染、不必要的 watcher |

### 4.3 初始状态

首次生成时 gotchas 文件为**种子内容**，后续通过 `delivery-code-review` 的 `recurring-issues.md` 持续补充。

---

## 第五步：提取测试规范（→ test-gotchas.md）

| 提取项 | 分析方式 |
|---|---|
| 测试工具 | 搜索 test 目录、jest.config / pytest.ini 等 |
| 测试数据策略 | 是否有 fixture / factory / seed 数据 |
| 环境差异 | 本地 vs 测试 vs 生产的配置差异 |
| 常见遗漏 | 权限测试、边界值、并发场景 |

> 如果项目没有测试基础设施，输出一份最小可用的 test-gotchas.md，标注 `[建议]`。

---

## 第六步：提取部署手册（→ deploy-runbook.md + rollback-runbook.md）

### 6.1 部署手册

从现有部署脚本 / CI 配置 / Dockerfile 等提取：

```markdown
## 部署步骤

1. 前置检查
   - [ ] review 全部关闭
   - [ ] 测试通过
   - [ ] 配置文件已更新

2. 备份
   - 数据库备份命令
   - 当前版本备份

3. 构建
   - 后端构建命令
   - 前端构建命令

4. 部署
   - 替换步骤
   - 服务重启命令

5. 冒烟验证
   - 健康检查 URL
   - 核心功能验证点
```

### 6.2 回滚手册

```markdown
## 回滚条件
- 冒烟验证失败
- 核心功能不可用
- 性能严重劣化

## 回滚步骤
1. 停止服务
2. 恢复备份
3. 重启服务
4. 验证回滚成功
```

> 如果项目没有部署脚本，输出模板并标注 `[待填充]`。

---

## 第七步：生成文件并用户确认

创建目录并输出文件：

```
doc/
├── development/
│   ├── coding-standards.md
│   ├── project-structure.md
│   ├── backend-gotchas.md
│   └── frontend-gotchas.md
├── testing/
│   └── test-gotchas.md
└── deployment/
    ├── deploy-runbook.md
    └── rollback-runbook.md
```

输出后提示用户确认：
```
已生成工程规范文档：
1. doc/development/（编码规范 + 项目结构 + 前后端 gotchas）
2. doc/testing/（测试 gotchas）
3. doc/deployment/（部署手册 + 回滚手册）

请审阅后确认，后续开发/测试/部署 Skill 将以此为基准。
```

---

## 第八步：更新 shared-config.json

确认后，检查配置是否正确指向生成的文件路径：

```json
{
  "development": {
    "coding_standards_path": "doc/development/coding-standards.md",
    "backend_gotchas_path": "doc/development/backend-gotchas.md",
    "frontend_gotchas_path": "doc/development/frontend-gotchas.md",
    "project_structure_path": "doc/development/project-structure.md"
  },
  "testing": {
    "test_strategy": "api-first",
    "test_env": "local",
    "test_gotchas_path": "doc/testing/test-gotchas.md"
  },
  "deployment": {
    "platform": "ecs",
    "deploy_runbook_path": "doc/deployment/deploy-runbook.md",
    "rollback_runbook_path": "doc/deployment/rollback-runbook.md"
  }
}
```

运行 `../sync_shared_config.py` 同步到各 Skill。

---

## 第九步：记录运行日志

文件命名：`{YYYY-MM-DD}-init.md`

日志内容：日期、项目名、技术栈、提取的规范数量、gotchas 条目数量、输出文件路径。

---

## 降级策略

| 场景 | 做法 |
|---|---|
| 新项目无代码 | 按用户选择的技术栈生成模板，值标注 `[待填充]` |
| 项目无测试基础 | 生成最小 test-gotchas.md，标注 `[建议]` |
| 项目无部署脚本 | 生成部署手册模板，标注 `[待填充]` |
| 只有后端无前端 | 跳过 frontend-gotchas.md，标注"纯后端项目" |

---

## Gotchas（最高优先级阅读）

详见 `references/gotchas.md`，最关键三条：

1. **只提取事实，不发明规范**：从代码中读到什么就写什么。"建议改进"单独列出，不混入基线。

2. **Gotchas 不是规范**：规范说"应该怎么做"，gotchas 说"踩过什么坑、怎么避免"。两者分文件存放。

3. **部署手册必须可执行**：不能只写"部署到服务器"，要写具体命令。如果不知道命令，标注 `[待填充]` 让用户补充。

---

## 文件索引

| 文件 | 用途 | 何时读取 |
|---|---|---|
| `config.json` | 项目配置（代码路径 + 输出路径） | 第一步，必读 |
| `references/domain-rules.md` | 提取规则与输出格式规范 | 第二~六步 |
| `references/gotchas.md` | 常见错误 | 开始前必读 |
| `references/examples.md` | 不同技术栈的示例输出 | 不确定格式时参考 |
| `references/glossary.md` | 术语定义 | 遇到歧义时查阅 |
| `assets/*-template.md` | 各文件的输出模板 | 第七步 |
| `scripts/scan_project.py` | 扫描项目结构和技术栈 | 第二步，辅助工具 |
| `scripts/init_dev_docs.sh` | 初始化输出目录 | 第一步（可选） |
| `logs/` | 历次运行记录 | 输出前查阅 |
