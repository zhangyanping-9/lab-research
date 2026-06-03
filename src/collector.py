"""Collector — orchestrates crawling of lab research pages."""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
from bs4 import BeautifulSoup

from src.config import settings
from src.registry import LabRegistry

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class CollectedArticle:
    """单个采集到的研究文章。"""

    lab_id: str
    title: str
    url: str
    published_at: str
    summary: str
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
# HTTP client
# ---------------------------------------------------------------------------


def make_client() -> httpx.Client:
    return httpx.Client(
        timeout=settings.http_timeout,
        headers={
            "User-Agent": settings.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        },
        follow_redirects=True,
    )


# ---------------------------------------------------------------------------
# Research page URL discovery
# ---------------------------------------------------------------------------

PAGE_TYPE_SIGNALS = {
    "publications": ["publication", "paper", "research", "publist", "pubs", "library"],
    "research_area": ["research", "research-area", "research-group", "our-research"],
    "news": ["news", "press", "announcement", "room", "story"],
    "people": ["people", "team", "member", "staff", "profile"],
    "about": ["about", "overview", "company", "mission"],
}

DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "advanced_process": [
        "gaa", "cfet", "nanosheet", "forksheet", "bspdn", "backside power",
        "euv", "high-na", "multi-patterning", "sub-2nm", "atomic layer",
        "gate-all-around", "buried power rail", "contact over active gate",
    ],
    "advanced_packaging": [
        "hybrid bonding", "3d stacking", "silicon interposer", "fowlp", "foplp",
        "hbm", "micro-bump", "tcb", "chiplet", "ucie", "2.5d", "3dic",
        "through-silicon via", "tsv", "fan-out", "thermo-compression",
    ],
    "memory_technology": [
        "hbm", "cxl", "mram", "feram", "pcm", "stt-mram", "sot-mram",
        "3d nand", "dram scaling", "computational memory", "cross-point",
        "memory hierarchy", "cxl memory", "hbm4",
    ],
    "ai_chip_architecture": [
        "dsa", "neuromorphic", "in-memory computing", "analog computing",
        "transformer accelerator", "sparse computation", "dataflow architecture",
        "tensor core", "ai accelerator", "ml accelerator", "spatial architecture",
        "reconfigurable", "near-memory processing",
    ],
    "eda_design_automation": [
        "rtl-to-gdsii", "ml-eda", "design space exploration", "timing closure",
        "floorplanning", "routing optimization", "placement", "synthesis",
        "physical design", "design rule", "opc", "litho simulation",
        "design-technology co-optimization", "dtco",
    ],
    "semiconductor_materials": [
        "sic", "gan", "2d materials", "graphene", "mos2", "wide bandgap",
        "ultra-wide bandgap", "ferroelectric", "high-k", "low-k", "dielectric",
        "iii-v", "gallium nitride", "silicon carbide", "diamond",
    ],
    "quantum_computing": [
        "qubit", "superconducting", "spin qubit", "silicon quantum",
        "quantum error correction", "quantum-classical", "quantum gate",
        "topological qubit", "quantum processor",
    ],
    "photonics": [
        "silicon photonics", "optical interconnect", "co-packaged optics",
        "integrated laser", "modulator", "photodetector", "waveguide",
        "photonic integrated circuit", "sic photonics",
    ],
    "manufacturing_equipment": [
        "ald", "ale", "cvd", "pvd", "etch", "metrology", "inspection",
        "atomic layer deposition", "atomic layer etch", "plasma etch",
        "chemical mechanical", "cmp", "epitaxy", "ion implant",
    ],
    "reliability_test": [
        "tddb", "bti", "hci", "nbti", "electromigration", "thermal management",
        "reliability", "lifetime", "degradation", "stress test", "eos",
    ],
    "security": [
        "hardware security", "trojan", "side-channel", "puf", "trusted execution",
        "secure enclave", "hardware root of trust",
    ],
    "chiplet_interconnect": [
        "ucie", "open hpc", "bunch of wires", "bow", "chiplet", "die-to-die",
        "interconnect", "universal chiplet", "chiplet ecosystem",
    ],
}


def classify_domains(text: str) -> list[str]:
    """根据文本关键词匹配，分类研究方向领域。"""
    text_lower = text.lower()
    matched = []
    for domain, keywords in DOMAIN_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                matched.append(domain)
                break
    return matched


