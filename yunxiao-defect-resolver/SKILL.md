---
name: yunxiao-defect-resolver
description: 阿里云云效缺陷处理 Skill。单条循环模式：拉一条「待处理 / 再次打开」缺陷 → 让 Claude 定位代码并修复 → 调 codex:rescue 做独立 review → review 通过则把云效缺陷状态推到「已解决」并追加包含 commit 摘要与 review 结论的评论。用户提到"修云效缺陷 / 拉缺陷修复 / 处理云效 bug / 推 bug 状态 / 解决缺陷"等场景时使用本 Skill。不要批量整批跑，每条之间必须等待用户说「继续」。
compatibility:
  tools: Read, Write, Edit, Bash, Agent
  dependencies: 可用的云效 PAT、组织 ID、项目 ID；本机能跑 codex:rescue
---

# 云效缺陷修复闭环 Skill

> 技术栈无关。整目录复制到任意项目后，只改 `config.json`（项目信息）+ `export YUNXIAO_TOKEN`（PAT 密钥）即可用。安装见同目录 `README.md`。

## 核心目标

按「单条循环 + 用户继续闸门」模式处理云效缺陷：

1. 拉取项目下「待处理 / 再次打开」状态的缺陷列表
2. 对其中**一条**缺陷：
   - 读详情（标题、复现步骤、附件）
   - Claude 定位代码 → 修复 → 本地验证（编译/单测）
   - 调 `codex:rescue` 做 second-opinion review
   - review 通过：commit → 把云效缺陷状态推到「已解决」 → 追加云效评论
3. 等用户明确说「继续」再拉下一条

绝不允许批量执行整批缺陷。每条结束后必须停下来等用户指令。

## 何时使用

用户说以下任一句，就走本 Skill：

- "修云效缺陷" / "处理云效 bug"
- "拉一条缺陷" / "拉缺陷列表"
- "把这个 bug 改成已解决"
- "推动 bug 状态" / "解决缺陷"

如果用户只是问"云效有什么 bug"——只跑 `list-states` + `list`，不进入修复流程。

## 固定输入

凭据与项目信息分两类来源，脚本读取优先级：**命令行参数 > 环境变量 > config.json > 内置默认**。

1. **PAT 密钥（环境变量，必填，绝不写进 config.json）**
   - `YUNXIAO_TOKEN`：云效个人访问令牌（PAT）。只从环境变量读，不落库。

2. **项目配置（`config.json` 的 `yunxiao` 段，可被同名环境变量覆盖）**

   | config.json 键 | 环境变量 | 必填 | 默认 |
   |---|---|---|---|
   | `organization_id` | `YUNXIAO_ORG_ID` | 是 | — |
   | `project_id` | `YUNXIAO_PROJECT_ID` | 是 | — |
   | `base_url` | `YUNXIAO_BASE_URL` | 否 | `https://openapi-rdc.aliyuncs.com` |
   | `bug_type_name` | `YUNXIAO_BUG_TYPE_NAME` | 否 | `缺陷` |
   | `todo_state_names` | `YUNXIAO_DEFECT_TODO_STATES` | 否 | `待处理,再次打开` |
   | `resolved_state_name` | `YUNXIAO_DEFECT_RESOLVED_STATE` | 否 | `已解决` |
   | — | `YUNXIAO_HTTP_TIMEOUT_SECONDS` | 否 | `120` |

   首次接入新项目：把 `config.json` 里的占位值（形如 `<your-org-id>`）改成你项目的真实值，并 `export YUNXIAO_TOKEN=...`。状态名若与你项目不同（如「待修复」「重新打开」），第 1 步 `list-states` 会暴露真实状态名，按需改 `config.json`。

脚本入口：`scripts/yunxiao_defects.py`

## 执行流程（强制顺序）

### 第 1 步：鉴权 + 状态映射对齐

```bash
python skills/yunxiao-defect-resolver/scripts/yunxiao_defects.py validate
python skills/yunxiao-defect-resolver/scripts/yunxiao_defects.py list-states \
  --output /tmp/yunxiao-defect-states.json
```

`list-states` 输出包含：
- 项目下 `category=Bug` 的工作项类型 `id + name`
- 该工作项类型的全部工作流状态（id ↔ name 映射）
- `todoStateNames` / `resolvedStateName` 当前配置

**必须把 `states` 数组完整打到运行日志里**，让用户人眼确认本项目实际状态名与配置值是否对得上。
如果项目状态名与配置不同，让用户改 `config.json`（或用环境变量覆盖）后重跑本步。

### 第 2 步：拉一条缺陷

