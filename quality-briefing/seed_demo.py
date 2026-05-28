#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
skill-quality-briefing · 演示数据播种（可复用）

往 dqm_test.dqm_warning_event_record 灌入两周演示数据，供简报评审跑出真实图表：
  - 本期 2025-05-19 ~ 05-25：353 条
  - 上期 2025-05-12 ~ 05-18：325 条（用于「较上周」环比）
确定性构造（固定随机种子），每次结果一致，并精确命中简报关键口径：
  日趋势 [52,48,61,45,57,43,47]、待处理 77、超3天未处理 11、处理率 78.2%、
  未处理 TOP5 区域 粤东20/长三角18/川渝11/华中10/京津冀10（+闽南8）。

幂等：仅删除 2025-05-12 ~ 2025-05-25 区间的旧演示数据再插入，
不触碰该区间外的其它数据（如别的团队当天的真实/测试数据）。

用法：python3 seed_demo.py        依赖：pymysql
"""
import datetime as dt
import random

import pymysql

from query import _load_db_conf

random.seed(20250525)

CUR_DAILY = {"2025-05-19": 52, "2025-05-20": 48, "2025-05-21": 61, "2025-05-22": 45,
             "2025-05-23": 57, "2025-05-24": 43, "2025-05-25": 47}   # 合计 353
PREV_DAILY = {"2025-05-12": 44, "2025-05-13": 46, "2025-05-14": 52, "2025-05-15": 40,
              "2025-05-16": 49, "2025-05-17": 51, "2025-05-18": 43}  # 合计 325

ORGANS = {"粤东区域": 11, "长三角区域": 12, "川渝区域": 13,
          "华中区域": 15, "京津冀区域": 14, "闽南区域": 16}
ORG_W = {"粤东区域": .24, "长三角区域": .21, "川渝区域": .16,
         "华中区域": .14, "京津冀区域": .14, "闽南区域": .12}
ORG_NAMES = list(ORGANS)
ORG_WEIGHTS = [ORG_W[n] for n in ORG_NAMES]

# 本期：各区待处理目标（→TOP5），及其中“超3天”(触发日<=05-22)的条数
PENDING_TARGET = {"粤东区域": 20, "长三角区域": 18, "川渝区域": 11,
                  "华中区域": 10, "京津冀区域": 10, "闽南区域": 8}   # 合计 77
OVERDUE_SPLIT = {"粤东区域": 3, "长三角区域": 3, "川渝区域": 2,
                 "华中区域": 1, "京津冀区域": 1, "闽南区域": 1}      # 合计 11
OVERDUE_BEFORE = "2025-05-22"  # 触发日 <= 此日视为超3天（相对 05-25）

CATS = [("ZX-TKYC", "案场接管异常", "R-TK-001", "案场接管状态异常未闭环", .32),
        ("ZX-RYQS", "在职人员缺失", "R-RY-002", "项目无在职人员在岗", .23),
        ("ZX-SJYS", "数据更新延迟", "R-SJ-003", "数仓源表更新超时", .13),
        ("ZX-JGBY", "接管状态不一致", "R-JG-005", "案场与常规接管状态不一致", .12),
        ("ZX-BMDQ", "白名单到期未续", "R-BM-004", "白名单豁免到期未续期", .11),
        ("ZX-QT", "其它", "R-QT-006", "其它数据质量异常", .09)]
CAT_POP = [c[:4] for c in CATS]
CAT_W = [c[4] for c in CATS]

PROJ_NAMES = ["星河湾·云邸", "半山樾", "悦云台", "棠樾", "云麓里", "凤凰城三期", "青田秀府",
              "锦绣华庭", "时代倾城", "君悦府", "翠湖天著", "江山赋", "观澜雅筑", "天玺湾",
              "湖山赋", "海上明月", "沁园春晓", "御湖湾", "翠堤春晓", "锦绣华府"]
# 稳定的项目 id / 楼盘编号
PROJ_ID = {n: 10000 + i * 137 for i, n in enumerate(PROJ_NAMES)}
PROJ_COMM = {n: f"P{100000 + i * 4099:06d}"[:7] for i, n in enumerate(PROJ_NAMES)}

COLS = ("warning_code,warning_category_code,warning_category_name,warning_rule_code,warning_rule_name,"
        "project_id,project_comm_num,project_name,organ_id,organ_name,tenant_id,sale_fiel_tkover_status_cd,"
        "conv_tkover_status_cd,has_on_duty_staff,on_duty_staff_cnt,whitelist_end_date,is_in_whitelist,"
        "warning_trigger_time,first_warning_time,warning_handle_time,warning_status,handle_duration_minutes,"
        "handle_duration_hours,data_date,elt_update_time,source_system,version_no,is_latest_version,"
        "created_time,updated_time")
PH = ",".join(["%s"] * 30)


def _row(code, day, organ, status):
    ccode, cname, rcode, rname = random.choices(CAT_POP, weights=CAT_W)[0]
    pname = random.choice(PROJ_NAMES)
    hh, mm = random.randint(6, 21), random.randint(0, 59)
    trig = f"{day} {hh:02d}:{mm:02d}:00"
    if cname == "在职人员缺失":
        ds, cnt = 0, 0
    else:
        ds, cnt = 1, random.randint(3, 18)
    wl_end = "2025-05-10" if cname == "白名单到期未续" else None
    in_wl = 1 if cname == "白名单到期未续" else 0
    sale, conv = f"TK0{random.randint(1, 3)}", f"CV0{random.randint(1, 3)}"
    if status == "PROCESSED":
        dur_min = min(max(15, int(random.gauss(220, 150))), 1800)
        ht = (dt.datetime.strptime(trig, "%Y-%m-%d %H:%M:%S") + dt.timedelta(minutes=dur_min))
        handle_time = ht.strftime("%Y-%m-%d %H:%M:%S")
        dur_hours = round(dur_min / 60, 2)
    else:
        handle_time, dur_min, dur_hours = None, None, None
    cu = f"{day} 09:00:00"
    elt = f"{day} 23:30:00"
    return (code, ccode, cname, rcode, rname, PROJ_ID[pname], PROJ_COMM[pname], pname,
            ORGANS[organ], organ, 1001, sale, conv, ds, cnt, wl_end, in_wl, trig, trig,
            handle_time, status, dur_min, dur_hours, day, elt, "DW-ELT", 1, 1, cu, cu)


def _build_current():
    """构造本期 353 条，精确满足待处理/超期/TOP5 约束。"""
    # 1) 展开成 (day) 列表
    days = []
    for d, n in CUR_DAILY.items():
        days += [d] * n
    # 2) 给每条分配区域，并保证各区在 早(<=05-22) / 晚(>=05-23) 两桶里
    #    都有足够行数承载待处理目标；不满足则换种子重试。
    for attempt in range(200):
        rnd = random.Random(1000 + attempt)
        organ_of = [rnd.choices(ORG_NAMES, weights=ORG_WEIGHTS)[0] for _ in days]
        early, late = {o: [] for o in ORG_NAMES}, {o: [] for o in ORG_NAMES}
        for i, d in enumerate(days):
            (early if d <= OVERDUE_BEFORE else late)[organ_of[i]].append(i)
        ok = all(len(early[o]) >= OVERDUE_SPLIT[o]
                 and len(late[o]) >= PENDING_TARGET[o] - OVERDUE_SPLIT[o]
                 for o in ORG_NAMES)
        if ok:
            break
    else:
        raise RuntimeError("未能为各区域分配到足够行数，请调整目标")

    pending_idx = set()
    for o in ORG_NAMES:
        rnd2 = random.Random(2000 + ORGANS[o])
        e = rnd2.sample(early[o], OVERDUE_SPLIT[o])
        l = rnd2.sample(late[o], PENDING_TARGET[o] - OVERDUE_SPLIT[o])
        pending_idx.update(e + l)

    rows = []
    seq = {}
    for i, d in enumerate(days):
        seq[d] = seq.get(d, 0) + 1
        code = f"YJ-{d.replace('-', '')}-{seq[d]:03d}"
        status = "PENDING" if i in pending_idx else "PROCESSED"
        rows.append(_row(code, d, organ_of[i], status))
    return rows


def _build_prev():
    """构造上期 325 条：老数据约 95% 已处理（仅少量遗留待处理）。"""
    rows = []
    for d, n in PREV_DAILY.items():
        for i in range(1, n + 1):
            code = f"YJ-{d.replace('-', '')}-{i:03d}"
            organ = random.choices(ORG_NAMES, weights=ORG_WEIGHTS)[0]
            status = "PROCESSED" if random.random() < 0.95 else "PENDING"
            rows.append(_row(code, d, organ, status))
    return rows


def main():
    rows = _build_prev() + _build_current()
    conn = pymysql.connect(**_load_db_conf())
    try:
        cur = conn.cursor()
        deleted = cur.execute(
            "DELETE FROM dqm_warning_event_record WHERE data_date BETWEEN %s AND %s",
            ("2025-05-12", "2025-05-25"))
        cur.executemany(
            f"INSERT INTO dqm_warning_event_record ({COLS}) VALUES ({PH})", rows)
        conn.commit()
        print(f"[seed] 清理旧演示数据 {deleted} 条，插入 {len(rows)} 条（上期325 + 本期353）。")

        def show(sql, args=()):
            cur.execute(sql, args)
            return cur.fetchall()

        CURW = "data_date BETWEEN '2025-05-19' AND '2025-05-25'"
        tot = show(f"SELECT COUNT(*) FROM dqm_warning_event_record WHERE {CURW}")[0][0]
        pend = show(f"SELECT COUNT(*) FROM dqm_warning_event_record WHERE {CURW} AND warning_status='PENDING'")[0][0]
        over = show(f"SELECT COUNT(*) FROM dqm_warning_event_record WHERE {CURW} AND warning_status='PENDING' AND data_date<='2025-05-22'")[0][0]
        print(f"[seed] 本期 总数={tot} 待处理={pend} 超3天={over} 处理率={(tot-pend)/tot*100:.1f}%")
        print("[seed] 未处理 TOP5 区域：", show(
            f"SELECT organ_name,COUNT(*) c FROM dqm_warning_event_record WHERE {CURW} "
            f"AND warning_status='PENDING' GROUP BY organ_name ORDER BY c DESC LIMIT 5"))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