def estimate_lifecycle(keywords: list[str], confidence: float) -> str:
    """基于关键词和置信度估算研究方向生命周期阶段。"""
    emerging_signals = ["towards", "preliminary", "novel", "first demonstration",
                        "emerging", "exploration", "concept"]
    growing_signals = ["optimization", "improved", "enhanced", "scaling",
                       "integration", "high-performance"]
    mature_signals = ["production", "manufacturing", "volume", "deployment",
                      "industry", "commercial"]
    declining_signals = ["limit", "challenge", "bottleneck", "replacement"]

    text = " ".join(keywords).lower()

    if any(s in text for s in emerging_signals):
        return "emerging"
    if any(s in text for s in declining_signals):
        return "declining"
    if any(s in text for s in mature_signals) and confidence > 0.7:
        return "mature"
    if any(s in text for s in growing_signals):
        return "growing"

    if confidence < 0.4:
        return "emerging"
    if confidence < 0.7:
        return "growing"
    return "mature"


# ---------------------------------------------------------------------------
# Extraction helpers
# ---------------------------------------------------------------------------


def extract_article_meta_from_html(html: str, url: str) -> dict[str, Any]:
    """从 HTML 中提取基本元信息。"""
    soup = BeautifulSoup(html, "lxml")
    meta: dict[str, Any] = {
        "title": "",
        "author": "",
        "published_at": "",
        "summary": "",
        "keywords": [],
    }

    # Title
    if soup.title:
        meta["title"] = soup.title.get_text(strip=True)
    h1 = soup.find("h1")
    if h1:
        meta["title"] = h1.get_text(strip=True)

    # Meta description
    desc = soup.find("meta", attrs={"name": "description"}) or soup.find(
        "meta", attrs={"property": "og:description"}
    )
    if desc and desc.get("content"):
        meta["summary"] = desc["content"][:500]

    # Date
    for attr in ["article:published_time", "date", "pubdate"]:
        tag = soup.find("meta", attrs={"property": attr}) or soup.find(
            "meta", attrs={"name": attr}
        )
        if tag and tag.get("content"):
            meta["published_at"] = tag["content"][:10]
            break
    if not meta["published_at"]:
        import re
        patterns = [
            r"\d{4}-\d{2}-\d{2}", r"\d{4}/\d{2}/\d{2}",
            r"\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}",
        ]
        for pat in patterns:
            m = re.search(pat, html[:5000])
            if m:
                meta["published_at"] = m.group()
                break

    # Author
    author_tag = soup.find("meta", attrs={"name": "author"})
    if author_tag and author_tag.get("content"):
        meta["author"] = author_tag["content"][:100]

    # Keywords
    kw = soup.find("meta", attrs={"name": "keywords"})
    if kw and kw.get("content"):
        meta["keywords"] = [k.strip() for k in kw["content"].split(",")][:10]

    return meta


def extract_body_text(html: str, max_chars: int = 3000) -> str:
    """从 HTML 中提取正文文本。"""
    soup = BeautifulSoup(html, "lxml")
    # Remove non-content elements
    for tag in soup.select("script, style, nav, footer, header, aside, .sidebar, .comments"):
        tag.decompose()

    body = soup.find("article") or soup.find("main") or soup.find("body")
    if not body:
        body = soup

    text = body.get_text(separator="\n", strip=True)
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    clean = "\n".join(lines)

    # Limit to avoid overly long text
    if len(clean) > max_chars:
        clean = clean[:max_chars] + "\n\n[...truncated...]"

    return clean[:2000]  # Summary length for research direction extraction


# ---------------------------------------------------------------------------
# Collectors
# ---------------------------------------------------------------------------


def fetch_page(url: str, client: httpx.Client | None = None) -> str | None:
    """Fetch a URL and return HTML text, or None on failure."""
    close_client = client is None
    client = client or make_client()

    try:
        for attempt in range(settings.max_retries):
            try:
                resp = client.get(url)
                resp.raise_for_status()
                time.sleep(settings.http_delay)
                return resp.text
            except (httpx.HTTPError, httpx.TimeoutException) as exc:
                logger.warning("Attempt %d/%d failed for %s: %s",
                               attempt + 1, settings.max_retries, url, exc)
                time.sleep(2 ** attempt)
    finally:
        if close_client:
            client.close()

    return None


