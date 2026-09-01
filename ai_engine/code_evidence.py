# -*- coding: utf-8 -*-
"""
Code Evidence Pipeline (V2)：从学员提供的 GitHub 仓库 URL 拉取代码证据。

工作方式：
  1. 解析仓库 URL -> owner/repo
  2. GitHub API 拉取仓库元信息（default_branch）+ 递归文件树
  3. 精选关键文件：README / 依赖清单 / 主入口 / 配置
  4. 经 raw.githubusercontent.com 拉取关键文件内容（截断）
  5. 组装成一段结构化"代码证据"文本，注入 Debugger / Reviewer 的 Prompt

公开仓库：无需 Token；可选 GITHUB_TOKEN 提升速率限制。
结果按 repo_url 做 TTL 缓存，避免逐条消息重复拉取。
"""
from __future__ import annotations

import json
import os
import re
import time
import httpx

GITHUB_API = "https://api.github.com"
RAW_BASE = "https://raw.githubusercontent.com"

STRUCTURE_MAX = 200       # 展示结构最多条目数
KEY_FILES_MAX = 8         # 最多拉取几个关键文件
FILE_LINES_MAX = 120      # 单个文件正文最多行数
EVIDENCE_CHAR_CAP = 16000 # 证据文本总字符上限
CACHE_TTL = 300           # 秒

# 在文件树中忽略的目录
_SKIP_DIRS = {".git", "node_modules", "__pycache__", "venv", ".venv",
              "dist", "build", ".next", ".nuxt", "target", "Pods", ".idea", ".vscode"}

_KEY_README = {"readme.md", "readme", "readme.txt", "readme.rst"}
_KEY_DEPS = {"requirements.txt", "pyproject.toml", "setup.py", "environment.yml",
             "package.json", "go.mod", "cargo.toml", "pom.xml", "composer.json", "gemfile"}
_KEY_MAIN = {"main.py", "app.py", "server.py", "run.py", "manage.py", "cli.py",
             "index.js", "server.js", "main.js", "app.js", "index.jsx", "main.pyw",
             "manage.py", "main.go", "main.rs"}
_KEY_CFG = {".env.example", "config.py", "settings.py", "config.js", "config.ts",
            "dockerfile", "docker-compose.yml", "docker-compose.yaml"}

_cache: dict[str, tuple[float, dict]] = {}


# ---------------------------------------------------------------------------
# 仓库 URL 解析
# ---------------------------------------------------------------------------
def parse_repo_url(url: str) -> tuple[str, str] | None:
    """解析为 (owner, repo)。支持 https/git@/bare 形式。"""
    if not url:
        return None
    url = url.strip().rstrip("/")
    if url.endswith(".git"):
        url = url[:-4]
    # git@github.com:owner/repo
    m = re.match(r"[^:/@]+@[^:]+:(.+)$", url)
    if m:
        url = m.group(1)
    # https://github.com/owner/repo ...
    url = url.split("/")
    try:
        i = url.index("github.com")
    except ValueError:
        # bare: owner/repo 或 user@host 已处理
        return None
    seg = [s for s in url[i + 1:] if s]
    if len(seg) < 2:
        return None
    return seg[0], seg[1]


# ---------------------------------------------------------------------------
# 拉取
# ---------------------------------------------------------------------------
def _auth_headers() -> dict:
    tok = os.environ.get("GITHUB_TOKEN")
    return {"Authorization": f"Bearer {tok}"} if tok else {}


async def _gh_get(client: httpx.AsyncClient, url: str) -> tuple[int, dict | None]:
    """GET GitHub REST API；返回 (HTTP状态码, 解析后的 json 或 None)。"""
    r = await client.get(url, headers=_auth_headers())
    if r.status_code != 200:
        return r.status_code, None
    return 200, r.json()


async def _repo_default_branch(owner: str, repo: str) -> str | None:
    async with httpx.AsyncClient(timeout=httpx.Timeout(connect=10, read=20, write=10, pool=10)) as c:
        r = await c.get(f"{GITHUB_API}/repos/{owner}/{repo}", headers=_auth_headers())
        if r.status_code != 200:
            return None
        return r.json().get("default_branch") or "main"


async def _fetch_tree(owner: str, repo: str, branch: str) -> list[dict]:
    url = f"{GITHUB_API}/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    async with httpx.AsyncClient(timeout=httpx.Timeout(connect=10, read=30, write=10, pool=10)) as c:
        r = await c.get(url, headers=_auth_headers())
        if r.status_code == 403:
            raise PermissionError("GitHub 速率限制，稍后重试（或在服务端配置 GITHUB_TOKEN）")
        if r.status_code == 404:
            raise FileNotFoundError("仓库或分支不存在")
        if r.status_code != 200:
            raise RuntimeError(f"GitHub API 错误 HTTP {r.status_code}")
        return r.json().get("tree", [])


