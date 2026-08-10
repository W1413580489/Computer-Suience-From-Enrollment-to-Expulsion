#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XKZ-Agent 知识库分块器 v3 —— 结构化语义分块
基于原始 Markdown 标题层级进行语义切分：
- 有标题标记处按章节边界分块（保留完整层级路径）
- 无标题处按段落语义切分（≤600字，以双换行为段落边界）
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
RAW_DIR = BASE / "data" / "raw"
OUT_FILE = BASE / "data" / "chunks.jsonl"
MANIFEST = BASE / "data" / "docs_manifest.csv"

CHUNK_MAX = 600  # 目标块最大字符数
CHUNK_MIN = 30   # 最小块字符数

# HTML 标签 + 导航噪音
HTML_TAGS = re.compile(
    r"</?(?:img|figure|source|cite|callout|blockquote|title|u|column|grid|md|sheet|bitable|"
    r"table|colgroup|col|tbody|tr|td|th|div|p|b|i|br|h[1-6])[^>]*/?>",
    re.IGNORECASE
)
NOISE_LINES = re.compile(
    r"^[-—–=*]{3,}\s*$|^返回导航页[：:]?\s*$|^-{1,2}\s*返回导航页"
)

def clean_markdown(text: str) -> str:
    text = HTML_TAGS.sub("", text)
    lines = []
    for line in text.split("\n"):
        stripped = line.strip()
        if NOISE_LINES.match(stripped):
            continue
        stripped = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", stripped)  # link
        stripped = re.sub(r"\*\*([^*]+)\*\*", r"\1", stripped)          # bold
        stripped = re.sub(r"\*([^*]+)\*", r"\1", stripped)              # italic
        stripped = re.sub(r"__([^_]+)__", r"\1", stripped)              # bold
        stripped = re.sub(r"~~([^~]+)~~", r"\1", stripped)              # strike
        stripped = re.sub(r"`([^`]+)`", r"\1", stripped)                # inline code
        stripped = re.sub(r"^\s*[-*+>]\s+", "", stripped)               # 列表/引用前导符
        stripped = re.sub(r"\\n", "", stripped)
        lines.append(stripped)
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text

def extract_number(header_text: str) -> str:
    m = re.match(r"^(\d+(?:\.\d+)*)\s+", header_text)
    return m.group(1) if m else ""

def clean_header_text(raw: str) -> str:
    t = raw.strip()
    t = re.sub(r"\*\*([^*]+)\*\*", r"\1", t)   # bold
    t = re.sub(r"\*([^*]+)\*", r"\1", t)       # italic
    t = re.sub(r"\s+", " ", t).strip()
    # 去除开头的纯装饰符号
    t = re.sub(r"^[^\w\u4e00-\u9fff]+", "", t).strip()
    return t

def parse_headers(raw_text: str) -> list[tuple[int, str, str]]:
    """
    返回 [(level, raw_line, clean_text), ...]
    level: #→1, ##→2, ###→3, ####→4
    """
    headers = []
    for line in raw_text.split("\n"):
        m = re.match(r"^(#{1,3})\s+(.+)$", line.strip())
        if m:
            level = len(m.group(1))
            raw_header = m.group(2).strip()
            clean = clean_header_text(raw_header)
            if clean:
                headers.append((level, line.strip(), clean))
    return headers

