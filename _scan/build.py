# -*- coding: utf-8 -*-
"""把 _scan/projects.json + 人工策展 → 单文件工作台 index.html"""
import os, json, re, datetime

BASE = "D:/ai_person/personal-all-console"
SCAN = os.path.join(BASE, "_scan/projects.json")
TPL = os.path.join(BASE, "_scan/template.html")
OUT = os.path.join(BASE, "index.html")

_J = json.load(open(SCAN, encoding="utf-8"))
RAW = {d["key"]: d for d in _J["projects"]}
DISC = _J.get("discovered", [])
SNAPSHOT = _J.get("generated", "")


def exists(root, rel):
    return os.path.exists(os.path.join(root, rel).replace("\\", "/"))


# ============ 通用英文→中文 ============
TERM = {
    "index": "首页", "home": "首页", "product": "产品", "products": "产品列表",
    "product-detail": "产品详情", "cart": "购物车", "checkout": "结算收银台",
    "orders": "订单管理", "order-detail": "订单详情", "login": "登录",
    "register": "注册", "profile": "个人中心", "settings": "系统设置",
    "market": "行情中心", "news": "资讯快报", "about": "关于我们",
    "service": "服务体系", "help": "帮助中心", "favorites": "我的收藏",
    "addresses": "地址管理", "invoices": "发票管理", "history": "浏览足迹",
    "dashboard": "工作台", "overview": "总览", "tracking": "轨迹跟踪",
    "dispatch": "智能调度", "settlement": "结算中心", "contract": "合同管理",
    "contracts": "合同中心", "vehicle": "车辆管理", "driver-app": "司机端 APP",
    "command-center": "调度指挥中心", "customer": "客户管理", "map": "业务地图",
    "asean": "东盟专区", "risk": "风控中心", "logistics": "物流管理",
    "warehouse": "仓储管理", "trade": "交易中心", "search": "搜索",
    "self-service": "自助服务终端", "publicity": "宣传页", "publish": "发布",
    "quotes": "报价行情", "prepare": "投标准备", "tech": "技术实现",
    "system": "交易体系", "methods": "交易方法论", "strategies": "交易策略",
    "portfolio": "持仓组合", "rules": "市场规则", "policy": "政策解读",
    "macro": "宏观经济", "fed": "美联储与利率", "notes": "学习笔记",
    "weekly": "周报", "tags": "标签", "archive": "归档", "post": "文章",
}


def auto_name(path):
    rel = path.replace("\\", "/")
    if rel.startswith("dir://"):
        rel = rel[6:]
    parts = rel.split("/")
    base = parts[-1]
    stem = re.sub(r"\.html?$", "", base, flags=re.I)
    key = stem.lower()
    if key in ("index", "index_bak"):
        return (parts[-2] if len(parts) > 1 else "首页")
    return TERM.get(key, stem)


# ============ 人工策展 ============
CUR = {}

CUR["invest"] = dict(
    label="面试求职", accent="#38bdf8", icon="invest",
    title="interview-kit 面试工作台",
    desc="B2B 技术经理求职材料库：八股题库、备战手册、实战案例、简历站点，八股+备战+简历+投标一栈全包。",
    main="index.html", mainDoc="README.md",
    order=["工作台与备战", "八股题库", "简历站点", "投标与案例", "文档目录"],
    name={
        "index.html": "面试工作台 App",
        "prep/index.html": "备战资料库总览",
        "prep/面试框架/index.html": "面试答题框架",
        "resume/index.html": "简历与项目实战站点",
        "resume/md-viewer.html": "Markdown 阅读器",
        "slides/index.html": "数字产业链 PPT 翻页器（169 页）",
        "banks/面试背诵集合.html": "面试背诵集合（终极大合集）",
        "banks/md-viewer.html": "题库 Markdown 阅读器",
    },
    drop=["resume/md-viewer.html"],
    grp=lambda p: ("工作台与备战" if p.startswith(("index.html", "prep/"))
                   else "八股题库" if p.startswith("banks/")
                   else "简历站点" if p.startswith(("resume/", "slides/"))
                   else "文档目录"),
    extra=[
        dict(name="cases/ 实战案例目录", path="dir://cases", group="投标与案例",
             desc="投标技术方案 + 客户案例"),
        dict(name="tools/ 生成脚本目录", path="dir://tools", group="文档目录",
             desc="题库 HTML / 背诵集合 / PPT / docx 全部生成脚本"),
    ],
)

