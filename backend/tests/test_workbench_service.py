import tempfile
import unittest
from pathlib import Path

from app.research import MockModel, MockSourceProvider, ResearchService
from app.service import WorkbenchService
from app.store import TaskStore


class WorkbenchServiceTests(unittest.TestCase):
    def test_run_task_completes_and_creates_report(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            store = TaskStore(root / "workbench.sqlite3")
            research = ResearchService(MockSourceProvider(), MockModel(), root / "reports")
            service = WorkbenchService(store, research)
            task = service.create_task("研究 AI Agent 趋势")

            report = service.run_task(task["id"])

            self.assertEqual(store.get_task(task["id"])["status"], "completed")
            self.assertTrue(report.file_path.exists())
            self.assertEqual(report.goal, "研究 AI Agent 趋势")


if __name__ == "__main__":
    unittest.main()
