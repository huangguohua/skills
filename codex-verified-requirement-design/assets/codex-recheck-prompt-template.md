# Codex 同线程复核提示词模板（--resume）

> 修订需求后续用同一 codex 线程：`codex:rescue --resume`，让它保留上一轮上下文。

```
--resume Still a REQUIREMENTS DOCUMENT review (not code). I revised the spec per your findings:

Fixed (blocking):
- <你的编号/标题> → 对应功能 <Fn> / 章节，我怎么改的：<一句话>;
- <编号> → <同上>.

Regarding findings I did NOT change:
- <编号>: 这是有意收窄 / 属 Out of Scope，理由：<…>，请确认可标记 RESOLVED;
- <编号>: <同上>.

Please re-review the revised spec, confirm no new gap was introduced by the revision,
and state whether ALL blocking (HIGH/MEDIUM) issues are now resolved (CLEAR).
```

## 要点
- 开头 `--resume`，命中已有线程，并**重申"需求文档评审"**（resume 后 codex 可能忘记定调）。
- 对**已改的**：说清改法对应哪条 finding、哪个功能编号。
- 对**判定为 Out of Scope / 有意收窄的**：给理由请它确认，别默默跳过。
- 结尾要它**明确给 CLEAR 与否**，作为放行判据。
- 超过 `config.review.max_rounds` 仍未 CLEAR：停下，分歧点交用户。
