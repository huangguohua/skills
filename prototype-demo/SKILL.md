---
name: prototype-demo
description: prototype-generate 生成拆分 HTML 后可随时调用。将多个按二级菜单/模块拆分的 `{feature-name}[-{module}][-H5].html` 原型文件，组装为可供业务方完整演示的单文件交互原型。后台端输出 DEMO-{feature-name}-admin.html，H5 端输出 DEMO-{feature-name}-mobile.html，统一放在 `specs-mcp/{feature-name}/` 目录下。触发场景：用户提到"组装原型"、"整合原型"、"合并HTML"、"原型演示"、"prototype assembly"、"把这些页面合成一个"、"做成可以演示的"时，务必使用此技能。不阻断主流程原型确认闸门。
triggers:
  - 组装原型
  - 整合原型
  - 合并 HTML
  - 原型演示
  - 做成可以演示的
  - 把这些页面合成一个
  - prototype assembly
---

# Prototype Demo Skill

**定位：原型组装器，不是生成器。**

本 Skill 是 `prototype-generate` 的**可选下游步骤**，在 prototype-generate 产出拆分 HTML 后随时可触发，不阻断原型确认闸门（闸门 ① HTML / 闸门 ② .pen）与后续 architect-design 流程。

**上游**：`prototype-generate`（产出多个 `{feature-name}[-{module}][-H5].html` 拆分文件，命名规范见 `prototype-generate/SKILL.md § 2.1`）

**输入**（当前需求目录 `specs-mcp/{feature-name}/`）：
- **管理端**：`{feature-name}-{module}.html`（文件名不含 `-H5`）
- **H5 / 小程序端**：`{feature-name}-{module}-H5.html`（文件名以 `-H5.html` 结尾）
- 排除已存在的 `DEMO-*.html`（本 Skill 自身历史输出）
- 排除一级总览 HTML（若存在 `{feature-name}.html` 无 module，按需询问用户是否包含）

**输出**（同目录，不新建子目录）：
- `DEMO-{feature-name}-admin.html` — 后台管理端统一演示稿（左侧菜单 + 顶栏面包屑 + 跨菜单页面跳转）
- `DEMO-{feature-name}-mobile.html` — 小程序端统一演示稿（375px 手机框 + NavBar + TabBar + 栈式路由）；**仅当存在至少一个 `-H5` 文件时输出**

核心工作是**结构整合 + 跨菜单交互串联**，原有页面的视觉设计和内容保持不变；保留每个页面节点的 `data-page="{page-key}"` 属性以便与 ui-design-baseline / .pen 对齐。

---

## 第一步：读取并分析输入文件

用户上传多个独立 HTML 原型文件后，执行以下分析：

```
1. 逐一读取所有 HTML 文件内容，识别每个页面的：
   - 页面名称 / 功能模块归属（从 <title>、<h1>、文件名推断）
   - 端类型（后台 admin / 移动端 mobile）—— 视口宽度、class命名、布局特征
   - 已有的跳转链接（<a href="*.html">、onclick、window.location）→ 组装连线依据
   - 页面层级关系（列表页 → 详情页 → 编辑页）

2. 输出组装方案摘要，供用户确认：
   - 后台端页面清单（模块分组 → 对应左侧菜单结构）
   - 移动端页面清单（TabBar 主页 + 二级/三级页面）
   - 识别到的跳转关系（哪个页面 → 哪个页面）
   - 无法识别归属的页面 → 请用户手动指定
   - 拟定的默认首页（admin / mobile 各一个）
```

> ⚠️ **确认后再组装**：输出摘要后等待用户确认，再进入组装阶段。组装过程**不修改原页面视觉内容**，只做结构整合和交互串联。

---

## 第二步：组装策略

### 整体架构（单文件多页面）

每个输入页面的 `<body>` 内容作为独立 `<section class="page">` 被嵌入，原有样式通过命名空间隔离后保留。两个输出文件各自采用**单文件多视图**架构：

```html
<!-- 所有"页面"以 <section> 或 <div> 存储在同一HTML中 -->
<!-- 通过 JS 控制 display:none / display:block 实现页面切换 -->
<!-- URL hash (#page-name) 记录当前页，支持浏览器前进/后退 -->
```

核心路由逻辑见 `scripts/router.js`（复制到 `<script>` 块内使用）。

