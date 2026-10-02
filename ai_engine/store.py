# -*- coding: utf-8 -*-
"""
SQLite 持久化封装（v1.1 Part B）：会话真相源 / 评审幂等缓存 / 评审失败熔断 / Evidence Store。

设计约定（方案 §3.3 / §4 / §5）：
  - DB 路径环境变量可覆盖：XKZ_DB_PATH；默认服务端 /opt/xkz-agent/data/engine.db，
    本地开发 data/engine.db（相对于本模块向上两级）。
  - 启动只建表，不做内存→SQLite 迁移（内存 dict 重启本就为空）。
  - 并发：单写连接 + WAL，读写都走同一连接（uvicorn 单 worker / SQLite 串行即可）；
    busy_timeout=30 兜底跨进程（如手动 sqlite3 工具）。
  - review_results 永久幂等（版本化 key），懒清理 >90 天 / 每任务保留最近 200 条；
  - review_failures 按 retry_after 惰性过期删除（5 分钟熔断）。
  - evidence 按 task_id 追加（进程内存 _evidence_store 的直接替代）。
"""
from __future__ import annotations

import json
import os
import sqlite3
import threading
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

from schemas import AISession, DebuggerState, Evidence, Submission

TZ = timezone(timedelta(hours=8))

# 版本常量（评审 key/data 字段；改 rubric/prompt/聚合逻辑时必须手动 bump）
REVIEW_RUBRIC_VERSION = "2"    # Rubric 数据规则版本（v2：新增 evaluation_role 角色分桶）
REVIEW_PROMPT_VERSION = "1"    # Review Prompt 版本
REVIEW_ENGINE_VERSION = "2"    # 聚合/Key 算法版本（v2：按 acceptance/theory/reflection 三分桶）

# 清理阈值
REVIEW_RESULTS_KEEP_DAYS = 90          # review_results 软保留天数
REVIEW_RESULTS_KEEP_PER_TASK = 200     # 每任务软保留条数
FAILURE_TTL = 300                      # 评审失败熔断 TTL（秒）


def default_db_path() -> Path:
    env = os.environ.get("XKZ_DB_PATH")
    if env:
        return Path(env)
    # ai_engine/store.py -> 项目根/data/engine.db
    return Path(__file__).resolve().parent.parent / "data" / "engine.db"


class _KV:  # 版本化评审 key 组合工具
    """review_results / review_failures 共用：6 元组 → 幂等 key。"""

    @staticmethod
    def fields(task_id: str, snapshot_hash: str, model: str) -> tuple[str, str, str, str, dict]:
        payload = {
            "task_id": task_id,
            "snapshot_hash": snapshot_hash,
            "rubric_version": REVIEW_RUBRIC_VERSION,
            "prompt_version": REVIEW_PROMPT_VERSION,
            "engine_version": REVIEW_ENGINE_VERSION,
            "model": model,
        }
        # review_failures 的主键：散列 6 字段，避免超长主键（TEXT PK 可容纳，散列更紧凑）
        key = f"{task_id}:{snapshot_hash}:{REVIEW_RUBRIC_VERSION}:{REVIEW_PROMPT_VERSION}:{REVIEW_ENGINE_VERSION}:{model}"
        return key, payload.get("rubric_version"), payload.get("prompt_version"), payload.get("engine_version"), payload


