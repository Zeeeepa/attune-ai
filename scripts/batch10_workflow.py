#!/usr/bin/env python3
"""Master workflow script for batch 10 test generation and validation.

This script orchestrates the complete workflow:
1. Show batch 10 modules
2. Generate test templates
3. Validate tests
4. Check coverage progress

Usage:
    python scripts/batch10_workflow.py           # Interactive workflow
    python scripts/batch10_workflow.py --all     # Run all steps
    python scripts/batch10_workflow.py --step 1  # Run specific step
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Optional


class Batch10Workflow:
    """Orchestrator for batch 10 testing workflow."""

    def __init__(self, project_root: Path):
        """Initialize workflow.

        Args:
            project_root: Root directory of project
        """
        self.project_root = project_root
        self.scripts_dir = project_root / "scripts"
        self.test_dir = project_root / "tests" / "behavioral" / "generated" / "batch10"

    def print_header(self, title: str):
        """Print section header.

        Args:
            title: Section title
        """
        print()
        print("=" * 70)
        print(title.center(70))
        print("=" * 70)
        print()

    def run_script(self, script_name: str, args: Optional[list] = None) -> int:
        """Run a script and return exit code.

        Args:
            script_name: Name of script to run
            args: Optional arguments to pass

        Returns:
            Exit code from script
        """
        script_path = self.scripts_dir / script_name
        cmd = [sys.executable, str(script_path)]

        if args:
            cmd.extend(args)

        result = subprocess.run(cmd, cwd=self.project_root)
        return result.returncode

    def step_1_show_modules(self) -> int:
        """Step 1: Show batch 10 modules.

        Returns:
            Exit code
        """
        self.print_header("STEP 1: View Batch 10 Modules")

        print("This step shows all modules in batch 10 with uncovered line counts.")
        print()

        return self.run_script("show_batch10_modules.py")

    def step_2_generate_tests(self) -> int:
        """Step 2: Generate test templates.

        Returns:
            Exit code
        """
        self.print_header("STEP 2: Generate Test Templates")

        print("This step generates behavioral test templates for all batch 10 modules.")
        print()

        # Check if tests already exist
        if self.test_dir.exists():
            existing_tests = list(self.test_dir.glob("test_*_behavior.py"))
            if existing_tests:
                print(f"⚠️  Warning: {len(existing_tests)} test files already exist")
                response = input("Regenerate tests? (y/N): ")
                if response.lower() != "y":
                    print("Skipping test generation")
                    return 0

        return self.run_script("generate_batch10_tests.py")

    def step_3_validate_tests(self, strict: bool = False) -> int:
        """Step 3: Validate test files.

        Args:
            strict: If True, apply strict validation

        Returns:
            Exit code
        """
        self.print_header("STEP 3: Validate Test Files")

        print("This step validates test files for completeness and quality.")
        print()

        args = ["--strict"] if strict else []
        return self.run_script("validate_batch10_tests.py", args)

    def step_4_check_progress(self, detailed: bool = False) -> int:
        """Step 4: Check coverage progress.

        Args:
            detailed: If True, show detailed coverage

        Returns:
            Exit code
        """
        self.print_header("STEP 4: Check Coverage Progress")

        print("This step runs tests and reports coverage progress.")
        print()

        args = ["--detailed"] if detailed else []
        return self.run_script("check_batch10_progress.py", args)

    def run_interactive(self):
        """Run interactive workflow."""
        self.print_header("Batch 10 Testing Workflow")

        print("This workflow guides you through generating and validating batch 10 tests.")
        print()
        print("Steps:")
        print("  1. View batch 10 modules")
        print("  2. Generate test templates")
        print("  3. Validate test files")
        print("  4. Check coverage progress")
        print()

        while True:
            print("=" * 70)
            print("Select an option:")
            print()
            print("  1 - View batch 10 modules")
            print("  2 - Generate test templates")
            print("  3 - Validate test files")
            print("  4 - Check coverage progress")
            print("  5 - Run all steps")
            print("  q - Quit")
            print()

            choice = input("Enter choice: ").strip().lower()

            if choice == "q":
                print("\nGoodbye!")
                break
            elif choice == "1":
                self.step_1_show_modules()
            elif choice == "2":
                self.step_2_generate_tests()
            elif choice == "3":
                strict = input("Use strict validation? (y/N): ").lower() == "y"
                self.step_3_validate_tests(strict=strict)
            elif choice == "4":
                detailed = input("Show detailed coverage? (y/N): ").lower() == "y"
                self.step_4_check_progress(detailed=detailed)
            elif choice == "5":
                self.run_all_steps()
            else:
                print("Invalid choice. Please try again.")

            input("\nPress Enter to continue...")

    def run_all_steps(self) -> int:
        """Run all workflow steps.

        Returns:
            Exit code (0 if all succeed)
        """
        steps = [
            ("View Modules", lambda: self.step_1_show_modules()),
            ("Generate Tests", lambda: self.step_2_generate_tests()),
            ("Validate Tests", lambda: self.step_3_validate_tests()),
            ("Check Progress", lambda: self.step_4_check_progress()),
        ]

        for step_name, step_func in steps:
            print()
            print(f"Running: {step_name}")
            print("-" * 70)

            result = step_func()

            if result != 0:
                print(f"\n❌ {step_name} failed with exit code {result}")
                print("Stopping workflow")
                return result

            print(f"\n✅ {step_name} completed")

        self.print_header("Workflow Complete")
        print("✅ All steps completed successfully!")
        print()
        print("Next Steps:")
        print("  1. Review generated tests in tests/behavioral/generated/batch10/")
        print("  2. Complete TODO items in each test file")
        print("  3. Run tests: pytest tests/behavioral/generated/batch10/ -v")
        print("  4. Check progress: python scripts/check_batch10_progress.py")
        print()

        return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Batch 10 testing workflow orchestrator")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all workflow steps automatically",
    )
    parser.add_argument(
        "--step",
        type=int,
        choices=[1, 2, 3, 4],
        help="Run specific step (1-4)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Use strict validation (for step 3)",
    )
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Show detailed coverage (for step 4)",
    )
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    workflow = Batch10Workflow(project_root)

    if args.all:
        # Run all steps
        return workflow.run_all_steps()
    elif args.step:
        # Run specific step
        if args.step == 1:
            return workflow.step_1_show_modules()
        elif args.step == 2:
            return workflow.step_2_generate_tests()
        elif args.step == 3:
            return workflow.step_3_validate_tests(strict=args.strict)
        elif args.step == 4:
            return workflow.step_4_check_progress(detailed=args.detailed)
    else:
        # Interactive mode
        workflow.run_interactive()
        return 0


if __name__ == "__main__":
    sys.exit(main())