def load_manifest() -> dict[str, dict]:
    meta = {}
    with open(MANIFEST, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(",", 3)
            if len(parts) >= 4:
                meta[parts[0]] = {"title": parts[1], "category": parts[2], "url": parts[3]}
    return meta

def chunk_document(
    filepath: Path,
    doc_title: str,
    source_url: str
) -> list[dict]:
    raw = filepath.read_text(encoding="utf-8")
    clean = clean_markdown(raw)

    # 构建标题路径栈
    headers = parse_headers(raw)  # 从原始文本解析标题（因为 clean 可能丢掉 #）
    header_stack: list[str] = [doc_title]
    header_ptr = 0

    def section_path() -> str:
        return " > ".join(header_stack)

    def section_leaf() -> str:
        return header_stack[-1] if len(header_stack) > 1 else doc_title

    chunks: list[dict] = []
    buf: list[str] = []
    chunk_idx = 0

    def flush():
        nonlocal buf, chunk_idx
        text = "\n".join(buf).strip()
        # 超过上限按段落拆
        if len(text) > CHUNK_MAX:
            paragraphs = re.split(r"\n{2,}", text)
            sub_buf = ""
            for p in paragraphs:
                p = p.strip()
                if not p:
                    continue
                if sub_buf and len(sub_buf) + len(p) + 2 > CHUNK_MAX:
                    if len(sub_buf.strip()) >= CHUNK_MIN:
                        chunks.append(make_chunk(sub_buf.strip(), chunk_idx))
                        chunk_idx += 1
                    sub_buf = ""
                sub_buf = (sub_buf + "\n\n" + p).strip() if sub_buf else p
            if sub_buf and len(sub_buf.strip()) >= CHUNK_MIN:
                chunks.append(make_chunk(sub_buf.strip(), chunk_idx))
                chunk_idx += 1
        elif len(text) >= CHUNK_MIN:
            chunks.append(make_chunk(text, chunk_idx))
            chunk_idx += 1
        buf.clear()

    def make_chunk(text: str, idx: int) -> dict:
        sec = section_path()
        leaf = section_leaf()
        return {
            "id": f"{filepath.stem}_{idx:03d}",
            "doc": doc_title,
            "section": leaf,
            "section_path": sec,
            "text": text[:CHUNK_MAX * 2],  # 最终截断保护
            "source_url": source_url,
            "updated_at": "2026-08-10",
            "chunk_size": len(text),
        }

    lines = clean.split("\n")
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if buf:
                buf.append("")
            continue

        # 检查是否匹配下一个标题（从 clean 文本可能检测不到标题，用原始行号映射）
        # 简化：在 clean 文本中检测剩余 # 行
        if re.match(r"^#{1,3}\s+\S", stripped):
            # 与 header_stack 同步：弹出比我深或同级的标题
            m = re.match(r"^(#{1,3})\s+(.+)", stripped)
            level = len(m.group(1))
            h_text = clean_header_text(m.group(2))
            flush()
            while len(header_stack) > level:
                header_stack.pop()
            if len(header_stack) < level:
                header_stack.append(h_text)
            else:
                header_stack[-1] = h_text
            continue

        # 普通内容行
        line_stripped = re.sub(r"^\s+", "", stripped)
        if not line_stripped:
            continue
        buf.append(line_stripped)

        # 检测段落边界（空行后）且缓冲区过大 → 部分刷新
        if buf and buf[-1] == "" and len("\n".join(buf)) > CHUNK_MAX * 0.7:
            # 找到上一个段落边界切出
            para_end = -1
            for i in range(len(buf) - 2, -1, -1):
                if buf[i] == "":
                    para_end = i
                    break
            if para_end > 0:
                para_text = "\n".join(buf[:para_end]).strip()
                buf = buf[para_end + 1:]
                if len(para_text) >= CHUNK_MIN:
                    chunks.append(make_chunk(para_text, chunk_idx))
                    chunk_idx += 1

    flush()
    return chunks

def main():
    meta = load_manifest()
    all_chunks = []
    stats = {}

    for f in sorted(RAW_DIR.glob("*.md")):
        doc_id = f.stem
        info = meta.get(doc_id, {"title": doc_id, "category": "guide", "url": ""})
        doc_title = info["title"]
        source_url = info["url"]

        chunks = chunk_document(f, doc_title, source_url)
        all_chunks.extend(chunks)
        sections = sorted({c["section_path"] for c in chunks})
        avg_size = sum(c["chunk_size"] for c in chunks) // max(len(chunks), 1)
        stats[doc_id] = {"chunks": len(chunks), "avg": avg_size, "sections": len(sections)}
        print(f"{doc_id:14s} {len(chunks):3d} chunks  avg {avg_size:4d}  sections {len(sections):2d}")

    # 写入
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        for c in all_chunks:
            json_str = json.dumps(c, ensure_ascii=False)
            f.write(json_str + "\n")

    total = sum(c["chunk_size"] for c in all_chunks)
    print(f"\n{'='*60}")
    print(f"总块数: {len(all_chunks)}")
    print(f"总字符: {total:,}")
    print(f"平均块长: {total // max(len(all_chunks), 1)}")
    print(f"输出: {OUT_FILE}")

if __name__ == "__main__":
    main()
