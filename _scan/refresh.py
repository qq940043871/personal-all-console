# -*- coding: utf-8 -*-
"""一键刷新总工作台：扫描 → 生成 →（可选）浏览器校验。

用法：
    python _scan/refresh.py            # 扫描 + 重新生成 index.html
    python _scan/refresh.py --verify   # 追加浏览器校验：
                                       #   verify_go.py          file:// 与 serve.py 双模式跳转
                                       #   audit_static_mode.py  静态预览必须降级（不得产出 404 链接）
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = sys.executable


def run(title, script, *args):
    print("\n=== %s ===" % title)
    r = subprocess.run([PY, str(HERE / script), *args], cwd=str(HERE))
    if r.returncode:
        print("!! 失败（退出码 %d）：%s" % (r.returncode, script))
        sys.exit(r.returncode)


def main():
    run("1/4 扫描各仓库入口 / 端口 / git 状态", "scan_projects.py")
    run("2/4 合并策展，生成 index.html", "build.py")
    if "--verify" in sys.argv:
        run("3/4 双模式跳转校验（file:// 与 serve.py）", "verify_go.py")
        run("4/4 静态预览降级校验（无挂载服务器不得产出 404 链接）", "audit_static_mode.py")
    else:
        print("\n=== 3/4 跳过浏览器校验（加 --verify 启用）===")
    print("\n刷新完成：双击 index.html 直开（file://），"
          "或运行 python serve.py 后访问 http://127.0.0.1:3000/")


if __name__ == "__main__":
    main()
