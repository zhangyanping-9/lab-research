"""Analyzer — research direction clustering, trend detection, lifecycle assessment.

Supports both article-level (fast) and project-level (deep) analysis.
"""

from __future__ import annotations

import json
import logging
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.collector import CollectedArticle, DOMAIN_KEYWORDS
from src.models import ResearchProject, ProjectTimeline

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
# Project-level analyzer (deep mode)
# ---------------------------------------------------------------------------


class ProjectAnalyzer:
    """研究项目级分析器：项目聚类、时间线跟踪、投资组合分析。"""

    def __init__(self) -> None:
        self.projects: list[ResearchProject] = []

    def load_projects(
        self,
        date_str: str,
        base_dir: str | Path = "artifacts",
        lab_ids: list[str] | None = None,
        domains: list[str] | None = None,
    ) -> list[ResearchProject]:
        """从磁盘加载研究项目。"""
        base = Path(base_dir) / date_str / "projects"
        if not base.exists():
            # Fallback: try articles directory
            base = Path(base_dir) / date_str / "articles"
            if not base.exists():
                logger.warning("No projects or articles found for %s", date_str)
                return []

        projects: list[ResearchProject] = []
        for lab_dir in base.iterdir():
            if not lab_dir.is_dir():
                continue
            if lab_ids and lab_dir.name not in lab_ids:
                continue

            for f in lab_dir.glob("*.json"):
                if f.name.startswith("_all"):
                    continue
                try:
                    with open(f, encoding="utf-8") as fh:
                        data = json.load(fh)
                    # Try as ResearchProject first, fallback to CollectedArticle
                    if "project_id" in data:
                        proj = ResearchProject.from_dict(data)
                    else:
                        # Convert CollectedArticle to minimal ResearchProject
                        proj = ResearchProject(
                            project_id=f"{data.get('lab_id', 'unknown')}-{_make_slug_id(data.get('title', ''))}",
                            lab_id=data.get("lab_id", "unknown"),
                            project_name=data.get("title", ""),
                            url=data.get("url", ""),
                            description=data.get("summary", ""),
                            domains=data.get("domains", []),
                            keywords=data.get("keywords", []),
                            lifecycle=data.get("lifecycle", "unknown"),
                            confidence=data.get("confidence", 0.0),
                            source_type="article_converted",
                        )
                    if domains and not any(d in proj.domains for d in domains):
                        continue
                    projects.append(proj)
                except Exception as exc:
                    logger.warning("Failed to load project from %s: %s", f, exc)

        self.projects = projects
        logger.info("Loaded %d projects for analysis", len(projects))
        return projects

    def cluster_by_domain(self) -> dict[str, list[ResearchProject]]:
        """按领域聚类项目。"""
        clusters: dict[str, list[ResearchProject]] = defaultdict(list)
        for proj in self.projects:
            for domain in proj.domains:
                clusters[domain].append(proj)
        return dict(clusters)

    def cluster_by_lifecycle(self) -> dict[str, list[ResearchProject]]:
        """按生命周期阶段聚类。"""
        clusters: dict[str, list[ResearchProject]] = defaultdict(list)
        for proj in self.projects:
            clusters[proj.lifecycle].append(proj)
        return dict(clusters)

    def funding_summary(self) -> dict[str, Any]:
        """资金分布摘要。"""
        sources: Counter[str] = Counter()
        total_amounts: list[str] = []
        for proj in self.projects:
            if proj.funding_source:
                sources[proj.funding_source] += 1
            if proj.funding_amount:
                total_amounts.append(proj.funding_amount)

        return {
            "by_source": dict(sources.most_common(10)),
            "total_projects_with_funding": sum(sources.values()),
            "funding_amounts": total_amounts[:20],
        }

    def lab_portfolio(self) -> list[dict[str, Any]]:
        """各实验室的项目组合分析。"""
        lab_projects: dict[str, list[ResearchProject]] = defaultdict(list)
        for proj in self.projects:
            lab_projects[proj.lab_id].append(proj)

        portfolio = []
        for lab_id, projects in sorted(lab_projects.items(),
                                        key=lambda x: -len(x[1])):
            domains_set = set()
            lifecycle_counts: Counter[str] = Counter()
            total_confidence = 0.0
            for p in projects:
                for d in p.domains:
                    domains_set.add(d)
                lifecycle_counts[p.lifecycle] += 1
                total_confidence += p.confidence

            portfolio.append({
                "lab_id": lab_id,
                "lab_name": projects[0].lab_name or lab_id,
                "project_count": len(projects),
                "domains": sorted(domains_set),
                "lifecycle_distribution": dict(lifecycle_counts),
                "avg_confidence": round(total_confidence / len(projects), 2) if projects else 0,
                "key_projects": [p.project_name for p in projects[:3]],
            })

        return portfolio

    def tech_roadmap(self) -> list[dict[str, Any]]:
        """生成技术路线图 — 按领域组织项目时间线。"""
        roadmap: list[dict[str, Any]] = []
        domain_clusters = self.cluster_by_domain()

        for domain, projects in sorted(domain_clusters.items()):
            milestones = []
            for proj in projects:
                for m in proj.milestones:
                    milestones.append({
                        "date": m.get("date", "TBD"),
                        "description": m.get("description", ""),
                        "status": m.get("status", "planned"),
                        "project": proj.project_name,
                        "lab": proj.lab_id,
                    })

            # Sort by date
            milestones.sort(key=lambda m: m["date"])

            roadmap.append({
                "domain": domain,
                "project_count": len(projects),
                "milestones": milestones[:30],
            })

        return roadmap

    def generate_project_reports(
        self,
        lab_ids: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """为每个项目生成详细报告结构。"""
        reports = []
        target = self.projects
        if lab_ids:
            target = [p for p in target if p.lab_id in lab_ids]

        for proj in target:
            sections = proj.detail_sections()
            reports.append({
                "project_id": proj.project_id,
                "project_name": proj.project_name,
                "lab_id": proj.lab_id,
                "lab_name": proj.lab_name,
                "url": proj.url,
                "lifecycle": proj.lifecycle,
                "confidence": proj.confidence,
                "domains": proj.domains,
                "sections": sections,
            })

        return sorted(reports, key=lambda r: -r["confidence"])

    def save_project_analysis(
        self,
        date_str: str,
        base_dir: str | Path = "artifacts",
    ) -> dict[str, str]:
        """保存项目级分析结果。"""
        base = Path(base_dir) / date_str / "analysis"
        base.mkdir(parents=True, exist_ok=True)

        file_map: dict[str, str] = {}

        # Project portfolio
        portfolio = self.lab_portfolio()
        portfolio_path = base / "project_portfolio.json"
        with open(portfolio_path, "w", encoding="utf-8") as f:
            json.dump({
                "analysis_date": date_str,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "total_projects": len(self.projects),
                "lab_count": len(portfolio),
                "portfolio": portfolio,
            }, f, ensure_ascii=False, indent=2)
        file_map["project_portfolio"] = str(portfolio_path)

        # Funding summary
        funding = self.funding_summary()
        funding_path = base / "funding_summary.json"
        with open(funding_path, "w", encoding="utf-8") as f:
            json.dump({
                "analysis_date": date_str,
                "funding": funding,
            }, f, ensure_ascii=False, indent=2)
        file_map["funding_summary"] = str(funding_path)

        # Tech roadmap
        roadmap = self.tech_roadmap()
        roadmap_path = base / "tech_roadmap.json"
        with open(roadmap_path, "w", encoding="utf-8") as f:
            json.dump({
                "analysis_date": date_str,
                "domains_covered": len(roadmap),
                "roadmap": roadmap,
            }, f, ensure_ascii=False, indent=2)
        file_map["tech_roadmap"] = str(roadmap_path)

        # Detailed project reports
        reports = self.generate_project_reports()
        reports_path = base / "project_reports.json"
        with open(reports_path, "w", encoding="utf-8") as f:
            json.dump({
                "analysis_date": date_str,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "project_count": len(reports),
                "reports": reports,
            }, f, ensure_ascii=False, indent=2)
        file_map["project_reports"] = str(reports_path)

        logger.info("Project analysis saved to %s", base)
        return file_map


def _make_slug_id(text: str) -> str:
    """Make a short slug from text for ID generation."""
    import re as _re
    text = text.lower()
    text = _re.sub(r"[^a-z0-9\s-]", "", text)
    text = _re.sub(r"\s+", "-", text.strip())
    return text[:30]


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
