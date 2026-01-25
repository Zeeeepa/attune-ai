"""Memory Leak Scanner - Identifies potential memory issues across the codebase.

This tool performs:
1. Static analysis - Scans for patterns that commonly cause memory leaks
2. Hot file detection - Ranks files by likelihood of memory issues
3. Dynamic profiling - Optional runtime memory testing of suspicious modules
4. Issue reporting - Consolidated report with prioritized fixes

Usage:
    # Scan entire src directory
    python benchmarks/memory_leak_scanner.py

    # Scan specific directory
    python benchmarks/memory_leak_scanner.py --path src/empathy_os/memory

    # Scan and profile top 5 hot files
    python benchmarks/memory_leak_scanner.py --profile --top 5

    # Output JSON report
    python benchmarks/memory_leak_scanner.py --json > memory_report.json

    # Scan specific feature (finds related files)
    python benchmarks/memory_leak_scanner.py --feature "pattern search"
"""

import argparse
import ast
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@dataclass
class MemoryIssue:
    """A detected memory issue."""

    file_path: str
    line_number: int
    issue_type: str
    severity: str  # HIGH, MEDIUM, LOW
    description: str
    code_snippet: str
    suggestion: str
    mitigated: bool = False  # True if issue has existing mitigation
    mitigation_note: str = ""  # Explanation of why it's mitigated

    def to_dict(self) -> dict:
        result = {
            "file": self.file_path,
            "line": self.line_number,
            "type": self.issue_type,
            "severity": self.severity,
            "description": self.description,
            "code": self.code_snippet,
            "suggestion": self.suggestion,
        }
        if self.mitigated:
            result["mitigated"] = True
            result["mitigation_note"] = self.mitigation_note
        return result


@dataclass
class FileAnalysis:
    """Analysis results for a single file."""

    file_path: str
    issues: list[MemoryIssue] = field(default_factory=list)
    risk_score: float = 0.0
    patterns_found: list[str] = field(default_factory=list)

    @property
    def high_count(self) -> int:
        """Count of active (non-mitigated) HIGH severity issues."""
        return sum(1 for i in self.issues if i.severity == "HIGH" and not i.mitigated)

    @property
    def medium_count(self) -> int:
        """Count of active (non-mitigated) MEDIUM severity issues."""
        return sum(1 for i in self.issues if i.severity == "MEDIUM" and not i.mitigated)

    @property
    def low_count(self) -> int:
        """Count of active (non-mitigated) LOW severity issues."""
        return sum(1 for i in self.issues if i.severity == "LOW" and not i.mitigated)

    @property
    def active_count(self) -> int:
        """Count of all active (non-mitigated) issues."""
        return sum(1 for i in self.issues if not i.mitigated)

    @property
    def mitigated_count(self) -> int:
        """Count of mitigated issues."""
        return sum(1 for i in self.issues if i.mitigated)


# =============================================================================
# PATTERN DEFINITIONS
# =============================================================================

