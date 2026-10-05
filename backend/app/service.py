"""Application service combining task persistence and research execution."""

from __future__ import annotations

from app.research import Report, ResearchService
from app.store import TaskStore


class WorkbenchService:
    def __init__(self, store: TaskStore, research: ResearchService):
        self.store = store
        self.research = research

    def create_task(self, goal: str, schedule_time: str | None = None) -> dict:
        return self.store.create_task(goal, schedule_time)

    def run_task(self, task_id: str) -> Report:
        task = self.store.get_task(task_id)
        self.store.mark_running(task_id)
        try:
            report = self.research.run_now(task["goal"])
        except Exception:
            self.store.mark_failed(task_id)
            raise
        self.store.save_report(
            task_id,
            report.markdown,
            report.file_path,
            [source.__dict__ for source in report.sources],
        )
        self.store.mark_completed(task_id)
        return report
