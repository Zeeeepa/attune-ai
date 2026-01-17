"""CLI commands for meta-workflow system.

Provides command-line interface for:
- Listing available workflow templates
- Running meta-workflows
- Viewing analytics and insights
- Managing execution history

Usage:
    empathy meta-workflow list-templates
    empathy meta-workflow run <template_id>
    empathy meta-workflow analytics [template_id]
    empathy meta-workflow list-runs
    empathy meta-workflow show <run_id>

Created: 2026-01-17
"""

from datetime import datetime, timedelta
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from empathy_os.meta_workflows import (
    MetaWorkflow,
    PatternLearner,
    TemplateRegistry,
    list_execution_results,
    load_execution_result,
)

# Create Typer app for meta-workflow commands
meta_workflow_app = typer.Typer(
    name="meta-workflow",
    help="Meta-workflow system for dynamic agent team generation",
    no_args_is_help=True,
)

console = Console()


# =============================================================================
# Template Commands
# =============================================================================


@meta_workflow_app.command("list-templates")
def list_templates(
    storage_dir: str = typer.Option(
        ".empathy/meta_workflows/templates",
        "--storage-dir",
        "-d",
        help="Templates storage directory",
    ),
):
    """List all available workflow templates.

    Shows template metadata including:
    - Template ID and name
    - Description
    - Estimated cost range
    - Number of questions and agent rules
    """
    try:
        registry = TemplateRegistry(storage_dir=storage_dir)
        template_ids = registry.list_templates()

        if not template_ids:
            console.print("[yellow]No templates found.[/yellow]")
            console.print(f"\nLooking in: {storage_dir}")
            console.print("\nCreate templates by running workflow wizard or")
            console.print("placing template JSON files in the templates directory.")
            return

        console.print(f"\n[bold]Available Templates[/bold] ({len(template_ids)}):\n")

        for template_id in template_ids:
            template = registry.load_template(template_id)

            if template:
                # Create info panel
                info_lines = [
                    f"[bold]{template.name}[/bold]",
                    f"[dim]{template.description}[/dim]",
                    "",
                    f"ID: {template.template_id}",
                    f"Version: {template.version}",
                    f"Author: {template.author}",
                    f"Tags: {', '.join(template.tags)}",
                    "",
                    f"Questions: {len(template.form_schema.questions)}",
                    f"Agent Rules: {len(template.agent_composition_rules)}",
                    "",
                    f"Est. Cost: ${template.estimated_cost_range[0]:.2f}-${template.estimated_cost_range[1]:.2f}",
                    f"Est. Duration: ~{template.estimated_duration_minutes} min",
                ]

                console.print(Panel("\n".join(info_lines), border_style="blue"))
                console.print()

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)


