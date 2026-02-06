#!/usr/bin/env python
"""Clinical Decision Support Demo.

Run the CDS multi-agent system with Redis coordination.

Usage:
    # Simulated mode (default) - no API costs
    python examples/cds_demo.py

    # Real LLM mode - uses actual API calls
    CDS_LLM_MODE=real python examples/cds_demo.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from attune.agents.healthcare.cds_team import demo

if __name__ == "__main__":
    asyncio.run(demo())
