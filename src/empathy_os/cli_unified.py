"""Unified CLI for Empathy Framework

A single entry point for all Empathy Framework commands using Typer.

Usage:
    empathy --help                    # Show all commands
    empathy code-review .             # Run code review workflow
    empathy report costs              # View cost reports
    empathy memory status             # Memory control panel

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import subprocess
import sys
from importlib.metadata import version as get_version
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

# =============================================================================
# APP SETUP
# =============================================================================

app = typer.Typer(
    name="empathy",
    help="Empathy Framework - Predictive AI-Developer Collaboration",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

console = Console()


def get_empathy_version() -> str:
    """Get the installed version of empathy-framework."""
    try:
        return get_version("empathy-framework")
    except Exception:
        return "dev"


def version_callback(value: bool):
    """Show version and exit."""
    if value:
        console.print(f"[bold blue]Empathy Framework[/bold blue] v{get_empathy_version()}")
        raise typer.Exit()


@app.callback()
def callback(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
):
    """Empathy Framework - Predictive AI-Developer Collaboration

    The AI collaboration framework that predicts problems before they happen.

    [bold]Workflows:[/bold]
        empathy code-review .     Multi-tier code analysis
        empathy security-audit .  OWASP vulnerability scanning
        empathy test-gen .        Generate tests for coverage gaps

    [bold]Reports:[/bold]
        empathy report costs      API cost tracking
        empathy report dashboard  Open web dashboard

    [bold]Memory:[/bold]
        empathy memory status     Check memory system status
        empathy memory start      Start Redis server

    [bold]Utility:[/bold]
        empathy utility scan .    Scan codebase for issues
        empathy utility learn     Learn patterns from git history
    """


# =============================================================================
# WORKFLOW HELPER
# =============================================================================


def _run_workflow(name: str, path: Path, json_output: bool = False, extra_args: dict | None = None):
    """Helper to run a workflow via the legacy CLI."""
    workflow_input = f'{{"path": "{path}"}}'
    if extra_args:
        import json
        input_dict = {"path": str(path), **extra_args}
        workflow_input = json.dumps(input_dict)

    cmd = [
        sys.executable,
        "-m",
        "empathy_os.cli",
        "workflow",
        "run",
        name,
        "--input",
        workflow_input,
    ]
    if json_output:
        cmd.append("--json")
    subprocess.run(cmd, check=False)


# =============================================================================
# WORKFLOW COMMANDS - Analysis (8)
# =============================================================================


@app.command("code-review")
def code_review(
    path: Path = typer.Argument(Path("."), help="Path to analyze"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """Multi-tier code review with pattern analysis.

    Analyzes code using Haiku (classify), Sonnet (scan), and Opus (architect review).
    Detects change types, security issues, bug patterns, and architectural concerns.

    Examples:
        empathy code-review .
        empathy code-review ./src --json
    """
    _run_workflow("code-review", path, json_output)


@app.command("security-audit")
def security_audit(
    path: Path = typer.Argument(Path("."), help="Path to analyze"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """OWASP-focused vulnerability scanning.

    Scans for injection risks, authentication issues, and security vulnerabilities.
    Integrates with team security decisions to filter false positives.

    Examples:
        empathy security-audit .
        empathy security-audit ./src --json
    """
    _run_workflow("security-audit", path, json_output)


@app.command("test-gen")
def test_gen(
    path: Path = typer.Argument(Path("."), help="Path to analyze"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """Generate tests for areas with low coverage or historical bugs.

    Uses AST-based function/class analysis with complexity estimation.
    Identifies coverage gaps and generates appropriate test cases.

    Examples:
        empathy test-gen .
        empathy test-gen ./src/utils --json
    """
    _run_workflow("test-gen", path, json_output)


@app.command("bug-predict")
def bug_predict(
    path: Path = typer.Argument(Path("."), help="Path to analyze"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """Predict bugs from learned patterns.

    Analyzes code against historical bug patterns to identify potential issues.
    Uses risk threshold of 0.7 (configurable).

    Examples:
        empathy bug-predict .
        empathy bug-predict ./src --json
    """
    _run_workflow("bug-predict", path, json_output)


@app.command("doc-gen")
def doc_gen(
    path: Path = typer.Argument(Path("."), help="Path to analyze"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """Generate documentation with cost-optimized pipeline.

    Stages: outline (CHEAP), write (CAPABLE), polish (PREMIUM).
    Auto-scales tokens and uses chunked polish for large projects.

    Examples:
        empathy doc-gen .
        empathy doc-gen ./src/api --json
    """
    _run_workflow("doc-gen", path, json_output)


@app.command("perf-audit")
def perf_audit(
    path: Path = typer.Argument(Path("."), help="Path to analyze"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """Identify performance bottlenecks and optimization opportunities.

    Detects anti-patterns: N+1 queries, sync in async, unnecessary list copies.
    Provides actionable recommendations for performance improvement.

    Examples:
        empathy perf-audit .
        empathy perf-audit ./src --json
    """
    _run_workflow("perf-audit", path, json_output)


@app.command("refactor-plan")
def refactor_plan(
    path: Path = typer.Argument(Path("."), help="Path to analyze"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """Prioritize tech debt based on trajectory analysis.

    Detects TODO, FIXME, HACK comments and complexity hotspots.
    Creates prioritized refactoring plan based on impact and risk.

    Examples:
        empathy refactor-plan .
        empathy refactor-plan ./src --json
    """
    _run_workflow("refactor-plan", path, json_output)


@app.command("dependency-check")
def dependency_check(
    path: Path = typer.Argument(Path("."), help="Path to analyze"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """Audit dependencies for vulnerabilities, updates, and licensing.

    Parses requirements.txt, package.json, setup.py, and pyproject.toml.
    Identifies outdated packages and security vulnerabilities.

    Examples:
        empathy dependency-check .
        empathy dependency-check ./backend --json
    """
    _run_workflow("dependency-check", path, json_output)


# =============================================================================
# WORKFLOW COMMANDS - Release (3)
# =============================================================================


@app.command("release-prep")
def release_prep(
    path: Path = typer.Argument(Path("."), help="Path to analyze"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """Multi-agent release readiness assessment.

    Runs 4 agents: Security, Testing, Quality, Documentation.
    Checks quality gates: security score, test coverage, code quality, docs completeness.

    Examples:
        empathy release-prep .
        empathy release-prep . --json
    """
    _run_workflow("release-prep", path, json_output)


@app.command("health-check")
def health_check(
    path: Path = typer.Argument(Path("."), help="Path to analyze"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """Project health check with multiple analysis dimensions.

    Evaluates code quality, test coverage, security posture, and documentation.
    Provides overall health score and actionable recommendations.

    Examples:
        empathy health-check .
        empathy health-check . --json
    """
    _run_workflow("health-check", path, json_output)


@app.command("test-coverage-boost")
def test_coverage_boost(
    path: Path = typer.Argument(Path("."), help="Path to analyze"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """Boost test coverage with intelligent test generation.

    3-agent workflow: Coverage Analyzer, Test Generator, Quality Validator.
    Identifies gaps and generates high-quality tests to fill them.

    Examples:
        empathy test-coverage-boost .
        empathy test-coverage-boost ./src --json
    """
    _run_workflow("test-coverage-boost", path, json_output)


# =============================================================================
# WORKFLOW COMMANDS - Review (3)
# =============================================================================


@app.command("pr-review")
def pr_review(
    path: Path = typer.Argument(Path("."), help="Path to analyze"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """Pull request analysis workflow.

    Reviews changes for quality, security, and best practices.
    Provides structured feedback suitable for PR comments.

    Examples:
        empathy pr-review .
        empathy pr-review . --json
    """
    _run_workflow("pr-review", path, json_output)


@app.command("pro-review")
def pro_review(
    path: Path = typer.Argument(Path("."), help="Path to analyze"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """Professional code review pipeline.

    Comprehensive code review with multiple analysis passes.
    Suitable for formal code review processes.

    Examples:
        empathy pro-review .
        empathy pro-review ./src --json
    """
    _run_workflow("pro-review", path, json_output)


@app.command("secure-release")
def secure_release(
    path: Path = typer.Argument(Path("."), help="Path to analyze"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """Security-focused release pipeline.

    Validates security requirements before release.
    Checks for vulnerabilities, secrets, and compliance issues.

    Examples:
        empathy secure-release .
        empathy secure-release . --json
    """
    _run_workflow("secure-release", path, json_output)


# =============================================================================
# REPORT SUBCOMMAND GROUP
# =============================================================================

report_app = typer.Typer(help="View reports and dashboards")
app.add_typer(report_app, name="report")


@report_app.callback(invoke_without_command=True)
def report_default(ctx: typer.Context):
    """View reports and dashboards."""
    if ctx.invoked_subcommand is None:
        console.print("\n[bold]Available Reports:[/bold]")
        console.print("  empathy report costs      - API cost tracking")
        console.print("  empathy report health     - Project health summary")
        console.print("  empathy report coverage   - Test coverage report")
        console.print("  empathy report patterns   - Learned patterns")
        console.print("  empathy report metrics    - Project metrics")
        console.print("  empathy report telemetry  - LLM usage telemetry")
        console.print("  empathy report dashboard  - Open web dashboard")
        console.print()


@report_app.command("costs")
def report_costs():
    """View API cost tracking."""
    subprocess.run([sys.executable, "-m", "empathy_os.cli", "costs"], check=False)


@report_app.command("health")
def report_health():
    """View project health summary."""
    subprocess.run([sys.executable, "-m", "empathy_os.cli", "status"], check=False)


@report_app.command("coverage")
def report_coverage():
    """View test coverage report."""
    subprocess.run([sys.executable, "-m", "empathy_os.cli", "tests"], check=False)


@report_app.command("patterns")
def report_patterns():
    """View learned patterns."""
    subprocess.run(
        [sys.executable, "-m", "empathy_os.memory.control_panel", "patterns", "--list"],
        check=False,
    )


@report_app.command("metrics")
def report_metrics():
    """View project metrics and statistics."""
    subprocess.run(
        [sys.executable, "-m", "empathy_os.cli", "metrics", "show"],
        check=False,
    )


@report_app.command("telemetry")
def report_telemetry(
    limit: int = typer.Option(20, "--limit", "-l", help="Number of entries"),
    days: int = typer.Option(None, "--days", "-d", help="Filter to last N days"),
):
    """View LLM usage telemetry."""
    args = [sys.executable, "-m", "empathy_os.cli", "telemetry", "show", "--limit", str(limit)]
    if days:
        args.extend(["--days", str(days)])
    subprocess.run(args, check=False)


@report_app.command("dashboard")
def report_dashboard(
    port: int = typer.Option(8765, "--port", "-p", help="Port to run on"),
    no_browser: bool = typer.Option(False, "--no-browser", help="Don't open browser"),
):
    """Open web dashboard."""
    cmd = [sys.executable, "-m", "empathy_os.cli", "dashboard"]
    cmd.extend(["--port", str(port)])
    if no_browser:
        cmd.append("--no-browser")
    subprocess.run(cmd, check=False)


# =============================================================================
# MEMORY SUBCOMMAND GROUP
# =============================================================================

memory_app = typer.Typer(help="Memory system control panel")
app.add_typer(memory_app, name="memory")


@memory_app.callback(invoke_without_command=True)
def memory_default(ctx: typer.Context):
    """Memory system control panel."""
    if ctx.invoked_subcommand is None:
        subprocess.run(
            [sys.executable, "-m", "empathy_os.memory.control_panel", "status"],
            check=False,
        )


@memory_app.command("status")
def memory_status():
    """Check memory system status (Redis, patterns, stats)."""
    subprocess.run(
        [sys.executable, "-m", "empathy_os.memory.control_panel", "status"],
        check=False,
    )


@memory_app.command("start")
def memory_start():
    """Start Redis server for short-term memory."""
    subprocess.run(
        [sys.executable, "-m", "empathy_os.memory.control_panel", "start"],
        check=False,
    )


@memory_app.command("stop")
def memory_stop():
    """Stop Redis server."""
    subprocess.run(
        [sys.executable, "-m", "empathy_os.memory.control_panel", "stop"],
        check=False,
    )


@memory_app.command("patterns")
def memory_patterns():
    """List stored patterns."""
    subprocess.run(
        [sys.executable, "-m", "empathy_os.memory.control_panel", "patterns", "--list"],
        check=False,
    )


# =============================================================================
# TIER SUBCOMMAND GROUP
# =============================================================================

tier_app = typer.Typer(help="Intelligent tier recommendations")
app.add_typer(tier_app, name="tier")


@tier_app.command("setup")
def tier_setup(
    default_tier: str = typer.Option(
        None, "--default", "-d", help="Default tier: CHEAP, CAPABLE, or PREMIUM"
    ),
    max_cost: float = typer.Option(
        None, "--max-cost", "-m", help="Maximum cost per workflow run ($)"
    ),
    auto_escalate: bool = typer.Option(
        None, "--auto-escalate/--no-auto-escalate", help="Enable automatic tier escalation"
    ),
    show: bool = typer.Option(False, "--show", "-s", help="Show current configuration"),
):
    """Configure tier preferences and cost limits."""
    import json
    config_path = Path(".empathy") / "tier_config.json"

    config = {}
    if config_path.exists():
        try:
            config = json.loads(config_path.read_text())
        except json.JSONDecodeError:
            pass

    if show or (default_tier is None and max_cost is None and auto_escalate is None):
        console.print("\n[bold]Tier Configuration[/bold]")
        console.print("-" * 40)
        console.print(f"Default Tier: {config.get('default_tier', 'CAPABLE')}")
        console.print(f"Max Cost: ${config.get('max_cost', 1.00):.2f}")
        console.print(f"Auto-Escalate: {config.get('auto_escalate', True)}")
        console.print(f"\nConfig file: {config_path}")
        console.print()
        return

    if default_tier:
        tier_upper = default_tier.upper()
        if tier_upper not in ("CHEAP", "CAPABLE", "PREMIUM"):
            console.print(f"[red]Invalid tier: {default_tier}[/red]")
            console.print("Valid tiers: CHEAP, CAPABLE, PREMIUM")
            raise typer.Exit(code=1)
        config["default_tier"] = tier_upper

    if max_cost is not None:
        config["max_cost"] = max_cost

    if auto_escalate is not None:
        config["auto_escalate"] = auto_escalate

    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(config, indent=2))

    console.print("[green]Tier configuration updated[/green]")
    console.print(f"Saved to: {config_path}")


@tier_app.command("recommend")
def tier_recommend(
    description: str = typer.Argument(..., help="Description of the bug or task"),
    files: str = typer.Option(None, "--files", "-f", help="Comma-separated affected files"),
    complexity: int = typer.Option(None, "--complexity", "-c", help="Complexity hint 1-10"),
):
    """Get intelligent tier recommendation for a bug/task."""
    from empathy_os.tier_recommender import TierRecommender

    recommender = TierRecommender()
    result = recommender.recommend(
        bug_description=description,
        files_affected=files.split(",") if files else None,
        complexity_hint=complexity,
    )

    console.print()
    console.print("[bold]TIER RECOMMENDATION[/bold]")
    console.print("-" * 50)
    console.print(f"Task: {description}")
    console.print()
    console.print(f"Recommended Tier: [bold]{result.tier}[/bold]")
    console.print(f"Confidence: {result.confidence * 100:.1f}%")
    console.print(f"Expected Cost: ${result.expected_cost:.3f}")
    console.print()
    console.print(f"Reasoning: {result.reasoning}")
    console.print()


# =============================================================================
# UTILITY SUBCOMMAND GROUP
# =============================================================================

utility_app = typer.Typer(help="Project utility tools")
app.add_typer(utility_app, name="utility")


@utility_app.callback(invoke_without_command=True)
def utility_default(ctx: typer.Context):
    """Project utility tools."""
    if ctx.invoked_subcommand is None:
        console.print("\n[bold]Available Utility Commands:[/bold]")
        console.print("  empathy utility scan .        - Scan codebase for issues")
        console.print("  empathy utility inspect .     - Deep inspection (SARIF)")
        console.print("  empathy utility fix           - Auto-fix lint/format")
        console.print("  empathy utility init          - Initialize project")
        console.print("  empathy utility new --list    - List project templates")
        console.print("  empathy utility onboard       - Interactive tutorial")
        console.print("  empathy utility explain <cmd> - Explain a command")
        console.print("  empathy utility learn         - Learn from git history")
        console.print("  empathy utility sync-claude   - Sync to Claude Code")
        console.print("  empathy utility cheatsheet    - Show quick reference")
        console.print()


@utility_app.command("scan")
def utility_scan(
    path: Path = typer.Argument(Path("."), help="Path to scan"),
    fix: bool = typer.Option(False, "--fix", help="Auto-fix issues"),
    staged: bool = typer.Option(False, "--staged", help="Scan staged files only"),
):
    """Scan codebase for issues."""
    args = ["empathy-scan", str(path)]
    if fix:
        args.append("--fix")
    if staged:
        args.append("--staged")
    result = subprocess.run(args, check=False)
    if result.returncode != 0:
        console.print("[yellow]Note: empathy-scan may not be installed[/yellow]")


@utility_app.command("inspect")
def utility_inspect(
    path: Path = typer.Argument(Path("."), help="Path to inspect"),
    format_out: str = typer.Option("text", "--format", "-f", help="Output format"),
):
    """Deep inspection with SARIF output for CI/CD."""
    args = ["empathy-inspect", str(path)]
    if format_out != "text":
        args.extend(["--format", format_out])
    result = subprocess.run(args, check=False)
    if result.returncode != 0:
        console.print("[yellow]Note: empathy-inspect may not be installed[/yellow]")


@utility_app.command("fix")
def utility_fix():
    """Auto-fix lint and format issues."""
    subprocess.run([sys.executable, "-m", "empathy_os.cli", "fix-all"], check=False)


@utility_app.command("init")
def utility_init():
    """Initialize a new Empathy project."""
    subprocess.run([sys.executable, "-m", "empathy_os.cli", "init"], check=False)


@utility_app.command("new")
def utility_new(
    template: str = typer.Argument(None, help="Template name (or --list to show all)"),
    name: str = typer.Argument(None, help="Project name"),
    list_templates: bool = typer.Option(False, "--list", "-l", help="List available templates"),
):
    """Create a new project from a template."""
    if list_templates or template is None:
        subprocess.run([sys.executable, "-m", "empathy_os.cli", "new", "--list"], check=False)
    else:
        args = [sys.executable, "-m", "empathy_os.cli", "new", template]
        if name:
            args.append(name)
        subprocess.run(args, check=False)


@utility_app.command("onboard")
def utility_onboard():
    """Interactive onboarding tutorial for new users."""
    subprocess.run([sys.executable, "-m", "empathy_os.cli", "onboard"], check=False)


@utility_app.command("explain")
def utility_explain(
    command: str = typer.Argument(..., help="Command to explain"),
):
    """Get detailed explanation of how a command works."""
    subprocess.run([sys.executable, "-m", "empathy_os.cli", "explain", command], check=False)


@utility_app.command("learn")
def utility_learn(
    analyze: int = typer.Option(20, "--analyze", "-a", help="Number of commits to analyze"),
):
    """Learn patterns from commit history."""
    subprocess.run(
        [sys.executable, "-m", "empathy_os.cli", "learn", "--analyze", str(analyze)],
        check=False,
    )


@utility_app.command("sync-claude")
def utility_sync_claude():
    """Sync patterns to Claude Code memory."""
    subprocess.run(["empathy-sync-claude", "--source", "patterns"], check=False)


@utility_app.command("cheatsheet")
def utility_cheatsheet():
    """Show quick reference for all commands."""
    console.print(
        Panel.fit(
            """[bold]Workflows (Analysis)[/bold]
  empathy code-review .       Multi-tier code analysis
  empathy security-audit .    OWASP vulnerability scan
  empathy test-gen .          Generate tests
  empathy bug-predict .       Predict bugs from patterns
  empathy doc-gen .           Generate documentation
  empathy perf-audit .        Performance analysis
  empathy refactor-plan .     Tech debt prioritization
  empathy dependency-check .  Dependency audit

