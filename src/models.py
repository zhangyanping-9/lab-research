"""Data models for semiconductor research direction collection.

Extends the basic CollectedArticle with detailed ResearchProject model
for tracking individual research projects with rich metadata.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


# ---------------------------------------------------------------------------
# Legacy article model (lightweight / fast collection)
# ---------------------------------------------------------------------------


@dataclass
class CollectedArticle:
    """单个采集到的研究文章。"""

    lab_id: str
    title: str
    url: str
    published_at: str = ""
    summary: str = ""
    keywords: list[str] = field(default_factory=list)
    domains: list[str] = field(default_factory=list)
    lifecycle: str = "unknown"
    page_type: str = "unknown"
    confidence: float = 0.0
    author: str = ""
    source_html_path: str = ""
    captured_at: str = ""
    quality_flags: dict[str, bool] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "lab_id": self.lab_id,
            "title": self.title,
            "url": self.url,
            "published_at": self.published_at,
            "summary": self.summary,
            "keywords": self.keywords,
            "domains": self.domains,
            "lifecycle": self.lifecycle,
            "page_type": self.page_type,
            "confidence": self.confidence,
            "author": self.author,
            "source_html_path": self.source_html_path,
            "captured_at": self.captured_at,
            "quality_flags": self.quality_flags,
        }


# ---------------------------------------------------------------------------
# Detailed research project model (deep collection mode)
# ---------------------------------------------------------------------------


@dataclass
class ResearchProject:
    """详细的研究项目记录 — 用于深度采集模式。

    与 CollectedArticle 的关系:
    - CollectedArticle: 轻量级，从列表页/研究页快速扫描，适合周采
    - ResearchProject: 重量级，从项目页/论文页深度提取，适合月采/深度采
    - 一个 ResearchProject 可以关联多个 CollectedArticle
    """

    # ---- 基础标识 ----
    project_id: str                          # e.g. "imec-bspdn-2026"
    lab_id: str                              # 所属实验室 ID
    lab_name: str = ""                       # 实验室名称
    project_name: str = ""                   # 项目名称
    url: str = ""                            # 项目主页 URL

    # ---- 项目描述 ----
    description: str = ""                    # 项目详细描述 (500-2000 字)
    objectives: list[str] = field(default_factory=list)    # 研究目标列表
    approach: str = ""                       # 技术路线/方法
    key_innovations: list[str] = field(default_factory=list)  # 关键创新点

    # ---- 团队信息 ----
    principal_investigators: list[str] = field(default_factory=list)  # PI 姓名
    team_size: str = ""                      # 团队规模 (可为人数字符串)
    collaborators: list[str] = field(default_factory=list)  # 合作机构

    # ---- 资金与时间 ----
    funding_source: str = ""                 # 资金来源 (DARPA/CHIPS Act/NSF/Internal...)
    funding_amount: str = ""                 # 资金规模
    start_date: str = ""                     # 开始日期 YYYY-MM-DD
    expected_completion: str = ""            # 预期完成日期
    status: str = ""                         # planning | active | completed | on_hold

    # ---- 技术指标 ----
    milestones: list[dict[str, str]] = field(default_factory=list)
    # [{date: "2026-Q2", description: "First tape-out", status: "completed"}]
    metrics: dict[str, str] = field(default_factory=dict)
    # {"node_size": "2nm", "power": "0.5 pJ/bit", "frequency": "3 GHz"}

    # ---- 产出 ----
    publications: list[dict[str, str]] = field(default_factory=list)
    # [{title: "...", url: "...", venue: "IEDM 2025", date: "2025-12"}]
    patents: list[str] = field(default_factory=list)
    open_source: str = ""                    # 开源地址
    demo_results: str = ""                   # 演示/原型结果

    # ---- 领域分类 ----
    domains: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    lifecycle: str = "emerging"              # emerging | growing | mature | declining
    confidence: float = 0.0                  # 0.0 - 1.0

    # ---- 关系 ----
    related_article_urls: list[str] = field(default_factory=list)  # 关联的 CollectedArticle URLs
    related_project_ids: list[str] = field(default_factory=list)   # 关联的 ResearchProject IDs

    # ---- 元数据 ----
    captured_at: str = ""                    # ISO 8601
    last_updated: str = ""                   # 最后更新时间
    source_type: str = ""                    # webpage | paper | presentation | press_release
    quality_score: float = 0.0               # 采集质量评分

    def __post_init__(self) -> None:
        if not self.captured_at:
            self.captured_at = datetime.now(timezone.utc).isoformat()
        if not self.last_updated:
            self.last_updated = self.captured_at
        if not self.project_id:
            # Auto-generate project_id
            slug = (
                self.project_name.lower()
                .replace(" ", "-")
                .replace(":", "")
                .replace("/", "-")
            )[:40]
            self.project_id = f"{self.lab_id}-{slug}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "lab_id": self.lab_id,
            "lab_name": self.lab_name,
            "project_name": self.project_name,
            "url": self.url,
            "description": self.description,
            "objectives": self.objectives,
            "approach": self.approach,
            "key_innovations": self.key_innovations,
            "principal_investigators": self.principal_investigators,
            "team_size": self.team_size,
            "collaborators": self.collaborators,
            "funding_source": self.funding_source,
            "funding_amount": self.funding_amount,
            "start_date": self.start_date,
            "expected_completion": self.expected_completion,
            "status": self.status,
            "milestones": self.milestones,
            "metrics": self.metrics,
            "publications": self.publications,
            "patents": self.patents,
            "open_source": self.open_source,
            "demo_results": self.demo_results,
            "domains": self.domains,
            "keywords": self.keywords,
            "lifecycle": self.lifecycle,
            "confidence": self.confidence,
            "related_article_urls": self.related_article_urls,
            "related_project_ids": self.related_project_ids,
            "captured_at": self.captured_at,
            "last_updated": self.last_updated,
            "source_type": self.source_type,
            "quality_score": self.quality_score,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ResearchProject:
        """从 JSON 反序列化。"""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def summary(self) -> str:
        """生成项目单行摘要。"""
        parts = [self.project_name]
        if self.lab_name:
            parts.append(f"({self.lab_name})")
        if self.status:
            parts.append(f"[{self.status}]")
        if self.lifecycle:
            parts.append(f"- {self.lifecycle}")
        return " ".join(parts)

    def detail_sections(self) -> dict[str, str]:
        """将项目分解为可报告的结构化段落。"""
        sections: dict[str, str] = {}

        if self.description:
            sections["overview"] = self.description

        if self.objectives:
            sections["objectives"] = "\n".join(f"- {o}" for o in self.objectives)

        if self.approach:
            sections["approach"] = self.approach

        if self.key_innovations:
            sections["innovations"] = "\n".join(
                f"- {i}" for i in self.key_innovations
            )

        if self.principal_investigators:
            # Format as numbered list
            sections["team"] = "\n".join(
                f"1. {pi}" for pi in self.principal_investigators
            )
            if self.collaborators:
                sections["team"] += "\n\n**合作机构**: " + ", ".join(
                    self.collaborators
                )

        if self.funding_source and self.funding_amount:
            sections["funding"] = (
                f"**来源**: {self.funding_source}\n"
                f"**规模**: {self.funding_amount}\n"
                f"**周期**: {self.start_date} → {self.expected_completion}"
            )

        if self.milestones:
            lines = []
            for m in self.milestones:
                status_icon = {"completed": "✅", "active": "🔄", "planned": "📋"}.get(
                    m.get("status", ""), "⏳"
                )
                lines.append(
                    f"- {status_icon} **{m.get('date', 'TBD')}**: {m.get('description', '')}"
                )
            sections["milestones"] = "\n".join(lines)

        if self.metrics:
            sections["metrics"] = "\n".join(
                f"- **{k}**: {v}" for k, v in self.metrics.items()
            )

        if self.publications:
            lines = []
            for p in self.publications:
                title = p.get("title", "")
                venue = p.get("venue", "")
                date = p.get("date", "")
                url = p.get("url", "")
                line = f"- {title}"
                if venue:
                    line += f" — *{venue}*"
                if date:
                    line += f" ({date})"
                if url:
                    line += f" [link]({url})"
                lines.append(line)
            sections["publications"] = "\n".join(lines)

        return sections


# ---------------------------------------------------------------------------
# Institution model (enhanced lab metadata)
# ---------------------------------------------------------------------------


@dataclass
class Institution:
    """增强的机构/信源元数据。"""

    id: str
    name: str
    category: str                            # university_lab | corporate_rd | research_institute | etc.
    region: str
    tier: int
    domains: list[str] = field(default_factory=list)
    description: str = ""
    homepage: str = ""
    research_page: str = ""
    publications_page: str = ""
    papers_page: str = ""

    # ---- 扩展字段 ----
    key_focus: list[str] = field(default_factory=list)     # 关键研究方向 (人类可读)
    funding: list[str] = field(default_factory=list)       # 已知资金/项目
    notable_partners: list[str] = field(default_factory=list)  # 重要合作方
    facilities: str = ""                                    # 核心设施描述
    notes: str = ""                                         # 补充说明
    parent: str = ""                                        # 父机构 ID (子实验室)

    def to_dict(self) -> dict[str, Any]:
        result = {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "region": self.region,
            "tier": self.tier,
            "domains": self.domains,
            "description": self.description,
            "homepage": self.homepage,
        }
        if self.research_page:
            result["research_page"] = self.research_page
        if self.publications_page:
            result["publications_page"] = self.publications_page
        if self.key_focus:
            result["key_focus"] = self.key_focus
        if self.funding:
            result["funding"] = self.funding
        if self.notable_partners:
            result["notable_partners"] = self.notable_partners
        if self.facilities:
            result["facilities"] = self.facilities
        if self.notes:
            result["notes"] = self.notes
        if self.parent:
            result["parent"] = self.parent
        return result


# ---------------------------------------------------------------------------
# Project timeline model (for analysis)
# ---------------------------------------------------------------------------


@dataclass
class ProjectTimeline:
    """研究项目时间线 — 跟踪项目随着时间的变化。"""

    project_id: str
    entries: list[dict[str, Any]] = field(default_factory=list)
    # [{date: "2026-01", event: "Project announced", source_url: "..."}, ...]

    def add_event(
        self, date: str, event: str, source_url: str = "", event_type: str = "update"
    ) -> None:
        self.entries.append({
            "date": date,
            "event": event,
            "source_url": source_url,
            "event_type": event_type,
        })

    def to_timeline_text(self) -> str:
        """Generate readable timeline. """
        if not self.entries:
            return "*No timeline data*"
        lines = []
        for entry in sorted(self.entries, key=lambda e: e.get("date", "")):
            lines.append(f"- **{entry['date']}**: {entry['event']}")
        return "\n".join(lines)
