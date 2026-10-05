import unittest

from app.research import Source
from app.sources import SourceCatalog


class FixedProvider:
    def __init__(self, sources):
        self.sources = sources

    def discover(self, goal: str):
        return self.sources


class SourceCatalogTests(unittest.TestCase):
    def test_discover_returns_unique_sources_from_all_providers(self):
        shared = Source("同一篇文章", "https://example.com/shared", "摘要", "2026-10-01")
        unique = Source("另一篇文章", "https://example.com/unique", "摘要", "2026-09-30")
        catalog = SourceCatalog([FixedProvider([shared]), FixedProvider([shared, unique])])

        sources = catalog.discover("AI Agent")

        self.assertEqual([source.url for source in sources], [shared.url, unique.url])


if __name__ == "__main__":
    unittest.main()