def _filter_structure(tree: list[dict]) -> list[str]:
    paths = []
    for node in tree:
        p = node.get("path", "")
        parts = p.split("/")
        if any(part in _SKIP_DIRS for part in parts):
            continue
        if node.get("type") == "blob":      # 文件
            paths.append(p)
    paths.sort()
    return paths


def _pick_key_files(paths: list[str], structure: list[dict]) -> list[str]:
    """按优先级精选关键文件（小写比对根节点名）。"""
    root = {p.split("/")[0].lower(): p for p in paths if "/" not in p}
    targets: list[str] = []
    for group in (_KEY_README, _KEY_DEPS, _KEY_MAIN, _KEY_CFG):
        for name in group:
            if name in root and root[name] not in targets:
                targets.append(root[name])
            if len(targets) >= KEY_FILES_MAX:
                return targets
    return targets


async def _fetch_file_content(owner: str, repo: str, branch: str, path: str) -> tuple[str, bool]:
    """通过 GitHub Contents API 拉取文件内容（走 api.github.com，不依赖 raw.githubusercontent.com）。"""
    import base64
    url = f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}?ref={branch}"
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(connect=10, read=30, write=10, pool=10)) as c:
            r = await c.get(url, headers=_auth_headers())
            if r.status_code != 200:
                return "(该文件无法获取)", False
            data = r.json()
            # Contents API 返回 base64 编码内容
            content_b64 = data.get("content", "")
            if not content_b64:
                return "(该文件为空)", False
            # GitHub 的 base64 可能含换行符，需先去掉
            raw = base64.b64decode(content_b64.replace("\n", "")).decode("utf-8", errors="replace")
    except httpx.RequestError:
        return "(该文件内容无法获取，请重试或更换网络)", False
    truncated = False
    lines = raw.splitlines()
    if len(lines) > FILE_LINES_MAX:
        lines = lines[:FILE_LINES_MAX]
        truncated = True
    return "\n".join(lines), truncated


# ---------------------------------------------------------------------------
# CI 自动验收证据（GitHub Actions）
# ---------------------------------------------------------------------------
# 工作流名 -> 验收维度（映射到 Rubric 的 requiredEvidence）
_CI_DIMENSION = {
    "build": "build", "ci": "build", "deploy": "runtime", "release": "runtime",
    "test": "test", "unit": "test", "e2e": "test", "integration": "test",
    "lint": "lint", "quality": "lint",
}


def _ci_dimension(name: str) -> str:
    n = name.lower()
    for key, dim in _CI_DIMENSION.items():
        if key in n:
            return dim
    return "test" if "test" in n else "unknown"


async def fetch_ci_evidence(owner: str, repo: str, branch: str) -> dict:
    """查询 GitHub Actions 工作流与最近运行结论。

    返回 {ok, has_ci, workflows: [{name, dimension, conclusion, status, url}],
    runs_count, text}；失败返回 {ok:False, error, code}。
    """
    try:
        timeout = httpx.Timeout(connect=10, read=30, write=10, pool=10)
        async with httpx.AsyncClient(timeout=timeout) as c:
            # 工作流列表
            wf_status, wf = await _gh_get(c, f"{GITHUB_API}/repos/{owner}/{repo}/actions/workflows")
            if wf_status == 403:
                return {"ok": False, "code": "CI_RATE_LIMITED",
                        "error": "GitHub 速率限制，无法获取 CI 状态（可配置 GITHUB_TOKEN）"}
            if wf_status == 404:
                return {"ok": False, "code": "CI_DISABLED", "error": "该仓库未开启 GitHub Actions"}
            if wf_status != 200 or not wf:
                return {"ok": False, "code": "CI_UNAVAILABLE", "error": f"无法获取 CI 信息（HTTP {wf_status}）"}

            workflows = wf.get("workflows") or []
            if not workflows:
                return {"ok": True, "has_ci": False, "workflows": [],
                        "runs_count": 0,
                        "text": "仓库没有配置任何 GitHub Actions 工作流（无 CI 自动验收证据）。"}

            by_name: dict[str, dict] = {}
            for w in workflows:
                bn = (w.get("name") or w.get("path")).strip()
                by_name[bn] = {"name": bn, "path": w.get("path", ""),
                               "dimension": _ci_dimension(bn), "conclusion": None,
                               "status": "none", "url": ""}

            # 最近运行（默认分支）
            runs_status, runs = await _gh_get(
                c, f"{GITHUB_API}/repos/{owner}/{repo}/actions/runs?branch={branch}&per_page=20")
            if runs_status == 200 and runs:
                for r in (runs.get("workflow_runs") or []):
                    wname = (r.get("name") or "").strip()
                    if wname not in by_name:
                        by_name[wname] = {"name": wname, "path": "",
                                          "dimension": _ci_dimension(wname),
                                          "conclusion": None, "status": "none", "url": ""}
                    target = by_name[wname]
                    if target["conclusion"] is None:
                        target["conclusion"] = r.get("conclusion")
                        target["status"] = r.get("status")
                        target["url"] = r.get("html_url", "")

        flow_list = list(by_name.values())
        has_ci = bool(flow_list)
        lines = ["[CI 自动验收证据]（来自 GitHub Actions，system 判定，权威）"]
        for fl in flow_list:
            conc = fl.get("conclusion") or fl.get("status") or ("未运行" if fl.get("status") == "none" else "未知")
            lines.append(f"  - 工作流 {fl['name']}（维度 {fl['dimension']}）：{conc}"
                         + (f"  {fl['url']}" if fl.get("url") else ""))
        text = "\n".join(lines)
        return {"ok": True, "has_ci": has_ci, "workflows": flow_list,
                "runs_count": len(flow_list), "text": text}

    except httpx.RequestError as e:
        return {"ok": False, "code": "CI_NETWORK", "error": f"无法连接 GitHub：{type(e).__name__}"}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "code": "CI_UNKNOWN", "error": f"获取 CI 失败：{e}"}


