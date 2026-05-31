# skills

个人 Claude Code / OpenClaw 技能集合。

## 已收录

| 技能 | 说明 |
|---|---|
| [`quality-briefing/`](./quality-briefing) | 数据质量监控每周图形化简报：取数 → 分析 → 渲染长图 → 推送钉钉群 |
| [`subagent-dev-orchestrator/`](./subagent-dev-orchestrator) | 主会话编排 + 子 agent 实现 + codex 复审：逐任务串行开发，每个任务一个独立子会话实现并经 codex 复审无 P0/P1 才进入下一个 |

每个子目录都是一个独立技能，入口是该目录下的 `SKILL.md`。

---

## 安装到其他项目

不同的 AI 编码工具从**不同目录**读取技能，所以同一个技能通常要安装到目标项目的多个 skills 目录：

| 目录 | 被谁读取 |
|---|---|
| `skills/` | 通用入口（手动浏览 / 其他工具） |
| `.claude/skills/` | Claude Code |
| `.codex/skills/` | Codex CLI |
| `.windsurf/skills/` | Windsurf |

### 方式一：一键脚本（推荐）

```bash
# 1. 克隆本仓库
git clone https://github.com/huangguohua/skills.git
cd skills

# 2. 安装指定技能到目标项目（只安装目标项目里已存在的 skills 目录）
./install.sh subagent-dev-orchestrator /路径/到/你的项目

# 如果目标项目还没有任何 skills 目录，用 --all 强制创建全部 4 个目录
./install.sh subagent-dev-orchestrator /路径/到/你的项目 --all
```

脚本会把技能本体拷贝到目标项目中**已存在**的那几个 skills 目录（`skills/`、`.claude/skills/`、`.codex/skills/`、`.windsurf/skills/`），并自动剔除 `.DS_Store`、运行日志等产物。

### 方式二：手动拷贝

```bash
git clone https://github.com/huangguohua/skills.git
PROJ=/路径/到/你的项目

for d in skills .claude/skills .codex/skills .windsurf/skills; do
  mkdir -p "$PROJ/$d"
  cp -R skills/subagent-dev-orchestrator "$PROJ/$d/"
done
```

### 安装后

进入目标项目，修改技能目录下的 `config.json`，适配该项目的技术栈、代码路径与数据库（MCP server）。其余文件（`SKILL.md`、`assets/`、`references/`）一般无需改动。