CUR["media"] = dict(
    label="自媒体中台", accent="#f472b6", icon="media",
    title="AI 自媒体内容生产中台",
    desc="三平面中台：创作（LangGraph 写作智能体）+ 发布（飞书/公众号/抖音/小说）+ Web 看板；创作资产库按作品建工程。",
    main="dir://assets", mainDoc="README.md",
    order=["看板与 CLI", "创作资产库", "平台层代码", "文档与技能", "启动命令"],
    name={"media-cli.py": "统一 CLI 入口（薄壳）"},
    grp=lambda p: "看板与 CLI",
    extra=[
        dict(name="workbench/ Web 看板 + 项目工作台", path="dir://workbench",
             group="看板与 CLI", desc="Flask · 首页创作统计，/workbench 为项目工作台", badge="Flask"),
        dict(name="skills/ 公众号文章技能线", path="dir://.claude/skills",
             group="文档与技能", desc="15 个技能包（宿主约定路径 .claude/skills）"),
        dict(name="assets/ 创作资产库总览", path="dir://assets",
             group="创作资产库", desc="按作品建工程、按平台做动作；drafts→published 状态流转"),
        dict(name="assets/novels/ 小说工程", path="dir://assets/novels",
             group="创作资产库", desc="沧元图 / 时间裂缝 / diff_life / little_man / 人物特稿 等"),
        dict(name="assets/articles/ 图文 → 公众号", path="dir://assets/articles",
             group="创作资产库", desc="公众号图文工程"),
        dict(name="assets/videos/ 短视频 → 抖音", path="dir://assets/videos",
             group="创作资产库", desc="抖音短视频工程"),
        dict(name="assets/wikis/ 知识库 → 飞书", path="dir://assets/wikis",
             group="创作资产库", desc="飞书知识库工程"),
        dict(name="core/ 对内能力层", path="dir://core",
             group="平台层代码", desc="配置 / providers 模型注册表 / 内容转化 / 素材 / 任务 / 盘点"),
        dict(name="creation/ 写平面·创作", path="dir://creation",
             group="平台层代码", desc="wechat_agent：LangGraph 写作智能体"),
        dict(name="publishing/ 写平面·出海", path="dir://publishing",
             group="平台层代码", desc="飞书 / 公众号 / 抖音 / 小说批量发布器"),
        dict(name="cli/ 命令实现包", path="dir://cli",
             group="平台层代码", desc="命令实现横跨三平面"),
        dict(name="system/ 运行时目录", path="dir://system", group="平台层代码",
             desc="models 模型缓存 / storage 运行库 / tests 平台层测试"),
        dict(name="ARCHITECTURE.md 架构说明", path="ARCHITECTURE.md", group="文档与技能"),
        dict(name="AGENTS.md 协作规范", path="AGENTS.md", group="文档与技能"),
        dict(name="publishing/README.md 发布契约", path="publishing/README.md", group="文档与技能"),
        dict(name="assets/README.md 资产库说明", path="assets/README.md", group="文档与技能"),
        dict(name="环境自检 + 探活", path="cmd://python media-cli.py doctor --live",
             group="启动命令", desc="配置/依赖/数据库自检，并实调 LLM 与发布平台", badge="命令"),
        dict(name="查看中台状态", path="cmd://python media-cli.py status",
             group="启动命令", desc="运行 python media-cli.py status", badge="命令"),
        dict(name="启动交互菜单", path="cmd://start.bat",
             group="启动命令", desc="菜单：自检 / 看板 / 资产库 / 发布 / 装依赖 / 测试", badge="命令"),
        dict(name="Web 数据看板（127.0.0.1:5000）", path="cmd://start.bat  # 菜单选 [6] 看板",
             group="启动命令", desc="Flask 看板，仅绑本地回环", badge="命令"),
    ],
)

