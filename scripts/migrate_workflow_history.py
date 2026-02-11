#!/usr/bin/env python3
"""Migrate workflow history from JSON to SQLite.

This script migrates the legacy JSON-based workflow history
(.attune/workflow_runs.json) to the new SQLite-based storage
(.attune/history.db).

Features:
    - Preserves all workflow run data
    - Creates backup of JSON file
    - Validates migration success
    - Idempotent - safe to run multiple times

Usage:
    python scripts/migrate_workflow_history.py

    # Custom paths:
    python scripts/migrate_workflow_history.py \\
        --json-path=.attune/workflow_runs.json \\
        --db-path=.attune/history.db

Copyright 2025 Smart-AI-Memory
Licensed under the Apache License, Version 2.0
"""

import argparse
import json
import sys
import uuid
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from attune.workflows.base import (
    WORKFLOW_HISTORY_FILE,
    CostReport,
    ModelTier,
    WorkflowResult,
    WorkflowStage,
)
from attune.workflows.history import WorkflowHistoryStore


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Migrate workflow history from JSON to SQLite")
    parser.add_argument(
        "--json-path",
        default=WORKFLOW_HISTORY_FILE,
        help=f"Path to JSON history file (default: {WORKFLOW_HISTORY_FILE})",
    )
    parser.add_argument(
        "--db-path",
        default=WorkflowHistoryStore.DEFAULT_DB,
        help=f"Path to SQLite database (default: {WorkflowHistoryStore.DEFAULT_DB})",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip creating backup of JSON file",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing database",
    )
    return parser.parse_args()


