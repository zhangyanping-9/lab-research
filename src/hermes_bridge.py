"""HermesBridge — Hermes 智能体适配层。

对外暴露的工具接口Hermes智能体可以直接调用。
所有输入和输出均为结构化 JSON，符合 Hermes 工具调用规范。
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.analyzer import ResearchAnalyzer
from src.collector import CollectedArticle, collect_from_lab, save_articles
from src.registry import LabRegistry
from src.reporter import InsightReporter

logger = logging.getLogger(__name__)


class HermesBridge:
    """Hermes 智能体与半导体研究方向采集系统的适配层。

    使用示例:
        bridge = HermesBridge()
        result = bridge.collect_and_report(
            labs=["imec", "intel-labs", "mit-mtl"],
            mode="weekly",
        )
    """

    def __init__(
        self,
        registry: LabRegistry | None = None,
        analyzer: ResearchAnalyzer | None = None,
        reporter: InsightReporter | None = None,
    ) -> None:
        self.registry = registry or LabRegistry()
        self.analyzer = analyzer or ResearchAnalyzer()
        self.reporter = reporter or InsightReporter()
        self._date_str: str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # ------------------------------------------------------------------
    # Tool: collect_research_directions
    # ------------------------------------------------------------------

    def collect_research_directions(
        self,
        labs: list[str],
        mode: str = "weekly",
        max_per_lab: int = 10,
        domains: list[str] | None = None,
    ) -> dict[str, Any]:
        """采集指定实验室的最新研究方向。

        Args:
            labs: 实验室 ID 列表
            mode: 采集密度 (daily/weekly/monthly/deep)
            max_per_lab: 每实验室最大文章数
            domains: 限定领域

        Returns:
            采集结果摘要
        """
        logger.info("HermesBridge: collect_research_directions labs=%s mode=%s", labs, mode)

        # Resolve labs
        self.registry.load()
        lab_entries = self.registry.resolve_ids(labs)
        if not lab_entries:
            # Try fuzzy matching
            lab_entries = self.registry.find(lab_ids=labs)
        if not lab_entries:
            return {
                "status": "error",
                "error": f"未找到实验室: {labs}。可用实验室请调用 list_available_labs()",
            }

        # Filter by domain if specified
        if domains:
            lab_entries = [
                l for l in lab_entries
                if any(d in l.get("domains", []) for d in domains)
            ]

        logger.info("Resolved %d lab entries", len(lab_entries))

        # Collect
        all_articles: dict[str, list[CollectedArticle]] = {}
        total = 0
        errors = []

        for lab in lab_entries[:15]:  # limit per run
            try:
                articles = collect_from_lab(lab, max_articles=max_per_lab)
                if articles:
                    all_articles[lab.get("id", "unknown")] = articles
                    total += len(articles)
            except Exception as exc:
                errors.append({"lab": lab.get("id"), "error": str(exc)})
                logger.warning("Collection failed for %s: %s", lab.get("id"), exc)

        # Save
        file_map = save_articles(all_articles, self._date_str)

        # Summary
        return {
            "status": "success",
            "date": self._date_str,
            "mode": mode,
            "labs_requested": len(labs),
            "labs_collected": len(all_articles),
            "total_articles": total,
            "articles_by_lab": {
                lab_id: len(arts) for lab_id, arts in all_articles.items()
            },
            "file_paths": file_map,
            "errors": errors if errors else None,
        }

    # ------------------------------------------------------------------
    # Tool: analyze_research_trends
    # ------------------------------------------------------------------

    def analyze_research_trends(
        self,
        date: str | None = None,
        min_confidence: float = 0.6,
        domains: list[str] | None = None,
        include_labs: list[str] | None = None,
    ) -> dict[str, Any]:
        """分析已采集的研究数据，识别趋势。

        Args:
            date: 日期 YYYY-MM-DD，默认最新
            min_confidence: 最小置信度
            domains: 限定领域
            include_labs: 限定实验室

        Returns:
            分析结果
        """
        date = date or self._date_str
        logger.info("HermesBridge: analyze_research_trends date=%s", date)

        try:
            trends = self.analyzer.load_and_analyze(
                date,
                min_confidence=min_confidence,
                include_labs=include_labs,
                domains=domains,
            )
        except Exception as exc:
            return {
                "status": "error",
                "error": f"分析失败: {exc}",
            }

        if not trends:
            return {
                "status": "warning",
                "message": f"{date} 未找到符合条件的分析数据",
                "trends": [],
            }

        # Save analysis
        file_map = self.analyzer.save_analysis(trends, date)

        # Summary
        lab_activity = self.analyzer.lab_activity(trends)
        cross_ref = self.analyzer.cross_reference_summary(trends)

        return {
            "status": "success",
            "date": date,
            "articles_analyzed": sum(len(t.articles) for t in trends),
            "total_trends": len(trends),
            "lifecycle_distribution": {
                lc: len([t for t in trends if t.lifecycle == lc])
                for lc in ["emerging", "growing", "mature", "declining"]
            },
            "top_emerging": [
                {"direction": t.name, "confidence": t.confidence, "labs": list(t.labs)}
                for t in trends[:5] if t.lifecycle == "emerging"
            ],
            "lab_count": len(lab_activity),
            "cross_convergences": cross_ref.get("total_convergences", 0),
            "file_paths": file_map,
        }

    # ------------------------------------------------------------------
    # Tool: generate_insight_report
    # ------------------------------------------------------------------

    def generate_insight_report(
        self,
        date: str | None = None,
        format: str = "both",
        focus: str = "",
        include_labs: list[str] | None = None,
    ) -> dict[str, Any]:
        """生成研究方向洞察报告。

        Args:
            date: 日期
            format: 输出格式 (json/markdown/both)
            focus: 报告重点
            include_labs: 限定实验室

        Returns:
            报告元信息和文件路径
        """
        date = date or self._date_str
        logger.info("HermesBridge: generate_insight_report date=%s focus=%s", date, focus)

        # Load trends
        try:
            trends = self.analyzer.load_and_analyze(
                date,
                min_confidence=0.5,
                include_labs=include_labs,
            )
        except Exception as exc:
            return {"status": "error", "error": f"加载数据失败: {exc}"}

        if not trends:
            return {
                "status": "warning",
                "message": f"{date} 没有足够的分析数据来生成报告",
            }

        # Gather lab stats
        from src.collector import CollectedArticle
        all_articles = []
        articles_dir = Path("artifacts") / date / "articles"
        if articles_dir.exists():
            for f in articles_dir.rglob("*.json"):
                if f.name == "_all.json":
                    continue
                try:
                    with open(f, encoding="utf-8") as fh:
                        all_articles.append(json.load(fh))
                except Exception:
                    pass

        lab_stats = {
            "total_articles": len(all_articles),
        }

        formats = {"json": ["json"], "markdown": ["markdown"], "both": ["json", "markdown"]}
        file_map = self.reporter.save_report(
            trends,
            date,
            focus=focus,
            lab_stats=lab_stats,
            formats=formats.get(format, ["json", "markdown"]),
        )

        return {
            "status": "success",
            "date": date,
            "focus": focus,
            "trends_in_report": len(trends),
            "file_paths": file_map,
        }

    # ------------------------------------------------------------------
    # Tool: collect_and_report (end-to-end)
    # ------------------------------------------------------------------

    def collect_and_report(
        self,
        labs: list[str],
        mode: str = "weekly",
        focus: str = "",
        format: str = "both",
    ) -> dict[str, Any]:
        """端到端一体化操作：采集 + 分析 + 报告。

        Args:
            labs: 实验室 ID 列表
            mode: 采集密度
            focus: 报告重点关注
            format: 输出格式

        Returns:
            完整结果
        """
        logger.info("HermesBridge: collect_and_report labs=%s mode=%s", labs, mode)

        # Step 1: Collect
        collect_result = self.collect_research_directions(labs, mode)
        if collect_result.get("status") == "error":
            return collect_result

        date = collect_result["date"]

        # Step 2: Analyze
        analyze_result = self.analyze_research_trends(date=date)
        if analyze_result.get("status") == "error":
            return analyze_result

        # Step 3: Report
        report_result = self.generate_insight_report(
            date=date, format=format, focus=focus
        )

        return {
            "status": "success",
            "summary": f"完成 {date} 的采集与分析，覆盖 {collect_result['labs_collected']} 个实验室，"
                       f"采集 {collect_result['total_articles']} 篇文章，"
                       f"识别 {analyze_result['total_trends']} 个研究方向",
            "date": date,
            "collection": collect_result,
            "analysis": analyze_result,
            "report": report_result,
        }

    # ------------------------------------------------------------------
    # Tool: list_available_labs
    # ------------------------------------------------------------------

    def list_available_labs(
        self,
        category: str | None = None,
        region: str | None = None,
        domain: str | None = None,
    ) -> dict[str, Any]:
        """列出注册表中可用的实验室。

        Args:
            category: 类别过滤
            region: 区域过滤
            domain: 领域过滤

        Returns:
            符合条件的实验室列表
        """
        self.registry.load()

        if category or region or domain or True:
            labs = self.registry.find(
                category=category,
                region=region,
                domain=domain,
            )
        else:
            labs = self.registry.labs

        return {
            "status": "success",
            "total": len(labs),
            "stats": self.registry.stats(),
            "labs": [
                {
                    "id": l.get("id"),
                    "name": l.get("name"),
                    "category": l.get("category"),
                    "tier": l.get("tier"),
                    "region": l.get("region"),
                    "domains": l.get("domains"),
                    "description": l.get("description", ""),
                }
                for l in labs
            ],
        }

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def get_system_status(self) -> dict[str, Any]:
        """获取系统状态摘要。"""
        self.registry.load()
        return {
            "system": "semi-research-direction-collect",
            "version": "0.1.0",
            "registry": self.registry.stats(),
            "available_tools": [
                "collect_research_directions",
                "analyze_research_trends",
                "generate_insight_report",
                "collect_and_report",
                "list_available_labs",
            ],
            "last_run_date": self._date_str,
        }
