"""Tests for project_index reports module.

Covers ReportGenerator and all report types.

Copyright 2025 Smart-AI-Memory
Licensed under the Apache License, Version 2.0
"""

from datetime import datetime

import pytest

from attune.project_index.models import (
    FileCategory,
    FileRecord,
    ProjectSummary,
    TestRequirement,
)
from attune.project_index.reports import ReportGenerator


def create_test_record(
    path: str = "src/module.py",
    name: str = "module.py",
    category: FileCategory = FileCategory.SOURCE,
    test_requirement: TestRequirement = TestRequirement.REQUIRED,
    tests_exist: bool = False,
    coverage_percent: float = 0.0,
    impact_score: float = 3.0,
    lines_of_code: int = 100,
    imported_by_count: int = 0,
    is_stale: bool = False,
    staleness_days: int = 0,
    last_modified: datetime | None = None,
    tests_last_modified: datetime | None = None,
    test_file_path: str | None = None,
    needs_attention: bool = False,
    attention_reasons: list[str] | None = None,
) -> FileRecord:
    """Factory to create FileRecord for testing."""
    return FileRecord(
        path=path,
        name=name,
        category=category,
        test_requirement=test_requirement,
        tests_exist=tests_exist,
        coverage_percent=coverage_percent,
        impact_score=impact_score,
        lines_of_code=lines_of_code,
        imported_by_count=imported_by_count,
        is_stale=is_stale,
        staleness_days=staleness_days,
        last_modified=last_modified,
        tests_last_modified=tests_last_modified,
        test_file_path=test_file_path,
        needs_attention=needs_attention,
        attention_reasons=attention_reasons or [],
    )


def create_test_summary(
    total_files: int = 100,
    source_files: int = 60,
    test_files: int = 30,
    test_coverage_avg: float = 75.0,
    files_requiring_tests: int = 60,
    files_with_tests: int = 45,
    files_without_tests: int = 15,
    stale_file_count: int = 5,
    files_with_docstrings_pct: float = 70.0,
    files_with_type_hints_pct: float = 80.0,
    critical_untested_files: list[str] | None = None,
    most_stale_files: list[str] | None = None,
    files_needing_attention: int = 10,
) -> ProjectSummary:
    """Factory to create ProjectSummary for testing."""
    return ProjectSummary(
        total_files=total_files,
        source_files=source_files,
        test_files=test_files,
        test_coverage_avg=test_coverage_avg,
        files_requiring_tests=files_requiring_tests,
        files_with_tests=files_with_tests,
        files_without_tests=files_without_tests,
        stale_file_count=stale_file_count,
        files_with_docstrings_pct=files_with_docstrings_pct,
        files_with_type_hints_pct=files_with_type_hints_pct,
        critical_untested_files=critical_untested_files or [],
        most_stale_files=most_stale_files or [],
        files_needing_attention=files_needing_attention,
    )


@pytest.mark.unit
class TestReportGeneratorInit:
    """Tests for ReportGenerator initialization."""

    def test_basic_init(self):
        """Test basic initialization."""
        summary = create_test_summary()
        records = [create_test_record()]

        generator = ReportGenerator(summary, records)

        assert generator.summary == summary
        assert generator.records == records

    def test_filters_source_records(self):
        """Test that _source_records only contains source files."""
        summary = create_test_summary()
        records = [
            create_test_record(path="src/a.py", category=FileCategory.SOURCE),
            create_test_record(path="tests/test_a.py", category=FileCategory.TEST),
            create_test_record(path="config.yaml", category=FileCategory.CONFIG),
        ]

        generator = ReportGenerator(summary, records)

        assert len(generator._source_records) == 1
        assert generator._source_records[0].path == "src/a.py"

    def test_empty_records(self):
        """Test with empty records list."""
        summary = create_test_summary()

        generator = ReportGenerator(summary, [])

        assert generator._source_records == []


