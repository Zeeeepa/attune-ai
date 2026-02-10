"""CDS Decision Audit Trail.

HIPAA-compliant logging of all clinical decision support outputs.
Patient IDs are SHA256 hashed. Supports local JSON Lines storage
and optional Redis pub/sub for real-time audit streaming.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

from .decision_log import CDSAuditLogger

__all__ = ["CDSAuditLogger"]
