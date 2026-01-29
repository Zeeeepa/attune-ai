#!/usr/bin/env python3
"""Validate batch 10 test files for completeness and quality.

This script checks generated test files to ensure:
- TODO items have been completed
- Tests follow Given/When/Then pattern
- Proper imports are present
- Docstrings are descriptive

Usage:
    python scripts/validate_batch10_tests.py
    python scripts/validate_batch10_tests.py --strict
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple


class TestValidator:
    """Validator for behavioral test files."""

    def __init__(self, strict: bool = False):
        """Initialize validator.

        Args:
            strict: If True, enforce stricter validation rules
        """
        self.strict = strict
        self.issues: List[str] = []
        self.warnings: List[str] = []

    def validate_file(self, test_file: Path) -> Tuple[bool, List[str], List[str]]:
        """Validate a single test file.

        Args:
            test_file: Path to test file

        Returns:
            Tuple of (is_valid, issues, warnings)
        """
        self.issues = []
        self.warnings = []

        if not test_file.exists():
            self.issues.append(f"File not found: {test_file}")
            return False, self.issues, self.warnings

        content = test_file.read_text()

        # Run validation checks
        self._check_todos(content, test_file)
        self._check_imports(content, test_file)
        self._check_given_when_then(content, test_file)
        self._check_docstrings(content, test_file)
        self._check_test_count(content, test_file)
        self._check_assertions(content, test_file)

        if self.strict:
            self._check_strict_requirements(content, test_file)

        is_valid = len(self.issues) == 0

        return is_valid, self.issues, self.warnings

    def _check_todos(self, content: str, test_file: Path):
        """Check for incomplete TODO items."""
        todo_pattern = r"#\s*TODO:"
        todos = re.findall(todo_pattern, content, re.IGNORECASE)

        if todos:
            count = len(todos)
            self.issues.append(
                f"{test_file.name}: {count} TODO items remaining (must be completed)"
            )

    def _check_imports(self, content: str, test_file: Path):
        """Check for proper imports."""
        # Check for pytest import
        if "import pytest" not in content:
            self.issues.append(f"{test_file.name}: Missing 'import pytest'")

        # Check for mock imports if patches are used
        if "@patch" in content and "from unittest.mock import" not in content:
            self.issues.append(
                f"{test_file.name}: Uses @patch but missing mock imports"
            )

        # Check for module under test import
        if "from empathy_os" not in content:
            self.warnings.append(
                f"{test_file.name}: No imports from empathy_os (is module imported?)"
            )

    def _check_given_when_then(self, content: str, test_file: Path):
        """Check for Given/When/Then pattern in tests."""
        # Find all test methods
        test_methods = re.findall(r"def (test_\w+)\(", content)

        for method_name in test_methods:
            # Extract method body
            method_pattern = rf"def {method_name}\(.*?\):(.*?)(?=\n    def |\n\nclass |\Z)"
            match = re.search(method_pattern, content, re.DOTALL)

            if match:
                method_body = match.group(1)

                # Check for Given/When/Then comments
                has_given = "# Given:" in method_body or "# GIVEN:" in method_body
                has_when = "# When:" in method_body or "# WHEN:" in method_body
                has_then = "# Then:" in method_body or "# THEN:" in method_body

                if not (has_given and has_when and has_then):
                    self.warnings.append(
                        f"{test_file.name}::{method_name}: Missing Given/When/Then structure"
                    )

    def _check_docstrings(self, content: str, test_file: Path):
        """Check for descriptive docstrings."""
        # Find test methods without docstrings
        test_pattern = r'def (test_\w+)\([^)]*\):\s*\n\s*(?!""")'
        methods_without_docstring = re.findall(test_pattern, content)

        if methods_without_docstring:
            for method in methods_without_docstring:
                self.warnings.append(
                    f"{test_file.name}::{method}: Missing docstring"
                )

        # Check for generic docstrings
        generic_patterns = [
            r'"""Test.*\."""',
            r'"""Test function\."""',
            r'"""TODO:.*\."""',
        ]

        for pattern in generic_patterns:
            if re.search(pattern, content):
                self.warnings.append(
                    f"{test_file.name}: Contains generic/TODO docstrings"
                )

    def _check_test_count(self, content: str, test_file: Path):
        """Check for minimum test count."""
        test_methods = re.findall(r"def (test_\w+)\(", content)

        if len(test_methods) < 5:
            self.warnings.append(
                f"{test_file.name}: Only {len(test_methods)} tests (consider adding more)"
            )

    def _check_assertions(self, content: str, test_file: Path):
        """Check that tests have assertions."""
        # Find test methods
        test_methods = re.findall(r"def (test_\w+)\(", content)

        for method_name in test_methods:
            # Extract method body
            method_pattern = rf"def {method_name}\(.*?\):(.*?)(?=\n    def |\n\nclass |\Z)"
            match = re.search(method_pattern, content, re.DOTALL)

            if match:
                method_body = match.group(1)

                # Check for assertions or pytest.raises
                has_assert = (
                    "assert " in method_body or "pytest.raises" in method_body
                )

                # Check for just 'pass'
                has_only_pass = method_body.strip().endswith("pass")

                if has_only_pass or not has_assert:
                    self.warnings.append(
                        f"{test_file.name}::{method_name}: No assertions (stub test)"
                    )

    def _check_strict_requirements(self, content: str, test_file: Path):
        """Apply strict validation rules."""
        # Strict: All tests must have parametrize for multiple cases
        if "happy_path" in content.lower() and "@pytest.mark.parametrize" not in content:
            self.warnings.append(
                f"{test_file.name}: Consider using @pytest.mark.parametrize for happy path tests"
            )

        # Strict: Must have fixtures
        if "@pytest.fixture" not in content:
            self.warnings.append(
                f"{test_file.name}: No fixtures defined (consider adding for reusability)"
            )

        # Strict: Must have mock tests
        if "@patch" not in content and "Mock" not in content:
            self.warnings.append(
                f"{test_file.name}: No mocking used (consider mocking external dependencies)"
            )


