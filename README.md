# personal-all-console — 总工作台

跨项目统一入口：贯串 5 个个人域仓库 + 2 个工作域仓库，单文件 HTML，`file://` 直开零依赖。

## 使用

- 双击 `index.html`（file:// 直开），或 `start.bat` → http://127.0.0.1:3000（`serve.py` 本地服务，无需 npx）
- 卡片点「打开主入口」拉起对应项目页面：file:// 模式直接开本地文件；http 模式浏览器禁止开 file://，改开 `serve.py` 挂载的 `http://127.0.0.1:3000/p/<key>/` 页面；「全部 N」展开抽屉内全量入口（可过滤、可搜索、可复制路径）
- 顶部端口条实时标注各项目 http-server 端口，**invest 与 b2b 均占用 3003，存在冲突**

## 覆盖范围

| 域 | 项目 | 路径 | 端口 |
|----|------|------|------|
| 生活域 | 面试求职 interview-kit | `D:/ai_person/personal-investment-notes` | 3003 ⚠ |
| 生活域 | 自媒体内容中台 | `D:/ai_person/personal-media-content` | -（CLI/Flask） |
| 生活域 | 投资交易工作站 | `D:/ai_person/personal-money-note` | 3004 |
| 生活域 | IT 技术知识库 | `D:/ai_person/personal-tech-knowledge` | 3005 |
| 生活域 | 家庭亲子仓库 | `D:/ai_person/personal-my-family` | - |
| 工作域 | B2B 供应链全景原型 | `D:/ai_work/p001_b2b_supply_chain` | 3003 ⚠ |
| 工作域 | HTML 交付原型集 | `D:/ai_work/p001_all_html_axure` | - |

当前快照：7 仓库 / 1672 页面 / 255 个直开入口 / 95 commits。

## 维护

项目新增页面或新仓库后重新生成快照：

```bash
python _scan/scan_projects.py   # 扫描各仓库入口/端口/git 状态 → _scan/projects.json
python _scan/build.py           # 策展合并 → 生成 index.html
python _scan/check.py           # 浏览器冒烟（playwright，anaconda python）
python _scan/verify_go.py       # 「打开主入口」按钮回归：file:// 弹窗 + http 兜底
```

- 中文命名与分组策展在 `_scan/build.py` 的 `CUR` 字典里维护
- 模板（样式 + 交互）在 `_scan/template.html`
- `python` 请用 anaconda 解释器（playwright 仅装在 anaconda）
