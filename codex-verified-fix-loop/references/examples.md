# Example — 优惠券锁缺陷的完整内循环

真实案例，展示本 Skill 五个阶段如何串起来。

## 诉求
> "3245 用户今天支付失败了，找出错误日志并排查修复。"

## ① 定位（查日志 + 查 DB MCP + 读代码）

1. SSH 拉生产日志（`config.diagnostics.prod_log_access`），`grep -n 3245 | grep 支付` 锁定行号。
2. `awk` 取下单时间窗，去色码后读到：`ERROR PayServiceImpl - 创建支付订单异常: BadRequestException: 该券不可使用`。
3. `grep -rn "该券不可使用"` 定位到 `CouponUserServiceImpl.calculateDiscountWithOwnerCheck`（状态非 AVAILABLE 即抛）。
4. 读状态机 SQL：`tryReserveCoupon` 把券 `AVAILABLE→LOCKED`，惰性释放 `releaseExpiredLocks` **只在查券列表接口触发**。
5. MCP 查 `coupon_user`：该用户 3 张券全卡 `LOCKED`、`order_id` 为空 → **根因**：用户反复点支付，自己上一笔未付订单锁住券，下单路径无惰性释放兜底，陷入"该券不可使用"死循环。

→ 与用户对齐根因后再改。

## ② 实施改动（最小改动）

`calculateDiscountWithOwnerCheck` 入口加 `releaseExpiredLocks(userId, LOCK_TTL_MINUTES)` 自愈过期锁；
`LOCKED` 返回友好文案"该券有未完成的订单，请稍后再试"，其他非 AVAILABLE 保留"该券不可使用"。

## ③ codex 复审

`Agent(subagent_type:"codex:codex-rescue")`，给背景+根因+改动，要求只审本次改动、按 HIGH/MEDIUM/LOW/SUGGESTION 分级。
→ 返回：无 HIGH；MEDIUM×2（TTL>支付窗口保证、批量释放副作用）；LOW×2（其一：非本人 LOCKED 券会误报"有未完成订单"）。

## ④ 修复 + 同线程复核

- 判定 MEDIUM 两项为既有设计（TTL=15>窗口5 有文档；批量释放与查询接口一致）→ 回传说明请其确认。
- 修 LOW#2：把券归属校验提前到状态分支之前。
- `codex:rescue --resume` 复核 → 返回 **CLEAR**：LOW#2 已正确修复、未引入新问题、MEDIUM 两项确认 RESOLVED、无开放 HIGH/MEDIUM。

## ⑤ 收尾

- 写循环日志（根因 / 改动 / 两轮 codex 结论 / 无遗留阻塞）。
- 按 `config.handoff` 提示下游：编译通过 → package 测试通过 → （用户授权后）发布生产并健康检查 HTTP 200。
- 生产脏数据（3 张卡死的券）由用户执行 SQL 放回 AVAILABLE，附回滚预案。

## 关键点回顾
- 根因 ≠ 表象：报错是"该券不可使用"，根因是"锁未释放 + 下单路径无兜底"。
- codex 的"既有设计"提点要回传确认，不默默忽略。
- 复核走 `--resume` 同线程，codex 记得上一轮结论，省一轮上下文重建。
