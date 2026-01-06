"""Run test5 workflow with Refactoring Crew"""

import asyncio
import sys
from pathlib import Path

from empathy_os.workflows import get_workflow


async def main():
    print("=" * 60)
    print("🚀 Running test5 Workflow with Refactoring Crew")
    print("=" * 60)

    # Get the workflow
    workflow_cls = get_workflow("test5")
    workflow = workflow_cls()

    print(f"\n📋 Workflow: {workflow.name}")
    print(f"📝 Description: {workflow.description}")
    print(f"🔄 Stages: {', '.join(workflow.stages)}")
    print(f"🎯 Tier Map: {workflow.tier_map}")

    # Sample code to analyze
    code_path = Path("src/empathy_os/workflows")

    print(f"\n📂 Analyzing code in: {code_path}")
    print("\n⏳ Starting workflow execution...")
    print("-" * 60)

    try:
        # Execute the workflow
        result = await workflow.execute(
            path=str(code_path), focus="code quality and refactoring opportunities"
        )

        print("\n" + "=" * 60)
        print("✅ Workflow Completed Successfully!")
        print("=" * 60)

        # Display results
        if hasattr(result, "stages") and result.stages:
            print("\n📊 Stage Results:")
            for stage in result.stages:
                print(f"\n  🔸 {stage.name.upper()}:")
                if stage.result:
                    # Pretty print the result
                    if isinstance(stage.result, dict):
                        for key, value in stage.result.items():
                            if key == "findings" and isinstance(value, list):
                                print(f"     {key}: {len(value)} items")
                                for i, finding in enumerate(value[:3], 1):  # Show first 3
                                    print(f"       {i}. {finding.get('title', 'N/A')}")
                                if len(value) > 3:
                                    print(f"       ... and {len(value) - 3} more")
                            else:
                                print(f"     {key}: {value}")
                    else:
                        print(f"     {stage.result}")
                print(f"     Cost: ${stage.cost:.4f}")
                print(f"     Duration: {stage.duration_ms}ms")

        if hasattr(result, "cost_report"):
            print("\n💰 Cost Report:")
            print(f"   Total Cost: ${result.cost_report.total_cost:.4f}")
            if hasattr(result.cost_report, "savings_percent"):
                print(f"   Savings: {result.cost_report.savings_percent:.1f}%")

        if hasattr(result, "summary"):
            print("\n📋 Summary:")
            print(f"   {result.summary}")

        return 0

    except Exception as e:
        print(f"\n❌ Error running workflow: {e}")
        print(f"\n🔍 Error details: {type(e).__name__}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