CUR["readbook"] = dict(
    label="读书拆书", accent="#f0abfc", icon="book",
    title="personal-read-book 读书拆书工程",
    desc="网文与书籍深度分析产出：我吃西红柿全系列（盘龙/星辰变/沧元图…）+ 孙子兵法蒸馏 + 拆书工程。",
    main="analyses/我吃西红柿全部小说总览.html", mainDoc="README.md",
    order=["总览与清单", "作品分析", "拆书工程"],
    name={
        "analyses/我吃西红柿全部小说总览.html": "我吃西红柿全部小说总览",
        "INDEX.md": "分析稿清单（按作品）",
    },
    grp=lambda p: ("总览与清单" if "总览" in p or p.upper().startswith("INDEX")
                   else "作品分析" if p.startswith("analyses/") else "拆书工程"),
    extra=[
        dict(name="INDEX.md 分析稿清单", path="INDEX.md", group="总览与清单"),
        dict(name="articles|novels|videos 资产", path="dir://assets", group="拆书工程",
             desc="分析稿引用的素材与插图"),
        dict(name="books/ 拆书工程（PDF + .cangjie）", path="dir://books", group="拆书工程",
             desc="《人工智能（第2版）》等原书与拆书产物"),
    ],
)

CUR["aieng"] = dict(
    label="AI 工程", accent="#818cf8", icon="ai",
    title="personal-ai-engineering 个人 AI 工程工作区",
    desc="聚合五个子项目：多智能体运行时框架、AI 技术栈学习主工程、本地大模型实验、AI 课程站与面试题库、AI 工作台门户。",
    main="ai-study-note/index.html", mainDoc="README.md",
    order=["站点与门户", "子项目", "文档"],
    name={
        "ai-study-note/index.html": "AI 课程站 + 大模型面试题库",
        "ai-study-note/md-viewer.html": "题库 Markdown 阅读器",
        "ai-workbench/index.html": "AI 工作台门户",
    },
    grp=lambda p: ("文档" if p.lower().endswith(".md") else "站点与门户"),
    extra=[
        dict(name="agent-harness/ 多智能体运行时框架", path="dir://agent-harness",
             group="子项目", desc="课程跟学实践：Harness 架构与实现", badge="框架"),
        dict(name="ai_study_py/ AI 学习主工程", path="dir://ai_study_py",
             group="子项目", desc="框架学习 / 项目 / 工具"),
        dict(name="ai-study-note/ AI 课程站", path="dir://ai-study-note",
             group="子项目", desc="courses / documents / exam 静态站点"),
        dict(name="ai-workbench/ AI 工作台门户", path="dir://ai-workbench",
             group="子项目", desc="单页门户 index.html"),
        dict(name="ollama-lab/ 本地大模型实验", path="dir://ollama-lab",
             group="子项目", desc="Ollama 对话与 RAG 实验"),
    ],
)

