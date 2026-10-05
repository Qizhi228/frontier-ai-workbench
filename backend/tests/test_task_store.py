import tempfile
import unittest
from pathlib import Path

from app.store import TaskStore


class TaskStoreTests(unittest.TestCase):
    def test_create_and_get_task_persist_goal_and_schedule(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = TaskStore(Path(temp_dir) / "workbench.sqlite3")

            created = store.create_task("研究 AI Agent 趋势", "09:00")
            loaded = store.get_task(created["id"])

            self.assertEqual(loaded["goal"], "研究 AI Agent 趋势")
            self.assertEqual(loaded["schedule_time"], "09:00")
            self.assertEqual(loaded["status"], "ready")


if __name__ == "__main__":
    unittest.main()
