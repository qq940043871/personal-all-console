# personal-all-console — 总工作台

跨项目统一入口：贯串个人域 + 工作域仓库，单文件 HTML，`file://` 直开零依赖。

## 使用

**推荐：双击 `index.html`**（file:// 直开，零依赖）；或 `start.bat` / `python serve.py` → http://127.0.0.1:3000（无需 npx）。

- 卡片「打开主入口」拉起对应项目页面；「全部 N」展开抽屉内全量入口（可过滤、可搜索、可复制路径）
- 抽屉里的**命令型条目**（Python / CLI 项目）点击复制命令，粘贴到终端执行

### 三种承载方式与跳转能力 ⚠️

「打开主入口」能不能跳，取决于**谁在承载这个页面**：

| 承载方式 | 打开主入口 | 说明 |
|----------|-----------|------|
| `file://`（双击 index.html） | ✅ 直接打开项目文件 | 最省事，推荐 |
| `serve.py`（`start.bat`，端口 3000） | ✅ 走 `/p/<key>/` 挂载 | 绕过浏览器「http 页面禁止打开 file://」 |
| 其他静态服务器 / IDE 内置预览 | ⚠️ 只复制本地路径 | 没有 `/p/` 挂载，**跳不了** |

> **为什么**：工作台加载时用 `HEAD ./index.html` 探测响应头 `X-Console-Serve` 来识别承载者身份。
> 只有 `serve.py` 会带这个头。识别失败时自动降级为「复制路径 + 顶部蓝色提示条」，
> **绝不会**再生成一个必然 404 的 `/p/<key>/` 链接 —— 那正是「点击主入口无法访问」的成因。

## 覆盖范围

| 域 | 项目 | 路径 | 端口 |
|----|------|------|------|
| 生活域 | 面试求职 interview-kit | `D:/ai_person/personal-investment-notes` | 3001 |
| 生活域 | 自媒体内容中台 | `D:/ai_person/personal-media-content` | 5000（Flask 看板） |
| 生活域 | 投资交易工作站 | `D:/ai_person/personal-money-note` | 3002 |
| 生活域 | IT 技术知识库 | `D:/ai_person/personal-tech-knowledge` | 3005 |
| 生活域 | 家庭亲子仓库 | `D:/ai_person/personal-my-family` | - |
| 生活域 | 读书拆书工程 | `D:/ai_person/personal-read-book` | - |
| 生活域 | AI 工程工作区 | `D:/ai_person/personal-ai-engineering` | - |
| 工作域 | B2B 供应链全景原型 | `D:/ai_work/p001_b2b_supply_chain` | 3003 |
| 工作域 | HTML 交付原型集 | `D:/ai_work/p001_all_html_axure` | - |

入口总数与页面数随快照变化，以 `index.html` 顶部统计为准。端口条实时标出冲突（多项目抢同一端口时标红）。

## 三类维护信号（页面顶部告警条）

工作台的价值取决于数据新鲜度，以下情况会在顶部黄条自动告警：

1. **快照过期** — 生成时间距今 ≥ 7 天，提示重跑 `refresh.py`
2. **入口失效** — 策展表登记过、磁盘上已不存在的入口（项目重构后常见），卡片显示「入口失效 N」徽章，悬停可见明细
3. **未登记仓库** — `D:/ai_person`、`D:/ai_work` 下存在 `.git`/README 但未纳入策展表的目录，确认后可加入

另有**蓝色模式提示条**：当前承载者不是 `serve.py` 时出现，说明为何跳转不可用。

## 维护

### 一键刷新（推荐）

```bash
python _scan/refresh.py            # 扫描 + 重新生成
python _scan/refresh.py --verify   # 追加浏览器回归校验（两套）
```

> `python` 请用 anaconda 解释器（playwright 仅装在 anaconda）。

### 分步执行

| 脚本 | 作用 |
|------|------|
| `_scan/scan_projects.py` | 扫描各仓库入口 / 端口 / git 状态，并发现未登记仓库 → `_scan/projects.json` |
| `_scan/build.py` | 策展合并 → 生成 `index.html`（**中文命名与分组在这里维护**） |
| `_scan/template.html` | 样式与交互模板（生成时注入数据） |
| `serve.py` | 本地服务：本体 + `/p/<key>/` 仓库挂载 + `/__console__` 自述端点 |
| `_scan/check.py` | 整体冒烟：卡片数、搜索、抽屉、console 错误 |
| `_scan/verify_go.py` | 双模式跳转回归：file:// 与 serve.py，含抽屉条目用例 |
| `_scan/audit_static_mode.py` | 静态预览降级回归：非 serve.py 承载时不得产出 404 链接 |

### 新增项目 / 页面

1. 在 `_scan/scan_projects.py` 的 `ROOTS` 里加一行（key / 中文名 / 路径 / 域）
2. 在 `_scan/build.py` 的 `CUR` 里补一段策展（label、accent、icon、main、order、name、extra）
3. `python _scan/refresh.py --verify`

### 已知取舍

- 入口是**策展**的（人工精选 + 自动扫描兜底），不是全量页面；抽屉内可项目内过滤
- 策展表是最脆弱的资产：项目目录重构后会出现「入口失效」，靠告警条发现而非静默丢失
- 页面数据是**快照**，git 状态与页面计数为生成时点数值
- 静态预览与 `file://` 同源限制来自浏览器安全策略，无法绕过；要直接跳转只有双击 `index.html` 或用 `serve.py` 两条路
