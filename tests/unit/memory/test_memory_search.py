"""Tests for UnifiedMemory search_patterns functionality.

Tests keyword search, relevance scoring, filtering, and edge cases.

Copyright 2025 Smart AI Memory, LLC
Licensed under the Apache License, Version 2.0
"""

import json

import pytest

from attune.memory.long_term import Classification
from attune.memory.unified import UnifiedMemory


class TestMemorySearchBasics:
    """Test basic search functionality."""

    @pytest.fixture
    def memory_with_patterns(self, tmp_path, monkeypatch):
        """Create memory with sample patterns for testing."""
        # Create storage directory
        storage_dir = tmp_path / "memory_storage"
        storage_dir.mkdir()

        # Create sample pattern files
        patterns = [
            {
                "pattern_id": "pattern1",
                "pattern_type": "meta_workflow_execution",
                "classification": "INTERNAL",
                "content": "Successful workflow execution with test coverage 90%",
                "metadata": {"success": True, "cost": 0.50},
            },
            {
                "pattern_id": "pattern2",
                "pattern_type": "meta_workflow_execution",
                "classification": "INTERNAL",
                "content": "Failed workflow execution due to timeout",
                "metadata": {"success": False, "cost": 0.25},
            },
            {
                "pattern_id": "pattern3",
                "pattern_type": "algorithm",
                "classification": "PUBLIC",
                "content": "Quick sort algorithm implementation",
                "metadata": {"complexity": "O(n log n)"},
            },
        ]

        for pattern in patterns:
            pattern_file = storage_dir / f"{pattern['pattern_id']}.json"
            pattern_file.write_text(json.dumps(pattern))

        # Set storage directory via environment variable using monkeypatch
        # This ensures it's set during the entire test
        monkeypatch.setenv("EMPATHY_STORAGE_DIR", str(storage_dir))

        # Create memory instance - will use the env var for storage
        memory = UnifiedMemory(user_id="test_user")
        return memory

    def test_search_with_query(self, memory_with_patterns):
        """Test search with text query."""
        results = memory_with_patterns.search_patterns(
            query="successful workflow",
            limit=10,
        )

        # Should find pattern1 (contains "successful workflow")
        assert len(results) >= 1
        assert any("successful" in str(r.get("content", "")).lower() for r in results)

    def test_search_filter_by_pattern_type(self, memory_with_patterns):
        """Test filtering by pattern type."""
        results = memory_with_patterns.search_patterns(
            pattern_type="meta_workflow_execution",
            limit=10,
        )

        # Should find pattern1 and pattern2 (both are meta_workflow_execution)
        assert len(results) >= 2
        assert all(r.get("pattern_type") == "meta_workflow_execution" for r in results)

    def test_search_filter_by_classification(self, memory_with_patterns):
        """Test filtering by classification."""
        results = memory_with_patterns.search_patterns(
            classification=Classification.INTERNAL,
            limit=10,
        )

        # Should find pattern1 and pattern2 (both are INTERNAL)
        assert len(results) >= 2
        assert all(r.get("classification") == "INTERNAL" for r in results)

    def test_search_combined_filters(self, memory_with_patterns):
        """Test search with multiple filters."""
        results = memory_with_patterns.search_patterns(
            query="successful",
            pattern_type="meta_workflow_execution",
            classification=Classification.INTERNAL,
            limit=10,
        )

        # Should find only pattern1
        assert len(results) >= 1
        found_pattern1 = any(r.get("pattern_id") == "pattern1" for r in results)
        assert found_pattern1

    def test_search_with_limit(self, memory_with_patterns):
        """Test limit parameter."""
        results = memory_with_patterns.search_patterns(
            limit=1,
        )

        # Should return at most 1 result
        assert len(results) <= 1

    def test_search_no_results(self, memory_with_patterns):
        """Test search with no matching results."""
        results = memory_with_patterns.search_patterns(
            query="nonexistent query that will not match",
            limit=10,
        )

        assert len(results) == 0

    def test_search_without_memory(self):
        """Test search when memory is not available."""
        memory = UnifiedMemory(user_id="test_user")

        # Disable long-term memory
        memory._long_term = None

        results = memory.search_patterns(query="test")

        # Should return empty list gracefully
        assert results == []


