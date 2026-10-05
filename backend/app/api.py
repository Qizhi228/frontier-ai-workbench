"""Framework-independent application API facade."""

from __future__ import annotations

from app.service import WorkbenchService


class WorkbenchApi:
    def __init__(self, service: WorkbenchService):
        self.service = service

    def create_task(self, payload: dict) -> dict:
        return self.service.create_task(payload.get("goal", ""), payload.get("schedule_time"))

    def run_task(self, task_id: str) -> dict:
        report = self.service.run_task(task_id)
        return {"task_id": task_id, "status": "completed", "report": report.markdown}

    def get_task(self, task_id: str) -> dict:
        return self.service.store.get_task(task_id)

    def get_report(self, task_id: str) -> dict:
        report = self.service.store.get_report(task_id)
        report["task_id"] = task_id
        return report
