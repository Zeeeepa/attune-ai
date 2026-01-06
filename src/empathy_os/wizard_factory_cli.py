"""Wizard Factory CLI integration for Empathy Framework.

Provides wizard-factory commands integrated into the main empathy CLI:
- empathy wizard-factory create
- empathy wizard-factory list-patterns
- empathy wizard-factory generate-tests
- empathy wizard-factory analyze

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import subprocess
import sys


def cmd_wizard_factory_create(args):
    """Create a new wizard using scaffolding."""
    # Build command
    cmd = ["python", "-m", "scaffolding", "create", args.name]

    if args.domain:
        cmd.extend(["--domain", args.domain])

    if args.type:
        cmd.extend(["--type", args.type])

    if args.methodology:
        cmd.extend(["--methodology", args.methodology])

    if args.patterns:
        cmd.extend(["--patterns", args.patterns])

    if args.interactive:
        cmd.append("--interactive")

    # Run scaffolding
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


def cmd_wizard_factory_list_patterns(args):
    """List available patterns."""
    result = subprocess.run(["python", "-m", "scaffolding", "list-patterns"])
    sys.exit(result.returncode)


def cmd_wizard_factory_generate_tests(args):
    """Generate tests for a wizard."""
    cmd = ["python", "-m", "test_generator", "generate", args.wizard_id]

    if args.patterns:
        cmd.extend(["--patterns", args.patterns])

    if args.output:
        cmd.extend(["--output", args.output])

    result = subprocess.run(cmd)
    sys.exit(result.returncode)


def cmd_wizard_factory_analyze(args):
    """Analyze wizard risk."""
    cmd = ["python", "-m", "test_generator", "analyze", args.wizard_id]

    if args.patterns:
        cmd.extend(["--patterns", args.patterns])

    if args.json:
        cmd.append("--json")

    result = subprocess.run(cmd)
    sys.exit(result.returncode)


def add_wizard_factory_commands(subparsers):
    """Add wizard-factory commands to main CLI.

    Args:
        subparsers: ArgumentParser subparsers object
    """
    # Main wizard-factory command
    parser_wf = subparsers.add_parser(
        "wizard-factory",
        help="Wizard Factory - create wizards 12x faster",
    )
    wf_subparsers = parser_wf.add_subparsers(dest="wizard_factory_command")

    # wizard-factory create
    parser_wf_create = wf_subparsers.add_parser(
        "create",
        help="Create a new wizard",
    )
    parser_wf_create.add_argument("name", help="Wizard name (snake_case)")
    parser_wf_create.add_argument(
        "--domain",
        "-d",
        help="Domain (healthcare, finance, software, legal, etc.)",
    )
    parser_wf_create.add_argument(
        "--type",
        "-t",
        choices=["domain", "coach", "ai"],
        default="domain",
        help="Wizard type (default: domain)",
    )
    parser_wf_create.add_argument(
        "--methodology",
        "-m",
        choices=["pattern", "tdd"],
        default="pattern",
        help="Methodology (pattern-compose or tdd-first, default: pattern)",
    )
    parser_wf_create.add_argument(
        "--patterns",
        "-p",
        help="Comma-separated pattern IDs (e.g. linear_flow,approval)",
    )
    parser_wf_create.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Interactive pattern selection",
    )
    parser_wf_create.set_defaults(func=cmd_wizard_factory_create)

    # wizard-factory list-patterns
    parser_wf_list = wf_subparsers.add_parser(
        "list-patterns",
        help="List available patterns",
    )
    parser_wf_list.set_defaults(func=cmd_wizard_factory_list_patterns)

    # wizard-factory generate-tests
    parser_wf_gen = wf_subparsers.add_parser(
        "generate-tests",
        help="Generate tests for a wizard",
    )
    parser_wf_gen.add_argument("wizard_id", help="Wizard ID")
    parser_wf_gen.add_argument(
        "--patterns",
        "-p",
        required=True,
        help="Comma-separated pattern IDs",
    )
    parser_wf_gen.add_argument(
        "--output",
        "-o",
        help="Output directory for tests",
    )
    parser_wf_gen.set_defaults(func=cmd_wizard_factory_generate_tests)

    # wizard-factory analyze
    parser_wf_analyze = wf_subparsers.add_parser(
        "analyze",
        help="Analyze wizard risk and get coverage recommendations",
    )
    parser_wf_analyze.add_argument("wizard_id", help="Wizard ID")
    parser_wf_analyze.add_argument(
        "--patterns",
        "-p",
        required=True,
        help="Comma-separated pattern IDs",
    )
    parser_wf_analyze.add_argument(
        "--json",
        action="store_true",
        help="Output JSON format",
    )
    parser_wf_analyze.set_defaults(func=cmd_wizard_factory_analyze)
