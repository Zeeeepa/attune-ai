"""Unified CLI for Empathy Framework

A simplified, intelligent CLI using Socratic questioning.

Usage:
    empathy do "review code in src/"    # Intelligent - asks questions if needed
    empathy r .                         # Quick: review
    empathy s .                         # Quick: security
    empathy t .                         # Quick: test
    empathy scan .                      # Quick scan (no API)
    empathy ship                        # Pre-commit check

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import json
import subprocess
import sys
from importlib.metadata import version as get_version
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

# =============================================================================
# CONSTANTS
# =============================================================================

CHEATSHEET_CONTENT = """\
[bold]Main Command[/bold]
  empathy do "..."        Intelligent task execution (asks questions if needed)

[bold]Quick Actions (short aliases)[/bold]
  empathy r [path]        Review code
  empathy s [path]        Security audit
  empathy t [path]        Generate tests
  empathy d [path]        Generate docs

[bold]Utilities[/bold]
  empathy scan [path]     Quick scan (no API needed)
  empathy ship            Pre-commit validation
  empathy health          Project health check

[bold]Reports[/bold]
  empathy report costs    API cost tracking
  empathy report health   Project health summary
  empathy report patterns Learned patterns

[bold]Memory[/bold]
  empathy memory          Memory system status
  empathy memory start    Start Redis"""

TIER_CONFIG_PATH = Path(".empathy") / "tier_config.json"


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def _load_tier_config() -> dict:
    """Load tier configuration from .empathy/tier_config.json."""
    if TIER_CONFIG_PATH.exists():
        try:
            return json.loads(TIER_CONFIG_PATH.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def _save_tier_config(config: dict) -> None:
    """Save tier configuration to .empathy/tier_config.json."""
    TIER_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    TIER_CONFIG_PATH.write_text(json.dumps(config, indent=2))


def _auto_sync_patterns() -> None:
    """Automatically sync patterns to Claude Code after workflow completion."""
    try:
        result = subprocess.run(
            ["empathy-sync-claude", "--source", "patterns"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if result.returncode == 0:
            console.print("\n[dim]✓ Patterns synced to Claude Code[/dim]")
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass  # Silent fail


def _run_workflow(name: str, path: Path, json_output: bool = False):
    """Helper to run a workflow via the legacy CLI."""
    workflow_input = f'{{"path": "{path}"}}'

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

    result = subprocess.run(cmd, check=False)

    if result.returncode == 0 and not json_output:
        _auto_sync_patterns()


# =============================================================================
# APP SETUP
# =============================================================================

app = typer.Typer(
    name="empathy",
    help="Empathy Framework - Intelligent AI-Developer Collaboration",
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
    """Empathy Framework - Intelligent AI-Developer Collaboration

    [bold]Quick Start:[/bold]
        empathy do "review the code"    Ask AI to do something
        empathy r .                     Quick code review
        empathy scan .                  Quick security scan

    [bold]Shortcuts:[/bold]
        r = review, s = security, t = test, d = docs
    """


# =============================================================================
# MAIN COMMAND: do
# =============================================================================


@app.command("do")
def do_command(
    goal: str = typer.Argument(..., help="What you want to accomplish"),
    path: Path = typer.Option(Path("."), "--path", "-p", help="Path to analyze"),
    interactive: bool = typer.Option(
        True, "--interactive/--no-interactive", "-i", help="Ask clarifying questions"
    ),
):
    """Intelligent task execution using Socratic questioning.

    The AI will understand your goal and ask clarifying questions if needed.
    Uses domain templates for common tasks like code review, security, testing.

    Examples:
        empathy do "review the authentication code"
        empathy do "find security vulnerabilities" --path ./src
        empathy do "generate tests for the API" --no-interactive
    """
    console.print(f"\n[bold]Goal:[/bold] {goal}")
    console.print(f"[dim]Path: {path}[/dim]\n")

    # Use Socratic system for intelligent task execution
    try:
        from empathy_os.socratic import SocraticWorkflowBuilder
        from empathy_os.socratic.cli import console as socratic_console
        from empathy_os.socratic.cli import render_form_interactive
        from empathy_os.socratic.storage import get_default_storage

        builder = SocraticWorkflowBuilder()
        storage = get_default_storage()

        # Start session with the goal
        session = builder.start_session()
        session = builder.set_goal(session, f"{goal} (path: {path})")
        storage.save_session(session)

        # Show domain detection
        if session.goal_analysis:
            console.print(f"[cyan]Detected domain:[/cyan] {session.goal_analysis.domain}")
            console.print(f"[cyan]Confidence:[/cyan] {session.goal_analysis.confidence:.0%}")

            if session.goal_analysis.ambiguities and interactive:
                console.print("\n[yellow]Clarifications needed:[/yellow]")
                for amb in session.goal_analysis.ambiguities:
                    console.print(f"  • {amb}")

        # Interactive questioning if needed
        if interactive:
            while not builder.is_ready_to_generate(session):
                form = builder.get_next_questions(session)
                if not form:
                    break

                answers = render_form_interactive(form, socratic_console)
                session = builder.submit_answers(session, answers)
                storage.save_session(session)

        # Generate and execute workflow
        if builder.is_ready_to_generate(session):
            console.print("\n[bold]Generating workflow...[/bold]")
            workflow = builder.generate_workflow(session)
            storage.save_session(session)

            console.print(
                f"\n[green]✓ Generated workflow with {len(workflow.agents)} agents[/green]"
            )
            console.print(workflow.describe())

            # Execute the workflow
            if session.blueprint:
                storage.save_blueprint(session.blueprint)
                console.print(f"\n[dim]Blueprint saved: {session.blueprint.id[:8]}...[/dim]")

        _auto_sync_patterns()

    except ImportError as e:
        console.print(f"[yellow]Socratic system not fully available: {e}[/yellow]")
        console.print("[dim]Falling back to keyword matching...[/dim]\n")

        # Fallback: keyword-based workflow selection
        goal_lower = goal.lower()
        if any(w in goal_lower for w in ["review", "check", "analyze"]):
            _run_workflow("code-review", path)
        elif any(w in goal_lower for w in ["security", "vulnerab", "owasp"]):
            _run_workflow("security-audit", path)
        elif any(w in goal_lower for w in ["test", "coverage"]):
            _run_workflow("test-gen", path)
        elif any(w in goal_lower for w in ["doc", "document"]):
            _run_workflow("doc-gen", path)
        else:
            _run_workflow("code-review", path)


# =============================================================================
# SHORT ALIASES
# =============================================================================


@app.command("r")
def review_short(
    path: Path = typer.Argument(Path("."), help="Path to review"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """[bold]Review[/bold] - Quick code review.

    Alias for: empathy do "review code"
    """
    _run_workflow("code-review", path, json_output)


@app.command("s")
def security_short(
    path: Path = typer.Argument(Path("."), help="Path to scan"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """[bold]Security[/bold] - Quick security audit.

    Alias for: empathy do "security audit"
    """
    _run_workflow("security-audit", path, json_output)


@app.command("t")
def test_short(
    path: Path = typer.Argument(Path("."), help="Path to analyze"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """[bold]Test[/bold] - Generate tests.

    Alias for: empathy do "generate tests"
    """
    _run_workflow("test-gen", path, json_output)


@app.command("d")
def docs_short(
    path: Path = typer.Argument(Path("."), help="Path to document"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """[bold]Docs[/bold] - Generate documentation.

    Alias for: empathy do "generate docs"
    """
    _run_workflow("doc-gen", path, json_output)


# =============================================================================
# UTILITY COMMANDS
# =============================================================================


@app.command("scan")
def scan_command(
    scan_type: str = typer.Argument("all", help="Scan type: security, performance, or all"),
    path: Path = typer.Argument(Path("."), help="Path to scan"),
):
    """Quick security/performance scan (no API needed).

    Examples:
        empathy scan all .
        empathy scan security ./src
    """
    if scan_type not in ("security", "performance", "all"):
        console.print(f"[red]Invalid scan type: {scan_type}[/red]")
        console.print("Valid types: security, performance, all")
        raise typer.Exit(code=1)

    subprocess.run(["empathy-scan", scan_type, str(path)], check=False)


@app.command("ship")
def ship_command(
    skip_sync: bool = typer.Option(False, "--skip-sync", help="Skip pattern sync"),
):
    """Pre-commit validation (lint, format, tests, security).

    Run this before committing to ensure code quality.
    """
    args = [sys.executable, "-m", "empathy_os.cli", "ship"]
    if skip_sync:
        args.append("--skip-sync")
    subprocess.run(args, check=False)


@app.command("health")
def health_command(
    deep: bool = typer.Option(False, "--deep", help="Comprehensive check"),
    fix: bool = typer.Option(False, "--fix", help="Auto-fix issues"),
):
    """Quick project health check.

    Shows lint issues, test status, and overall health score.
    """
    args = [sys.executable, "-m", "empathy_os.cli", "health"]
    if deep:
        args.append("--deep")
    if fix:
        args.append("--fix")
    subprocess.run(args, check=False)


# =============================================================================
# REPORT SUBCOMMAND GROUP
# =============================================================================

report_app = typer.Typer(help="View reports and dashboards")
app.add_typer(report_app, name="report")


@report_app.command("costs")
def report_costs():
    """View API cost tracking."""
    subprocess.run([sys.executable, "-m", "empathy_os.cli", "costs"], check=False)


@report_app.command("health")
def report_health():
    """View project health summary."""
    subprocess.run([sys.executable, "-m", "empathy_os.cli", "status"], check=False)


@report_app.command("patterns")
def report_patterns():
    """View learned patterns."""
    subprocess.run(
        [sys.executable, "-m", "empathy_os.memory.control_panel", "patterns"],
        check=False,
    )


@report_app.command("telemetry")
def report_telemetry(
    limit: int = typer.Option(20, "--limit", "-l", help="Number of entries"),
):
    """View LLM usage telemetry."""
    subprocess.run(
        [sys.executable, "-m", "empathy_os.cli", "telemetry", "show", "--limit", str(limit)],
        check=False,
    )


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
    """Check memory system status."""
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
        [sys.executable, "-m", "empathy_os.memory.control_panel", "patterns"],
        check=False,
    )


# =============================================================================
# CHEATSHEET
# =============================================================================


@app.command("cheatsheet")
def cheatsheet():
    """Show quick reference for all commands."""
    console.print(
        Panel.fit(
            CHEATSHEET_CONTENT,
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