@pytest.mark.unit
class TestTestGapReport:
    """Tests for test_gap_report method."""

    def test_basic_gap_report(self):
        """Test basic test gap report."""
        summary = create_test_summary()
        records = [
            create_test_record(
                path="src/untested.py",
                tests_exist=False,
                impact_score=8.0,
                lines_of_code=200,
            ),
        ]

        generator = ReportGenerator(summary, records)
        report = generator.test_gap_report()

        assert report["report_type"] == "test_gap"
        assert "generated_at" in report
        assert report["summary"]["total_files_needing_tests"] == 1
        assert report["summary"]["total_loc_untested"] == 200
        assert len(report["priority_files"]) == 1

    def test_gap_report_prioritization(self):
        """Test that files are prioritized by impact score."""
        summary = create_test_summary()
        records = [
            create_test_record(path="src/low.py", tests_exist=False, impact_score=2.0),
            create_test_record(path="src/high.py", tests_exist=False, impact_score=10.0),
            create_test_record(path="src/mid.py", tests_exist=False, impact_score=5.0),
        ]

        generator = ReportGenerator(summary, records)
        report = generator.test_gap_report()

        paths = [f["path"] for f in report["priority_files"]]
        assert paths[0] == "src/high.py"
        assert paths[1] == "src/mid.py"
        assert paths[2] == "src/low.py"

    def test_gap_report_excludes_tested_files(self):
        """Test that tested files are excluded."""
        summary = create_test_summary()
        records = [
            create_test_record(path="src/tested.py", tests_exist=True),
            create_test_record(path="src/untested.py", tests_exist=False),
        ]

        generator = ReportGenerator(summary, records)
        report = generator.test_gap_report()

        assert report["summary"]["total_files_needing_tests"] == 1
        assert report["priority_files"][0]["path"] == "src/untested.py"

    def test_gap_report_excludes_optional(self):
        """Test that files with optional test requirement are excluded."""
        summary = create_test_summary()
        records = [
            create_test_record(
                path="src/optional.py",
                tests_exist=False,
                test_requirement=TestRequirement.OPTIONAL,
            ),
            create_test_record(
                path="src/required.py",
                tests_exist=False,
                test_requirement=TestRequirement.REQUIRED,
            ),
        ]

        generator = ReportGenerator(summary, records)
        report = generator.test_gap_report()

        assert report["summary"]["total_files_needing_tests"] == 1

    def test_gap_report_high_impact_count(self):
        """Test high impact file counting."""
        summary = create_test_summary()
        records = [
            create_test_record(path="src/a.py", tests_exist=False, impact_score=6.0),
            create_test_record(path="src/b.py", tests_exist=False, impact_score=3.0),
            create_test_record(path="src/c.py", tests_exist=False, impact_score=5.0),
        ]

        generator = ReportGenerator(summary, records)
        report = generator.test_gap_report()

        # impact >= 5.0 is high impact
        assert report["summary"]["high_impact_untested"] == 2

    def test_gap_report_by_directory(self):
        """Test grouping by directory."""
        summary = create_test_summary()
        records = [
            create_test_record(path="src/a.py", tests_exist=False),
            create_test_record(path="src/b.py", tests_exist=False),
            create_test_record(path="lib/c.py", tests_exist=False),
        ]

        generator = ReportGenerator(summary, records)
        report = generator.test_gap_report()

        assert "by_directory" in report
        assert report["by_directory"]["src"] == 2
        assert report["by_directory"]["lib"] == 1


@pytest.mark.unit
class TestTestRecommendations:
    """Tests for _test_recommendations method."""

    def test_high_impact_recommendation(self):
        """Test recommendation for high impact files."""
        summary = create_test_summary()
        records = [
            create_test_record(
                path="src/critical.py",
                name="critical.py",
                tests_exist=False,
                impact_score=7.0,
            ),
        ]

        generator = ReportGenerator(summary, records)
        needing_tests = [r for r in records if not r.tests_exist]
        recommendations = generator._test_recommendations(needing_tests)

        assert len(recommendations) >= 1
        assert "PRIORITY" in recommendations[0]
        assert "critical.py" in recommendations[0]

    def test_batch_recommendation(self):
        """Test recommendation for many files needing tests."""
        summary = create_test_summary()
        records = [
            create_test_record(path=f"src/file{i}.py", tests_exist=False, impact_score=1.0)
            for i in range(60)
        ]

        generator = ReportGenerator(summary, records)
        recommendations = generator._test_recommendations(records)

        assert any("batch" in r.lower() for r in recommendations)