@meta_workflow_app.command("inspect")
def inspect_template(
    template_id: str = typer.Argument(..., help="Template ID to inspect"),
    storage_dir: str = typer.Option(
        ".empathy/meta_workflows/templates",
        "--storage-dir",
        "-d",
        help="Templates storage directory",
    ),
    show_rules: bool = typer.Option(
        False,
        "--show-rules",
        "-r",
        help="Show agent composition rules",
    ),
):
    """Inspect a specific template in detail.

    Shows comprehensive template information including:
    - Form questions and types
    - Agent composition rules (optional)
    - Configuration mappings
    """
    try:
        registry = TemplateRegistry(storage_dir=storage_dir)
        template = registry.load_template(template_id)

        if not template:
            console.print(f"[red]Template not found:[/red] {template_id}")
            raise typer.Exit(code=1)

        # Header
        console.print(f"\n[bold cyan]Template: {template.name}[/bold cyan]")
        console.print(f"[dim]{template.description}[/dim]\n")

        # Form Schema
        console.print("[bold]Form Questions:[/bold]")
        form_tree = Tree("📋 Questions")

        for i, question in enumerate(template.form_schema.questions, 1):
            question_text = f"[cyan]{question.text}[/cyan]"
            q_node = form_tree.add(f"{i}. {question_text}")
            q_node.add(f"ID: {question.id}")
            q_node.add(f"Type: {question.type.value}")
            if question.options:
                options_str = ", ".join(question.options[:3])
                if len(question.options) > 3:
                    options_str += f", ... ({len(question.options) - 3} more)"
                q_node.add(f"Options: {options_str}")
            if question.required:
                q_node.add("[yellow]Required[/yellow]")
            if question.default:
                q_node.add(f"Default: {question.default}")

        console.print(form_tree)

        # Agent Composition Rules (optional)
        if show_rules:
            console.print(f"\n[bold]Agent Composition Rules:[/bold] ({len(template.agent_composition_rules)})\n")

            for i, rule in enumerate(template.agent_composition_rules, 1):
                rule_lines = [
                    f"[bold cyan]{i}. {rule.role}[/bold cyan]",
                    f"   Base Template: {rule.base_template}",
                    f"   Tier Strategy: {rule.tier_strategy.value}",
                    f"   Tools: {', '.join(rule.tools) if rule.tools else 'None'}",
                ]

                if rule.required_responses:
                    rule_lines.append(f"   Required When: {rule.required_responses}")

                if rule.config_mapping:
                    rule_lines.append(f"   Config Mapping: {len(rule.config_mapping)} fields")

                console.print("\n".join(rule_lines))
                console.print()

        # Summary
        console.print("\n[bold]Summary:[/bold]")
        console.print(f"  Questions: {len(template.form_schema.questions)}")
        console.print(f"  Agent Rules: {len(template.agent_composition_rules)}")
        console.print(f"  Estimated Cost: ${template.estimated_cost_range[0]:.2f}-${template.estimated_cost_range[1]:.2f}")
        console.print()

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)


# =============================================================================
# Execution Commands
# =============================================================================


@meta_workflow_app.command("run")
def run_workflow(
    template_id: str = typer.Argument(..., help="Template ID to execute"),
    mock: bool = typer.Option(
        True,
        "--mock/--real",
        help="Use mock execution (for testing)",
    ),
    use_memory: bool = typer.Option(
        False,
        "--use-memory",
        "-m",
        help="Enable memory integration for enhanced analytics",
    ),
    user_id: str = typer.Option(
        "cli_user",
        "--user-id",
        "-u",
        help="User ID for memory integration",
    ),
):
    """Execute a meta-workflow from template.

    This will:
    1. Load the template
    2. Ask form questions interactively (via AskUserQuestion)
    3. Generate dynamic agent team
    4. Execute agents (mock or real)
    5. Save results (files + optional memory)
    6. Display summary
    """
    try:
        # Load template
        console.print(f"\n[bold]Loading template:[/bold] {template_id}")
        registry = TemplateRegistry()
        template = registry.load_template(template_id)

        if not template:
            console.print(f"[red]Template not found:[/red] {template_id}")
            raise typer.Exit(code=1)

        console.print(f"[green]✓[/green] {template.name}")

        # Setup memory if requested
        pattern_learner = None
        if use_memory:
            console.print("\n[bold]Initializing memory integration...[/bold]")
            from empathy_os.memory.unified import UnifiedMemory

            try:
                memory = UnifiedMemory(user_id=user_id)
                pattern_learner = PatternLearner(memory=memory)
                console.print("[green]✓[/green] Memory enabled")
            except Exception as e:
                console.print(f"[yellow]Warning:[/yellow] Memory initialization failed: {e}")
                console.print("[yellow]Continuing without memory integration[/yellow]")

        # Create workflow
        workflow = MetaWorkflow(
            template=template,
            pattern_learner=pattern_learner,
        )

        # Execute (will ask questions via AskUserQuestion)
        console.print("\n[bold]Executing workflow...[/bold]")
        console.print(f"Mode: {'Mock' if mock else 'Real'}")

        result = workflow.execute(mock_execution=mock)

        # Display summary
        console.print("\n[bold green]Execution Complete![/bold green]\n")

        summary_lines = [
            f"[bold]Run ID:[/bold] {result.run_id}",
            f"[bold]Status:[/bold] {'✅ Success' if result.success else '❌ Failed'}",
            "",
            f"[bold]Agents Created:[/bold] {len(result.agents_created)}",
            f"[bold]Agents Executed:[/bold] {len(result.agent_results)}",
            f"[bold]Total Cost:[/bold] ${result.total_cost:.2f}",
            f"[bold]Duration:[/bold] {result.total_duration:.1f}s",
        ]

        if result.error:
            summary_lines.append(f"\n[bold red]Error:[/bold red] {result.error}")

        console.print(Panel("\n".join(summary_lines), title="Execution Summary", border_style="green"))

        # Show agents
        console.print("\n[bold]Agents Executed:[/bold]\n")

        for agent_result in result.agent_results:
            status = "✅" if agent_result.success else "❌"
            console.print(
                f"  {status} [cyan]{agent_result.role}[/cyan] "
                f"(tier: {agent_result.tier_used}, cost: ${agent_result.cost:.2f})"
            )

        # Show where results saved
        console.print("\n[bold]Results saved to:[/bold]")
        console.print(f"  📁 Files: .empathy/meta_workflows/executions/{result.run_id}/")
        if use_memory and pattern_learner and pattern_learner.memory:
            console.print("  🧠 Memory: Long-term storage")

        console.print(f"\n[dim]View details: empathy meta-workflow show {result.run_id}[/dim]")
        console.print()

    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}")
        import traceback
        traceback.print_exc()
        raise typer.Exit(code=1)


