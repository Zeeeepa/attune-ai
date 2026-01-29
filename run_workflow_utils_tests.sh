#!/bin/bash
# Run workflow utilities behavioral tests
cd /Users/patrickroebuck/Documents/empathy1-11-2025-local/empathy-framework
python -m pytest tests/behavioral/generated/test_workflow_utilities_behavioral.py -v --tb=short -n 0
