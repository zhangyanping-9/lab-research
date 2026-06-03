"""Collector — orchestrates crawling of lab research pages.

Supports two collection modes:
  - fast (CollectedArticle): lightweight, suitable for weekly collection
  - deep (ResearchProject): detailed project profiles, suitable for monthly/deep collection
"""

from __future__ import annotations

import json
import logging
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from src.config import settings
from src.models import CollectedArticle, ResearchProject

logger = logging.getLogger(__name__)


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


# ---------------------------------------------------------------------------
# Project-level collection (deep mode)
# ---------------------------------------------------------------------------

# Keywords for identifying project-specific pages (as opposed to news/list pages)
PROJECT_PAGE_SIGNALS = [
    "project", "grant", "award", "funding", "milestone", "roadmap",
    "initiative", "center", "consortium", "collaboration", "team",
    "progress", "breakthrough", "demonstration", "prototype",
]

PROJECT_SECTION_SIGNALS = {
    "objectives": ["objective", "goal", "aim", "target", "mission"],
    "approach": ["approach", "method", "methodology", "technique", "strategy", "architecture"],
    "team": ["team", "investigator", "pi", "researcher", "faculty", "professor", "lead"],
    "funding": ["funding", "grant", "award", "sponsor", "budget", "support"],
    "milestones": ["milestone", "timeline", "schedule", "phase", "deliverable", "roadmap"],
    "publications": ["publication", "paper", "patent", "article", "conference", "journal"],
    "results": ["result", "demonstration", "prototype", "achievement", "performance", "measured"],
}


