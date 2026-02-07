"""Documentation Orchestrator Filters.

Filtering, severity validation, and output extension checking for the
DocumentationOrchestrator. Extracted from documentation_orchestrator.py
for maintainability.

Contains:
- DocOrchFilterMixin: File exclusion, severity filtering, output validation

Expected attributes on the host class:
    exclude_patterns: list[str]
    min_severity: str
    _excluded_files: list[dict]
    ALLOWED_OUTPUT_EXTENSIONS: list[str]

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from __future__ import annotations

import fnmatch
from pathlib import Path


class DocOrchFilterMixin:
    """Mixin providing filtering and validation for documentation orchestrator."""

    # Class-level defaults for expected attributes
    exclude_patterns: list[str] = []
    min_severity: str = "low"
    _excluded_files: list[dict] = []  # noqa: RUF012
    ALLOWED_OUTPUT_EXTENSIONS: list[str] = [".md", ".mdx", ".rst"]  # noqa: RUF012

    def _severity_to_priority(self, severity: str) -> int:
        """Convert severity string to numeric priority (1=highest)."""
        return {"high": 1, "medium": 2, "low": 3}.get(severity.lower(), 3)

    def _should_include_severity(self, severity: str) -> bool:
        """Check if severity meets minimum threshold."""
        severity_order = {"high": 1, "medium": 2, "low": 3}
        item_level = severity_order.get(severity.lower(), 3)
        min_level = severity_order.get(self.min_severity.lower(), 3)
        return item_level <= min_level

    def _should_exclude(self, file_path: str, track: bool = False) -> bool:
        """Check if a file should be excluded from documentation generation.

        Uses fnmatch-style pattern matching against exclude_patterns.

        Args:
            file_path: Path to check (relative or absolute)
            track: If True, add to _excluded_files list when excluded

        Returns:
            True if file should be excluded

        """
        # Normalize path for matching
        path_str = str(file_path)
        # Also check just the filename for simple patterns
        filename = Path(file_path).name

        for pattern in self.exclude_patterns:
            # Check full path
            if fnmatch.fnmatch(path_str, pattern):
                if track:
                    self._excluded_files.append(
                        {
                            "file_path": path_str,
                            "matched_pattern": pattern,
                            "reason": self._get_exclusion_reason(pattern),
                        },
                    )
                return True
            # Check just filename
            if fnmatch.fnmatch(filename, pattern):
                if track:
                    self._excluded_files.append(
                        {
                            "file_path": path_str,
                            "matched_pattern": pattern,
                            "reason": self._get_exclusion_reason(pattern),
                        },
                    )
                return True
            # Check if path contains the pattern (for directory patterns)
            if "**" in pattern:
                # Convert ** pattern to a simpler check
                base_pattern = pattern.replace("/**", "").replace("**", "")
                if base_pattern in path_str:
                    if track:
                        self._excluded_files.append(
                            {
                                "file_path": path_str,
                                "matched_pattern": pattern,
                                "reason": self._get_exclusion_reason(pattern),
                            },
                        )
                    return True

        return False

    def _get_exclusion_reason(self, pattern: str) -> str:
        """Get a human-readable reason for why a pattern excludes a file."""
        # Generated directories
        if any(
            p in pattern
            for p in [
                "site/**",
                "dist/**",
                "build/**",
                "out/**",
                "node_modules/**",
                "__pycache__/**",
                ".git/**",
                "egg-info",
            ]
        ):
            return "Generated/build directory"
        # Binary files
        if any(
            p in pattern
            for p in [
                ".png",
                ".jpg",
                ".jpeg",
                ".gif",
                ".ico",
                ".svg",
                ".pdf",
                ".woff",
                ".ttf",
                ".pyc",
                ".so",
                ".dll",
                ".exe",
                ".zip",
                ".tar",
                ".gz",
                ".vsix",
            ]
        ):
            return "Binary/asset file"
        # Empathy internal
        if any(p in pattern for p in [".attune/**", ".claude/**", ".empathy_index/**"]):
            return "Framework internal file"
        # Book/docs
        if any(
            p in pattern
            for p in [
                "book/**",
                "docs/generated/**",
                "docs/word/**",
                "docs/pdf/**",
                ".docx",
                ".doc",
            ]
        ):
            return "Book/document source"
        return "Excluded by pattern"

    def _is_allowed_output(self, file_path: str) -> bool:
        """Check if a file is allowed to be created/modified.

        Uses the ALLOWED_OUTPUT_EXTENSIONS whitelist - this is the PRIMARY
        safety mechanism to ensure only documentation files can be written.

        Args:
            file_path: Path to check

        Returns:
            True if the file extension is in the allowed whitelist

        """
        ext = Path(file_path).suffix.lower()
        return ext in self.ALLOWED_OUTPUT_EXTENSIONS
