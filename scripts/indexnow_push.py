# -*- coding: utf-8 -*-
"""IndexNow 推送：把 sitemap.xml 中的 URL 通知给 Bing 等参与方，加速收录与更新感知。

用法（在仓库根目录执行）：
    python scripts/indexnow_push.py --dry-run   # 只打印将要推送的 URL，不发请求
    python scripts/indexnow_push.py             # 真正推送（前置条件：key 文件已部署）

关于 key：
    IndexNow 的 key 不是密钥，只是「站点所有权」的公开凭证——
    文件名即 key、文件内容也是同一串 key，部署后可通过
    https://jnuxky.xyz/<key>.txt 访问，Bing 抓取该文件校验通过后才接受通知。
    因此它必须长期保留在网站根目录，可以公开、也可以放进仓库。
    本脚本从 frontend/public/<key>.txt 反查 key，保证只有这一个真相源。
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

SITE_HOST = "jnuxky.xyz"
SITE_ORIGIN = f"https://{SITE_HOST}"
INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"

ROOT = Path(__file__).resolve().parent.parent
PUBLIC_DIR = ROOT / "frontend" / "public"


def _find_key() -> str:
    """从 frontend/public/<key>.txt 反查 key（文件名即 key，内容需与文件名一致）。"""
    for path in sorted(PUBLIC_DIR.glob("*.txt")):
        if re.fullmatch(r"[0-9a-f]{32}", path.stem) and path.read_text(encoding="utf-8").strip() == path.stem:
            return path.stem
    raise SystemExit("未找到 IndexNow key 文件：需要 frontend/public/<32 位十六进制>.txt，且内容与文件名一致")


def _sitemap_urls() -> list:
    xml = (PUBLIC_DIR / "sitemap.xml").read_text(encoding="utf-8")
    return re.findall(r"<loc>(.*?)</loc>", xml)


def main() -> int:
    ap = argparse.ArgumentParser(description="IndexNow 推送（Bing / Yandex / Seznam / Naver）")
    ap.add_argument("--dry-run", action="store_true", help="只打印将要推送的 URL，不发请求")
    args = ap.parse_args()

    key = _find_key()
    urls = _sitemap_urls()
    payload = {
        "host": SITE_HOST,
        "key": key,
        "keyLocation": f"{SITE_ORIGIN}/{key}.txt",
        "urlList": urls,
    }

    print(f"key          = {key}")
    print(f"keyLocation  = {payload['keyLocation']}")
    print(f"待推送 URL   = {len(urls)} 个")
    for url in urls:
        print("  " + url)

    if args.dry_run:
        print("\n--dry-run：未发送请求。")
        return 0

    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        INDEXNOW_ENDPOINT,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            # 200 = 已接受；202 = 已接受但 key 尚待校验
            print(f"\nIndexNow 响应：HTTP {resp.status}")
            return 0 if resp.status in (200, 202) else 1
    except urllib.error.HTTPError as e:
        # 403 = key 文件抓不到（未部署或路径不对）；422 = host/URL 不合法
        detail = e.read().decode("utf-8", "ignore")[:300]
        print(f"\nIndexNow 请求失败：HTTP {e.code} {detail}", file=sys.stderr)
        return 1
    except urllib.error.URLError as e:
        print(f"\nIndexNow 请求失败：{e.reason}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())