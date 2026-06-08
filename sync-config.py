#!/usr/bin/env python3
"""统一配置同步脚本。

把同目录下的 shared-config.json 中的通用键，合并写入每个子技能目录的 config.json。
自动发现所有相邻技能目录（含 config.json 的子目录），无需维护技能清单。

用法：
    1. cp shared-config.template.json shared-config.json
    2. 编辑 shared-config.json，填入本项目的实际值
    3. python3 sync-config.py

放置位置：
    - 本仓库根目录（同步仓库内各技能的 config.json，便于本地测试）
    - 或目标项目的 .claude/skills/ 等技能父目录（安装后就近同步）
"""
import json
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SHARED = ROOT / "shared-config.json"
# 仅这些通用键由 shared-config 统一管理；各技能专属键（output.*、prd.*、prototype.* 等）保持不动
COMMON_KEYS = ("project", "output", "database", "codebase",
               "design_system", "development", "testing", "deployment")


def deep_merge(base, overlay):
    if not isinstance(base, dict) or not isinstance(overlay, dict):
        return deepcopy(overlay)
    merged = deepcopy(base)
    for key, value in overlay.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged


def main():
    if not SHARED.exists():
        print(f"错误：未找到 {SHARED}")
        print("请先执行：cp shared-config.template.json shared-config.json，并填入项目值。")
        raise SystemExit(1)

    shared = json.loads(SHARED.read_text(encoding="utf-8"))
    targets = sorted(p for p in ROOT.glob("*/config.json"))
    if not targets:
        print("未发现任何 <技能>/config.json，无需同步。")
        return

    for path in targets:
        current = json.loads(path.read_text(encoding="utf-8"))
        for key in COMMON_KEYS:
            if key in shared:
                current[key] = deep_merge(current.get(key, {}), shared[key])
        path.write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
        print(f"已同步：{path.relative_to(ROOT)}")

    print(f"\n完成：共同步 {len(targets)} 个技能。")


if __name__ == "__main__":
    main()