# =============================================================================
# Analytics Commands
# =============================================================================


@meta_workflow_app.command("analytics")
def show_analytics(
    template_id: str | None = typer.Argument(
        None,
        help="Template ID to analyze (optional, all if not specified)",
    ),
    min_confidence: float = typer.Option(
        0.5,
        "--min-confidence",
        "-c",
        help="Minimum confidence threshold (0.0-1.0)",
    ),
    use_memory: bool = typer.Option(
        False,
        "--use-memory",
        "-m",
        help="Use memory-enhanced analytics",
    ),
):
    """Show pattern learning analytics and recommendations.

    Displays:
    - Execution statistics
    - Tier performance insights
    - Cost analysis
    - Recommendations
    """
    try:
        # Initialize pattern learner
        pattern_learner = PatternLearner()

        if use_memory:
            console.print("[bold]Initializing memory-enhanced analytics...[/bold]\n")
            from empathy_os.memory.unified import UnifiedMemory
            memory = UnifiedMemory(user_id="cli_analytics")
            pattern_learner = PatternLearner(memory=memory)

        # Generate report
        report = pattern_learner.generate_analytics_report(template_id=template_id)

        # Display summary
        summary = report["summary"]

        console.print("\n[bold cyan]Meta-Workflow Analytics Report[/bold cyan]")
        if template_id:
            console.print(f"[dim]Template: {template_id}[/dim]")
        console.print()

        summary_table = Table(show_header=False, box=None)
        summary_table.add_column("Metric", style="bold")
        summary_table.add_column("Value")

        summary_table.add_row("Total Runs", str(summary["total_runs"]))
        summary_table.add_row(
            "Successful",
            f"{summary['successful_runs']} ({summary['success_rate']:.0%})"
        )
        summary_table.add_row("Total Cost", f"${summary['total_cost']:.2f}")
        summary_table.add_row("Avg Cost/Run", f"${summary['avg_cost_per_run']:.2f}")
        summary_table.add_row("Total Agents", str(summary["total_agents_created"]))
        summary_table.add_row("Avg Agents/Run", f"{summary['avg_agents_per_run']:.1f}")

        console.print(Panel(summary_table, title="Summary", border_style="cyan"))

        # Recommendations
        recommendations = report.get("recommendations", [])
        if recommendations:
            console.print("\n[bold]Recommendations:[/bold]\n")
            for rec in recommendations:
                console.print(f"  {rec}")

        # Insights
        insights = report.get("insights", {})

        if insights.get("tier_performance"):
            console.print("\n[bold]Tier Performance:[/bold]\n")
            for insight in insights["tier_performance"][:5]:  # Top 5
                console.print(f"  • {insight['description']}")
                console.print(f"    [dim]Confidence: {insight['confidence']:.0%} (n={insight['sample_size']})[/dim]")

        if insights.get("cost_analysis"):
            console.print("\n[bold]Cost Analysis:[/bold]\n")
            for insight in insights["cost_analysis"]:
                console.print(f"  • {insight['description']}")

                # Tier breakdown
                breakdown = insight['data'].get('tier_breakdown', {})
                if breakdown:
                    console.print("\n  [dim]By Tier:[/dim]")
                    for tier, stats in breakdown.items():
                        console.print(
                            f"    {tier}: ${stats['avg']:.2f} avg "
                            f"(${stats['total']:.2f} total, {stats['count']} runs)"
                        )

        if insights.get("failure_analysis"):
            console.print("\n[bold yellow]Failure Analysis:[/bold yellow]\n")
            for insight in insights["failure_analysis"]:
                console.print(f"  ⚠️  {insight['description']}")

        console.print()

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)