```bash
python skills/yunxiao-defect-resolver/scripts/yunxiao_defects.py list \
  --limit 50 \
  --output /tmp/yunxiao-defects.json
```

输出后取 `defects` 数组**首条**作为本轮目标。把 id + 标题告诉用户。

如果命中数为 0，直接告诉用户「没有待处理/再次打开的缺陷」，结束。
如果命中数 > 1，告诉用户总数，但只处理第一条；其余等用户说「继续」时下一轮再处理。

### 第 3 步：拉详情 + 定位代码

```bash
python skills/yunxiao-defect-resolver/scripts/yunxiao_defects.py detail \
  --workitem-id <id> \
  --output /tmp/yunxiao-defect-<id>.json
```

读详情里关键字段：
- `subject` / `title` 缺陷标题
- `description` / `descriptionHtml` 复现步骤、期望结果、实际结果
- `attachments` 附件元数据（截图 URL 等）
- `assignedTo` / `creator` 当前负责人
- `priority` 优先级

按描述里的功能点和报错关键字定位代码（grep / Explore agent）。
**先把定位结论告诉用户再动手改代码**——避免改错文件。

### 第 4 步：修复 + 本地验证

按**本项目的编码规范**修复，并做与改动相称的本地验证：
- 后端：编译 + 相关单测（按项目构建工具而定，如 Maven `mvn -pl <module> -am compile -DskipTests` / Gradle / npm 等）
- 前端：检查模板/脚本语法，必要时跑 lint / 构建
- 涉及数据库或配置变更：先对照项目的设计文档与发布手册确认影响面与发布顺序

> 具体编译命令、技术栈与文档路径取决于目标项目，由该项目自身的工程规范约定，本 Skill 不写死。

修完不要立刻 commit，先进入 review。

### 第 5 步：调 codex:rescue 做 second-opinion review

通过 `Skill` 工具调起 `codex:rescue`，把以下 4 项上下文带过去：

1. 云效缺陷标题 + 描述（截图原文）
2. 改动文件清单 + 改动摘要
3. `git diff` 关键 hunk
4. 本地验证结果（编译输出 / 测试输出 / 截图描述）

明确请求 codex 检查：
- 改动是否真的修了用户报告的现象
- 有没有引入新的回归（命名冲突、null pointer、状态机漏分支等）
- 是否有边界条件遗漏

把 codex 的结论原文回贴给用户。

### 第 6 步：闸门 — 让用户确认 review 结论

- codex 说"无阻断问题" → 继续第 7 步
- codex 提出新问题 → 回到第 4 步修，循环直到 review 通过
- codex 说"严重缺陷"或推翻方向 → 把判定告诉用户，等用户决定是不是要重新设计

**绝不允许跳过 review 直接 commit/改状态。**

### 第 7 步：commit + 推动云效状态

按**本项目的提交规范** commit（下面是一个通用示例，scope/语言以项目约定为准）：

```
fix(<scope>): <72 字符内摘要>

<可选 body>

Co-Authored-By: Claude <noreply@anthropic.com>
```

commit 完成后，把缺陷状态推到「已解决」（默认）：

```bash
python skills/yunxiao-defect-resolver/scripts/yunxiao_defects.py update-status \
  --workitem-id <id> \
  --state "已解决"
```

首次跑可以加 `--dry-run` 看下 payload 再实际推。

### 第 8 步：追加云效评论

把 commit 摘要 + review 结论拼成一段，追加到云效缺陷评论：

```bash
python skills/yunxiao-defect-resolver/scripts/yunxiao_defects.py add-comment \
  --workitem-id <id> \
  --content "$(cat <<'EOF'
本轮修复 commit:
  - <repo>: <sha7> <commit subject>

修复要点:
  - <一句话总结改动落点>

codex:rescue 结论:
  - <粘贴 codex 给出的关键句>

本地验证:
  - <编译/测试/手动验证摘要>
EOF
)"
```

### 第 9 步：等用户「继续」

向用户汇报本条处理完成（缺陷 id、commit sha、新状态）。
**停下来。**等用户说「继续」/「下一条」再回到第 2 步处理下一条。

如果用户没说继续，本 Skill 完成。

### 第 10 步（可选）：CI/CD 流水线部署

> 仅当目标项目使用**云效 Flow 流水线**、且用户明确要求「发起流水线 / 部署」时适用。这是不可回退的对外动作，触发前必须满足全部闸门。属于项目专有高级用法——`config.json` 的 `pipelines` 未配置（仍是占位符）时**跳过本步**。

**强制前置闸门：**