CUR["money"] = dict(
    label="投资交易", accent="#fb7185", icon="money",
    title="投资交易工作站 p000_0000_money",
    desc="中文金融教育与交易管理纯前端原型：行情、方法、个股、政策、宏观、71 页面零后端直开，涨红跌绿。",
    main="index.html", mainDoc="README.md",
    order=["门户首页", "行情市场", "交易体系", "散户专区", "政策与宏观", "学习成长", "行业追踪", "系统"],
    name={
        "index.html": "交易工作站外壳",
        "portal/home.html": "首页门户", "portal/portal.html": "门户导航页",
        "market/market.html": "行情市场总览", "market/read_news.html": "读新闻",
        "market/cognition.html": "股市认知", "market/market_essence.html": "市场本质",
        "market/fundamental_logic.html": "基本面逻辑", "market/first_mover_advantage.html": "先手优势",
        "market/technology_imagination.html": "技术想象空间", "market/china_future.html": "中国期货市场",
        "trading/system.html": "交易体系总纲", "trading/methods.html": "交易方法论",
        "trading/strategies.html": "交易策略库", "trading/stock_analysis.html": "个股分析",
        "trading/manipulation.html": "庄家与散户博弈", "trading/mainipulation_process.html": "操盘流程还原",
        "trading/market_resonance.html": "市场共振", "trading/stock_cycle.html": "个股周期",
        "trading/stock_navigation.html": "个股导航", "trading/volume_price.html": "量价关系",
        "trading/investment_plan.html": "投资计划", "trading/trading_system.html": "交易系统搭建",
        "trading/tongce_medical.html": "通策医疗个股档案",
        "trading/retail_mistakes/index.html": "散户误区专区",
        "policy/meetings_policy.html": "政策与会议", "policy/macro.html": "宏观经济",
        "policy/rules.html": "市场规则", "policy/policy.html": "政策解读",
        "policy/fed.html": "美联储与利率", "policy/delisting_rules.html": "退市规则",
        "policy/financial_disclosure_rules.html": "财报披露规则",
        "policy/economic_conditions.html": "经济形势", "policy/economic_development.html": "经济发展",
        "policy/global_economic_development.html": "全球经济格局",
        "policy/government_finance.html": "财政与政府收支", "policy/meetings.html": "重要会议追踪",
        "learning/notes.html": "学习笔记总览", "learning/learning.html": "学习成长",
        "learning/learning_system.html": "学习体系", "learning/learning_news.html": "财经新闻课",
        "learning/scoring_system.html": "评分体系", "learning/biography.html": "投资人物传记",
        "learning/psychological_construction.html": "心理建设", "learning/retail_psychology.html": "散户心理",
        "industry/overview.html": "行业追踪总览", "industry/industry_tracking.html": "行业动态",
        "industry/industrial_software.html": "工业软件", "industry/industrial_software_chain.html": "工业软件产业链",
        "system/settings.html": "系统设置",
    },
    grp=lambda p: ("门户首页" if p.startswith("portal/")
                   else "行情市场" if p.startswith("market/")
                   else "散户专区" if p.startswith("trading/retail_mistakes")
                   else "交易体系" if p.startswith("trading/")
                   else "政策与宏观" if p.startswith("policy/")
                   else "学习成长" if p.startswith("learning/")
                   else "行业追踪" if p.startswith("industry/")
                   else "系统" if p.startswith("system/")
                   else "门户首页"),
)

CUR["tech"] = dict(
    label="技术知识", accent="#a78bfa", icon="tech",
    title="personal-tech-knowledge IT 技术知识库",
    desc="自 p000_0000_it 拆分：手写系列、17 年技术经验总结、码潮博客与本地大模型实验，69 页面。",
    main="index.html", mainDoc="README.md",
    order=["门户与站点", "专栏内容"],
    name={
        "index.html": "知识库门户（暗色粒子 landing）",
        "blog/index.html": "码潮 CodeTide 技术博客",
        "library/index.html": "技术学习指南库",
        "library/python.html": "Python 专题",
        "library/17年技术经验总结/09-技术知识库/index.html": "17 年技术经验 · 知识库门户",
    },
    grp=lambda p: ("专栏内容" if p.startswith("library/17") else "门户与站点"),
    extra=[
        dict(name="blog/ 博客源码目录", path="dir://blog", group="门户与站点",
             desc="后端 / AI / 架构 修炼笔记单页应用"),
        dict(name="library/ 学习指南目录", path="dir://library", group="专栏内容",
             desc="JVM / 操作系统 / 数据库 / 浏览器 手写系列"),
    ],
)

