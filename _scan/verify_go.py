# -*- coding: utf-8 -*-
"""验证「打开主入口」按钮：
- file:// 模式：应弹出新页（项目本地文件）
- http 模式（serve.py）：应弹出 /p/<key>/ 挂载页面；中文路径、目录、README 链接均可用
"""
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "index.html"
PY = sys.executable
PORT = 3199
fails = []

def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("  " + detail if detail else ""))
    if not cond:
        fails.append(name)

srv = subprocess.Popen([PY, str(ROOT / "serve.py"), "--port", str(PORT)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    up = False
    for _ in range(40):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{PORT}/", timeout=1)
            up = True
            break
        except Exception:
            time.sleep(0.25)
    check("serve.py 启动", up)
    if not up:
        print("\n服务器未启动，后续 http 用例无法进行")
        sys.exit(1)

    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)

        # ---- 模式一：file:// 直开（预期：popup 打开项目本地页面）----
        ctx = b.new_context(viewport={"width": 1500, "height": 1000})
        pg = ctx.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(HTML.as_uri())
        pg.wait_for_timeout(800)
        pop = None
        try:
            with pg.expect_popup(timeout=4000) as pinfo:
                pg.locator(".card").nth(0).locator("button.btn.primary").click()
            pop = pinfo.value
        except Exception:
            pass
        check("file:// 点击主入口弹出项目页", pop is not None,
              "popup url = " + (pop.url if pop else "无"))
        check("file:// 弹出的是 invest 主页", bool(
            pop and pop.url == "file:///D:/ai_person/personal-investment-notes/index.html"),
            pop.url if pop else "")
        check("file:// 模式无 JS 报错", not errs, "; ".join(errs[:3]))
        ctx.close()

        # ---- 模式二：http://（serve.py 挂载，预期：弹出 /p/invest/ 页面）----
        ctx2 = b.new_context(viewport={"width": 1500, "height": 1000})
        pg2 = ctx2.new_page()
        errs2 = []
        pg2.on("pageerror", lambda e: errs2.append(str(e)))
        pg2.goto(f"http://127.0.0.1:{PORT}/index.html")
        pg2.wait_for_timeout(800)
        pop2 = None
        try:
            with pg2.expect_popup(timeout=4000) as pinfo2:
                pg2.locator(".card").nth(0).locator("button.btn.primary").click()
            pop2 = pinfo2.value
        except Exception:
            pass
        check("http:// 点击主入口弹出挂载页面", pop2 is not None,
              "popup url = " + (pop2.url if pop2 else "无"))
        check("http:// 弹出的是 /p/invest/index.html", bool(
            pop2 and pop2.url == f"http://127.0.0.1:{PORT}/p/invest/index.html"),
            pop2.url if pop2 else "")
        if pop2:
            pop2.wait_for_load_state()
            check("挂载页面真实加载（非错误页）",
                  pop2.evaluate("document.readyState") == "complete"
                  and "投研" not in (pop2.title() or ""),
                  "title = " + (pop2.title() or ""))
        # 中文文件名 / 目录 / README 链接
        st_html = pg2.evaluate(
            "fetch('/p/invest/banks/'+encodeURIComponent('Java深度八股文.html')).then(r=>r.status)")
        st_dir = pg2.evaluate("fetch('/p/invest/cases/').then(r=>r.status)")
        st_rd = pg2.evaluate("fetch('/p/invest/README.md').then(r=>r.status)")
        st_404 = pg2.evaluate("fetch('/p/invest/../../windows/win.ini').then(r=>r.status)")
        check("中文文件名可访问", st_html == 200, f"status={st_html}")
        check("目录挂载可访问（dir:// 条目）", st_dir == 200, f"status={st_dir}")
        check("README 链接可访问", st_rd == 200, f"status={st_rd}")
        check("路径穿越被拒", st_404 == 404, f"status={st_404}")
        # ---- 抽屉条目：回归用例（曾因内联 onclick 转义错误，255 个按钮全失效）----
        pg2.locator(".card").nth(0).locator("button.btn").nth(1).click()
        pg2.wait_for_timeout(500)
        n_items = pg2.locator("#dBody .item").count()
        check("抽屉渲染条目", n_items > 0, f"items={n_items}")
        popd = None
        try:
            with pg2.expect_popup(timeout=4000) as pi3:
                pg2.locator("#dBody .item .mini").nth(0).click()
            popd = pi3.value
        except Exception:
            pass
        check("抽屉条目可打开", popd is not None,
              "popup = " + (popd.url if popd else "无"))
        if popd:
            popd.wait_for_load_state()
        pg2.wait_for_timeout(300)
        pg2.locator("#dClose").click()
        pg2.wait_for_timeout(300)

        # 命令型条目（Python/CLI 项目）
        pg2.locator(".card").nth(1).locator("button.btn").nth(1).click()
        pg2.wait_for_timeout(500)
        ncmd = pg2.locator('#dBody button[data-act="cmd"]').count()
        check("命令型条目渲染", ncmd > 0, f"cmd buttons={ncmd}")
        check("http:// 模式无 JS 报错", not errs2, "; ".join(errs2[:3]))
        ctx2.close()
        b.close()
finally:
    srv.terminate()

print("\n" + ("ALL PASS" if not fails else "FAILED: " + ", ".join(fails)))
sys.exit(1 if fails else 0)
