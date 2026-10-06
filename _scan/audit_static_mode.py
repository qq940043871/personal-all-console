# -*- coding: utf-8 -*-
"""静态预览模式的降级验证。

复现用户现场：不用 serve.py，而是用普通 http.server（无 /p/ 挂载）承载 index.html。
此时点「打开主入口」必须降级为「复制本地路径 + 顶部提示」，绝不能打开一个 404 页面。
"""
import socket
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(r"D:/ai_person/personal-all-console")
PORT = 3198


def port_free(p):
    s = socket.socket()
    s.settimeout(0.3)
    r = s.connect_ex(("127.0.0.1", p))
    s.close()
    return r != 0


if not port_free(PORT):
    sys.exit("port %d busy" % PORT)

srv = subprocess.Popen(
    [sys.executable, "-m", "http.server", str(PORT), "--bind", "127.0.0.1"],
    cwd=str(ROOT), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.2)

ok_all = True


def check(name, cond, extra=""):
    global ok_all
    print(("PASS " if cond else "FAIL ") + name + (("  " + str(extra)) if extra else ""))
    if not cond:
        ok_all = False


try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context()
        try:
            ctx.grant_permissions(["clipboard-read", "clipboard-write"])
        except Exception:
            pass
        pg = ctx.new_page()
        errs = []
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: errs.append(str(e)))

        pg.goto("http://127.0.0.1:%d/index.html" % PORT, wait_until="load")
        pg.wait_for_timeout(1400)          # 等 /__console__ 探测 settle

        # 1) 服务身份探测必须判否
        check("探测判定为非 serve.py", pg.evaluate("SERVE_OK") is False,
              pg.evaluate("SERVE_OK"))

        # 2) 顶部出现降级提示条
        bar = pg.eval_on_selector_all(
            "#modebar", "els=>els.map(e=>[e.className,e.innerText.replace(/\\s+/g,' ').slice(0,60)])")
        check("出现降级提示条", bool(bar) and bar[0][0].startswith("modebar"), bar)

        # 3) 点击主入口不得打开 404 新页，而应复制本地路径
        popups = []
        ctx.on("page", lambda np: popups.append(np))
        pg.click("#main article.card:first-child .btn.primary")
        pg.wait_for_timeout(900)
        check("不打开新页面（避免 404）", len(popups) == 0, [x.url for x in popups])
        toast = pg.inner_text("#toast")
        check("提示已复制本地路径", "复制" in toast, toast)

        # 4) 复制内容应是本地 Windows 路径（若剪贴板不可读则跳过）
        try:
            clip = pg.evaluate("navigator.clipboard.readText()")
        except Exception as e:
            clip = ""
            print("SKIP clipboard read (%s)" % e)
        if clip:
            check("剪贴板为本地路径", "personal-investment-notes" in clip, clip)

        # 5) 抽屉条目同样不得生成 p/ 链接
        pg.click("#main article.card:first-child .btn:not(.primary):not(.icon)")
        pg.wait_for_timeout(500)
        hrefs = pg.eval_on_selector_all(
            "#dBody button[data-act='open']", "els=>els.length")
        check("抽屉渲染出打开按钮", hrefs > 0, hrefs)
        first = pg.eval_on_selector("#dBody button[data-act='open']", "e=>e.dataset.i")
        item = pg.evaluate("CUR_ITEMS[%s]" % first)
        check("抽屉条目不再固化 p/ 链接", "u" not in item and "/p/" not in str(item), item)

        # 6) 视觉留档：顶部应出现蓝色降级提示条
        pg.screenshot(path=str(ROOT / "_scan" / "shot_static_mode.png"))

        # 7) 全程无 JS 错误
        check("无 JS 报错", not errs, errs[:3])

        b.close()
finally:
    srv.terminate()

print("ALL PASS" if ok_all else "HAS FAILURE")
sys.exit(0 if ok_all else 1)
