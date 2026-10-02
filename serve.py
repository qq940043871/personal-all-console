# -*- coding: utf-8 -*-
"""总工作台本地服务：控制台本身 + 7 个项目仓库统一挂载到 /p/<key>/。

浏览器禁止 http 页面打开 file:// 链接，因此 start.bat 用本服务替代
npx http-server：「打开主入口」在 http 模式下直接开 /p/<key>/ 页面，
双击 index.html（file:// 直开）仍走本地文件路径，两种模式都能用。

用法：python serve.py [--port 3000]
"""
import json
import re
import sys
from pathlib import Path
from posixpath import normpath
from urllib.parse import unquote
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

ROOT = Path(__file__).resolve().parent
PORT = 3000
if "--port" in sys.argv:
    PORT = int(sys.argv[sys.argv.index("--port") + 1])

# 挂载表与卡片 UI 同源：直接取 index.html 里注入的 DATA（key → 项目根目录）
_m = re.search(r"const DATA = (\[.*?\]);\n",
               (ROOT / "index.html").read_text(encoding="utf-8"), re.S)
MOUNTS = {d["key"]: Path(d["root"]) for d in json.loads(_m.group(1))}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT), **kw)

    def translate_path(self, path):
        p = normpath(unquote(path.split("?", 1)[0].split("#", 1)[0]))
        segs = [s for s in p.split("/") if s and s != "."]
        if len(segs) >= 2 and segs[0] == "p":
            root = MOUNTS.get(segs[1])
            if root is not None:
                fp = (root.joinpath(*segs[2:]) if len(segs) > 2 else root).resolve()
                try:
                    fp.relative_to(root.resolve())
                except ValueError:
                    return str(ROOT / "__forbidden__")  # 白名单外一律 404
                return str(fp)
        return str(ROOT.joinpath(*segs)) if segs else str(ROOT)

    def guess_type(self, path):
        t = super().guess_type(path) or "application/octet-stream"
        if t.startswith("text/") and "charset=" not in t:
            t += "; charset=utf-8"
        return t

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        pass

    def log_error(self, fmt, *args):
        sys.stderr.write("  [err] %s\n" % (fmt % args))


def main():
    try:
        srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    except OSError:
        print(f"端口 {PORT} 被占用：可能总工作台已在运行，直接用浏览器打开 "
              f"http://127.0.0.1:{PORT}/ 即可")
        sys.exit(1)
    print(f"总工作台  http://127.0.0.1:{PORT}/")
    for k, root in MOUNTS.items():
        print(f"  /p/{k}/  ->  {root}")
    print("Ctrl+C 退出")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