CUR["family"] = dict(
    label="家庭亲子", accent="#fbbf24", icon="family",
    title="personal-my-family 家庭主题仓库",
    desc="全家签到 APP + 小程序 + 亲子学习资料 + 少儿编程课件 + 中文识字启蒙游戏，128 页面体量。",
    main="kids-learning-chinese/game/index.html", mainDoc="README.md",
    order=["家庭应用", "启蒙游戏", "学习资料"],
    drop_re=r"(^|_/)_|[/.]_|index_bak\.html$",
    name={
        "kids-learning-chinese/game/index.html": "启蒙游戏大厅",
        "kids-learning-chinese/game/games/index.html": "游戏合集",
        "kids-learning-chinese/chinese-app/index.html": "中文识字 App",
        "family-check-in/index.html": "uni-app 编译入口（壳）",
    },
    grp=lambda p: ("启蒙游戏" if "kids-learning-chinese" in p
                   else "家庭应用" if p.startswith("dir://family")
                   else "学习资料"),
    extra=[
        dict(name="family-check-in 全家签到 uni-app", path="dir://family-check-in",
             group="家庭应用", desc="Vue3 · 5 位家庭成员差异化习惯养成 + 宠物成长", badge="uni-app"),
        dict(name="family-check-in-mini 签到小程序", path="dir://family-check-in-mini",
             group="家庭应用", desc="微信小程序原生版：首页/打卡/宠物/家庭/我的", badge="小程序"),
        dict(name="family-check-in-tools 素材工具", path="dir://family-check-in-tools",
             group="家庭应用", desc="头像批量生成、图标资产、布局校验脚本"),
        dict(name="hello_course_pdf 练习资料", path="dir://hello_course_pdf",
             group="学习资料", desc="幼小衔接 + 三年级上册 PDF（语数英）"),
        dict(name="kids-coding 少儿编程课件", path="dir://kids-coding",
             group="学习资料", desc="少儿编程 30 天 PPT（Day01–30）"),
        dict(name="kids-learning-chinese 中文学习", path="dir://kids-learning-chinese",
             group="启蒙游戏", desc="启蒙游戏 + 中文识字 App + 教材资源"),
    ],
)

