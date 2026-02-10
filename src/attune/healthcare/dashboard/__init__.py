"""Nurse Dashboard for Clinical Decision Support.

FastAPI-based real-time monitoring dashboard for bedside nurses.
Provides REST API for assessments and WebSocket for live updates.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

from __future__ import annotations

from .app import create_nurse_app, run_nurse_dashboard

__all__ = ["create_nurse_app", "run_nurse_dashboard"]
