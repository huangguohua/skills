#!/usr/bin/env bash
#
# install.sh — 把本仓库的技能安装到目标项目的所有 skills 目录。
#
# 不同的 AI 编码工具从不同目录读取技能：
#   skills/             通用入口（手动浏览 / 其他工具）
#   .claude/skills/     Claude Code
#   .codex/skills/      Codex CLI
#   .windsurf/skills/   Windsurf
#
# 本脚本把指定技能（或整套全流程技能）同时安装到上面这些目录中
# （默认只安装目标项目里已存在的那些；用 --all 强制创建全部 4 个目录）。
# 安装时会把 shared-config.template.json 与 sync-config.py 拷入各 skills 目录，
# 供「统一配置」使用。
#
# 用法：
#   ./install.sh <技能名|suite> <目标项目根目录> [--all]
#
#   <技能名>          本仓库下的技能目录名，如 subagent-dev-orchestrator
#   suite             安装全流程套件（需求→设计→UI→前后端开发→测试→审查→发布）
#   <目标项目根目录>   要安装到的项目根路径
#   --all             即使目标目录不存在也强制创建并安装到全部 4 个目录
#
# 示例：
#   ./install.sh suite ~/work/my-project --all
#   ./install.sh codex-verified-fix-loop ~/work/my-project
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

SKILL="${1:-}"
TARGET="${2:-}"
FORCE_ALL="${3:-}"

# 全流程套件成员（与 README 一致）
SUITE=(
  solution-discovery prd-generate business-requirement-review
  ui-design-baseline prototype-generate prototype-demo design-system-init
  architect-design technical-design-review project-dev-init
  development-orchestrator subagent-dev-orchestrator
  backend-development frontend-development testing-expert
  delivery-code-review codex-verified-fix-loop project-release-deploy
)

if [[ -z "$SKILL" || -z "$TARGET" ]]; then
  echo "用法: ./install.sh <技能名|suite> <目标项目根目录> [--all]" >&2
  exit 1
fi
if [[ ! -d "$TARGET" ]]; then
  echo "错误: 目标项目根目录不存在: $TARGET" >&2
  exit 1
fi

if [[ "$SKILL" == "suite" ]]; then
  SKILLS=("${SUITE[@]}")
else
  if [[ ! -d "$SCRIPT_DIR/$SKILL" ]]; then
    echo "错误: 本仓库中不存在技能目录: $SKILL" >&2
    echo "可用技能 (或用 suite 安装全套):" >&2
    find "$SCRIPT_DIR" -maxdepth 1 -mindepth 1 -type d ! -name '.git' -exec basename {} \; >&2
    exit 1
  fi
  SKILLS=("$SKILL")
fi

SKILL_DIRS=("skills" ".claude/skills" ".codex/skills" ".windsurf/skills")

copy_skill() {  # $1=技能名 $2=目标父目录
  local name="$1" dest="$2/$1"
  rm -rf "$dest"
  rsync -a --exclude='.DS_Store' --exclude='logs/*.log' --exclude='outputs/*' "$SCRIPT_DIR/$name/" "$dest/" 2>/dev/null \
    || { cp -R "$SCRIPT_DIR/$name" "$dest" && find "$dest" -name '.DS_Store' -delete; }
}

installed_dirs=0
for d in "${SKILL_DIRS[@]}"; do
  parent="$TARGET/$d"
  if [[ -d "$parent" || "$FORCE_ALL" == "--all" ]]; then
    mkdir -p "$parent"
    for name in "${SKILLS[@]}"; do
      copy_skill "$name" "$parent"
    done
    cp "$SCRIPT_DIR/shared-config.template.json" "$parent/shared-config.template.json"
    cp "$SCRIPT_DIR/sync-config.py" "$parent/sync-config.py"
    echo "✓ 已安装 ${#SKILLS[@]} 个技能 + 共享配置到 $parent"
    installed_dirs=$((installed_dirs+1))
  else
    echo "· 跳过 $parent（目录不存在，用 --all 可强制创建）"
  fi
done

if [[ $installed_dirs -eq 0 ]]; then
  echo "未安装到任何目录。目标项目中没有现成的 skills 目录，可加 --all 强制创建。" >&2
  exit 1
fi

cat <<EOF

完成：共安装到 $installed_dirs 个 skills 目录。

下一步（统一配置）：
  cd "$TARGET/.claude/skills"   # 或任一已安装的 skills 目录
  cp shared-config.template.json shared-config.json
  # 编辑 shared-config.json，填入本项目技术栈、代码路径、数据库(MCP)等
  python3 sync-config.py        # 同步到各技能的 config.json

各技能运行时优先读取上层 shared-config.json，每个工具目录各放一份并各自 sync 即可。
EOF
