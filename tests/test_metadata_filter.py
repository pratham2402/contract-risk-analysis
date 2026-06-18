"""Tests for RetrievalFilters metadata filtering."""

import pytest

from contract_analyzer.retrieval.metadata_filter import RetrievalFilters


class TestRetrievalFiltersCreation:
    def test_empty(self):
        f = RetrievalFilters()
        assert f.jurisdiction is None
        assert f.standard_category is None
        assert f.authority_level is None

    def test_all_set(self):
        f = RetrievalFilters(
            jurisdiction="US",
            standard_category="data_protection",
            authority_level="regulation",
        )
        assert f.jurisdiction == "US"
        assert f.standard_category == "data_protection"
        assert f.authority_level == "regulation"


class TestRetrievalFiltersDescribe:
    def test_no_filters(self):
        assert RetrievalFilters().describe() == "no filters active"

    def test_jurisdiction_only(self):
        assert RetrievalFilters(jurisdiction="US").describe() == "jurisdiction=US"

    def test_all_filters(self):
        f = RetrievalFilters(
            jurisdiction="India",
            standard_category="contract_law",
            authority_level="statute",
        )
        desc = f.describe()
        assert "jurisdiction=India" in desc
        assert "category=contract_law" in desc
        assert "authority=statute" in desc


class TestRetrievalFiltersMatching:
    def test_matches_when_no_filters(self):
        f = RetrievalFilters()
        assert f.matches({"jurisdiction": "US", "standard_category": "any"})

    def test_matches_jurisdiction_exact(self):
        f = RetrievalFilters(jurisdiction="US")
        assert f.matches({"jurisdiction": "US"})
        assert not f.matches({"jurisdiction": "India"})

    def test_matches_jurisdiction_global_passthrough(self):
        """Global entries should pass through jurisdiction filters."""
        f = RetrievalFilters(jurisdiction="US")
        assert f.matches({"jurisdiction": "Global"})

    def test_matches_category(self):
        f = RetrievalFilters(standard_category="data_protection")
        assert f.matches({"standard_category": "data_protection"})
        assert not f.matches({"standard_category": "security"})

    def test_matches_authority(self):
        f = RetrievalFilters(authority_level="statute")
        assert f.matches({"authority_level": "statute"})
        assert not f.matches({"authority_level": "regulation"})

    def test_matches_combined(self):
        f = RetrievalFilters(
            jurisdiction="US",
            standard_category="data_protection",
            authority_level="regulation",
        )
        # All match
        assert f.matches({
            "jurisdiction": "US",
            "standard_category": "data_protection",
            "authority_level": "regulation",
        })
        # Global jurisdiction passes
        assert f.matches({
            "jurisdiction": "Global",
            "standard_category": "data_protection",
            "authority_level": "regulation",
        })
        # Category mismatch
        assert not f.matches({
            "jurisdiction": "US",
            "standard_category": "security",
            "authority_level": "regulation",
        })
        # Authority mismatch
        assert not f.matches({
            "jurisdiction": "US",
            "standard_category": "data_protection",
            "authority_level": "framework",
        })


class TestFromToolArgs:
    def test_empty_args(self):
        f = RetrievalFilters.from_tool_args({})
        assert f.jurisdiction is None
        assert f.standard_category is None
        assert f.authority_level is None

    def test_jurisdiction_mapping(self):
        cases = [
            ("us", "US"),
            ("usa", "US"),
            ("united states", "US"),
            ("delaware", "US"),
            ("california", "US"),
            ("new york", "US"),
            ("india", "India"),
            ("indian", "India"),
            ("eu", "EU"),
            ("europe", "EU"),
            ("european union", "EU"),
            ("gdpr", "EU"),
            ("uk", "UK"),
            ("united kingdom", "UK"),
            ("global", "Global"),
        ]
        for input_val, expected in cases:
            f = RetrievalFilters.from_tool_args({"jurisdiction": input_val})
            assert f.jurisdiction == expected, f"Failed for {input_val}"

    def test_jurisdiction_unknown_passthrough(self):
        f = RetrievalFilters.from_tool_args({"jurisdiction": "brazil"})
        assert f.jurisdiction == "brazil"

    def test_category_mapping(self):
        cases = [
            ("data_protection", "data_protection"),
            ("privacy", "data_protection"),
            ("security", "security"),
            ("contract_law", "contract_law"),
            ("contract", "contract_law"),
            ("industry", "industry"),
            ("financial", "financial_reporting"),
            ("financial_reporting", "financial_reporting"),
        ]
        for input_val, expected in cases:
            f = RetrievalFilters.from_tool_args({"standard_type": input_val})
            assert f.standard_category == expected, f"Failed for {input_val}"

    def test_authority_mapping(self):
        cases = [
            ("statute", "statute"),
            ("regulation", "regulation"),
            ("framework", "framework"),
            ("common_law", "common_law"),
            ("industry_standard", "industry_standard"),
            ("treaty", "treaty"),
        ]
        for input_val, expected in cases:
            f = RetrievalFilters.from_tool_args({"authority_level": input_val})
            assert f.authority_level == expected, f"Failed for {input_val}"

    def test_combined_args(self):
        f = RetrievalFilters.from_tool_args({
            "jurisdiction": "california",
            "standard_type": "privacy",
            "authority_level": "regulation",
        })
        assert f.jurisdiction == "US"
        assert f.standard_category == "data_protection"
        assert f.authority_level == "regulation"
