# Testing Expert Skill

前后端开发完成后的质量闸门：Phase 1 设计测试用例（test-cases.md），Phase 2 执行测试并输出测试报告（test-report.md）。

## 快速开始

### 1. 前置条件

确保以下文件已存在：

```
specs-mcp/<feature-name>/requirements.md    ← 功能规格
specs-mcp/<feature-name>/design.md          ← 技术设计
specs-mcp/<feature-name>/tasks.md           ← 开发任务清单
```

### 2. 触发 Skill

```
"测试"
"设计测试用例"
"执行测试"
"生成测试报告"
"回归测试"
```

### 3. 输出

```
specs-mcp/<feature-name>/test-cases.md     ← Phase 1 输出
specs-mcp/<feature-name>/test-report.md    ← Phase 2 输出
```

---

## 两阶段工作流

```
Phase 1：测试用例设计
    ↓ 输出 test-cases.md
    ↓ 闸门：用户确认
Phase 2：测试执行
    ↓ 输出 test-report.md
    ↓ 闸门：全部 PASS → 进入人工 UI 验收
           存在 FAIL → 按归属分发修复
```

---

## 阅读顺序

首次使用本 Skill 或需要了解工作流时，按以下顺序阅读：

1. **SKILL.md** — 完整工作流（10 步，2 个 Phase）
2. **references/gotchas.md** — 常见测试陷阱，必读
3. **references/domain-rules.md** — 用例格式、报告格式、归属规则
4. **references/api.md** — MCP 数据库验证查询模板
5. 其余文件按需查阅

---

## 目录结构

```text
testing-expert/
├── SKILL.md                       # 主 Skill 文件（Claude 执行入口）
├── config.json                    # 共享配置的本地副本
├── references/
│   ├── gotchas.md                 # 常见测试陷阱（必读）
│   ├── domain-rules.md            # 用例格式、报告格式、归属标注规则
│   ├── examples.md                # 示例 test-cases.md 与 test-report.md 片段
│   ├── api.md                     # MCP 数据库验证查询模板
│   └── glossary.md                # 术语定义
├── assets/
│   ├── test-cases-template.md     # 测试用例模板
│   ├── test-report-template.md    # 测试报告模板（含归属标签）
│   └── checklist-template.md      # 测试覆盖度自检清单
├── scripts/
│   └── validate_output.py         # 验证输出文件格式
├── logs/                          # 历次测试记录
└── outputs/                       # 备用输出目录
```

---

## 与其他 Skill 的关系

```
development-orchestrator
    ↓ 前后端开发完成
testing-expert（本 Skill）
    ↓ Phase 1：test-cases.md（用户确认）
    ↓ Phase 2：test-report.md（全部 PASS）
人工 UI 验收
    ↓ 验收通过
delivery-code-review
```

---

## 失败归属标签

test-report.md 中每个 FAIL 用例必须标注归属，供编排 Skill 分发修复：

| 归属 | 含义 |
|---|---|
| `后端` | 接口逻辑、数据库状态、业务规则错误 |
| `前端` | 页面渲染、交互逻辑、字段展示错误 |
| `联调` | 前后端接口对接不一致 |
| `未明确` | 无法判断归属，需进一步排查 |

---

## 数据库查询方式

本项目统一使用 MCP 工具查询数据库，**不使用本地数据库直连**：

```
工具名：mcp__{config.database.mcp_server}__execute_sql
参数：{"query": "SELECT ..."}
```

详见 `references/api.md`。
