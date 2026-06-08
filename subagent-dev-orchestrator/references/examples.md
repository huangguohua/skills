# 示例：单个任务的完整内循环

> 场景：feature `coupon-center`，tasks.md 中的 `T3 优惠券领取接口`。

## 1. 主会话开子 agent 实现（Agent 工具）

```
subagent_type: general-purpose
prompt:（按 assets/subagent-task-prompt-template.md 填充）
  任务 T3：优惠券领取接口
  目标：POST /api/coupon/claim，幂等领取，库存扣减
  验收：见 tasks.md T3 验收标准
  契约：见 design.md §4.2（请求/响应字段、错误码）
  代码库：<后端代码库路径>（如 Spring Boot + MyBatis-Plus）
  规范：doc/development/coding-standards.md、backend-gotchas.md
  边界：只实现 T3；完成后汇报改动文件清单与关键决策。
```

子 agent 返回："新增 CouponClaimController / CouponClaimService / mapper xml；改了 CouponMapper。幂等用 user_id+coupon_id 唯一键 + 乐观锁扣库存。"

## 2. 主会话调 codex:rescue 复审（Agent 工具，subagent_type "codex:codex-rescue"）

```
prompt:（按 assets/codex-review-prompt-template.md 填充）
  只读复审，不要修改代码。聚焦本次改动：
    CouponClaimController.java / CouponClaimService.java / CouponMapper.xml / CouponMapper.java
  对照 design.md §4.2 契约与 doc/development/backend-gotchas.md。
  逐条输出：问题 + 级别(P0/P1/P2) + 文件:行 + 修复建议。
```

codex 返回：
- **P1** `CouponClaimService.java:58` 乐观锁更新未校验受影响行数，库存可能超扣 → 应判断 update 返回值。
- **P2** `CouponClaimController.java:31` 入参未加 `@Validated`，建议补充。

## 3. 判定 → 有 P1 → SendMessage 回传同一子 agent 修复

```
SendMessage → 子 agent A：
  codex 复审发现：
  [P1] CouponClaimService.java:58 乐观锁未校验受影响行数，会超扣，请判断 update 返回值并在 0 时抛领取失败。
  [P2] 入参建议加 @Validated（本轮可一并修）。
  请逐条修复并说明改法。
```

子 agent 修复并回报："已在扣库存处判断 affectedRows==0 抛 CouponSoldOutException；Controller 已加 @Validated。"

## 4. 回到 codex 复审

codex 返回："未发现 P0/P1 问题。"（P2 已清）→ **通过**。

## 5. 收口

- 更新 `CHANGELOG.md`：T3 完成，codex 复审 2 轮通过，无遗留 P2。
- 写 `logs/2026-05-31_coupon-center_task3.md`。
- TaskUpdate T3 → completed。进入 T4。