CUR["b2b"] = dict(
    label="B2B 供应链", accent="#2dd4bf", icon="b2b",
    title="B2B 供应链全景原型 p001_b2b_supply_chain",
    desc="大宗商品合同履约与供应链产业电商纯静态原型：28 个子系统、1243 页面，Tailwind 自包含零后端。",
    main="index.html", mainDoc="README.md",
    order=["全景与顶层设计", "管理工具", "交易域（深度最高）", "门户与客户端", "物流·金融·云仓", "需求与规范"],
    name={
        "index.html": "B2B 供应链全景图（28 子系统入口）",
        "product.html": "产品全景",
        "01-design/index.html": "设计文档中心",
        "01-design/scenarios/business-scenarios.html": "业务场景矩阵",
        "01-design/ai-talk.html": "AI 对话原型",
        "01-design/form/index.html": "表单设计规范",
        "01-design/product/index.html": "产品域设计",
        "01-design/trade/index.html": "交易模式全景（35 种）",
        "01-design/trade/mode-flow-atlas.html": "全模式流程图谱",
        "01-design/trade/trade-schema-matrix.html": "表结构需求矩阵",
        "01-design/trade/trade-schema-unified.html": "表结构统一化设计（权威 DDL）",
        "01-design/trade/trade-mode-manuals.html": "行业规则与操作手册",
        "01-tech-foundation/index.html": "技术底座",
        "01-tech-foundation/GAP-ANALYSIS.html": "能力差距分析",
        "01-tech-foundation/foundation-map.html": "底座能力地图",
        "01-project-lifecycle/index.html": "项目投标生命周期",
        "01-project-lifecycle/prepare.html": "投标准备",
        "01-project-lifecycle/tech.html": "技术实现方案",
        "01-project-lifecycle/saas/index.html": "SaaS 交付方案",
        "00_tech_leader/index.html": "技术经理入口",
        "00_tech_leader/interview-training.html": "面试训练场",
        "00_tech_leader/customer-review.html": "客户交流会复盘",
        "00_tech_leader/dual-capability.html": "双能力模型",
        "00_tech_leader/quick-brief.html": "快速简报",
        "00_tech_leader/rectifications.html": "整改清单",
        "00_tech_leader/郑大信息-供应链B2B与供应链金融方案深度分析.html": "郑大信息方案深度分析",
        "02-sass/index.html": "SaaS 运营端",
        "02-manage/index.html": "产业电商管理端",
        "02-manage-god/index.html": "上帝视角全链路透视",
        "02-org/index.html": "机构协同",
        "02-org/portal/index.html": "开发者/机构门户",
        "02-org-kiosk/index.html": "自助服务端",
        "02-org-kiosk/self-service.html": "自助终端操作台",
        "02-org-kiosk/logistics/index.html": "自助提货业务",
        "02-org-kiosk/warehouse/index.html": "自助仓储业务",
        "05-screen/index.html": "数字决策驾驶仓",
        "05-screen/overview.html": "驾驶仓总览",
        "05-screen/trade.html": "交易大屏",
        "05-screen/logistics.html": "物流大屏",
        "05-screen/warehouse.html": "仓储大屏",
        "05-screen/risk.html": "风控大屏",
        "06-portal/index.html": "农产品门户",
        "06-portal-ind/index.html": "工业门户",
        "06-portal-ind/home.html": "工业门户首页",
        "06-portal-ind/products.html": "工业品商城",
        "06-portal-ind/asean.html": "东盟专区",
        "06-portal-ind/map.html": "业务地图",
        "06-portal-power/index.html": "能源门户",
        "06-portal-power/westcoal.html": "煤炭专区",
        "03-client/index.html": "会员中心",
        "03-client/dashboard/index.html": "会员工作台",
        "03-client/commodity-center/index.html": "商品中心",
        "03-client/orders/index.html": "订单中心",
        "03-client/settlement/index.html": "结算中心",
        "03-client/fund-center/index.html": "资金中心",
        "03-client/document-center/index.html": "单据中心",
        "03-client/message-center/index.html": "消息中心",
        "03-client/tasks/index.html": "待办任务",
        "03-client/dispute/index.html": "争议处理",
        "03-mobile/index.html": "手机 APP",
        "07-b2c/index.html": "B2C 商城",
        "08-webapp/index.html": "企微应用总览",
        "08-webapp/wecom/chat/index.html": "企微聊天待办",
        "08-webapp/wecom/chat/group.html": "企微群聊",
        "05-org-logistics/index.html": "智慧物流",
        "05-org-logistics/command-center.html": "物流指挥中心",
        "05-org-logistics/dispatch.html": "智能调度",
        "05-org-logistics/tracking.html": "轨迹跟踪",
        "05-org-logistics/settlement.html": "物流结算",
        "05-org-logistics/vehicle.html": "车辆管理",
        "05-org-logistics/driver-app.html": "司机端 APP",
        "05-org-logistics/contract.html": "物流合同",
        "05-org-logistics/customer.html": "客户管理",
        "05-org-financial/index.html": "供应链金融",
        "05-org-financial/institution.html": "金融机构",
        "05-org-financial/bank-risk.html": "银行风控",
        "05-org-financial/inspection.html": "监管核查",
        "05-org-financial/core-enterprise/index.html": "核心企业",
        "05-org-financial/buyer/index.html": "采购方融资",
        "05-org-financial/capital/index.html": "资金方",
        "05-org-financial/supervisor/index.html": "监管方",
        "05-org-financial/disposal/index.html": "资产处置",
        "05-org-warehouse/index.html": "智慧云仓",
        "04-ctrm/index.html": "CTRM 贸易平台",
        "04-futures-hedging-cotrol/index.html": "期货套保风控",
        "04-futures-hedging-cotrol/dashboard.html": "套保风控驾驶舱",
        "04-erp/index.html": "ERP 平台",
        "04-erp/dashboard/index.html": "ERP 工作台",
        "04-driver/index.html": "司机端（占位）",
        "00_html_standards/enterprise-ui-layout-spec.html": "企业级 UI 布局规范",
        "00_html_standards/bulk-layout-pattern-gallery.html": "布局模式画廊",
        "00_requirement_dev/competitor-analysis-6-vendors.html": "友商竞品分析（6 家）",
        "00_requirement_dev/stylepulse-mobile-external/index.html": "StylePulse 外部参考",
        "00_requirement_dev/套期保值风控管理系统/prototype/index.html": "套保系统原型",
        "00_requirement_dev/期货套保风控管理/04-futures-hedging-cotrol-v1/index.html": "套保原型 v1",
    },
    grp=lambda p: ("全景与顶层设计" if p.startswith(("product.html", "01-design/index", "01-design/ai-talk",
                                                    "01-design/form", "01-design/product",
                                                    "01-tech-foundation", "01-project-lifecycle", "00_tech_leader"))
                   else "交易域（深度最高）" if p.startswith("01-design/trade")
                   else "管理工具" if p.startswith(("02-", "05-screen"))
                   else "门户与客户端" if p.startswith(("06-portal", "03-", "07-b2c", "08-webapp"))
                   else "物流·金融·云仓" if p.startswith(("05-org", "04-"))
                   else "需求与规范" if p.startswith(("00_html_standards", "00_requirement_dev"))
                   else "全景与顶层设计" if p == "index.html" else "需求与规范"),
    extra=[
        dict(name="01-design/scenarios/ 业务场景", path="01-design/scenarios/business-scenarios.html",
             group="全景与顶层设计", desc="业务场景矩阵") if exists(RAW["b2b"]["root"], "01-design/scenarios/business-scenarios.html") else None,
    ],
)

