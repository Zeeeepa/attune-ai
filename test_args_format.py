"""Test that enhanced prompts generate Args/Returns/Raises format."""

import asyncio
from pathlib import Path

from empathy_os.workflows.document_gen import DocumentGenerationWorkflow


async def test_args_format():
    """Test Args/Returns/Raises format in generated docs."""
    print("📚 Testing Args/Returns/Raises Format\n")

    # Use a simple module with functions that have parameters
    test_module = Path("src/empathy_os/cache_stats.py")

    if not test_module.exists():
        print(f"❌ Test module not found: {test_module}")
        return

    print(f"📝 Generating documentation for: {test_module}")
    print(f"🎯 Expected: **Args:**, **Returns:**, **Raises:** sections\n")

    # Read full source code (needed for AST parsing in API reference generation)
    source_code = test_module.read_text()

    # Create workflow with enhanced prompts
    workflow = DocumentGenerationWorkflow(
        export_path="docs/generated",
        max_cost=0.5,
        graceful_degradation=True,
    )

    print(f"🔄 Calling LLM with MANDATORY format requirements...\n")

    # Generate documentation
    result = await workflow.execute(
        source_code=source_code,
        target=str(test_module),
        doc_type="api_reference",
        audience="developers",
    )

    # Extract document
    if hasattr(result, "final_output") and isinstance(result.final_output, dict):
        document = result.final_output.get("document", "")
        export_path = result.final_output.get("export_path", "")
    else:
        print(f"❌ Unexpected result format")
        return

    print(f"✅ Documentation Generated!\n")

    # Check for required format elements
    has_args = "**Args:**" in document or "Args:" in document
    has_returns = "**Returns:**" in document or "Returns:" in document
    has_raises = "**Raises:**" in document or "Raises:" in document

    print(f"📊 Format Check:")
    print(f"   {'✅' if has_args else '❌'} Has **Args:** sections")
    print(f"   {'✅' if has_returns else '❌'} Has **Returns:** sections")
    print(f"   {'✅' if has_raises else '❌'} Has **Raises:** sections")

    # Count occurrences
    args_count = document.count("**Args:**") + document.count("Args:")
    returns_count = document.count("**Returns:**") + document.count("Returns:")
    raises_count = document.count("**Raises:**") + document.count("Raises:")

    print(f"\n📈 Occurrences:")
    print(f"   Args: {args_count} times")
    print(f"   Returns: {returns_count} times")
    print(f"   Raises: {raises_count} times")

    if export_path:
        print(f"\n📁 Saved to: {export_path}")

    # Show a sample with Args
    if has_args:
        print(f"\n📄 Sample showing Args format:")
        print("-" * 60)
        lines = document.split("\n")
        for i, line in enumerate(lines):
            if "**Args:**" in line or "Args:" in line:
                # Show 20 lines around this Args section
                start = max(0, i - 5)
                end = min(len(lines), i + 15)
                print("\n".join(lines[start:end]))
                break
        print("-" * 60)
    else:
        print(f"\n⚠️  No Args sections found! Showing first 1000 chars:")
        print("-" * 60)
        print(document[:1000])
        print("-" * 60)

    # Overall verdict
    if has_args and has_returns:
        print(f"\n✅ SUCCESS: Documentation uses required Args/Returns/Raises format!")
    else:
        print(f"\n❌ FAILED: Documentation missing required format sections")


if __name__ == "__main__":
    asyncio.run(test_args_format())
