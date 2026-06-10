#!/usr/bin/env python3
"""
半导体研究报告网站 — 本地服务器

启动一个简单的 HTTP 服务器，在浏览器中查看所有生成的 HTML 报告页面。

Usage:
    python scripts/serve_reports.py          # 默认端口 8080
    python scripts/serve_reports.py --port 3000
    python scripts/serve_reports.py --open    # 自动打开浏览器
"""

from __future__ import annotations

import argparse
import http.server
import logging
import os
import socket
import sys
import webbrowser
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

PORT = 8080

# Ensure artifacts/index.html exists
def ensure_index() -> str:
    """Generate index.html in CWD if missing."""
    idx = Path("index.html")
    if not idx.exists():
        logger.info("Index page missing, generating now...")
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
            from src.report_page_generator import ReportPageGenerator

            gen = ReportPageGenerator(".")
            idx.write_text(gen.generate_index_page(), encoding="utf-8")
            logger.info("Index page generated.")
        except Exception as exc:
            logger.warning("Could not generate index: %s", exc)
    return str(idx.resolve())


def find_free_port(start: int = PORT) -> int:
    """Find an available port starting from `start`."""
    port = start
    while port < start + 100:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
            port += 1
    return start  # fallback


def main() -> None:
    parser = argparse.ArgumentParser(description="Semiconductor Reports Server")
    parser.add_argument("--port", type=int, default=PORT, help=f"Port (default: {PORT})")
    parser.add_argument("--open", "-o", action="store_true", help="Open browser automatically")
    parser.add_argument(
        "--dir", "-d", default="artifacts",
        help="Directory to serve (default: artifacts)",
    )
    args = parser.parse_args()

    serve_dir = Path(args.dir).resolve()
    if not serve_dir.exists():
        logger.error("Directory not found: %s", serve_dir)
        sys.exit(1)

    # Ensure index page exists in the serve directory
    os.chdir(str(serve_dir))
    ensure_index()

    port = find_free_port(args.port)
    url = f"http://127.0.0.1:{port}/"

    handler = http.server.SimpleHTTPRequestHandler

    logger.info("")
    logger.info("╔══════════════════════════════════════════════╗")
    logger.info("║  半导体研究报告 — 本地服务器")
    logger.info(f"║")
    logger.info(f"║  📂 Serving: {serve_dir}")
    logger.info(f"║  🌐 URL:     {url}")
    logger.info("║")
    logger.info(f"║  📋 报告列表: {url}")
    logger.info("║")
    logger.info("║  Press Ctrl+C to stop")
    logger.info("╚══════════════════════════════════════════════╝")
    logger.info("")

    if args.open:
        webbrowser.open(url)

    try:
        server = http.server.HTTPServer(("127.0.0.1", port), handler)
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("\nServer stopped.")
        server.server_close()


if __name__ == "__main__":
    main()