# ---------------------------------------------------------------------------
# V1.5 Sprint 1：Task-aware Code Retrieval
# ---------------------------------------------------------------------------

def rank_candidate_files(paths: list[str], code_context) -> list[tuple[str, float]]:
    """按 Task 的 code_context 对文件评分。

    评分维度：
      1. 文件名匹配 likelyFiles（0.5 精确 / 0.3 包含）
      2. 路径中含 keywords（每个 +0.1）
      3. 路径权重：src/ 加分，test/docs 减分
    返回 [(path, score), ...] 按分数降序。
    """
    if not code_context or (not code_context.likelyFiles and not code_context.keywords):
        # 无 code_context 时回退到均匀分
        return [(p, 0.0) for p in paths]

    scores = {}
    for p in paths:
        score = 0.0
        basename = p.rsplit("/", 1)[-1].rsplit(".", 1)[0].lower()
        full_lower = p.lower()

        # 1. 文件名匹配
        for lf in code_context.likelyFiles:
            lf_lower = lf.lower()
            if lf_lower == basename:
                score += 0.5
            elif lf_lower in basename:
                score += 0.3

        # 2. 路径中关键词
        for kw in code_context.keywords:
            if kw.lower() in full_lower:
                score += 0.1

        # 3. 路径权重
        if any(seg in full_lower for seg in ("src/", "source/", "app/")):
            score += 0.05
        if any(seg in full_lower for seg in ("test", "doc", "__pycache__", ".git")):
            score -= 0.15

        scores[p] = score

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked


async def ai_relevance_filter(candidates: list[tuple[str, float]], task, client) -> list[dict]:
    """AI 二次筛选：把候选文件列表 + Task 目标给 LLM，让它判断哪些真正相关。

    返回 [{"file": path, "reason": "..."}, ...]。
    失败时返回 None（上层回退到纯程序评分结果）。
    """
    if not candidates or not client:
        return None

    # 取前 8 个候选
    top = candidates[:8]
    file_list = "\n".join(f"  {i+1}. {p} (score={s:.2f})" for i, (p, s) in enumerate(top))

    prompt = f"""你是代码检索助手。判断以下文件中哪些与当前任务真正相关。

【当前任务】
{task.title}：{task.objective}

【候选文件】
{file_list}

只输出一个合法 JSON，格式如下：
{{"relevantFiles": [{{"file": "文件路径", "reason": "为何相关"}}]}}
不要输出任何其它文字。"""

    messages = [{"role": "user", "content": prompt}]
    try:
        raw = await client._call(messages)
        from llm_client import _extract_json
        obj = _extract_json(raw)
        return obj.get("relevantFiles", [])
    except Exception:
        return None


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------
async def build_code_evidence(repo_url: str, task_id: str = "", code_context=None,
                              client=None) -> dict:
    """拉取并组装代码证据。返回 {ok, repo, default_branch, file_count,
    key_files: [{path, content}], evidence_text} 或在失败时返回 {ok:False, error, code}。"""
    parsed = parse_repo_url(repo_url)
    if not parsed:
        return {"ok": False, "code": "BAD_REPO_URL", "error": "无法解析的 GitHub 仓库链接"}

    # TTL 缓存
    now = time.time()
    hit = _cache.get(repo_url)
    if hit and now - hit[0] < CACHE_TTL:
        return hit[1]

    owner, repo = parsed
    try:
        branch = await _repo_default_branch(owner, repo)
        if not branch:
            return {"ok": False, "code": "REPO_NOT_FOUND", "error": f"仓库 {owner}/{repo} 不存在或无法访问"}
        tree = await _fetch_tree(owner, repo, branch)
        paths = _filter_structure(tree)
        if not paths:
            return {"ok": False, "code": "EMPTY_REPO", "error": "仓库内没有可用的源码文件"}

        key_files = []
        # V1.5：Task-aware Code Retrieval
        if code_context and (code_context.likelyFiles or code_context.keywords):
            # 用 Task 的 code_context 评分
            ranked = rank_candidate_files(paths, code_context)
            ranked_dict = dict(ranked)
            # AI 二次筛选（可选）
            ai_result = None
            if client and task_id:
                from course_data import get_task
                task_obj = get_task(task_id)
                if task_obj:
                    ai_result = await ai_relevance_filter(ranked, task_obj, client)
            if ai_result:
                # AI 筛选结果决定取哪些文件
                selected = [r["file"] for r in ai_result]
                ai_reasons = {r["file"]: r.get("reason", "") for r in ai_result}
            else:
                # 回退到程序评分取前 5
                selected = [p for p, s in ranked[:5] if s > 0]
                if not selected:
                    selected = [p for p, _ in ranked[:3]]
                ai_reasons = {}
            for p in selected:
                content, truncated = await _fetch_file_content(owner, repo, branch, p)
                key_files.append({"path": p, "content": content, "truncated": truncated,
                                  "relevance": ranked_dict.get(p, 0.0),
                                  "reason": ai_reasons.get(p, "")})
        else:
            # 无 code_context：回退到原有固定选取逻辑
            for p in _pick_key_files(paths, tree):
                content, truncated = await _fetch_file_content(owner, repo, branch, p)
                key_files.append({"path": p, "content": content, "truncated": truncated})

        evidence_text = _assemble(owner, repo, branch, paths, key_files)

        # CI 自动验收证据（GitHub Actions build/test/lint），失败不阻塞主流程
        ci = await fetch_ci_evidence(owner, repo, branch)
        ci_text = ci.get("text", "")
        ci_block = (("\n\n" + ci_text) if ci_text else "")
        if not ci_text and not ci.get("ok"):
            ci_block = f"\n\n[CI] 获取自动验收证据失败：{ci.get('error', '未知')}（不影响代码证据）"
        if ci_block:
            evidence_text = evidence_text + ci_block

        result = {
            "ok": True, "repo": f"{owner}/{repo}", "default_branch": branch,
            "file_count": len(paths), "key_files": key_files,
            "evidence_text": evidence_text,
            "ci": ci if ci.get("ok") else {"ok": False, "code": ci.get("code", "CI_UNKNOWN"),
                                           "error": ci.get("error", ""), "text": ci_text},
        }
        if len(result["evidence_text"]) > EVIDENCE_CHAR_CAP:
            result["evidence_text"] = result["evidence_text"][:EVIDENCE_CHAR_CAP] + "\n…[证据过长已截断]"
        _cache[repo_url] = (now, result)
        return result
    except PermissionError as e:
        return {"ok": False, "code": "RATE_LIMITED", "error": str(e)}
    except FileNotFoundError as e:
        return {"ok": False, "code": "REPO_NOT_FOUND", "error": str(e)}
    except httpx.RequestError as e:
        return {"ok": False, "code": "NETWORK", "error": f"无法连接 GitHub：{type(e).__name__}"}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "code": "UNKNOWN", "error": f"拉取代码失败：{e}"}


def _assemble(owner: str, repo: str, branch: str, paths: list[str],
              key_files: list[dict]) -> str:
    head_paths = paths[:STRUCTURE_MAX]
    struct = "\n".join(f"- {p}" for p in head_paths)
    if len(paths) > STRUCTURE_MAX:
        struct += f"\n  …共 {len(paths)} 个文件（已截断）"

    parts = [
        f"GITHUB-REPO: {owner}/{repo}  (branch: {branch}, 共 {len(paths)} 个源码文件)",
        "文件结构（前若干个）:",
        struct,
    ]
    if key_files:
        parts.append("关键文件内容（供审阅，可能截断）:")
        for kf in key_files:
            parts.append(f"===== {kf['path']} =====")
            parts.append(kf["content"])
            if kf["truncated"]:
                parts.append("...[内容过长已截断（仅展示前 {} 行）]".format(FILE_LINES_MAX))

    text = "\n\n".join(parts)
    if len(text) > EVIDENCE_CHAR_CAP:
        text = text[:EVIDENCE_CHAR_CAP] + "\n…[证据过长已截断]"
    return text


def invalidate_cache(repo_url: str | None = None) -> None:
    """清缓存（测试/更新用）。"""
    if repo_url is None:
        _cache.clear()
    else:
        _cache.pop(repo_url, None)


# 便捷：结构化文件列表（供测试/前端展示）
def structure_listing(paths: list[str], cap: int = 100) -> list[str]:
    return paths[:cap]