1. **人工确认代码已合并到目标分支/环境**：用户必须明确告知「已合并」。Claude 不自行判断合并状态，也不替用户合并。
2. **本次缺陷无 DB/配置中心变更**，或相关变更已按目标项目的发布手册顺序（如 DB DDL → 配置中心 → 后端 → 前端）先行落地。纯展示层/逻辑改动可直接走部署流水线。
3. **触发前必须先 GET 校验流水线存在且名字对得上**，再 POST 运行。绝不凭名字猜数字 ID。

**流水线信息从 `config.json` 的 `pipelines` 段读取（勿硬编码）：**

| 用途 | config.json 键 |
|---|---|
| 后端 | `pipelines.backend.name` / `pipelines.backend.id` |
| 前端 | `pipelines.frontend.name` / `pipelines.frontend.id` |

**云效 Flow OpenAPI（与缺陷脚本同一套 `x-yunxiao-token` 鉴权 + 同一 base_url）：**

```bash
BASE="${YUNXIAO_BASE_URL:-https://openapi-rdc.aliyuncs.com}"

# 1. 校验流水线（触发前必做；{pid} 必须是数字 Long）
curl -s -H "x-yunxiao-token: $YUNXIAO_TOKEN" \
  "$BASE/oapi/v1/flow/organizations/$YUNXIAO_ORG_ID/pipelines/{pid}"

# 2. 运行流水线（校验通过后才执行）
curl -s -X POST -H "x-yunxiao-token: $YUNXIAO_TOKEN" -H "Content-Type: application/json" \
  "$BASE/oapi/v1/flow/organizations/$YUNXIAO_ORG_ID/pipelines/{pid}/runs" -d '{}'
```

发布顺序：按项目依赖关系（如**先后端、确认后端起来再前端**，前端依赖后端 API）。每条触发后把 run 结果/链接回报用户，不替用户判断部署成功。

> ⚠️ **已知坑**：
> - `{pid}` 路径参数必须是**数字** pipelineId（如 `4983557`）。云效流水线**页面 URL 里的字母数字短串**（如 `lrd1t4sj3ef78ah7`）**不是** API 用的 ID，直接 POST 会报 `NumberFormatException: For input string`。需到流水线设置/“运行历史”里取数字 ID，或让用户提供。
> - PAT 必须具备对应流水线的 **Flow 运行权限**；缺陷工作项用的 PAT 不一定有。`GET /oapi/v1/flow/.../pipelines` 列不到目标流水线 = 无可见/运行权限，此时**不要尝试触发**，改由用户在云效流水线页面点「运行」，或换有权限的 token。

## 闸门清单（不可越过）

| 阶段 | 闸门 |
|---|---|
| 第 1 步 | 状态映射必须打到日志；项目状态名与配置不一致时必须先改 config.json/环境变量再继续 |
| 第 3 步 | 代码定位结论先告诉用户再动手 |
| 第 6 步 | codex:rescue 未给出"无阻断"结论前禁止 commit / 改状态 |
| 第 9 步 | 单条结束后必须停，禁止自动进入下一条 |
| 第 10 步 | 用户未明确「已合并」前禁止触发流水线；触发前必须 GET 校验流水线（数字 ID）；列不到/无权限不得强行触发 |

## 失败与回退

立即停止并报告，不要试图绕过：

- `validate` 报 `InvalidToken` → token 失效，让用户重新生成 PAT
- `list-states` 返回结构与预期不符 → 按 references 调脚本里 path
- `list` 命中 0 条 → 报告"无待处理缺陷"后退出
- 改了代码但编译/单测失败 → 让用户决定是回滚还是继续修
- `codex:rescue` 持续 2 轮仍判定有问题 → 把现状给用户，等用户决策
- `update-status` 404 / 状态流转拒绝 → 大概率是状态名不存在或流转规则禁止；不要伪造成功，把响应原文给用户
- 流水线 GET/POST 返回 `NumberFormatException` → `{pid}` 不是数字 ID，让用户给数字 pipelineId
- 流水线 GET 返回 403 / 列表里看不到目标流水线 → PAT 无 Flow 权限；不要绕过，让用户在云效页面运行或换 token

## 约束

- 严禁批量并行处理多条缺陷
- 严禁在 commit message / 评论 / 日志里输出 PAT 原文
- 严禁把 PAT 写进 config.json（config.json 会进版本库）；PAT 只走 `YUNXIAO_TOKEN` 环境变量
- 严禁跳过 codex:rescue 直接改状态
- 评论里如果涉及内部敏感信息（用户手机号、密钥等），先脱敏再上传

## 参考资料

- `references/yunxiao-defect-api.md` 缺陷相关 OpenAPI 接口约定
- 云效 OpenAPI 官方文档：https://help.aliyun.com/zh/yunxiao/developer-reference/
