import tempfile
import unittest
from pathlib import Path

from app.research import MockModel, MockSourceProvider, ResearchService


class ResearchServiceTests(unittest.TestCase):
    def test_run_now_creates_cited_report_and_saves_markdown(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            service = ResearchService(
                source_provider=MockSourceProvider(),
                model=MockModel(),
                report_dir=Path(temp_dir),
            )

            report = service.run_now("AI Agent 工具调用")

            self.assertEqual(report.goal, "AI Agent 工具调用")
            self.assertTrue(report.sources)
            self.assertIn("AI Agent 工具调用", report.markdown)
            self.assertIn("来源", report.markdown)
            self.assertIsNotNone(report.file_path)
            self.assertTrue(report.file_path.exists())
            self.assertIn("为什么重要", report.markdown)
            self.assertIn("介绍工具调用", report.markdown)


if __name__ == "__main__":
    unittest.main()
