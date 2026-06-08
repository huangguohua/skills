# Codex 复审提示词模板（首轮）

> 通过 `codex:rescue` 触发，内部转发到 `Agent(subagent_type:"codex:codex-rescue")`。
> 禁止 `Skill(codex:rescue)`。把下面填好的整段作为 prompt 传入。

```
Review my change to <文件路径> in <方法/范围>.

Background: <一句话缺陷或需求>. <根因或需求边界，含触发条件/数据佐证>.

My change: <逐条说明改了什么、为什么>.

Please review for correctness, concurrency/transaction safety, and edge cases.
Rank findings as HIGH / MEDIUM / LOW / SUGGESTION.
Only review THIS change; do not make unrelated edits or suggest broad refactors.
```

## 要点
- **背景**：让 codex 知道原始问题和你的根因判断，复审才能对准"根因是否真消除"。
- **改动清单**：逐条列，范围越窄越好。
- **分级要求**：明确 HIGH/MEDIUM/LOW/SUGGESTION，便于按阻塞线（HIGH+MEDIUM）决策。
- **约束范围**：only review this change，避免它发散去提无关重构。