def extract_project_details(
    html: str,
    url: str,
    lab_id: str,
    lab_name: str = "",
) -> ResearchProject | None:
    """从 HTML 页面中提取结构化研究项目信息。

    使用启发式方法识别项目相关段落并提取关键字段。
    对于最佳结果，应配合 LLM 进行提取 — 此函数提供基线提取。
    """
    soup = BeautifulSoup(html, "lxml")

    # Remove non-content elements
    for tag in soup.select("script, style, nav, footer, header, aside, .sidebar, .comments, .cookie"):
        tag.decompose()

    # ---- Title ----
    title = ""
    if soup.title:
        title = soup.title.get_text(strip=True)
    h1 = soup.find("h1")
    if h1:
        title = h1.get_text(strip=True)
    # Clean common suffixes
    for suffix in [" | MIT MTL", " | imec", " | Intel", " | NVIDIA Research",
                    " | IBM Research", " - Research", " | Research"]:
        if suffix in title:
            title = title.replace(suffix, "")

    # ---- Find main content area ----
    content = soup.find("article") or soup.find("main") or soup.find("body")
    if not content:
        content = soup

    # Get all text blocks (paragraphs, list items, headings)
    text_blocks: list[dict[str, Any]] = []
    for tag in content.find_all(["p", "li", "h2", "h3", "h4", "div"]):
        text = tag.get_text(strip=True)
        if not text or len(text) < 20:
            continue
        tag_name = tag.name
        text_blocks.append({"tag": tag_name, "text": text})

    # ---- Description (concatenate first meaningful paragraphs) ----
    description_parts = []
    for block in text_blocks[:10]:
        if block["tag"] in ("p", "div"):
            description_parts.append(block["text"])
            if len(" ".join(description_parts)) > 800:
                break
    description = " ".join(description_parts)[:2000]

    # ---- Section extraction ----
    sections: dict[str, list[str]] = {}
    current_section = "overview"
    for block in text_blocks:
        text = block["text"]
        # Check if this block is a heading
        if block["tag"] in ("h2", "h3", "h4"):
            text_lower = text.lower()
            for section_key, signals in PROJECT_SECTION_SIGNALS.items():
                if any(s in text_lower for s in signals):
                    current_section = section_key
                    break
        sections.setdefault(current_section, []).append(text)

    # ---- Extract structured fields ----
    objectives = []
    for text in sections.get("objectives", []):
        # Look for bullet points or numbered items
        for obj_signal in ["- ", "• ", "1.", "2.", "3.", "4.", "5."]:
            if obj_signal in text:
                # Split on common patterns
                parts = re.split(r"[-•]|\d+\.", text)
                for part in parts:
                    part = part.strip()
                    if len(part) > 15:
                        objectives.append(part[:300])
    if not objectives:
        # Fallback: grab first few sentences from objectives section
        obj_text = " ".join(sections.get("objectives", []))
        objectives = [s.strip() for s in obj_text.split(".") if len(s.strip()) > 20][:5]

    approach = " ".join(sections.get("approach", []))[:1000] if sections.get("approach") else ""

    # ---- Team/PI extraction ----
    pis = []
    team_text = " ".join(sections.get("team", []))
    # Look for professor/faculty names (common patterns)
    pi_patterns = [
        r"(?:Prof\.|Professor|Dr\.)\s+([A-Z][a-z]+(?:\s+[A-Z]\.)?\s+[A-Z][a-z]+)",
        r"([A-Z][a-z]+ [A-Z][a-z]+),?\s*(?:Professor|Associate Professor|Assistant Professor|Director|Lead)",
    ]
    for pat in pi_patterns:
        for match in re.finditer(pat, team_text):
            name = match.group(1).strip()
            if name not in pis and len(name) > 5:
                pis.append(name)

    # ---- Funding extraction ----
    funding_source = ""
    funding_amount = ""
    funding_text = " ".join(sections.get("funding", []))
    # Amount patterns
    amount_patterns = [
        r"\$(\d+(?:\.\d+)?)\s*(million|billion|M|B|K)",
        r"(\d+(?:\.\d+)?)\s*(million|billion)\s*(?:dollars|USD)",
    ]
    for pat in amount_patterns:
        m = re.search(pat, funding_text, re.IGNORECASE)
        if m:
            funding_amount = f"${m.group(1)} {m.group(2)}"
            break

    # Source patterns
    for source in ["DARPA", "NSF", "CHIPS Act", "DoD", "DOE", "SRC", "ARPA-E",
                    "NIST", "AFOSR", "ONR", "ARO", "Internal", "Industry"]:
        if source.lower() in funding_text.lower():
            funding_source = source
            break

    # ---- Publications ----
    publications: list[dict[str, str]] = []
    for text in sections.get("publications", []):
        # Find DOI-like patterns
        doi_match = re.search(r"10\.\d{4,}/[^\s]+", text)
        if doi_match:
            publications.append({"doi": doi_match.group(), "title": text[:200]})
        # Find arXiv IDs
        arxiv_match = re.search(r"arxiv:(\d+\.\d+)", text, re.IGNORECASE)
        if arxiv_match:
            publications.append({"arxiv": arxiv_match.group(1), "title": text[:200]})

    # ---- Milestones ----
    milestones: list[dict[str, str]] = []
    for text in sections.get("milestones", []):
        # Look for dates
        date_match = re.search(r"(20\d{2}(?:-\d{2})?|Q[1-4]\s*20\d{2})", text)
        if date_match:
            milestones.append({
                "date": date_match.group(),
                "description": text[:200],
                "status": "completed" if any(w in text.lower() for w in
                    ["completed", "achieved", "demonstrated", "published"]) else "planned",
            })

    # ---- Classify domains and lifecycle ----
    all_text = f"{title} {description} {' '.join(objectives)} {approach}"
    keywords = classify_domains(all_text)
    domains = list(set(keywords))
    confidence = min(1.0, 0.4 + len(keywords) * 0.08 + len(objectives) * 0.03 + len(milestones) * 0.05)
    lifecycle = estimate_lifecycle(keywords, confidence)

    # ---- Assemble project ----
    project = ResearchProject(
        lab_id=lab_id,
        lab_name=lab_name,
        project_name=title,
        url=url,
        description=description,
        objectives=objectives[:10],
        approach=approach,
        key_innovations=[],
        principal_investigators=pis[:10],
        team_size=str(len(pis)) if pis else "",
        collaborators=[],
        funding_source=funding_source,
        funding_amount=funding_amount,
        status="active" if description else "",
        milestones=milestones[:10],
        publications=publications[:10],
        domains=domains,
        keywords=keywords,
        lifecycle=lifecycle,
        confidence=round(confidence, 2),
        source_type="webpage",
    )

    return project