def collect_from_lab(
    lab: dict[str, Any],
    max_articles: int = 10,
    client: httpx.Client | None = None,
) -> list[CollectedArticle]:
    """从单个实验室采集研究方向信息。"""
    articles: list[CollectedArticle] = []
    now = datetime.now(timezone.utc).isoformat()
    close_client = client is None
    client = client or make_client()

    try:
        # Determine URLs to try
        urls_to_try = []
        for key in ["publications_page", "research_page", "papers_page"]:
            if lab.get(key):
                urls_to_try.append(lab[key])
        if not urls_to_try and lab.get("homepage"):
            urls_to_try.append(lab["homepage"])

        for url in urls_to_try[:3]:
            if len(articles) >= max_articles:
                break

            html = fetch_page(url, client)
            if not html:
                continue

            meta = extract_article_meta_from_html(html, url)
            body_text = extract_body_text(html)

            # Find article-like links
            soup = BeautifulSoup(html, "lxml")
            links = soup.find_all("a", href=True)

            article_candidates = []
            for link in links:
                href = link.get("href", "")
                text = link.get_text(strip=True)
                if not text or len(text) < 15:
                    continue
                # Filter for publication/article-like links
                if any(kw in href.lower() or kw in text.lower()
                       for kw in ["paper", "publication", "article", "research",
                                   "html", ".pdf", "doi", "ieee", "arxiv",
                                   "news", "story", "blog", "2024", "2025", "2026"]):
                    if href.startswith("/"):
                        from urllib.parse import urljoin
                        href = urljoin(url, href)
                    article_candidates.append({"url": href, "title": text})

            # Process article candidates
            for candidate in article_candidates[:max_articles]:
                if len(articles) >= max_articles:
                    break

                article_html = fetch_page(candidate["url"], client)
                if not article_html:
                    continue

                article_meta = extract_article_meta_from_html(article_html, candidate["url"])
                article_body = extract_body_text(article_html)

                title = article_meta["title"] or candidate["title"]
                all_text = f"{title} {article_body} {candidate['title']}"
                keywords = classify_domains(all_text)
                confidence = min(1.0, 0.5 + len(keywords) * 0.1)
                lifecycle = estimate_lifecycle(keywords + article_meta["keywords"], confidence)

                article = CollectedArticle(
                    lab_id=lab.get("id", "unknown"),
                    title=title,
                    url=candidate["url"],
                    published_at=article_meta.get("published_at", ""),
                    summary=article_body[:300],
                    keywords=list(set(keywords + article_meta["keywords"])),
                    domains=list(set(keywords)),
                    lifecycle=lifecycle,
                    page_type="article_page",
                    confidence=round(confidence, 2),
                    author=article_meta.get("author", ""),
                    captured_at=now,
                )
                articles.append(article)
                time.sleep(settings.http_delay)

    finally:
        if close_client:
            client.close()

    # If no articles found via HTTP, return a placeholder indicating discovery failed
    if not articles:
        articles.append(CollectedArticle(
            lab_id=lab.get("id", "unknown"),
            title=f"[No articles extracted from {lab.get('id', 'unknown')}]",
            url=lab.get("homepage", ""),
            published_at="",
            summary="Page could not be automatically extracted. Use Playwright MCP for JS-rendered content.",
            keywords=[],
            domains=lab.get("domains", []),
            page_type="discovery_failed",
            confidence=0.0,
            captured_at=now,
        ))

    return articles


def run_collection(
    labs: list[dict[str, Any]],
    max_per_lab: int = 10,
) -> dict[str, list[CollectedArticle]]:
    """批量采集多个实验室。"""
    results: dict[str, list[CollectedArticle]] = {}
    client = make_client()

    try:
        for lab in labs:
            lab_id = lab.get("id", "unknown")
            logger.info("Collecting from: %s (%s)", lab_id, lab.get("name", ""))
            articles = collect_from_lab(lab, max_articles=max_per_lab, client=client)
            results[lab_id] = articles
            logger.info("  -> Collected %d articles", len(articles))
    finally:
        client.close()

    return results


def save_articles(
    results: dict[str, list[CollectedArticle]],
    date_str: str,
    base_dir: str | Path = "artifacts",
) -> dict[str, list[str]]:
    """将采集结果保存到磁盘，返回每实验室的文件路径列表。"""
    base = Path(base_dir) / date_str / "articles"
    file_map: dict[str, list[str]] = {}

    for lab_id, articles in results.items():
        lab_dir = base / lab_id
        lab_dir.mkdir(parents=True, exist_ok=True)
        paths: list[str] = []

        for i, article in enumerate(articles):
            data = article.to_dict()
            slug = _make_slug(article.title)[:60] or f"article_{i:03d}"
            json_path = lab_dir / f"{slug}.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            paths.append(str(json_path))

        # Also save a combined JSON
        combined_path = lab_dir / "_all.json"
        with open(combined_path, "w", encoding="utf-8") as f:
            json.dump(
                {"lab_id": lab_id, "count": len(articles), "articles": [a.to_dict() for a in articles]},
                f,
                ensure_ascii=False,
                indent=2,
            )
        paths.append(str(combined_path))

        file_map[lab_id] = paths

    return file_map


def _make_slug(text: str) -> str:
    """Convert text to a URL-safe slug."""
    import re
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text.strip())
    text = re.sub(r"-+", "-", text)
    return text[:60]
