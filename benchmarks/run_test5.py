"""Run test5 workflow"""

import asyncio

from attune.workflows import get_workflow


async def main():
    # Get the workflow
    workflow_cls = get_workflow("test5")
    workflow = workflow_cls()

    print(f"Running workflow: {workflow.name}")
    print(f"Description: {workflow.description}")
    print(f"Stages: {workflow.stages}")

    # Run the workflow
    # Note: The workflow needs the crew to be configured properly
    # For now, this will show the workflow structure

    print("\n✅ Workflow registered and ready!")
    print("\n⚠️ Note: Edit src/attune/workflows/test5.py")
    print("   Change 'MyCrew' to 'RefactoringCrew' to use the refactoring agents")


if __name__ == "__main__":
    asyncio.run(main())
