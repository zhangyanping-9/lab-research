"""Analyzer — research direction clustering, trend detection, lifecycle assessment."""

from __future__ import annotations

import json
import logging
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.collector import CollectedArticle, DOMAIN_KEYWORDS

logger = logging.getLogger(__name__)


class ResearchAnalyzer:
    """研究方向分析器：聚类、趋势识别、跨实验室交叉验证。"""

    def __init__(self) -> None:
        self.directions: dict[str, TrendDirection] = {}

    # ------------------------------------------------------------------
    # Analysis pipeline
    # ------------------------------------------------------------------

    def analyze_articles(
        self,
        articles: list[CollectedArticle],
        min_confidence: float = 0.6,
    ) -> list[TrendDirection]:
        """对采集的文章进行全部分析，返回趋势方向列表。"""
        self._cluster_by_keywords(articles)
        self._assign_lifecycles()
        self._compute_confidence()
        self._cross_reference()
        return self._rank_trends(min_confidence=min_confidence)

    def load_and_analyze(
        self,
        date_str: str,
        base_dir: str | Path = "artifacts",
        min_confidence: float = 0.6,
        include_labs: list[str] | None = None,
        domains: list[str] | None = None,
    ) -> list[TrendDirection]:
        """从磁盘加载文章并进行分析。"""
        articles = self._load_articles(date_str, base_dir, include_labs, domains)
        if not articles:
            logger.warning("No articles found for %s", date_str)
            return []
        logger.info("Loaded %d articles for analysis", len(articles))
        return self.analyze_articles(articles, min_confidence=min_confidence)

    def _load_articles(
        self,
        date_str: str,
        base_dir: str | Path,
        include_labs: list[str] | None,
        domains: list[str] | None,
    ) -> list[CollectedArticle]:
        """从 artifacts 目录加载文章。"""
        articles: list[CollectedArticle] = []
        base = Path(base_dir) / date_str / "articles"
        if not base.exists():
            return articles

        for lab_dir in base.iterdir():
            if not lab_dir.is_dir():
                continue
            lab_id = lab_dir.name
            if include_labs and lab_id not in include_labs:
                continue

            for f in lab_dir.glob("*.json"):
                if f.name == "_all.json":
                    continue
                try:
                    with open(f, encoding="utf-8") as fh:
                        data = json.load(fh)
                    article = CollectedArticle(**data)
                    if domains and not any(d in article.domains for d in domains):
                        continue
                    articles.append(article)
                except Exception as exc:
                    logger.warning("Failed to load %s: %s", f, exc)

        return articles

    # ------------------------------------------------------------------
    # Internal analysis methods
    # ------------------------------------------------------------------

    def _cluster_by_keywords(self, articles: list[CollectedArticle]) -> None:
        """基于关键词对文章进行方向聚类。"""
        for article in articles:
            for kw in article.keywords:
                direction = self._map_keyword_to_direction(kw)
                if direction not in self.directions:
                    self.directions[direction] = TrendDirection(
                        name=direction,
                        keywords=set(),
                        articles=[],
                        labs=set(),
                        domains=article.domains,
                    )
                self.directions[direction].keywords.add(kw)
                self.directions[direction].articles.append(article)
                self.directions[direction].labs.add(article.lab_id)

        # Deduplicate articles within each direction
        for direction in self.directions.values():
            seen_urls: set[str] = set()
            unique: list[CollectedArticle] = []
            for a in direction.articles:
                if a.url not in seen_urls:
                    seen_urls.add(a.url)
                    unique.append(a)
            direction.articles = unique

    def _map_keyword_to_direction(self, keyword: str) -> str:
        """将关键词映射到标准研究方向名称。"""
        mapping = {
            # Advanced process
            "gaa": "Gate-All-Around (GAA) FETs",
            "cfet": "CFET (Complementary FET)",
            "nanosheet": "Nanosheet FETs",
            "forksheet": "Forksheet FETs",
            "bspdn": "Backside Power Delivery Network (BSPDN)",
            "backside power": "Backside Power Delivery Network (BSPDN)",
            "euv": "EUV Lithography",
            "high-na": "High-NA EUV Lithography",
            "sub-2nm": "Sub-2nm Process Technology",
            "dtco": "Design-Technology Co-Optimization (DTCO)",
            # Packaging
            "hybrid bonding": "Hybrid Bonding (Direct Cu-Cu)",
            "3d stacking": "3D Stacking / 3D IC",
            "chiplet": "Chiplet & UCIe Ecosystem",
            "ucie": "Chiplet & UCIe Ecosystem",
            "fowlp": "Fan-Out Wafer Level Packaging",
            "tsv": "Through-Silicon Via (TSV)",
            # Memory
            "hbm": "HBM (High Bandwidth Memory)",
            "mram": "MRAM / STT-MRAM / SOT-MRAM",
            "feram": "FeRAM (Ferroelectric RAM)",
            "pcm": "PCM / XPoint (Phase Change Memory)",
            "cxl": "CXL Memory Expansion",
            "3d nand": "3D NAND Scaling",
            # AI chip
            "neuromorphic": "Neuromorphic Computing",
            "in-memory computing": "In-Memory / Near-Memory Computing",
            "analog computing": "Analog / Mixed-Signal AI Accelerators",
            "transformer accelerator": "Transformer-Specific AI Accelerators",
            "dataflow architecture": "Spatial / Dataflow Architectures",
            # EDA
            "ml-eda": "ML for EDA (AI-Driven Design Automation)",
            "physical design": "Physical Design & Routing Optimization",
            "opc": "Optical Proximity Correction (OPC) & Computational Lithography",
            # Materials
            "sic": "SiC (Silicon Carbide) Power Devices",
            "gan": "GaN (Gallium Nitride) Power & RF",
            "2d materials": "2D Materials (Graphene, MoS2, etc.)",
            "wide bandgap": "Wide & Ultra-Wide Bandgap Semiconductors",
            # Quantum
            "qubit": "Quantum Computing",
            "silicon quantum": "Silicon Quantum Computing",
            "quantum error correction": "Quantum Error Correction",
            # Photonics
            "silicon photonics": "Silicon Photonics",
            "co-packaged optics": "Co-Packaged Optics (CPO)",
            # Manufacturing
            "ald": "Atomic Layer Deposition (ALD) / ALE",
            "etch": "Advanced Etch Technology",
            "metrology": "Semiconductor Metrology & Inspection",
            "cmp": "Chemical Mechanical Planarization (CMP)",
            # Reliability
            "tddb": "Reliability Physics (TDDB, BTI, HCI)",
            "electromigration": "Interconnect Reliability (EM, Stress Migration)",
            "thermal management": "Thermal Management & Cooling",
            # Security
            "hardware security": "Hardware Security & Root of Trust",
        }
        kw_lower = keyword.lower().strip()
        return mapping.get(kw_lower, f"Research: {keyword}")

    def _assign_lifecycles(self) -> None:
        """为每个方向分配生命周期阶段。"""
        for direction in self.directions.values():
            n_labs = len(direction.labs)
            n_articles = len(direction.articles)
            # More labs + more articles → more mature
            score = min(1.0, (n_labs * 0.15 + n_articles * 0.05))
            if score < 0.3:
                direction.lifecycle = "emerging"
            elif score < 0.5:
                direction.lifecycle = "growing"
            elif score < 0.75:
                direction.lifecycle = "mature"
            else:
                direction.lifecycle = "declining"

    def _compute_confidence(self) -> None:
        """计算每个方向的置信度。"""
        for direction in self.directions.values():
            n_labs = len(direction.labs)
            n_articles = len(direction.articles)
            # Confidence based on cross-lab evidence + article volume
            lab_factor = min(1.0, n_labs / 5.0) * 0.5
            article_factor = min(1.0, n_articles / 8.0) * 0.3
            quality_factor = 0.2  # base
            direction.confidence = round(
                min(1.0, lab_factor + article_factor + quality_factor), 2
            )

    def _cross_reference(self) -> None:
        """执行跨实验室交叉引用标注。"""
        # Each direction already tracks labs — build convergence map
        self._convergences: dict[str, list[str]] = {}
        for name, direction in self.directions.items():
            labs_list = sorted(direction.labs)
            self._convergences[name] = labs_list

    def _rank_trends(self, min_confidence: float = 0.6) -> list[TrendDirection]:
        """根据综合得分排序趋势方向。"""
        sorted_dirs = sorted(
            self.directions.values(),
            key=lambda d: (d.lifecycle_score(), d.confidence, len(d.labs)),
            reverse=True,
        )
        return [d for d in sorted_dirs if d.confidence >= min_confidence and len(d.articles) >= 1]

    # ------------------------------------------------------------------
    # Summary utilities
    # ------------------------------------------------------------------

    def domain_summary(self, trends: list[TrendDirection]) -> dict[str, dict[str, int]]:
        """生成每个领域的研究方向统计摘要。"""
        summary: dict[str, dict[str, int]] = {}
        for trend in trends:
            for domain in trend.domains:
                if domain not in summary:
                    summary[domain] = {"total": 0, "emerging": 0, "growing": 0,
                                       "mature": 0, "declining": 0, "labs": 0}
                summary[domain]["total"] += 1
                if trend.lifecycle in summary[domain]:
                    summary[domain][trend.lifecycle] += 1
                summary[domain]["labs"] = max(summary[domain]["labs"],
                                              len(trend.labs))
        return summary

    def lab_activity(self, trends: list[TrendDirection]) -> list[dict[str, Any]]:
        """统计各实验室的活跃研究方向。"""
        lab_counter: dict[str, Counter[str]] = defaultdict(Counter)
        lab_articles: dict[str, int] = defaultdict(int)

        for trend in trends:
            for lab_id in trend.labs:
                lab_counter[lab_id][trend.name] += 1
                lab_articles[lab_id] += 1

        return [
            {
                "lab": lab,
                "direction_count": len(dirs),
                "article_count": lab_articles[lab],
                "top_directions": [d for d, _ in dirs.most_common(5)],
            }
            for lab, dirs in sorted(lab_counter.items(), key=lambda x: -len(x[1]))
        ]

    def cross_reference_summary(
        self, trends: list[TrendDirection]
    ) -> dict[str, Any]:
        """生成跨实验室交叉引用摘要。"""
        convergences = []
        for trend in trends:
            if len(trend.labs) >= 2:
                strength = "strong" if len(trend.labs) >= 4 else "moderate"
                convergences.append({
                    "direction": trend.name,
                    "labs": sorted(trend.labs),
                    "strength": strength,
                })

        return {
            "total_convergences": len(convergences),
            "convergences": convergences,
        }

    def save_analysis(
        self,
        trends: list[TrendDirection],
        date_str: str,
        base_dir: str | Path = "artifacts",
    ) -> dict[str, str]:
        """保存分析结果到磁盘。"""
        base = Path(base_dir) / date_str / "analysis"
        base.mkdir(parents=True, exist_ok=True)

        domain_summary = self.domain_summary(trends)
        lab_activity = self.lab_activity(trends)
        cross_ref = self.cross_reference_summary(trends)

        # Trends data
        trends_data = self._trends_to_json(trends)
        file_map: dict[str, str] = {}

        # trends.json
        trends_path = base / "trends.json"
        output = {
            "analysis_date": date_str,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "articles_analyzed": sum(len(t.articles) for t in trends),
            "total_directions": len(trends),
            "trends": trends_data,
        }
        with open(trends_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        file_map["trends"] = str(trends_path)

        # domain_map.json
        domain_path = base / "domain_map.json"
        with open(domain_path, "w", encoding="utf-8") as f:
            json.dump(domain_summary, f, ensure_ascii=False, indent=2)
        file_map["domain_map"] = str(domain_path)

        # lab_activity.json
        lab_path = base / "lab_activity.json"
        with open(lab_path, "w", encoding="utf-8") as f:
            json.dump(lab_activity, f, ensure_ascii=False, indent=2)
        file_map["lab_activity"] = str(lab_path)

        # cross_reference.json
        cross_path = base / "cross_reference.json"
        with open(cross_path, "w", encoding="utf-8") as f:
            json.dump(cross_ref, f, ensure_ascii=False, indent=2)
        file_map["cross_reference"] = str(cross_path)

        logger.info("Analysis saved to %s", base)
        return file_map

    def _trends_to_json(self, trends: list[TrendDirection]) -> list[dict]:
        """Convert trend objects to JSON-safe dicts."""
        return [
            {
                "direction": t.name,
                "lifecycle": t.lifecycle,
                "confidence": t.confidence,
                "labs_active": sorted(t.labs),
                "article_count": len(t.articles),
                "keywords": sorted(t.keywords),
                "key_insight": "",
                "evidence": [
                    {
                        "lab": a.lab_id,
                        "title": a.title,
                        "url": a.url,
                        "published_at": a.published_at,
                        "summary": a.summary[:200],
                    }
                    for a in t.articles[:5]
                ],
                "score": t.score(),
            }
            for t in trends
        ]


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


class TrendDirection:
    """一个研究方向及其相关文章集合。"""

    def __init__(
        self,
        name: str,
        keywords: set[str] | None = None,
        articles: list[CollectedArticle] | None = None,
        labs: set[str] | None = None,
        domains: list[str] | None = None,
    ) -> None:
        self.name = name
        self.keywords = keywords or set()
        self.articles = articles or []
        self.labs = labs or set()
        self.domains = domains or []
        self.lifecycle = "emerging"
        self.confidence = 0.0

    def lifecycle_score(self) -> int:
        """Return numeric score for lifecycle (for sorting)."""
        scores = {"emerging": 4, "growing": 3, "mature": 2, "declining": 1}
        return scores.get(self.lifecycle, 0)

    def score(self) -> float:
        """综合活跃度得分。"""
        return self.confidence * self.lifecycle_score()
