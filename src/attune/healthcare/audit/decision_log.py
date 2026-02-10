"""CDS Decision Audit Logger.

HIPAA-compliant logging of all clinical decision support outputs.
Patient IDs are SHA256 hashed before storage. Stores decisions as
JSON Lines for efficient append-only writes and streaming reads.

Follows UsageTracker pattern from attune.telemetry.analytics.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Default storage location
DEFAULT_AUDIT_DIR = os.path.expanduser("~/.attune/healthcare/audit")

# Check Redis availability
try:
    import redis as redis_lib

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class CDSAuditLogger:
    """Audit logger for CDS decisions.

    Provides HIPAA-compliant logging with:
    - SHA256 hashing of patient identifiers
    - JSON Lines append-only storage
    - Decision retrieval by UUID
    - Filtered listing by patient and time range
    - Optional Redis pub/sub for real-time audit streaming

    Args:
        storage_dir: Directory for audit log files
        redis_client: Optional Redis client for pub/sub notifications
    """

    CHANNEL = "cds:audit:new_decision"

    def __init__(
        self,
        storage_dir: str | None = None,
        redis_client: Any | None = None,
    ) -> None:
        self.storage_dir = Path(storage_dir or DEFAULT_AUDIT_DIR)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.storage_dir / "cds_decisions.jsonl"
        self.redis = redis_client

    @staticmethod
    def _hash_patient_id(patient_id: str) -> str:
        """Hash patient ID with SHA256 for HIPAA compliance.

        Args:
            patient_id: Raw patient identifier

        Returns:
            SHA256 hex digest of the patient ID
        """
        return hashlib.sha256(patient_id.encode()).hexdigest()

    def log_decision(
        self,
        decision: Any,
        request_context: dict[str, Any] | None = None,
    ) -> str:
        """Log a CDS decision to the audit trail.

        Args:
            decision: CDSDecision object (must have to_dict() method)
            request_context: Optional metadata about the request
                (e.g., requesting_user, source_system, session_id)

        Returns:
            UUID string identifying this audit entry
        """
        decision_id = str(uuid.uuid4())
        decision_dict = decision.to_dict()

        entry = {
            "decision_id": decision_id,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "patient_id_hash": self._hash_patient_id(decision.patient_id),
            "request_context": request_context or {},
            "overall_risk": decision_dict.get("overall_risk", "unknown"),
            "confidence": decision_dict.get("confidence", 0.0),
            "cost": decision_dict.get("cost", 0.0),
            "agent_count": len(decision_dict.get("agent_results", [])),
            "quality_gates": decision_dict.get("quality_gates", []),
            "alerts": decision_dict.get("alerts", []),
            "recommendations": decision_dict.get("recommendations", []),
            "decision_summary": {
                "protocol_compliance": decision_dict.get("protocol_compliance", {}),
                "trajectory": decision_dict.get("trajectory", {}),
                "ecg_analysis": decision_dict.get("ecg_analysis"),
                "clinical_reasoning": decision_dict.get("clinical_reasoning"),
            },
        }

        # Append to JSONL file
        try:
            with self.log_file.open("a") as f:
                f.write(json.dumps(entry) + "\n")
        except OSError as e:
            logger.error(f"Failed to write audit log: {e}")
            raise

        # Publish to Redis if available
        if self.redis is not None:
            try:
                self.redis.publish(
                    self.CHANNEL,
                    json.dumps({"decision_id": decision_id, "risk": entry["overall_risk"]}),
                )
            except Exception as e:  # noqa: BLE001
                # INTENTIONAL: Redis pub/sub is optional, don't fail audit on it
                logger.warning(f"Redis publish failed (non-fatal): {e}")

        logger.info(
            f"CDS decision logged: {decision_id} "
            f"(risk={entry['overall_risk']}, cost=${entry['cost']:.4f})"
        )
        return decision_id

    def get_decision(self, decision_id: str) -> dict[str, Any] | None:
        """Retrieve a single decision by its UUID.

        Args:
            decision_id: UUID of the decision to retrieve

        Returns:
            Decision dict if found, None otherwise
        """
        if not self.log_file.exists():
            return None

        try:
            with self.log_file.open("r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        if entry.get("decision_id") == decision_id:
                            return entry
                    except json.JSONDecodeError:
                        continue
        except OSError as e:
            logger.error(f"Failed to read audit log: {e}")
            return None

        return None

    def list_decisions(
        self,
        patient_id: str | None = None,
        since: datetime | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """List decisions with optional filtering.

        Args:
            patient_id: Filter by patient (raw ID — will be hashed for lookup)
            since: Only include decisions after this timestamp
            limit: Maximum number of decisions to return

        Returns:
            List of decision dicts, most recent first
        """
        if not self.log_file.exists():
            return []

        patient_hash = self._hash_patient_id(patient_id) if patient_id else None
        results: list[dict[str, Any]] = []

        try:
            with self.log_file.open("r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    # Filter by patient
                    if patient_hash and entry.get("patient_id_hash") != patient_hash:
                        continue

                    # Filter by time
                    if since:
                        entry_time = datetime.fromisoformat(entry["timestamp"])
                        if entry_time < since:
                            continue

                    results.append(entry)
        except OSError as e:
            logger.error(f"Failed to read audit log: {e}")
            return []

        # Sort by timestamp descending (most recent first)
        results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return results[:limit]

    def count_decisions(
        self,
        patient_id: str | None = None,
        since: datetime | None = None,
    ) -> int:
        """Count decisions matching filters.

        Args:
            patient_id: Filter by patient (raw ID)
            since: Only count decisions after this timestamp

        Returns:
            Number of matching decisions
        """
        return len(self.list_decisions(patient_id=patient_id, since=since, limit=1_000_000))
