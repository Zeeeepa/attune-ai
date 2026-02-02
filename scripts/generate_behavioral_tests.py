#!/usr/bin/env python3
"""Batch test generator for behavioral tests.

Analyzes Python modules and generates behavioral test templates automatically.
Helps achieve 99.9% coverage systematically.

Usage:
    python scripts/generate_behavioral_tests.py --module src/attune/memory/short_term.py
    python scripts/generate_behavioral_tests.py --batch --top 50
    python scripts/generate_behavioral_tests.py --report

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

import argparse
import ast
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class FunctionInfo:
    """Information about a function to test."""

    name: str
    is_async: bool
    args: list[str]
    returns: str | None
    docstring: str | None
    line_number: int


@dataclass
class ClassInfo:
    """Information about a class to test."""

    name: str
    methods: list[FunctionInfo]
    is_abstract: bool
    bases: list[str]
    line_number: int


@dataclass
class ModuleInfo:
    """Information about a module to test."""

    file_path: str
    classes: list[ClassInfo]
    functions: list[FunctionInfo]
    imports: list[str]
    total_lines: int


class ModuleAnalyzer(ast.NodeVisitor):
    """Analyze Python module to extract testable elements."""

    def __init__(self, source_code: str):
        self.source_code = source_code
        self.classes: list[ClassInfo] = []
        self.functions: list[FunctionInfo] = []
        self.imports: list[str] = []
        self.current_class: str | None = None

    def visit_ClassDef(self, node: ast.ClassDef):
        """Extract class information."""
        methods = []
        is_abstract = any(
            isinstance(base, ast.Name) and base.id in ("ABC", "ABCMeta") for base in node.bases
        )

        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_info = self._extract_function_info(item)
                methods.append(method_info)

        class_info = ClassInfo(
            name=node.name,
            methods=methods,
            is_abstract=is_abstract,
            bases=[self._get_base_name(base) for base in node.bases],
            line_number=node.lineno,
        )
        self.classes.append(class_info)

        # Continue visiting
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Extract function information."""
        # Only top-level functions (not methods)
        if not self.current_class:
            func_info = self._extract_function_info(node)
            self.functions.append(func_info)

        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Extract async function information."""
        if not self.current_class:
            func_info = self._extract_function_info(node, is_async=True)
            self.functions.append(func_info)

        self.generic_visit(node)

    def visit_Import(self, node: ast.Import):
        """Extract imports."""
        for alias in node.names:
            self.imports.append(alias.name)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Extract from-imports."""
        if node.module:
            self.imports.append(node.module)

    def _extract_function_info(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef, is_async: bool = False
    ) -> FunctionInfo:
        """Extract information from function node."""
        args = [arg.arg for arg in node.args.args if arg.arg != "self"]

        # Get return type if annotated
        returns = None
        if node.returns:
            returns = ast.unparse(node.returns)

        # Get docstring
        docstring = ast.get_docstring(node)

        is_async = isinstance(node, ast.AsyncFunctionDef) or is_async

        return FunctionInfo(
            name=node.name,
            is_async=is_async,
            args=args,
            returns=returns,
            docstring=docstring,
            line_number=node.lineno,
        )

    def _get_base_name(self, base: ast.expr) -> str:
        """Get base class name."""
        if isinstance(base, ast.Name):
            return base.id
        return ast.unparse(base)


def analyze_module(file_path: Path) -> ModuleInfo:
    """Analyze a Python module and extract testable elements."""
    source_code = file_path.read_text()
    tree = ast.parse(source_code)

    analyzer = ModuleAnalyzer(source_code)
    analyzer.visit(tree)

    return ModuleInfo(
        file_path=str(file_path),
        classes=analyzer.classes,
        functions=analyzer.functions,
        imports=analyzer.imports,
        total_lines=len(source_code.splitlines()),
    )


