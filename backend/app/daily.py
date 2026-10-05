"""Daily scheduled research runner."""

from __future__ import annotations

from datetime import datetime

from app.service import WorkbenchService
from app.store import TaskStore


class DailyTaskRunner:
    def __init__(self, store: TaskStore, service: WorkbenchService):
        self.store = store
        self.service = service

    def run_due(self, now: datetime) -> list[str]:
        executed: list[str] = []
        current_time = now.strftime("%H:%M")
        current_day = now.date().isoformat()
        for task in self.store.list_tasks():
            if not task.get("schedule_time") or task["schedule_time"] > current_time:
                continue
            last_run_at = task.get("last_run_at")
            if last_run_at and last_run_at[:10] == current_day:
                continue
            self.service.run_task(task["id"])
            self._mark_last_run(task["id"], now)
            executed.append(task["id"])
        return executed

    def _mark_last_run(self, task_id: str, now: datetime) -> None:
        self.store.set_last_run_at(task_id, now)
