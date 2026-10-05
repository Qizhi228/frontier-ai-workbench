"""Runtime wiring for local, Tencent Cloud and test environments."""

from __future__ import annotations

import os
from pathlib import Path

from app.api import WorkbenchApi
from app.http import create_app
from app.research import MockModel, MockSourceProvider, OpenAICompatibleModel, ResearchService
from app.service import WorkbenchService
from app.sources import WebPageSourceProvider
from app.store import TaskStore


DEFAULT_SOURCE_URLS = [
    "https://openai.com/news/",
    "https://www.anthropic.com/news",
    "https://blog.google/technology/ai/",
    "https://huggingface.co/blog",
    "https://github.blog/ai-and-ml/",
]


class FallbackSourceProvider:
    def __init__(self, primary, fallback):
        self.primary = primary
        self.fallback = fallback

    def discover(self, goal: str):
        sources = self.primary.discover(goal)
        return sources or self.fallback.discover(goal)


def build_api(base_dir: Path | None = None) -> WorkbenchApi:
    root = Path(base_dir or os.getenv("WORKBENCH_DATA_DIR", "./data"))
    source_mode = os.getenv("SOURCE_MODE", "mock").lower()
    model_mode = os.getenv("MODEL_MODE", "mock").lower()
    mock_sources = MockSourceProvider()
    if source_mode == "web":
        source_provider = FallbackSourceProvider(WebPageSourceProvider(DEFAULT_SOURCE_URLS), mock_sources)
    else:
        source_provider = mock_sources
    model = OpenAICompatibleModel() if model_mode == "api" else MockModel()
    service = WorkbenchService(
        TaskStore(root / "workbench.sqlite3"),
        ResearchService(source_provider, model, root / "reports"),
    )
    return WorkbenchApi(service)


def build_app(base_dir: Path | None = None):
    return create_app(build_api(base_dir))
