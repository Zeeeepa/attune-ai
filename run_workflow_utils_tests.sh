#!/bin/bash
# Run workflow behavioral tests for attune-ai
# Updated: 2026-02-04

cd /Users/patrickroebuck/attune-ai

echo "Running workflow behavioral tests..."
uv run pytest tests/behavioral/test_workflow_base_behavioral.py \
    tests/behavioral/generated/batch100/test_workflow_behavioral.py \
    tests/behavioral/generated/batch13/test_workflow_commands_behavioral.py \
    -v --tb=short

echo ""
echo "To run ALL behavioral tests:"
echo "  uv run pytest tests/behavioral/ -v --tb=short"
