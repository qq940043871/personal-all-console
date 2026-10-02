# -*- coding: utf-8 -*-
"""扫描 7 个项目的入口 / 端口 / git 状态 / 更新时间，输出 projects.json"""
import os, re, json, subprocess, datetime

ROOTS = [
    ("invest",  "面试求职",   "D:/ai_person/personal-investment-notes", "生活"),
    ("media",   "自媒体中台", "D:/ai_person/personal-media-content",    "生活"),
    ("money",   "投资交易",   "D:/ai_person/personal-money-note",       "生活"),
    ("tech",    "技术知识",   "D:/ai_person/personal-tech-knowledge",   "生活"),
    ("family",  "家庭亲子",   "D:/ai_person/personal-my-family",        "生活"),
    ("b2b",     "B2B供应链",  "D:/ai_work/p001_b2b_supply_chain",       "工作"),
    ("axure",   "Axure原型",  "D:/ai_work/p001_all_html_axure",         "工作"),
]

SKIP_DIRS = {".git", "node_modules", ".workbuddy", ".zcode", ".claude", "__pycache__",
             ".venv", "venv", "dist", "build", ".idea", ".vscode", "models", "storage",
             "_archive", "backup", "bak", "output", "videos", "assets", "media"}

PORT_RE = re.compile(r"(\d{4,5})")


def read_text(p, limit=4000):
    try:
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            return f.read(limit)
    except Exception:
        try:
            with open(p, "r", encoding="gbk", errors="ignore") as f:
                return f.read(limit)
        except Exception:
            return ""


def git_info(root):
    info = {"dirty": None, "branch": "", "last_commit": "", "commits": None}
    try:
        r = subprocess.run(["git", "-C", root, "rev-parse", "--abbrev-ref", "HEAD"],
                           capture_output=True, text=True, timeout=10)
        info["branch"] = r.stdout.strip()
        r = subprocess.run(["git", "-C", root, "status", "--porcelain"],
                           capture_output=True, text=True, timeout=20)
        lines = [l for l in r.stdout.splitlines() if l.strip()]
        info["dirty"] = len(lines)
        r = subprocess.run(["git", "-C", root, "log", "-1", "--format=%ci|%s"],
                           capture_output=True, text=True, timeout=10)
        if r.stdout.strip():
            d, _, s = r.stdout.strip().partition("|")
            info["last_commit"] = d[:16]
            info["commit_msg"] = s[:60]
        r = subprocess.run(["git", "-C", root, "rev-list", "--count", "HEAD"],
                           capture_output=True, text=True, timeout=10)
        info["commits"] = int(r.stdout.strip() or 0)
    except Exception:
        pass
    return info


def scan_entries(root, max_depth=3):
    """收集候选入口 html：任何目录下的 index.html，以及浅层(<=2)的 .html"""
    out = []
    rd = root.replace("\\", "/")
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        rel = os.path.relpath(dirpath, root).replace("\\", "/")
        depth = 0 if rel == "." else rel.count("/") + 1
        if depth > max_depth:
            dirnames[:] = []
            continue
        # 统计 html 总量（用于展示规模）
        for fn in filenames:
            if not fn.lower().endswith(".html"):
                continue
            full = os.path.join(dirpath, fn)
            relf = os.path.relpath(full, root).replace("\\", "/")
            try:
                mt = datetime.datetime.fromtimestamp(os.path.getmtime(full))
                mtime = mt.strftime("%Y-%m-%d")
                size = os.path.getsize(full)
            except Exception:
                mtime, size = "", 0
            base = fn.lower()
            is_index = base.startswith("index")
            if is_index or depth <= 1:
                out.append({
                    "path": relf,
                    "file": fn,
                    "dir": "" if rel == "." else rel,
                    "mtime": mtime,
                    "size": size,
                    "is_index": is_index,
                })
    # 排序：根目录 index 优先，其次浅层
    out.sort(key=lambda x: (x["dir"].count("/"), x["dir"], not x["is_index"], x["file"]))
    return out


def count_html(root):
    n = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        n += len([f for f in filenames if f.lower().endswith(".html")])
    return n


def sub_projects(root, depth=1):
    """一级子目录中，哪些本身是个项目（含 index.html / README / package.json / bat）"""
    res = []
    for name in sorted(os.listdir(root)):
        p = os.path.join(root, name)
        if not os.path.isdir(p) or name in SKIP_DIRS or name.startswith("."):
            continue
        try:
            inner = os.listdir(p)
        except Exception:
            continue
        low = [x.lower() for x in inner]
        kinds = []
        if any(x == "index.html" for x in low):
            kinds.append("html")
        if any(x.startswith("readme") for x in low):
            kinds.append("doc")
        if "package.json" in low:
            kinds.append("node")
        if any(x.endswith(".bat") for x in low):
            kinds.append("bat")
        if any(x.endswith((".py",)) for x in low):
            kinds.append("py")
        res.append({"name": name, "kinds": kinds, "count": len(inner)})
    return res


def main():
    data = []
    for key, label, root, domain in ROOTS:
        root = root.replace("\\", "/")
        item = {
            "key": key, "label": label, "root": root, "domain": domain,
            "exists": os.path.isdir(root),
        }
        if not item["exists"]:
            data.append(item)
            continue
        item["entries"] = scan_entries(root)
        item["html_total"] = count_html(root)
        item["subs"] = sub_projects(root)
        item["git"] = git_info(root)
        bats = []
        for f in os.listdir(root):
            if f.lower().endswith(".bat"):
                txt = read_text(os.path.join(root, f), 1500)
                ports = sorted(set(PORT_RE.findall(txt)))
                ports = [p for p in ports if 3000 <= int(p) <= 9999]
                bats.append({"file": f, "ports": ports})
        item["bats"] = bats
        try:
            mt = datetime.datetime.fromtimestamp(os.path.getmtime(root))
            item["mtime"] = mt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            item["mtime"] = ""
        readme = read_text(os.path.join(root, "README.md"), 1200)
        desc = ""
        for line in readme.splitlines():
            line = line.strip()
            if line and not line.startswith(("#", ">", "|", "-", "`", "=")):
                desc = line[:120]
                break
        item["desc"] = desc
        data.append(item)
    with open("D:/ai_person/personal-all-console/_scan/projects.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    # 控制台摘要
    for it in data:
        print("=" * 60)
        print(it["key"], it["label"], it["root"])
        print("  exists=", it.get("exists"), "html_total=", it.get("html_total"),
              "entries=", len(it.get("entries", [])), "mtime=", it.get("mtime"))
        print("  git=", it.get("git"))
        print("  bats=", it.get("bats"))
        print("  desc=", it.get("desc"))
        print("  subs=", [(s["name"], ",".join(s["kinds"])) for s in it.get("subs", [])])
        print("  entries=")
        for e in it.get("entries", [])[:25]:
            print("     ", e["path"], e["mtime"], e["size"])


if __name__ == "__main__":
    main()
