#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成导航配置 data/nav_config.json
读取 docs_manifest.csv + 手工补充 → 输出 nav_config.json

依据: 需求文档 v3.2 §3.7.4 数据结构
"""
import csv
import json
from pathlib import Path

BASE = Path(r"D:\gitt\2026-07-26-17-31-16\xkz-agent")
MANIFEST = BASE / "data" / "docs_manifest.csv"
OUT = BASE / "data" / "nav_config.json"

# 侧边菜单 4 项��固定）
SIDE_MENU = [
    {"key": "guide",    "label": "攻略",     "subLabel": "GUIDE",    "number": "01", "route": "/guides",    "icon": "guide"},
    {"key": "appendix", "label": "附录",     "subLabel": "DATABASE", "number": "02", "route": "/appendix", "icon": "database"},
    {"key": "about",    "label": "关于我",   "subLabel": "ABOUT",    "number": "03", "route": "/about",     "icon": "user"},
    {"key": "changelog","label": "更新日志", "subLabel": "UPDATE",   "number": "04", "route": "/changelog", "icon": "history"},
]

# 章节描述（手工补充，用于列表页）
GUIDE_DESC = {
    "新生指南补缺": "入学前准备与新生常见问题",
    "常用链接": "常用网站与系统入口汇总",
    "大学政策简解": "奖学金/重修/毕业/处分政策",
    "学生组织介绍": "学代团/团委/院会/勤助等",
    "学术发展规划": "保研/考研/双学位/进组科研",
    "就业发展规划": "互联网/国企/考公/选调/简历",
    "竞赛指导": "A类竞赛与企业竞赛指南",
    "情感与生活指南": "恋爱/社交/生活经验",
    "效率工具推荐": "大学生必备提效工具",
    "美食娱乐排行": "校园周边美食与娱乐",
    "Git使用指南": "Git 入门到协作进阶",
}

# 附录受限标记
RESTRICTED = {"学习指南(权限观看)", "复习资料(权限观看)"}

# 快捷入口（4 项固定，URL 指向对应章节 wiki）
QUICK_ACCESS = [
    {"label": "新生任务", "desc": "从入学到毕业的全程指南", "url": "https://tralis2671.feishu.cn/wiki/DYhvw9owZivrJskU5LicGl06nAg"},
    {"label": "学业系统", "desc": "课程、成绩与培养方案",   "url": "https://bcnjr89bg80t.feishu.cn/wiki/GF54wCHgUiOSmdkYSTIcVSWwncb"},
    {"label": "资源中心", "desc": "常用网站与学习资源",     "url": "https://bcnjr89bg80t.feishu.cn/wiki/ZFQ4wlelJiOUkAk3L7tcn94xnKe"},
    {"label": "校园生活", "desc": "社团活动与校园地图",     "url": "https://tralis2671.feishu.cn/wiki/W1sRwXaB7iXYxrk5XKxcgivrnxg"},
]

FOOTER_TOOLS = [
    {"label": "教务系统", "url": "https://jw.jnu.edu.cn"},
    {"label": "学生邮箱", "url": "https://mail.jnu.edu.cn"},
    {"label": "图书馆",   "url": "https://lib.jnu.edu.cn"},
    {"label": "校园网",   "url": "https://net.jnu.edu.cn"},
    {"label": "IT 服务",  "url": "https://it.jnu.edu.cn"},
    {"label": "学院官网", "url": "https://ist.jnu.edu.cn"},
]

def build():
    # 读取 manifest
    guides, appendix = [], []
    with open(MANIFEST, "r", encoding="utf-8") as f:
        for row in csv.reader(f):
            if not row or row[0].startswith("#"):
                continue
            doc_id, title, category, url = row[0], row[1], row[2], ",".join(row[3:])
            item = {
                "label": title,
                "desc": GUIDE_DESC.get(title, ""),
                "url": url,
                "icon": "doc",
            }
            if category == "guide":
                guides.append(item)
            elif category == "appendix":
                item["restricted"] = title in RESTRICTED
                appendix.append(item)

    config = {
        "sideMenu": SIDE_MENU,
        "guides": guides,
        "appendix": appendix,
        "quickAccess": QUICK_ACCESS,
        "footerTools": FOOTER_TOOLS,
        "slogan": {"main": "探索·成长·连接未来", "sub": "EXPLORE  GROW  CONNECT"},
        "systemIndicator": {"label": "SYSTEM ONLINE", "version": "VER 1.0.0"},
        "newsUrl": "/news",
        "about": "/about",
        "chat": "/chat",
    }

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print(f"guides: {len(guides)} | appendix: {len(appendix)}")
    print(f"输出: {OUT}")

if __name__ == "__main__":
    build()
