"""
Advanced Debugging Wizard - Sub-package

Protocol-based debugging using linting configuration pattern.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

from .linter_parsers import (
    LintIssue,
    Severity,
    parse_linter_output,
    LinterParserFactory
)

from .config_loaders import (
    LintConfig,
    load_config,
    ConfigLoaderFactory
)

from .fix_applier import (
    FixResult,
    apply_fixes,
    group_issues_by_fixability,
    FixApplierFactory
)

from .verification import (
    VerificationResult,
    run_linter,
    verify_fixes,
    compare_issue_lists
)

from .bug_risk_analyzer import (
    BugRisk,
    RiskAssessment,
    BugRiskAnalyzer
)

from .language_patterns import (
    UniversalPattern,
    PatternCategory,
    CrossLanguagePatternLibrary,
    get_pattern_library
)

__all__ = [
    # Parsing
    "LintIssue",
    "Severity",
    "parse_linter_output",
    "LinterParserFactory",

    # Config
    "LintConfig",
    "load_config",
    "ConfigLoaderFactory",

    # Fixing
    "FixResult",
    "apply_fixes",
    "group_issues_by_fixability",
    "FixApplierFactory",

    # Verification
    "VerificationResult",
    "run_linter",
    "verify_fixes",
    "compare_issue_lists",

    # Risk Analysis (Level 4)
    "BugRisk",
    "RiskAssessment",
    "BugRiskAnalyzer",

    # Cross-Language Patterns (Level 5)
    "UniversalPattern",
    "PatternCategory",
    "CrossLanguagePatternLibrary",
    "get_pattern_library"
]
