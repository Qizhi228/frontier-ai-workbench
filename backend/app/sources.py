"""Source adapters and catalog."""

from __future__ import annotations

from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.request import Request, urlopen

from app.research import Source


class SourceCatalog:
    def __init__(self, providers):
        self.providers = list(providers)

    def discover(self, goal: str) -> list[Source]:
        unique: list[Source] = []
        seen: set[str] = set()
        for provider in self.providers:
            for source in provider.discover(goal):
                if source.url in seen:
                    continue
                seen.add(source.url)
                unique.append(source)
        return unique


class _PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title_parts: list[str] = []
        self.heading_parts: list[str] = []
        self.paragraph_parts: list[str] = []
        self._active: str | None = None

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self._active = "title"
        elif tag in {"h1", "h2"}:
            self._active = "heading"
        elif tag == "p":
            self._active = "paragraph"

    def handle_endtag(self, tag):
        if tag in {"title", "h1", "h2", "p"}:
            self._active = None

    def handle_data(self, data):
        text = " ".join(data.split())
        if not text:
            return
        if self._active == "title":
            self.title_parts.append(text)
        elif self._active == "heading":
            self.heading_parts.append(text)
        elif self._active == "paragraph":
            self.paragraph_parts.append(text)


class WebPageSourceProvider:
    def __init__(self, urls: list[str], fetcher=None):
        self.urls = urls
        self.fetcher = fetcher or self._fetch

    def discover(self, goal: str) -> list[Source]:
        sources = []
        for url in self.urls:
            try:
                html = self.fetcher(url)
                parser = _PageParser()
                parser.feed(html)
                title = "".join(parser.heading_parts or parser.title_parts).strip() or url
                summary = " ".join(parser.paragraph_parts)[:280] or f"待进一步阅读：{goal}"
                sources.append(Source(title, url, summary, datetime.now(timezone.utc).date().isoformat()))
            except Exception:
                continue
        return sources

    @staticmethod
    def _fetch(url: str) -> str:
        request = Request(url, headers={"User-Agent": "FrontierAIWorkbench/0.1"})
        with urlopen(request, timeout=12) as response:
            return response.read().decode("utf-8", errors="ignore")
