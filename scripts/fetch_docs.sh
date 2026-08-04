#!/bin/bash
# 批量导出飞书文档为 Markdown
# 用法: bash fetch_docs.sh
# 依赖: lark-cli (docs +fetch --doc-format markdown)

set -e

BASE="D:/gitt/2026-07-26-17-31-16/xkz-agent"
MANIFEST="$BASE/data/docs_manifest.csv"
RAW_DIR="$BASE/data/raw"
mkdir -p "$RAW_DIR"

# 跳过注释行和标题行
grep -v '^#' "$MANIFEST" | tail -n +2 | while IFS=, read -r id title category url; do
    outfile="$RAW_DIR/${id}.md"
    if [ -f "$outfile" ] && [ -s "$outfile" ]; then
        echo "SKIP  $id (exists)"
        continue
    fi
    echo "FETCH $id ($title)"
    # 输出 JSON，用 python 提取 content 字段
    LARKSUITE_CLI_NO_UPDATE_NOTIFIER=1 LARKSUITE_CLI_NO_SKILLS_NOTIFIER=1 \
        lark-cli docs +fetch --doc "$url" --doc-format markdown --format json 2>/dev/null \
        | python -c "
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
try:
    data = json.load(sys.stdin)
    doc = data['data']['document']
    content = doc['content']
    print(content)
except Exception as e:
    print('', file=sys.stderr)
    sys.exit(1)
" > "$outfile"
    # 校验
    if [ -s "$outfile" ]; then
        echo "  OK ($(wc -c < "$outfile") bytes)"
    else
        echo "  FAIL: empty output for $id"
    fi
done

echo "=== 导出完成 ==="
ls -la "$RAW_DIR"