# =============================================================================
# Execution History Commands
# =============================================================================


@meta_workflow_app.command("list-runs")
def list_runs(
    template_id: str | None = typer.Option(
        None,
        "--template",
        "-t",
        help="Filter by template ID",
    ),
    limit: int = typer.Option(
        10,
        "--limit",
        "-n",
        help="Maximum number of results",
    ),
):
    """List execution history.

    Shows recent workflow executions with:
    - Run ID and timestamp
    - Template name
    - Success status
    - Cost and duration
    """
    try:
        run_ids = list_execution_results()

        if not run_ids:
            console.print("[yellow]No execution results found.[/yellow]")
            return

        console.print(f"\n[bold]Recent Executions[/bold] (showing {min(limit, len(run_ids))} of {len(run_ids)}):\n")

        # Create table
        table = Table(show_header=True)
        table.add_column("Run ID", style="cyan")
        table.add_column("Template")
        table.add_column("Status")
        table.add_column("Cost", justify="right")
        table.add_column("Duration", justify="right")
        table.add_column("Timestamp")

        count = 0
        for run_id in run_ids[:limit]:
            try:
                result = load_execution_result(run_id)

                # Filter by template if specified
                if template_id and result.template_id != template_id:
                    continue

                status = "✅" if result.success else "❌"
                cost = f"${result.total_cost:.2f}"
                duration = f"{result.total_duration:.1f}s"

                # Parse timestamp
                try:
                    ts = datetime.fromisoformat(result.timestamp)
                    timestamp = ts.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    timestamp = result.timestamp[:16]

                table.add_row(
                    run_id,
                    result.template_id,
                    status,
                    cost,
                    duration,
                    timestamp,
                )

                count += 1

            except Exception as e:
                console.print(f"[yellow]Warning:[/yellow] Failed to load {run_id}: {e}")
                continue

        if count == 0:
            if template_id:
                console.print(f"[yellow]No executions found for template: {template_id}[/yellow]")
            else:
                console.print("[yellow]No valid execution results found.[/yellow]")
            return

        console.print(table)
        console.print("\n[dim]View details: empathy meta-workflow show <run_id>[/dim]\n")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)