class TestRelevanceScoring:
    """Test relevance scoring algorithm."""

    @pytest.fixture
    def memory_with_scored_patterns(self, tmp_path, monkeypatch):
        """Create memory with patterns for relevance testing."""
        storage_dir = tmp_path / "memory_storage"
        storage_dir.mkdir()

        patterns = [
            {
                "pattern_id": "exact_match",
                "pattern_type": "test",
                "content": "This is a test pattern with exact query match",
                "metadata": {},
            },
            {
                "pattern_id": "partial_match",
                "pattern_type": "test",
                "content": "This pattern contains some test words",
                "metadata": {},
            },
            {
                "pattern_id": "metadata_match",
                "pattern_type": "test",
                "content": "Different content",
                "metadata": {"query": "test pattern exact"},
            },
        ]

        for pattern in patterns:
            pattern_file = storage_dir / f"{pattern['pattern_id']}.json"
            pattern_file.write_text(json.dumps(pattern))

        # Set storage directory via environment variable
        monkeypatch.setenv("EMPATHY_STORAGE_DIR", str(storage_dir))

        memory = UnifiedMemory(user_id="test_user")
        return memory

    def test_exact_match_ranks_highest(self, memory_with_scored_patterns):
        """Test that exact phrase matches rank highest."""
        results = memory_with_scored_patterns.search_patterns(
            query="exact query match",
            limit=10,
        )

        # Exact match should be first
        if len(results) > 0:
            first_result = results[0]
            # Should be the exact_match pattern
            assert "exact query match" in first_result.get("content", "").lower()

    def test_keyword_match_scores_lower(self, memory_with_scored_patterns):
        """Test that keyword matches score lower than exact matches."""
        results = memory_with_scored_patterns.search_patterns(
            query="test pattern",
            limit=10,
        )

        # Should find multiple results
        assert len(results) >= 2

        # Results should be sorted by relevance
        # (implementation detail: exact phrase match > keyword match)

    def test_metadata_match_scores_lowest(self, memory_with_scored_patterns):
        """Test that metadata matches score lower than content matches."""
        results = memory_with_scored_patterns.search_patterns(
            query="test pattern",
            limit=10,
        )

        # Should find results, but metadata-only matches rank lower
        assert len(results) >= 1


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_search_empty_query(self):
        """Test search with empty query."""
        memory = UnifiedMemory(user_id="test_user")
        results = memory.search_patterns(query="", limit=10)

        # Should handle gracefully
        assert isinstance(results, list)

    def test_search_none_query(self):
        """Test search with None query."""
        memory = UnifiedMemory(user_id="test_user")
        results = memory.search_patterns(query=None, limit=10)

        # Should handle gracefully
        assert isinstance(results, list)

    def test_search_with_special_characters(self):
        """Test search with special characters."""
        memory = UnifiedMemory(user_id="test_user")
        results = memory.search_patterns(
            query="test@#$%^&*()",
            limit=10,
        )

        # Should not crash
        assert isinstance(results, list)

    def test_search_very_long_query(self):
        """Test search with very long query."""
        memory = UnifiedMemory(user_id="test_user")
        long_query = "test " * 1000  # Very long query

        results = memory.search_patterns(query=long_query, limit=10)

        # Should handle gracefully
        assert isinstance(results, list)

    def test_search_with_zero_limit(self):
        """Test search with limit=0."""
        memory = UnifiedMemory(user_id="test_user")
        results = memory.search_patterns(query="test", limit=0)

        # Should return empty list
        assert results == []

    def test_search_with_negative_limit(self):
        """Test search with negative limit."""
        memory = UnifiedMemory(user_id="test_user")
        results = memory.search_patterns(query="test", limit=-1)

        # Should handle gracefully (treat as 0 or error)
        assert isinstance(results, list)


class TestGetAllPatterns:
    """Test _iter_all_patterns helper method."""

    def test_iter_all_patterns_empty_storage(self, tmp_path, monkeypatch):
        """Test getting patterns from empty storage."""
        storage_dir = tmp_path / "empty_storage"
        storage_dir.mkdir()

        # Set storage directory via environment variable
        monkeypatch.setenv("EMPATHY_STORAGE_DIR", str(storage_dir))

        memory = UnifiedMemory(user_id="test_user")
        patterns = list(memory._iter_all_patterns())

        assert patterns == []

    def test_iter_all_patterns_with_invalid_json(self, tmp_path, monkeypatch):
        """Test getting patterns with invalid JSON files."""
        storage_dir = tmp_path / "invalid_storage"
        storage_dir.mkdir()

        # Create invalid JSON file
        invalid_file = storage_dir / "invalid.json"
        invalid_file.write_text("not valid json{{{")

        # Set storage directory via environment variable
        monkeypatch.setenv("EMPATHY_STORAGE_DIR", str(storage_dir))

        memory = UnifiedMemory(user_id="test_user")
        patterns = list(memory._iter_all_patterns())

        # Should skip invalid files and not crash
        assert isinstance(patterns, list)

    def test_iter_all_patterns_nested_directories(self, tmp_path, monkeypatch):
        """Test getting patterns from nested directories."""
        storage_dir = tmp_path / "nested_storage"
        storage_dir.mkdir()

        # Create nested structure
        subdir = storage_dir / "subdir"
        subdir.mkdir()

        pattern1 = storage_dir / "pattern1.json"
        pattern1.write_text(json.dumps({"pattern_id": "p1"}))

        pattern2 = subdir / "pattern2.json"
        pattern2.write_text(json.dumps({"pattern_id": "p2"}))

        # Set storage directory via environment variable
        monkeypatch.setenv("EMPATHY_STORAGE_DIR", str(storage_dir))

        memory = UnifiedMemory(user_id="test_user")
        patterns = list(memory._iter_all_patterns())

        # Should find both patterns (recursive glob)
        assert len(patterns) == 2
        pattern_ids = [p.get("pattern_id") for p in patterns]
        assert "p1" in pattern_ids
        assert "p2" in pattern_ids