def find_project_links(html: str, base_url: str) -> list[dict[str, str]]:
    """从研究页面中发现项目详情页链接。"""
    soup = BeautifulSoup(html, "lxml")
    links = soup.find_all("a", href=True)

    candidates = []
    for link in links:
        href = link.get("href", "")
        text = link.get_text(strip=True)
        if not text or len(text) < 10:
            continue

        # Check if link text contains project-related signals
        text_lower = text.lower()
        href_lower = href.lower()

        is_project = any(
            s in text_lower or s in href_lower
            for s in PROJECT_PAGE_SIGNALS
        )
        # Also match research topics (capitalized technical terms)
        has_technical_terms = bool(re.search(
            r"(?:GAA|CFET|BSPDN|EUV|3D|2D|Chiplet|HBM|GaN|SiC|CMOS|FET|FinFET|"
            r"Nanosheet|Quantum|Photonics|Neuromorphic|Packaging|Interconnect|"
            r"Memory|DRAM|NAND|MRAM|Architecture|Process|Integration)",
            text
        ))

        if is_project or has_technical_terms:
            if href.startswith("/"):
                href = urljoin(base_url, href)
            elif not href.startswith("http"):
                continue

            # Deduplicate by URL
            if not any(c["url"] == href for c in candidates):
                candidates.append({"url": href, "title": text})

    return candidates[:20]


def collect_projects_from_lab(
    lab: dict[str, Any],
    max_projects: int = 5,
    client: httpx.Client | None = None,
) -> list[ResearchProject]:
    """从单个实验室采集详细研究项目信息 (深度采集模式)。"""
    projects: list[ResearchProject] = []
    now = datetime.now(timezone.utc).isoformat()
    close_client = client is None
    client = client or make_client()

    lab_id = lab.get("id", "unknown")
    lab_name = lab.get("name", "")

    try:
        # Step 1: Get research page to discover project links
        urls_to_try = []
        for key in ["research_page", "publications_page", "papers_page", "homepage"]:
            if lab.get(key):
                urls_to_try.append(lab[key])

        project_candidates: list[dict[str, str]] = []

        for url in urls_to_try[:3]:
            html = fetch_page(url, client)
            if not html:
                continue

            # Find project links
            found = find_project_links(html, url)
            project_candidates.extend(found)

            if len(project_candidates) >= max_projects * 2:
                break

        # Deduplicate
        seen_urls: set[str] = set()
        unique_candidates = []
        for c in project_candidates:
            if c["url"] not in seen_urls:
                seen_urls.add(c["url"])
                unique_candidates.append(c)

        # Step 2: Visit each project page and extract details
        for candidate in unique_candidates[:max_projects * 2]:
            if len(projects) >= max_projects:
                break

            project_html = fetch_page(candidate["url"], client)
            if not project_html:
                continue

            project = extract_project_details(
                project_html, candidate["url"], lab_id, lab_name
            )

            if project and project.description:
                # Don't include if it looks like a list/home page
                if len(project.description) > 50:
                    projects.append(project)
                    time.sleep(settings.http_delay)

    finally:
        if close_client:
            client.close()

    # If no projects found, create a minimal entry
    if not projects and lab.get("description"):
        projects.append(ResearchProject(
            lab_id=lab_id,
            lab_name=lab_name,
            project_name=f"{lab_name} — Research Overview",
            url=lab.get("homepage", ""),
            description=lab.get("description", ""),
            domains=lab.get("domains", []),
            key_innovations=lab.get("key_focus", []),
            funding_amount=lab.get("funding", [""])[0] if lab.get("funding") else "",
            lifecycle="growing",
            confidence=0.3,
            source_type="registry_entry",
        ))

    return projects


def save_projects(
    results: dict[str, list[ResearchProject]],
    date_str: str,
    base_dir: str | Path = "artifacts",
) -> dict[str, list[str]]:
    """将项目采集结果保存到磁盘。"""
    base = Path(base_dir) / date_str / "projects"
    file_map: dict[str, list[str]] = {}

    for lab_id, projects in results.items():
        lab_dir = base / lab_id
        lab_dir.mkdir(parents=True, exist_ok=True)
        paths: list[str] = []

        for proj in projects:
            data = proj.to_dict()
            slug = _make_slug(proj.project_name)[:60] or f"project_{proj.project_id}"
            json_path = lab_dir / f"{slug}.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            paths.append(str(json_path))

        # Combined JSON
        combined_path = lab_dir / "_all_projects.json"
        with open(combined_path, "w", encoding="utf-8") as f:
            json.dump({
                "lab_id": lab_id,
                "project_count": len(projects),
                "projects": [p.to_dict() for p in projects],
            }, f, ensure_ascii=False, indent=2)
        paths.append(str(combined_path))

        file_map[lab_id] = paths

    return file_map


def _make_slug(text: str) -> str:
    """Convert text to a URL-safe slug."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text.strip())
    text = re.sub(r"-+", "-", text)
    return text[:60]