@meta_workflow_app.command("show")
def show_execution(
    run_id: str = typer.Argument(..., help="Run ID to display"),
    format: str = typer.Option(
        "text",
        "--format",
        "-f",
        help="Output format (text or json)",
    ),
):
    """Show detailed execution report.

    Displays comprehensive information about a specific workflow execution:
    - Form responses
    - Agents created and executed
    - Cost breakdown
    - Success/failure details
    """
    try:
        result = load_execution_result(run_id)

        if format == "json":
            # JSON output
            print(result.to_json())
            return

        # Text format (default)
        console.print(f"\n[bold cyan]Execution Report: {run_id}[/bold cyan]\n")

        # Status
        status = "✅ Success" if result.success else "❌ Failed"
        console.print(f"[bold]Status:[/bold] {status}")
        console.print(f"[bold]Template:[/bold] {result.template_id}")
        console.print(f"[bold]Timestamp:[/bold] {result.timestamp}")

        if result.error:
            console.print(f"\n[bold red]Error:[/bold red] {result.error}\n")

        # Summary
        console.print("\n[bold]Summary:[/bold]")
        console.print(f"  Agents Created: {len(result.agents_created)}")
        console.print(f"  Agents Executed: {len(result.agent_results)}")
        console.print(f"  Total Cost: ${result.total_cost:.2f}")
        console.print(f"  Duration: {result.total_duration:.1f}s")

        # Form Responses
        console.print("\n[bold]Form Responses:[/bold]\n")
        for key, value in result.form_responses.responses.items():
            console.print(f"  [cyan]{key}:[/cyan] {value}")

        # Agents
        console.print("\n[bold]Agents Executed:[/bold]\n")
        for i, agent_result in enumerate(result.agent_results, 1):
            status_emoji = "✅" if agent_result.success else "❌"
            console.print(f"  {i}. {status_emoji} [cyan]{agent_result.role}[/cyan]")
            console.print(f"     Tier: {agent_result.tier_used}")
            console.print(f"     Cost: ${agent_result.cost:.2f}")
            console.print(f"     Duration: {agent_result.duration:.1f}s")
            if agent_result.error:
                console.print(f"     [red]Error: {agent_result.error}[/red]")
            console.print()

        # Cost breakdown
        console.print("[bold]Cost Breakdown by Tier:[/bold]\n")
        tier_costs = {}
        for agent_result in result.agent_results:
            tier = agent_result.tier_used
            tier_costs[tier] = tier_costs.get(tier, 0.0) + agent_result.cost

        for tier, cost in sorted(tier_costs.items()):
            console.print(f"  {tier}: ${cost:.2f}")

        console.print()

    except FileNotFoundError:
        console.print(f"[red]Execution not found:[/red] {run_id}")
        console.print("\n[dim]List available runs: empathy meta-workflow list-runs[/dim]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)


# =============================================================================
# Maintenance Commands
# =============================================================================


@meta_workflow_app.command("cleanup")
def cleanup_executions(
    older_than_days: int = typer.Option(
        30,
        "--older-than",
        "-d",
        help="Delete executions older than N days",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what would be deleted without deleting",
    ),
    template_id: str | None = typer.Option(
        None,
        "--template",
        "-t",
        help="Filter by template ID",
    ),
):
    """Clean up old execution results.

    Deletes execution directories older than the specified number of days.
    Use --dry-run to preview what would be deleted.
    """
    try:
        cutoff_date = datetime.now() - timedelta(days=older_than_days)

        run_ids = list_execution_results()

        if not run_ids:
            console.print("[yellow]No execution results found.[/yellow]")
            return

        to_delete = []

        for run_id in run_ids:
            try:
                result = load_execution_result(run_id)

                # Filter by template if specified
                if template_id and result.template_id != template_id:
                    continue

                # Parse timestamp
                ts = datetime.fromisoformat(result.timestamp)

                if ts < cutoff_date:
                    to_delete.append((run_id, result, ts))

            except Exception as e:
                console.print(f"[yellow]Warning:[/yellow] Failed to load {run_id}: {e}")
                continue

        if not to_delete:
            console.print(
                f"[green]No executions older than {older_than_days} days found.[/green]"
            )
            return

        # Show what will be deleted
        console.print(f"\n[bold]Executions to delete:[/bold] ({len(to_delete)})\n")

        table = Table(show_header=True)
        table.add_column("Run ID", style="cyan")
        table.add_column("Template")
        table.add_column("Age (days)", justify="right")
        table.add_column("Cost", justify="right")

        total_cost_saved = 0.0
        for run_id, result, ts in to_delete:
            age_days = (datetime.now() - ts).days
            table.add_row(
                run_id,
                result.template_id,
                str(age_days),
                f"${result.total_cost:.2f}",
            )
            total_cost_saved += result.total_cost

        console.print(table)
        console.print(f"\nTotal cost represented: ${total_cost_saved:.2f}")

        if dry_run:
            console.print("\n[yellow]DRY RUN - No files deleted[/yellow]")
            console.print(f"Run without --dry-run to delete {len(to_delete)} executions")
            return

        # Confirm deletion
        if not typer.confirm(f"\nDelete {len(to_delete)} execution(s)?"):
            console.print("[yellow]Cancelled[/yellow]")
            return

        # Delete
        import shutil
        deleted = 0
        for run_id, _, _ in to_delete:
            try:
                run_dir = Path.home() / ".empathy" / "meta_workflows" / "executions" / run_id
                if run_dir.exists():
                    shutil.rmtree(run_dir)
                    deleted += 1
            except Exception as e:
                console.print(f"[red]Failed to delete {run_id}:[/red] {e}")

        console.print(f"\n[green]✓ Deleted {deleted} execution(s)[/green]\n")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)


