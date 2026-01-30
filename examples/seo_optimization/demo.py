"""Demo script showing SEO optimization workflow usage."""

import asyncio
from pathlib import Path

from empathy_os.workflows import SEOOptimizationWorkflow


async def main():
    """Run SEO optimization demo."""
    print("=" * 60)
    print("SEO Optimization Workflow Demo")
    print("=" * 60)

    # Initialize workflow
    workflow = SEOOptimizationWorkflow()

    # Example 1: Quick audit
    print("\n📊 Example 1: Quick Audit")
    print("-" * 60)
    result = await workflow.execute(
        docs_path=Path("../../docs"),
        site_url="https://smartaimemory.com",
        mode="audit",
    )

    print(f"✅ Audit complete!")
    print(f"   Files scanned: {result.metadata['files_scanned']}")
    print(f"   Issues found: {result.metadata['issues_found']}")
    print(f"   Cost: ${result.cost_report.total_cost:.4f}")
    print(f"   Savings: {result.cost_report.savings_percent:.1f}%")

    # Example 2: Suggest fixes
    print("\n💡 Example 2: Generate Fix Suggestions")
    print("-" * 60)
    result = await workflow.execute(
        docs_path=Path("../../docs"),
        site_url="https://smartaimemory.com",
        mode="suggest",
    )

    print(f"✅ Suggestions generated!")
    print(f"   Files scanned: {result.metadata['files_scanned']}")
    print(f"   Issues found: {result.metadata['issues_found']}")
    recommendations = result.data.get("recommendations", {})
    print(
        f"   Recommendations: {recommendations.get('total_recommendations', 0)}"
    )
    print(f"   High priority: {recommendations.get('high_priority', 0)}")
    print(f"   Cost: ${result.cost_report.total_cost:.4f}")

    # Example 3: Interactive fix (would prompt user in real scenario)
    print("\n🔧 Example 3: Interactive Fix Mode")
    print("-" * 60)
    print("In real usage, this would show interactive prompts for each fix.")
    print("For this demo, we'll skip to show the structure.")

    # Show workflow stages
    print("\n📋 Workflow Structure:")
    print(f"   Stage 1: scan (CHEAP - Haiku)")
    print(f"   Stage 2: analyze (CAPABLE - Sonnet)")
    print(f"   Stage 3: recommend (PREMIUM - Opus)")
    print(f"   Stage 4: implement (CAPABLE - Sonnet)")

    print("\n" + "=" * 60)
    print("Demo complete! 🎉")
    print("=" * 60)
    print("\nTo run for real:")
    print("  python seo_agent.py --mode audit")
    print("  python seo_agent.py --mode suggest")
    print("  python seo_agent.py --mode fix")


if __name__ == "__main__":
    asyncio.run(main())
