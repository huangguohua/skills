#!/usr/bin/env python3
"""Yunxiao defect (Bug) listing / detail / state transition CLI.

Subcommands:
  validate              校验 PAT 是否可用并打印当前用户。
  list-states           查询项目 Bug 工作项类型并打印工作流状态映射（id ↔ name）。
  list                  拉取指定状态集合下的缺陷列表。
  detail                拉取单条缺陷详情（含描述、状态、负责人、附件元信息）。
  update-status         按目标状态名推动工作项状态流转。
  add-comment           给工作项追加一条评论（用于回写 commit 摘要 + review 结论）。

设计目标：复用 yunxiao_workitems.py 的鉴权与 HTTP 调用模式，但保持本脚本自包含，
未来即便父脚本结构调整，缺陷解决工作流也不会被打断。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_BASE_URL = "https://openapi-rdc.aliyuncs.com"
DEFAULT_BUG_TYPE_NAME = "缺陷"
DEFAULT_TODO_STATE_NAMES = ("待处理", "再次打开")
DEFAULT_RESOLVED_STATE_NAME = "已解决"
NETWORK_RETRY_COUNT = 3
NETWORK_RETRY_DELAY_SECONDS = 1.0
DEFAULT_HTTP_TIMEOUT_SECONDS = 120


class YunxiaoError(RuntimeError):
    pass


@dataclass
class Config:
    token: str
    organization_id: str
    default_project_id: str
    base_url: str
    bug_type_name: str
    todo_state_names: tuple[str, ...]
    resolved_state_name: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Yunxiao defect (Bug) workflow CLI."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("validate", help="校验 token 并打印当前用户信息")

    p_states = sub.add_parser(
        "list-states", help="查询项目 Bug 工作项类型的全部工作流状态映射"
    )
    p_states.add_argument("--project-id", help="可选 项目 ID 覆盖")
    p_states.add_argument(
        "--output", help="可选 把状态映射写到 JSON 文件，便于调试与 SKILL.md 引用"
    )

    p_list = sub.add_parser("list", help="按状态名集合拉取缺陷列表")
    p_list.add_argument("--project-id", help="可选 项目 ID 覆盖")
    p_list.add_argument(
        "--states",
        help=(
            "逗号分隔的状态名列表，默认 '待处理,再次打开'。"
            "运行前先用 list-states 确认本项目实际状态名"
        ),
    )
    p_list.add_argument(
        "--assigned-to",
        help="可选 只拉指派给该用户 ID 的缺陷；缺省返回项目内所有",
    )
    p_list.add_argument("--limit", type=int, default=50, help="返回上限，默认 50")
    p_list.add_argument("--output", help="可选 把列表 JSON 写到指定文件")

    p_detail = sub.add_parser("detail", help="拉取单条缺陷详情")
    p_detail.add_argument("--workitem-id", required=True, help="云效工作项 ID")
    p_detail.add_argument("--output", help="可选 写到 JSON 文件")
    p_detail.add_argument(
        "--no-images",
        action="store_true",
        help="不下载 description 里 inline 截图（默认会下载到 /tmp/yx-imgs/<wid>/）",
    )

    p_update = sub.add_parser("update-status", help="把缺陷状态推动到目标状态")
    p_update.add_argument("--workitem-id", required=True, help="云效工作项 ID")
    p_update.add_argument(
        "--state",
        help=f"目标状态名，默认 '{DEFAULT_RESOLVED_STATE_NAME}'",
    )
    p_update.add_argument(
        "--dry-run",
        action="store_true",
        help="只解析目标 state-id 并打印将要发送的 payload，不实际改状态",
    )

    p_comment = sub.add_parser("add-comment", help="给工作项追加评论")
    p_comment.add_argument("--workitem-id", required=True, help="云效工作项 ID")
    p_comment.add_argument(
        "--content",
        help="评论内容；不传则从 stdin 读取（便于 heredoc）",
    )
    p_comment.add_argument(
        "--dry-run",
        action="store_true",
        help="只解析并打印评论 payload，不实际发送",
    )

    return parser.parse_args()


def _load_config_file() -> dict[str, Any]:
    """读取本 Skill 目录下的 config.json（scripts/ 的上一级）。

    config.json 只放**非密钥**的项目配置（organization_id / project_id / 状态名等）。
    PAT（YUNXIAO_TOKEN）属于密钥，永远只从环境变量读，绝不写进 config.json。
    文件不存在时返回空 dict（此时全部依赖环境变量）。
    占位符值（形如 <your-xxx>）视为未配置。
    """
    config_path = Path(__file__).resolve().parent.parent / "config.json"
    if not config_path.is_file():
        return {}
    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise YunxiaoError(f"读取 config.json 失败: {config_path}: {exc}") from exc
    section = raw.get("yunxiao") if isinstance(raw, dict) else None
    return section if isinstance(section, dict) else {}


def _is_placeholder(value: Any) -> bool:
    return not value or (isinstance(value, str) and value.strip().startswith("<"))


def load_config() -> Config:
    file_cfg = _load_config_file()

    def pick(env_name: str, file_key: str, default: Any = None) -> Any:
        """优先级：环境变量 > config.json > 内置默认。"""
        env_val = os.getenv(env_name)
        if env_val:
            return env_val
        file_val = file_cfg.get(file_key)
        if not _is_placeholder(file_val):
            return file_val
        return default

    # 密钥：token 只认环境变量，绝不从 config.json 读
    token = os.getenv("YUNXIAO_TOKEN")
    org_id = pick("YUNXIAO_ORG_ID", "organization_id")
    project_id = pick("YUNXIAO_PROJECT_ID", "project_id")

    missing = []
    if not token:
        missing.append("YUNXIAO_TOKEN（环境变量，PAT 密钥）")
    if _is_placeholder(org_id):
        missing.append("organization_id（环境变量 YUNXIAO_ORG_ID 或 config.json）")
    if _is_placeholder(project_id):
        missing.append("project_id（环境变量 YUNXIAO_PROJECT_ID 或 config.json）")
    if missing:
        raise YunxiaoError(
            "缺少必填配置: " + "; ".join(missing)
            + "。token 必须用环境变量；organization_id/project_id 可写在 config.json 或用环境变量覆盖。"
        )

    todo_env = os.getenv("YUNXIAO_DEFECT_TODO_STATES")
    if todo_env:
        todo_states = tuple(s.strip() for s in todo_env.split(",") if s.strip())
    else:
        file_todo = file_cfg.get("todo_state_names")
        if isinstance(file_todo, list) and file_todo:
            todo_states = tuple(str(s).strip() for s in file_todo if str(s).strip())
        else:
            todo_states = DEFAULT_TODO_STATE_NAMES

    return Config(
        token=token.strip(),
        organization_id=str(org_id).strip(),
        default_project_id=str(project_id).strip(),
        base_url=str(pick("YUNXIAO_BASE_URL", "base_url", DEFAULT_BASE_URL)).rstrip("/"),
        bug_type_name=str(pick("YUNXIAO_BUG_TYPE_NAME", "bug_type_name", DEFAULT_BUG_TYPE_NAME)).strip(),
        todo_state_names=todo_states,
        resolved_state_name=str(
            pick("YUNXIAO_DEFECT_RESOLVED_STATE", "resolved_state_name", DEFAULT_RESOLVED_STATE_NAME)
        ).strip(),
    )


def request_json(
    config: Config,
    path: str,
    *,
    query: dict[str, Any] | None = None,
    method: str = "GET",
    body: dict[str, Any] | None = None,
) -> Any:
    url = f"{config.base_url}{path}"
    if query:
        url = f"{url}?{urllib.parse.urlencode(query, doseq=True)}"

    headers = {
        "x-yunxiao-token": config.token,
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8",
    }
    payload = None
    if body is not None:
        payload = json.dumps(body, ensure_ascii=False).encode("utf-8")

    request = urllib.request.Request(url, data=payload, method=method, headers=headers)
    raw = ""
    timeout_seconds = float(
        os.getenv("YUNXIAO_HTTP_TIMEOUT_SECONDS", DEFAULT_HTTP_TIMEOUT_SECONDS)
    )
    last_error: Exception | None = None
    for attempt in range(1, NETWORK_RETRY_COUNT + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
                raw = response.read().decode("utf-8")
            break
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise YunxiaoError(f"{method} {url} 失败: {exc.code} {detail}") from exc
        except (urllib.error.URLError, socket.timeout, TimeoutError) as exc:
            last_error = exc
            if attempt >= NETWORK_RETRY_COUNT:
                raise YunxiaoError(
                    f"无法连接云效 API {url}: {exc}。请检查网络/代理/TLS。"
                ) from exc
            time.sleep(NETWORK_RETRY_DELAY_SECONDS)

    if not raw:
        return None

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise YunxiaoError(
            f"{method} {url} 返回非 JSON: {raw[:500]}"
        ) from exc


# ---------------------------------------------------------------- helpers


def fetch_current_user(config: Config) -> dict[str, Any]:
    payload = request_json(config, "/oapi/v1/platform/user")
    if not isinstance(payload, dict) or not payload.get("id"):
        raise YunxiaoError("Token 校验通过但用户信息缺失，请检查 PAT 权限。")
    return payload


def fetch_bug_workitem_type(config: Config, project_id: str) -> dict[str, Any]:
    """查项目下 category=Bug 的工作项类型，匹配 bug_type_name。"""
    types = request_json(
        config,
        f"/oapi/v1/projex/organizations/{config.organization_id}"
        f"/projects/{project_id}/workitemTypes",
        query={"category": "Bug"},
    )
    if not isinstance(types, list) or not types:
        raise YunxiaoError(
            f"项目 {project_id} 下没有 category=Bug 的工作项类型。"
            " 请确认项目模板是否启用缺陷管理。"
        )
    # 优先精确匹配，再模糊匹配
    exact = next(
        (
            t for t in types
            if str(t.get("name", "")).strip() == config.bug_type_name and t.get("id")
        ),
        None,
    )
    if exact:
        return exact
    partial = next(
        (
            t for t in types
            if config.bug_type_name in str(t.get("name", "")).strip() and t.get("id")
        ),
        None,
    )
    if partial:
        return partial
    available = ", ".join(str(t.get("name")) for t in types)
    raise YunxiaoError(
        f"未找到缺陷工作项类型 '{config.bug_type_name}'。可选: {available}"
    )


def fetch_workflow_states(
    config: Config, project_id: str, workitem_type_id: str
) -> list[dict[str, Any]]:
    """查指定工作项类型的工作流状态字典。
    云效实测可用接口（v1）:
      GET /oapi/v1/projex/organizations/{orgId}/projects/{projectId}
          /workitemTypes/{workitemTypeId}/workflows
    返回：{ name, id, defaultStatusId, statuses: [{id, name, nameEn, displayName}] }
    旧版文档里的 workflowStatuses / workflowStages 路径在当前云效 v1 OpenAPI 上返回 404。
    """
    payload = request_json(
        config,
        f"/oapi/v1/projex/organizations/{config.organization_id}"
        f"/projects/{project_id}/workitemTypes/{workitem_type_id}/workflows",
    )
    if isinstance(payload, dict):
        statuses = payload.get("statuses")
        if isinstance(statuses, list):
            return statuses
        if isinstance(payload.get("workflowStatuses"), list):
            return payload["workflowStatuses"]
    if isinstance(payload, list):
        return payload
    raise YunxiaoError(
        f"workflows 返回结构非预期: {payload!r}。"
        "请参考 references/yunxiao-defect-api.md 调整接口路径。"
    )


def resolve_state_id(states: list[dict[str, Any]], state_name: str) -> str:
    exact = next(
        (s for s in states if str(s.get("name", "")).strip() == state_name),
        None,
    )
    if exact and exact.get("id"):
        return str(exact["id"])
    candidates = ", ".join(
        f"{s.get('name')}({s.get('id')})" for s in states
    )
    raise YunxiaoError(
        f"未找到目标状态 '{state_name}'。当前可用: {candidates}"
    )


def fetch_defect_list(
    config: Config,
    project_id: str,
    workitem_type_id: str,
    state_ids: list[str],
    *,
    assigned_to: str | None,
    limit: int,
) -> list[dict[str, Any]]:
    """搜索工作项。
    云效 v1 OpenAPI 当前的 workitems:search 接口在 body 里写 statusStageIds/statusIds
    等任何状态字段都被服务端忽略（实测全部状态都会被一并返回），所以这里走
    "服务端拉全集 → 客户端按 status.id 过滤" 的方式，保证状态过滤精确。
    """
    body: dict[str, Any] = {
        "spaceId": project_id,
        "category": "Bug",
        "workitemTypeIds": [workitem_type_id],
        # 拉的页大小取上限，配合本地过滤减少漏查
        "pageSize": 200,
        "pageNumber": 1,
    }
    if assigned_to:
        body["assignedTo"] = assigned_to

    payload = request_json(
        config,
        f"/oapi/v1/projex/organizations/{config.organization_id}/workitems:search",
        method="POST",
        body=body,
    )
    raw: list[dict[str, Any]] | None = None
    if isinstance(payload, dict):
        for key in ("workitems", "list", "records", "data"):
            value = payload.get(key)
            if isinstance(value, list):
                raw = value
                break
    elif isinstance(payload, list):
        raw = payload
    if raw is None:
        raise YunxiaoError(
            f"workitems:search 返回结构未识别: {payload!r}。"
            " 请按云效官方文档调整 fetch_defect_list 的 path / body / 解析路径。"
        )

    wanted = {str(s) for s in state_ids}
    filtered: list[dict[str, Any]] = []
    for w in raw:
        status = w.get("status")
        sid = ""
        if isinstance(status, dict):
            sid = str(status.get("id") or "")
        if sid in wanted:
            filtered.append(w)
    return filtered[: max(1, min(limit, 200))]


def fetch_defect_detail(config: Config, workitem_id: str) -> dict[str, Any]:
    payload = request_json(
        config,
        f"/oapi/v1/projex/organizations/{config.organization_id}/workitems/{workitem_id}",
    )
    if not isinstance(payload, dict):
        raise YunxiaoError(f"工作项 {workitem_id} 详情返回非对象: {payload!r}")
    return payload


def update_defect_status(
    config: Config,
    workitem_id: str,
    state_id: str,
    *,
    dry_run: bool,
) -> dict[str, Any]:
    # 实测：PUT /workitems/{id} 的状态字段名是 "status"，传 statusStageId/statusId 一律
    # 返回 400 "workitem does not contains field"；成功响应是 HTTP 204 空 body。
    body = {"status": state_id}
    if dry_run:
        return {"dryRun": True, "workitemId": workitem_id, "body": body}
    payload = request_json(
        config,
        f"/oapi/v1/projex/organizations/{config.organization_id}/workitems/{workitem_id}",
        method="PUT",
        body=body,
    )
    return {"workitemId": workitem_id, "body": body, "response": payload}


def add_defect_comment(
    config: Config,
    workitem_id: str,
    content: str,
    *,
    dry_run: bool,
) -> dict[str, Any]:
    body = {"content": content}
    if dry_run:
        return {"dryRun": True, "workitemId": workitem_id, "body": body}
    payload = request_json(
        config,
        f"/oapi/v1/projex/organizations/{config.organization_id}/workitems/{workitem_id}/comments",
        method="POST",
        body=body,
    )
    return {"workitemId": workitem_id, "body": body, "response": payload}


# ---------------------------------------------------------------- commands


def cmd_validate(config: Config) -> int:
    user = fetch_current_user(config)
    print("Token 校验通过。", file=sys.stderr)
    print(json.dumps(user, ensure_ascii=False, indent=2))
    return 0


def cmd_list_states(config: Config, args: argparse.Namespace) -> int:
    project_id = (args.project_id or config.default_project_id).strip()
    bug_type = fetch_bug_workitem_type(config, project_id)
    states = fetch_workflow_states(config, project_id, str(bug_type["id"]))
    mapping = [
        {
            "id": str(s.get("id") or ""),
            "name": str(s.get("name") or ""),
            "category": s.get("category") or s.get("stageCategory"),
        }
        for s in states
    ]
    result = {
        "projectId": project_id,
        "bugWorkitemType": {"id": bug_type.get("id"), "name": bug_type.get("name")},
        "states": mapping,
        "todoStateNames": list(config.todo_state_names),
        "resolvedStateName": config.resolved_state_name,
    }
    print("缺陷工作项类型 + 状态映射 (供调试)：", file=sys.stderr)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.output:
        Path(args.output).write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"状态映射已写入 {args.output}", file=sys.stderr)
    return 0


def cmd_list(config: Config, args: argparse.Namespace) -> int:
    project_id = (args.project_id or config.default_project_id).strip()
    bug_type = fetch_bug_workitem_type(config, project_id)
    workitem_type_id = str(bug_type["id"])
    states = fetch_workflow_states(config, project_id, workitem_type_id)

    target_state_names = (
        tuple(s.strip() for s in args.states.split(",") if s.strip())
        if args.states
        else config.todo_state_names
    )
    target_state_ids = [resolve_state_id(states, name) for name in target_state_names]
    print(
        f"按状态过滤: {list(target_state_names)} → state_ids={target_state_ids}",
        file=sys.stderr,
    )

    defects = fetch_defect_list(
        config,
        project_id,
        workitem_type_id,
        target_state_ids,
        assigned_to=args.assigned_to,
        limit=args.limit,
    )
    result = {
        "projectId": project_id,
        "queriedStateNames": list(target_state_names),
        "queriedStateIds": target_state_ids,
        "count": len(defects),
        "defects": defects,
    }
    print(f"命中缺陷数: {len(defects)}", file=sys.stderr)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"列表已写入 {args.output}", file=sys.stderr)
    else:
        print(text)
    return 0


def download_inline_images(
    config: Config, workitem_id: str, payload: dict[str, Any]
) -> list[Path]:
    """从 description 里抽取 fileIdentifier 并把 inline 截图下载到 /tmp/yx-imgs/<wid>/。

    云效 v1 OpenAPI 实测可用：
      GET /oapi/v1/projex/organizations/{orgId}/workitems/{wid}/files/{fid}
    返回 { id, name, suffix, size, url }；url 是 OSS 签名 URL（约 24h 有效），
    直接 GET 即可拿 binary（不需要 x-yunxiao-token 鉴权头）。

    devops.aliyun.com/projex/api/workitem/file/url 这条 path 用 PAT 会 401，
    属于浏览器 session-only，与 OpenAPI 路径不同；不要走那条。
    """
    desc_raw = payload.get("description") or payload.get("descriptionHtml") or ""
    desc = desc_raw if isinstance(desc_raw, str) else json.dumps(desc_raw, ensure_ascii=False)
    fids = sorted(set(re.findall(r"fileIdentifier=([a-f0-9]+)", desc)))
    if not fids:
        return []

    out_dir = Path("/tmp/yx-imgs") / workitem_id
    out_dir.mkdir(parents=True, exist_ok=True)

    saved: list[Path] = []
    for fid in fids:
        try:
            meta = request_json(
                config,
                f"/oapi/v1/projex/organizations/{config.organization_id}"
                f"/workitems/{workitem_id}/files/{fid}",
            )
            if not isinstance(meta, dict):
                print(f"  [skip] {fid}: meta 返回非对象", file=sys.stderr)
                continue
            oss_url = meta.get("url")
            if not oss_url:
                print(f"  [skip] {fid}: meta 缺 url", file=sys.stderr)
                continue
            suffix = str(meta.get("suffix") or "bin").lstrip(".") or "bin"
            local = out_dir / f"{fid}.{suffix}"
            with urllib.request.urlopen(oss_url, timeout=60) as resp:
                local.write_bytes(resp.read())
            saved.append(local)
        except Exception as exc:
            print(f"  [skip] {fid}: {exc}", file=sys.stderr)
    return saved


def cmd_detail(config: Config, args: argparse.Namespace) -> int:
    detail = fetch_defect_detail(config, args.workitem_id)
    text = json.dumps(detail, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"详情已写入 {args.output}", file=sys.stderr)
    else:
        print(text)
    # 默认顺手把 description 里 inline 截图都下载下来，方便 AI 用 Read 直接看
    if not getattr(args, "no_images", False):
        imgs = download_inline_images(config, args.workitem_id, detail)
        if imgs:
            print(f"已下载 {len(imgs)} 张 inline 截图：", file=sys.stderr)
            for p in imgs:
                print(f"  {p}", file=sys.stderr)
    return 0


def cmd_update_status(config: Config, args: argparse.Namespace) -> int:
    target_state = (args.state or config.resolved_state_name).strip()
    detail = fetch_defect_detail(config, args.workitem_id)
    project_id = str(
        detail.get("spaceId") or detail.get("projectId") or config.default_project_id
    )
    workitem_type_id = str(
        detail.get("workitemTypeId") or detail.get("workitemTypeIdValue") or ""
    )
    if not workitem_type_id:
        bug_type = fetch_bug_workitem_type(config, project_id)
        workitem_type_id = str(bug_type["id"])
    states = fetch_workflow_states(config, project_id, workitem_type_id)
    state_id = resolve_state_id(states, target_state)

    outcome = update_defect_status(
        config, args.workitem_id, state_id, dry_run=args.dry_run
    )
    outcome.update(
        {
            "targetStateName": target_state,
            "targetStateId": state_id,
        }
    )
    print(json.dumps(outcome, ensure_ascii=False, indent=2))
    return 0


def cmd_add_comment(config: Config, args: argparse.Namespace) -> int:
    content = args.content
    if content is None:
        content = sys.stdin.read()
    content = (content or "").strip()
    if not content:
        raise YunxiaoError("评论内容为空，请通过 --content 或 stdin 提供")
    outcome = add_defect_comment(
        config, args.workitem_id, content, dry_run=args.dry_run
    )
    print(json.dumps(outcome, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    args = parse_args()
    try:
        config = load_config()
    except YunxiaoError as exc:
        print(f"[配置错误] {exc}", file=sys.stderr)
        return 2

    try:
        if args.command == "validate":
            return cmd_validate(config)
        if args.command == "list-states":
            return cmd_list_states(config, args)
        if args.command == "list":
            return cmd_list(config, args)
        if args.command == "detail":
            return cmd_detail(config, args)
        if args.command == "update-status":
            return cmd_update_status(config, args)
        if args.command == "add-comment":
            return cmd_add_comment(config, args)
    except YunxiaoError as exc:
        print(f"[云效错误] {exc}", file=sys.stderr)
        return 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