MEMORY_PATTERNS = {
    # HIGH severity patterns
    "sorted_slice": {
        "pattern": r"sorted\s*\([^)]+\)\s*\[\s*:\s*\d+\s*\]",
        "severity": "HIGH",
        "description": "sorted()[:N] creates full sorted list before slicing",
        "suggestion": "Use heapq.nlargest(N, iterable, key=...) instead",
    },
    "get_all_pattern": {
        "pattern": r"def\s+(_?get_all_\w+|_?load_all_\w+|_?fetch_all_\w+)\s*\(",
        "severity": "HIGH",
        "description": "get_all_* methods often load entire datasets into memory",
        "suggestion": "Consider adding a generator variant (iter_all_*) or pagination",
    },
    "list_append_loop": {
        "pattern": r"(\w+)\s*=\s*\[\]\s*\n.*?for\s+.*?:\s*\n\s+\1\.append\(",
        "severity": "MEDIUM",
        "description": "Building list with append in loop - may be unbounded",
        "suggestion": "Consider generator expression or bounded collection",
    },
    # MEDIUM severity patterns
    "list_comprehension_large": {
        "pattern": r"\[\s*\w+\s+for\s+\w+\s+in\s+(?:self\._\w+|glob|rglob|walk|listdir)",
        "severity": "MEDIUM",
        "description": "List comprehension over potentially large iterator",
        "suggestion": "Use generator expression if single iteration suffices",
    },
    "list_set_dedup": {
        "pattern": r"list\s*\(\s*set\s*\(",
        "severity": "MEDIUM",
        "description": "list(set(...)) loses insertion order",
        "suggestion": "Use list(dict.fromkeys(...)) to preserve order",
    },
    "list_range": {
        "pattern": r"list\s*\(\s*range\s*\(",
        "severity": "LOW",
        "description": "list(range(...)) creates unnecessary list",
        "suggestion": "Use range() directly if only iterating",
    },
    "no_cache_eviction": {
        "pattern": r"self\._cache\s*\[\s*\w+\s*\]\s*=(?!.*maxsize|.*lru|.*evict)",
        "severity": "MEDIUM",
        "description": "Cache assignment without apparent size limit",
        "suggestion": "Add max_size limit and eviction policy",
    },
    "global_list_accumulator": {
        "pattern": r"^(\w+)\s*:\s*list\s*=\s*\[\]",
        "severity": "MEDIUM",
        "description": "Module-level list that may accumulate indefinitely",
        "suggestion": "Consider bounded deque or periodic cleanup",
    },
    # LOW severity patterns
    "dict_values_list": {
        "pattern": r"list\s*\(\s*\w+\.values\s*\(\s*\)\s*\)",
        "severity": "LOW",
        "description": "list(dict.values()) creates copy - may be unnecessary",
        "suggestion": "Iterate directly over .values() if possible",
    },
    "dict_keys_list": {
        "pattern": r"list\s*\(\s*\w+\.keys\s*\(\s*\)\s*\)",
        "severity": "LOW",
        "description": "list(dict.keys()) creates copy - may be unnecessary",
        "suggestion": "Iterate directly over dict if possible",
    },
    "json_loads_large": {
        "pattern": r"json\.load[s]?\s*\([^)]*\)(?!.*streaming|.*ijson)",
        "severity": "LOW",
        "description": "JSON parsing loads entire content into memory",
        "suggestion": "Consider streaming JSON parser (ijson) for large files",
    },
    "read_entire_file": {
        "pattern": r"\.read\s*\(\s*\)(?!.*chunk|.*buffer)",
        "severity": "LOW",
        "description": "Reading entire file into memory",
        "suggestion": "Consider chunked reading for large files",
    },
}

# AST-based patterns (more accurate but slower)
AST_PATTERNS = {
    "unbounded_recursion": {
        "description": "Recursive function without apparent base case limit",
        "severity": "HIGH",
    },
    "circular_reference_risk": {
        "description": "Class holds reference to instances of same class",
        "severity": "MEDIUM",
    },
    "large_default_mutable": {
        "description": "Mutable default argument (list/dict) in function",
        "severity": "MEDIUM",
    },
}


