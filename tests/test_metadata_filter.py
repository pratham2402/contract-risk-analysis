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
