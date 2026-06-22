# 实例：App 会员到期推送 —— 需求设计 codex 复审循环

> 一个完整的内循环走查，演示 codex 如何把需求从"漏洞百出的草稿"逼到 CLEAR。

## 诉求
"新 RN App 要做会员到期推送提醒，到期前提醒用户续费。"

## ① 现状对齐
- DB MCP(tools_db) 查 `user_membership`：有 `end_time`，无"是否试用"独立标记 → 试用会员判断走 `is_trial`。
- grep 后端：已有 `JPushSenderServiceImpl`（统一 Android/iOS 推送），`push_send_log` 表已建。
- 现有：极光通道已通；**无**"推送开关设置页"，**无**到期扫描定时任务。
- In Scope：到期前 N 天扫描 + 触达 + 点击 deeplink 落地续费页。
  Out of Scope：站内信、短信兜底（本期不做）。
- 用户确认：高风险点（推送频控、试用是否提醒）已对齐。

## ② 产出 requirements.md（草稿）
按模板写 F1 到期扫描、F2 推送触达、F3 点击落地，含字段与验收。

## ③ codex 首轮复审（按需求维度）
| 维度 | 级别 | 命中（标注功能编号） |
|---|---|---|
| 完整性 | HIGH | F1 未定义"已续费用户在扫描窗口内是否重复推送"——缺幂等/去重规则 |
| 完整性 | MEDIUM | F2 未覆盖"用户关闭了系统通知权限"的空状态 |
| 一致性 | MEDIUM | F1 说"到期前3天"，F3 验收写"到期前7天"，自相矛盾 |
| 可实现性 | HIGH | F1 假设了 `membership.notified` 字段，DDL 实测不存在 |
| 可测试性 | LOW | F2 验收"尽快送达"不可度量 |
| 范围 | SUGGESTION | F2 写了 JPush 的 channel_id 参数（属 architect-design） |

## ④ 修订 + 同线程复核
- 修 HIGH/MEDIUM：补 F1 去重规则（按 `push_send_log` 当日去重）、补 F2 通知权限关闭空状态、统一为"到期前3天"、
  去掉对不存在字段的假设（改为"以 push_send_log 是否已发判断"）。
- LOW 顺手改"尽快送达"→"触发后5分钟内下发"。
- SUGGESTION（channel_id）：回传说明"属接口实现细节，已移交 architect-design，本需求 Out of Scope"，请 codex 确认 RESOLVED。
- `--resume` 复核 → codex 确认无 HIGH/MEDIUM = **CLEAR**。

## ⑤ 放行
- requirements.md 标记 CLEAR 定稿；日志写入 requirement-review-loop.md。
- 下游提示：可进 ui-design-baseline（推送开关页 UI）+ architect-design（扫描任务/接口/channel_id）。

## 复盘
- 价值最大的是 codex 抓出的两个 **HIGH**：重复推送幂等、假设了不存在的字段——这正是人工一次成稿最常漏的两类。
- 五维度里 **完整性**（异常流/幂等）和 **可实现性**（对齐真实 DDL）命中率最高，是需求阶段的主要质量风险。
