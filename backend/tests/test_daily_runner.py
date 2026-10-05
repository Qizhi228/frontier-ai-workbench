import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from app.daily import DailyTaskRunner
from app.research import MockModel, MockSourceProvider, ResearchService
from app.service import WorkbenchService
from app.store import TaskStore


class DailyTaskRunnerTests(unittest.TestCase):
    def test_daily_task_runs_once_at_configured_time(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            store = TaskStore(root / "workbench.sqlite3")
            service = WorkbenchService(store, ResearchService(MockSourceProvider(), MockModel(), root / "reports"))
            task = service.create_task("每日 AI 技术简报", "09:00")
            runner = DailyTaskRunner(store, service)
            now = datetime(2026, 10, 5, 9, 0, tzinfo=timezone.utc)

            first = runner.run_due(now)
            second = runner.run_due(now)

            self.assertEqual(first, [task["id"]])
            self.assertEqual(second, [])
            self.assertEqual(store.get_task(task["id"])["status"], "completed")


if __name__ == "__main__":
    unittest.main()
