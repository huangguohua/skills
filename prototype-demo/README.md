# prototype-demo

将 `prototype-generate` 按二级菜单/模块拆分产出的多个 HTML 原型文件，组装为可供业务方完整演示的单文件交互原型。

## 输入 · 输出

**输入**（`specs-mcp/{feature-name}/` 下由 `prototype-generate` 产出的拆分 HTML）：

| 文件模式 | 端 |
|---|---|
| `{feature-name}-{module}.html`（不含 `-H5`） | 管理端 |
| `{feature-name}-{module}-H5.html` | 小程序 / H5 |

**输出**（同目录下）：

| 文件 | 描述 | 触发条件 |
|---|---|---|
| `DEMO-{feature-name}-admin.html` | 后台统一演示稿（侧栏 + 顶栏 + 跨菜单跳转） | 至少存在 1 个管理端源文件 |
| `DEMO-{feature-name}-mobile.html` | 小程序统一演示稿（375px 手机框 + NavBar + TabBar + 栈式路由） | 至少存在 1 个 `-H5` 源文件 |

## 与主流程关系

```
ui-design-baseline (闸门)
   → prototype-generate (闸门①HTML / 闸门②.pen)
        → prototype-demo（可选，不阻断闸门）
   → architect-design
```

**不阻断**主流程原型确认闸门，演示稿仅作业务方走查辅助产物。

## 技术方案

- 单文件多视图：所有页面以 `<section class="page">` 存储，JS 控制显隐
- Hash 路由：URL `#page-key` 记录当前页，支持刷新还原与浏览器前进/后退
- 命名空间隔离：各源页面样式加 `.page-{page-key}` 前缀，防止全局污染
- 跨 HTML 跳转改写：源文件中 `window.location.href = 'xxx.html'` 改为同文件内 `navigate(pageKey)`
- 保留 `data-page="{page-key}"`：便于后续 .pen / 前端实现按 page-key 对齐
- 零依赖：纯 HTML/CSS/JS，无构建工具

## 目录结构

```
prototype-demo/
├── SKILL.md              # 主技能说明（Claude 读取）
├── README.md             # 本文件
├── config.json           # 输入/输出路径、命名规范、上下游配置
├── logs/                 # 执行日志（按 feature 追加）
├── outputs/              # 【已废弃】历史备用目录；实际输出与源文件同目录
├── references/
│   ├── design-tokens.md  # Design Token（管理端 + 小程序端）
│   ├── components.md     # 标准组件 HTML 模板库
│   └── gesture.md        # 移动端手势交互实现（可选）
└── scripts/
    └── router.js         # 单文件多页面路由核心逻辑
```

## 快速使用

1. 先由 `prototype-generate` 按规范产出 `{feature-name}[-{module}][-H5].html` 多个文件
2. 用户说"组装原型"/"把这些页面合成一个" → 触发本 Skill
3. 自动扫描当前 feature 目录下符合输入模式的 HTML（排除 `DEMO-*`）
4. 输出分析摘要（识别到的模块、端、跨页面跳转）供用户确认
5. 确认后在同目录产出 `DEMO-{feature-name}-admin.html` 与 `DEMO-{feature-name}-mobile.html`（二选一或全出）