### 后台管理端 (`_admin.html`) 布局规范

```
┌─────────────────────────────────────────────┐
│  顶部导航栏（Logo + 用户信息 + 全局操作）       │
├──────────┬──────────────────────────────────┤
│          │  面包屑导航                        │
│  左侧     ├──────────────────────────────────┤
│  菜单     │                                  │
│  (固定)   │        主内容区                   │
│          │        （各页面在此切换）           │
│          │                                  │
└──────────┴──────────────────────────────────┘
```

- 左侧菜单：一级模块可折叠，高亮当前页
- 顶部：固定，包含面包屑、用户头像、通知图标
- 内容区：带独立滚动条，不影响菜单

### 移动端 (`_mobile.html`) 布局规范

```
┌─────────────────────┐
│  顶部标题栏（可选返回）│
├─────────────────────┤
│                     │
│      主内容区        │
│  （各页面在此切换）   │
│                     │
├─────────────────────┤
│  底部 Tab 导航       │
└─────────────────────┘
```

- 宽度锁定为 375px，居中显示，外围加手机框装饰（可选）
- 顶部 NavBar：展示标题 + 返回按钮（栈式路由）
- 底部 TabBar：主导航模块（≤5个）
- 支持左滑/右滑手势切换（可选，见 `references/gesture.md`）

---

## 第三步：样式整合规范

组装时对各页面样式做最小化修正，确保嵌入后不冲突。Design Token 参考见 `references/design-tokens.md`，以下为核心规范：

### 后台端 Design Token
```css
/* 主色 */
--color-primary: #1677FF;       /* Ant Design Blue */
--color-primary-hover: #4096FF;
--color-success: #52C41A;
--color-warning: #FAAD14;
--color-error: #FF4D4F;

/* 中性色 */
--color-bg-base: #F5F7FA;
--color-bg-container: #FFFFFF;
--color-border: #E8E8E8;
--color-text-primary: #1D2129;
--color-text-secondary: #86909C;

/* 字体 */
--font-family: -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif;
--font-size-base: 14px;
--font-size-sm: 12px;
--font-size-lg: 16px;
--font-size-xl: 20px;

/* 圆角 / 阴影 */
--border-radius: 6px;
--shadow-card: 0 2px 8px rgba(0,0,0,0.08);
```

### 移动端 Design Token
```css
--color-primary: #1677FF;
--color-bg-page: #F2F3F5;
--color-bg-white: #FFFFFF;
--color-text-primary: #1D2129;
--color-text-secondary: #86909C;
--color-border: #E5E6EB;

--font-family: -apple-system, 'PingFang SC', sans-serif;
--font-size-base: 14px;
--font-size-sm: 12px;
--font-size-lg: 16px;

/* 移动端特有 */
--tab-bar-height: 50px;
--nav-bar-height: 44px;
--safe-area-bottom: env(safe-area-inset-bottom, 0px);
```

### 样式整合原则
1. **保留原样式**：各页面原有 CSS 全部保留，不重写
2. **命名空间隔离**：为每页样式加 `.page-{id}` 前缀，防止全局污染
3. **导航层独立维护**：菜单、NavBar、TabBar 使用统一 Design Token
4. **冲突处理**：若原页面有全局 body/reset 样式，限定在 `.page-{id}` 作用域内

---

## 第四步：交互逻辑整合

### 页面跳转规则

```javascript
// 统一跳转函数，替换所有原有 href / onclick
function navigate(pageId, params = {}) {
  // 1. 隐藏当前页
  // 2. 显示目标页
  // 3. 更新 URL hash
  // 4. 更新面包屑（admin）/ NavBar标题（mobile）
  // 5. 推入历史栈（mobile返回功能）
}
```

**处理原 HTML 中的跳转：**
- `<a href="xxx.html">` → 改为 `onclick="navigate('xxx')"`
- `window.location.href = 'xxx.html'` → 改为 `navigate('xxx')`
- `<a href="#xxx">` → 识别为锚点，保留或转换为 tab 切换

### 弹窗 / 抽屉 / Toast

- Modal 弹窗：使用统一的 `showModal(id)` / `closeModal(id)`
- 表单提交：拦截默认行为，显示 Success Toast 后跳转
- 删除确认：统一二次确认弹窗