def validate_all_tests(
    test_dir: Path, strict: bool = False
) -> Tuple[int, int, List[str]]:
    """Validate all test files in directory.

    Args:
        test_dir: Directory containing test files
        strict: If True, apply strict validation

    Returns:
        Tuple of (valid_count, total_count, all_issues)
    """
    validator = TestValidator(strict=strict)

    test_files = list(test_dir.glob("test_*_behavior.py"))

    if not test_files:
        print(f"No test files found in {test_dir}")
        return 0, 0, []

    valid_count = 0
    total_count = len(test_files)
    all_issues: List[str] = []

    print(f"Validating {total_count} test files...")
    print()

    for test_file in sorted(test_files):
        is_valid, issues, warnings = validator.validate_file(test_file)

        status = "✅" if is_valid else "❌"
        print(f"{status} {test_file.name}")

        if issues:
            for issue in issues:
                print(f"   ❌ {issue}")
                all_issues.append(issue)

        if warnings:
            for warning in warnings:
                print(f"   ⚠️  {warning}")

        if is_valid:
            valid_count += 1

        print()

    return valid_count, total_count, all_issues


def print_summary(valid_count: int, total_count: int, all_issues: List[str]):
    """Print validation summary.

    Args:
        valid_count: Number of valid test files
        total_count: Total number of test files
        all_issues: List of all issues found
    """
    print("=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    print()

    completion_pct = (valid_count / total_count * 100) if total_count > 0 else 0

    print(f"Total Files: {total_count}")
    print(f"Valid Files: {valid_count}")
    print(f"Files with Issues: {total_count - valid_count}")
    print(f"Completion: {completion_pct:.1f}%")
    print()

    if all_issues:
        print(f"Total Issues: {len(all_issues)}")
        print()
        print("Most Common Issues:")

        # Count issue types
        issue_types = {}
        for issue in all_issues:
            issue_type = issue.split(":")[1].strip() if ":" in issue else issue
            issue_types[issue_type] = issue_types.get(issue_type, 0) + 1

        # Sort by count
        sorted_issues = sorted(issue_types.items(), key=lambda x: x[1], reverse=True)

        for issue_type, count in sorted_issues[:5]:
            print(f"  • {issue_type}: {count}")

        print()

    if valid_count == total_count:
        print("✅ All tests validated successfully!")
        print()
        print("Next Steps:")
        print("  1. Run tests: pytest tests/behavioral/generated/batch10/ -v")
        print("  2. Check coverage: python scripts/check_batch10_progress.py")
    else:
        print("⚠️  Some tests need attention")
        print()
        print("Next Steps:")
        print("  1. Address validation issues listed above")
        print("  2. Complete TODO items")
        print("  3. Add missing assertions")
        print("  4. Improve docstrings")
        print("  5. Re-run validation")

    print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate batch 10 behavioral test files"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Apply strict validation rules",
    )
    args = parser.parse_args()

    test_dir = (
        Path(__file__).parent.parent / "tests" / "behavioral" / "generated" / "batch10"
    )

    if not test_dir.exists():
        print(f"Error: Test directory not found: {test_dir}", file=sys.stderr)
        print("\nRun: python scripts/generate_batch10_tests.py", file=sys.stderr)
        return 1

    # Validate all tests
    valid_count, total_count, all_issues = validate_all_tests(test_dir, args.strict)

    # Print summary
    print_summary(valid_count, total_count, all_issues)

    # Exit with non-zero if issues found
    return 0 if valid_count == total_count else 1


if __name__ == "__main__":
    sys.exit(main())
