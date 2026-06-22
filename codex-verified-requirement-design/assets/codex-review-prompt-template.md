# Codex 需求复审提示词模板（首轮）

> 通过 `codex:rescue` 触发，内部转发到 `Agent(subagent_type:"codex:codex-rescue")`。
> 禁止 `Skill(codex:rescue)`。把下面填好的整段作为 prompt 传入。
> **关键**：codex 默认偏代码审查，开头必须显式声明"这是需求文档评审，不要评代码"。

```
This is a REQUIREMENTS DOCUMENT review, NOT a code review. Do not review code, do not
suggest code edits. Evaluate the requirement spec for quality only.

Document under review: <specs-mcp/<feature>/requirements.md 全文，或路径>

Background & current-system constraints (already verified):
<① 阶段的需求边界对齐结论：In/Out of Scope、相关真实表/字段、现有接口、复用/改造/新增判断>

Please review the requirement spec across these dimensions and rank each finding as
HIGH / MEDIUM / LOW / SUGGESTION. For every finding, cite the specific feature id (F1…)
or section it refers to:

1. 完整性 Completeness — missing exception flows, empty/null states, permission denial,
   over-limit/concurrency branches, or undefined data semantics?
2. 一致性 Consistency — internal contradictions, inconsistent terminology, or conflicts
   with the stated current-system constraints / confirmed discovery?
3. 可实现性 Feasibility — does it assume fields/interfaces that do not exist, or depend on
   something unavailable given the constraints above?
4. 可测试性 Testability — are acceptance criteria measurable and executable, or do they use
   vague words ("尽量/更好/快速") that cannot be verified?
5. 范围 Scope — over-engineering, or out-of-scope content such as API contracts, DDL types,
   indexes, UI layout/colors, or tech-stack choices that belong to later phases? Any In-Scope
   item missing?

Only review THIS document. Do not invent new features beyond the stated scope.
```

## 要点
- **首句定调**：明确"需求文档评审，非代码评审"，否则 codex 会去找代码。
- **喂现状约束**：把 ① 阶段查到的真实表/字段/接口结论给它，它才能判"可实现性/一致性"。
- **五维度 + 分级**：对齐 `config.review.dimensions`，要求 HIGH/MEDIUM/LOW/SUGGESTION 并标注功能编号。
- **约束范围**：only review this document，避免它自行扩写需求或评下游 API/UI。
