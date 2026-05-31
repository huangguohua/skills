#!/usr/bin/env bash
#
# install.sh — 把本仓库的某个技能安装到目标项目的所有 skills 目录。
#
# 不同的 AI 编码工具从不同目录读取技能：
#   skills/             通用入口（手动浏览 / 其他工具）
#   .claude/skills/     Claude Code
#   .codex/skills/      Codex CLI
#   .windsurf/skills/   Windsurf
#
# 本脚本会把指定技能目录同时安装到上面这些目录中（只安装目标项目里已存在的那些）。
#
# 用法：
#   ./install.sh <技能名> <目标项目根目录> [--all]
#
#   <技能名>          本仓库下的技能目录名，如 subagent-dev-orchestrator
#   <目标项目根目录>   要安装到的项目根路径
#   --all             即使目标目录不存在也强制创建并安装到全部 4 个目录
#
# 示例：
#   ./install.sh subagent-dev-orchestrator ~/work/my-project
#   ./install.sh subagent-dev-orchestrator ~/work/my-project --all
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

SKILL="${1:-}"
TARGET="${2:-}"
FORCE_ALL="${3:-}"

if [[ -z "$SKILL" || -z "$TARGET" ]]; then
  echo "用法: ./install.sh <技能名> <目标项目根目录> [--all]" >&2
  exit 1
fi

SRC="$SCRIPT_DIR/$SKILL"
if [[ ! -d "$SRC" ]]; then
  echo "错误: 本仓库中不存在技能目录: $SKILL" >&2
  echo "可用技能:" >&2
  find "$SCRIPT_DIR" -maxdepth 1 -mindepth 1 -type d ! -name '.git' -exec basename {} \; >&2
  exit 1
fi

if [[ ! -d "$TARGET" ]]; then
  echo "错误: 目标项目根目录不存在: $TARGET" >&2
  exit 1
fi

# 目标项目里所有需要安装的 skills 父目录
SKILL_DIRS=("skills" ".claude/skills" ".codex/skills" ".windsurf/skills")

installed=0
for d in "${SKILL_DIRS[@]}"; do
  parent="$TARGET/$d"
  if [[ -d "$parent" || "$FORCE_ALL" == "--all" ]]; then
    mkdir -p "$parent"
    dest="$parent/$SKILL"
    rm -rf "$dest"
    # 拷贝技能本体，剔除运行产物与系统文件
    rsync -a --exclude='.DS_Store' --exclude='logs/*.log' "$SRC/" "$dest/" 2>/dev/null \
      || { cp -R "$SRC" "$dest" && find "$dest" -name '.DS_Store' -delete; }
    echo "✓ 已安装到 $parent/$SKILL"
    installed=$((installed+1))
  else
    echo "· 跳过 $parent（目录不存在，用 --all 可强制创建）"
  fi
done

if [[ $installed -eq 0 ]]; then
  echo "未安装到任何目录。目标项目中没有现成的 skills 目录，可加 --all 强制创建。" >&2
  exit 1
fi

echo ""
echo "完成：共安装到 $installed 个目录。"
echo "下一步：进入目标项目，按需修改 $SKILL/config.json 适配该项目的技术栈与数据库。"
