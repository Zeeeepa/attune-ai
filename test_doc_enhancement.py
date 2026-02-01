"""Test enhanced documentation generation.

Verifies that the improved prompts generate comprehensive, production-ready docs.
"""

import asyncio
from pathlib import Path

from attune.workflows.document_gen import DocumentGenerationWorkflow


async def test_doc_generation():
    """Test enhanced documentation generation."""
    print("📚 Testing Enhanced Documentation Generator\n")

    # Test on a small module
    test_module = Path("src/attune/platform_utils.py")

    if not test_module.exists():
        print(f"❌ Test module not found: {test_module}")
        return

    print(f"📝 Generating documentation for: {test_module}")
    print("🎯 Expected improvements:")
    print("   - Real, executable code examples (not placeholders)")
    print("   - Comprehensive API documentation with parameters")
    print("   - Usage guides with best practices")
    print("   - Edge case handling examples\n")

    # Read source code
    source_code = test_module.read_text()

    # Create enhanced workflow
    workflow = DocumentGenerationWorkflow(
        export_path="docs/generated",
        max_cost=1.0,  # Limit to $1 for testing
        graceful_degradation=True,
    )

    print("🔄 Calling LLM to generate enhanced documentation...\n")

    # Generate documentation
    result = await workflow.execute(
        source_code=source_code,
        target=str(test_module),
        doc_type="api_reference",
        audience="developers",
    )

    print("\n✅ Documentation Generation Complete!\n")

    # Extract results from WorkflowResult
    if hasattr(result, "final_output") and isinstance(result.final_output, dict):
        output = result.final_output
        document = output.get("document", "")
        export_path = output.get("export_path", "")
        accumulated_cost = output.get("accumulated_cost", 0.0)
        print(f"✓ Extracted from final_output: document length = {len(document)}")
    elif isinstance(result, dict):
        document = result.get("document", "")
        export_path = output.get("export_path", "")
        accumulated_cost = result.get("accumulated_cost", 0.0)
        print(f"✓ Extracted from dict: document length = {len(document)}")
    else:
        print(f"❌ Unexpected result format: {type(result)}")
        return

    if not document:
        print("❌ No document generated (document is empty)")
        return

    print("📊 Results:")
    print(f"   Output Size: {len(document)} characters")
    print(f"   Word Count: {len(document.split())} words")
    print(f"   Sections: ~{document.count('##')} sections")
    print(f"   Cost: ${accumulated_cost:.4f}")

    if export_path:
        print(f"   📁 Saved to: {export_path}")

    print("\n🔍 Quality Checks:")

    # Check for real examples (not placeholders)
    has_code_blocks = "```python" in document
    has_imports = "import" in document or "from " in document
    has_real_function_names = test_module.stem in document.lower()
    no_placeholders = "TODO" not in document and "..." not in document
    has_parameters = "Args:" in document or "Parameters:" in document
    has_examples = "Example:" in document or "example" in document.lower()

    checks = [
        ("✅" if has_code_blocks else "❌", "Contains Python code blocks"),
        ("✅" if has_imports else "❌", "Includes import statements"),
        ("✅" if has_real_function_names else "❌", "References actual code"),
        ("✅" if no_placeholders else "❌", "No TODO placeholders"),
        ("✅" if has_parameters else "❌", "Documents parameters"),
        ("✅" if has_examples else "❌", "Includes examples"),
    ]

    for icon, check in checks:
        print(f"   {icon} {check}")

    # Show a sample of the output
    print("\n📄 Documentation Preview (first 1000 chars):")
    print("-" * 60)
    print(document[:1000])
    if len(document) > 1000:
        print("...")
    print("-" * 60)


if __name__ == "__main__":
    asyncio.run(test_doc_generation())
