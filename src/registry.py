"""Lab registry loader — manages the 100+ source lab registry."""

from __future__ import annotations

from pathlib import Path
from typing import Any


class LabRegistry:
    """加载、查询和过滤实验室注册表。"""

    def __init__(self, registry_path: str | Path | None = None) -> None:
        self.path = Path(registry_path) if registry_path else None
        self._raw: dict[str, Any] = {}
        self._flat: list[dict[str, Any]] = []
        self._loaded = False

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def load(self, registry_path: str | Path | None = None) -> LabRegistry:
        """从 YAML 文件加载注册表。"""
        import yaml

        path = registry_path or self.path
        if not path:
            from src.config import LAB_REGISTRY_PATH

            path = LAB_REGISTRY_PATH

        with open(path, encoding="utf-8") as f:
            self._raw = yaml.safe_load(f) or {}

        self._flatten()
        self._loaded = True
        return self

    def _flatten(self) -> None:
        """将嵌套 YAML 结构展平为统一的实验室列表。"""
        flat: list[dict[str, Any]] = []
        # YAML top keys: version, total_sources, tier1..tier6
        for tier_key in [f"tier{i}" for i in range(1, 7)]:
            tier_data = self._raw.get(tier_key, {})
            # tier_data can be a dict (categories → labs) or a list (flat labs)
            if isinstance(tier_data, dict):
                for category, entries in tier_data.items():
                    if isinstance(entries, dict):
                        for lab_id, lab_info in entries.items():
                            if isinstance(lab_info, dict):
                                lab_info["id"] = lab_id
                                lab_info["tier"] = int(tier_key[-1])
                                lab_info["category"] = category
                                if "labs" in lab_info:
                                    labs_subs = lab_info.pop("labs")
                                    for sub in labs_subs:
                                        sub_entry = dict(lab_info)
                                        sub_entry.update(sub)
                                        sub_entry["id"] = sub["id"]
                                        sub_entry["parent"] = lab_id
                                        flat.append(sub_entry)
                                flat.append(lab_info)
                    elif isinstance(entries, list):
                        for item in entries:
                            if isinstance(item, dict) and "id" in item:
                                item.setdefault("tier", int(tier_key[-1]))
                                item.setdefault("category", category)
                                flat.append(item)
            elif isinstance(tier_data, list):
                for item in tier_data:
                    if isinstance(item, dict) and "id" in item:
                        item.setdefault("tier", int(tier_key[-1]))
                        item.setdefault("category", "general")
                        flat.append(item)

        self._flat = flat

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    @property
    def labs(self) -> list[dict[str, Any]]:
        if not self._loaded:
            self.load()
        return self._flat

    def find(
        self,
        category: str | None = None,
        region: str | None = None,
        domain: str | None = None,
        tier: int | None = None,
        lab_ids: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """按各种条件过滤实验室。"""
        results = self.labs

        if category:
            results = [r for r in results if r.get("category") == category]
        if region:
            results = [r for r in results if r.get("region") == region]
        if domain:
            results = [
                r
                for r in results
                if domain in r.get("domains", [])
            ]
        if tier:
            results = [r for r in results if r.get("tier") == tier]
        if lab_ids:
            results = [r for r in results if r.get("id") in lab_ids]

        return results

    def get(self, lab_id: str) -> dict[str, Any] | None:
        """通过 ID 查找单个实验室。"""
        for lab in self.labs:
            if lab.get("id") == lab_id:
                return lab
            if lab.get("parent") == lab_id:
                return lab
        return None

    def resolve_ids(self, lab_ids: list[str]) -> list[dict[str, Any]]:
        """解析实验室ID列表，返回完整信息，自动处理父子关系。"""
        resolved = {}
        for lid in lab_ids:
            lab = self.get(lid)
            if lab:
                # If this is a parent with sub-labs, include sub-labs too
                children = [l for l in self.labs if l.get("parent") == lid]
                if children:
                    for child in children:
                        resolved[child["id"]] = child
                resolved[lab["id"]] = lab
        return list(resolved.values())

    def stats(self) -> dict[str, Any]:
        """注册表统计信息。"""
        labs_all = self.labs
        return {
            "total": len(labs_all),
            "by_tier": {
                str(t): len([l for l in labs_all if l.get("tier") == t])
                for t in range(1, 7)
            },
            "by_category": {
                cat: len([l for l in labs_all if l.get("category") == cat])
                for cat in set(l.get("category", "") for l in labs_all)
            },
            "by_region": {
                reg: len([l for l in labs_all if l.get("region") == reg])
                for reg in set(l.get("region", "") for l in labs_all if l.get("region"))
            },
            "by_domain": {
                dom: len([l for l in labs_all if dom in l.get("domains", [])])
                for dom in sorted(
                    set(d for l in labs_all for d in l.get("domains", []))
                )
            },
        }

    def as_json(self) -> dict:
        """返回可在 Hermes 工具间传递的 JSON 表示。"""
        return {
            "version": self._raw.get("version", ""),
            "total_sources": self._raw.get("total_sources", 0),
            "stats": self.stats(),
        }