### 数据 Mock

原型中的动态数据使用内联 JS 对象 Mock，不依赖后端：
```javascript
const MOCK_DATA = {
  userList: [...],
  orderList: [...],
  // ...
};
```

---

## 第五步：输出规范

### 文件命名与存放位置
```
specs-mcp/{feature-name}/
├── {feature-name}-{moduleA}.html        # prototype-generate 产出（管理端，不动）
├── {feature-name}-{moduleB}-H5.html     # prototype-generate 产出（小程序端，不动）
├── ...
├── DEMO-{feature-name}-admin.html       # ← 本 Skill 输出（管理端统一演示稿）
└── DEMO-{feature-name}-mobile.html      # ← 本 Skill 输出（仅存在 -H5 源文件时产出）
```

**与 prototype-generate 输出共存于同一 feature 目录**，不新建 `outputs/` / `doc/` 子目录。
**保留每个页面节点的 `data-page="{page-key}"`**，便于后续 .pen 文件按 page-key 对齐。

### 文件内部结构
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <!-- admin: viewport width=1440 -->
  <!-- mobile: viewport width=device-width, initial-scale=1, maximum-scale=1 -->
  <title>{项目名} {版本} {端} 原型</title>
  <style>
    /* 1. CSS Reset */
    /* 2. Design Tokens (CSS Variables) */
    /* 3. 全局布局 */
    /* 4. 导航组件（菜单/TabBar/NavBar）*/
    /* 5. 各页面样式（以 .page-{id} 为命名空间） */
    /* 6. 公共组件（Modal, Toast, Table, Form...） */
  </style>
</head>
<body>
  <!-- 全局布局框架 -->
  <!-- 所有页面 section（默认 display:none，当前页 display:block/flex） -->
  <!-- Modal 层 -->
  <!-- Toast 层 -->
  <script>
    /* 1. Mock Data */
    /* 2. Router（navigate / back / hashchange） */
    /* 3. 各页面初始化逻辑 */
    /* 4. 公共交互（Modal, Toast, Form） */
    /* 5. 启动：navigate(defaultPage) */
  </script>
</body>
</html>
```

### 质量检查清单（输出前自查）

- [ ] 所有页面均可从导航菜单/TabBar进入
- [ ] 所有原 `href="*.html"` 已替换为 navigate 调用
- [ ] 弹窗可正常打开和关闭
- [ ] 表单提交有反馈（Toast/跳转）
- [ ] 移动端宽度固定 375px，无横向滚动
- [ ] 后台端左侧菜单高亮当前页
- [ ] 浏览器刷新后能还原当前页（hash路由）
- [ ] 无 JS 报错（console 无红色错误）

---

## 参考文件索引

| 文件 | 用途 | 何时读取 |
|------|------|---------|
| `references/design-tokens.md` | 完整 Design Token 列表 | 开始生成前 |
| `references/components.md` | 标准组件 HTML 模板库 | 遇到表格/表单/弹窗时 |
| `references/gesture.md` | 移动端手势交互实现 | 需要滑动手势时 |
| `scripts/router.js` | 单文件路由核心逻辑 | 构建路由系统时 |
| `scripts/mock-gen.js` | Mock 数据生成辅助 | 需要批量 Mock 数据时 |
| `assets/` | 图标、占位图等静态资源 | 需要内联资源时 |

---

## 常见问题处理

**Q: 某个页面无法判断是后台端还是移动端？**
A: 优先看视口宽度设定。有 `width=device-width` 或宽度 ≤ 414px 的为移动端；宽度 ≥ 1024px 的为后台端。仍无法判断时，在分析摘要中列出，请用户确认。

**Q: 原 HTML 使用了第三方库（ECharts、Element UI 等）？**
A: 通过 CDN 引入，保持原有依赖不变。注意检查 CDN 链接有效性，替换失效链接。

**Q: 页面数量超过 30 个，单文件体积过大？**
A: 超过 30 页时，在分析摘要阶段告知用户，建议按模块拆分为多个 HTML（如 `admin_用户管理.html`、`admin_订单管理.html`），并提供模块间跳转方案。

**Q: 原 HTML 样式冲突严重？**
A: 为每个原页面的样式添加 `.page-{id}` 命名空间前缀，隔离冲突。