[bold]Workflows (Release)[/bold]
  empathy release-prep .      Release readiness check
  empathy health-check .      Project health check
  empathy test-coverage-boost . Boost test coverage

[bold]Workflows (Review)[/bold]
  empathy pr-review .         Pull request review
  empathy pro-review .        Professional code review
  empathy secure-release .    Security-focused release

[bold]Reports[/bold]
  empathy report costs        API cost tracking
  empathy report health       Project health summary
  empathy report coverage     Test coverage
  empathy report patterns     Learned patterns
  empathy report metrics      Project metrics
  empathy report telemetry    LLM usage telemetry
  empathy report dashboard    Open web dashboard

[bold]Memory[/bold]
  empathy memory              Show status
  empathy memory start        Start Redis
  empathy memory stop         Stop Redis
  empathy memory patterns     List patterns

[bold]Tier Optimization[/bold]
  empathy tier setup          Configure tier preferences
  empathy tier recommend      Get tier recommendation

[bold]Utility[/bold]
  empathy utility scan .        Quick scan for issues
  empathy utility inspect .     Deep inspection (SARIF)
  empathy utility fix           Auto-fix lint/format
  empathy utility init          Initialize project
  empathy utility new --list    List project templates
  empathy utility onboard       Interactive tutorial
  empathy utility explain <cmd> Explain a command
  empathy utility learn         Learn from git history
  empathy utility sync-claude   Sync to Claude Code""",
            title="[bold blue]Empathy Framework Cheatsheet[/bold blue]",
        ),
    )


# =============================================================================
# ENTRY POINT
# =============================================================================


def main():
    """Entry point for the unified CLI."""
    app()


if __name__ == "__main__":
    main()