def generate_test_template(module_info: ModuleInfo, output_path: Path) -> str:
    """Generate behavioral test template for a module."""
    module_name = Path(module_info.file_path).stem
    import_path = module_info.file_path.replace("src/", "").replace(".py", "").replace("/", ".")

    lines = []
    lines.append(f'"""Behavioral tests for {module_name}.py - AUTO-GENERATED TEMPLATE.')
    lines.append("")
    lines.append("INSTRUCTIONS:")
    lines.append("1. Review and customize the tests below")
    lines.append("2. Add mock data and assertions")
    lines.append("3. Test both success and error paths")
    lines.append("4. Run: pytest {output_path} --cov={module_info.file_path} -v")
    lines.append("")
    lines.append("Copyright 2026 Smart-AI-Memory")
    lines.append("Licensed under Apache 2.0")
    lines.append('"""')
    lines.append("")
    lines.append("import pytest")
    lines.append("from unittest.mock import Mock, AsyncMock, patch, MagicMock")
    lines.append("")

    # Add imports for the module being tested
    lines.append(f"# Import from module under test")
    if module_info.classes:
        class_names = ", ".join(c.name for c in module_info.classes[:5])
        lines.append(f"from {import_path} import {class_names}")
    if module_info.functions:
        func_names = ", ".join(f.name for f in module_info.functions[:5])
        lines.append(f"from {import_path} import {func_names}")
    lines.append("")
    lines.append("")

    # Generate tests for each class
    for class_info in module_info.classes:
        lines.append(f"class Test{class_info.name}:")
        lines.append(f'    """Behavioral tests for {class_info.name} class."""')
        lines.append("")

        # Generate test for initialization
        if not class_info.is_abstract:
            lines.append(f"    def test_{class_info.name.lower()}_initializes(self):")
            lines.append(f'        """Test {class_info.name} can be initialized."""')
            lines.append(f"        # TODO: Add proper initialization params")
            lines.append(f"        # obj = {class_info.name}(...)")
            lines.append(f"        # assert obj is not None")
            lines.append(f"        pass  # Remove after implementing")
            lines.append("")

        # Generate tests for each method
        for method in class_info.methods[:10]:  # Limit to first 10 methods
            if method.name.startswith("_"):
                continue  # Skip private methods in template

            test_name = f"test_{method.name.lower()}"
            decorator = "    @pytest.mark.asyncio" if method.is_async else ""

            if decorator:
                lines.append(decorator)

            async_prefix = "async " if method.is_async else ""
            lines.append(f"    {async_prefix}def {test_name}(self):")
            lines.append(f'        """Test {class_info.name}.{method.name}() behavior."""')
            lines.append(f"        # TODO: Implement test for {method.name}")
            lines.append(f"        # obj = {class_info.name}(...)")

            if method.is_async:
                lines.append(
                    f"        # result = await obj.{method.name}({', '.join(method.args)})"
                )
            else:
                lines.append(f"        # result = obj.{method.name}({', '.join(method.args)})")

            lines.append(f"        # assert result == expected")
            lines.append(f"        pass  # Remove after implementing")
            lines.append("")

        lines.append("")

    # Generate tests for module-level functions
    if module_info.functions:
        lines.append("class TestModuleFunctions:")
        lines.append('    """Tests for module-level functions."""')
        lines.append("")

        for func in module_info.functions[:10]:
            if func.name.startswith("_"):
                continue

            test_name = f"test_{func.name.lower()}"
            decorator = "    @pytest.mark.asyncio" if func.is_async else ""

            if decorator:
                lines.append(decorator)

            async_prefix = "async " if func.is_async else ""
            lines.append(f"    {async_prefix}def {test_name}(self):")
            lines.append(f'        """Test {func.name}() function."""')
            lines.append(f"        # TODO: Implement test")

            if func.is_async:
                lines.append(f"        # result = await {func.name}({', '.join(func.args)})")
            else:
                lines.append(f"        # result = {func.name}({', '.join(func.args)})")

            lines.append(f"        # assert result == expected")
            lines.append(f"        pass  # Remove after implementing")
            lines.append("")

    # Add footer with instructions
    lines.append("")
    lines.append("# ========================================================================")
    lines.append("# NEXT STEPS:")
    lines.append("# 1. Replace 'pass' with actual test logic")
    lines.append("# 2. Add proper test data and mocks")
    lines.append("# 3. Test both success and failure cases")
    lines.append("# 4. Run: pytest tests/behavioral/... --cov=src/... -v")
    lines.append("# ========================================================================")

    return "\n".join(lines)