CUR["axure"] = dict(
    label="Html 原型", accent="#60a5fa", icon="axure",
    title="p001_all_html_axure 交付原型集",
    desc="面向客户的 HTML 交付原型合集：MES、农产品收购、多市场协议、反向开票、VR 商城等 6 个子项目。",
    main="p001_farm_purchase/index.html", mainDoc="p001_farm_purchase/README.md",
    order=["原型工程", "项目目录"],
    name={
        "p001_1033_design_claude/index.html": "设计稿 · Claude 版",
        "p001_1033_mes/index.html": "MES 生产制造执行系统",
        "p001_1033_mes/01-design/index.html": "MES · 设计中心",
        "p001_1033_mes/02-manage/index.html": "MES · 管理端",
        "p001_1033_mes/03-client/index.html": "MES · 客户端",
        "p001_1033_mes/03-client/dashboard/index.html": "MES · 客户端工作台",
        "p001_farm_purchase/index.html": "农产品收购平台",
        "p001_farm_purchase/architecture.html": "农产品 · 架构设计",
        "p001_farm_purchase/overview.html": "农产品 · 业务总览",
        "p001_farm_purchase/business-flow.html": "农产品 · 业务流程",
        "p001_farm_purchase/merchant-flow.html": "农产品 · 商户流程",
        "p001_farm_purchase/broker-flow.html": "农产品 · 经纪人流程",
        "p001_farm_purchase/development-estimate.html": "农产品 · 开发工作量评估",
        "p001_multi_market_agreement/index.html": "多市场协议方案",
        "p001_reverse_invoicing/小程序原型/index.html": "反向开票小程序原型",
        "p001_vr_shop/index.html": "VR 商城",
    },
    grp=lambda p: "原型工程",
    extra=[
        dict(name="p001_reverse_invoicing 反向开票", path="dir://p001_reverse_invoicing",
             group="项目目录", desc="反向开票（含小程序原型）"),
        dict(name="p001_vr_shop VR 商城", path="dir://p001_vr_shop", group="项目目录"),
        dict(name="p001_multi_market_agreement 多市场协议", path="dir://p001_multi_market_agreement",
             group="项目目录"),
        dict(name="p001_1033_mes MES 系统", path="dir://p001_1033_mes", group="项目目录"),
    ],
)

DOMAIN_NAME = {"生活": "生活域", "工作": "工作域", "life": "生活域", "work": "工作域"}
DOMAIN_KEY = {"生活": "life", "工作": "work", "life": "life", "work": "work"}


