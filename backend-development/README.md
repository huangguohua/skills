# Backend Development

后端开发 Skill，负责按 `design.md` 和 `tasks.md` 实现后端功能代码，并支持修复轮次处理。

## 快速开始

1. 确保 `requirements.md`、`design.md`、`tasks.md` 均已通过用户确认
2. 由 `development-orchestrator` 分派后端任务，或直接触发（关键词：开发后端 / 实现接口）
3. 本 Skill 逐任务实现后端代码，更新 CHANGELOG
4. 若为修复轮次，读取 `REVIEW_REPORT.md` 中的待修复问题，修复后回写状态为"已修复"

## 开发流程图

```
tasks.md (后端任务)
    |
    v
+---------------------------+
| Step 1: 读取后端任务列表    |
+---------------------------+
    |
    v
+---------------------------+
| Step 2: 读取编码规范       |
| Step 3: 读取后端陷阱清单   |
| Step 4: 读取项目结构       |
+---------------------------+
    |
    v
+---------------------------+
| Step 5: 逐任务实现         |
| - 阅读接口定义             |
| - 检查现有代码             |
| - 编写 Controller/Service  |
| - 编写 SQL 变更            |
| - 配置权限                 |
| - 最小化验证               |
+---------------------------+
    |
    v
+---------------------------+
| Step 6: 更新 CHANGELOG     |
+---------------------------+
    |
    v (修复轮次时)
+---------------------------+
| Step 7: 读取 REVIEW_REPORT |
| - 分析待修复问题           |
| - 实施修复                 |
| - 回写状态为"已修复"       |
+---------------------------+
```

## 目录结构

```
backend-development/
  SKILL.md                    # Skill 定义与开发规则
  config.json                 # 配置文件
  README.md                   # 本文件
  references/
    gotchas.md                # 后端开发常见陷阱
    domain-rules.md           # 代码实现领域规则
    examples.md               # CHANGELOG / REVIEW_REPORT 示例
    glossary.md               # 术语表
  assets/
    checklist-template.md     # 提交前检查清单
  scripts/
  logs/
    README.md                 # 日志格式说明
  outputs/
    .gitkeep
```

## 核心原则

- **规范先行**：编码前必须读取编码规范和陷阱清单
- **契约不破**：不擅自修改 `design.md` 定义的接口契约
- **变更可追溯**：每轮开发必须更新 CHANGELOG
- **修复闭环**：修复完成后必须回写 REVIEW_REPORT 状态，附带修复说明
- **职责边界**：只处理后端代码，不触碰前端文件
