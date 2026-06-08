# skills

通用的 AI 编码技能集合 —— 覆盖**需求 → 设计原型 → UI → 前后端开发 → 测试 → 代码审查 → 发布**全流程，技术栈无关，改 `config.json` 即可换项目复用。同时适配 Claude Code / Codex CLI / Windsurf 等工具。

## 全流程套件（suite）

按软件交付顺序排列，每个子目录是一个独立技能，入口是其 `SKILL.md`：

| 阶段 | 技能 | 一句话 |
|---|---|---|
| 现状探索 | [`solution-discovery`](./solution-discovery) | 查代码/库/接口，输出 `discovery.md` |
| 需求 | [`prd-generate`](./prd-generate) | 产出 `requirements.md` + `prototype.md` |
| 需求评审 | [`business-requirement-review`](./business-requirement-review) | 结构化评审需求质量 |
| UI 基线 | [`ui-design-baseline`](./ui-design-baseline) | 定视觉/交互基线 |
| 原型 | [`prototype-generate`](./prototype-generate) | 生成 `ui-design.html` + `.pen` 高保真稿 |
| 原型演示 | [`prototype-demo`](./prototype-demo) | 拆分 HTML 组装成可演示单文件 |
| 设计系统 | [`design-system-init`](./design-system-init) | 提取项目设计基线文件 |
| 架构设计 | [`architect-design`](./architect-design) | 输出 `design.md` + `tasks.md` + DB 设计 |
| 设计评审 | [`technical-design-review`](./technical-design-review) | 六维度评审技术设计 |
| 工程规范 | [`project-dev-init`](./project-dev-init) | 提取编码规范/gotchas/部署手册 |
| 开发编排 | [`development-orchestrator`](./development-orchestrator) | 按 tasks.md 调度前后端 |
| 子agent编排 | [`subagent-dev-orchestrator`](./subagent-dev-orchestrator) | 主会话编排 + 子 agent 实现 + codex 复审 |
| 后端实现 | [`backend-development`](./backend-development) | 按 design/tasks 写后端 |
| 前端实现 | [`frontend-development`](./frontend-development) | 按 design + 原型写前端 |
| 测试 | [`testing-expert`](./testing-expert) | 设计用例 + 执行 + `test-report.md` |
| 代码审查 | [`delivery-code-review`](./delivery-code-review) | 结构化审查，产出 `REVIEW_REPORT.md` |
| 验证修复闭环 | [`codex-verified-fix-loop`](./codex-verified-fix-loop) | 定位 → 修复 → codex 复审循环（单缺陷/小需求） |
| 发布 | [`project-release-deploy`](./project-release-deploy) | 按部署配置执行发布 |

> 套件的强制闸门、阶段流转与协作规则见各 `SKILL.md`。

## 安装

不同 AI 编码工具从**不同目录**读取技能，所以同一技能通常要装到目标项目的多个 skills 目录：

| 目录 | 被谁读取 |
|---|---|
| `skills/` | 通用入口（手动浏览 / 其他工具） |
| `.claude/skills/` | Claude Code |
| `.codex/skills/` | Codex CLI |
| `.windsurf/skills/` | Windsurf |

### 一键脚本（推荐）

```bash
git clone https://github.com/huangguohua/skills.git
cd skills

# 安装全流程套件到目标项目（首次没有 skills 目录时加 --all 强制创建全部 4 个）
./install.sh suite /路径/到/你的项目 --all

# 或只装某一个技能
./install.sh codex-verified-fix-loop /路径/到/你的项目
```

脚本会把技能拷到目标项目中已存在（或 `--all` 强制创建）的 `skills/`、`.claude/skills/`、`.codex/skills/`、`.windsurf/skills/`，自动剔除 `.DS_Store` 与运行日志，并把 `shared-config.template.json` 和 `sync-config.py` 一并放入每个 skills 目录。

### 手动拷贝

```bash
PROJ=/路径/到/你的项目
for d in skills .claude/skills .codex/skills .windsurf/skills; do
  mkdir -p "$PROJ/$d"
  cp -R subagent-dev-orchestrator "$PROJ/$d/"
done
```

## 统一配置（共享配置）

全流程套件里的技能共用同一组项目参数（技术栈、代码路径、数据库 MCP、文档路径等）。这些参数集中在 **`shared-config.json`**，无需逐个技能改 `config.json`：

```bash
cd /路径/到/你的项目/.claude/skills    # 任一已安装的 skills 目录
cp shared-config.template.json shared-config.json
# 编辑 shared-config.json，填入本项目实际值
python3 sync-config.py                 # 同步通用键到各技能的 config.json
```

- 技能运行时**优先读取上层 `shared-config.json`**，`config.json` 是同步后的就近副本。
- `sync-config.py` 只覆盖通用键（`project / output / database / codebase / design_system / development / testing / deployment`），各技能专属键（如 `prd.*`、`prototype.*`、`output.naming_convention`）保持不动。
- 每个工具目录（`.claude/skills`、`.codex/skills`…）各放一份 `shared-config.json` 并各自 `sync-config.py` 即可；内容相同。

`config.json` 关键字段：

| 字段 | 含义 |
|---|---|
| `project.*` | 项目名 / 描述 / 前缀 |
| `database.mcp_server` | 查真实 DDL 的 MCP server（无则留空，定位时不查库） |
| `codebase.*` | 前后端路径与框架 |
| `design_system.*` / `development.*` | 设计系统与工程规范文档路径 |
| `testing.*` / `deployment.*` | 测试与部署配置 |

## 其它独立技能

除全流程套件外，本仓库还收录：

| 技能 | 说明 |
|---|---|
| [`quality-briefing`](./quality-briefing) | 数据质量周报：取数 → 分析 → 渲染长图 → 推送钉钉群 |
| [`yunxiao-defect-resolver`](./yunxiao-defect-resolver) | 阿里云云效缺陷修复闭环，技术栈无关 |

## 维护

- 新增/下线技能时，同步更新本 README 表格与 `install.sh` 里的 `SUITE` 数组。
- 技能带模板/脚本/参考资料时，放在各自目录内由 `SKILL.md` 引用。
- 通用参数改动改 `shared-config.template.json`；项目侧改 `shared-config.json` 后重跑 `sync-config.py`。
