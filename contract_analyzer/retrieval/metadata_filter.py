"""Metadata-aware filtering for standards retrieval.

Provides post-retrieval metadata filtering on jurisdiction,
standard category, and authority level.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class RetrievalFilters:
    """Filters applied to standards retrieval queries."""

    jurisdiction: str | None = None
    standard_category: str | None = None
    authority_level: str | None = None

    def matches(self, entry: dict[str, Any]) -> bool:
        """Check whether a retrieved entry matches all active filters."""
        if self.jurisdiction:
            entry_jur = entry.get("jurisdiction", "Global")
            if entry_jur != "Global" and entry_jur != self.jurisdiction:
                return False
        if self.standard_category:
            if entry.get("standard_category") != self.standard_category:
                return False
        if self.authority_level:
            if entry.get("authority_level") != self.authority_level:
                return False
        return True

    def describe(self) -> str:
        parts = []
        if self.jurisdiction:
            parts.append(f"jurisdiction={self.jurisdiction}")
        if self.standard_category:
            parts.append(f"category={self.standard_category}")
        if self.authority_level:
            parts.append(f"authority={self.authority_level}")
        return ", ".join(parts) if parts else "no filters active"
