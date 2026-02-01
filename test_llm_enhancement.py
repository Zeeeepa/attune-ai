"""Test LLM-enhanced test generation.

Quick verification that the enhanced generator works.
"""

import ast
from pathlib import Path

from attune.workflows.test_gen_behavioral import (
    BehavioralTestLLMGenerator,
    ModuleAnalyzer,
    ModuleInfo,
)


def test_llm_generation():
    """Test LLM-enhanced test generation."""
    print("🧪 Testing LLM-Enhanced Test Generator\n")

    # Create LLM generator
    generator = BehavioralTestLLMGenerator(use_llm=True, model_tier="capable")

    # Test on a small module
    test_module = Path("src/attune/platform_utils.py")

    if not test_module.exists():
        print(f"❌ Test module not found: {test_module}")
        return

    print(f"📝 Generating tests for: {test_module}")
    print("🤖 LLM Tier: capable (Claude Sonnet 4.5)\n")

    # Analyze module
    source_code = test_module.read_text()
    tree = ast.parse(source_code)
    analyzer = ModuleAnalyzer(source_code)
    analyzer.visit(tree)

    from dataclasses import asdict

    module_info = ModuleInfo(
        file_path=str(test_module),
        classes=[asdict(c) for c in analyzer.classes],
        functions=[asdict(f) for f in analyzer.functions],
        imports=analyzer.imports,
        total_lines=len(source_code.splitlines()),
    )

    # Generate tests
    output_dir = Path("tests/behavioral/llm_test")
    output_dir.mkdir(exist_ok=True, parents=True)
    output_file = output_dir / f"test_{test_module.stem}_behavioral.py"

    print("🔄 Calling LLM to generate tests...")
    test_content = generator.generate_test_file(
        module_info=module_info, output_path=output_file, source_code=source_code
    )

    # Save generated test
    output_file.write_text(test_content)

    print("\n✅ Test Generation Complete!")
    print(f"   Output File: {output_file}")
    print(f"   Size: {len(test_content)} bytes")
    print(f"   Lines: {len(test_content.splitlines())}")

    # Check if it's a real test (not placeholder)
    has_todos = "# TODO:" in test_content or "pass  # TODO" in test_content
    if has_todos:
        print("   ⚠️  Contains TODOs (template fallback)")
    else:
        print("   ✅ Complete implementation (LLM generated)")

    # Count test functions
    test_count = test_content.count("def test_")
    print(f"   Test Functions: {test_count}")

    # Show stats
    stats = generator.get_stats()
    print("\n📊 Generation Stats:")
    print(f"   LLM Requests: {stats['llm_requests']}")
    print(f"   LLM Failures: {stats['llm_failures']}")
    print(f"   Template Fallbacks: {stats['template_fallbacks']}")
    print(f"   Cache Hits: {stats['cache_hits']}")
    print(f"   Cache Misses: {stats['cache_misses']}")
    print(f"   Estimated Cost: ${stats['total_cost_usd']:.4f}")


if __name__ == "__main__":
    test_llm_generation()
