import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app.api import WorkbenchApi
from app.http import create_app
from app.research import MockModel, MockSourceProvider, ResearchService
from app.service import WorkbenchService
from app.store import TaskStore


class HttpApiTests(unittest.TestCase):
    def test_task_lifecycle_over_http(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            service = WorkbenchService(
                TaskStore(root / "workbench.sqlite3"),
                ResearchService(MockSourceProvider(), MockModel(), root / "reports"),
            )
            client = TestClient(create_app(WorkbenchApi(service)))

            created = client.post("/api/tasks", json={"goal": "研究 AI Agent 趋势"})
            task_id = created.json()["id"]
            executed = client.post(f"/api/tasks/{task_id}/run")
            report = client.get(f"/api/tasks/{task_id}/report")

            self.assertEqual(created.status_code, 201)
            self.assertEqual(executed.status_code, 200)
            self.assertEqual(executed.json()["status"], "completed")
            self.assertEqual(report.status_code, 200)
            self.assertIn("来源", report.json()["markdown"])


if __name__ == "__main__":
    unittest.main()
