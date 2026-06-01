# Yunxiao Defect Resolver

阿里云**云效缺陷修复闭环** Skill：单条循环处理云效缺陷（Bug 工作项）——
拉一条「待处理 / 再次打开」缺陷 → 定位代码并修复 → `codex:rescue` 独立 review →
通过后 commit、把缺陷推到「已解决」、回写评论。每条之间停下来等用户「继续」，绝不批量跑。

技术栈无关：整目录复制到任意项目，只改 `config.json` + `export YUNXIAO_TOKEN` 即可用。

## 目录结构

```
yunxiao-defect-resolver/
  SKILL.md                       # Skill 定义与执行流程（强制顺序 + 闸门）
  config.json                    # 唯一需按项目修改的文件（不含密钥）
  README.md                      # 本文件
  scripts/
    yunxiao_defects.py           # 云效缺陷 CLI（validate/list-states/list/detail/update-status/add-comment）
  references/
    yunxiao-defect-api.md        # 缺陷相关 OpenAPI 接口约定
```

## 依赖

- Python 3（标准库即可，无第三方依赖）
- 一个云效**个人访问令牌（PAT）**，对目标项目有缺陷读写权限
- 本机能跑 `codex:rescue`（用于第 5 步独立 review）

## 安装

本 Skill 随 [`skills`](https://github.com/huangguohua/skills) 仓库分发。不同 AI 工具从不同目录读技能，所以通常要装到目标项目的多个 skills 目录。

### 方式一：一键脚本（推荐）

```bash
git clone https://github.com/huangguohua/skills.git
cd skills

# 装到目标项目里已存在的 skills 目录（skills/ .claude/skills/ .codex/skills/ .windsurf/skills/）
./install.sh yunxiao-defect-resolver /路径/到/你的项目

# 若目标项目还没有任何 skills 目录，用 --all 强制创建全部 4 个
./install.sh yunxiao-defect-resolver /路径/到/你的项目 --all
```

### 方式二：手动拷贝

```bash
git clone https://github.com/huangguohua/skills.git
PROJ=/路径/到/你的项目
for d in skills .claude/skills .codex/skills .windsurf/skills; do
  mkdir -p "$PROJ/$d"
  cp -R skills/yunxiao-defect-resolver "$PROJ/$d/"
done
```

> 提示：如果目标项目用软链让 `.claude/skills`、`.codex/skills` 都指向同一个 `skills/`
> （`ln -s ../skills .claude/skills`），那么只需把本 Skill 放进 `skills/` 一处即可，三处共享同一份。

## 配置

### 1）项目信息 → `config.json`（会进版本库，**不放密钥**）

把占位值改成你云效项目的真实值：

```jsonc
{
  "yunxiao": {
    "organization_id": "<your-org-id>",     // 必填
    "project_id": "<your-project-id>",       // 必填
    "base_url": "https://openapi-rdc.aliyuncs.com",
    "bug_type_name": "缺陷",
    "todo_state_names": ["待处理", "再次打开"],
    "resolved_state_name": "已解决"
  }
}
```

> 怎么拿 `organization_id` / `project_id`：登录云效，组织 ID 在组织管理页 URL 里；
> 项目 ID 可先随便填，跑 `validate` 通过后用 `list-states` 报错信息或云效项目设置页确认。
> 状态名（待处理/已解决等）因项目模板而异——先跑 `list-states` 看真实状态名再校正。

### 2）PAT 密钥 → 环境变量（**绝不写进 config.json**）

```bash
export YUNXIAO_TOKEN="你的云效PAT"
```

`config.json` 里的所有键都能用同名大写环境变量覆盖（`YUNXIAO_ORG_ID` / `YUNXIAO_PROJECT_ID` /
`YUNXIAO_BASE_URL` / `YUNXIAO_BUG_TYPE_NAME` / `YUNXIAO_DEFECT_TODO_STATES` /
`YUNXIAO_DEFECT_RESOLVED_STATE` / `YUNXIAO_HTTP_TIMEOUT_SECONDS`），优先级高于 config.json。

## 验证安装

```bash
export YUNXIAO_TOKEN="你的PAT"
cd /路径/到/你的项目

# 1. 校验 token + 打印当前用户
python skills/yunxiao-defect-resolver/scripts/yunxiao_defects.py validate

# 2. 打印项目 Bug 工作流状态映射（确认状态名与 config.json 对得上）
python skills/yunxiao-defect-resolver/scripts/yunxiao_defects.py list-states

# 3. 拉「待处理/再次打开」缺陷列表
python skills/yunxiao-defect-resolver/scripts/yunxiao_defects.py list --limit 50
```

`validate` 打出当前用户、`list-states` 打出状态映射，即安装成功。
之后在 Claude Code / Codex 里说「修云效缺陷 / 拉一条缺陷」即可进入 SKILL.md 的闭环流程。

## CLI 速查

| 子命令 | 作用 |
|---|---|
| `validate` | 校验 PAT 并打印当前用户 |
| `list-states` | 打印项目 Bug 工作项类型与工作流状态（id ↔ name） |
| `list [--states .. --limit ..]` | 拉指定状态集合下的缺陷列表 |
| `detail --workitem-id <id>` | 拉单条缺陷详情（描述/附件/负责人） |
| `update-status --workitem-id <id> --state 已解决 [--dry-run]` | 推动缺陷状态 |
| `add-comment --workitem-id <id> --content ..` | 给缺陷追加评论 |

## 安全约束

- **PAT 只走环境变量**，绝不写进 `config.json`（后者进版本库）。
- 不在 commit message / 评论 / 日志里输出 PAT 原文。
- 第 5 步 `codex:rescue` 未给「无阻断」结论前，禁止 commit / 改状态。
- 第 10 步 CI/CD 部署是不可回退动作，未配置 `pipelines` 或用户未确认「已合并」时跳过。
