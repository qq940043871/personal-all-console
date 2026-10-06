# -*- coding: utf-8 -*-
"""追加审查：http 模式下抽屉内条目的「打开」按钮是否可用（verify_go.py 未覆盖）"""
import subprocess, sys, time, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path("D:/ai_person/personal-all-console")
PY = sys.executable
PORT = 3211

srv = subprocess.Popen([PY, str(ROOT / "serve.py"), "--port", str(PORT)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    for _ in range(40):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{PORT}/", timeout=1); break
        except Exception:
            time.sleep(0.25)

    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        ctx = b.new_context(viewport={"width": 1500, "height": 1000})
        pg = ctx.new_page()
        errs, blocked = [], []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(f"http://127.0.0.1:{PORT}/index.html")
        pg.wait_for_timeout(700)

        # 打开「面试求职」抽屉（生活域第 1 张卡）
        pg.locator(".card").nth(0).locator("button.btn").nth(1).click()
        pg.wait_for_timeout(600)
        print("抽屉:", pg.locator("#dName").inner_text(), "条目", pg.locator("#dBody .item").count())

        # 点第一个条目的「打开」按钮
        pop = None
        try:
            with pg.expect_popup(timeout=4000) as pi:
                pg.locator("#dBody .item").nth(0).locator(".mini").nth(0).click()
            pop = pi.value
        except Exception:
            pass
        print("抽屉条目点击 → popup:", pop.url if pop else "无（被阻止）")

        # 读最近的 toast 文案，看是否走了兜底
        pg.wait_for_timeout(600)
        toast = pg.locator("#toast").inner_text()
        print("toast 文案:", repr(toast))
        print("pageerror:", errs[:3] if errs else "无")

        # 抽屉内切到含 dir:// 条目的项目（自媒体中台）验证目录型条目
        pg.locator("#dClose").click(); pg.wait_for_timeout(400)
        pg.locator(".card").nth(1).locator("button.btn").nth(1).click()
        pg.wait_for_timeout(600)
        names = pg.locator("#dBody .item .iname").all_inner_texts()
        print("\n自媒体中台前 4 条:", names[:4])
        pop2 = None
        try:
            with pg.expect_popup(timeout=4000) as pi2:
                pg.locator("#dBody .item").nth(0).locator(".mini").nth(0).click()
            pop2 = pi2.value
        except Exception:
            pass
        print("目录型条目点击 → popup:", pop2.url if pop2 else "无（被阻止）")
        print("toast 文案:", repr(pg.locator("#toast").inner_text()))
        ctx.close()
        b.close()
finally:
    srv.terminate()
