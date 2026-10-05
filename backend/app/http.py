"""FastAPI adapter for the framework-independent WorkbenchApi."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.api import WorkbenchApi


class TaskRequest(BaseModel):
    goal: str
    schedule_time: str | None = None


def create_app(api: WorkbenchApi) -> FastAPI:
    app = FastAPI(title="Frontier AI Workbench", version="0.1.0")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.post("/api/tasks", status_code=201)
    def create_task(request: TaskRequest):
        try:
            return api.create_task(request.model_dump())
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

    @app.get("/api/tasks")
    def list_tasks():
        return api.service.store.list_tasks()

    @app.get("/api/tasks/{task_id}")
    def get_task(task_id: str):
        try:
            return api.get_task(task_id)
        except KeyError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error

    @app.post("/api/tasks/{task_id}/run")
    def run_task(task_id: str):
        try:
            return api.run_task(task_id)
        except KeyError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

    @app.get("/api/tasks/{task_id}/report")
    def get_report(task_id: str):
        try:
            return api.get_report(task_id)
        except KeyError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error

    return app
