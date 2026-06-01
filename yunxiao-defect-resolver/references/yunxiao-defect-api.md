# 云效缺陷 OpenAPI 接口约定

> 鉴权头与组织/项目环境变量与姊妹 Skill `yunxiao-workitem-creator` 完全一致。
> 这份文档只列出本 Skill 用到的「缺陷相关」接口约定。

## 鉴权

- 请求头：`x-yunxiao-token: <PAT>`
- 获取当前用户：`GET /oapi/v1/platform/user`
  - 用于 `validate` 子命令；不可用即 token 失效

## 缺陷工作项类型

云效里"缺陷"本质上是 `category=Bug` 的工作项类型。

- `GET /oapi/v1/projex/organizations/{orgId}/projects/{projectId}/workitemTypes?category=Bug`
- 返回数组，每项含 `id` 与 `name`。本 Skill 默认匹配 `name=缺陷`，可通过 `YUNXIAO_BUG_TYPE_NAME` 覆盖。

## 工作流状态映射

按工作项类型查工作流状态字典（id ↔ 中文名）：

- `GET /oapi/v1/projex/organizations/{orgId}/projects/{projectId}/workitemTypes/{workitemTypeId}/workflowStatuses`
- 返回数组（或包裹在 `{workflowStatuses: [...]}` 的对象里，本脚本两种都兼容）
- 每项含：
  - `id` 状态 ID（提交工作项更新时使用）
  - `name` 状态中文名
  - `category` / `stageCategory` 状态阶段分类（TODO/DOING/DONE 之类），可选

如果实际返回结构与上述路径不一致，可能是接口版本差异。修正点：
- 脚本里 `fetch_workflow_states` 函数
- 大概率改成 `.../workflowStages` 或带 `:list` 后缀

## 缺陷列表搜索

- `POST /oapi/v1/projex/organizations/{orgId}/workitems:search`
- 请求 body：
  ```json
  {
    "spaceId": "<projectId>",
    "workitemTypeId": "<bug workitem type id>",
    "statusStageIds": ["<state id 1>", "<state id 2>"],
    "pageSize": 50,
    "pageNumber": 1,
    "assignedTo": "<可选 user id>"
  }
  ```
- 响应里数组键名可能是 `workitems` / `list` / `records` / `data`，脚本依次尝试

字段过滤可能不止 `statusStageIds`，云效部分接口用 `statusIds`。如果跑通后发现状态过滤未生效，按响应里的实际字段名调脚本里 `fetch_defect_list` 的 body。

## 缺陷详情

- `GET /oapi/v1/projex/organizations/{orgId}/workitems/{workitemId}`
- 返回完整工作项对象，包含：
  - `subject` 标题
  - `description` / `descriptionHtml` 详细描述
  - `attachments` 附件列表
  - `assignedTo` / `creator` / `participants`
  - `statusStageId` / `statusStageName` 当前状态
  - `spaceId` / `workitemTypeId` 上下文
  - `priority`

## 状态推动

- `PUT /oapi/v1/projex/organizations/{orgId}/workitems/{workitemId}`
- body：
  ```json
  {
    "statusStageId": "<目标状态 id>"
  }
  ```
- 如果项目工作流配置了"流转规则"（如必须先到「处理中」才能到「已解决」），直接推到「已解决」会被拒。响应里会带 `transition not allowed` 类提示。
- 解决方式：
  1. 让用户在云效项目里把规则放开
  2. 或者本 Skill 改成走中间态：先推「处理中」再推「已解决」（按需扩展 update-status 子命令支持 `--via` 参数）

## 追加评论

- `POST /oapi/v1/projex/organizations/{orgId}/workitems/{workitemId}/comments`
- body：
  ```json
  {
    "content": "<纯文本或 Markdown>"
  }
  ```
- 部分接口版本要求 `contentType: "text/markdown"` 或 `format: "markdown"`，跑通时观察返回是否含纯文本警告决定是否补字段。

## 路径不确定项 — 首次跑时需要确认

下列接口路径基于云效 v1 OpenAPI 通用结构推测，**首次跑通时如果 404 / 字段不对，请按返回 detail 调整**：

| 接口 | 不确定点 |
|---|---|
| workflowStatuses | 可能叫 `workflowStages` / `statuses` |
| workitems:search | 可能是 `workitems/search` 或 `workitems:list` |
| 状态字段 | body 字段名可能是 `statusStageIds` / `statusIds` / `statusStageId`（更新接口） |
| 评论接口 | body 字段名可能是 `content` / `commentContent` / `body` |

修正点都集中在 `scripts/yunxiao_defects.py` 顶部到下面这几个函数：
- `fetch_workflow_states`
- `fetch_defect_list`
- `update_defect_status`
- `add_defect_comment`

每个函数都在 docstring 标了出处。

## 官方文档锚点

云效开发者文档主页：
- https://help.aliyun.com/zh/yunxiao/developer-reference/

常用接口（与姊妹 Skill 一致）：
- GetUserByToken
- ListWorkitemTypes
- CreateWorkitem
- UpdateWorkitem
- ListWorkitemWorkFlowStatus（如有）
- SearchWorkitems（如有）

首次跑通脚本时，建议同时打开云效文档对照 JSON 响应字段名。
