"""Research workflow public seam.

The first slice intentionally keeps providers small and explicit. Real HTTP and
model adapters can be added behind these interfaces without changing the
ResearchService contract.
"""

from __future__ import annotations

import json
import os
import re
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class Source:
    title: str
    url: str
    summary: str
    published_at: str


@dataclass(frozen=True)
class Report:
    goal: str
    markdown: str
    sources: list[Source]
    file_path: Path


class MockSourceProvider:
    def discover(self, goal: str) -> list[Source]:
        return [
            Source(
                title=f"官方技术说明：{goal}",
                url="https://example.com/official-ai-update",
                summary="介绍工具调用、结构化输出和 Agent 工作流的应用方式。",
                published_at="2026-10-01",
            ),
            Source(
                title=f"工程实践笔记：{goal}",
                url="https://example.com/engineering-note",
                summary="讨论如何为 Agent 增加权限、日志和结果验证。",
                published_at="2026-09-28",
            ),
        ]


class MockModel:
    def compose(self, goal: str, sources: list[Source]) -> str:
        lines = [
            f"# {goal} 技术简报",
            "",
            "## 一句话摘要",
            f"本报告围绕“{goal}”整理公开资料，并把技术变化转换成可验证的业务问题。",
            "",
            "## 发生了什么",
            "资料显示，Agent 系统正在从单轮问答转向工具调用、任务规划和结果验证。",
            "",
            "## 资料要点",
        ]
        for index, source in enumerate(sources, start=1):
            lines.append(f"{index}. {source.summary}")
        lines.extend([
            "",
            "## 为什么重要",
            "对 AI 应用开发者而言，重点不只是调用模型，还包括工具边界、权限控制和可观察性。",
            "",
            "## 适合什么业务场景",
            "适合知识研究、资料整理、企业问答和需要人工确认的工作流。",
            "",
            "## 可以如何复现",
            "先用 Mock 模式跑通检索、总结、引用和保存，再接入真实模型与来源适配器。",
            "",
            "## 已知限制",
            "当前内容来自 Mock 来源，不能代表真实市场结论；接入真实来源后仍需人工核验。",
            "",
            "## 来源",
        ])
        for index, source in enumerate(sources, start=1):
            lines.append(f"{index}. [{source.title}]({source.url}) - {source.published_at}")
        return "\n".join(lines) + "\n"


class OpenAICompatibleModel:
    def __init__(self):
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.model = os.getenv("OPENAI_MODEL", "")

    def compose(self, goal: str, sources: list[Source]) -> str:
        context = "\n".join(f"- {source.title}: {source.summary} ({source.url})" for source in sources)
        payload = {
            "model": self.model,
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": "你是技术研究助理。只根据给定来源写报告，资料不足要明确说明。"},
                {"role": "user", "content": f"主题：{goal}\n来源：\n{context}\n请输出中文技术简报，包含摘要、变化、重要性、场景、复现、限制和来源。"},
            ],
        }
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=45) as response:
            body = json.loads(response.read().decode("utf-8"))
        return body["choices"][0]["message"]["content"]


class ResearchService:
    def __init__(self, source_provider: MockSourceProvider, model: MockModel, report_dir: Path):
        self.source_provider = source_provider
        self.model = model
        self.report_dir = report_dir

    def run_now(self, goal: str) -> Report:
        clean_goal = goal.strip()
        if not clean_goal:
            raise ValueError("研究主题不能为空")
        sources = self._deduplicate(self.source_provider.discover(clean_goal))
        markdown = self.model.compose(clean_goal, sources)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{self._slug(clean_goal)}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}.md"
        file_path = self.report_dir / filename
        file_path.write_text(markdown, encoding="utf-8")
        return Report(clean_goal, markdown, sources, file_path)

    @staticmethod
    def _deduplicate(sources: list[Source]) -> list[Source]:
        seen: set[str] = set()
        result = []
        for source in sources:
            if source.url not in seen:
                seen.add(source.url)
                result.append(source)
        return result

    @staticmethod
    def _slug(goal: str) -> str:
        ascii_slug = re.sub(r"[^a-zA-Z0-9]+", "-", goal).strip("-").lower()
        return ascii_slug or "research-report"