class MemoryLeakScanner:
    """Scans codebase for memory leak patterns."""

    def __init__(self, base_path: str = "src", filter_false_positives: bool = True):
        self.base_path = Path(base_path)
        self.analyses: list[FileAnalysis] = []
        self.total_issues = 0
        self.filter_false_positives = filter_false_positives
        self.filtered_count = 0  # Track filtered issues

    def scan_directory(self, path: Path | None = None) -> list[FileAnalysis]:
        """Scan directory for memory issues."""
        scan_path = path or self.base_path
        self.analyses = []

        for py_file in self._iter_python_files(scan_path):
            analysis = self._analyze_file(py_file)
            if analysis.issues:
                self.analyses.append(analysis)
                self.total_issues += len(analysis.issues)

        # Sort by risk score (highest first)
        self.analyses.sort(key=lambda a: a.risk_score, reverse=True)
        return self.analyses

    def scan_feature(self, feature_name: str) -> list[FileAnalysis]:
        """Scan files related to a specific feature."""
        # Find files mentioning the feature
        feature_words = feature_name.lower().split()
        related_files = []

        for py_file in self._iter_python_files(self.base_path):
            try:
                content = py_file.read_text(encoding="utf-8").lower()
                # Check if file is related to feature
                matches = sum(1 for word in feature_words if word in content)
                if matches >= len(feature_words) // 2 + 1:
                    related_files.append(py_file)
            except (OSError, UnicodeDecodeError):
                continue

        # Analyze related files
        self.analyses = []
        for py_file in related_files:
            analysis = self._analyze_file(py_file)
            self.analyses.append(analysis)
            self.total_issues += len(analysis.issues)

        self.analyses.sort(key=lambda a: a.risk_score, reverse=True)
        return self.analyses

    def _iter_python_files(self, path: Path) -> Iterator[Path]:
        """Iterate over Python files, skipping tests and venv."""
        skip_dirs = {"__pycache__", ".git", "venv", ".venv", "node_modules", ".tox"}

        for py_file in path.rglob("*.py"):
            # Skip test files and virtual environments
            if any(skip in py_file.parts for skip in skip_dirs):
                continue
            if "test_" in py_file.name and "/tests/" not in str(py_file):
                continue
            yield py_file

    def _analyze_file(self, file_path: Path) -> FileAnalysis:
        """Analyze a single file for memory issues."""
        analysis = FileAnalysis(file_path=str(file_path))

        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.splitlines()
        except (OSError, UnicodeDecodeError) as e:
            return analysis

        # Regex-based pattern matching
        for pattern_name, pattern_info in MEMORY_PATTERNS.items():
            for match in re.finditer(pattern_info["pattern"], content, re.MULTILINE):
                line_num = content[:match.start()].count("\n") + 1
                code_line = lines[line_num - 1].strip() if line_num <= len(lines) else ""

                issue = MemoryIssue(
                    file_path=str(file_path),
                    line_number=line_num,
                    issue_type=pattern_name,
                    severity=pattern_info["severity"],
                    description=pattern_info["description"],
                    code_snippet=code_line[:100],
                    suggestion=pattern_info["suggestion"],
                )
                analysis.issues.append(issue)
                analysis.patterns_found.append(pattern_name)

        # AST-based analysis for more complex patterns
        try:
            tree = ast.parse(content)
            self._analyze_ast(tree, analysis, lines)
        except SyntaxError:
            pass  # Skip files with syntax errors

        # Check for false positives and mark mitigated issues
        if self.filter_false_positives:
            self._check_false_positives(analysis, content, lines)
            # Count filtered issues
            self.filtered_count += sum(1 for i in analysis.issues if i.mitigated)

        # Calculate risk score
        analysis.risk_score = self._calculate_risk_score(analysis)

        return analysis

    def _analyze_ast(
        self, tree: ast.AST, analysis: FileAnalysis, lines: list[str]
    ) -> None:
        """AST-based analysis for complex patterns."""
        for node in ast.walk(tree):
            # Check for mutable default arguments
            if isinstance(node, ast.FunctionDef):
                for default in node.args.defaults + node.args.kw_defaults:
                    if default and isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        code_line = (
                            lines[node.lineno - 1].strip()
                            if node.lineno <= len(lines)
                            else ""
                        )
                        issue = MemoryIssue(
                            file_path=analysis.file_path,
                            line_number=node.lineno,
                            issue_type="mutable_default_arg",
                            severity="MEDIUM",
                            description="Mutable default argument shares state across calls",
                            code_snippet=code_line[:100],
                            suggestion="Use None default and create mutable inside function",
                        )
                        analysis.issues.append(issue)
                        analysis.patterns_found.append("mutable_default_arg")

            # Check for while True without break/return (potential infinite loop)
            if isinstance(node, ast.While):
                if isinstance(node.test, ast.Constant) and node.test.value is True:
                    has_exit = any(
                        isinstance(n, (ast.Break, ast.Return)) for n in ast.walk(node)
                    )
                    if not has_exit:
                        code_line = (
                            lines[node.lineno - 1].strip()
                            if node.lineno <= len(lines)
                            else ""
                        )
                        issue = MemoryIssue(
                            file_path=analysis.file_path,
                            line_number=node.lineno,
                            issue_type="infinite_loop_risk",
                            severity="HIGH",
                            description="while True without visible break statement",
                            code_snippet=code_line[:100],
                            suggestion="Ensure loop has exit condition",
                        )
                        analysis.issues.append(issue)
                        analysis.patterns_found.append("infinite_loop_risk")

    def _calculate_risk_score(self, analysis: FileAnalysis) -> float:
        """Calculate risk score based on issues found."""
        score = 0.0
        for issue in analysis.issues:
            if issue.mitigated:
                continue  # Don't count mitigated issues
            if issue.severity == "HIGH":
                score += 10.0
            elif issue.severity == "MEDIUM":
                score += 5.0
            else:
                score += 1.0

        # Bonus for multiple patterns (compound risk)
        unique_patterns = len(set(analysis.patterns_found))
        if unique_patterns > 3:
            score *= 1.5

        return score

    def _check_false_positives(
        self, analysis: FileAnalysis, content: str, lines: list[str]
    ) -> None:
        """Check for false positives and mark issues as mitigated.

        This method applies smart filtering to reduce noise from patterns
        that are technically detected but have existing mitigations.
        """
        for issue in analysis.issues:
            # Check get_all_* patterns for iterator variants
            if issue.issue_type == "get_all_pattern":
                mitigation = self._check_get_all_mitigation(
                    content, lines, issue.line_number
                )
                if mitigation:
                    issue.mitigated = True
                    issue.mitigation_note = mitigation

            # Check infinite loops for try/except wrappers
            elif issue.issue_type == "infinite_loop_risk":
                if self._check_loop_has_exception_handler(content, issue.line_number):
                    issue.mitigated = True
                    issue.mitigation_note = "Loop wrapped in try/except (e.g., KeyboardInterrupt)"

            # Check list_append_loop for bounded contexts
            elif issue.issue_type == "list_append_loop":
                if self._check_append_is_bounded(content, lines, issue.line_number):
                    issue.mitigated = True
                    issue.mitigation_note = "Append loop is bounded (serialization or fixed iteration)"

            # Check list comprehensions in mock/test code
            elif issue.issue_type == "list_comprehension_large":
                if "_mock" in content.lower() or "mock_storage" in content.lower():
                    if "_mock" in issue.code_snippet.lower():
                        issue.mitigated = True
                        issue.mitigation_note = "In mock/test code"

    def _check_get_all_mitigation(
        self, content: str, lines: list[str], line_num: int
    ) -> str | None:
        """Check if get_all_* method has mitigations."""
        # Get the method name from the line
        if line_num > len(lines):
            return None
        line = lines[line_num - 1]

        # Extract method name
        match = re.search(r"def\s+(_?(?:get|load|fetch)_all_\w+)", line)
        if not match:
            return None
        method_name = match.group(1)

        # Check for iterator variant (iter_all_* or iter_*)
        base_name = method_name.replace("get_all_", "").replace("load_all_", "").replace("fetch_all_", "")
        iter_patterns = [
            f"def iter_all_{base_name}",
            f"def iter_{base_name}",
            f"def _iter_all_{base_name}",
            f"def _iter_{base_name}",
        ]
        for pattern in iter_patterns:
            if pattern in content:
                return f"Has iterator variant: {pattern.replace('def ', '')}"

        # Check if method just returns a reference (not a copy)
        # Look for "return self._" pattern in nearby lines
        start_line = line_num
        end_line = min(line_num + 10, len(lines))
        method_body = "\n".join(lines[start_line:end_line])
        if re.search(r"return\s+self\._\w+\s*$", method_body, re.MULTILINE):
            return "Returns reference, not copy"

        # Check for documentation warning about memory
        doc_start = max(0, line_num - 1)
        doc_end = min(line_num + 5, len(lines))
        doc_area = "\n".join(lines[doc_start:doc_end]).lower()
        if "memory" in doc_area and ("iter" in doc_area or "generator" in doc_area):
            return "Documented memory consideration"

        return None

    def _check_loop_has_exception_handler(self, content: str, line_num: int) -> bool:
        """Check if while True loop is inside try/except block."""
        lines = content.splitlines()
        if line_num > len(lines):
            return False

        # Look backwards for try: statement
        indent_of_while = len(lines[line_num - 1]) - len(lines[line_num - 1].lstrip())
        for i in range(line_num - 2, max(0, line_num - 20), -1):
            line = lines[i]
            if not line.strip():
                continue
            line_indent = len(line) - len(line.lstrip())
            # Found a try statement at lower indentation
            if line.strip().startswith("try:") and line_indent < indent_of_while:
                # Check if there's a matching except
                for j in range(line_num, min(len(lines), line_num + 20)):
                    if lines[j].strip().startswith("except"):
                        return True
                break
            # Hit function definition, stop searching
            if line.strip().startswith("def "):
                break

        return False

    def _check_append_is_bounded(
        self, content: str, lines: list[str], line_num: int
    ) -> bool:
        """Check if list append loop is bounded."""
        if line_num > len(lines):
            return False

        # Look at surrounding context (10 lines before and after)
        start = max(0, line_num - 10)
        end = min(len(lines), line_num + 10)
        context = "\n".join(lines[start:end]).lower()

        # Check for bounded iteration patterns
        bounded_patterns = [
            r"for\s+\w+\s+in\s+\w+\.agents",  # Iterating over agents
            r"for\s+\w+\s+in\s+\w+\.stages",  # Iterating over stages
            r"for\s+\w+\s+in\s+\w+\.metrics",  # Iterating over metrics
            r"for\s+\w+\s+in\s+\w+\.tools",  # Iterating over tools
            r"for\s+\w+\s+in\s+\w+\.items",  # Iterating over items
            r"for\s+\w+\s+in\s+range\(",  # Fixed range
            r"for\s+\w+\s+in\s+enumerate\(",  # Enumeration
        ]

        for pattern in bounded_patterns:
            if re.search(pattern, context):
                return True

        # Check for JSON serialization context
        if "json" in context or "serialize" in context or "to_dict" in context:
            return True

        return False

    def get_hot_files(self, top_n: int = 10) -> list[FileAnalysis]:
        """Get top N files most likely to have memory issues."""
        return self.analyses[:top_n]

    def generate_report(self, format: str = "text") -> str:
        """Generate a report of findings."""
        if format == "json":
            return self._generate_json_report()
        return self._generate_text_report()

    def _generate_text_report(self) -> str:
        """Generate human-readable text report."""
        lines = []
        lines.append("=" * 70)
        lines.append("MEMORY LEAK SCANNER REPORT")
        lines.append("=" * 70)
        lines.append(f"\nFiles scanned: {len(self.analyses) + self._count_clean_files()}")
        lines.append(f"Files with issues: {len(self.analyses)}")
        lines.append(f"Total issues found: {self.total_issues}")
        if self.filter_false_positives and self.filtered_count > 0:
            active_issues = self.total_issues - self.filtered_count
            lines.append(f"  - Active issues: {active_issues}")
            lines.append(f"  - Mitigated (false positives): {self.filtered_count}")

        # Summary by severity
        high = sum(a.high_count for a in self.analyses)
        medium = sum(a.medium_count for a in self.analyses)
        low = sum(a.low_count for a in self.analyses)
        lines.append(f"\nBy severity: HIGH={high}, MEDIUM={medium}, LOW={low}")

        lines.append("\n" + "-" * 70)
        lines.append("HOT FILES (ranked by risk score)")
        lines.append("-" * 70)

        for i, analysis in enumerate(self.analyses[:15], 1):
            rel_path = self._relative_path(analysis.file_path)
            lines.append(
                f"\n{i}. {rel_path}"
                f"\n   Risk Score: {analysis.risk_score:.1f} | "
                f"Issues: {len(analysis.issues)} "
                f"(H:{analysis.high_count} M:{analysis.medium_count} L:{analysis.low_count})"
            )

            # Show top 3 active (non-mitigated) issues per file
            active_issues = [i for i in analysis.issues if not i.mitigated]
            mitigated_count = len(analysis.issues) - len(active_issues)

            for issue in active_issues[:3]:
                lines.append(f"   [{issue.severity}] Line {issue.line_number}: {issue.issue_type}")
                lines.append(f"       {issue.description}")

            if len(active_issues) > 3:
                lines.append(f"   ... and {len(active_issues) - 3} more active issues")

            if mitigated_count > 0:
                lines.append(f"   ✓ {mitigated_count} issue(s) already mitigated")

        lines.append("\n" + "-" * 70)
        lines.append("ISSUE TYPE SUMMARY")
        lines.append("-" * 70)

        # Count by issue type (separating active vs mitigated)
        type_counts: dict[str, dict[str, int]] = {}
        for analysis in self.analyses:
            for issue in analysis.issues:
                if issue.issue_type not in type_counts:
                    type_counts[issue.issue_type] = {"active": 0, "mitigated": 0, "severity": issue.severity}
                if issue.mitigated:
                    type_counts[issue.issue_type]["mitigated"] += 1
                else:
                    type_counts[issue.issue_type]["active"] += 1

        for issue_type, counts in sorted(type_counts.items(), key=lambda x: -(x[1]["active"])):
            severity = counts["severity"]
            active = counts["active"]
            mitigated = counts["mitigated"]
            if mitigated > 0:
                lines.append(f"  [{severity}] {issue_type}: {active} active, {mitigated} mitigated")
            else:
                lines.append(f"  [{severity}] {issue_type}: {active} occurrences")

        lines.append("\n" + "=" * 70)
        lines.append("RECOMMENDATIONS")
        lines.append("=" * 70)

        if high > 0:
            lines.append(f"\n1. Address {high} HIGH severity issues first:")
            lines.append("   - sorted()[:N] → heapq.nlargest()")
            lines.append("   - get_all_* methods → add iterator variants")
            lines.append("   - Infinite loops → ensure exit conditions")

        if medium > 0:
            lines.append(f"\n2. Review {medium} MEDIUM severity issues:")
            lines.append("   - Large list comprehensions → generators")
            lines.append("   - Unbounded caches → add eviction")
            lines.append("   - Mutable defaults → use None pattern")

        lines.append("\n" + "=" * 70)
        return "\n".join(lines)

    def _generate_json_report(self) -> str:
        """Generate JSON report."""
        report = {
            "summary": {
                "files_with_issues": len(self.analyses),
                "total_issues": self.total_issues,
                "high_severity": sum(a.high_count for a in self.analyses),
                "medium_severity": sum(a.medium_count for a in self.analyses),
                "low_severity": sum(a.low_count for a in self.analyses),
            },
            "hot_files": [
                {
                    "file": self._relative_path(a.file_path),
                    "risk_score": a.risk_score,
                    "issue_count": len(a.issues),
                    "issues": [i.to_dict() for i in a.issues],
                }
                for a in self.analyses[:20]
            ],
        }
        return json.dumps(report, indent=2)

    def _relative_path(self, path: str) -> str:
        """Convert to relative path for cleaner output."""
        try:
            return str(Path(path).relative_to(Path.cwd()))
        except ValueError:
            return path

    def _count_clean_files(self) -> int:
        """Count files without issues (for reporting)."""
        # This is approximate since we don't store clean files
        return 0