@pytest.mark.unit
class TestStalenessReport:
    """Tests for staleness_report method."""

    def test_basic_staleness_report(self):
        """Test basic staleness report."""
        summary = create_test_summary()
        records = [
            create_test_record(
                path="src/stale.py",
                is_stale=True,
                staleness_days=10,
                last_modified=datetime(2025, 1, 1),
                test_file_path="tests/test_stale.py",
                tests_last_modified=datetime(2024, 12, 1),
            ),
        ]

        generator = ReportGenerator(summary, records)
        report = generator.staleness_report()

        assert report["report_type"] == "staleness"
        assert report["summary"]["stale_file_count"] == 1
        assert report["summary"]["max_staleness_days"] == 10
        assert len(report["stale_files"]) == 1

    def test_staleness_sorting(self):
        """Test that stale files are sorted by staleness."""
        summary = create_test_summary()
        records = [
            create_test_record(path="src/a.py", is_stale=True, staleness_days=5),
            create_test_record(path="src/b.py", is_stale=True, staleness_days=20),
            create_test_record(path="src/c.py", is_stale=True, staleness_days=10),
        ]

        generator = ReportGenerator(summary, records)
        report = generator.staleness_report()

        paths = [f["path"] for f in report["stale_files"]]
        assert paths[0] == "src/b.py"  # Most stale
        assert paths[1] == "src/c.py"
        assert paths[2] == "src/a.py"

    def test_staleness_excludes_fresh(self):
        """Test that fresh files are excluded."""
        summary = create_test_summary()
        records = [
            create_test_record(path="src/stale.py", is_stale=True, staleness_days=10),
            create_test_record(path="src/fresh.py", is_stale=False, staleness_days=0),
        ]

        generator = ReportGenerator(summary, records)
        report = generator.staleness_report()

        assert report["summary"]["stale_file_count"] == 1

    def test_staleness_average_calculation(self):
        """Test average staleness calculation."""
        summary = create_test_summary()
        records = [
            create_test_record(path="src/a.py", is_stale=True, staleness_days=10),
            create_test_record(path="src/b.py", is_stale=True, staleness_days=20),
        ]

        generator = ReportGenerator(summary, records)
        report = generator.staleness_report()

        assert report["summary"]["avg_staleness_days"] == 15.0

    def test_staleness_empty(self):
        """Test staleness report with no stale files."""
        summary = create_test_summary()
        records = [
            create_test_record(path="src/fresh.py", is_stale=False),
        ]

        generator = ReportGenerator(summary, records)
        report = generator.staleness_report()

        assert report["summary"]["stale_file_count"] == 0
        assert report["summary"]["avg_staleness_days"] == 0
        assert report["summary"]["max_staleness_days"] == 0