def validate_json_history(history: list) -> tuple[bool, str]:
    """Validate JSON history structure.

    Args:
        history: Loaded JSON history list

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(history, list):
        return False, "History is not a list"

    for i, run in enumerate(history):
        if not isinstance(run, dict):
            return False, f"Run {i} is not a dictionary"

        # Check required fields
        required = ["workflow", "started_at", "completed_at"]
        for field in required:
            if field not in run:
                return False, f"Run {i} missing required field: {field}"

    return True, ""


def migrate_run(run: dict, run_id: str) -> WorkflowResult:
    """Convert JSON run record to WorkflowResult.

    Args:
        run: JSON run dictionary
        run_id: Generated run ID

    Returns:
        WorkflowResult object
    """
    # Parse stages
    stages = []
    for stage_data in run.get("stages", []):
        try:
            tier = ModelTier(stage_data.get("tier", "capable"))
        except ValueError:
            # Invalid tier, default to capable
            tier = ModelTier.CAPABLE

        stage = WorkflowStage(
            name=stage_data.get("name", "unknown"),
            tier=tier,
            skipped=stage_data.get("skipped", False),
            cost=stage_data.get("cost", 0.0),
            duration_ms=stage_data.get("duration_ms", 0),
            input_tokens=stage_data.get("input_tokens", 0),
            output_tokens=stage_data.get("output_tokens", 0),
            skip_reason=stage_data.get("skip_reason"),
        )
        stages.append(stage)

    # Parse timestamps
    try:
        started_at = datetime.fromisoformat(run["started_at"])
    except (ValueError, KeyError):
        # Fallback to current time if invalid
        started_at = datetime.now()

    try:
        completed_at = datetime.fromisoformat(run["completed_at"])
    except (ValueError, KeyError):
        completed_at = started_at

    # Build final output
    final_output: dict = {}
    if run.get("xml_parsed"):
        final_output["xml_parsed"] = True
        if run.get("summary"):
            final_output["summary"] = run["summary"]
        if run.get("findings"):
            final_output["findings"] = run["findings"]
        if run.get("checklist"):
            final_output["checklist"] = run["checklist"]

    # Create cost report
    cost_report = CostReport(
        total_cost=run.get("cost", 0.0),
        baseline_cost=run.get("baseline_cost", run.get("cost", 0.0)),
        savings=run.get("savings", 0.0),
        savings_percent=run.get("savings_percent", 0.0),
        by_tier={},  # Reconstructed from stages
        cache_savings=0.0,  # Not stored in old format
    )

    # Reconstruct by_tier from stages
    for stage in stages:
        if not stage.skipped:
            tier_key = stage.tier.value
            cost_report.by_tier[tier_key] = cost_report.by_tier.get(tier_key, 0.0) + stage.cost

    # Create WorkflowResult
    result = WorkflowResult(
        success=run.get("success", True),
        stages=stages,
        final_output=final_output,
        cost_report=cost_report,
        started_at=started_at,
        completed_at=completed_at,
        total_duration_ms=run.get("duration_ms", 0),
        provider=run.get("provider", "unknown"),
        error=run.get("error"),
        error_type=run.get("error_type"),
        transient=run.get("transient", False),
    )

    return result


def migrate(
    json_path: str,
    db_path: str,
    no_backup: bool = False,
    force: bool = False,
) -> int:
    """Run migration.

    Args:
        json_path: Path to JSON history file
        db_path: Path to SQLite database
        no_backup: Skip creating backup
        force: Overwrite existing database

    Returns:
        Number of runs migrated
    """
    json_file = Path(json_path)

    # Check if JSON file exists
    if not json_file.exists():
        print(f"❌ JSON history file not found: {json_path}")
        print("   Nothing to migrate.")
        return 0

    # Check if database already exists
    db_file = Path(db_path)
    if db_file.exists() and not force:
        print(f"❌ Database already exists: {db_path}")
        print("   Use --force to overwrite, or delete the file first.")
        return 0

    # Load JSON history
    print(f"📖 Loading JSON history from: {json_path}")
    try:
        with open(json_file) as f:
            history = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return 0
    except OSError as e:
        print(f"❌ Failed to read file: {e}")
        return 0

    # Validate structure
    valid, error = validate_json_history(history)
    if not valid:
        print(f"❌ Invalid history structure: {error}")
        return 0

    print(f"✅ Found {len(history)} workflow runs")

    # Create SQLite store
    print(f"💾 Creating SQLite database: {db_path}")
    try:
        store = WorkflowHistoryStore(db_path)
    except Exception as e:  # noqa: BLE001
        print(f"❌ Failed to create database: {e}")
        return 0

    # Migrate each run
    print("🔄 Migrating runs...")
    migrated = 0
    errors = 0

    for i, run in enumerate(history, 1):
        # Generate run_id from timestamp + UUID
        timestamp = run.get("started_at", "unknown").replace(":", "-").replace(".", "-")
        run_id = f"migrated_{timestamp}_{uuid.uuid4().hex[:8]}"

        try:
            # Convert to WorkflowResult
            result = migrate_run(run, run_id)

            # Store in SQLite
            store.record_run(
                run_id=run_id,
                workflow_name=run.get("workflow", "unknown"),
                provider=run.get("provider", "unknown"),
                result=result,
            )

            migrated += 1

            # Progress indicator
            if i % 10 == 0:
                print(f"  Migrated {i}/{len(history)} runs...")

        except Exception as e:  # noqa: BLE001
            # INTENTIONAL: Continue migration even if individual runs fail
            print(f"  ⚠️  Failed to migrate run {i}: {e}")
            errors += 1

    store.close()

    # Validate migration
    print("✅ Validating migration...")
    store = WorkflowHistoryStore(db_path)
    stats = store.get_stats()
    total_in_db = stats["total_runs"]
    store.close()

    if total_in_db != migrated:
        print(f"⚠️  Warning: Expected {migrated} runs, found {total_in_db} in database")

    # Create backup
    if not no_backup:
        backup_path = json_file.with_suffix(".json.backup")
        print(f"💾 Creating backup: {backup_path}")
        try:
            json_file.rename(backup_path)
            print(f"✅ Original JSON backed up to: {backup_path}")
        except OSError as e:
            print(f"⚠️  Failed to create backup: {e}")
            print("   Original JSON file still exists")

    # Summary
    print("\n" + "=" * 60)
    print("✅ MIGRATION COMPLETE")
    print("=" * 60)
    print(f"  Migrated: {migrated} runs")
    print(f"  Errors: {errors} runs")
    print(f"  Database: {db_path}")
    if not no_backup:
        print(f"  Backup: {backup_path}")
    print()
    print("Next steps:")
    print(
        "  1. Verify migration: python -c 'from attune.workflows.history import WorkflowHistoryStore; store = WorkflowHistoryStore(); print(store.get_stats())'"
    )
    print("  2. Update your code to use WorkflowHistoryStore")
    print("  3. Delete backup after confidence period: rm .attune/workflow_runs.json.backup")
    print()

    return migrated


def main():
    """Main entry point."""
    args = parse_args()

    print("=" * 60)
    print("WORKFLOW HISTORY MIGRATION")
    print("JSON → SQLite")
    print("=" * 60)
    print()

    migrated = migrate(
        json_path=args.json_path,
        db_path=args.db_path,
        no_backup=args.no_backup,
        force=args.force,
    )

    if migrated > 0:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