# =============================================================================
# Memory Search Commands
# =============================================================================


@meta_workflow_app.command("search-memory")
def search_memory(
    query: str = typer.Argument(..., help="Search query for patterns"),
    pattern_type: str | None = typer.Option(
        None,
        "--type",
        "-t",
        help="Filter by pattern type (e.g., 'meta_workflow_execution')",
    ),
    limit: int = typer.Option(
        10,
        "--limit",
        "-l",
        help="Maximum number of results to return",
    ),
    user_id: str = typer.Option(
        "cli_user",
        "--user-id",
        "-u",
        help="User ID for memory access",
    ),
):
    """Search memory for patterns using keyword matching.

    Searches long-term memory for patterns matching the query.
    Uses relevance scoring: exact phrase (10 pts), keyword in content (2 pts),
    keyword in metadata (1 pt).

    Examples:
        empathy meta-workflow search-memory "successful workflow"
        empathy meta-workflow search-memory "test coverage" --type meta_workflow_execution
        empathy meta-workflow search-memory "error" --limit 20
    """
    try:
        from empathy_os.memory.unified import UnifiedMemory

        console.print(f"\n[bold]Searching memory for:[/bold] '{query}'")
        if pattern_type:
            console.print(f"[dim]Pattern type: {pattern_type}[/dim]")
        console.print()

        # Initialize memory
        memory = UnifiedMemory(user_id=user_id)

        # Search
        results = memory.search_patterns(
            query=query,
            pattern_type=pattern_type,
            limit=limit,
        )

        if not results:
            console.print("[yellow]No matching patterns found.[/yellow]\n")
            return

        # Display results
        console.print(f"[green]Found {len(results)} matching pattern(s):[/green]\n")

        for i, pattern in enumerate(results, 1):
            panel = Panel(
                f"[bold]Pattern ID:[/bold] {pattern.get('pattern_id', 'N/A')}\n"
                f"[bold]Type:[/bold] {pattern.get('pattern_type', 'N/A')}\n"
                f"[bold]Classification:[/bold] {pattern.get('classification', 'N/A')}\n\n"
                f"[bold]Content:[/bold]\n{str(pattern.get('content', 'N/A'))[:200]}...\n\n"
                f"[bold]Metadata:[/bold] {pattern.get('metadata', {})}",
                title=f"Result {i}/{len(results)}",
                border_style="blue",
            )
            console.print(panel)
            console.print()

    except ImportError:
        console.print(
            "[red]Error:[/red] UnifiedMemory not available. "
            "Ensure memory module is installed."
        )
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)


# =============================================================================
# Session Context Commands
# =============================================================================


