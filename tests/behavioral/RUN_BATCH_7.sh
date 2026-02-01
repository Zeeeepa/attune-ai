#!/bin/bash
# Run Batch 7: Telemetry & Monitoring Module Behavioral Tests
# Usage: ./tests/behavioral/RUN_BATCH_7.sh

set -e

echo "========================================"
echo "Batch 7: Telemetry & Monitoring Tests"
echo "========================================"
echo ""

echo "Module 1: Usage Tracker"
python -m pytest tests/behavioral/test_usage_tracker_behavioral.py -v --tb=short || true
echo ""

echo "Module 2: Alerts System"
python -m pytest tests/behavioral/test_alerts_behavioral.py -v --tb=short || true
echo ""

echo "Module 3: Agent Tracking"
python -m pytest tests/behavioral/test_agent_tracking_behavioral.py -v --tb=short || true
echo ""

echo "Module 4: Prompt Metrics"
python -m pytest tests/behavioral/test_prompt_metrics_behavioral.py -v --tb=short || true
echo ""

echo "Modules 5-15: Telemetry Modules"
python -m pytest tests/behavioral/test_telemetry_modules_behavioral.py -v --tb=short || true
echo ""

echo "Module 16: Alerts CLI"
python -m pytest tests/behavioral/test_alerts_cli_behavioral.py -v --tb=short || true
echo ""

echo "========================================"
echo "Summary"
echo "========================================"
python -m pytest tests/behavioral/test_*_behavioral.py --collect-only -q | grep "test session starts" -A 20 || true

echo ""
echo "To run with coverage:"
echo "  pytest tests/behavioral/test_*_behavioral.py --cov=src/empathy_os/telemetry --cov=src/empathy_os/monitoring --cov=src/empathy_os/metrics --cov-report=html"
echo ""
echo "To run specific test:"
echo "  pytest tests/behavioral/test_usage_tracker_behavioral.py::TestLLMCallTracking::test_tracks_basic_llm_call -v"
