#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
章节感知分块器（XKZ-Agent）v2
读取 data/raw/*.md → 清洗（保留标题结构）→ 章节感知分块 → 输出 data/chunks.jsonl

v2 修复:
- 清洗阶段保留 Markdown 标题符号（#），供章节感知分块识别 section
- 新增导航噪音清理（"--返回导航页"、"返回导航页："、分隔线等）
- section 从标题行提取，标题文字不再混入正文块
"""

import json
import re
from pathlib import Path

BASE = Path(r"D:\gitt\2026-07-26-17-31-16\xkz-agent")
RAW_DIR = BASE / "data" / "raw"
OUT_FILE = BASE / "data" / "chunks.jsonl"
MANIFEST = BASE / "data" / "docs_manifest.csv"

CHUNK_SIZE = 400      # 目标块大小（字符）
MIN_CHUNK = 30        # 最小块长度
MAX_CHUNK = 1200      # 单块上限（截断）

# 噪音模式（不保留标题符号）
NOISE_PATTERNS = [
    r"!\[[^\]]*\]\([^)]*\)",            # 图片
    r"<img[^>]*/?>",
    r"<figure[^>]*>.*?</figure>",       # 卡片引用块
    r"<source[^>]*/?>",
    r"<cite[^>]*>.*?</cite>",
    r"<callout[^>]*>", r"</callout>",
    r"<blockquote>", r"</blockquote>",
    r"<title>.*?</title>",
    r"<u>", r"</u>",
    r"<column[^>]*>", r"</column>",       # 飞书分栏标签
    r"<grid[^>]*>", r"</grid>",
    r"<md>", r"</md>",
    r"<sheet[^>]*/?>", r"</sheet>",       # 嵌入表格（含闭合）
    r"<bitable[^>]*/?>",
    r"<table[^>]*>", r"</table>",         # HTML 表格结构（保留单元格文本）
    r"<colgroup[^>]*>", r"</colgroup>",
    r"<col[^>]*/?>",
    r"<tbody[^>]*>", r"</tbody>",
    r"<tr[^>]*>", r"</tr>",
    r"<td[^>]*>", r"</td>",
    r"<th[^>]*>", r"</th>",
    r"<div[^>]*>", r"</div>",
    r"<p[^>]*>", r"</p>",                 # 段落标签
    r"<b[^>]*>", r"</b>",
    r"<i[^>]*>", r"</i>",
    r"<br[^>]*/?>",                       # 换行 → 换行
    r"<h[1-6][^>]*>", r"</h[1-6]>",       # HTML 标题（保留文本）
    r"返回导航页[：:]?",                   # 导航残留
    r"^\s*[-—–]{3,}\s*$",              # 分隔线 ---
    r"--\s*返回导航页[：:].*$",          # 导航噪音
    r"^\s*返回导航页[：:]?\s*$",
    r"\[点击进入[^\]]*\]\([^)]*\)",     # 导航链接
    r"\[👉?[^\]]*\]\([^)]*\)",
    r"^\s*>\s*",                        # 行首引用符号
    r"^\s*[-*]\s+",                     # 行首列表符号
    r"\*\*|\*|__|~~|`",                 # markdown 强调符号
    r"[^\S\n]{2,}",                     # 行内多余空白（保留换行结构）
]

def clean_text(text: str) -> str:
    """清洗：去图片/标签/导航噪音/强调符号，但【保留标题 # 符号】用于章节识别。"""
    for pat in NOISE_PATTERNS:
        text = re.sub(pat, "", text, flags=re.MULTILINE | re.DOTALL)
    text = text.replace("\\n", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()
    return text


def split_heading_aware(text: str, doc: str, fallback_section: str, source_url: str) -> list:
    """按标题（#/##/###）感知分块。标题行提取为 section，不进入正文块。"""
    chunks = []
    lines = text.split("\n")
    buf = ""
    current_section = fallback_section
    chunk_index = 0

    def flush():
        nonlocal buf, chunk_index
        if not buf:
            return
        clean = buf.strip()
        if len(clean) >= MIN_CHUNK:
            chunks.append({
                "id": f"{doc}_{chunk_index:04d}",
                "doc": doc,
                "section": current_section,
                "text": clean[:MAX_CHUNK],
                "source_url": source_url,
                "updated_at": "2026-08-04",
            })
            chunk_index += 1
        buf = ""

    for line in lines:
        line = line.rstrip()
        stripped = line.strip()
        if not stripped:
            continue
        # 标题行 → 刷新当前块并切换 section
        m = re.match(r"^(#{1,3})\s+(.+)$", stripped)
        if m:
            flush()
            level = len(m.group(1))
            title = m.group(2).strip()
            title = re.sub(r"\s+", " ", title)
            # 标题文字去装饰符号（保留中英文）
            title = re.sub(r"^[#*\s>]+|[#*\s<]+$", "", title).strip()
            current_section = title[:40] if title else fallback_section
            continue
        # 普通行：累积到缓冲
        if buf and len(buf) + len(stripped) + 1 > CHUNK_SIZE:
            flush()
        buf += stripped + "\n"
        if len(buf) >= CHUNK_SIZE * 2:
            flush()

    flush()
    return chunks


def load_manifest() -> dict:
    meta = {}
    with open(MANIFEST, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(",")
            if len(parts) >= 4:
                meta[parts[0]] = {"title": parts[1], "category": parts[2], "url": ",".join(parts[3:])}
    return meta


def main():
    meta = load_manifest()
    all_chunks = []
    for f in sorted(RAW_DIR.glob("*.md")):
        doc_id = f.stem
        info = meta.get(doc_id, {"title": doc_id, "category": "guide", "url": ""})
        raw = f.read_text(encoding="utf-8")
        clean = clean_text(raw)
        chunks = split_heading_aware(clean, info["title"], "概览", info["url"])
        all_chunks.extend(chunks)
        sections = sorted({c["section"] for c in chunks})
        print(f"{doc_id:12s} {len(chunks):3d} chunks | {len(clean):6d} chars | sections: {len(sections)}")

    # 去重
    seen = set()
    unique = []
    for c in all_chunks:
        key = (c["doc"], c["text"][:100])
        if key in seen:
            continue
        seen.add(key)
        unique.append(c)

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        for c in unique:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    total = sum(len(c["text"]) for c in unique)
    print(f"\n=== 完成 ===")
    print(f"原始块: {len(all_chunks)} | 去重后: {len(unique)}")
    print(f"总字符: {total:,} | 平均块长: {total // max(len(unique), 1)}")
    print(f"输出: {OUT_FILE}")


if __name__ == "__main__":
    main()
