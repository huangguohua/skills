# Codex Verified Requirement Design

通用的「需求设计 → codex 复审循环」Skill。把 `codex-verified-fix-loop` 的复审内循环从**改代码**迁移到**写需求**：
产出经 codex 把关、可直接进入架构/开发的需求规格。技术栈无关，整目录复制到任意项目后只改 `config.json` 即可用。

## 核心模型

把「写需求 → codex review → 修订 → codex 复核 → …… 直到全部解决」固化为闭环：

- **主会话**：对齐现状（查 DB MCP/现有接口/代码）后，亲自写**结构化需求文档**。
- **codex:rescue**：每次写完/改完做只读复审，按 **HIGH/MEDIUM/LOW/SUGGESTION** 分级，
  审的是**需求质量五维度**——完整性 / 一致性 / 可实现性 / 可测试性 / 范围。
- **内循环**：写 → codex 复审 → 按 HIGH/MEDIUM 修订 → **同一 codex 线程**（`--resume`）复核 → 直到 CLEAR。
- **放行线**：无 HIGH/MEDIUM 即定稿；LOW/SUGGESTION 记日志不阻塞。
- **下游**：CLEAR 后提示业务评审 / UI 基线 / 架构设计，由用户确认后再启动。

## 与相邻 Skill 的区别

| | codex-verified-requirement-design | codex-verified-fix-loop | prd-generate |
|---|---|---|---|
| 产出 | 需求规格（系统做什么） | 代码改动 | 需求规格 |
| 谁产出 | 主会话写文档 | 主会话改代码 | 主会话写文档 |
| codex 角色 | 需求质量闸门（5 维度） | 代码质量闸门 | 无（一次成稿） |
| 复审循环 | ✅ 同线程内循环 | ✅ 同线程内循环 | ❌ |

> 一句话：**prd-generate 出稿 + 把 business-requirement-review 的人工评审前移成 codex 自动内循环**。

## 快速开始

1. 给一段业务诉求（或已确认的 discovery.md）。
2. 确认本机 Codex CLI 就绪（否则 `/codex:setup`）。
3. 触发本 Skill（关键词：codex 把关需求 / 需求设计到没问题 / verified PRD）。
4. 主会话对齐现状 → 写需求 → codex 复审循环；全部 CLEAR 后提示下游 Skill。

## 目录结构

```
codex-verified-requirement-design/
  SKILL.md                                   # Skill 定义与闭环规则（技术栈无关）
  config.json                                # 唯一需按项目修改的文件（输出位置 / 数据库 MCP / 复审维度参数）
  README.md                                  # 本文件
  references/
    gotchas.md                               # 坑点（codex 跑去评代码、喂现状约束、查库走 MCP、放行线等）
    examples.md                              # 一个完整需求复审内循环实例（会员到期推送案例）
  assets/
    requirement-doc-template.md              # 结构化需求文档模板（requirements.md）
    codex-review-prompt-template.md          # 给 codex:rescue 的需求复审提示词模板（首轮）
    codex-recheck-prompt-template.md         # 同线程复核（--resume）提示词模板
    requirement-review-loop-template.md      # 每次循环的日志模板
  specs/                                     # 需求文档与循环日志输出（实际落 config.output_dir）
```

## 安装 / 部署（重要）

不同 AI 编码工具从**不同目录**读取技能，所以同一技能要装到目标项目的多个 skills 目录：
`skills/`（通用入口）、`.claude/skills/`（Claude Code）、`.codex/skills/`（Codex CLI）、`.windsurf/skills/`（Windsurf）。
这些目录各自独立，**必须把整个 `codex-verified-requirement-design/` 同步到每一处，运行时才加载得到。**

**用本仓库根目录的 `install.sh`（推荐）**：

```bash
git clone https://github.com/huangguohua/skills.git
cd skills
./install.sh codex-verified-requirement-design /路径/到/你的项目
```

脚本会把本技能拷到目标项目里已存在的 `skills/`、`.claude/skills/`、`.codex/skills/`、`.windsurf/skills/`
（首次没有这些目录时加 `--all` 强制创建全部 4 个），并自动剔除 `.DS_Store` 与运行日志。

**手动安装（等价）**：

```bash
PROJ=/路径/到/你的项目
for d in skills .claude/skills .codex/skills .windsurf/skills; do
  mkdir -p "$PROJ/$d"
  cp -R codex-verified-requirement-design "$PROJ/$d/"
done
```

安装后**重启对应 AI 工具的会话**即可加载。更新技能时重跑同一命令覆盖即可（幂等）。

## 关键原则

- **codex 用 Agent 工具调**：`subagent_type: "codex:codex-rescue"`，禁止 `Skill(codex:rescue)`（会挂起）。
- **首句声明"需求文档评审"**：否则 codex 会跑去评代码；resume 复核要重申。
- **喂现状约束**：把真实表/字段/接口结论给 codex，它才能判可实现性/一致性。
- **HIGH/MEDIUM 不放行**：未关闭不算定稿，不进下游。
- **查库走 MCP**：禁止猜表结构、禁止跨库套字段。
- **可移植**：换项目只改 `config.json`。
