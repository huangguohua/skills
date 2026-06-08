# Codex 同线程复核提示词模板（--resume）

> 修复后续用同一 codex 线程：`codex:rescue --resume`，让它保留上一轮上下文。

```
--resume Re-review <文件/方法> after my follow-up fix for your <编号/标题> finding:
<说明你怎么改的，对应它哪条问题>.

Regarding your other findings:
- <编号>: <为什么是既有设计/有意为之，请其确认 RESOLVED>;
- <编号>: <同上>.

Please verify the fix is correct, confirm no new issue was introduced by the change,
and state whether ALL blocking (HIGH/MEDIUM) issues are now resolved (CLEAR).
```

## 要点
- 开头 `--resume`，命中已有线程。
- 对**已修的**：说清改法对应哪条 finding。
- 对**判定为既有设计的**：给理由请它确认，别默默跳过。
- 结尾要它**明确给 CLEAR 与否**，作为放行判据。
- 超过 `config.review.max_rounds` 仍未 CLEAR：停下，分歧点交用户。