@meta_workflow_app.command("session-stats")
def show_session_stats(
    session_id: str | None = typer.Option(
        None,
        "--session-id",
        "-s",
        help="Session ID (optional, creates new if not specified)",
    ),
    user_id: str = typer.Option(
        "cli_user",
        "--user-id",
        "-u",
        help="User ID for session",
    ),
):
    """Show session context statistics.

    Displays information about user's session including:
    - Recent form choices
    - Templates used
    - Choice counts

    Examples:
        empathy meta-workflow session-stats
        empathy meta-workflow session-stats --session-id sess_123
    """
    try:
        from empathy_os.memory.unified import UnifiedMemory
        from empathy_os.meta_workflows.session_context import SessionContext

        # Initialize memory and session
        memory = UnifiedMemory(user_id=user_id)
        session = SessionContext(
            memory=memory,
            session_id=session_id,
        )

        console.print("\n[bold]Session Statistics[/bold]")
        console.print(f"[dim]Session ID: {session.session_id}[/dim]")
        console.print(f"[dim]User ID: {session.user_id}[/dim]\n")

        # Get stats
        stats = session.get_session_stats()

        # Display
        table = Table(show_header=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Value")

        table.add_row("Total Choices", str(stats.get("choice_count", 0)))
        table.add_row("Templates Used", str(len(stats.get("templates_used", []))))
        table.add_row(
            "Most Recent Choice",
            stats.get("most_recent_choice_timestamp", "N/A")
        )

        console.print(table)
        console.print()

        # Show templates used
        templates = stats.get("templates_used", [])
        if templates:
            console.print("[bold]Templates Used:[/bold]")
            for template_id in templates:
                console.print(f"  • {template_id}")
            console.print()

    except ImportError:
        console.print(
            "[red]Error:[/red] Session context not available. "
            "Ensure memory and session modules are installed."
        )
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)


@meta_workflow_app.command("suggest-defaults")
def suggest_defaults_cmd(
    template_id: str = typer.Argument(..., help="Template ID to get defaults for"),
    session_id: str | None = typer.Option(
        None,
        "--session-id",
        "-s",
        help="Session ID (optional)",
    ),
    user_id: str = typer.Option(
        "cli_user",
        "--user-id",
        "-u",
        help="User ID for session",
    ),
):
    """Get suggested default values based on session history.

    Analyzes recent choices for the specified template and suggests
    intelligent defaults for the next run.

    Examples:
        empathy meta-workflow suggest-defaults test_creation_management_workflow
        empathy meta-workflow suggest-defaults python_package_publish --session-id sess_123
    """
    try:
        from empathy_os.memory.unified import UnifiedMemory
        from empathy_os.meta_workflows.session_context import SessionContext

        # Initialize
        memory = UnifiedMemory(user_id=user_id)
        session = SessionContext(memory=memory, session_id=session_id)

        # Load template
        registry = TemplateRegistry()
        template = registry.load_template(template_id)
        if not template:
            console.print(f"[red]Error:[/red] Template not found: {template_id}")
            raise typer.Exit(code=1)

        console.print(f"\n[bold]Suggested Defaults for:[/bold] {template.name}")
        console.print(f"[dim]Template ID: {template_id}[/dim]\n")

        # Get suggestions
        defaults = session.suggest_defaults(
            template_id=template_id,
            form_schema=template.form_schema,
        )

        if not defaults:
            console.print("[yellow]No suggestions available (no recent history).[/yellow]\n")
            return

        # Display
        console.print(f"[green]Found {len(defaults)} suggested default(s):[/green]\n")

        table = Table(show_header=True)
        table.add_column("Question ID", style="cyan")
        table.add_column("Suggested Value")

        for question_id, value in defaults.items():
            # Find the question to get the display text
            question = next(
                (q for q in template.form_schema.questions if q.id == question_id),
                None
            )
            question_text = question.text if question else question_id

            value_str = str(value)
            if isinstance(value, list):
                value_str = ", ".join(str(v) for v in value)

            table.add_row(question_text, value_str)

        console.print(table)
        console.print(
            f"\n[dim]Use these defaults by running:[/dim]\n"
            f"  empathy meta-workflow run {template_id} --use-defaults\n"
        )

    except ImportError:
        console.print(
            "[red]Error:[/red] Session context not available. "
            "Ensure memory and session modules are installed."
        )
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    meta_workflow_app()
