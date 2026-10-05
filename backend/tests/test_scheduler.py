import unittest
from datetime import datetime, timezone

from app.scheduler import ScheduledTask, TaskScheduler


class TaskSchedulerTests(unittest.TestCase):
    def test_run_due_once_only_runs_tasks_due_at_or_before_now(self):
        calls = []

        def run_task(goal: str) -> None:
            calls.append(goal)

        due = ScheduledTask(
            task_id="due",
            goal="AI Agent 工具调用",
            next_run_at=datetime(2026, 10, 5, 9, 0, tzinfo=timezone.utc),
        )
        future = ScheduledTask(
            task_id="future",
            goal="未来主题",
            next_run_at=datetime(2026, 10, 5, 11, 0, tzinfo=timezone.utc),
        )
        scheduler = TaskScheduler([due, future], run_task)

        executed = scheduler.run_due_once(datetime(2026, 10, 5, 10, 0, tzinfo=timezone.utc))

        self.assertEqual(executed, ["due"])
        self.assertEqual(calls, ["AI Agent 工具调用"])
        self.assertIsNotNone(due.last_run_at)
        self.assertIsNone(future.last_run_at)


if __name__ == "__main__":
    unittest.main()
