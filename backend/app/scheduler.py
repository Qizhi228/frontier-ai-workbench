"""Simple daily task scheduler public seam."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable


@dataclass
class ScheduledTask:
    task_id: str
    goal: str
    next_run_at: datetime
    enabled: bool = True
    last_run_at: datetime | None = None


class TaskScheduler:
    def __init__(self, tasks: list[ScheduledTask], run_task: Callable[[str], None]):
        self.tasks = tasks
        self.run_task = run_task

    def run_due_once(self, now: datetime) -> list[str]:
        executed: list[str] = []
        for task in self.tasks:
            if not task.enabled or task.next_run_at > now:
                continue
            self.run_task(task.goal)
            task.last_run_at = now
            task.next_run_at = task.next_run_at + timedelta(days=1)
            executed.append(task.task_id)
        return executed
