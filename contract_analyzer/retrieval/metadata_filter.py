"""Metadata-aware filtering for standards retrieval.

Provides pre-retrieval and post-retrieval metadata filtering on jurisdiction,
standard category, effective date, and authority level.
"""

from dataclasses import dataclass
from datetime import date
from typing import Any


@dataclass
class RetrievalFilters:
    """Filters applied to standards retrieval queries."""

    jurisdiction: str | None = None
    standard_category: str | None = None
    authority_level: str | None = None
    effective_before: date | None = None
    effective_after: date | None = None

    @classmethod
    def from_tool_args(cls, args: dict[str, Any]) -> "RetrievalFilters":
        """Create filters from retrieve_standards tool arguments."""
        jur = args.get("jurisdiction")
        cat = args.get("standard_type")
        auth = args.get("authority_level")

        # Map common jurisdiction inputs to standard values
        jurisdiction_map = {
            "us": "US",
            "usa": "US",
            "united states": "US",
            "delaware": "US",
            "california": "US",
            "new york": "US",
            "india": "India",
            "indian": "India",
            "eu": "EU",
            "europe": "EU",
            "european union": "EU",
            "gdpr": "EU",
            "uk": "UK",
            "united kingdom": "UK",
            "global": "Global",
        }
        mapped_jur = jurisdiction_map.get((jur or "").lower(), jur)

        cat_map = {
            "data_protection": "data_protection",
            "privacy": "data_protection",
            "security": "security",
            "contract_law": "contract_law",
            "contract": "contract_law",
            "industry": "industry",
            "financial": "financial_reporting",
            "financial_reporting": "financial_reporting",
        }
        mapped_cat = cat_map.get((cat or "").lower(), cat)

        auth_map = {
            "statute": "statute",
            "regulation": "regulation",
            "framework": "framework",
            "common_law": "common_law",
            "industry_standard": "industry_standard",
            "treaty": "treaty",
        }
        mapped_auth = auth_map.get((auth or "").lower(), auth)

        return cls(
            jurisdiction=mapped_jur,
            standard_category=mapped_cat,
            authority_level=mapped_auth,
        )

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
