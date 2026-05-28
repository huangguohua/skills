#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
skill-quality-briefing · 一个技能跑完闭环

  ① fetch + ② analyze  →  query.fetch_briefing()
  ③ render             →  注入 render.html，headless 截图为竖屏长图 PNG
  ④ push               →  push_dingtalk() 占位（接入群机器人 webhook 后即可发送）

用法：
  python3 run.py                 # 默认本期末日 2025-05-25
  python3 run.py 2025-05-25      # 指定本期末日
依赖：pymysql、playwright（pip install playwright && playwright install chromium）、requests

钉钉推送（企业内部应用机器人，方案A：直接发图片，免公网URL）配置——
环境变量，或在本目录放 dingtalk.json（已 gitignore）：
  DINGTALK_APP_KEY / DINGTALK_APP_SECRET            必填
  DINGTALK_ROBOT_CODE                                选填，默认取 APP_KEY
  DINGTALK_OPEN_CONVERSATION_ID                      必填，目标群的 openConversationId
未配置则跳过推送，仅出图。
"""
import os
import re
import sys
import json

import requests

from query import fetch_briefing

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "render.html")
OUT_HTML = os.path.join(HERE, "out", "briefing.filled.html")
OUT_PNG = os.path.join(HERE, "out", "briefing.png")


def render_html(data):
    """把指标注入模板的 __DATA__ 占位，产出可独立打开的 HTML。"""
    with open(TEMPLATE, "r", encoding="utf-8") as f:
        tpl = f.read()
    payload = json.dumps(data, ensure_ascii=False)
    filled = re.sub(
        r"/\*__DATA__\*/.*?/\*__DATA_END__\*/",
        lambda _: f"/*__DATA__*/ {payload} /*__DATA_END__*/",
        tpl, count=1, flags=re.S)
    os.makedirs(os.path.dirname(OUT_HTML), exist_ok=True)
    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(filled)
    return OUT_HTML


def shoot(html_path):
    """headless 渲染并截取手机卡片为 PNG。"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[render] 未安装 playwright，已生成 HTML，可手动打开："
              f"\n  {html_path}\n  安装出图：pip install playwright && playwright install chromium")
        return None
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 460, "height": 1200},
                                device_scale_factor=2)
        page.goto("file://" + html_path)
        # 等字体/ECharts 画布绘制完成
        try:
            page.wait_for_function("window.__CHARTS_READY__===true", timeout=8000)
        except Exception:
            pass
        page.wait_for_timeout(900)
        os.makedirs(os.path.dirname(OUT_PNG), exist_ok=True)
        page.locator("#phone").screenshot(path=OUT_PNG)
        browser.close()
    return OUT_PNG


def _load_dingtalk_conf():
    """先读本目录 dingtalk.json（gitignore），环境变量覆盖之。"""
    conf = {}
    cfg_path = os.path.join(HERE, "dingtalk.json")
    if os.path.exists(cfg_path):
        with open(cfg_path, "r", encoding="utf-8") as f:
            conf = json.load(f)
    for k in ("DINGTALK_APP_KEY", "DINGTALK_APP_SECRET",
              "DINGTALK_ROBOT_CODE", "DINGTALK_OPEN_CONVERSATION_ID"):
        if os.getenv(k):
            conf[k] = os.getenv(k)
    return conf


def _dt_access_token(app_key, app_secret):
    r = requests.get("https://oapi.dingtalk.com/gettoken",
                     params={"appkey": app_key, "appsecret": app_secret}, timeout=15)
    j = r.json()
    if j.get("errcode") != 0:
        raise RuntimeError(f"gettoken 失败：{j}")
    return j["access_token"]


def _dt_upload_image(token, png_path):
    with open(png_path, "rb") as f:
        r = requests.post("https://oapi.dingtalk.com/media/upload",
                          params={"access_token": token, "type": "image"},
                          files={"media": f}, timeout=30)
    j = r.json()
    if j.get("errcode") != 0:
        raise RuntimeError(f"media/upload 失败：{j}")
    return j["media_id"]


def _dt_send_group_image(token, robot_code, conv_id, media_id):
    r = requests.post(
        "https://api.dingtalk.com/v1.0/robot/groupMessages/send",
        headers={"x-acs-dingtalk-access-token": token,
                 "Content-Type": "application/json"},
        json={"robotCode": robot_code, "openConversationId": conv_id,
              "msgKey": "sampleImageMsg",
              "msgParam": json.dumps({"photoURL": media_id})},
        timeout=15)
    if r.status_code != 200:
        raise RuntimeError(f"groupMessages/send 失败：{r.status_code} {r.text}")
    return r.json()


def push_dingtalk(png_path, data):
    """④ push：企业内部应用机器人发图片到群（access_token → media_id → 群发）。"""
    if not png_path:
        print("[push] 无 PNG（未出图），跳过推送。")
        return
    c = _load_dingtalk_conf()
    app_key, app_secret = c.get("DINGTALK_APP_KEY"), c.get("DINGTALK_APP_SECRET")
    conv_id = c.get("DINGTALK_OPEN_CONVERSATION_ID")
    if not (app_key and app_secret and conv_id):
        print("[push] 未配置钉钉企业内部应用凭据（DINGTALK_APP_KEY/SECRET/OPEN_CONVERSATION_ID），"
              "跳过推送。配置后即可自动发图到群。")
        return
    robot_code = c.get("DINGTALK_ROBOT_CODE") or app_key
    try:
        token = _dt_access_token(app_key, app_secret)
        media_id = _dt_upload_image(token, png_path)
        resp = _dt_send_group_image(token, robot_code, conv_id, media_id)
        print(f"[push] 已推送简报图片到钉钉群（processQueryKey={resp.get('processQueryKey', resp)}）。")
    except Exception as e:
        print(f"[push] 推送失败：{e}")


def main():
    period_end = sys.argv[1] if len(sys.argv) > 1 else None
    print(f"[fetch] 取数 + 分析（本期末日 {period_end or '自动取库内最新'}）…")
    data = fetch_briefing(period_end=period_end)
    print(f"[fetch] 本期 {data['periodStart']}~{data['periodEnd']} · 预警总数 {data['total']} · 待处理 {data['pending']} "
          f"· 超3天 {data['overdue3d']} · 处理率 {float(data['processRate'])*100:.1f}%")
    html_path = render_html(data)
    print(f"[render] 已注入模板：{html_path}")
    png = shoot(html_path)
    if png:
        print(f"[render] 已出图：{png}")
    push_dingtalk(png, data)
    print("[done] skill-quality-briefing 执行完毕。")


if __name__ == "__main__":
    main()
