"""Global configuration for semi-research-direction-collect."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

# Project root (auto-detect from file location)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# --- Directories ---
DATA_DIR = PROJECT_ROOT / "data"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
HERMES_DIR = PROJECT_ROOT / "hermes"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# --- Files ---
LAB_REGISTRY_PATH = DATA_DIR / "lab_registry.yaml"
COLLECTION_CONFIG_PATH = DATA_DIR / "collection_config.yaml"
HERMES_TOOLS_PATH = HERMES_DIR / "tools.json"
HERMES_AGENT_CONFIG_PATH = HERMES_DIR / "agent_config.yaml"

# --- Defaults ---
DEFAULT_TIMEOUT_SEC = 60
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)
DEFAULT_LAB_CATEGORIES: list[str] = field(default_factory=lambda: [
    "university_lab",
    "research_institute",
    "corporate_rd",
    "consortium",
    "government_lab",
])

ResearchStage = Literal["emerging", "growing", "mature", "declining"]
CollectionMode = Literal["daily", "weekly", "monthly", "deep"]
ReportFormat = Literal["json", "markdown", "both"]


@dataclass
class Settings:
    """Application settings — can be overridden via env vars."""

    # HTTP
    http_timeout: int = int(os.getenv("SEMI_HTTP_TIMEOUT", str(DEFAULT_TIMEOUT_SEC)))
    http_delay: float = float(os.getenv("SEMI_HTTP_DELAY", "1.0"))
    user_agent: str = os.getenv("SEMI_USER_AGENT", DEFAULT_USER_AGENT)
    max_retries: int = int(os.getenv("SEMI_MAX_RETRIES", "3"))

    # Collection
    max_articles_per_lab: int = int(os.getenv("SEMI_MAX_ARTICLES_PER_LAB", "10"))
    max_labs_per_run: int = int(os.getenv("SEMI_MAX_LABS_PER_RUN", "50"))
    default_mode: CollectionMode = os.getenv("SEMI_DEFAULT_MODE", "weekly")  # type: ignore[assignment]

    # Output
    report_format: ReportFormat = os.getenv("SEMI_REPORT_FORMAT", "both")  # type: ignore[assignment]
    compress_artifacts: bool = os.getenv("SEMI_COMPRESS", "false").lower() == "true"

    def lab_registry(self) -> dict:
        """Load and return the full lab registry."""
        import yaml
        with open(LAB_REGISTRY_PATH, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}


# Singleton
settings = Settings()
