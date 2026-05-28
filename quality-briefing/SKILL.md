---
name: quality-briefing
description: "生成数据质量监控每周图形化简报竖屏长图，并按需推送到钉钉群。何时使用：用户要数据质量周报/预警简报、或要把简报图片发到钉钉。"
metadata:
  {
    "openclaw":
      {
        "emoji": "📊",
        "requires":
          {
            "bins": ["python3"],
            "env": ["DINGTALK_APP_KEY", "DINGTALK_APP_SECRET", "DINGTALK_OPEN_CONVERSATION_ID"],
          },
        "primaryEnv": "DINGTALK_OPEN_CONVERSATION_ID",
        "install":
          [
            {
              "id": "ensurepip",
              "kind": "shell",
              "command": "python3 -m ensurepip --upgrade --default-pip",
              "bins": ["pip3"],
              "label": "Bootstrap pip via ensurepip",
            },
            {
              "id": "pip-deps",
              "kind": "shell",
              "command": "python3 -m pip install --upgrade pip pymysql requests playwright",
              "bins": ["playwright"],
              "label": "Install Python deps (pymysql, requests, playwright)",
            },
            {
              "id": "playwright-chromium",
              "kind": "shell",
              "command": "python3 -m playwright install chromium",
              "label": "Install Chromium browser for headless rendering",
            },
          ],
      },
  }
---

# 数据质量监控 · 每周预警简报技能

一个技能跑完闭环：**取数 → 分析 → 渲染图片 → 推送钉钉群**。

## 何时使用
- 定时（建议每周一 9:00）生成数据质量周报并发到钉钉群；
- 用户临时要一张「本周预警简报」图片时。

## 环境变量
| 变量 | 用途 | 默认 / 必需 |
|---|---|---|
| `DQM_API_BASE` | 后端统计接口地址 | 默认 `https://dqm-test.bgyfw.com/dqm` |
| `DQM_BRIEFING_SOURCE` | `auto`/`api`/`db` | 默认 `auto`；推荐 `api` |
| `DINGTALK_APP_KEY` / `DINGTALK_APP_SECRET` | 钉钉企业内部应用凭据 | 推送时必需 |
| `DINGTALK_ROBOT_CODE` | 机器人编码，留空取 AppKey | 选填 |
| `DINGTALK_OPEN_CONVERSATION_ID` | 目标钉钉群 ID | 推送时必需 |

> 推荐使用 `api` 模式：技能只调内网后端接口，不接触数仓库凭据。

## 运行
```bash
python3 run.py            # 本期末日自动取库内最新业务日期（生产推荐）
python3 run.py 2025-05-25 # 指定本期末日
```
产物：`out/briefing.png`（手机竖屏长图）。配置了 `DINGTALK_*` 时自动推送到群。

## 定时任务建议
cron `0 9 * * 1`（每周一 9:00），代理指令例如：
> 运行 quality-briefing 技能：生成本周数据质量简报并发送到钉钉群。

## 故障排查
- **图表全 0 / 无数据**：当期数仓无数据；测试库按日重置，需要时先跑 `seed_demo.py`。
- **钉钉未推送**：检查 `DINGTALK_*` 是否齐全；机器人需已加入目标群。
- **渲染失败**：确认 `playwright install chromium` 已成功执行。
- **接口连不上**：确认节点能访问 `DQM_API_BASE`。

## 目录文件
- `run.py`        入口：取数→渲染→推送
- `query.py`      取数+分析（接口优先，回退直连数仓）
- `render.html`   数据驱动的手机竖图模板
- `dingtalk.json.example` 钉钉凭据样例（也可用环境变量）
- `requirements.txt` Python 依赖清单（OpenClaw 通过 install 步骤自动装）
