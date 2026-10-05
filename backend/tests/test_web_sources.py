import unittest

from app.sources import WebPageSourceProvider


class WebPageSourceProviderTests(unittest.TestCase):
    def test_fetch_page_extracts_title_and_summary_without_network(self):
        html = """
        <html><head><title>Agent 工具调用更新</title></head>
        <body><h1>Agent 工具调用更新</h1><p>介绍结构化工具调用和权限边界。</p></body></html>
        """

        provider = WebPageSourceProvider(
            ["https://example.com/agent"],
            fetcher=lambda url: html,
        )

        sources = provider.discover("AI Agent")

        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0].title, "Agent 工具调用更新")
        self.assertIn("结构化工具调用", sources[0].summary)
        self.assertEqual(sources[0].url, "https://example.com/agent")


if __name__ == "__main__":
    unittest.main()
