---
name: project-release-deploy
description: >
  delivery-code-review 全部关闭且测试通过后调用。读取项目部署配置和部署手册，
  执行发布流程。通过 config.deployment.* 适配不同部署平台（ECS/K8s/Docker/Vercel/裸机等）。
triggers:
  - 发布
  - 部署最新版本
  - 更新线上环境
  - 重启服务
inputs:
  - REVIEW_REPORT.md
  - test-report.md
  - config.deployment.*
outputs:
  - deploy-log-<timestamp>.md
dependencies: []
gate:
  - REVIEW_REPORT.md 中不得存在"待修复"条目
  - test-report.md 必须全部通过
reads:
  - config.deployment.deploy_runbook_path
  - config.deployment.rollback_runbook_path
  - config.deployment.platform
on_demand_hooks:
  - pre-deploy health check
  - backup-required guard
  - prod-config diff check
  - post-deploy smoke check
  - rollback guard
---

# Project Release Deploy

> **定位**：通用项目发布部署 Skill——读取部署手册、执行标准化发布流程、验证上线结果，适配多种部署平台。**不负责首次环境初始化**。

---

## 1 前置条件（闸门）

在启动部署前，必须逐项确认以下条件：

| 条件 | 检查方式 | 不满足时动作 |
|---|---|---|
| `REVIEW_REPORT.md` 无"待修复"条目 | 脚本扫描 / 人工确认 | **中止部署**，提示用户先完成修复 |
| `test-report.md` 全部通过 | 脚本扫描 / 人工确认 | **中止部署**，提示用户先完成测试 |
| 部署手册存在 | 检查 `config.deployment.deploy_runbook_path` 文件 | **中止部署**，提示用户先编写部署手册 |
| 回滚手册存在 | 检查 `config.deployment.rollback_runbook_path` 文件 | **警告**，建议补充回滚手册 |

若任一必要条件未满足，**禁止进入部署阶段**。

---

## 2 部署步骤（主流程）

### Step 1：Pre-check（预检查）

1. 执行 `scripts/pre_deploy_check.py` 验证闸门条件
2. 读取 `config.json` 中的 `deployment` 配置块，确定目标平台和路径
3. 读取部署手册 `config.deployment.deploy_runbook_path`
4. 读取回滚手册 `config.deployment.rollback_runbook_path`（若存在）

### Step 2：读取部署手册（Read Deploy Runbook）

- 按部署手册中的步骤清单生成本次部署计划
- 展示部署计划摘要给用户确认
- 用户确认后方可继续

### Step 3：备份（Backup）

- **On-Demand Hook: backup-required guard**
- 根据部署手册中的备份策略执行备份：
  - 数据库备份（若涉及数据库变更）
  - 当前版本代码/产物备份
  - 配置文件备份
- 记录备份位置和时间戳

### Step 4：生产配置差异检查

- **On-Demand Hook: prod-config diff check**
- 对比本次部署涉及的配置变更与线上配置
- 若存在关键配置变更，高亮展示并要求用户二次确认

### Step 5：构建后端（Build Backend）

- 根据 `config.codebase.backend_framework` 确定构建方式
- 执行后端构建命令（参照部署手册）
- 验证构建产物完整性

### Step 6：构建前端（Build Frontend）

- 根据 `config.codebase.frontend_framework` 确定构建方式
- 执行前端构建命令（参照部署手册）
- 验证构建产物完整性

### Step 7：部署（Deploy）

- **On-Demand Hook: pre-deploy health check**
- 根据 `config.deployment.platform` 选择部署策略：
  - `ecs`：SSH 上传产物、替换、重启服务
  - `k8s`：kubectl apply / helm upgrade
  - `docker`：docker-compose up -d / docker service update
  - `vercel`：vercel deploy --prod
  - 其他：按部署手册自定义步骤执行
- 记录部署版本号和时间戳

### Step 8：重启服务（Restart）

- 根据部署平台执行服务重启
- 等待服务启动完成
- 检查服务进程/容器状态

### Step 9：冒烟验证（Smoke Test）

- **On-Demand Hook: post-deploy smoke check**
- 按照 `assets/checklist-template.md` 中的部署后检查清单逐项验证：
  - 健康检查接口是否返回 200
  - 核心页面是否可访问
  - 关键 API 是否正常响应
  - 日志中是否有异常报错
- 若冒烟验证失败 → 进入 Step 10 回滚

### Step 10：回滚（Rollback，仅在失败时触发）

- **On-Demand Hook: rollback guard**
- 读取回滚手册 `config.deployment.rollback_runbook_path`
- 验证备份完整性
- 按回滚手册执行回滚操作
- 回滚后重新执行冒烟验证
- 记录回滚原因和过程

---

## 3 部署日志记录

每次部署都必须在 `logs/` 目录下产出部署日志，格式参照 `assets/deploy-log-template.md`：

```
文件名：YYYY-MM-DD_<feature>_deploy.md

内容：
- 部署时间
- 功能名称 / 版本号
- 部署平台
- 备份记录（位置、时间）
- 构建结果（后端、前端）
- 部署结果
- 冒烟验证结果
- 回滚记录（若有）
- 操作人（若可追溯）
```

---

## 4 禁止事项

| 编号 | 禁止行为 | 原因 |
|---|---|---|
| P1 | 在 REVIEW_REPORT 存在"待修复"时部署 | 未闭环的代码不得上线 |
| P2 | 跳过备份直接部署 | 无法回滚将导致灾难性后果 |
| P3 | 跳过冒烟验证 | 无法确认部署是否成功 |
| P4 | 首次环境初始化 | 本 Skill 仅用于已初始化环境的增量发布 |
| P5 | 未经用户确认直接部署 | 部署计划必须经用户确认后执行 |
| P6 | 回滚时不验证备份完整性 | 损坏的备份会导致回滚失败 |

---

## 5 平台适配说明

本 Skill 通过 `config.deployment.platform` 字段适配不同部署平台：

| 平台 | platform 值 | 典型部署方式 |
|---|---|---|
| 阿里云 ECS / AWS EC2 | `ecs` | SSH + systemd + Nginx |
| Kubernetes | `k8s` | kubectl / Helm |
| Docker Compose | `docker` | docker-compose |
| Vercel | `vercel` | Vercel CLI |
| 裸机 | `bare` | 手动部署手册 |

具体部署命令和步骤以部署手册为准，`platform` 字段仅用于选择默认策略模板。

---

## 6 On-Demand Hooks 说明

| Hook 名称 | 触发时机 | 用途 |
|---|---|---|
| pre-deploy health check | 部署前 | 检查目标环境健康状态，确认可接收部署 |
| backup-required guard | 备份阶段 | 判断是否需要备份及备份范围 |
| prod-config diff check | 配置检查阶段 | 对比配置差异，防止遗漏关键变更 |
| post-deploy smoke check | 部署后 | 执行冒烟验证，确认服务正常 |
| rollback guard | 回滚前 | 验证备份完整性，确认回滚可行性 |