class Store:
    def __init__(self, db_path: str | Path | None = None):
        self._lock = threading.Lock()
        self.path = Path(db_path) if db_path else default_db_path()
        self._conn: sqlite3.Connection | None = None
        self._open()

    # ------------------------------------------------------------------
    # 连接与建表
    # ------------------------------------------------------------------
    def _open(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=30000")
        conn.execute("PRAGMA synchronous=NORMAL")
        self._conn = conn
        self._create_tables()

    def _ensure_column(self, table: str, column: str, decl: str) -> None:
        """轻量列迁移：表已存在但缺列时补上（CREATE TABLE IF NOT EXISTS 不会加列）。"""
        cols = {r["name"] for r in self._fetchall(f"PRAGMA table_info({table})")}
        if column not in cols:
            self._exec(f"ALTER TABLE {table} ADD COLUMN {column} {decl}")

    def _create_tables(self) -> None:
        self._exec("""
        CREATE TABLE IF NOT EXISTS sessions (
          session_key      TEXT PRIMARY KEY,
          session_id       TEXT NOT NULL,
          student_id       TEXT NOT NULL,
          task_id          TEXT NOT NULL,
          mode             TEXT NOT NULL,
          hint_level       INTEGER DEFAULT 0,
          history_json     TEXT DEFAULT '[]',
          debug_state_json TEXT,
          summary_json     TEXT,
          last_system_error TEXT,
          attempt_count    TEXT,
          created_at       TEXT NOT NULL,
          updated_at       TEXT NOT NULL
        )
        """)
        self._exec("""
        CREATE TABLE IF NOT EXISTS review_results (
          id             INTEGER PRIMARY KEY AUTOINCREMENT,
          task_id        TEXT NOT NULL,
          snapshot_hash  TEXT NOT NULL,
          rubric_version TEXT NOT NULL,
          prompt_version TEXT NOT NULL,
          engine_version TEXT NOT NULL,
          model          TEXT NOT NULL,
          response_json  TEXT NOT NULL,
          created_at     TEXT NOT NULL
        )
        """)
        self._exec("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_review_result_key ON review_results(
          task_id, snapshot_hash, rubric_version, prompt_version, engine_version, model)
        """)
        self._exec("""
        CREATE TABLE IF NOT EXISTS review_failures (
          review_key  TEXT PRIMARY KEY,
          retry_after REAL NOT NULL,
          error       TEXT,
          created_at  TEXT NOT NULL
        )
        """)
        self._exec("""
        CREATE TABLE IF NOT EXISTS evidence (
          id TEXT PRIMARY KEY, task_id TEXT NOT NULL, rubric_id TEXT DEFAULT '',
          type TEXT NOT NULL, source TEXT DEFAULT '', content TEXT DEFAULT '',
          confidence REAL DEFAULT 1.0, created_at TEXT NOT NULL
        )
        """)
        self._exec("CREATE INDEX IF NOT EXISTS idx_evidence_task ON evidence(task_id, rubric_id)")

        # P2：学生身份 / 提交历史 / 评审历史（与 review_results 幂等缓存分离）——
        #   students      ：稳定学生的档案（student_id 为主键）
        #   submissions   ：每一次提交都是独立事件（含 head_sha，供 P3 修订比对）
        #   evaluations   ：评审历史（每份提交一行；review_results 只是"同输入同输出"的缓存）
        self._exec("""
        CREATE TABLE IF NOT EXISTS students (
          student_id TEXT PRIMARY KEY,
          name       TEXT DEFAULT '匿名学生',
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL
        )
        """)
        self._exec("""
        CREATE TABLE IF NOT EXISTS submissions (
          id                   TEXT PRIMARY KEY,
          student_id           TEXT NOT NULL,
          task_id              TEXT NOT NULL,
          project_id           TEXT DEFAULT '',
          github_url           TEXT DEFAULT '',
          deployment_url       TEXT DEFAULT '',
          code                 TEXT DEFAULT '',
          description          TEXT DEFAULT '',
          head_sha             TEXT DEFAULT '',
          parent_submission_id TEXT DEFAULT '',
          revision_json        TEXT DEFAULT '',
          submitted_at         TEXT NOT NULL
        )
        """)
        self._exec(
            "CREATE INDEX IF NOT EXISTS idx_submissions_student_task "
            "ON submissions(student_id, task_id, submitted_at)")
        self._exec("""
        CREATE TABLE IF NOT EXISTS evaluations (
          submission_id  TEXT PRIMARY KEY,
          student_id     TEXT NOT NULL,
          task_id        TEXT NOT NULL,
          project_id     TEXT DEFAULT '',
          snapshot_hash  TEXT DEFAULT '',
          rubric_version TEXT DEFAULT '',
          prompt_version TEXT DEFAULT '',
          engine_version TEXT DEFAULT '',
          model          TEXT DEFAULT '',
          status         TEXT NOT NULL,
          score          INTEGER DEFAULT 0,
          passed         INTEGER DEFAULT 0,
          ci_conclusion  TEXT DEFAULT '',
          head_sha       TEXT DEFAULT '',
          revision_json  TEXT DEFAULT '',
          criteria_json  TEXT DEFAULT '{}',
          created_at     TEXT NOT NULL
        )
        """)
        self._exec(
            "CREATE INDEX IF NOT EXISTS idx_evaluations_student_task "
            "ON evaluations(student_id, task_id, created_at)")
        # 轻量列迁移：表已存在时 CREATE TABLE IF NOT EXISTS 不会补列（P3 新增 revision_json）
        self._ensure_column("submissions", "revision_json", "TEXT DEFAULT ''")
        self._ensure_column("evaluations", "revision_json", "TEXT DEFAULT ''")
        # P6：简历/复盘需要"该次提交的 CI 结论"（确定性数据，避免只存在于前端 localStorage）
        self._ensure_column("evaluations", "ci_conclusion", "TEXT DEFAULT ''")

    def _exec(self, sql: str, params: tuple = ()) -> None:
        with self._lock:
            self._conn.execute(sql, params)
            self._conn.commit()

    def _fetchone(self, sql: str, params: tuple = ()) -> sqlite3.Row | None:
        with self._lock:
            cur = self._conn.execute(sql, params)
            return cur.fetchone()

    def _fetchall(self, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
        with self._lock:
            cur = self._conn.execute(sql, params)
            return cur.fetchall()

    # ------------------------------------------------------------------
    # Sessions（真相源）
    # ------------------------------------------------------------------
    def get_session(self, session_key: str) -> AISession | None:
        row = self._fetchone(
            "SELECT * FROM sessions WHERE session_key=?", (session_key,))
        if not row:
            return None
        sess = AISession(
            session_id=row["session_id"],
            student_id=row["student_id"],
            task_id=row["task_id"],
            mode=row["mode"],
            attempt_count=int(row["attempt_count"] or 0),
            hint_level=row["hint_level"] or 0,
            history=json.loads(row["history_json"] or "[]"),
            created_at=row["created_at"],
        )
        if row["debug_state_json"]:
            try:
                sess.debug_state = DebuggerState.model_validate_json(row["debug_state_json"])
            except Exception:  # noqa: BLE001 — 状态损坏不阻塞会话恢复
                sess.debug_state = None
        sess.last_system_error = row["last_system_error"] or None
        return sess

    def save_session(self, sess: AISession) -> None:
        """Upsert 会话快照（调用方在修改完 sess 后调用）。"""
        skey = f"{sess.session_id}:{sess.task_id}"
        now = datetime.now(TZ).isoformat(timespec="seconds")
        self._exec(
            """
            INSERT INTO sessions (session_key, session_id, student_id, task_id, mode,
                                  hint_level, history_json, debug_state_json, summary_json,
                                  last_system_error, attempt_count, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(session_key) DO UPDATE SET
              hint_level=excluded.hint_level,
              history_json=excluded.history_json,
              debug_state_json=excluded.debug_state_json,
              last_system_error=excluded.last_system_error,
              attempt_count=excluded.attempt_count,
              mode=excluded.mode,
              updated_at=excluded.updated_at
            """,
            (skey, sess.session_id, sess.student_id, sess.task_id,
             sess.mode.value if hasattr(sess.mode, "value") else str(sess.mode),
             sess.hint_level, json.dumps(sess.history, ensure_ascii=False),
             sess.debug_state.model_dump_json() if sess.debug_state else None,
             None,  # summary_json：V1 不做 LLM 摘要，留空
             sess.last_system_error, str(sess.attempt_count),
             sess.created_at, now),
        )

    def session_history(self, session_key: str) -> dict | None:
        """GET /api/ai/session_history 数据源：历史 + 结构化状态。"""
        sess = self.get_session(session_key)
        if not sess:
            return None
        return {
            "session_id": sess.session_id,
            "task_id": sess.task_id,
            "mode": sess.mode.value if hasattr(sess.mode, "value") else str(sess.mode),
            "hint_level": sess.hint_level,
            "history": sess.history,
            "debug_state": {
                "rounds": sess.debug_state.rounds,
                "phase": sess.debug_state.phase.value,
                "phase_desc": "",
                "last_diagnostic_question": sess.debug_state.last_diagnostic_question,
                "last_suspected_cause": sess.debug_state.last_suspected_cause,
            } if sess.debug_state else None,
            "last_system_error": sess.last_system_error,
            "updated_at": None,  # 内部占位；展示用优化可复用 get_session
        }

    # ------------------------------------------------------------------
    # Review：成功幂等缓存 + 失败熔断
    # ------------------------------------------------------------------
    def get_review_result(self, task_id: str, snapshot_hash: str, model: str) -> dict | None:
        _, rv, pv, ev_, _ = _KV.fields(task_id, snapshot_hash, model)
        row = self._fetchone(
            "SELECT response_json FROM review_results "
            "WHERE task_id=? AND snapshot_hash=? AND rubric_version=? "
            "AND prompt_version=? AND engine_version=? AND model=?",
            (task_id, snapshot_hash, rv, pv, ev_, model))
        if not row:
            return None
        try:
            return json.loads(row["response_json"])
        except json.JSONDecodeError:
            return None

    def save_review_result(self, task_id: str, snapshot_hash: str, model: str,
                           response: dict) -> None:
        _, rv, pv, ev_, _ = _KV.fields(task_id, snapshot_hash, model)
        now = datetime.now(TZ).isoformat(timespec="seconds")
        self._exec(
            "INSERT OR REPLACE INTO review_results "
            "(task_id, snapshot_hash, rubric_version, prompt_version, engine_version, model, response_json, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (task_id, snapshot_hash, rv, pv, ev_, model,
             json.dumps(response, ensure_ascii=False), now))

    def get_review_failure(self, task_id: str, snapshot_hash: str, model: str) -> str | None:
        """熔断查询：未过期返回错误信息（触发熔断），过期删除并返回 None。"""
        key, _, _, _, _ = _KV.fields(task_id, snapshot_hash, model)
        row = self._fetchone(
            "SELECT retry_after, error FROM review_failures WHERE review_key=?", (key,))
        if not row:
            return None
        if time.time() >= row["retry_after"]:
            self._exec("DELETE FROM review_failures WHERE review_key=?", (key,))
            return None
        return row["error"] or "评审临时不可用"

    def save_review_failure(self, task_id: str, snapshot_hash: str, model: str,
                            error: str | None = None) -> None:
        key, _, _, _, _ = _KV.fields(task_id, snapshot_hash, model)
        now_ts = time.time()
        now = datetime.now(TZ).isoformat(timespec="seconds")
        self._exec(
            "INSERT OR REPLACE INTO review_failures (review_key, retry_after, error, created_at) "
            "VALUES (?, ?, ?, ?)",
            (key, now_ts + FAILURE_TTL, (error or "")[:500], now))

    # ------------------------------------------------------------------
    # Evidence（替代进程内存 _evidence_store）
    # ------------------------------------------------------------------
    def add_evidence(self, ev: Evidence) -> None:
        self._exec(
            "INSERT OR REPLACE INTO evidence (id, task_id, rubric_id, type, source, content, confidence, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (ev.id, ev.task_id, ev.rubric_id,
             ev.type.value if hasattr(ev.type, "value") else str(ev.type),
             ev.source, ev.content, ev.confidence, ev.created_at))

    def list_evidence(self, task_id: str, rubric_id: str | None = None) -> list[Evidence]:
        if rubric_id:
            rows = self._fetchall(
                "SELECT * FROM evidence WHERE task_id=? AND rubric_id=? ORDER BY created_at",
                (task_id, rubric_id))
        else:
            rows = self._fetchall(
                "SELECT * FROM evidence WHERE task_id=? ORDER BY created_at", (task_id,))
        out = []
        for r in rows:
            try:
                out.append(Evidence(
                    id=r["id"], task_id=r["task_id"], rubric_id=r["rubric_id"],
                    type=r["type"], source=r["source"], content=r["content"],
                    confidence=r["confidence"], created_at=r["created_at"],
                ))
            except Exception:  # noqa: BLE001 — 单条损坏不阻塞列表
                continue
        return out

    # ------------------------------------------------------------------
    # P2：学生 / 提交 / 评审历史（与 review_results 幂等缓存分离）
    # ------------------------------------------------------------------
    def upsert_student(self, student_id: str, name: str | None = None) -> None:
        """建档：name 为 None 时只保证"存在"（评审链不会覆盖已存姓名）；显式给 name 时才更新。"""
        if not student_id:
            return
        now = datetime.now(TZ).isoformat(timespec="seconds")
        if name is None:
            self._exec(
                "INSERT OR IGNORE INTO students (student_id, name, created_at, updated_at) "
                "VALUES (?, ?, ?, ?)",
                (student_id, "匿名学生", now, now))
            return
        self._exec(
            "INSERT INTO students (student_id, name, created_at, updated_at) VALUES (?, ?, ?, ?) "
            "ON CONFLICT(student_id) DO UPDATE SET name=excluded.name, updated_at=excluded.updated_at",
            (student_id, name or "匿名学生", now, now))

    def save_submission(self, sub: Submission) -> None:
        """每一份提交都是独立历史事件（同 id 覆盖，新提交新增）。"""
        self._exec(
            "INSERT OR REPLACE INTO submissions "
            "(id, student_id, task_id, project_id, github_url, deployment_url, code, description, "
            " head_sha, parent_submission_id, revision_json, submitted_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (sub.id, sub.student_id, sub.task_id, sub.project_id, sub.github_url,
             sub.deployment_url, sub.code, sub.description, sub.head_sha,
             sub.parent_submission_id, sub.revision_json, sub.submitted_at))

    def latest_submission(self, student_id: str, task_id: str) -> dict | None:
        row = self._fetchone(
            "SELECT * FROM submissions WHERE student_id=? AND task_id=? "
            "ORDER BY submitted_at DESC, rowid DESC LIMIT 1",
            (student_id, task_id))
        return dict(row) if row else None

    def list_submissions(self, student_id: str, task_id: str, limit: int = 50) -> list[dict]:
        rows = self._fetchall(
            "SELECT * FROM submissions WHERE student_id=? AND task_id=? "
            "ORDER BY submitted_at DESC, rowid DESC LIMIT ?",
            (student_id, task_id, limit))
        return [dict(r) for r in rows]

    def save_evaluation(self, *, submission_id: str, student_id: str, task_id: str,
                        project_id: str = "", snapshot_hash: str = "", model: str = "",
                        status: str = "NEED_REVIEW", score: int = 0, passed: bool = False,
                        ci_conclusion: str = "",
                        head_sha: str = "", revision_json: str = "",
                        criteria: dict | None = None) -> None:
        """评审历史：按 submission_id 幂等写入（同一提交重复评审覆盖，不新增行）。"""
        now = datetime.now(TZ).isoformat(timespec="seconds")
        self._exec(
            "INSERT OR REPLACE INTO evaluations "
            "(submission_id, student_id, task_id, project_id, snapshot_hash, rubric_version, "
            " prompt_version, engine_version, model, status, score, passed, ci_conclusion, head_sha, "
            " revision_json, criteria_json, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (submission_id, student_id, task_id, project_id, snapshot_hash,
             REVIEW_RUBRIC_VERSION, REVIEW_PROMPT_VERSION, REVIEW_ENGINE_VERSION, model,
             status, int(score), 1 if passed else 0, ci_conclusion, head_sha, revision_json or "",
             json.dumps(criteria or {}, ensure_ascii=False), now))

    def list_evaluations(self, student_id: str, task_id: str, limit: int = 50) -> list[dict]:
        rows = self._fetchall(
            "SELECT submission_id, status, score, passed, head_sha, created_at FROM evaluations "
            "WHERE student_id=? AND task_id=? ORDER BY created_at DESC LIMIT ?",
            (student_id, task_id, limit))
        return [dict(r) for r in rows]

    def latest_evaluations(self, student_id: str, task_ids: list[str]) -> dict[str, dict]:
        """P4：批量取"每个任务的最新一次评审结果"（project_state 聚合的数据源）。

        created_at 只到秒级，同秒内多次提交/评审顺序不可靠，故按 (created_at, rowid) 升序
        取全部候选后在 Python 侧归并（后写覆盖先写 = 取最新）。
        """
        ids = [t for t in dict.fromkeys(task_ids) if t]
        if not student_id or not ids:
            return {}
        placeholders = ",".join("?" for _ in ids)
        rows = self._fetchall(
            f"SELECT rowid AS rid, task_id, status, score, passed, created_at FROM evaluations "
            f"WHERE student_id=? AND task_id IN ({placeholders}) "
            f"ORDER BY created_at ASC, rowid ASC",
            (student_id, *ids))
        out: dict[str, dict] = {}
        for r in rows:
            out[r["task_id"]] = {
                "status": r["status"] or "",
                "score": r["score"] or 0,
                "passed": bool(r["passed"]),
                "created_at": r["created_at"],
            }
        return out

    def list_session_task_ids(self, student_id: str) -> list[str]:
        """P5：该学生实际接触过的任务（sessions 表 → Learner State 的 EXPOSED 依据）。"""
        if not student_id:
            return []
        rows = self._fetchall(
            "SELECT DISTINCT task_id FROM sessions WHERE student_id=? AND task_id<>''",
            (student_id,))
        return [r["task_id"] for r in rows]

    def list_student_evaluations(self, student_id: str, limit: int = 500) -> list[dict]:
        """P5：学生全部评审历史（按时间升序；Learner State / Learning Gap 的读侧数据源）。

        每份提交只有一行（submission_id 为主键、INSERT OR REPLACE），
        因此"缺口出现次数"天然按提交去重，不会因幂等缓存命中和重试被重复计数。
        """
        if not student_id:
            return []
        rows = self._fetchall(
            "SELECT task_id, status, score, passed, criteria_json, created_at "
            "FROM evaluations WHERE student_id=? ORDER BY created_at ASC, rowid ASC LIMIT ?",
            (student_id, limit))
        return [dict(r) for r in rows]

    def latest_project_evaluations(self, student_id: str, project_id: str) -> list[dict]:
        """P6：本项目"每个任务最新一次评审"（简历历史结果 / 项目复盘的读侧数据源）。

        与 latest_evaluations 同理：created_at 只到秒，同秒内多次评审顺序不可靠，
        故按 (created_at, rowid) 升序全取后在 Python 侧归并（后写覆盖先写 = 取最新）。
        """
        if not student_id or not project_id:
            return []
        rows = self._fetchall(
            "SELECT rowid AS rid, submission_id, task_id, status, score, passed, ci_conclusion, "
            "criteria_json, head_sha, created_at FROM evaluations "
            "WHERE student_id=? AND project_id=? ORDER BY created_at ASC, rowid ASC",
            (student_id, project_id))
        latest: dict[str, dict] = {}
        for r in rows:
            latest[r["task_id"]] = dict(r)
        return list(latest.values())

    def list_project_submissions(self, student_id: str, project_id: str, limit: int = 200) -> list[dict]:
        """P6：本项目全部提交事件（附其评审结论）——项目复盘的时间线数据源。"""
        if not student_id or not project_id:
            return []
        rows = self._fetchall(
            "SELECT s.id AS submission_id, s.task_id, s.submitted_at, s.parent_submission_id, "
            "s.head_sha AS sub_head_sha, s.revision_json AS sub_revision_json, "
            "e.status, e.score, e.passed, e.ci_conclusion, "
            "e.head_sha AS eval_head_sha, e.revision_json AS eval_revision_json, "
            "e.created_at AS evaluated_at "
            "FROM submissions s LEFT JOIN evaluations e ON e.submission_id = s.id "
            "WHERE s.student_id=? AND s.project_id=? "
            "ORDER BY s.submitted_at ASC, s.rowid ASC LIMIT ?",
            (student_id, project_id, limit))
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------
    # 惰性清理（每次调用某表前顺带触发；不做后台任务）
    # ------------------------------------------------------------------
    def lazy_cleanup(self) -> None:
        """在 teach/review 入口调用：成本极低（单次 DELETE），幂等。
        review_failures 清过期；review_results 清 >90 天 + 每任务保留最近 200 条。
        """
        with self._lock:
            conn = self._conn
            try:
                conn.execute("DELETE FROM review_failures WHERE retry_after < ?", (time.time(),))
                cutoff = (datetime.now(TZ) - timedelta(days=REVIEW_RESULTS_KEEP_DAYS)).isoformat(timespec="seconds")
                conn.execute(
                    "DELETE FROM review_results WHERE created_at < ?", (cutoff,))
                # 每任务软保留最近 REVIEW_RESULTS_KEEP_PER_TASK 条（保留最新行）
                conn.execute(
                    """
                    DELETE FROM review_results WHERE id NOT IN (
                      SELECT id FROM (
                        SELECT id, ROW_NUMBER() OVER (PARTITION BY task_id ORDER BY id DESC) AS rn
                        FROM review_results
                      ) WHERE rn <= ?
                    )
                    """, (REVIEW_RESULTS_KEEP_PER_TASK,))
                conn.commit()
            except Exception:  # noqa: BLE001 — 清理失败不影响主流程
                conn.rollback()


# 全局单例（模块导入即建表）
store = Store()