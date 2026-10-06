# -*- coding: utf-8 -*-
"""总工作台本地服务：控制台本身 + 各项目仓库统一挂载到 /p/<key>/。

浏览器禁止 http 页面打开 file:// 链接，因此 start.bat 用本服务替代
npx http-server：「打开主入口」在 http 模式下直接开 /p/<key>/ 页面，
双击 index.html（file:// 直开）仍走本地文件路径，两种模式都能用。

另暴露 GET /__console__ 作为「服务身份探测」端点：前端据此判断当前页面
是被真正的 serve.py 承载，还是被普通静态服务器 / 内置预览承载。后者没有
/p/ 挂载，若照旧生成 p/<key>/ 链接会直接 404 —— 必须降级为复制本地路径。

用法：python serve.py [--port 3000]
"""
import json
import sys
from pathlib import Path
from posixpath import normpath
from urllib.parse import unquote
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

ROOT = Path(__file__).resolve().parent
PORT = 3000
if "--port" in sys.argv:
    PORT = int(sys.argv[sys.argv.index("--port") + 1])

# 挂载表取 _scan/projects.json（结构化产物），不再从 index.html 正则抠 JS——
# 后者会因模板格式变动而静默失效。
_SJ = ROOT / "_scan" / "projects.json"
if not _SJ.exists():
    sys.exit("缺少 _scan/projects.json，请先运行：python _scan/refresh.py")
MOUNTS = {d["key"]: Path(d["root"])
          for d in json.loads(_SJ.read_text(encoding="utf-8"))["projects"]}

# 探测端点响应体：console 字段即前端识别服务身份的凭据
PROBE = json.dumps({
    "console": "personal-all-console",
    "port": PORT,
    "root": str(ROOT),
    "mounts": {k: str(v) for k, v in MOUNTS.items()},
}, ensure_ascii=False).encode("utf-8")


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT), **kw)

    def do_GET(self):
        if self.path.split("?", 1)[0].rstrip("/") == "/__console__":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(PROBE)))
            self.end_headers()
            self.wfile.write(PROBE)
            return
        super().do_GET()

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
        self.send_header("X-Console-Serve", "1")
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
