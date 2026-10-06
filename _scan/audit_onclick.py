# -*- coding: utf-8 -*-
"""抓取抽屉条目 button 的真实 onclick 属性，定位语法错误来源"""
import subprocess, sys, time, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path("D:/ai_person/personal-all-console")
PORT = 3222
srv = subprocess.Popen([sys.executable, str(ROOT / "serve.py"), "--port", str(PORT)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    for _ in range(40):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{PORT}/", timeout=1); break
        except Exception:
            time.sleep(0.25)
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        pg = b.new_context(viewport={"width": 1500, "height": 1000}).new_page()
        pg.goto(f"http://127.0.0.1:{PORT}/index.html")
        pg.wait_for_timeout(600)
        pg.locator(".card").nth(0).locator("button.btn").nth(1).click()
        pg.wait_for_timeout(500)
        info = pg.evaluate("""() => {
          const b = document.querySelector('#dBody .item .mini');
          const html = b.outerHTML;
          let ok = false, err = '';
          try { new Function(b.getAttribute('onclick')); ok = true; }
          catch(e) { err = e.message; }
          return {html: html.slice(0, 320), attr: b.getAttribute('onclick').slice(0,240), ok, err};
        }""")
        print("outerHTML:\n", info["html"])
        print("\nonclick 值:\n", info["attr"])
        print("\n可编译:", info["ok"], "|", info["err"])

        # 报告全部 item 的 onclick 可编译性
        bad = pg.evaluate("""() => {
          const out=[];
          document.querySelectorAll('#dBody .item .mini').forEach((b,i)=>{
            const a=b.getAttribute('onclick');
            try{ new Function(a); }catch(e){ out.push(i+': '+e.message+' <- '+a.slice(0,110)); }
          });
          return out;
        }""")
        print("\n不可编译的按钮数:", len(bad))
        for x in bad[:8]:
            print("  ", x)
        b.close()
finally:
    srv.terminate()