def build():
    out = []
    warn = []
    for key in ["invest", "media", "money", "tech", "family", "readbook", "aieng", "b2b", "axure"]:
        raw = RAW[key]
        cur = CUR[key]
        root = raw["root"].replace("\\", "/")
        entries = []
        stale = []          # 策展过但磁盘上已不存在的入口（项目重构后会大量出现）

        # 1) 扫描出来的 html 入口
        for e in raw.get("entries", []):
            p = e["path"]
            if p in cur.get("drop", []):
                continue
            if cur.get("drop_re") and re.search(cur["drop_re"], p):
                continue
            if "/" in p and any(seg.startswith("_") and seg.endswith((".html",)) for seg in p.split("/")):
                continue
            if not p.startswith(("p001_", "dir://")) and "/_" in p:
                continue
            if not exists(root, p):
                warn.append(key + " 缺失: " + p)
                stale.append(p)
                continue
            entries.append(dict(
                name=cur["name"].get(p) or auto_name(p),
                path=p,
                group=cur["grp"](p),
            ))

        # 2) 手工附加（目录型 / 文档型 / 命令型 / README 提及的关键页）
        for it in cur.get("extra", []):
            if not it:
                continue
            p = it["path"]
            if p.startswith("cmd://"):
                entries.append(dict(it))
                continue
            real = p[6:] if p.startswith("dir://") else p
            if not os.path.exists(os.path.join(root, real) if not os.path.isabs(real) else real):
                warn.append(key + " extra 缺失: " + p)
                stale.append(it.get("name") or p)
                continue
            d = dict(it)
            d.setdefault("group", cur["order"][0])
            entries.append(d)

        # 3) 排序：按 groups order，再按名称
        order = {t: i for i, t in enumerate(cur["order"])}
        def skey(e):
            g = e.get("group") or cur["order"][-1]
            return (order.get(g, 99), g, e["name"])
        entries.sort(key=skey)

        # 4) 主入口校验（dir:// 取目录本身，cmd:// 不可作主入口）
        main = cur["main"]
        mreal = main[6:] if main.startswith(("dir://", "cmd://")) else main
        if main.startswith("cmd://") or not mreal or not exists(root, mreal):
            warn.append(key + " 主入口不可用: " + main)
            cand = [e for e in entries if not str(e.get("path", "")).startswith("cmd://")]
            main = cand[0]["path"] if cand else ""

        git = raw.get("git") or {}
        out.append(dict(
            key=key, label=cur["label"], title=cur["title"], desc=cur["desc"],
            root=root, exists=True, domain=DOMAIN_KEY[raw["domain"]], domainName=DOMAIN_NAME[raw["domain"]],
            accent=cur["accent"], icon=cur["icon"],
            main=main, mainDoc=cur["mainDoc"] if exists(root, cur["mainDoc"]) else "",
            ports=list({p for b in raw.get("bats", []) for p in b["ports"]}),
            htmlTotal=raw.get("html_total") or raw.get("htmlTotal") or 0, mtime=raw.get("mtime", ""),
            git=dict(dirty=git.get("dirty"), branch=git.get("branch", ""),
                     commits=git.get("commits"), lastCommit=git.get("lastCommit", "")),
            groups=[dict(title=t) for t in cur["order"]],
            entries=entries,
            stale=stale,
        ))

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    for d in out:
        d["generated"] = now

    payload = {"generated": now, "projects": out, "discovered": DISC}

    tpl = open(TPL, encoding="utf-8").read()
    js = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    if "/*__DATA__*/null" not in tpl:
        raise SystemExit("模板占位符丢失")
    html = tpl.replace("/*__DATA__*/null", js)
    open(OUT, "w", encoding="utf-8").write(html)

    print("生成完成:", OUT, "%.1f KB" % (os.path.getsize(OUT) / 1024))
    for d in out:
        line = "  %-9s %-9s 入口 %-4d 页面 %-5d 端口 %s" % (
            d["key"], d["label"], len(d["entries"]), d["htmlTotal"], d["ports"] or "-")
        if d.get("stale"):
            line += "  ⚠ 失效 %d" % len(d["stale"])
        print(line)
    if DISC:
        print("\n[未登记仓库] %d 个：" % len(DISC))
        for d in DISC:
            print("   - %-28s HTML %-5d %s" % (d["name"], d["html"], "git" if d["git"] else "   "))
    if warn:
        print("\n[警告] 共 %d 条：" % len(warn))
        for w in warn[:40]:
            print("   -", w)
    return warn


if __name__ == "__main__":
    build()
