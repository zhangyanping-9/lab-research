"""ReportPageGenerator — generates a beautiful HTML report page from collected JSON data.

Inspired by the design of gathering.xian.li/semireport, produces a self-contained
HTML page with hero, TOC, trends, domain summary, lab activity, cross-reference,
and per-trend deep analysis sections. Fully responsive and mobile-friendly.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any, Literal

logger = logging.getLogger(__name__)

# ── Lifecycle colour mapping ──────────────────────────────────────────────
LIFECYCLE_COLORS: dict[str, str] = {
    "emerging": "#16a34a",
    "growing": "#2563eb",
    "mature": "#d97706",
    "declining": "#dc2626",
}
LIFECYCLE_LABELS: dict[str, str] = {
    "emerging": "Emerging",
    "growing": "Growing",
    "mature": "Mature",
    "declining": "Declining",
}
LIFECYCLE_CHART_ORDER = ["emerging", "growing", "mature", "declining"]

DOMAIN_EMOJI: dict[str, str] = {
    "advanced_process": "🔬",
    "advanced_packaging": "📦",
    "memory_technology": "💾",
    "ai_chip_architecture": "🧠",
    "eda_design_automation": "⚙️",
    "semiconductor_materials": "🧪",
    "quantum_computing": "⚛️",
    "photonics": "🔦",
    "manufacturing_equipment": "🏭",
    "reliability_test": "✅",
    "security": "🔒",
    "chiplet_interconnect": "🔗",
}
CATEGORY_EMOJI: dict[str, str] = {
    "corporate_rd": "🏢",
    "university_lab": "🎓",
    "university": "🎓",
    "research_institute": "🏛️",
    "government_lab": "🏛️",
    "consortia": "🤝",
    "blogs_conferences": "📰",
}


class ReportPageGenerator:
    """Generates a self-contained HTML report page from collected JSON data.

    Supports two JSON schemas:
      - ``semiconductor-research-insight-{date}.json`` (trend-level insight report)
      - ``us_semiconductor_report_{date}.json`` (US-deep report with projects+funding)
    """

    def __init__(self, base_dir: str | Path = "artifacts") -> None:
        self.base_dir = Path(base_dir)

    # ── Public API ─────────────────────────────────────────────────────────

    def generate(
        self,
        date_str: str,
        output_path: str | Path | None = None,
    ) -> str:
        """Generate a standalone HTML report page.

        Args:
            date_str: YYYY-MM-DD collection date.
            output_path: Where to write the HTML. If None, writes to
                ``{base_dir}/{date_str}/reports/semiconductor-report.html``.

        Returns:
            Absolute path to the generated HTML file.
        """
        # Load the primary insight report
        report_path = self.base_dir / date_str / "reports" / f"semiconductor-research-insight-{date_str}.json"
        if not report_path.exists():
            logger.warning("Report JSON not found at %s, trying US report", report_path)
            report_path = self.base_dir / date_str / "reports" / f"us_semiconductor_report_{date_str}.json"

        if not report_path.exists():
            msg = f"No report JSON found for {date_str} in {self.base_dir / date_str / 'reports'}"
            raise FileNotFoundError(msg)

        with open(report_path, encoding="utf-8") as f:
            data = json.load(f)

        # Detect schema type
        if "top_emerging_trends" in data:
            html = self._render_us_report(data, date_str)
        else:
            html = self._render_insight_report(data, date_str)

        # Determine output path
        if output_path is None:
            output_path = self.base_dir / date_str / "reports" / f"semiconductor-report-{date_str}.html"
        else:
            output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding="utf-8")

        logger.info("HTML report page generated: %s", output_path.resolve())
        return str(output_path.resolve())

    # ── Insight report renderer (from semiconductor-research-insight-*.json) ──

    def _render_insight_report(self, data: dict[str, Any], date_str: str) -> str:
        meta = data.get("report_meta", {})
        top_trends = data.get("top_trends", [])
        domain_summary = data.get("domain_summary", {})
        lab_activity = data.get("lab_activity", [])
        cross_ref = data.get("cross_reference", {})
        appendix = data.get("appendix", {})
        all_trends = appendix.get("all_trends", top_trends)
        lifecycle_dist = appendix.get("lifecycle_distribution", {})

        title = meta.get("title", f"半导体研究方向洞察报告 {date_str}")
        labs_covered = meta.get("labs_covered", 0)
        articles_collected = meta.get("articles_collected", 0)
        trends_identified = meta.get("trends_identified", 0)
        generated_at = meta.get("generated_at", "")[:19]

        sections_html = ""

        # ── Digest section ──
        sections_html += self._section_digest(top_trends)

        # ── Lifecycle distribution ──
        sections_html += self._section_lifecycle_chart(lifecycle_dist)

        # ── Domain summary ──
        sections_html += self._section_domain_summary(domain_summary)

        # ── Deep trends ──
        sections_html += self._section_deep_trends(top_trends[:8])

        # ── Lab activity ──
        sections_html += self._section_lab_activity(lab_activity)

        # ── Cross-reference ──
        sections_html += self._section_cross_reference(cross_ref)

        # ── All trends appendix ──
        sections_html += self._section_all_trends(all_trends)

        toc_items = [
            ("digest", "Digest"),
            ("lifecycle", "Lifecycle"),
            ("domains", "Domains"),
            ("trends", "Deep Trends"),
            ("labs", "Lab Activity"),
            ("cross-ref", "Cross-Reference"),
            ("all-trends", "All Trends"),
        ]

        return self._wrap_html(
            title=title,
            date_str=date_str,
            hero_label="Research Insight",
            hero_title=title,
            hero_subtitle=f"覆盖 {labs_covered} 个实验室 · {articles_collected} 篇文章 · {trends_identified} 个研究方向",
            generated_at=generated_at,
            toc_items=toc_items,
            sections_html=sections_html,
            all_trends_count=len(all_trends),
        )

    # ── US report renderer (from us_semiconductor_report_*.json) ──

    def _render_us_report(self, data: dict[str, Any], date_str: str) -> str:
        meta = data.get("report_meta", {})
        top_trends = data.get("top_emerging_trends", [])
        domain_summary = data.get("domain_summary", {})
        lab_activity = data.get("lab_activity_top20", [])
        cross_ref = data.get("cross_references", {})
        key_projects = data.get("key_projects", [])
        market_outlook = data.get("market_outlook", {})

        title = meta.get("title", f"美国半导体研究方向深度报告 {date_str}")
        generated_at = meta.get("generated_at", date_str)
        labs = meta.get("labs_covered", 0)
        source_cats = meta.get("source_categories", {})

        sections_html = ""

        # ── Market outlook ──
        if market_outlook:
            sections_html += self._section_market_outlook(market_outlook)

        # ── Top emerging trends ──
        sections_html += self._section_us_top_trends(top_trends)

        # ── Domain summary ──
        sections_html += self._section_us_domains(domain_summary)

        # ── Key projects ──
        sections_html += self._section_key_projects(key_projects)

        # ── Lab activity ──
        sections_html += self._section_us_labs(lab_activity)

        # ── Cross-references & funding ──
        sections_html += self._section_us_funding(cross_ref)

        toc_items = [
            ("market", "Market"),
            ("trends", "Top Trends"),
            ("domains", "Domains"),
            ("projects", "Key Projects"),
            ("labs", "Lab Activity"),
            ("funding", "Funding"),
        ]

        hero_subtitle_lines = [
            f"覆盖 {labs} 个信源",
        ]
        for cat, cnt in source_cats.items():
            hero_subtitle_lines.append(f"{cat.replace('_', ' ').title()}: {cnt}")
        hero_subtitle_lines.append(f"识别 {len(top_trends)} 个重点方向")

        return self._wrap_html(
            title=title,
            date_str=date_str,
            hero_label="US Semiconductor Research",
            hero_title=title,
            hero_subtitle=" · ".join(hero_subtitle_lines),
            generated_at=generated_at,
            toc_items=toc_items,
            sections_html=sections_html,
            all_trends_count=len(top_trends),
        )

    # ── Section builders ──────────────────────────────────────────────────

    @staticmethod
    def _section_digest(trends: list[dict]) -> str:
        if not trends:
            return ""
        items = "".join(
            f"""<li>
                <span class="digest-num">{i + 1}</span>
                <span class="digest-tag">{escape(t.get("lifecycle", ""))}</span>
                <span class="digest-text">{escape(t["direction"])}</span>
              </li>"""
            for i, t in enumerate(trends[:12])
        )
        return f"""<div class="section" id="digest">
          <div class="section-head">
            <span class="section-num">01</span>
            <h2 class="section-title">Digest</h2>
            <div class="section-sub">Top Research Directions</div>
          </div>
          <ul class="digest">{items}</ul>
        </div>"""

    @staticmethod
    def _section_lifecycle_chart(dist: dict[str, int]) -> str:
        if not dist:
            return ""
        total = sum(dist.values()) or 1
        bars = ""
        for lc in LIFECYCLE_CHART_ORDER:
            count = dist.get(lc, 0)
            pct = round(count / total * 100)
            color = LIFECYCLE_COLORS.get(lc, "#999")
            bars += f"""<div class="lc-bar-row">
                <span class="lc-label">{LIFECYCLE_LABELS.get(lc, lc)}</span>
                <div class="lc-bar-track">
                  <div class="lc-bar-fill" style="width:{pct}%;background:{color}"></div>
                </div>
                <span class="lc-count">{count}</span>
              </div>"""
        return f"""<div class="section" id="lifecycle">
          <div class="section-head">
            <span class="section-num">02</span>
            <h2 class="section-title">Lifecycle Distribution</h2>
            <div class="section-sub">Research maturity breakdown</div>
          </div>
          <div class="hl-box">
            <div class="label">Lifecycle balance</div>
            <div class="lc-chart">{bars}</div>
          </div>
        </div>"""

    @staticmethod
    def _section_domain_summary(domain_summary: dict[str, Any]) -> str:
        if not domain_summary:
            return ""
        cards = ""
        for key, info in domain_summary.items():
            emoji = DOMAIN_EMOJI.get(key, "📌")
            label = info.get("label_en") or info.get("label_zh") or key
            total = info.get("total", 0)
            emerging = info.get("emerging", 0)
            growing = info.get("growing", 0)
            mature = info.get("mature", 0)
            declining = info.get("declining", 0)
            labs = info.get("labs", 0)

            bar_html = ""
            if total > 0:
                bar_html = f"""<div class="dom-bar">
                  <span class="dom-bar-seg seg-emerging" style="width:{emerging/max(total,1)*100:.0f}%" title="Emerging {emerging}"></span>
                  <span class="dom-bar-seg seg-growing" style="width:{growing/max(total,1)*100:.0f}%" title="Growing {growing}"></span>
                  <span class="dom-bar-seg seg-mature" style="width:{mature/max(total,1)*100:.0f}%" title="Mature {mature}"></span>
                  <span class="dom-bar-seg seg-declining" style="width:{declining/max(total,1)*100:.0f}%" title="Declining {declining}"></span>
                </div>"""

            cards += f"""<div class="dom-card">
              <div class="dom-card-head">
                <span class="dom-emoji">{emoji}</span>
                <span class="dom-name">{escape(label)}</span>
                <span class="dom-count">{total}</span>
              </div>
              {bar_html}
              <div class="dom-labs">{labs} labs</div>
            </div>"""

        return f"""<div class="section" id="domains">
          <div class="section-head">
            <span class="section-num">03</span>
            <h2 class="section-title">Domain Summary</h2>
            <div class="section-sub">Research directions by domain</div>
          </div>
          <div class="dom-grid">{cards}</div>
          <div class="dom-legend">
            <span><span class="leg-dot" style="background:#16a34a"></span>Emerging</span>
            <span><span class="leg-dot" style="background:#2563eb"></span>Growing</span>
            <span><span class="leg-dot" style="background:#d97706"></span>Mature</span>
            <span><span class="leg-dot" style="background:#dc2626"></span>Declining</span>
          </div>
        </div>"""

    @staticmethod
    def _section_deep_trends(trends: list[dict]) -> str:
        if not trends:
            return ""

        items = ""
        for i, t in enumerate(trends):
            color = LIFECYCLE_COLORS.get(t.get("lifecycle", ""), "#999")
            evidence = t.get("evidence", [])
            ev_html = ""
            if evidence:
                ev_links = "".join(
                    f"""<a href="{escape(e.get("url", "#"))}" target="_blank" rel="noopener" class="item-sources">
                        [{escape(e.get("lab", ""))}] {escape(e.get("title", ""))[:80]}
                       </a><br>"""
                    for e in evidence[:3]
                )
                ev_html = f'<div class="item-sources">{ev_links}</div>'

            labs_str = ", ".join(t.get("labs_active", []))
            domains_str = ", ".join(
                DOMAIN_EMOJI.get(d, "") + " " + d.replace("_", " ")
                for d in t.get("domains", [])
            )
            confidence = t.get("confidence", 0)

            items += f"""<div class="item">
              <div class="item-title">
                <span class="trend-num">{i + 1}</span>
                {escape(t.get("direction", ""))}
                <span class="trend-badge" style="background:{color}10;color:{color};border:1px solid {color}30">
                  {LIFECYCLE_LABELS.get(t.get("lifecycle", ""), "")}
                </span>
              </div>
              <div class="item-text">
                <span class="trend-meta">
                  Confidence: <strong>{confidence:.0%}</strong> &middot;
                  Labs: <strong>{labs_str}</strong> &middot;
                  Articles: <strong>{t.get("article_count", 0)}</strong> &middot;
                  Score: <strong>{t.get("score", 0):.2f}</strong>
                </span>
                <br>
                <span class="trend-domains">{domains_str}</span>
              </div>
              {ev_html}
            </div>"""

        return f"""<div class="section" id="trends">
          <div class="section-head">
            <span class="section-num">04</span>
            <h2 class="section-title">Deep Trends</h2>
            <div class="section-sub">Detailed trend analysis with evidence</div>
          </div>
          {items}
        </div>"""

    @staticmethod
    def _section_lab_activity(lab_activity: list[dict]) -> str:
        if not lab_activity:
            return ""
        items = ""
        for lab in lab_activity:
            lab_id = lab.get("lab", "")
            dir_count = lab.get("direction_count", 0)
            art_count = lab.get("article_count", 0)
            top_dirs = lab.get("top_directions", [])
            top_str = " · ".join(escape(d) for d in top_dirs[:4])

            items += f"""<div class="company">
              <div class="company-head">
                <span class="company-name">{escape(lab_id)}</span>
                <span class="company-ticker">{dir_count} dirs &middot; {art_count} arts</span>
              </div>
              <div class="company-hl">{top_str}</div>
            </div>"""

        return f"""<div class="section" id="labs">
          <div class="section-head">
            <span class="section-num">05</span>
            <h2 class="section-title">Lab Activity</h2>
            <div class="section-sub">Research direction counts by lab</div>
          </div>
          {items}
        </div>"""

    @staticmethod
    def _section_cross_reference(cross_ref: dict[str, Any]) -> str:
        convs = cross_ref.get("convergences", [])
        if not convs:
            return ""
        items = ""
        for c in convs:
            strength = c.get("strength", "moderate")
            badge = "🟢" if strength == "strong" else "🟡"
            items += f"""<div class="reading">
              <div class="reading-num">{badge}</div>
              <div>
                <span class="reading-title">{escape(c.get("direction", ""))}</span>
                <div class="reading-source">{escape(", ".join(c.get("labs", [])))}</div>
                <div class="reading-desc">Cross-lab convergence &middot; {strength}</div>
              </div>
            </div>"""

        total = cross_ref.get("total_convergences", len(convs))
        return f"""<div class="section" id="cross-ref">
          <div class="section-head">
            <span class="section-num">06</span>
            <h2 class="section-title">Cross-Reference</h2>
            <div class="section-sub">{total} cross-lab convergences identified</div>
          </div>
          {items}
        </div>"""

    @staticmethod
    def _section_all_trends(all_trends: list[dict]) -> str:
        if not all_trends:
            return ""
        rows = ""
        for t in all_trends:
            color = LIFECYCLE_COLORS.get(t.get("lifecycle", ""), "#999")
            labs_str = ", ".join(t.get("labs_active", [])[:4])
            rows += f"""<tr>
              <td>{escape(t.get("direction", ""))}</td>
              <td><span class="at-badge" style="color:{color}">{LIFECYCLE_LABELS.get(t.get("lifecycle", ""), "")}</span></td>
              <td>{t.get("confidence", 0):.0%}</td>
              <td class="at-score">{t.get("score", 0):.2f}</td>
              <td>{escape(labs_str)}</td>
            </tr>"""

        return f"""<div class="section" id="all-trends">
          <div class="section-head">
            <span class="section-num">07</span>
            <h2 class="section-title">All Trends</h2>
            <div class="section-sub">Complete research direction list</div>
          </div>
          <div class="table-wrap">
            <table class="data-table">
              <thead><tr><th>Direction</th><th>Lifecycle</th><th>Confidence</th><th>Score</th><th>Labs</th></tr></thead>
              <tbody>{rows}</tbody>
            </table>
          </div>
        </div>"""

    # ── US report sections ─────────────────────────────────────────────────

    @staticmethod
    def _section_market_outlook(mo: dict[str, Any]) -> str:
        if not mo:
            return ""
        items = "".join(
            f"""<div class="stock-card">
              <div class="stock-ticker">{escape(k.replace("_", " ").title())}</div>
              <div class="stock-price" style="font-size:0.95rem">{escape(str(v))}</div>
            </div>"""
            for k, v in list(mo.items())[:8]
        )
        return f"""<div class="section" id="market">
          <div class="section-head">
            <span class="section-num">01</span>
            <h2 class="section-title">Market Outlook</h2>
            <div class="section-sub">Global semiconductor market projections</div>
          </div>
          <div class="stock-grid">{items}</div>
        </div>"""

    @staticmethod
    def _section_us_top_trends(top_trends: list[dict]) -> str:
        if not top_trends:
            return ""
        items = ""
        for t in top_trends:
            color = LIFECYCLE_COLORS.get(t.get("lifecycle", ""), "#999")
            labs_str = ", ".join(t.get("key_labs", [])[:6])
            summary = t.get("summary", "")
            source_count = t.get("source_count", 0)

            items += f"""<div class="item">
              <div class="item-title">
                <span class="trend-num">#{t.get("rank", "")}</span>
                {escape(t.get("direction", ""))}
                <span class="trend-badge" style="background:{color}10;color:{color};border:1px solid {color}30">
                  {LIFECYCLE_LABELS.get(t.get("lifecycle", ""), "")}
                </span>
              </div>
              <div class="item-text">
                <strong>Confidence:</strong> {t.get("confidence", 0):.0%} &middot;
                <strong>Sources:</strong> {source_count} &middot;
                <strong>Labs:</strong> {escape(labs_str)}
                <br>
                {escape(summary)}
              </div>
            </div>"""

        return f"""<div class="section" id="trends">
          <div class="section-head">
            <span class="section-num">02</span>
            <h2 class="section-title">Top Emerging Trends</h2>
            <div class="section-sub">Key research directions 2025-2026</div>
          </div>
          {items}
        </div>"""

    @staticmethod
    def _section_us_domains(domain_summary: dict[str, Any]) -> str:
        if not domain_summary:
            return ""
        rows = ""
        for key, info in domain_summary.items():
            emoji = DOMAIN_EMOJI.get(key, "📌")
            label = key.replace("_", " ").title()
            trends = info.get("trends", 0)
            labs_active = info.get("labs_active", 0)
            top_dir = info.get("top_direction", "")
            lifecycle = info.get("lifecycle", "")
            color = LIFECYCLE_COLORS.get(lifecycle, "#999")

            rows += f"""<tr>
              <td>{emoji} {escape(label)}</td>
              <td>{trends}</td>
              <td>{labs_active}</td>
              <td>{escape(top_dir[:60])}</td>
              <td><span class="at-badge" style="color:{color}">{escape(lifecycle.title())}</span></td>
            </tr>"""
        return f"""<div class="section" id="domains">
          <div class="section-head">
            <span class="section-num">03</span>
            <h2 class="section-title">Domain Landscape</h2>
            <div class="section-sub">Research domains and activity levels</div>
          </div>
          <div class="table-wrap">
            <table class="data-table">
              <thead><tr><th>Domain</th><th>Trends</th><th>Labs</th><th>Top Direction</th><th>Phase</th></tr></thead>
              <tbody>{rows}</tbody>
            </table>
          </div>
        </div>"""

    @staticmethod
    def _section_key_projects(projects: list[dict]) -> str:
        if not projects:
            return ""
        items = ""
        for p in projects:
            name = p.get("project_name", "")
            lab = p.get("lab_id", "")
            desc = p.get("description", "")[:200]
            funding = p.get("funding", "")
            status = p.get("status", "")
            innovations = p.get("key_innovations", [])

            innov_str = ""
            if innovations:
                innov_str = "<br>" + " · ".join(
                    escape(str(i)) for i in innovations[:3]
                )

            items += f"""<div class="item">
              <div class="item-title">{escape(name)} <span class="trend-badge" style="color:#666;border-color:#ddd">{escape(status)}</span></div>
              <div class="item-text">
                <strong>{escape(lab)}</strong> &middot; {escape(funding)}<br>
                {escape(desc)}{innov_str}
              </div>
            </div>"""

        return f"""<div class="section" id="projects">
          <div class="section-head">
            <span class="section-num">04</span>
            <h2 class="section-title">Key Projects</h2>
            <div class="section-sub">Major research initiatives</div>
          </div>
          {items}
        </div>"""

    @staticmethod
    def _section_us_labs(lab_activity: list[dict]) -> str:
        if not lab_activity:
            return ""
        rows = ""
        for lab in lab_activity:
            name = lab.get("lab_name", lab.get("lab_id", ""))
            cat = lab.get("category", "")
            emoji = CATEGORY_EMOJI.get(cat, "🏢")
            dir_count = lab.get("direction_count", 0)
            projects = lab.get("key_projects", [])
            proj_str = ", ".join(str(p) for p in projects[:3])

            rows += f"""<tr>
              <td>{emoji} {escape(name)}</td>
              <td>{cat.replace('_', ' ')}</td>
              <td>{dir_count}</td>
              <td>{escape(proj_str[:80])}</td>
            </tr>"""
        return f"""<div class="section" id="labs">
          <div class="section-head">
            <span class="section-num">05</span>
            <h2 class="section-title">Lab Activity</h2>
            <div class="section-sub">Top 20 labs by research direction count</div>
          </div>
          <div class="table-wrap">
            <table class="data-table">
              <thead><tr><th>Lab</th><th>Category</th><th>Dirs</th><th>Key Projects</th></tr></thead>
              <tbody>{rows}</tbody>
            </table>
          </div>
        </div>"""

    @staticmethod
    def _section_us_funding(cross_ref: dict[str, Any]) -> str:
        fm = cross_ref.get("funding_map", {})
        if not fm:
            return ""
        sections = ""

        for section_name, section_data in [
            ("CHIPS Act Related", fm.get("chips_act_related", [])),
            ("DoD / DARPA", fm.get("dod_darpa", [])),
            ("Venture Capital", fm.get("venture_capital", [])),
        ]:
            if not section_data:
                continue
            rows = ""
            for item in section_data:
                name = item.get("program") or item.get("company") or ""
                amount = item.get("amount", "")
                lead = item.get("lead", "")
                rows += f"""<tr>
                  <td>{escape(name)}</td>
                  <td class="mono">{escape(amount)}</td>
                  <td>{escape(lead)}</td>
                </tr>"""
            sections += f"""<div class="hl-box">
              <div class="label">{escape(section_name)}</div>
              <div class="table-wrap">
                <table class="data-table compact">
                  <tbody>{rows}</tbody>
                </table>
              </div>
            </div>"""

        if not sections:
            return ""

        return f"""<div class="section" id="funding">
          <div class="section-head">
            <span class="section-num">06</span>
            <h2 class="section-title">Funding Landscape</h2>
            <div class="section-sub">Government programs and VC investments</div>
          </div>
          {sections}
        </div>"""

    # ── HTML wrapper ──────────────────────────────────────────────────────

    def _wrap_html(
        self,
        title: str,
        date_str: str,
        hero_label: str,
        hero_title: str,
        hero_subtitle: str,
        generated_at: str,
        toc_items: list[tuple[str, str]],
        sections_html: str,
        all_trends_count: int,
        **kwargs: Any,
    ) -> str:
        # `**kwargs` absorbs any extra context callers pass without binding.
        hero_date = date_str
        if generated_at:
            try:
                dt = datetime.fromisoformat(generated_at)
                hero_date = dt.strftime("%Y.%m.%d")
            except (ValueError, TypeError):
                hero_date = date_str

        # TOC
        toc_links = "".join(
            f"""<a href="#{hid}" class="toc-item">
              <span class="toc-num">{i+1:02d}</span>
              <span class="toc-label">{label}</span>
            </a>"""
            for i, (hid, label) in enumerate(toc_items)
        )

        # Download links (JSON and Markdown)
        download_json = f"semiconductor-research-insight-{date_str}.json"
        download_md = f"semiconductor-research-insight-{date_str}.md"
        download_html = f"semiconductor-report-{date_str}.html"

        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escape(title)}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&family=Inter:wght@300;400;500;600;700;900&display=swap');
  @font-face {{ font-family: 'HarmonyOS Sans'; src: url('https://cdn.jsdelivr.net/npm/harmonyos-sans@1.0.0/HarmonyOS_Sans_SC/HarmonyOS_Sans_SC_Regular.woff2') format('woff2'); font-weight: 400; }}
  @font-face {{ font-family: 'HarmonyOS Sans'; src: url('https://cdn.jsdelivr.net/npm/harmonyos-sans@1.0.0/HarmonyOS_Sans_SC/HarmonyOS_Sans_SC_Medium.woff2') format('woff2'); font-weight: 500; }}
  @font-face {{ font-family: 'HarmonyOS Sans'; src: url('https://cdn.jsdelivr.net/npm/harmonyos-sans@1.0.0/HarmonyOS_Sans_SC/HarmonyOS_Sans_SC_Bold.woff2') format('woff2'); font-weight: 700; }}
  @font-face {{ font-family: 'HarmonyOS Sans'; src: url('https://cdn.jsdelivr.net/npm/harmonyos-sans@1.0.0/HarmonyOS_Sans_SC/HarmonyOS_Sans_SC_Light.woff2') format('woff2'); font-weight: 300; }}

  :root {{
    --black: #141414; --dark: #1a1a1a; --body: #333; --secondary: #666;
    --tertiary: #999; --border: #e0e0e0; --light: #efefef; --bg: #fafaf8;
    --white: #fff; --red: #c0392b; --green: #16a34a; --down-red: #dc2626;
    --tag-bg: #f5f5f3; --font: 'HarmonyOS Sans', -apple-system, 'PingFang SC', sans-serif;
    --mono: 'JetBrains Mono', 'Menlo', monospace;
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html {{ font-size: 16px; scroll-behavior: smooth; -webkit-font-smoothing: antialiased; }}
  body {{ font-family: var(--font); color: var(--body); background: var(--white); line-height: 1.8; }}

  .content-zone {{
    background: var(--bg);
    border-top: 1px solid var(--border);
    padding-top: 64px;
    margin-top: 0;
  }}

  /* ===== NAV ===== */
  .nav {{
    position: sticky; top: 0; z-index: 100;
    background: rgba(255,255,255,0.92); backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--border);
    padding: 0 24px;
  }}
  .nav-inner {{
    max-width: 1100px; margin: 0 auto;
    display: flex; justify-content: space-between; align-items: center;
    height: 56px;
  }}
  .nav-brand {{
    font-size: 0.75rem; font-weight: 600; letter-spacing: 0.12em;
    text-transform: uppercase; color: var(--dark);
    display: flex; align-items: center; gap: 8px;
  }}
  .nav-date {{ font-family: var(--mono); font-size: 0.7rem; color: var(--tertiary); margin-right: 16px; }}
  .nav-right {{ display: flex; gap: 8px; align-items: center; }}
  .btn-download {{
    display: inline-flex; align-items: center; gap: 6px;
    padding: 7px 14px; border-radius: 6px; font-size: 0.72rem; font-weight: 500;
    text-decoration: none; border: 1px solid var(--border); color: var(--dark);
    background: var(--white); transition: all 0.15s; cursor: pointer;
    font-family: var(--font);
  }}
  .btn-download:hover {{ border-color: var(--dark); background: var(--dark); color: var(--white); }}
  .btn-download svg {{ width: 14px; height: 14px; }}

  /* ===== HERO ===== */
  .hero {{
    max-width: 760px; margin: 0 auto; padding: 80px 24px 64px;
  }}
  .hero-label {{
    font-family: var(--mono); font-size: 0.72rem; letter-spacing: 0.12em;
    color: var(--red); text-transform: uppercase; margin-bottom: 20px;
  }}
  .hero h1 {{
    font-size: 2.8rem; font-weight: 900; color: var(--black);
    line-height: 1.2; letter-spacing: -0.02em; margin-bottom: 28px;
  }}
  .hero-subtitle {{
    font-size: 1.1rem; font-weight: 300; color: var(--secondary);
    line-height: 1.85; border-left: 2px solid var(--border); padding-left: 20px;
    max-width: 580px;
  }}
  .hero-meta {{
    margin-top: 40px; display: flex; gap: 24px; flex-wrap: wrap;
  }}
  .hero-meta-item {{
    font-family: var(--mono); font-size: 0.7rem; color: var(--tertiary);
    padding: 5px 12px; background: var(--white); border-radius: 4px;
    border: 1px solid var(--light);
  }}

  /* ===== TOC ===== */
  .toc {{
    max-width: 760px; margin: 0 auto; padding: 0 24px 48px;
  }}
  .toc-grid {{
    display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 8px;
  }}
  .toc-item {{
    display: flex; align-items: baseline; gap: 10px;
    padding: 10px 14px; border-radius: 6px;
    text-decoration: none; color: var(--body);
    transition: background 0.12s;
  }}
  .toc-item:hover {{ background: var(--tag-bg); }}
  .toc-num {{ font-family: var(--mono); font-size: 0.68rem; color: var(--red); }}
  .toc-label {{ font-size: 0.85rem; font-weight: 500; }}

  /* ===== CONTENT ===== */
  .content {{ max-width: 760px; margin: 0 auto; padding: 0 24px; }}

  .section {{ margin-bottom: 64px; }}
  .section-head {{ margin-bottom: 32px; }}
  .section-num {{
    font-family: var(--mono); font-size: 0.68rem; color: var(--red);
    letter-spacing: 0.08em; display: block; margin-bottom: 4px;
  }}
  .section-title {{ font-size: 1.6rem; font-weight: 700; color: var(--black); margin-bottom: 4px; }}
  .section-sub {{ font-family: var(--mono); font-size: 0.72rem; color: var(--tertiary); text-transform: uppercase; }}

  /* Digest */
  .digest {{ list-style: none; }}
  .digest li {{
    padding: 16px 0; border-bottom: 1px solid var(--light);
    display: flex; gap: 14px; align-items: baseline;
  }}
  .digest-num {{ font-family: var(--mono); font-size: 0.75rem; color: var(--tertiary); width: 22px; flex-shrink: 0; }}
  .digest-tag {{
    font-family: var(--mono); font-size: 0.62rem; color: var(--secondary);
    background: var(--tag-bg); padding: 2px 8px; border-radius: 3px;
    margin-right: 8px; flex-shrink: 0;
  }}
  .digest-text {{ font-size: 0.95rem; color: var(--dark); font-weight: 500; line-height: 1.7; }}

  /* Lifecycle chart */
  .lc-chart {{ display: flex; flex-direction: column; gap: 12px; padding: 4px 0; }}
  .lc-bar-row {{ display: flex; align-items: center; gap: 12px; }}
  .lc-label {{ font-family: var(--mono); font-size: 0.72rem; color: var(--secondary); width: 80px; flex-shrink: 0; }}
  .lc-bar-track {{ flex: 1; height: 12px; background: var(--light); border-radius: 6px; overflow: hidden; }}
  .lc-bar-fill {{ height: 100%; border-radius: 6px; transition: width 0.6s ease; min-width: 0; }}
  .lc-count {{ font-family: var(--mono); font-size: 0.85rem; color: var(--dark); width: 24px; text-align: right; }}

  /* Domain cards */
  .dom-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
  @media (max-width: 600px) {{ .dom-grid {{ grid-template-columns: 1fr; }} }}
  .dom-card {{
    padding: 16px; border: 1px solid var(--light); border-radius: 8px;
    background: var(--white); transition: box-shadow 0.15s;
  }}
  .dom-card:hover {{ box-shadow: 0 2px 12px rgba(0,0,0,0.06); }}
  .dom-card-head {{ display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }}
  .dom-emoji {{ font-size: 1.2rem; }}
  .dom-name {{ font-size: 0.85rem; font-weight: 600; color: var(--dark); flex: 1; }}
  .dom-count {{ font-family: var(--mono); font-size: 1.1rem; font-weight: 500; color: var(--black); }}
  .dom-bar {{ display: flex; height: 6px; border-radius: 3px; overflow: hidden; margin-bottom: 8px; }}
  .dom-bar-seg {{ min-width: 2px; }}
  .seg-emerging {{ background: #16a34a; }}
  .seg-growing {{ background: #2563eb; }}
  .seg-mature {{ background: #d97706; }}
  .seg-declining {{ background: #dc2626; }}
  .dom-labs {{ font-family: var(--mono); font-size: 0.62rem; color: var(--tertiary); }}
  .dom-legend {{ display: flex; gap: 16px; margin-top: 12px; font-size: 0.72rem; color: var(--secondary); flex-wrap: wrap; }}
  .leg-dot {{ display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }}

  /* Items */
  .item {{ margin-bottom: 28px; padding-bottom: 28px; border-bottom: 1px solid var(--light); }}
  .item:last-child {{ border-bottom: none; }}
  .item-title {{ font-size: 1.02rem; font-weight: 700; color: var(--dark); margin-bottom: 8px; }}
  .item-text {{ font-size: 0.92rem; color: var(--body); line-height: 1.8; }}
  .item-sources {{ margin-top: 6px; }}
  .item-sources a {{
    font-family: var(--mono); font-size: 0.7rem; color: var(--tertiary);
    text-decoration: none; border-bottom: 1px dotted var(--border); margin-right: 10px;
    transition: color 0.12s, border-bottom-color 0.12s; line-height: 1.6;
  }}
  .item-sources a:hover {{ color: var(--red); border-bottom-color: var(--red); }}

  .trend-num {{
    font-family: var(--mono); font-size: 0.75rem; color: var(--tertiary);
    margin-right: 6px;
  }}
  .trend-badge {{
    font-family: var(--mono); font-size: 0.6rem; font-weight: 500;
    padding: 2px 8px; border-radius: 4px; margin-left: 8px;
    text-transform: uppercase; letter-spacing: 0.04em;
  }}
  .trend-meta {{ font-family: var(--mono); font-size: 0.7rem; color: var(--tertiary); }}
  .trend-domains {{ font-family: var(--mono); font-size: 0.65rem; color: var(--secondary); }}

  /* Highlight box */
  .hl-box {{
    background: var(--tag-bg); border-left: 3px solid var(--black);
    padding: 20px 24px; margin: 20px 0; border-radius: 0 6px 6px 0;
  }}
  .hl-box .label {{ font-family: var(--mono); font-size: 0.65rem; color: var(--tertiary); text-transform: uppercase; margin-bottom: 12px; }}

  /* Company blocks */
  .company {{ margin-bottom: 28px; padding-bottom: 28px; border-bottom: 1px solid var(--light); }}
  .company:last-child {{ border-bottom: none; }}
  .company-head {{ display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 12px; }}
  .company-name {{ font-size: 1.05rem; font-weight: 700; color: var(--black); }}
  .company-ticker {{ font-family: var(--mono); font-size: 0.7rem; color: var(--tertiary); }}
  .company-hl {{
    border-left: 3px solid var(--red); padding: 10px 16px; margin-bottom: 14px;
    background: linear-gradient(90deg, #fdf8f7, transparent); border-radius: 0 6px 6px 0;
    font-size: 0.88rem; color: var(--dark); font-weight: 500; line-height: 1.7;
  }}

  /* Reading-style cross-ref */
  .reading {{ display: flex; gap: 16px; padding: 18px 0; border-bottom: 1px solid var(--light); }}
  .reading:last-child {{ border-bottom: none; }}
  .reading-num {{ font-size: 1.3rem; line-height: 1; padding-top: 4px; }}
  .reading-title {{ font-size: 1rem; font-weight: 700; color: var(--dark); margin-bottom: 4px; display: block; }}
  .reading-source {{ font-family: var(--mono); font-size: 0.65rem; color: var(--tertiary); margin-bottom: 4px; }}
  .reading-desc {{ font-size: 0.82rem; color: var(--secondary); line-height: 1.6; }}

  /* Stock grid */
  .stock-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
  @media (max-width: 600px) {{ .stock-grid {{ grid-template-columns: 1fr; }} }}
  .stock-card {{
    padding: 18px; border: 1px solid var(--light); border-radius: 8px;
    background: var(--white); transition: box-shadow 0.15s;
  }}
  .stock-card:hover {{ box-shadow: 0 2px 12px rgba(0,0,0,0.06); }}
  .stock-ticker {{ font-family: var(--mono); font-size: 0.65rem; color: var(--tertiary); margin-bottom: 6px; text-transform: uppercase; }}
  .stock-price {{ font-family: var(--mono); font-size: 1.2rem; font-weight: 500; color: var(--black); line-height: 1.3; word-break: break-word; }}

  /* Tables */
  .table-wrap {{ overflow-x: auto; }}
  .data-table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; }}
  .data-table th {{
    text-align: left; padding: 10px 12px; font-family: var(--mono);
    font-size: 0.7rem; color: var(--tertiary); text-transform: uppercase;
    border-bottom: 2px solid var(--border); letter-spacing: 0.04em;
  }}
  .data-table td {{ padding: 10px 12px; border-bottom: 1px solid var(--light); color: var(--body); }}
  .data-table tr:hover td {{ background: var(--tag-bg); }}
  .data-table.compact td {{ padding: 6px 12px; font-size: 0.8rem; }}
  .mono {{ font-family: var(--mono); }}
  .at-badge {{ font-family: var(--mono); font-size: 0.62rem; font-weight: 500; }}
  .at-score {{ font-family: var(--mono); font-size: 0.8rem; }}

  /* Footer */
  .site-footer {{
    max-width: 760px; margin: 48px auto 0; padding: 24px 24px 48px;
    border-top: 1px solid var(--border);
    display: flex; justify-content: space-between; align-items: center;
    font-family: var(--mono); font-size: 0.65rem; color: var(--tertiary);
  }}

  /* ===== MOBILE ===== */
  @media (max-width: 720px) {{
    html {{ font-size: 15px; }}
    .nav {{ padding: 0 16px; }}
    .nav-inner {{ height: 52px; }}
    .nav-brand {{ font-size: 0.68rem; }}
    .nav-date {{ display: none; }}
    .nav-right .btn-download {{ display: none; }}

    .hero {{ padding: 40px 20px 32px; }}
    .hero-label {{ font-size: 0.68rem; }}
    .hero h1 {{ font-size: 1.85rem; }}
    .hero-subtitle {{ font-size: 0.98rem; padding-left: 14px; }}
    .hero-meta {{ gap: 8px; }}
    .hero-meta-item {{ font-size: 0.62rem; }}

    .toc {{ padding: 0 0 32px; }}
    .toc-grid {{
      display: flex; flex-wrap: nowrap; gap: 8px;
      padding: 0 20px 12px; overflow-x: auto;
      scrollbar-width: none;
    }}
    .toc-grid::-webkit-scrollbar {{ display: none; }}
    .toc-item {{
      flex-shrink: 0; flex-direction: column; align-items: flex-start;
      gap: 2px; padding: 10px 14px; background: var(--white);
      border: 1px solid var(--light); border-radius: 10px;
      min-width: 110px;
    }}
    .toc-num {{ font-size: 0.62rem; }}
    .toc-label {{ font-size: 0.78rem; white-space: nowrap; }}

    .content-zone {{ padding-top: 40px; }}
    .content {{ padding: 0 20px; }}
    .section {{ margin-bottom: 48px; }}
    .section-title {{ font-size: 1.35rem; }}

    .digest li {{ flex-wrap: wrap; padding: 14px 0; gap: 6px; }}
    .digest-num {{ font-size: 0.68rem; width: auto; background: var(--tag-bg); padding: 2px 8px; border-radius: 3px; }}
    .digest-text {{ flex-basis: 100%; }}

    .item {{ margin-bottom: 24px; padding-bottom: 24px; }}
    .item-title {{ font-size: 0.98rem; }}
    .item-text {{ font-size: 0.9rem; }}
    .company {{ margin-bottom: 24px; padding-bottom: 24px; }}
    .company-head {{ flex-direction: column; gap: 2px; }}

    .reading {{ gap: 12px; padding: 14px 0; }}
    .reading-num {{ font-size: 1.1rem; }}
    .reading-title {{ font-size: 0.92rem; }}
    .reading-source {{ font-size: 0.6rem; }}

    .data-table {{ font-size: 0.78rem; }}
    .data-table th, .data-table td {{ padding: 8px 10px; }}
    .stock-card {{ padding: 14px 12px; }}
    .stock-price {{ font-size: 1rem; }}
    .site-footer {{ flex-direction: column; gap: 8px; align-items: flex-start; padding: 24px 20px 40px; font-size: 0.6rem; }}
  }}
</style>
</head>
<body>

<!-- NAV -->
<nav class="nav">
  <div class="nav-inner">
    <div class="nav-brand">Semiconductor Report</div>
    <div class="nav-right">
      <span class="nav-date">{escape(hero_date)}</span>
      <a class="btn-download" href="{escape(download_json)}" download>
        <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M8 2v9m0 0l-3-3m3 3l3-3M3 13h10"/></svg>
        JSON
      </a>
      <a class="btn-download" href="{escape(download_md)}" download>
        <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M8 2v9m0 0l-3-3m3 3l3-3M3 13h10"/></svg>
        MD
      </a>
    </div>
  </div>
</nav>

<!-- HERO -->
<div class="hero">
  <div class="hero-label">{escape(hero_label)}</div>
  <h1>{escape(hero_title)}</h1>
  <div class="hero-subtitle">{escape(hero_subtitle)}</div>
  <div class="hero-meta">
    <span class="hero-meta-item">{escape(hero_date)}</span>
    <span class="hero-meta-item">{all_trends_count} trends</span>
  </div>
</div>

<!-- TOC -->
<div class="toc">
  <div class="toc-grid">
    {toc_links}
  </div>
</div>

<!-- CONTENT -->
<div class="content-zone">
  <div class="content">
    {sections_html}
  </div>
</div>

<!-- FOOTER -->
<footer class="site-footer">
  <span>Semi Research Direction Collect</span>
  <span>Generated automatically &middot; {escape(hero_date)}</span>
</footer>

</body>
</html>"""

    # ── Index page generation ──────────────────────────────────────────────

    def generate_index_page(self) -> str:
        """Generate an ``index.html`` listing all available reports."""
        reports: list[dict[str, Any]] = []

        # Scan artifacts/ for report JSONs
        artifacts_dir = self.base_dir
        if not artifacts_dir.exists():
            return self._render_empty_index()

        for subdir in sorted(artifacts_dir.iterdir(), reverse=True):
            if not subdir.is_dir() or subdir.name.startswith("."):
                continue
            reports_dir = subdir / "reports"
            if not reports_dir.exists():
                continue

            # Try to load the insight report
            for fname in [
                f"semiconductor-research-insight-{subdir.name}.json",
                f"us_semiconductor_report_{subdir.name}.json",
            ]:
                fpath = reports_dir / fname
                if fpath.exists():
                    try:
                        with open(fpath, encoding="utf-8") as f:
                            data = json.load(f)
                        meta = data.get("report_meta", {})

                        # Detect schema
                        has_us = "top_emerging_trends" in data
                        trends = data.get("top_emerging_trends", data.get("top_trends", []))
                        trends_count = len(trends)
                        labs_count = meta.get("labs_covered", len(data.get("lab_activity", [])))

                        # Find the HTML report file
                        html_path = reports_dir / f"semiconductor-report-{subdir.name}.html"
                        has_html = html_path.exists()

                        reports.append({
                            "date": subdir.name,
                            "title": meta.get("title", f"Report {subdir.name}"),
                            "trends_count": trends_count,
                            "labs_count": labs_count,
                            "has_html": has_html,
                            "has_json": True,
                            "type": "us" if has_us else "insight",
                        })
                        break
                    except (json.JSONDecodeError, KeyError):
                        continue

        if not reports:
            return self._render_empty_index()

        rows = ""
        for r in reports:
            date = r["date"]
            html_link = f"{date}/reports/semiconductor-report-{date}.html"
            json_link = f"{date}/reports/semiconductor-research-insight-{date}.json"

            type_badge = '<span class="type-badge type-us">US Deep</span>' if r["type"] == "us" else ""
            links_html = f"""<a href="{html_link}" class="rp-link">HTML</a> · <a href="{json_link}" class="rp-link">JSON</a>"""

            rows += f"""<div class="rp-row">
              <div class="rp-date">{date}</div>
              <div class="rp-title">{escape(r['title'][:80])} {type_badge}</div>
              <div class="rp-stats">{r['trends_count']} trends · {r['labs_count']} labs</div>
              <div class="rp-links">{links_html}</div>
            </div>"""

        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Semiconductor Research Reports</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&family=Inter:wght@300;400;500;600;700&display=swap');
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: 'Inter', -apple-system, 'PingFang SC', sans-serif; background: #fafaf8; color: #333; line-height: 1.8; }}
  .wrap {{ max-width: 860px; margin: 0 auto; padding: 40px 24px; }}
  h1 {{ font-size: 2rem; font-weight: 800; color: #141414; margin-bottom: 6px; letter-spacing: -0.01em; }}
  .sub {{ font-size: 0.9rem; color: #666; margin-bottom: 32px; }}
  .rp-row {{ display: grid; grid-template-columns: 100px 1fr auto auto; gap: 12px; align-items: center; padding: 14px 16px; border-bottom: 1px solid #eee; transition: background 0.1s; }}
  .rp-row:hover {{ background: #fff; }}
  .rp-date {{ font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #999; }}
  .rp-title {{ font-size: 0.85rem; font-weight: 600; color: #1a1a1a; }}
  .rp-stats {{ font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #999; }}
  .rp-links {{ font-size: 0.72rem; }}
  .rp-link {{ color: #c0392b; text-decoration: none; }}
  .rp-link:hover {{ text-decoration: underline; }}
  .type-badge {{ font-size: 0.6rem; font-weight: 500; padding: 2px 8px; border-radius: 4px; margin-left: 6px; }}
  .type-us {{ background: #eff6ff; color: #1e40af; }}
  .footer {{ margin-top: 48px; padding-top: 24px; border-top: 1px solid #e0e0e0; font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; color: #999; display: flex; justify-content: space-between; }}
  @media (max-width: 640px) {{ .rp-row {{ grid-template-columns: 1fr; gap: 4px; }} .rp-stats {{ font-size: 0.6rem; }} }}
</style>
</head>
<body>
<div class="wrap">
  <h1>Semiconductor Research Reports</h1>
  <div class="sub">Global semiconductor lab direction collection &amp; analysis</div>
  <div class="rp-list">
    {rows}
  </div>
  <div class="footer">
    <span>Semi Research Direction Collect</span>
    <span>{len(reports)} reports</span>
  </div>
</div>
</body>
</html>"""

    @staticmethod
    def _render_empty_index() -> str:
        return """<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><title>Semiconductor Reports</title>
<style>body{font-family:system-ui;background:#fafaf8;color:#333;padding:60px 24px;max-width:600px;margin:0 auto;line-height:1.8}h1{font-size:2rem;color:#141414}.sub{color:#999}</style>
</head>
<body>
<h1>Semiconductor Research Reports</h1>
<p class="sub">No reports available yet. Run the collector first.</p>
</body>
</html>"""


# ── CLI entry point ────────────────────────────────────────────────────────

def main() -> None:
    """CLI: generate HTML report pages from existing JSON data."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate HTML report pages from collected data",
    )
    parser.add_argument("--date", help="YYYY-MM-DD date (default: latest)")
    parser.add_argument("--base-dir", default="artifacts", help="Artifacts base directory")
    parser.add_argument("--index-only", action="store_true", help="Only regenerate the index page")
    parser.add_argument("--all", action="store_true", help="Regenerate all reports")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    gen = ReportPageGenerator(args.base_dir)

    if args.index_only:
        idx_path = Path(args.base_dir) / "index.html"
        idx_path.write_text(gen.generate_index_page(), encoding="utf-8")
        logger.info("Index page written: %s", idx_path.resolve())
        return

    if args.all:
        artifacts_dir = Path(args.base_dir)
        dates = sorted(
            (d for d in artifacts_dir.iterdir() if d.is_dir() and not d.name.startswith(".")),
            reverse=True,
        )
        for d in dates:
            try:
                gen.generate(d.name)
            except FileNotFoundError:
                logger.debug("No report JSON for %s, skipping", d.name)
        # Then update index
        idx_path = Path(args.base_dir) / "index.html"
        idx_path.write_text(gen.generate_index_page(), encoding="utf-8")
        logger.info("All reports generated, index updated.")
        return

    if args.date:
        gen.generate(args.date)
    else:
        # Auto-detect latest
        artifacts_dir = Path(args.base_dir)
        dates = sorted(
            (d for d in artifacts_dir.iterdir() if d.is_dir() and not d.name.startswith(".")),
            reverse=True,
        )
        if not dates:
            logger.error("No data directories found in %s", args.base_dir)
            return
        gen.generate(dates[0].name)

    # Update index
    idx_path = Path(args.base_dir) / "index.html"
    idx_path.write_text(gen.generate_index_page(), encoding="utf-8")
    logger.info("Index page updated: %s", idx_path.resolve())


if __name__ == "__main__":
    main()
