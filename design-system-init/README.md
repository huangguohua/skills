# Design System Init Skill

为项目初始化设计系统基线文件，从现有前端代码中提取视觉变量、组件规范和页面模板。

## 快速开始

### 1. 前置条件

- 项目有前端代码（SCSS/CSS/Vue/React 等）
- 或：新项目需要从零建立设计基线

### 2. 触发 Skill

```
"初始化设计系统"
"生成设计基线"
"提取设计变量"
```

### 3. 输出

```
doc/design-system/style-guide.md       ← 视觉基线
doc/design-system/component-rules.md   ← 组件规范
doc/design-system/page-templates.md    ← 页面模板
```

---

## 阅读顺序

1. **SKILL.md** — 完整工作流（7 步）
2. **references/gotchas.md** — 常见错误，必读
3. **references/domain-rules.md** — 提取规则
4. 其余文件按需查阅

---

## 与其他 Skill 的关系

```
design-system-init（本 Skill）
    ↓ 输出 style-guide.md + component-rules.md + page-templates.md
    ↓ 更新 shared-config.json design_system 配置
ui-design-baseline
    ↓ 读取项目设计基线
prototype-generate
    ↓ 遵循设计基线生成原型
```

---

## 适用场景

| 场景 | 做法 |
|---|---|
| 新项目接入 UI Skill | 运行本 Skill 生成基线，再运行 ui-design-baseline |
| 现有项目首次使用 | 从代码提取基线，用户确认后继续 |
| 切换 UI 组件库 | 重新运行本 Skill，生成新基线 |
| 新项目无前端代码 | 选择技术栈后生成最小可用基线 |