def get_coverage_report() -> dict[str, float]:
    """Get current coverage by module."""
    try:
        # Run coverage report and parse JSON
        subprocess.run(
            ["coverage", "json", "-o", "/tmp/coverage_temp.json"],
            capture_output=True,
            check=True,
        )

        with open("/tmp/coverage_temp.json") as f:
            data = json.load(f)

        coverage_by_file = {}
        for file_path, info in data.get("files", {}).items():
            if file_path.startswith("src/"):
                coverage_pct = info["summary"]["percent_covered"]
                coverage_by_file[file_path] = coverage_pct

        return coverage_by_file

    except Exception as e:
        print(f"Warning: Could not get coverage report: {e}")
        return {}


def find_low_coverage_modules(top_n: int = 50) -> list[tuple[str, float]]:
    """Find modules with lowest coverage."""
    coverage = get_coverage_report()

    # Sort by coverage (lowest first)
    sorted_modules = sorted(coverage.items(), key=lambda x: x[1])

    return sorted_modules[:top_n]


def batch_generate_tests(num_modules: int = 50, min_lines: int = 50):
    """Batch generate test templates for low-coverage modules."""
    print(f"Finding {num_modules} modules with lowest coverage...")

    low_coverage = find_low_coverage_modules(num_modules)

    if not low_coverage:
        print("No coverage data found. Run 'coverage run -m pytest' first.")
        return

    output_dir = Path("tests/behavioral/generated")
    output_dir.mkdir(exist_ok=True, parents=True)

    generated = []

    for file_path, coverage_pct in low_coverage:
        src_path = Path(file_path)

        if not src_path.exists():
            continue

        # Skip very small files
        if src_path.stat().st_size < min_lines * 40:  # Rough estimate
            continue

        print(f"\nAnalyzing: {file_path} (coverage: {coverage_pct:.1f}%)")

        try:
            module_info = analyze_module(src_path)

            # Generate output filename
            test_filename = f"test_{src_path.stem}_behavioral.py"
            output_path = output_dir / test_filename

            # Generate template
            template = generate_test_template(module_info, output_path)

            # Write file
            output_path.write_text(template)

            generated.append((file_path, str(output_path), coverage_pct))

            print(f"  ✅ Generated: {output_path}")
            print(f"     Classes: {len(module_info.classes)}")
            print(f"     Functions: {len(module_info.functions)}")

        except Exception as e:
            print(f"  ❌ Error: {e}")

    # Print summary
    print("\n" + "=" * 80)
    print("BATCH GENERATION COMPLETE")
    print("=" * 80)
    print(f"Generated {len(generated)} test files")
    print(f"\nLocation: {output_dir}")
    print("\nNext steps:")
    print("1. Review generated templates in tests/behavioral/generated/")
    print("2. Fill in TODO sections with actual test logic")
    print("3. Run: pytest tests/behavioral/generated/ -v")
    print("4. Check coverage: coverage run -m pytest tests/behavioral/generated/ -n 0")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Generate behavioral test templates")

    parser.add_argument(
        "--module", help="Generate test for specific module (e.g., src/attune/config.py)"
    )
    parser.add_argument(
        "--batch", action="store_true", help="Batch generate tests for low-coverage modules"
    )
    parser.add_argument(
        "--top", type=int, default=50, help="Number of modules to generate in batch (default: 50)"
    )
    parser.add_argument("--report", action="store_true", help="Show coverage report")

    args = parser.parse_args()

    if args.report:
        coverage = get_coverage_report()
        print("Coverage by module (sorted by coverage):")
        for file_path, pct in sorted(coverage.items(), key=lambda x: x[1])[:20]:
            print(f"  {pct:>6.2f}%  {file_path}")

    elif args.batch:
        batch_generate_tests(num_modules=args.top)

    elif args.module:
        module_path = Path(args.module)
        if not module_path.exists():
            print(f"Error: {module_path} not found")
            return

        module_info = analyze_module(module_path)

        output_dir = Path("tests/behavioral/generated")
        output_dir.mkdir(exist_ok=True, parents=True)

        test_filename = f"test_{module_path.stem}_behavioral.py"
        output_path = output_dir / test_filename

        template = generate_test_template(module_info, output_path)
        output_path.write_text(template)

        print(f"✅ Generated: {output_path}")
        print(f"\nClasses: {len(module_info.classes)}")
        print(f"Functions: {len(module_info.functions)}")
        print(f"\nNext: Edit {output_path} and fill in TODOs")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
