#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
skill-quality-briefing · 阶段 ① fetch + ② analyze

按「看板卡片指标定义」取数并做环比分析，产出简报所需的全部指标。
口径：
  - 本期      = [period_end-6 天, period_end]，默认 7 天
  - 上期      = 本期前一周同期（再往前 7 天），用于「较上周」环比
  - 超期兜底  = 待处理且触发已超 overdue_days（默认 3 天）
  - 仅统计最新版本记录（is_latest_version=1），与后端 page/export 及接口口径一致

取数双通道（生产以接口为准，保证口径统一、权限收敛）：
  1) 优先调用后端 dqm-backend 的 POST /warning-event/stats/briefing
  2) 接口不可用时回退直连数仓（MCP/pymysql，凭据复用 .mcp.json）
  可用环境变量 DQM_BRIEFING_SOURCE = auto(默认) | api | db 控制；
  接口地址用 DQM_API_BASE 覆盖：
    测试环境 → https://dqm-test.bgyfw.com/dqm（含 /dqm context-path，**默认**）
    本地 dev → http://127.0.0.1:18081
  注：调接口走 trust_env=False 绕过系统代理，便于直连内网测试域名。
"""
import os
import sys
import json
import datetime as dt

import pymysql


def _log(msg):
    """诊断日志打到 stderr，保持 stdout 为纯 JSON，便于管道消费。"""
    print(msg, file=sys.stderr)


T = "dqm_warning_event_record"
_API_PATH = "/warning-event/stats/briefing"

# 指标键（不含 insights）；两条取数通道都返回同样结构，便于复用 analyze
_METRIC_KEYS = (
    "periodStart", "periodEnd", "total", "totalChainRatio", "newToday",
    "newTodayChainRatio", "pending", "overdue3d", "processed", "processRate",
    "processRatePrev", "trendLabels", "trend", "peak", "topPendingOrgans",
)


def _load_db_conf():
    """优先从工作区 .mcp.json 读取连接信息，其次环境变量。"""
    here = os.path.dirname(os.path.abspath(__file__))
    mcp_path = os.path.abspath(os.path.join(here, "..", "..", ".mcp.json"))
    env = {}
    if os.path.exists(mcp_path):
        with open(mcp_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        env = cfg.get("mcpServers", {}).get("dqm-mysql", {}).get("env", {})
    return {
        "host": os.getenv("MYSQL_HOST", env.get("MYSQL_HOST", "public-db1.bgyfw.com")),
        "port": int(os.getenv("MYSQL_PORT", env.get("MYSQL_PORT", "3308"))),
        "user": os.getenv("MYSQL_USER", env.get("MYSQL_USER", "dqm_rw")),
        "password": os.getenv("MYSQL_PASS", env.get("MYSQL_PASS", "")),
        "database": os.getenv("MYSQL_DB", env.get("MYSQL_DB", "dqm_test")),
        # 数仓前有代理，必须显式设置超时，否则查询会中途断开
        "connect_timeout": 15,
        "read_timeout": 30,
        "write_timeout": 30,
        "charset": "utf8mb4",
    }


def _ratio(cur, prev):
    if not prev:
        return None
    return round((cur - prev) / prev, 3)


def fetch_briefing(period_end=None, period_days=7, overdue_days=3, source=None):
    """取简报指标。period_end 留空则取库内最新业务日期。
    source: auto(默认,先接口后DB) | api | db；默认读 DQM_BRIEFING_SOURCE。"""
    source = (source or os.getenv("DQM_BRIEFING_SOURCE", "auto")).lower()

    metrics = None
    if source in ("auto", "api"):
        try:
            metrics = _fetch_via_api(period_end, period_days, overdue_days)
            _log("[query] 取数通道：后端接口 /warning-event/stats/briefing")
        except Exception as exc:
            if source == "api":
                raise
            _log(f"[query] 接口取数失败，回退直连数据库：{exc}")
    if metrics is None:
        metrics = _fetch_via_db(period_end, period_days, overdue_days)
        _log("[query] 取数通道：直连数仓 dqm_test")

    # ② analyze：两条通道得到同样的指标结构，统一在此补「本周要点」
    pending = metrics.get("pending") or 0
    top = metrics.get("topPendingOrgans") or []
    top2_share = round(sum(o["pending"] for o in top[:2]) / pending, 2) if pending else 0
    metrics["insights"] = _analyze(metrics, top2_share)
    return metrics


def _fetch_via_api(period_end, period_days, overdue_days):
    """① 通道 A：调后端聚合接口，返回指标字典（不含 insights）；失败则抛异常以便回退。"""
    import requests  # 延迟导入：DB-only 场景无需 requests

    base = os.getenv("DQM_API_BASE", "https://dqm-test.bgyfw.com/dqm").rstrip("/")
    body = {"periodEnd": period_end, "periodDays": period_days, "overdueDays": overdue_days}
    # 后端为内网/本地服务，直连即可；trust_env=False 绕过系统代理，
    # 避免本机 https_proxy 把对内网测试域名(如 dqm-test.bgyfw.com)的请求拦截掉
    session = requests.Session()
    session.trust_env = False
    resp = session.post(base + _API_PATH, json=body, timeout=10)
    resp.raise_for_status()
    payload = resp.json()
    if str(payload.get("code")) != "0" or payload.get("data") is None:
        raise RuntimeError(f"接口返回异常：code={payload.get('code')} message={payload.get('message')}")
    data = payload["data"]
    # 只保留约定的指标键，避免后端附加字段污染下游
    return {k: data.get(k) for k in _METRIC_KEYS}


def _fetch_via_db(period_end, period_days, overdue_days):
    """① 通道 B：直连数仓聚合，返回指标字典（不含 insights）。period_end 留空取库内最新业务日期。"""
    conn = pymysql.connect(**_load_db_conf())
    try:
        cur = conn.cursor()

        def scalar(sql, args=()):
            cur.execute(sql, args)
            return cur.fetchone()[0]

        if not period_end:
            period_end = scalar(f"SELECT MAX(data_date) FROM {T} WHERE is_latest_version=1")
            if not period_end:
                raise RuntimeError("dqm_test 暂无数据，无法确定本期末日")

        end = dt.date.fromisoformat(str(period_end))
        start = end - dt.timedelta(days=period_days - 1)
        prev_end = start - dt.timedelta(days=1)
        prev_start = prev_end - dt.timedelta(days=period_days - 1)
        overdue_before = end - dt.timedelta(days=overdue_days)

        # 仅统计最新版本记录，与后端 page/export 及 /stats/briefing 接口口径一致
        between = f"data_date BETWEEN %s AND %s AND is_latest_version=1"

        total = scalar(f"SELECT COUNT(*) FROM {T} WHERE {between}", (start, end))
        total_prev = scalar(f"SELECT COUNT(*) FROM {T} WHERE {between}", (prev_start, prev_end))

        new_today = scalar(f"SELECT COUNT(*) FROM {T} WHERE data_date=%s AND is_latest_version=1", (end,))
        new_prev = scalar(f"SELECT COUNT(*) FROM {T} WHERE data_date=%s AND is_latest_version=1", (prev_end,))

        pending = scalar(
            f"SELECT COUNT(*) FROM {T} WHERE {between} AND warning_status='PENDING'",
            (start, end))
        processed = scalar(
            f"SELECT COUNT(*) FROM {T} WHERE {between} AND warning_status='PROCESSED'",
            (start, end))
        overdue = scalar(
            f"SELECT COUNT(*) FROM {T} WHERE {between} AND warning_status='PENDING' AND data_date<=%s",
            (start, end, overdue_before))

        processed_prev = scalar(
            f"SELECT COUNT(*) FROM {T} WHERE {between} AND warning_status='PROCESSED'",
            (prev_start, prev_end))

        # 近 7 日触发趋势（补齐缺失日为 0）
        cur.execute(
            f"SELECT data_date, COUNT(*) FROM {T} WHERE {between} GROUP BY data_date",
            (start, end))
        day_map = {str(d): int(c) for d, c in cur.fetchall()}
        days = [start + dt.timedelta(days=i) for i in range(period_days)]
        trend_labels = [d.strftime("%m-%d") for d in days]
        trend = [day_map.get(str(d), 0) for d in days]

        # 未处理 TOP5 区域
        cur.execute(
            f"""SELECT organ_name, COUNT(*) c FROM {T}
                WHERE {between} AND warning_status='PENDING'
                GROUP BY organ_name ORDER BY c DESC LIMIT 5""",
            (start, end))
        top_organs = [{"organName": n, "pending": int(c)} for n, c in cur.fetchall()]
    finally:
        conn.close()

    return {
        "periodStart": str(start),
        "periodEnd": str(end),
        "total": total,
        "totalChainRatio": _ratio(total, total_prev),
        "newToday": new_today,
        "newTodayChainRatio": _ratio(new_today, new_prev),
        "pending": pending,
        "overdue3d": overdue,
        "processed": processed,
        "processRate": round(processed / total, 3) if total else 0,
        "processRatePrev": round(processed_prev / total_prev, 3) if total_prev else 0,
        "trendLabels": trend_labels,
        "trend": trend,
        "peak": max(trend) if trend else 0,
        "topPendingOrgans": top_organs,
    }


def _pct(x):
    return f"{x * 100:.1f}%" if x is not None else "—"


def _analyze(d, top2_share):
    """② analyze：把指标翻译成给领导看的自然语言「本周要点」。"""
    out = []
    out.append(
        f"本期预警总数 {d['total']} 起，较上周 {_signed(d['totalChainRatio'])}；"
        f"今日新增 {d['newToday']} 起，较上周 {_signed(d['newTodayChainRatio'])}，"
        f"{'呈上行趋势，需关注源头治理' if (d['totalChainRatio'] or 0) > 0 else '总体平稳'}。")
    out.append(
        f"待处理 {d['pending']} 起、处理率 {_pct(d['processRate'])}"
        f"（上周 {_pct(d['processRatePrev'])}），其中 {d['overdue3d']} 起超 3 天未闭环，建议优先督办。")
    if d["topPendingOrgans"]:
        names = "、".join(f"{o['organName']}({o['pending']})" for o in d["topPendingOrgans"][:2])
        out.append(
            f"未处理区域以 {names} 居前，二者合计占待处理 {int(top2_share * 100)}%，"
            f"建议重点跟进两区案场接管闭环。")
    return out


def _signed(r):
    if r is None:
        return "—"
    return f"{'+' if r >= 0 else ''}{r * 100:.1f}%"


if __name__ == "__main__":
    end = sys.argv[1] if len(sys.argv) > 1 else None
    print(json.dumps(fetch_briefing(period_end=end), ensure_ascii=False, indent=2))
