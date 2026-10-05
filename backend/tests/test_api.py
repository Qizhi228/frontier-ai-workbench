import tempfile
import unittest
from pathlib import Path

from app.api import WorkbenchApi
from app.research import MockModel, MockSourceProvider, ResearchService
from app.service import WorkbenchService
from app.store import TaskStore


class WorkbenchApiTests(unittest.TestCase):
    def test_create_run_get_status_and_report(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            service = WorkbenchService(
                TaskStore(root / "workbench.sqlite3"),
                ResearchService(MockSourceProvider(), MockModel(), root / "reports"),
            )
            api = WorkbenchApi(service)

            created = api.create_task({"goal": "研究 AI Agent 趋势", "schedule_time": "09:00"})
            run_result = api.run_task(created["id"])
            status = api.get_task(created["id"])
            report = api.get_report(created["id"])

            self.assertEqual(run_result["status"], "completed")
            self.assertEqual(status["status"], "completed")
            self.assertIn("来源", report["markdown"])
            self.assertEqual(report["task_id"], created["id"])
            self.assertTrue(report["sources"])


if __name__ == "__main__":
    unittest.main()
