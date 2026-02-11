"""Attune AI — Workflow Quickstart

Demonstrates running developer workflows programmatically:
1. Security audit on a target path
2. Performance audit
3. Bug prediction
4. Release readiness check (4-agent team)

Usage:
    # Requires ANTHROPIC_API_KEY for API mode
    export ANTHROPIC_API_KEY="sk-ant-..."
    python examples/quickstart_workflows.py

    # In Claude Code, use /attune instead — $0 cost.
"""

import sys


def run_security_audit(target_path: str = "./src") -> None:
    """Run a security audit workflow on the target path."""
    from attune.workflows.security_audit import SecurityAuditWorkflow

    print("=" * 60)
    print("Security Audit")
    print("=" * 60)

    workflow = SecurityAuditWorkflow()
    result = workflow.execute({"path": target_path})

    print(f"  Score: {result.get('score', 'N/A')}/100")
    print(f"  Findings: {result.get('total_findings', 0)}")

    for finding in result.get("findings", [])[:5]:
        severity = finding.get("severity", "UNKNOWN")
        message = finding.get("message", "")
        print(f"  [{severity}] {message}")

    print()


def run_perf_audit(target_path: str = "./src") -> None:
    """Run a performance audit workflow."""
    from attune.workflows.perf_audit import PerformanceAuditWorkflow

    print("=" * 60)
    print("Performance Audit")
    print("=" * 60)

    workflow = PerformanceAuditWorkflow()
    result = workflow.execute({"path": target_path})

    print(f"  Score: {result.get('score', 'N/A')}/100")
    print(f"  Findings: {result.get('total_findings', 0)}")
    print()


def run_bug_predict(target_path: str = "./src") -> None:
    """Run bug prediction on the target path."""
    from attune.workflows.bug_predict import BugPredictionWorkflow

    print("=" * 60)
    print("Bug Prediction")
    print("=" * 60)

    workflow = BugPredictionWorkflow()
    result = workflow.execute({"path": target_path})

    print(f"  Risk Score: {result.get('risk_score', 'N/A')}/100")
    print(f"  Predictions: {result.get('total_predictions', 0)}")
    print()


def run_release_prep() -> None:
    """Run release readiness check with 4-agent team."""
    from attune.agents.release.release_team import ReleaseTeam

    print("=" * 60)
    print("Release Readiness (4-Agent Team)")
    print("=" * 60)

    team = ReleaseTeam()
    report = team.check_readiness()

    status = "APPROVED" if report.approved else "NOT READY"
    print(f"  Status: {status}")
    print(f"  Confidence: {report.confidence}")

    print("\n  Quality Gates:")
    for gate in report.quality_gates:
        icon = "PASS" if gate.passed else "FAIL"
        print(f"    [{icon}] {gate.name}: {gate.actual} (threshold: {gate.threshold})")

    print()


def main() -> int:
    """Run all workflow demos."""
    print()
    print("Attune AI — Workflow Quickstart")
    print("Run developer workflows programmatically.")
    print()
    print("Tip: In Claude Code, type /attune for $0 workflow access.")
    print()

    target = sys.argv[1] if len(sys.argv) > 1 else "./src"

    try:
        run_security_audit(target)
        run_perf_audit(target)
        run_bug_predict(target)
        run_release_prep()
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Install with: pip install attune-ai[developer]")
        return 1
    except Exception as e:  # noqa: BLE001
        # INTENTIONAL: Top-level catch for demo script — show friendly error
        print(f"Error: {type(e).__name__}: {e}")
        print("Ensure ANTHROPIC_API_KEY is set for API mode.")
        return 1

    print("=" * 60)
    print("All workflows complete!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
