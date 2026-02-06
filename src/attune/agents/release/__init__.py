"""Release Preparation Agent Team.

A multi-agent system for automated release readiness assessment.

Agents:
    - Security Auditor: Runs bandit, classifies vulnerabilities
    - Test Coverage: Runs pytest --cov, parses coverage
    - Code Quality: Runs ruff, checks complexity
    - Documentation: Checks docstring coverage

Collaboration: Parallel execution with result aggregation
Tier Strategy: Progressive (CHEAP -> CAPABLE -> PREMIUM)
"""

from .release_prep_team import (
    ReleaseAgent,
    ReleasePrepTeam,
    ReleasePrepTeamWorkflow,
    ReleaseReadinessReport,
)

__all__ = [
    "ReleaseAgent",
    "ReleasePrepTeam",
    "ReleasePrepTeamWorkflow",
    "ReleaseReadinessReport",
]
