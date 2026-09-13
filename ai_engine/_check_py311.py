# -*- coding: utf-8 -*-
"""部署前语法兼容性检查：用 Python 3.11 语法规则解析 ai_engine 全部模块。

背景（2026-09-13 线上事故）：本地开发环境是 Python 3.13，服务器是 **Python 3.11**。
Python 3.12 起才允许在 f-string 表达式里写反斜杠 / 复用同类引号（PEP 701），
3.11 会直接 SyntaxError，导致 Uvicorn 导入 app 失败、进程崩溃循环。

用法：python _check_py311.py   （退出码 0 = 通过；非 0 = 有不兼容语法）

两层检查：
  A. ast 语法层：用 feature_version=(3,11) 解析，可发现 match / 海象等语法差异；
     **注意**：抓不到 f-string 内的反斜杠（PEP 701 属 tokenizer 层，feature_version 不覆盖）。
  B. 文本启发式：扫描 f-string 的 {} 表达式里是否出现反斜杠——这是本次事故的直接成因。
最权威的检查仍是"用服务器上的 Python 3.11 执行 py_compile"（部署流程已内置该步骤）。
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

TARGET = (3, 11)
HERE = Path(__file__).resolve().parent


def backslash_in_fstring(src: str) -> list[tuple[int, str]]:
    """启发式：找出 f-string 的 {} 表达式内出现反斜杠的行（Python 3.11 会 SyntaxError）。"""
    hits: list[tuple[int, str]] = []
    for lineno, line in enumerate(src.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("#") or ("f\"" not in line and "f'" not in line):
            continue
        depth = 0
        for ch in line:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth = max(0, depth - 1)
            elif ch == "\\" and depth > 0:
                hits.append((lineno, line.strip()[:100]))
                break
    return hits


def main() -> int:
    bad: list[tuple[str, int, str]] = []
    files = sorted(p for p in HERE.glob("*.py") if p.name != Path(__file__).name)
    for f in files:
        src = f.read_text(encoding="utf-8")
        try:
            ast.parse(src, filename=str(f), feature_version=TARGET)
        except SyntaxError as e:
            bad.append((f.name, e.lineno or 0, e.msg))
        for lineno, text in backslash_in_fstring(src):
            bad.append((f.name, lineno, f"f-string 表达式内出现反斜杠：{text}"))

    if bad:
        print(f"✕ 发现 {len(bad)} 处不兼容 Python {TARGET[0]}.{TARGET[1]} 的写法：")
        for name, line, msg in bad:
            print(f"    {name}:{line}  {msg}")
        print("\n提示：f-string 表达式内不能出现反斜杠或同类引号（Python 3.12+ 才允许）。")
        print("      把表达式提前算到变量里，再在 f-string 中引用该变量。")
        return 1

    print(f"✓ 全部 {len(files)} 个模块通过 Python {TARGET[0]}.{TARGET[1]} 兼容性检查")
    return 0


if __name__ == "__main__":
    sys.exit(main())
