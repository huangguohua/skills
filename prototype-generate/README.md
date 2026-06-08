# Prototype Generate Skill

基于需求与设计基线，分阶段生成 ui-design.html 交互演示稿和 .pen 高保真设计稿。

## 快速开始

### 1. 前置条件

```
specs-mcp/<feature-name>/requirements.md         ← 已确认
specs-mcp/<feature-name>/prototype.md            ← 已确认
specs-mcp/<feature-name>/ui-design-baseline.md   ← 已确认
```

### 2. 触发 Skill

```
"出交互稿"
"生成 HTML 原型"
"出高保真设计稿"
"基线已确认出原型"
```

### 3. 输出

```
specs-mcp/<feature-name>/ui-design.html              ← Phase 2
specs-mcp/<feature-name>/ui-design-{page-key}.pen    ← Phase 3
specs-mcp/<feature-name>/ui-design-notes.md          ← 降级时
```

---

## 阅读顺序

1. **SKILL.md** — 完整工作流（3 Phase）
2. **references/gotchas.md** — 常见错误，必读
3. **项目设计基线文件**（`config.design_system.*` 指向） — 必读
4. **references/domain-rules.md** — HTML 与 .pen 产出规则
5. 其余文件按需查阅

---

## 与其他 Skill 的关系

```
ui-design-baseline
    ↓ 输出 ui-design-baseline.md
prototype-generate（本 Skill）
    ↓ Phase 2: ui-design.html → 闸门 1: 用户确认
    ↓ Phase 3: .pen 设计稿 → 闸门 2: 用户确认
architect-design
    ↓ 技术设计
...（后续阶段）
```

---

## 数据库查询方式

```
工具名：mcp__{config.database.mcp_server}__execute_sql
参数：{"query": "SELECT ..."}
```

详见 `references/api.md`。
