# UI Design Baseline Skill

定义本次需求的视觉与交互基线，明确 page-key、组件规范、状态集合，对齐 AD 管理端设计语言。

## 快速开始

### 1. 前置条件

```
specs-mcp/<feature-name>/requirements.md    ← 已确认
specs-mcp/<feature-name>/prototype.md       ← 已确认
business-requirement-review 已通过
```

### 2. 触发 Skill

```
"定设计基线"
"统一这批页面的设计规则"
"给 UI 建立统一规范"
```

### 3. 输出

```
specs-mcp/<feature-name>/ui-design-baseline.md
```

---

## 阅读顺序

1. **SKILL.md** — 完整工作流（8 步）
2. **references/gotchas.md** — 常见错误，必读
3. **项目设计基线文件**（`config.design_system.*` 指向） — 必读
4. **references/domain-rules.md** — page-key 命名规则、状态矩阵规则
5. 其余文件按需查阅

---

## 与其他 Skill 的关系

```
business-requirement-review
    ↓ 评审通过
ui-design-baseline（本 Skill）
    ↓ 输出 ui-design-baseline.md
prototype-generate
    ↓ 输出 ui-design.html + .pen
...（后续阶段）
```

---

## 数据库查询方式

```
工具名：mcp__{config.database.mcp_server}__execute_sql
参数：{"query": "SELECT ..."}
```

详见 `references/api.md`。