@pytest.mark.unit
class TestCoverageReport:
    """Tests for coverage_report method."""

    def test_basic_coverage_report(self):
        """Test basic coverage report."""
        summary = create_test_summary(test_coverage_avg=75.0)
        records = [
            create_test_record(path="src/high.py", coverage_percent=90.0),
            create_test_record(path="src/low.py", coverage_percent=30.0),
        ]

        generator = ReportGenerator(summary, records)
        report = generator.coverage_report()

        assert report["report_type"] == "coverage"
        assert report["summary"]["avg_coverage"] == 75.0
        assert report["summary"]["files_with_data"] == 2
        assert report["summary"]["files_below_50pct"] == 1

    def test_coverage_excludes_zero(self):
        """Test that files with 0% coverage are excluded from 'with_data'."""
        summary = create_test_summary()
        records = [
            create_test_record(path="src/covered.py", coverage_percent=80.0),
            create_test_record(path="src/uncovered.py", coverage_percent=0.0),
        ]

        generator = ReportGenerator(summary, records)
        report = generator.coverage_report()

        assert report["summary"]["files_with_data"] == 1

    def test_low_coverage_files_sorted(self):
        """Test that low coverage files are sorted by coverage."""
        summary = create_test_summary()
        records = [
            create_test_record(path="src/a.py", coverage_percent=40.0),
            create_test_record(path="src/b.py", coverage_percent=10.0),
            create_test_record(path="src/c.py", coverage_percent=30.0),
        ]

        generator = ReportGenerator(summary, records)
        report = generator.coverage_report()

        # Should use heapq.nsmallest for lowest coverage first
        low_coverage = report["low_coverage_files"]
        assert low_coverage[0]["path"] == "src/b.py"  # 10%
        assert low_coverage[1]["path"] == "src/c.py"  # 30%
        assert low_coverage[2]["path"] == "src/a.py"  # 40%

    def test_coverage_by_directory(self):
        """Test coverage by directory calculation."""
        summary = create_test_summary()
        records = [
            create_test_record(path="src/a.py", coverage_percent=80.0),
            create_test_record(path="src/b.py", coverage_percent=60.0),
            create_test_record(path="lib/c.py", coverage_percent=90.0),
        ]

        generator = ReportGenerator(summary, records)
        report = generator.coverage_report()

        by_dir = report["coverage_by_directory"]
        assert by_dir["src"] == 70.0  # Average of 80 and 60
        assert by_dir["lib"] == 90.0


@pytest.mark.unit
class TestHealthReport:
    """Tests for health_report method."""

    def test_basic_health_report(self):
        """Test basic health report."""
        summary = create_test_summary()
        records = [create_test_record()]

        generator = ReportGenerator(summary, records)
        report = generator.health_report()

        assert report["report_type"] == "health"
        assert "health_score" in report
        assert "health_grade" in report
        assert "summary" in report
        assert "strengths" in report
        assert "concerns" in report
        assert "action_items" in report

    def test_health_score_calculation(self):
        """Test health score calculation."""
        summary = create_test_summary(
            test_coverage_avg=85.0,  # +25 points
            files_requiring_tests=100,
            files_with_tests=90,  # 90% = +12 points
            stale_file_count=0,  # No penalty
            source_files=100,
            files_with_docstrings_pct=85.0,  # +10 points
        )
        records = []

        generator = ReportGenerator(summary, records)
        report = generator.health_report()

        # Base 50 + 25 (coverage) + 12 (test ratio) + 10 (docs) = ~97
        assert report["health_score"] >= 90

    def test_health_grades(self):
        """Test health grade assignment."""
        summary = create_test_summary()
        records = []
        generator = ReportGenerator(summary, records)

        assert generator._health_grade(95) == "A"
        assert generator._health_grade(85) == "B"
        assert generator._health_grade(75) == "C"
        assert generator._health_grade(65) == "D"
        assert generator._health_grade(55) == "F"

    def test_health_score_bounds(self):
        """Test that health score stays within 0-100."""
        # Very bad project
        bad_summary = create_test_summary(
            test_coverage_avg=5.0,
            files_requiring_tests=100,
            files_with_tests=0,
            stale_file_count=50,
            source_files=50,
            files_with_docstrings_pct=0.0,
        )
        bad_generator = ReportGenerator(bad_summary, [])
        bad_report = bad_generator.health_report()

        assert bad_report["health_score"] >= 0

        # Very good project
        good_summary = create_test_summary(
            test_coverage_avg=95.0,
            files_requiring_tests=100,
            files_with_tests=100,
            stale_file_count=0,
            source_files=100,
            files_with_docstrings_pct=95.0,
        )
        good_generator = ReportGenerator(good_summary, [])
        good_report = good_generator.health_report()

        assert good_report["health_score"] <= 100


