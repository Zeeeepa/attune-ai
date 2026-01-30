#!/usr/bin/env python3
"""Generate behavioral tests for refactored modules.

This script generates comprehensive behavioral tests for:
1. document_gen package (config, report_formatter)
2. cli_commands package (all 6 command modules)
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from empathy_os.workflows.autonomous_test_gen import AutonomousTestGenerator


def main():
    """Generate tests for all refactored modules."""

    print("=" * 70)
    print("GENERATING TESTS FOR REFACTORED MODULES")
    print("=" * 70)

    # Batch 12: document_gen modules
    print("\n📦 Batch 12: document_gen modules")
    print("-" * 70)

    doc_gen_modules = [
        {
            "file": "src/empathy_os/workflows/document_gen/config.py",
            "description": "Token costs and document generation step configuration"
        },
        {
            "file": "src/empathy_os/workflows/document_gen/report_formatter.py",
            "description": "Document generation report formatting"
        },
    ]

    doc_gen = AutonomousTestGenerator(
        agent_id="batch12",
        batch_num=12,
        modules=doc_gen_modules
    )

    print(f"Generating tests for {len(doc_gen_modules)} modules...")
    doc_result = doc_gen.generate_all()
    print(f"✅ Batch 12 complete: {doc_result['tests_generated']} tests generated")

    # Batch 13: cli_commands modules
    print("\n📦 Batch 13: cli_commands modules")
    print("-" * 70)

    cli_modules = [
        {
            "file": "src/empathy_os/meta_workflows/cli_commands/template_commands.py",
            "description": "CLI commands for template operations"
        },
        {
            "file": "src/empathy_os/meta_workflows/cli_commands/workflow_commands.py",
            "description": "CLI commands for workflow execution"
        },
        {
            "file": "src/empathy_os/meta_workflows/cli_commands/analytics_commands.py",
            "description": "CLI commands for analytics and execution history"
        },
        {
            "file": "src/empathy_os/meta_workflows/cli_commands/memory_commands.py",
            "description": "CLI commands for memory operations"
        },
        {
            "file": "src/empathy_os/meta_workflows/cli_commands/config_commands.py",
            "description": "CLI commands for configuration management"
        },
        {
            "file": "src/empathy_os/meta_workflows/cli_commands/agent_commands.py",
            "description": "CLI commands for agent creation"
        },
    ]

    cli_gen = AutonomousTestGenerator(
        agent_id="batch13",
        batch_num=13,
        modules=cli_modules
    )

    print(f"Generating tests for {len(cli_modules)} modules...")
    cli_result = cli_gen.generate_all()
    print(f"✅ Batch 13 complete: {cli_result['tests_generated']} tests generated")

    # Summary
    print("\n" + "=" * 70)
    print("TEST GENERATION COMPLETE")
    print("=" * 70)
    print(f"Batch 12 (document_gen): {doc_result['tests_generated']} tests")
    print(f"Batch 13 (cli_commands): {cli_result['tests_generated']} tests")
    print(f"Total: {doc_result['tests_generated'] + cli_result['tests_generated']} tests")
    print("\nTest files created in:")
    print("  - tests/behavioral/generated/batch12/")
    print("  - tests/behavioral/generated/batch13/")
    print("=" * 70)


if __name__ == "__main__":
    main()
