# -*- coding: utf-8 -*-
"""冒烟：file:// 打开 index.html，抓 console 错误 + 校验 DOM 渲染"""
import re, sys, pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path("D:/ai_person/personal-all-console")
HTML = ROOT / "index.html"

src = HTML.read_text(encoding="utf-8")
m = re.search(r"const _RAW = (.*?);\nconst DATA", src, re.S)
print("数据注入:", "OK" if m else "失败")
if not m:
    sys.exit(1)
import json
_raw = json.loads(m.group(1))
data = _raw["projects"]
disc = _raw.get("discovered", [])
print("项目数:", len(data), "| 入口合计:", sum(len(d["entries"]) for d in data),
      "| 未登记仓库:", len(disc))

errs, warns = [], []
with sync_playwright() as pw:
    b = pw.chromium.launch()
    pg = b.new_page(viewport={"width": 1500, "height": 1000})
    pg.on("console", lambda msg: (errs if msg.type == "error" else warns).append(msg.text))
    pg.on("pageerror", lambda e: errs.append("PAGEERROR: " + str(e)))
    pg.goto(HTML.as_uri())
    pg.wait_for_timeout(1200)

    print("标题:", pg.title())
    print("卡片数:", pg.locator(".card").count())
    print("域分组:", pg.locator(".secttl").count())
    print("统计块:", pg.locator(".stat").count())
    print("端口标签:", pg.locator(".pport").count())
    print("冲突标记:", pg.locator(".pport.clash").count())
    print("主标题文本:", pg.locator("h1").inner_text()[:40])
    stats = pg.locator(".stat .v").all_inner_texts()
    print("全局统计:", stats)

    # 搜索
    pg.fill("#q", "签到")
    pg.wait_for_timeout(400)
    print("搜索『签到』命中卡:", pg.locator(".card").count(),
          "| 标记:", pg.locator(".hitmark").all_inner_texts())
    pg.fill("#q", "ctrm")
    pg.wait_for_timeout(400)
    print("搜索『ctrm』命中卡:", pg.locator(".card").count())
    pg.fill("#q", "不存在的关键字xyz")
    pg.wait_for_timeout(400)
    print("空结果态:", pg.locator(".empty").count())
    pg.fill("#q", "")
    pg.wait_for_timeout(300)

    # 抽屉
    pg.locator(".card").nth(5).locator(".btn").nth(1).click()
    pg.wait_for_timeout(600)
    print("抽屉标题:", pg.locator("#dName").inner_text(),
          "| 条目:", pg.locator("#dBody .item").count(),
          "| 分组:", pg.locator("#dBody .grpttl").count())
    pg.fill("#dq", "合同")
    pg.wait_for_timeout(400)
    print("抽屉内过滤『合同』:", pg.locator("#dBody .item").count())
    pg.screenshot(path=str(ROOT / "_scan/shot_detail.png"), full_page=False)
    pg.fill("#dq", "")
    pg.wait_for_timeout(300)
    pg.locator("#dClose").click()
    pg.wait_for_timeout(500)

    pg.screenshot(path=str(ROOT / "_scan/shot_full.png"), full_page=True)
    b.close()

print("\nconsole error:", len(errs))
for e in errs[:12]:
    print("  ✗", e[:200])
print("console warn:", len(warns))
for w in warns[:6]:
    print("  !", w[:160])