@pytest.mark.unit
class TestStrengthsAndConcerns:
    """Tests for _identify_strengths and _identify_concerns methods."""

    def test_identify_coverage_strength(self):
        """Test identifying good coverage as a strength."""
        summary = create_test_summary(test_coverage_avg=75.0)
        generator = ReportGenerator(summary, [])

        strengths = generator._identify_strengths()

        assert any("coverage" in s.lower() for s in strengths)

    def test_identify_documentation_strength(self):
        """Test identifying good documentation as a strength."""
        summary = create_test_summary(files_with_docstrings_pct=80.0)
        generator = ReportGenerator(summary, [])

        strengths = generator._identify_strengths()

        assert any("documented" in s.lower() for s in strengths)

    def test_identify_typing_strength(self):
        """Test identifying good type hints as a strength."""
        summary = create_test_summary(files_with_type_hints_pct=85.0)
        generator = ReportGenerator(summary, [])

        strengths = generator._identify_strengths()

        assert any("typing" in s.lower() for s in strengths)

    def test_identify_no_stale_strength(self):
        """Test identifying no stale files as a strength."""
        summary = create_test_summary(stale_file_count=0)
        generator = ReportGenerator(summary, [])

        strengths = generator._identify_strengths()

        assert any("up to date" in s.lower() for s in strengths)

    def test_identify_low_coverage_concern(self):
        """Test identifying low coverage as a concern."""
        summary = create_test_summary(test_coverage_avg=30.0)
        generator = ReportGenerator(summary, [])

        concerns = generator._identify_concerns()

        assert any("coverage" in c.lower() for c in concerns)

    def test_identify_missing_tests_concern(self):
        """Test identifying many files without tests as a concern."""
        summary = create_test_summary(files_without_tests=15)
        generator = ReportGenerator(summary, [])

        concerns = generator._identify_concerns()

        assert any("without tests" in c.lower() for c in concerns)

    def test_identify_stale_concern(self):
        """Test identifying stale files as a concern."""
        summary = create_test_summary(stale_file_count=10)
        generator = ReportGenerator(summary, [])

        concerns = generator._identify_concerns()

        assert any("stale" in c.lower() for c in concerns)


@pytest.mark.unit
class TestActionItems:
    """Tests for _generate_action_items method."""

    def test_action_items_for_critical_untested(self):
        """Test action items for critical untested files."""
        summary = create_test_summary(critical_untested_files=["critical.py", "important.py"])
        generator = ReportGenerator(summary, [])

        items = generator._generate_action_items()

        high_priority = [i for i in items if i["priority"] == "high"]
        assert len(high_priority) >= 1
        assert "critical.py" in high_priority[0]["action"]

    def test_action_items_for_stale(self):
        """Test action items for stale files."""
        summary = create_test_summary(most_stale_files=["old.py"])
        generator = ReportGenerator(summary, [])

        items = generator._generate_action_items()

        medium_priority = [i for i in items if i["priority"] == "medium"]
        assert len(medium_priority) >= 1


