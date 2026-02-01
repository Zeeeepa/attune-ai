"""Tests for project_index models module.

Covers FileCategory, TestRequirement, FileRecord, ProjectSummary, IndexConfig.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from datetime import datetime

import pytest

from attune.project_index.models import (
    FileCategory,
    FileRecord,
    IndexConfig,
    ProjectSummary,
    TestRequirement,
)


@pytest.mark.unit
class TestFileCategory:
    """Tests for FileCategory enum."""

    def test_all_categories_exist(self):
        """Test all expected categories exist."""
        assert FileCategory.SOURCE == "source"
        assert FileCategory.TEST == "test"
        assert FileCategory.CONFIG == "config"
        assert FileCategory.DOCS == "docs"
        assert FileCategory.ASSET == "asset"
        assert FileCategory.GENERATED == "generated"
        assert FileCategory.BUILD == "build"
        assert FileCategory.UNKNOWN == "unknown"

    def test_category_values(self):
        """Test category values are lowercase strings."""
        for cat in FileCategory:
            assert cat.value == cat.value.lower()
            assert isinstance(cat.value, str)

    def test_category_from_string(self):
        """Test creating category from string."""
        assert FileCategory("source") == FileCategory.SOURCE
        assert FileCategory("test") == FileCategory.TEST
        assert FileCategory("unknown") == FileCategory.UNKNOWN


@pytest.mark.unit
class TestTestRequirement:
    """Tests for TestRequirement enum."""

    def test_all_requirements_exist(self):
        """Test all expected requirements exist."""
        assert TestRequirement.REQUIRED == "required"
        assert TestRequirement.OPTIONAL == "optional"
        assert TestRequirement.NOT_APPLICABLE == "not_applicable"
        assert TestRequirement.EXCLUDED == "excluded"

    def test_requirement_from_string(self):
        """Test creating requirement from string."""
        assert TestRequirement("required") == TestRequirement.REQUIRED
        assert TestRequirement("optional") == TestRequirement.OPTIONAL


@pytest.mark.unit
class TestFileRecord:
    """Tests for FileRecord dataclass."""

    def test_basic_creation(self):
        """Test creating a basic FileRecord."""
        record = FileRecord(
            path="src/module.py",
            name="module.py",
        )

        assert record.path == "src/module.py"
        assert record.name == "module.py"
        assert record.category == FileCategory.UNKNOWN
        assert record.language == ""
        assert record.test_requirement == TestRequirement.REQUIRED
        assert record.tests_exist is False

    def test_full_creation(self):
        """Test creating a FileRecord with all fields."""
        now = datetime.now()
        record = FileRecord(
            path="src/attune/core.py",
            name="core.py",
            category=FileCategory.SOURCE,
            language="python",
            test_requirement=TestRequirement.REQUIRED,
            test_file_path="tests/unit/test_core.py",
            tests_exist=True,
            test_count=15,
            coverage_percent=85.5,
            last_modified=now,
            tests_last_modified=now,
            last_indexed=now,
            staleness_days=0,
            is_stale=False,
            lines_of_code=250,
            lines_of_test=400,
            complexity_score=3.5,
            has_docstrings=True,
            has_type_hints=True,
            lint_issues=0,
            imports=["os", "sys"],
            imported_by=["src/cli.py"],
            import_count=2,
            imported_by_count=1,
            impact_score=7.5,
            metadata={"custom": "data"},
            needs_attention=False,
            attention_reasons=[],
        )

        assert record.category == FileCategory.SOURCE
        assert record.tests_exist is True
        assert record.coverage_percent == 85.5
        assert record.impact_score == 7.5
        assert len(record.imports) == 2

    def test_to_dict(self):
        """Test FileRecord serialization."""
        now = datetime(2025, 1, 15, 10, 30, 0)
        record = FileRecord(
            path="src/module.py",
            name="module.py",
            category=FileCategory.SOURCE,
            language="python",
            last_modified=now,
            lines_of_code=100,
            impact_score=5.0,
            imports=["os"],
        )

        data = record.to_dict()

        assert data["path"] == "src/module.py"
        assert data["category"] == "source"
        assert data["last_modified"] == "2025-01-15T10:30:00"
        assert data["lines_of_code"] == 100
        assert data["imports"] == ["os"]

    def test_from_dict(self):
        """Test FileRecord deserialization."""
        data = {
            "path": "src/core.py",
            "name": "core.py",
            "category": "source",
            "language": "python",
            "test_requirement": "required",
            "tests_exist": True,
            "test_count": 10,
            "coverage_percent": 75.0,
            "last_modified": "2025-01-15T10:30:00",
            "lines_of_code": 200,
            "impact_score": 6.0,
            "imports": ["typing", "dataclasses"],
            "imported_by": [],
        }

        record = FileRecord.from_dict(data)

        assert record.path == "src/core.py"
        assert record.category == FileCategory.SOURCE
        assert record.test_requirement == TestRequirement.REQUIRED
        assert record.tests_exist is True
        assert record.coverage_percent == 75.0
        assert record.last_modified == datetime(2025, 1, 15, 10, 30, 0)
        assert len(record.imports) == 2

    def test_from_dict_defaults(self):
        """Test FileRecord from_dict with minimal data."""
        data = {"path": "test.py", "name": "test.py"}

        record = FileRecord.from_dict(data)

        assert record.path == "test.py"
        assert record.category == FileCategory.UNKNOWN
        assert record.tests_exist is False
        assert record.imports == []

    def test_roundtrip(self):
        """Test FileRecord serialization roundtrip."""
        now = datetime(2025, 1, 15, 12, 0, 0)
        original = FileRecord(
            path="src/test.py",
            name="test.py",
            category=FileCategory.SOURCE,
            last_modified=now,
            lines_of_code=50,
            imports=["abc", "def"],
            metadata={"key": "value"},
        )

        data = original.to_dict()
        restored = FileRecord.from_dict(data)

        assert restored.path == original.path
        assert restored.category == original.category
        assert restored.last_modified == original.last_modified
        assert restored.imports == original.imports
        assert restored.metadata == original.metadata


@pytest.mark.unit
class TestProjectSummary:
    """Tests for ProjectSummary dataclass."""

    def test_default_creation(self):
        """Test creating ProjectSummary with defaults."""
        summary = ProjectSummary()

        assert summary.total_files == 0
        assert summary.source_files == 0
        assert summary.test_files == 0
        assert summary.test_coverage_avg == 0.0
        assert summary.stale_file_count == 0
        assert summary.most_stale_files == []
        assert summary.critical_untested_files == []

    def test_full_creation(self):
        """Test creating ProjectSummary with all fields."""
        summary = ProjectSummary(
            total_files=100,
            source_files=60,
            test_files=30,
            config_files=5,
            doc_files=5,
            files_requiring_tests=60,
            files_with_tests=45,
            files_without_tests=15,
            test_coverage_avg=75.5,
            total_test_count=500,
            stale_file_count=5,
            avg_staleness_days=3.5,
            most_stale_files=["old1.py", "old2.py"],
            total_lines_of_code=10000,
            total_lines_of_test=8000,
            test_to_code_ratio=0.8,
            avg_complexity=2.5,
            files_with_docstrings_pct=80.0,
            files_with_type_hints_pct=90.0,
            total_lint_issues=12,
            high_impact_files=["core.py", "api.py"],
            critical_untested_files=["critical.py"],
            files_needing_attention=10,
            top_attention_files=["fix_me.py"],
        )

        assert summary.total_files == 100
        assert summary.test_coverage_avg == 75.5
        assert len(summary.most_stale_files) == 2
        assert summary.test_to_code_ratio == 0.8

    def test_to_dict(self):
        """Test ProjectSummary serialization."""
        summary = ProjectSummary(
            total_files=50,
            source_files=30,
            test_coverage_avg=80.0,
            critical_untested_files=["a.py", "b.py"],
        )

        data = summary.to_dict()

        assert data["total_files"] == 50
        assert data["source_files"] == 30
        assert data["test_coverage_avg"] == 80.0
        assert data["critical_untested_files"] == ["a.py", "b.py"]

    def test_from_dict(self):
        """Test ProjectSummary deserialization."""
        data = {
            "total_files": 100,
            "source_files": 60,
            "test_files": 30,
            "test_coverage_avg": 75.0,
            "stale_file_count": 5,
            "most_stale_files": ["stale.py"],
        }

        summary = ProjectSummary.from_dict(data)

        assert summary.total_files == 100
        assert summary.test_coverage_avg == 75.0
        assert summary.most_stale_files == ["stale.py"]

    def test_from_dict_defaults(self):
        """Test ProjectSummary from_dict with minimal data."""
        data = {}

        summary = ProjectSummary.from_dict(data)

        assert summary.total_files == 0
        assert summary.test_coverage_avg == 0.0
        assert summary.most_stale_files == []

    def test_roundtrip(self):
        """Test ProjectSummary serialization roundtrip."""
        original = ProjectSummary(
            total_files=80,
            source_files=50,
            test_coverage_avg=65.0,
            high_impact_files=["important.py"],
        )

        data = original.to_dict()
        restored = ProjectSummary.from_dict(data)

        assert restored.total_files == original.total_files
        assert restored.test_coverage_avg == original.test_coverage_avg
        assert restored.high_impact_files == original.high_impact_files


@pytest.mark.unit
class TestIndexConfig:
    """Tests for IndexConfig dataclass."""

    def test_default_creation(self):
        """Test creating IndexConfig with defaults."""
        config = IndexConfig()

        assert len(config.exclude_patterns) > 0
        assert "**/__pycache__/**" in config.exclude_patterns
        assert len(config.no_test_patterns) > 0
        assert "**/__init__.py" in config.no_test_patterns
        assert config.staleness_threshold_days == 7
        assert config.low_coverage_threshold == 50.0
        assert config.high_impact_threshold == 5.0
        assert config.test_dir == "tests"
        assert config.use_redis is False

    def test_custom_creation(self):
        """Test creating IndexConfig with custom values."""
        config = IndexConfig(
            exclude_patterns=["**/*.log"],
            no_test_patterns=["**/__init__.py"],
            staleness_threshold_days=14,
            low_coverage_threshold=60.0,
            high_impact_threshold=10.0,
            source_dirs=["src", "lib"],
            test_dir="test",
            use_redis=True,
            redis_key_prefix="myapp:index",
        )

        assert config.exclude_patterns == ["**/*.log"]
        assert config.staleness_threshold_days == 14
        assert config.use_redis is True
        assert config.redis_key_prefix == "myapp:index"

    def test_default_exclude_patterns(self):
        """Test default exclude patterns include common patterns."""
        config = IndexConfig()

        expected_patterns = [
            "**/__pycache__/**",
            "**/*.pyc",
            "**/.git/**",
            "**/.venv/**",
            "**/node_modules/**",
            "**/dist/**",
        ]

        for pattern in expected_patterns:
            assert pattern in config.exclude_patterns

    def test_default_no_test_patterns(self):
        """Test default no_test patterns include common patterns."""
        config = IndexConfig()

        expected_patterns = [
            "**/__init__.py",
            "**/*.yml",
            "**/*.md",
            "**/test_*.py",
        ]

        for pattern in expected_patterns:
            assert pattern in config.no_test_patterns

    def test_to_dict(self):
        """Test IndexConfig serialization."""
        config = IndexConfig(
            staleness_threshold_days=10,
            use_redis=True,
        )

        data = config.to_dict()

        assert data["staleness_threshold_days"] == 10
        assert data["use_redis"] is True
        assert "exclude_patterns" in data
        assert "no_test_patterns" in data

    def test_from_dict(self):
        """Test IndexConfig deserialization."""
        data = {
            "staleness_threshold_days": 14,
            "low_coverage_threshold": 70.0,
            "use_redis": True,
            "redis_key_prefix": "custom:prefix",
        }

        config = IndexConfig.from_dict(data)

        assert config.staleness_threshold_days == 14
        assert config.low_coverage_threshold == 70.0
        assert config.use_redis is True
        assert config.redis_key_prefix == "custom:prefix"

    def test_from_dict_partial(self):
        """Test IndexConfig from_dict preserves defaults for missing keys."""
        data = {
            "staleness_threshold_days": 21,
        }

        config = IndexConfig.from_dict(data)

        # Custom value applied
        assert config.staleness_threshold_days == 21
        # Defaults preserved
        assert config.low_coverage_threshold == 50.0
        assert config.test_dir == "tests"

    def test_roundtrip(self):
        """Test IndexConfig serialization roundtrip."""
        original = IndexConfig(
            staleness_threshold_days=5,
            use_redis=True,
            source_dirs=["src", "lib"],
        )

        data = original.to_dict()
        restored = IndexConfig.from_dict(data)

        assert restored.staleness_threshold_days == original.staleness_threshold_days
        assert restored.use_redis == original.use_redis
        assert restored.source_dirs == original.source_dirs
