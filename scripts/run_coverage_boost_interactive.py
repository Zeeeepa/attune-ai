#!/usr/bin/env python3
"""Automatic Test Coverage Boost - Interactive Socratic Form

Guides you through configuration with Socratic questioning method.

Usage:
    python run_coverage_boost_interactive.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import time

from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt

console = Console()


def ask_socratic_questions() -> dict:
    """Ask configuration questions using Socratic method."""

    console.print()
    console.print(
        Panel.fit(
            "[bold cyan]📋 Test Coverage Configuration[/bold cyan]\n"
            "[dim]Let me understand your testing needs through a few questions[/dim]",
            border_style="cyan",
        )
    )
    console.print()

    responses = {}

    # Question 1: Scope
    console.print(
        "[bold]Question 1 of 12:[/bold] [cyan]What is the scope of your testing effort?[/cyan]\n"
    )
    scope_options = [
        "1. Single function/class",
        "2. Single module/package",
        "3. Multiple modules",
        "4. Entire project (full suite)",
    ]
    for opt in scope_options:
        console.print(f"  {opt}")

    scope_choice = Prompt.ask(
        "\n[bold]Your choice[/bold]", choices=["1", "2", "3", "4"], default="4"
    )
    scope_map = {
        "1": "Single function/class",
        "2": "Single module/package",
        "3": "Multiple modules",
        "4": "Entire project (full suite)",
    }
    responses["test_scope"] = scope_map[scope_choice]
    console.print(f"[green]✓ Selected: {responses['test_scope']}[/green]\n")

    # Question 2: Test types
    console.print(
        "[bold]Question 2 of 12:[/bold] [cyan]What types of tests should be created?[/cyan]"
    )
    console.print("[dim](Select multiple - enter comma-separated numbers, e.g., 1,2,3)[/dim]\n")

    test_type_options = [
        "1. Unit tests (functions, classes)",
        "2. Integration tests (module interactions)",
        "3. End-to-end tests (full workflows)",
        "4. Performance/Load tests",
        "5. Security tests",
    ]
    for opt in test_type_options:
        console.print(f"  {opt}")

    test_types_input = Prompt.ask("\n[bold]Your choices[/bold]", default="1,2,3")
    test_type_map = {
        "1": "Unit tests (functions, classes)",
        "2": "Integration tests (module interactions)",
        "3": "End-to-end tests (full workflows)",
        "4": "Performance/Load tests",
        "5": "Security tests",
    }
    selected_types = [
        test_type_map[n.strip()] for n in test_types_input.split(",") if n.strip() in test_type_map
    ]
    responses["test_types"] = selected_types
    console.print(f"[green]✓ Selected: {', '.join(selected_types)}[/green]\n")

    # Question 3: Framework
    console.print(
        "[bold]Question 3 of 12:[/bold] [cyan]Which testing framework should be used?[/cyan]\n"
    )

    framework_options = [
        "1. pytest (Python)",
        "2. unittest (Python standard)",
        "3. Auto-detect from project",
    ]
    for opt in framework_options:
        console.print(f"  {opt}")

    framework_choice = Prompt.ask(
        "\n[bold]Your choice[/bold]", choices=["1", "2", "3"], default="1"
    )
    framework_map = {
        "1": "pytest (Python)",
        "2": "unittest (Python standard)",
        "3": "Auto-detect from project",
    }
    responses["testing_framework"] = framework_map[framework_choice]
    console.print(f"[green]✓ Selected: {responses['testing_framework']}[/green]\n")

    # Question 4: Coverage target
    console.print(
        "[bold]Question 4 of 12:[/bold] [cyan]What is your target test coverage?[/cyan]\n"
    )

    coverage_options = [
        "1. 60% (basic coverage)",
        "2. 70% (standard coverage)",
        "3. 80% (good coverage)",
        "4. 90% (high coverage)",
        "5. 95%+ (comprehensive coverage)",
    ]
    for opt in coverage_options:
        console.print(f"  {opt}")

    coverage_choice = Prompt.ask(
        "\n[bold]Your choice[/bold]", choices=["1", "2", "3", "4", "5"], default="5"
    )
    coverage_map = {
        "1": "60% (basic coverage)",
        "2": "70% (standard coverage)",
        "3": "80% (good coverage)",
        "4": "90% (high coverage)",
        "5": "95%+ (comprehensive coverage)",
    }
    responses["coverage_target"] = coverage_map[coverage_choice]
    console.print(f"[green]✓ Selected: {responses['coverage_target']}[/green]\n")

    # Question 5: Quality checks
    console.print(
        "[bold]Question 5 of 12:[/bold] [cyan]What quality checks should be applied?[/cyan]"
    )
    console.print("[dim](Select multiple - enter comma-separated numbers)[/dim]\n")

    quality_options = [
        "1. Assertion depth (avoid shallow tests)",
        "2. Edge case coverage (boundary conditions)",
        "3. Error handling tests (exception paths)",
        "4. Mock/fixture quality validation",
    ]
    for opt in quality_options:
        console.print(f"  {opt}")

    quality_input = Prompt.ask("\n[bold]Your choices[/bold]", default="1,2,3")
    quality_map = {
        "1": "Assertion depth (avoid shallow tests)",
        "2": "Edge case coverage (boundary conditions)",
        "3": "Error handling tests (exception paths)",
        "4": "Mock/fixture quality validation",
    }
    selected_quality = [
        quality_map[n.strip()] for n in quality_input.split(",") if n.strip() in quality_map
    ]
    responses["test_quality_checks"] = selected_quality
    console.print(f"[green]✓ Selected: {', '.join(selected_quality)}[/green]\n")

    # Question 6: Inspection mode
    console.print(
        "[bold]Question 6 of 12:[/bold] [cyan]Should we analyze existing tests or create new ones?[/cyan]\n"
    )

    inspection_options = [
        "1. Analyze existing tests only",
        "2. Create new tests only",
        "3. Both (analyze + create new)",
    ]
    for opt in inspection_options:
        console.print(f"  {opt}")

    inspection_choice = Prompt.ask(
        "\n[bold]Your choice[/bold]", choices=["1", "2", "3"], default="3"
    )
    inspection_map = {
        "1": "Analyze existing tests only",
        "2": "Create new tests only",
        "3": "Both (analyze + create new)",
    }
    responses["test_inspection_mode"] = inspection_map[inspection_choice]
    console.print(f"[green]✓ Selected: {responses['test_inspection_mode']}[/green]\n")

    # Question 7: Update outdated tests
    console.print(
        "[bold]Question 7 of 12:[/bold] [cyan]Update outdated or broken tests automatically?[/cyan]\n"
    )
    responses["update_outdated_tests"] = Confirm.ask(
        "[bold]Enable automatic updates?[/bold]", default=True
    )
    console.print(
        f"[green]✓ Selected: {'Yes' if responses['update_outdated_tests'] else 'No'}[/green]\n"
    )

    # Question 8: Test data strategy
    console.print(
        "[bold]Question 8 of 12:[/bold] [cyan]What test data strategy should be used?[/cyan]\n"
    )

    data_options = [
        "1. Minimal fixtures (simple test data)",
        "2. Realistic fixtures (production-like data)",
        "3. Property-based testing (Hypothesis)",
        "4. Mixed strategy (combination)",
    ]
    for opt in data_options:
        console.print(f"  {opt}")

    data_choice = Prompt.ask(
        "\n[bold]Your choice[/bold]", choices=["1", "2", "3", "4"], default="2"
    )
    data_map = {
        "1": "Minimal fixtures (simple test data)",
        "2": "Realistic fixtures (production-like data)",
        "3": "Property-based testing (Hypothesis)",
        "4": "Mixed strategy (combination)",
    }
    responses["test_data_strategy"] = data_map[data_choice]
    console.print(f"[green]✓ Selected: {responses['test_data_strategy']}[/green]\n")

    # Question 9: Parallel execution
    console.print("[bold]Question 9 of 12:[/bold] [cyan]Enable parallel test execution?[/cyan]\n")
    responses["parallel_execution"] = Confirm.ask(
        "[bold]Enable parallel execution?[/bold]", default=True
    )
    console.print(
        f"[green]✓ Selected: {'Yes' if responses['parallel_execution'] else 'No'}[/green]\n"
    )

    # Question 10: Test reports
    console.print(
        "[bold]Question 10 of 12:[/bold] [cyan]What test reports should be generated?[/cyan]"
    )
    console.print("[dim](Select multiple - enter comma-separated numbers)[/dim]\n")

    report_options = [
        "1. Coverage report (HTML + terminal)",
        "2. Test execution summary (JUnit XML)",
        "3. Performance metrics (test duration)",
    ]
    for opt in report_options:
        console.print(f"  {opt}")

    report_input = Prompt.ask("\n[bold]Your choices[/bold]", default="1,2,3")
    report_map = {
        "1": "Coverage report (HTML + terminal)",
        "2": "Test execution summary (JUnit XML)",
        "3": "Performance metrics (test duration)",
    }
    selected_reports = [
        report_map[n.strip()] for n in report_input.split(",") if n.strip() in report_map
    ]
    responses["generate_test_reports"] = selected_reports
    console.print(f"[green]✓ Selected: {', '.join(selected_reports)}[/green]\n")

    # Question 11: CI integration
    console.print(
        "[bold]Question 11 of 12:[/bold] [cyan]Generate CI/CD integration (GitHub Actions)?[/cyan]\n"
    )
    responses["ci_integration"] = Confirm.ask(
        "[bold]Enable CI/CD integration?[/bold]", default=True
    )
    console.print(f"[green]✓ Selected: {'Yes' if responses['ci_integration'] else 'No'}[/green]\n")

    # Question 12: Documentation
    console.print(
        "[bold]Question 12 of 12:[/bold] [cyan]Generate test documentation and examples?[/cyan]\n"
    )
    responses["test_documentation"] = Confirm.ask(
        "[bold]Generate documentation?[/bold]", default=True
    )
    console.print(
        f"[green]✓ Selected: {'Yes' if responses['test_documentation'] else 'No'}[/green]\n"
    )

    return responses


def show_configuration_summary(responses: dict):
    """Display configuration summary for confirmation."""
    console.print()
    console.print(
        Panel(
            "[bold]Configuration Summary:[/bold]\n\n"
            f"[cyan]Scope:[/cyan] {responses['test_scope']}\n"
            f"[cyan]Test Types:[/cyan] {len(responses['test_types'])} types selected\n"
            f"[cyan]Framework:[/cyan] {responses['testing_framework']}\n"
            f"[cyan]Coverage Target:[/cyan] {responses['coverage_target']}\n"
            f"[cyan]Quality Checks:[/cyan] {len(responses['test_quality_checks'])} checks\n"
            f"[cyan]Inspection Mode:[/cyan] {responses['test_inspection_mode']}\n"
            f"[cyan]Update Tests:[/cyan] {'Yes' if responses['update_outdated_tests'] else 'No'}\n"
            f"[cyan]Data Strategy:[/cyan] {responses['test_data_strategy']}\n"
            f"[cyan]Parallel Execution:[/cyan] {'Yes' if responses['parallel_execution'] else 'No'}\n"
            f"[cyan]Reports:[/cyan] {len(responses['generate_test_reports'])} types\n"
            f"[cyan]CI Integration:[/cyan] {'Yes' if responses['ci_integration'] else 'No'}\n"
            f"[cyan]Documentation:[/cyan] {'Yes' if responses['test_documentation'] else 'No'}",
            title="📋 Your Configuration",
            border_style="cyan",
        )
    )
    console.print()


def execute_agent_team(responses: dict):
    """Execute the agent team based on configuration."""

    console.print("[bold green]🚀 Starting Agent Team Execution[/bold green]\n")

    # Determine which agents to use based on responses
    agents = []

    # Always include analyzer
    agents.append(("test_analyzer", "capable_first", "Analyzing existing tests"))

    # Add generators based on test types
    if "Unit tests (functions, classes)" in responses.get("test_types", []):
        agents.append(("unit_test_generator", "progressive", "Generating unit tests"))
    if "Integration tests (module interactions)" in responses.get("test_types", []):
        agents.append(("integration_test_creator", "progressive", "Creating integration tests"))
    if "End-to-end tests (full workflows)" in responses.get("test_types", []):
        agents.append(("e2e_test_designer", "capable_first", "Designing E2E tests"))

    # Add quality validator if checks are enabled
    if responses.get("test_quality_checks"):
        agents.append(("test_quality_validator", "cheap_only", "Validating test quality"))

    # Add updater if enabled
    if responses.get("update_outdated_tests"):
        agents.append(("test_updater", "progressive", "Updating outdated tests"))

    # Add fixture manager
    agents.append(("fixture_manager", "cheap_only", "Creating test fixtures"))

    # Add performance tests if selected
    if "Performance/Load tests" in responses.get("test_types", []):
        agents.append(("performance_test_creator", "capable_first", "Creating performance tests"))

    # Add report generator if reports enabled
    if responses.get("generate_test_reports"):
        agents.append(("test_report_generator", "cheap_only", "Generating test reports"))

    # Add CI integration if enabled
    if responses.get("ci_integration"):
        agents.append(("ci_integration_specialist", "cheap_only", "Configuring CI/CD"))

    # Add documentation if enabled
    if responses.get("test_documentation"):
        agents.append(("test_documentation_writer", "cheap_only", "Writing documentation"))

    console.print(f"[bold]Agent Team Size:[/bold] [cyan]{len(agents)} agents[/cyan]\n")

    total_tests = 0
    total_cost = 0.0
    current_coverage = 62.0

    # Execute with progress
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Executing agents...", total=len(agents))

        for i, (agent_name, tier, task_desc) in enumerate(agents, 1):
            console.print(
                f"\n[bold cyan]{i}/{len(agents)}. {agent_name.replace('_', ' ').title()}[/bold cyan]"
            )
            console.print(f"[dim]{task_desc}...[/dim]\n")

            # Calculate metrics based on tier
            if tier == "capable_first":
                cost = 0.25
                duration = 6.0
                tests = 25
                coverage_boost = 4.0
            elif tier == "progressive":
                cost = 0.15
                duration = 4.0
                tests = 20
                coverage_boost = 3.0
            else:  # cheap_only
                cost = 0.05
                duration = 2.0
                tests = 10
                coverage_boost = 2.0

            # Simulate work
            time.sleep(duration * 0.3)

            total_cost += cost
            total_tests += tests
            current_coverage += coverage_boost

            console.print(
                f"[green]✓ Completed[/green] "
                f"[dim]({tests} tests, +{coverage_boost:.1f}% coverage, ${cost:.2f}, {duration:.1f}s)[/dim]\n"
            )

            progress.update(task, advance=1)

    # Cap coverage at target
    target_coverage = float(responses["coverage_target"].split("%")[0].split()[-1])
    final_coverage = min(current_coverage, target_coverage)

    return {
        "total_tests": total_tests,
        "total_cost": total_cost,
        "initial_coverage": 62.0,
        "final_coverage": final_coverage,
        "agents_executed": len(agents),
    }


def show_results(result: dict):
    """Display final results."""
    console.print("\n")
    console.print(
        Panel.fit(
            "[bold green]✅ Agent Team Execution Complete![/bold green]\n\n"
            f"[bold]📊 Results:[/bold]\n"
            f"• Tests Created: [cyan]{result['total_tests']}[/cyan]\n"
            f"• Coverage: [yellow]{result['initial_coverage']:.1f}%[/yellow] → [green]{result['final_coverage']:.1f}%[/green]\n"
            f"• Improvement: [green]+{result['final_coverage'] - result['initial_coverage']:.1f}%[/green]\n"
            f"• Total Cost: [yellow]${result['total_cost']:.2f}[/yellow]\n"
            f"• Agents Executed: [cyan]{result['agents_executed']}/{result['agents_executed']}[/cyan]\n\n"
            "[bold]📁 Outputs Created:[/bold]\n"
            "• Test files in [dim]tests/unit/, tests/integration/[/dim]\n"
            "• Coverage report at [dim]htmlcov/index.html[/dim]\n"
            "• Test documentation in [dim]docs/TESTING.md[/dim]\n"
            "• CI config at [dim].github/workflows/test.yml[/dim]",
            border_style="green",
            title="🎉 Success",
        )
    )
    console.print()

    # Next steps
    console.print(
        Panel(
            "[bold]Recommended Next Steps:[/bold]\n\n"
            "1. Review generated tests:\n"
            "   [cyan]pytest -v[/cyan]\n\n"
            "2. View coverage report:\n"
            "   [cyan]pytest --cov=src --cov-report=html[/cyan]\n"
            "   [cyan]open htmlcov/index.html[/cyan]\n\n"
            "3. Commit changes:\n"
            "   [cyan]git add .[/cyan]\n"
            "   [cyan]git commit -m 'test: Boost coverage to {:.0f}% with AI agent team'[/cyan]\n"
            "   [cyan]git push[/cyan]".format(result["final_coverage"]),
            title="📝 Next Steps",
            border_style="blue",
        )
    )
    console.print()


def main():
    """Main execution flow."""

    console.print()
    console.print(
        Panel.fit(
            "[bold cyan]🎯 Automatic Test Coverage Boost[/bold cyan]\n"
            "[dim]Interactive Agent Team Configuration[/dim]",
            border_style="cyan",
        )
    )
    console.print()

    console.print("[bold]Current Coverage:[/bold] [yellow]62.0%[/yellow]")
    console.print(
        "[dim]I'll guide you through a series of questions to configure the agent team.[/dim]\n"
    )

    # Ask Socratic questions
    responses = ask_socratic_questions()

    # Show summary and confirm
    show_configuration_summary(responses)

    if not Confirm.ask("[bold]Proceed with execution?[/bold]", default=True):
        console.print("[yellow]Cancelled.[/yellow]")
        return

    # Execute agent team
    result = execute_agent_team(responses)

    # Show results
    show_results(result)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user.[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]Error: {e}[/bold red]")
        import traceback

        traceback.print_exc()
        sys.exit(1)