@pytest.mark.unit
class TestSprintPlanningReport:
    """Tests for sprint_planning_report method."""

    def test_basic_sprint_report(self):
        """Test basic sprint planning report."""
        summary = create_test_summary()
        records = [
            create_test_record(
                path="src/a.py",
                needs_attention=True,
                attention_reasons=["No tests"],
                impact_score=8.0,
                lines_of_code=100,
            ),
        ]

        generator = ReportGenerator(summary, records)
        report = generator.sprint_planning_report(sprint_capacity=5)

        assert report["report_type"] == "sprint_planning"
        assert report["sprint_capacity"] == 5
        assert "suggested_work" in report
        assert "backlog" in report
        assert "metrics_to_track" in report

    def test_sprint_respects_capacity(self):
        """Test that sprint respects capacity limit."""
        summary = create_test_summary()
        records = [
            create_test_record(
                path=f"src/file{i}.py",
                needs_attention=True,
                attention_reasons=["Needs work"],
                impact_score=float(10 - i),
            )
            for i in range(10)
        ]

        generator = ReportGenerator(summary, records)
        report = generator.sprint_planning_report(sprint_capacity=3)

        assert len(report["suggested_work"]) == 3

    def test_sprint_prioritizes_by_impact(self):
        """Test that sprint work is prioritized by impact."""
        summary = create_test_summary()
        records = [
            create_test_record(path="src/low.py", needs_attention=True, impact_score=2.0),
            create_test_record(path="src/high.py", needs_attention=True, impact_score=9.0),
            create_test_record(path="src/mid.py", needs_attention=True, impact_score=5.0),
        ]

        generator = ReportGenerator(summary, records)
        report = generator.sprint_planning_report(sprint_capacity=3)

        paths = [w["path"] for w in report["suggested_work"]]
        assert paths[0] == "src/high.py"

    def test_effort_estimation(self):
        """Test effort estimation for files."""
        summary = create_test_summary()
        records = []
        generator = ReportGenerator(summary, records)

        # Small file without tests
        small = create_test_record(lines_of_code=30, tests_exist=False)
        assert "small" in generator._estimate_effort(small)

        # Medium file without tests
        medium = create_test_record(lines_of_code=100, tests_exist=False)
        assert "medium" in generator._estimate_effort(medium)

        # Large file without tests
        large = create_test_record(lines_of_code=300, tests_exist=False)
        assert "large" in generator._estimate_effort(large)

        # Stale file (has tests)
        stale = create_test_record(tests_exist=True, is_stale=True)
        assert "update" in generator._estimate_effort(stale).lower()


@pytest.mark.unit
class TestMarkdownReports:
    """Tests for markdown report generation."""

    def test_health_markdown(self):
        """Test health report markdown generation."""
        summary = create_test_summary()
        generator = ReportGenerator(summary, [])

        markdown = generator.to_markdown("health")

        assert "# Project Health Report" in markdown
        assert "Health Score" in markdown
        assert "Summary" in markdown

    def test_test_gap_markdown(self):
        """Test test gap report markdown generation."""
        summary = create_test_summary()
        records = [
            create_test_record(path="src/untested.py", tests_exist=False, impact_score=5.0),
        ]
        generator = ReportGenerator(summary, records)

        markdown = generator.to_markdown("test_gap")

        assert "# Test Gap Report" in markdown
        assert "Files Needing Tests" in markdown
        assert "Priority Files" in markdown

    def test_staleness_markdown(self):
        """Test staleness report markdown generation."""
        summary = create_test_summary()
        records = [
            create_test_record(path="src/stale.py", is_stale=True, staleness_days=10),
        ]
        generator = ReportGenerator(summary, records)

        markdown = generator.to_markdown("staleness")

        assert "# Test Staleness Report" in markdown
        assert "Stale Files" in markdown

    def test_unknown_report_type_defaults_to_health(self):
        """Test that unknown report type defaults to health."""
        summary = create_test_summary()
        generator = ReportGenerator(summary, [])

        markdown = generator.to_markdown("unknown_type")

        assert "# Project Health Report" in markdown


@pytest.mark.unit
class TestGroupByDirectory:
    """Tests for _group_by_directory utility method."""

    def test_basic_grouping(self):
        """Test basic directory grouping."""
        summary = create_test_summary()
        generator = ReportGenerator(summary, [])

        records = [
            create_test_record(path="src/a.py"),
            create_test_record(path="src/b.py"),
            create_test_record(path="lib/c.py"),
        ]

        grouped = generator._group_by_directory(records)

        assert grouped["src"] == 2
        assert grouped["lib"] == 1

    def test_root_level_files(self):
        """Test grouping root level files."""
        summary = create_test_summary()
        generator = ReportGenerator(summary, [])

        records = [
            create_test_record(path="root.py"),
        ]

        grouped = generator._group_by_directory(records)

        assert grouped["."] == 1

    def test_empty_records(self):
        """Test grouping with empty records."""
        summary = create_test_summary()
        generator = ReportGenerator(summary, [])

        grouped = generator._group_by_directory([])

        assert grouped == {}
