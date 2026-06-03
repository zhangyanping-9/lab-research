"""Reporter — generates structured insight reports in JSON and Markdown."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.analyzer import ResearchAnalyzer, TrendDirection

logger = logging.getLogger(__name__)

# Domain label mapping (Chinese & English)
DOMAIN_LABELS: dict[str, dict[str, str]] = {
    "advanced_process": {"en": "Advanced Process Technology", "zh": "先进制程技术"},
    "advanced_packaging": {"en": "Advanced Packaging", "zh": "先进封装"},
    "memory_technology": {"en": "Memory Technology", "zh": "存储器技术"},
    "ai_chip_architecture": {"en": "AI Chip Architecture", "zh": "AI芯片架构"},
    "eda_design_automation": {"en": "EDA & Design Automation", "zh": "EDA设计自动化"},
    "semiconductor_materials": {"en": "Semiconductor Materials", "zh": "半导体材料"},
    "quantum_computing": {"en": "Quantum Computing", "zh": "量子计算"},
    "photonics": {"en": "Silicon Photonics", "zh": "硅光子学"},
    "manufacturing_equipment": {"en": "Manufacturing Equipment", "zh": "制造装备与工艺"},
    "reliability_test": {"en": "Reliability & Test", "zh": "可靠性与测试"},
    "security": {"en": "Hardware Security", "zh": "硬件安全"},
    "chiplet_interconnect": {"en": "Chiplet Interconnect", "zh": "Chiplet互联"},
}

LIFECYCLE_LABELS: dict[str, dict[str, str]] = {
    "emerging": {"en": "🟢 Emerging", "zh": "🟢 新兴"},
    "growing": {"en": "🔵 Growing", "zh": "🔵 成长"},
    "mature": {"en": "🟠 Mature", "zh": "🟠 成熟"},
    "declining": {"en": "🔴 Declining", "zh": "🔴 衰退"},
}


class InsightReporter:
    """研究方向洞察报告生成器。"""

    def __init__(self, analyzer: ResearchAnalyzer | None = None) -> None:
        self.analyzer = analyzer or ResearchAnalyzer()

    # ------------------------------------------------------------------
    # JSON report
    # ------------------------------------------------------------------

    def generate_json_report(
        self,
        trends: list[TrendDirection],
        date_str: str,
        focus: str = "",
        lab_stats: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """生成 JSON 格式的结构化报告。"""
        domain_summary = self.analyzer.domain_summary(trends)
        lab_activity = self.analyzer.lab_activity(trends)
        cross_ref = self.analyzer.cross_reference_summary(trends)

        now = datetime.now(timezone.utc).isoformat()

        report = {
            "report_meta": {
                "title": f"半导体研究方向洞察报告 {date_str}",
                "generated_at": now,
                "collection_date": date_str,
                "focus": focus,
                "labs_covered": len(lab_activity),
                "articles_collected": lab_stats.get("total_articles", 0) if lab_stats else 0,
                "trends_identified": len(trends),
            },
            "top_trends": self._trends_to_report(trends[:10]),
            "domain_summary": self._domain_summary_with_labels(domain_summary),
            "lab_activity": lab_activity,
            "cross_reference": cross_ref,
            "appendix": {
                "lifecycle_distribution": self._lifecycle_distribution(trends),
                "all_trends": self._trends_to_report(trends),
            },
        }
        return report

    # ------------------------------------------------------------------
    # Markdown report
    # ------------------------------------------------------------------

    def generate_markdown_report(
        self,
        trends: list[TrendDirection],
        date_str: str,
        focus: str = "",
        lab_stats: dict[str, Any] | None = None,
    ) -> str:
        """生成 Markdown 格式的人类可读报告。"""
        json_report = self.generate_json_report(trends, date_str, focus, lab_stats)
        meta = json_report["report_meta"]
        top_trends = json_report["top_trends"]
        domain_summary = json_report["domain_summary"]
        lab_activity = json_report["lab_activity"]
        cross_ref = json_report["cross_reference"]
        appendix = json_report["appendix"]

        lines: list[str] = []
        _w = lines.append

        # Title
        _w(f"# {meta['title']}")
        _w(f"")
        _w(f"> 生成时间: {meta['generated_at'][:19]}")
        _w(f"> 覆盖实验室: {meta['labs_covered']} | 采集文章: {meta['articles_collected']} | 识别方向: {meta['trends_identified']}")
        if focus:
            _w(f"> 重点关注: {focus}")
        _w("")
        _w("---")
        _w("")

        # Executive summary
        _w("## 📋 执行摘要")
        _w("")
        _w(f"本期报告覆盖 **{meta['labs_covered']}** 个实验室/研究机构，采集 **{meta['articles_collected']}** 篇研究相关内容，")
        _w(f"识别出 **{meta['trends_identified']}** 个活跃研究方向。")
        _w("")

        if top_trends:
            _w("**Top 趋势: **")
            for i, t in enumerate(top_trends[:5], 1):
                _w(f"  {i}. **{t['direction']}** — {t['lifecycle']} (置信度: {t['confidence']:.1%}) — {len(t['labs_active'])} 个实验室活跃")

        _w("")
        _w("---")
        _w("")

        # Research hot map
        _w("## 🔬 研究热点地图")
        _w("")
        for domain_key, info in domain_summary.items():
            label = DOMAIN_LABELS.get(domain_key, {}).get("en", domain_key)
            total = info["total"]
            if total == 0:
                continue
            _w(f"### {label}")
            _w("")
            _w(f"- 活跃方向: {total} | 新兴: {info.get('emerging', 0)} | 成长: {info.get('growing', 0)} | 成熟: {info.get('mature', 0)} | 衰退: {info.get('declining', 0)}")
            _w("")
            # Show domain-specific trends
            domain_trends = [t for t in top_trends if t["direction"] in [
                d.name for d in trends if domain_key in d.domains]]
            for t in domain_trends[:3]:
                _w(f"- **{t['direction']}** ({t['lifecycle']})")
            _w("")

        _w("---")
        _w("")

        # Deep trend analysis (top 5)
        _w("## 📊 深度趋势分析")
        _w("")

        for idx, t in enumerate(top_trends[:5], 1):
            domain_label = ", ".join(
                DOMAIN_LABELS.get(d, {}).get("en", d) for d in t.get("domains", []) if d in DOMAIN_LABELS
            )
            _w(f"### {idx}. {t['direction']}")
            _w("")
            _w(f"- **生命周期**: {t['lifecycle']}")
            _w(f"- **置信度**: {t['confidence']:.1%}")
            _w(f"- **活跃实验室**: {', '.join(t['labs_active'][:8])}")
            _w(f"- **相关文章数**: {t['article_count']}")
            _w(f"- **关联领域**: {domain_label}")
            _w("")

            if t.get("evidence"):
                _w("证据来源:")
                for ev in t["evidence"][:3]:
                    _w(f"  - [{ev['lab']}] {ev['title']}")
            _w("")

        _w("---")
        _w("")

        # Lab activity
        _w("## 🏛️ 实验室活跃度")
        _w("")
        _w("| 实验室 | 研究方向数 | 文章数 | Top方向 |")
        _w("|---|---|---|---|")
        for lab in lab_activity[:15]:
            top_dirs = ", ".join(lab["top_directions"][:3])
            _w(f"| {lab['lab']} | {lab['direction_count']} | {lab['article_count']} | {top_dirs} |")
        _w("")

        _w("---")
        _w("")

        # Cross-reference
        _w("## 🔗 跨实验室交叉研究")
        _w("")
        convs = cross_ref.get("convergences", [])
        if convs:
            for c in convs[:10]:
                badge = "🟢 Strong" if c["strength"] == "strong" else "🟡 Moderate"
                _w(f"- **{c['direction']}** ({badge}) — {', '.join(c['labs'][:5])}")
        else:
            _w("*暂无明显的跨实验室交叉研究方向*")
        _w("")

        _w("---")
        _w("")

        # Appendix
        _w("## 📎 附录")
        _w("")

        _w("### 所有研究方向列表")
        _w("")
        _w("| 研究方向 | 生命周期 | 置信度 | 活跃实验室 |")
        _w("|---|---|---|---|")
        for t in appendix.get("all_trends", []):
            labs_str = ", ".join(t["labs_active"][:4])
            _w(f"| {t['direction']} | {t['lifecycle']} | {t['confidence']:.1%} | {labs_str} |")
        _w("")

        _w("### 方法说明")
        _w("")
        _w("- 数据来源: 全球半导体实验室/研究机构/企业R&D中心官网及出版物")
        _w("- 采集方式: HTTP获取 + Playwright MCP (JS渲染页面) + WebSearch 降级")
        _w("- 方向聚类: 基于关键词匹配和跨实验室交叉验证")
        _w("- 生命周期判断: 多维度评分 (实验室数×文章数×领域分布)")
        _w(f"- 报告生成时间: {meta['generated_at'][:19]}")
        _w("")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Save report
    # ------------------------------------------------------------------

    def save_report(
        self,
        trends: list[TrendDirection],
        date_str: str,
        focus: str = "",
        lab_stats: dict[str, Any] | None = None,
        base_dir: str | Path = "artifacts",
        formats: list[str] | None = None,
    ) -> dict[str, str]:
        """保存报告到磁盘，返回文件路径映射。"""
        formats = formats or ["json", "markdown"]
        base = Path(base_dir) / date_str / "reports"
        base.mkdir(parents=True, exist_ok=True)

        file_map: dict[str, str] = {}

        if "json" in formats:
            json_report = self.generate_json_report(trends, date_str, focus, lab_stats)
            json_path = base / f"semiconductor-research-insight-{date_str}.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(json_report, f, ensure_ascii=False, indent=2)
            file_map["json"] = str(json_path)
            logger.info("JSON report saved: %s", json_path)

        if "markdown" in formats:
            md_report = self.generate_markdown_report(trends, date_str, focus, lab_stats)
            md_path = base / f"semiconductor-research-insight-{date_str}.md"
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(md_report)
            file_map["markdown"] = str(md_path)
            logger.info("Markdown report saved: %s", md_path)

        return file_map

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _trends_to_report(self, trends: list[TrendDirection]) -> list[dict]:
        """Convert trends to simplified JSON."""
        return [
            {
                "direction": t.name,
                "lifecycle": t.lifecycle,
                "confidence": t.confidence,
                "labs_active": sorted(t.labs),
                "article_count": len(t.articles),
                "domains": t.domains,
                "keywords": sorted(t.keywords),
                "evidence": [
                    {"lab": a.lab_id, "title": a.title, "url": a.url}
                    for a in t.articles[:5]
                ],
                "score": round(t.score(), 2),
            }
            for t in trends
        ]

    def _domain_summary_with_labels(
        self, domain_summary: dict[str, dict[str, int]]
    ) -> dict[str, Any]:
        """Add domain labels to summary."""
        labeled = {}
        for key, info in domain_summary.items():
            labels = DOMAIN_LABELS.get(key, {})
            labeled[key] = {
                "label_en": labels.get("en", key),
                "label_zh": labels.get("zh", key),
                **info,
            }
        return labeled

    def _lifecycle_distribution(
        self, trends: list[TrendDirection]
    ) -> dict[str, int]:
        """统计生命周期分布。"""
        dist: dict[str, int] = {"emerging": 0, "growing": 0, "mature": 0, "declining": 0}
        for t in trends:
            if t.lifecycle in dist:
                dist[t.lifecycle] += 1
        return dist
