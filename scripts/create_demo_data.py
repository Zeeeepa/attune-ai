"""Create demo progressive workflow data for CLI testing."""

import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from empathy_os.workflows.progressive.core import (
    FailureAnalysis,
    ProgressiveWorkflowResult,
    Tier,
    TierResult,
)


def create_demo_result() -> ProgressiveWorkflowResult:
    """Create a demo progressive workflow result."""
    # Create tier results showing escalation
    tier_results = [
        TierResult(
            tier=Tier.CHEAP,
            model="gpt-4o-mini",
            success=False,
            quality_score=0.65,  # Low quality, needs escalation
            items_processed=10,
            items_successful=6,
            cost=0.30,
            duration=5.2,
            tokens_used={"input": 1000, "output": 2000, "total": 3000},
            failure_analysis=FailureAnalysis(
                failed_item_ids=["item_1", "item_2", "item_3", "item_4"],
                failure_reasons={
                    "syntax_errors": 2,
                    "low_coverage": 1,
                    "weak_assertions": 1,
                },
                confidence_scores={"item_1": 0.45, "item_2": 0.50, "item_3": 0.55, "item_4": 0.60},
            ),
        ),
        TierResult(
            tier=Tier.CAPABLE,
            model="claude-3-5-sonnet-20241022",
            success=False,
            quality_score=0.78,  # Better but still needs improvement
            items_processed=4,
            items_successful=3,
            cost=0.60,
            duration=8.5,
            tokens_used={"input": 2000, "output": 3000, "total": 5000},
            failure_analysis=FailureAnalysis(
                failed_item_ids=["item_1"],
                failure_reasons={"complex_logic": 1},
                confidence_scores={"item_1": 0.72},
            ),
        ),
        TierResult(
            tier=Tier.PREMIUM,
            model="claude-opus-4-20250514",
            success=True,
            quality_score=0.92,  # High quality final result
            items_processed=1,
            items_successful=1,
            cost=0.50,
            duration=12.3,
            tokens_used={"input": 3000, "output": 4000, "total": 7000},
            failure_analysis=None,
        ),
    ]

    # Calculate totals
    total_cost = sum(t.cost for t in tier_results)
    baseline_cost = 10 * 0.50  # 10 items at premium tier rate
    cost_savings = baseline_cost - total_cost

    # Create result
    result = ProgressiveWorkflowResult(
        task_id=f"demo-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        workflow="test-generation",
        timestamp=datetime.now().isoformat(),
        total_items=10,
        total_cost=total_cost,
        cost_savings=cost_savings,
        cost_savings_percent=(cost_savings / baseline_cost) * 100,
        escalation_count=2,
        tier_results=tier_results,
        final_quality_score=0.92,
        success=True,
        duration=26.0,
    )

    return result


def main():
    """Create and save demo data."""
    print("Creating demo progressive workflow data...")

    result = create_demo_result()

    # Save to disk
    saved_path = result.save_to_disk()
    print(f"✅ Saved demo data to: {saved_path}")
    print()

    # Show summary
    print("=" * 70)
    print("DEMO DATA SUMMARY")
    print("=" * 70)
    print(f"Task ID: {result.task_id}")
    print(f"Workflow: {result.workflow}")
    print(f"Total Items: {result.total_items}")
    print(f"Total Cost: ${result.total_cost:.2f}")
    print(f"Cost Savings: ${result.cost_savings:.2f} ({result.cost_savings_percent:.0f}%)")
    print(f"Escalations: {result.escalation_count}")
    print(f"Final Quality: {result.final_quality_score:.2f}")
    print()

    # Show CLI commands
    print("=" * 70)
    print("TEST CLI COMMANDS")
    print("=" * 70)
    print("empathy progressive list")
    print(f"empathy progressive show {result.task_id}")
    print("empathy progressive analytics")
    print("empathy progressive analytics --json")
    print()


if __name__ == "__main__":
    main()
