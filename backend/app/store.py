"""SQLite persistence for single-user workbench tasks and reports."""

from __future__ import annotations

import sqlite3
import json
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


class TaskStore:
    def __init__(self, database_path: Path):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @contextmanager
    def _connection(self):
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    goal TEXT NOT NULL,
                    schedule_time TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_run_at TEXT
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS reports (
                    task_id TEXT PRIMARY KEY,
                    markdown TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    sources_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            columns = {row[1] for row in connection.execute("PRAGMA table_info(reports)").fetchall()}
            if "sources_json" not in columns:
                connection.execute("ALTER TABLE reports ADD COLUMN sources_json TEXT NOT NULL DEFAULT '[]'")

    def create_task(self, goal: str, schedule_time: str | None = None) -> dict:
        clean_goal = goal.strip()
        if not clean_goal:
            raise ValueError("任务目标不能为空")
        task = {
            "id": uuid.uuid4().hex,
            "goal": clean_goal,
            "schedule_time": schedule_time,
            "status": "ready",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_run_at": None,
        }
        with self._connection() as connection:
            connection.execute(
                "INSERT INTO tasks (id, goal, schedule_time, status, created_at, last_run_at) VALUES (?, ?, ?, ?, ?, ?)",
                tuple(task.values()),
            )
        return task

    def get_task(self, task_id: str) -> dict:
        with self._connection() as connection:
            row = connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if row is None:
            raise KeyError(f"任务不存在：{task_id}")
        return dict(row)

    def list_tasks(self) -> list[dict]:
        with self._connection() as connection:
            rows = connection.execute("SELECT * FROM tasks ORDER BY created_at DESC").fetchall()
        return [dict(row) for row in rows]

    def mark_running(self, task_id: str) -> None:
        self._update_status(task_id, "running")

    def mark_completed(self, task_id: str) -> None:
        self._update_status(task_id, "completed")

    def mark_failed(self, task_id: str) -> None:
        self._update_status(task_id, "failed")

    def set_last_run_at(self, task_id: str, when) -> None:
        with self._connection() as connection:
            cursor = connection.execute("UPDATE tasks SET last_run_at = ? WHERE id = ?", (when.isoformat(), task_id))
            if cursor.rowcount != 1:
                raise KeyError(f"任务不存在：{task_id}")

    def _update_status(self, task_id: str, status: str) -> None:
        with self._connection() as connection:
            cursor = connection.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
            if cursor.rowcount != 1:
                raise KeyError(f"任务不存在：{task_id}")

    def save_report(self, task_id: str, markdown: str, file_path: Path, sources: list[dict]) -> None:
        with self._connection() as connection:
            connection.execute(
                "INSERT OR REPLACE INTO reports (task_id, markdown, file_path, sources_json, created_at) VALUES (?, ?, ?, ?, ?)",
                (task_id, markdown, str(file_path), json.dumps(sources, ensure_ascii=False), datetime.now(timezone.utc).isoformat()),
            )

    def get_report(self, task_id: str) -> dict:
        with self._connection() as connection:
            row = connection.execute("SELECT * FROM reports WHERE task_id = ?", (task_id,)).fetchone()
        if row is None:
            raise KeyError(f"报告不存在：{task_id}")
        result = dict(row)
        result["sources"] = json.loads(result.pop("sources_json"))
        return result