def profile_hot_files(scanner: MemoryLeakScanner, top_n: int = 5) -> dict:
    """Dynamically profile the top hot files."""
    try:
        from memory_profiler import memory_usage
    except ImportError:
        return {"error": "memory_profiler not installed. Run: pip install memory_profiler"}

    results = {}
    hot_files = scanner.get_hot_files(top_n)

    for analysis in hot_files:
        file_path = Path(analysis.file_path)
        module_name = file_path.stem

        # Try to import and profile key functions
        try:
            # Get baseline memory
            baseline = memory_usage(-1, interval=0.1, timeout=1)[0]

            # Import the module
            import importlib.util

            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Check memory after import
                after_import = memory_usage(-1, interval=0.1, timeout=1)[0]

                results[str(file_path)] = {
                    "baseline_mb": baseline,
                    "after_import_mb": after_import,
                    "import_overhead_mb": after_import - baseline,
                    "risk_score": analysis.risk_score,
                    "issues": len(analysis.issues),
                }
        except Exception as e:
            results[str(file_path)] = {"error": str(e)}

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Scan codebase for memory leak patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--path",
        default="src",
        help="Directory to scan (default: src)",
    )
    parser.add_argument(
        "--feature",
        help="Scan files related to a specific feature",
    )
    parser.add_argument(
        "--profile",
        action="store_true",
        help="Run dynamic memory profiling on hot files",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="Number of hot files to show/profile (default: 10)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON format",
    )
    parser.add_argument(
        "--min-severity",
        choices=["HIGH", "MEDIUM", "LOW"],
        default="LOW",
        help="Minimum severity to report (default: LOW)",
    )
    parser.add_argument(
        "--no-filter",
        action="store_true",
        help="Disable false positive filtering (show all raw detections)",
    )
    parser.add_argument(
        "--show-mitigated",
        action="store_true",
        help="Include mitigated issues in output (only with filtering enabled)",
    )

    args = parser.parse_args()

    scanner = MemoryLeakScanner(
        base_path=args.path,
        filter_false_positives=not args.no_filter,
    )

    if args.feature:
        print(f"Scanning files related to: {args.feature}")
        scanner.scan_feature(args.feature)
    else:
        print(f"Scanning directory: {args.path}")
        scanner.scan_directory()

    # Filter by severity if requested
    if args.min_severity != "LOW":
        severity_order = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        min_level = severity_order[args.min_severity]
        for analysis in scanner.analyses:
            analysis.issues = [
                i for i in analysis.issues
                if severity_order.get(i.severity, 0) >= min_level
            ]

    # Generate report
    if args.json:
        print(scanner.generate_report(format="json"))
    else:
        print(scanner.generate_report())

        # Optional profiling
        if args.profile:
            print("\n" + "=" * 70)
            print("DYNAMIC PROFILING RESULTS")
            print("=" * 70)
            profile_results = profile_hot_files(scanner, args.top)
            for file_path, result in profile_results.items():
                rel_path = scanner._relative_path(file_path)
                if "error" in result:
                    print(f"\n{rel_path}: Error - {result['error']}")
                else:
                    print(f"\n{rel_path}:")
                    print(f"  Import overhead: {result['import_overhead_mb']:.2f} MB")
                    print(f"  Risk score: {result['risk_score']:.1f}")


if __name__ == "__main__":
    main()
