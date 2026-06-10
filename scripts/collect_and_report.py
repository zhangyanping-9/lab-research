#!/usr/bin/env python3
"""
半导体研究方向采集与洞察报告 — 主入口

Usage:
    # 端到端采集+分析+报告（完成后自动生成 HTML 报告页面）
    python collect_and_report.py --labs imec,intel-labs --mode weekly

    # 仅采集
    python collect_and_report.py --labs imec,cea-leti --mode weekly --skip-analysis

    # 仅从已有数据生成报告（含 HTML 页面）
    python collect_and_report.py --date 2026-06-02 --report-only

    # 跳过 HTML 页面生成
    python collect_and_report.py --labs imec --no-html

    # 列出可用实验室
    python collect_and_report.py --list-labs

    # 指定 Hermes 输出格式
    python collect_and_report.py --labs imec --format json
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.hermes_bridge import HermesBridge
from rich.logging import RichHandler


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, show_path=False)],
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="全球半导体研究方向采集与洞察系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python collect_and_report.py --labs imec,intel-labs --mode weekly
  python collect_and_report.py --labs imec,cea-leti --mode weekly --skip-analysis
  python collect_and_report.py --date 2026-06-02 --report-only
  python collect_and_report.py --list-labs
  python collect_and_report.py --labs imec --format json
        """,
    )

    parser.add_argument("--labs", help="实验室 ID 列表，逗号分隔")
    parser.add_argument("--mode", choices=["daily", "weekly", "monthly", "deep"],
                        default="weekly", help="采集密度 (monthly/deep = 深度项目模式)")
    parser.add_argument("--focus", default="", help="报告重点关注方向")
    parser.add_argument("--format", choices=["json", "markdown", "both"],
                        default="both", help="报告输出格式")
    parser.add_argument("--date", help="日期 YYYY-MM-DD (用于已有数据分析)")
    parser.add_argument("--skip-analysis", action="store_true",
                        help="仅采集，跳过分析和报告")
    parser.add_argument("--report-only", action="store_true",
                        help="仅从已有数据生成报告")
    parser.add_argument("--project-mode", action="store_true",
                        help="启用深度项目采集模式 (含项目详细描述)")
    parser.add_argument("--list-labs", action="store_true",
                        help="列出可用实验室")
    parser.add_argument("--category", help="实验室类别过滤")
    parser.add_argument("--region", choices=["asia", "europe", "north_america", "other"],
                        help="区域过滤")
    parser.add_argument("--domain", help="研究方向领域过滤")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细日志")
    parser.add_argument("--hermes-output", action="store_true",
                        help="输出 Hermes 可消费的 JSON (stdout)")
    parser.add_argument("--generate-html", action="store_true",
                        help="生成 HTML 报告页面 (artifacts/{date}/reports/semiconductor-report.html)")
    parser.add_argument("--no-html", action="store_true",
                        help="跳过 HTML 报告页面生成")

    args = parser.parse_args()
    setup_logging(args.verbose)

    from src.report_page_generator import ReportPageGenerator

    bridge = HermesBridge()

    # --list-labs
    if args.list_labs:
        result = bridge.list_available_labs(
            category=args.category,
            region=args.region,
            domain=args.domain,
        )
        labs = result.get("labs", [])
        print(f"\n可用实验室 ({len(labs)}):")
        print(f"{'ID':<30} {'名称':<50} {'类别':<20} {'领域'}")
        print("-" * 130)
        for lab in labs:
            domains = ", ".join(lab.get("domains", [])[:3])
            print(f"{lab['id']:<30} {lab['name'][:48]:<50} "
                  f"{lab.get('category', ''):<20} {domains}")
        print(f"\n统计: {json.dumps(result.get('stats', {}), indent=2)}")
        return

    # --report-only
    if args.report_only:
        if not args.date:
            print("错误: --report-only 需要 --date 参数")
            sys.exit(1)
        result = bridge.generate_insight_report(
            date=args.date, format=args.format, focus=args.focus,
        )
        _print_result(result, args.hermes_output)
        _generate_html_if_needed(args, result)
        return

    # --labs is required for collection
    if not args.labs:
        parser.print_help()
        print("\n错误: 需要指定 --labs 或 --list-labs")
        sys.exit(1)

    lab_list = [l.strip() for l in args.labs.split(",")]

    if args.skip_analysis:
        # Collect only
        if args.project_mode:
            result = bridge.collect_project_details(
                labs=lab_list,
                max_projects_per_lab=5,
            )
        else:
            result = bridge.collect_research_directions(
                labs=lab_list, mode=args.mode,
            )
    else:
        # End-to-end
        if args.project_mode or args.mode in ("monthly", "deep"):
            result = bridge.collect_and_report_deep(
                labs=lab_list, mode=args.mode,
                focus=args.focus,
            )
        else:
            result = bridge.collect_and_report(
                labs=lab_list, mode=args.mode,
                focus=args.focus, format=args.format,
            )

    _print_result(result, args.hermes_output)
    _generate_html_if_needed(args, result)


def _generate_html_if_needed(args: argparse.Namespace, result: dict) -> None:
    """Generate HTML report page if requested."""
    if args.no_html:
        return
    if args.hermes_output:
        return
    if result.get("status") != "success":
        return

    date_str = result.get("date", "")
    if not date_str:
        return

    try:
        gen = ReportPageGenerator("artifacts")
        html_path = gen.generate(date_str)
        # Update index
        from pathlib import Path
        idx_path = Path("artifacts/index.html")
        idx_path.write_text(gen.generate_index_page(), encoding="utf-8")
        print(f"  📄 HTML 报告页面: {html_path}")
        print(f"  📇 报告索引: {idx_path.resolve()}")
    except Exception as exc:
        logger.warning("HTML report generation failed (non-fatal): %s", exc)


def _print_result(result: dict, hermes_output: bool = False) -> None:
    """打印结果。"""
    if hermes_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    status = result.get("status", "unknown")
    print(f"\n{'='*60}")
    print(f"  状态: {status}")
    print(f"{'='*60}")

    if status == "error":
        print(f"  错误: {result.get('error', 'unknown')}")
        return

    if "summary" in result:
        print(f"  {result['summary']}")

    if "file_paths" in result:
        fps = result["file_paths"]
        if isinstance(fps, dict):
            print("\n  文件输出:")
            for key, path in fps.items():
                if isinstance(path, list):
                    print(f"    {key}: {len(path)} files")
                else:
                    print(f"    {key}: {path}")
        elif isinstance(fps, str):
            print(f"\n  文件输出: {fps}")

    if "collection" in result:
        coll = result["collection"]
        print(f"\n  采集统计:")
        print(f"    实验室: {coll.get('labs_collected', 0)}")
        print(f"    文章数: {coll.get('total_articles', 0)}")

    if "analysis" in result:
        ana = result["analysis"]
        print(f"\n  分析统计:")
        print(f"    识别方向: {ana.get('total_trends', 0)}")
        print(f"    实验室数: {ana.get('lab_count', 0)}")

    if "report" in result:
        rep = result["report"]
        print(f"\n  报告:")
        fps = rep.get("file_paths", {})
        for fmt, path in fps.items():
            print(f"    {fmt}: {path}")

    print()


if __name__ == "__main__":
    main()
