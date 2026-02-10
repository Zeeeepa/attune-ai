"""Comprehensive unit tests for CDSAuditLogger.

Tests cover HIPAA-compliant audit logging of clinical decision support outputs,
including JSONL persistence, SHA256 patient ID hashing, decision retrieval,
filtered listing, and edge cases.
"""

import hashlib
import json
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from attune.healthcare.audit.decision_log import CDSAuditLogger

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_mock_decision(
    patient_id: str = "test-001",
    risk: str = "moderate",
    confidence: float = 0.85,
    cost: float = 0.0,
) -> MagicMock:
    """Create a mock CDSDecision with a ``to_dict()`` method."""
    decision = MagicMock()
    decision.patient_id = patient_id
    decision.to_dict.return_value = {
        "patient_id": patient_id,
        "overall_risk": risk,
        "confidence": confidence,
        "cost": cost,
        "agent_results": [],
        "quality_gates": [],
        "alerts": [],
        "recommendations": [],
        "protocol_compliance": {},
        "trajectory": {},
        "ecg_analysis": None,
        "clinical_reasoning": None,
    }
    return decision


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------


class TestCDSAuditLoggerInit:
    """Tests for CDSAuditLogger initialization."""

    def test_creates_storage_directory(self, tmp_path: "Path") -> None:
        """Storage directory is created on init when it does not exist."""
        audit_dir = tmp_path / "audit" / "nested"
        logger = CDSAuditLogger(storage_dir=str(audit_dir))

        assert audit_dir.exists()
        assert audit_dir.is_dir()
        assert logger.log_file == audit_dir / "cds_decisions.jsonl"

    def test_reuses_existing_storage_directory(self, tmp_path: "Path") -> None:
        """No error when storage directory already exists."""
        audit_dir = tmp_path / "audit"
        audit_dir.mkdir()

        logger = CDSAuditLogger(storage_dir=str(audit_dir))
        assert logger.storage_dir == audit_dir

    def test_redis_client_stored(self, tmp_path: "Path") -> None:
        """Optional Redis client is stored on the instance."""
        mock_redis = MagicMock()
        logger = CDSAuditLogger(storage_dir=str(tmp_path), redis_client=mock_redis)

        assert logger.redis is mock_redis

    def test_redis_client_defaults_to_none(self, tmp_path: "Path") -> None:
        """Redis client defaults to None when not provided."""
        logger = CDSAuditLogger(storage_dir=str(tmp_path))
        assert logger.redis is None


# ---------------------------------------------------------------------------
# SHA256 Patient ID Hashing (HIPAA)
# ---------------------------------------------------------------------------


class TestPatientIdHashing:
    """Verify HIPAA-compliant SHA256 hashing of patient identifiers."""

    def test_hash_is_sha256_hex(self) -> None:
        """Returned hash matches independent SHA256 computation."""
        raw_id = "patient-42"
        expected = hashlib.sha256(raw_id.encode()).hexdigest()

        assert CDSAuditLogger._hash_patient_id(raw_id) == expected

    def test_hash_is_deterministic(self) -> None:
        """Same input always produces the same hash."""
        h1 = CDSAuditLogger._hash_patient_id("patient-99")
        h2 = CDSAuditLogger._hash_patient_id("patient-99")
        assert h1 == h2

    def test_different_ids_produce_different_hashes(self) -> None:
        """Distinct patient IDs produce distinct hashes."""
        h1 = CDSAuditLogger._hash_patient_id("patient-A")
        h2 = CDSAuditLogger._hash_patient_id("patient-B")
        assert h1 != h2

    def test_hash_length_is_64_hex_chars(self) -> None:
        """SHA256 hex digest is always 64 characters."""
        result = CDSAuditLogger._hash_patient_id("any-id")
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)

    def test_empty_string_hashes_correctly(self) -> None:
        """Empty string still produces a valid SHA256 hash."""
        expected = hashlib.sha256(b"").hexdigest()
        assert CDSAuditLogger._hash_patient_id("") == expected


# ---------------------------------------------------------------------------
# Writing Decisions (log_decision)
# ---------------------------------------------------------------------------


class TestLogDecision:
    """Tests for writing decisions to the JSONL audit log."""

    def test_returns_uuid_string(self, tmp_path: "Path") -> None:
        """log_decision returns a UUID string."""
        logger = CDSAuditLogger(storage_dir=str(tmp_path))
        decision = make_mock_decision()

        decision_id = logger.log_decision(decision)

        # UUID4 format: 8-4-4-4-12 hex digits
        parts = decision_id.split("-")
        assert len(parts) == 5
        assert [len(p) for p in parts] == [8, 4, 4, 4, 12]

    def test_writes_jsonl_entry_to_file(self, tmp_path: "Path") -> None:
        """A single JSON line is appended to the log file."""
        logger = CDSAuditLogger(storage_dir=str(tmp_path))
        decision = make_mock_decision()

        logger.log_decision(decision)

        lines = logger.log_file.read_text().strip().splitlines()
        assert len(lines) == 1

        entry = json.loads(lines[0])
        assert "decision_id" in entry
        assert "timestamp" in entry

    def test_patient_id_is_hashed_in_entry(self, tmp_path: "Path") -> None:
        """Stored entry contains hashed patient ID, not raw."""
        logger = CDSAuditLogger(storage_dir=str(tmp_path))
        decision = make_mock_decision(patient_id="secret-patient-id")

        logger.log_decision(decision)

        entry = json.loads(logger.log_file.read_text().strip())
        expected_hash = hashlib.sha256(b"secret-patient-id").hexdigest()

        assert entry["patient_id_hash"] == expected_hash
        # Raw patient ID must NOT appear in the stored entry
        assert "secret-patient-id" not in json.dumps(entry)

    def test_entry_contains_decision_fields(self, tmp_path: "Path") -> None:
        """Stored entry captures risk, confidence, cost, and summaries."""
        logger = CDSAuditLogger(storage_dir=str(tmp_path))
        decision = make_mock_decision(risk="high", confidence=0.92, cost=0.035)

        logger.log_decision(decision)

        entry = json.loads(logger.log_file.read_text().strip())
        assert entry["overall_risk"] == "high"
        assert entry["confidence"] == 0.92
        assert entry["cost"] == 0.035
        assert entry["agent_count"] == 0
        assert entry["quality_gates"] == []
        assert entry["alerts"] == []
        assert entry["recommendations"] == []
        assert "decision_summary" in entry
        assert entry["decision_summary"]["protocol_compliance"] == {}
        assert entry["decision_summary"]["ecg_analysis"] is None

    def test_request_context_stored(self, tmp_path: "Path") -> None:
        """Optional request_context is persisted in the entry."""
        logger = CDSAuditLogger(storage_dir=str(tmp_path))
        decision = make_mock_decision()
        ctx = {"requesting_user": "dr_smith", "source_system": "ehr"}

        logger.log_decision(decision, request_context=ctx)

        entry = json.loads(logger.log_file.read_text().strip())
        assert entry["request_context"] == ctx

    def test_request_context_defaults_to_empty_dict(self, tmp_path: "Path") -> None:
        """When no request_context is supplied, an empty dict is stored."""
        logger = CDSAuditLogger(storage_dir=str(tmp_path))
        decision = make_mock_decision()

        logger.log_decision(decision)

        entry = json.loads(logger.log_file.read_text().strip())
        assert entry["request_context"] == {}

    def test_timestamp_is_utc_iso_format(self, tmp_path: "Path") -> None:
        """Logged timestamp is a valid UTC ISO 8601 string."""
        logger = CDSAuditLogger(storage_dir=str(tmp_path))
        decision = make_mock_decision()

        logger.log_decision(decision)

        entry = json.loads(logger.log_file.read_text().strip())
        ts = datetime.fromisoformat(entry["timestamp"])
        assert ts.tzinfo is not None  # timezone-aware

    def test_agent_count_reflects_agent_results(self, tmp_path: "Path") -> None:
        """agent_count equals the length of agent_results."""
        logger = CDSAuditLogger(storage_dir=str(tmp_path))
        decision = MagicMock()
        decision.patient_id = "p-1"
        decision.to_dict.return_value = {
            "patient_id": "p-1",
            "overall_risk": "low",
            "confidence": 0.9,
            "cost": 0.0,
            "agent_results": [{"agent": "a"}, {"agent": "b"}, {"agent": "c"}],
            "quality_gates": [],
            "alerts": [],
            "recommendations": [],
            "protocol_compliance": {},
            "trajectory": {},
            "ecg_analysis": None,
            "clinical_reasoning": None,
        }

        logger.log_decision(decision)

        entry = json.loads(logger.log_file.read_text().strip())
        assert entry["agent_count"] == 3


# ---------------------------------------------------------------------------
# Multiple Decisions Written Sequentially
# ---------------------------------------------------------------------------


class TestMultipleDecisions:
    """Tests for writing several decisions in sequence."""

    def test_multiple_decisions_appended(self, tmp_path: "Path") -> None:
        """Each call appends a new line; lines accumulate."""
        logger = CDSAuditLogger(storage_dir=str(tmp_path))

        ids = []
        for i in range(5):
            d = make_mock_decision(patient_id=f"p-{i}")
            ids.append(logger.log_decision(d))

        lines = logger.log_file.read_text().strip().splitlines()
        assert len(lines) == 5

        stored_ids = [json.loads(line)["decision_id"] for line in lines]
        assert stored_ids == ids

    def test_unique_ids_for_each_decision(self, tmp_path: "Path") -> None:
        """Every logged decision gets a unique UUID."""
        logger = CDSAuditLogger(storage_dir=str(tmp_path))

        ids = set()
        for _ in range(10):
            ids.add(logger.log_decision(make_mock_decision()))

        assert len(ids) == 10

    def test_different_patients_stored_with_distinct_hashes(self, tmp_path: "Path") -> None:
        """Decisions for different patients have distinct patient_id_hash values."""
        logger = CDSAuditLogger(storage_dir=str(tmp_path))

        logger.log_decision(make_mock_decision(patient_id="alpha"))
        logger.log_decision(make_mock_decision(patient_id="beta"))

        lines = logger.log_file.read_text().strip().splitlines()
        hashes = [json.loads(line)["patient_id_hash"] for line in lines]
        assert hashes[0] != hashes[1]


# ---------------------------------------------------------------------------
# Reading Decisions by UUID (get_decision)
# ---------------------------------------------------------------------------


class TestGetDecision:
    """Tests for retrieving a single decision by its UUID."""

    def test_retrieves_logged_decision(self, tmp_path: "Path") -> None:
        """A previously logged decision is retrievable by its ID."""
        logger = CDSAuditLogger(storage_dir=str(tmp_path))
        decision = make_mock_decision(risk="critical")

        decision_id = logger.log_decision(decision)
        result = logger.get_decision(decision_id)

        assert result is not None
        assert result["decision_id"] == decision_id
        assert result["overall_risk"] == "critical"

    def test_returns_none_for_unknown_id(self, tmp_path: "Path") -> None:
        """Returns None when the decision ID does not exist."""
        logger = CDSAuditLogger(storage_dir=str(tmp_path))
        logger.log_decision(make_mock_decision())

        result = logger.get_decision("nonexistent-uuid")
        assert result is None

    def test_returns_none_when_log_file_missing(self, tmp_path: "Path") -> None:
        """Returns None when the log file does not exist yet."""
        logger = CDSAuditLogger(storage_dir=str(tmp_path))
        # Do not log any decision, so log file never created

        assert logger.get_decision("any-id") is None

    def test_retrieves_correct_decision_among_many(self, tmp_path: "Path") -> None:
        """Correct decision returned when multiple exist."""
        logger = CDSAuditLogger(storage_dir=str(tmp_path))

        ids = []
        for i in range(5):
            d = make_mock_decision(patient_id=f"p-{i}", risk=f"level-{i}")
            ids.append(logger.log_decision(d))

        # Retrieve the third decision
        result = logger.get_decision(ids[2])
        assert result is not None
        assert result["decision_id"] == ids[2]
        assert result["overall_risk"] == "level-2"

    def test_skips_malformed_json_lines(self, tmp_path: "Path") -> None:
        """Malformed JSONL lines are silently skipped during lookup."""
        logger = CDSAuditLogger(storage_dir=str(tmp_path))
        decision_id = logger.log_decision(make_mock_decision())

        # Inject a malformed line before the valid entry
        content = logger.log_file.read_text()
        logger.log_file.write_text("NOT VALID JSON\n" + content)

        result = logger.get_decision(decision_id)
        assert result is not None
        assert result["decision_id"] == decision_id

    def test_skips_blank_lines(self, tmp_path: "Path") -> None:
        """Blank lines in the JSONL file are ignored."""
        logger = CDSAuditLogger(storage_dir=str(tmp_path))
        decision_id = logger.log_decision(make_mock_decision())

        content = logger.log_file.read_text()
        logger.log_file.write_text("\n\n" + content + "\n\n")

        result = logger.get_decision(decision_id)
        assert result is not None


# ---------------------------------------------------------------------------
# Listing Decisions with Filtering (list_decisions)
# ---------------------------------------------------------------------------


class TestListDecisions:
    """Tests for listing decisions with patient/time filtering."""

    def test_list_all_decisions(self, tmp_path: "Path") -> None:
        """All decisions returned when no filters applied."""
        logger = CDSAuditLogger(storage_dir=str(tmp_path))

        for i in range(3):
            logger.log_decision(make_mock_decision(patient_id=f"p-{i}"))

        results = logger.list_decisions()
        assert len(results) == 3

    def test_filter_by_patient_id(self, tmp_path: "Path") -> None:
        """Only decisions for the requested patient are returned."""
        logger = CDSAuditLogger(storage_dir=str(tmp_path))

        logger.log_decision(make_mock_decision(patient_id="alice"))
        logger.log_decision(make_mock_decision(patient_id="bob"))
        logger.log_decision(make_mock_decision(patient_id="alice"))

        results = logger.list_decisions(patient_id="alice")
        assert len(results) == 2

        expected_hash = hashlib.sha256(b"alice").hexdigest()
        for entry in results:
            assert entry["patient_id_hash"] == expected_hash

    def test_filter_by_patient_returns_empty_for_unknown(self, tmp_path: "Path") -> None:
        """Filtering by a patient with no decisions returns empty list."""
        logger = CDSAuditLogger(storage_dir=str(tmp_path))
        logger.log_decision(make_mock_decision(patient_id="alice"))

        results = logger.list_decisions(patient_id="unknown-patient")
        assert results == []

    def test_filter_by_since_timestamp(self, tmp_path: "Path") -> None:
        """Only decisions after the 'since' timestamp are returned."""
        logger = CDSAuditLogger(storage_dir=str(tmp_path))

        # Log a decision, then manually backdate its timestamp
        logger.log_decision(make_mock_decision(patient_id="early"))
        logger.log_decision(make_mock_decision(patient_id="recent"))

        # Read file, modify the first entry's timestamp to be old
        lines = logger.log_file.read_text().strip().splitlines()
        old_entry = json.loads(lines[0])
        old_entry["timestamp"] = "2020-01-01T00:00:00+00:00"
        lines[0] = json.dumps(old_entry)
        logger.log_file.write_text("\n".join(lines) + "\n")

        since = datetime(2024, 1, 1, tzinfo=timezone.utc)
        results = logger.list_decisions(since=since)

        assert len(results) == 1
        assert results[0]["patient_id_hash"] == hashlib.sha256(b"recent").hexdigest()

    def test_limit_restricts_result_count(self, tmp_path: "Path") -> None:
        """Limit parameter caps the number of returned decisions."""
        logger = CDSAuditLogger(storage_dir=str(tmp_path))

        for i in range(10):
            logger.log_decision(make_mock_decision(patient_id=f"p-{i}"))

        results = logger.list_decisions(limit=3)
        assert len(results) == 3

    def test_results_sorted_most_recent_first(self, tmp_path: "Path") -> None:
        """Returned decisions are sorted by timestamp descending."""
        logger = CDSAuditLogger(storage_dir=str(tmp_path))

        # Log three decisions with manually assigned timestamps
        timestamps = [
            "2025-06-01T00:00:00+00:00",
            "2025-09-15T00:00:00+00:00",
            "2025-03-10T00:00:00+00:00",
        ]
        for ts in timestamps:
            logger.log_decision(make_mock_decision())

        # Override timestamps in the file
        lines = logger.log_file.read_text().strip().splitlines()
        for i, ts in enumerate(timestamps):
            entry = json.loads(lines[i])
            entry["timestamp"] = ts
            lines[i] = json.dumps(entry)
        logger.log_file.write_text("\n".join(lines) + "\n")

        results = logger.list_decisions()
        result_timestamps = [r["timestamp"] for r in results]
        assert result_timestamps == sorted(result_timestamps, reverse=True)

    def test_empty_log_file_returns_empty_list(self, tmp_path: "Path") -> None:
        """Returns empty list when the log file does not exist."""
        logger = CDSAuditLogger(storage_dir=str(tmp_path))
        # No decisions logged, log file not created
        results = logger.list_decisions()
        assert results == []

    def test_combined_patient_and_since_filters(self, tmp_path: "Path") -> None:
        """Patient and time filters can be combined."""
        logger = CDSAuditLogger(storage_dir=str(tmp_path))

        # Log decisions for two patients
        logger.log_decision(make_mock_decision(patient_id="alice"))
        logger.log_decision(make_mock_decision(patient_id="bob"))
        logger.log_decision(make_mock_decision(patient_id="alice"))

        # Backdate the first alice decision
        lines = logger.log_file.read_text().strip().splitlines()
        entry = json.loads(lines[0])
        entry["timestamp"] = "2020-01-01T00:00:00+00:00"
        lines[0] = json.dumps(entry)
        logger.log_file.write_text("\n".join(lines) + "\n")

        since = datetime(2024, 1, 1, tzinfo=timezone.utc)
        results = logger.list_decisions(patient_id="alice", since=since)

        assert len(results) == 1

    def test_skips_malformed_lines(self, tmp_path: "Path") -> None:
        """Malformed JSON lines are skipped without error."""
        logger = CDSAuditLogger(storage_dir=str(tmp_path))
        logger.log_decision(make_mock_decision())

        content = logger.log_file.read_text()
        logger.log_file.write_text("CORRUPT\n" + content)

        results = logger.list_decisions()
        assert len(results) == 1


# ---------------------------------------------------------------------------
# Counting Decisions (count_decisions)
# ---------------------------------------------------------------------------


class TestCountDecisions:
    """Tests for count_decisions."""

    def test_count_all(self, tmp_path: "Path") -> None:
        """Counts all decisions when no filters applied."""
        logger = CDSAuditLogger(storage_dir=str(tmp_path))

        for _ in range(4):
            logger.log_decision(make_mock_decision())

        assert logger.count_decisions() == 4

    def test_count_by_patient(self, tmp_path: "Path") -> None:
        """Counts only decisions for a specific patient."""
        logger = CDSAuditLogger(storage_dir=str(tmp_path))

        logger.log_decision(make_mock_decision(patient_id="alice"))
        logger.log_decision(make_mock_decision(patient_id="bob"))
        logger.log_decision(make_mock_decision(patient_id="alice"))

        assert logger.count_decisions(patient_id="alice") == 2
        assert logger.count_decisions(patient_id="bob") == 1

    def test_count_returns_zero_for_empty_log(self, tmp_path: "Path") -> None:
        """Returns 0 when no decisions exist."""
        logger = CDSAuditLogger(storage_dir=str(tmp_path))
        assert logger.count_decisions() == 0

    def test_count_with_since_filter(self, tmp_path: "Path") -> None:
        """Counts only decisions after a given timestamp."""
        logger = CDSAuditLogger(storage_dir=str(tmp_path))

        logger.log_decision(make_mock_decision())
        logger.log_decision(make_mock_decision())

        # Backdate the first decision
        lines = logger.log_file.read_text().strip().splitlines()
        entry = json.loads(lines[0])
        entry["timestamp"] = "2020-01-01T00:00:00+00:00"
        lines[0] = json.dumps(entry)
        logger.log_file.write_text("\n".join(lines) + "\n")

        since = datetime(2024, 1, 1, tzinfo=timezone.utc)
        assert logger.count_decisions(since=since) == 1


# ---------------------------------------------------------------------------
# Empty / Missing Log File Handling
# ---------------------------------------------------------------------------


class TestEmptyLogHandling:
    """Edge cases for empty or nonexistent log files."""

    def test_get_decision_no_file(self, tmp_path: "Path") -> None:
        """get_decision returns None when log file never created."""
        logger = CDSAuditLogger(storage_dir=str(tmp_path))
        assert logger.get_decision("any") is None

    def test_list_decisions_no_file(self, tmp_path: "Path") -> None:
        """list_decisions returns empty list when log file never created."""
        logger = CDSAuditLogger(storage_dir=str(tmp_path))
        assert logger.list_decisions() == []

    def test_count_decisions_no_file(self, tmp_path: "Path") -> None:
        """count_decisions returns 0 when log file never created."""
        logger = CDSAuditLogger(storage_dir=str(tmp_path))
        assert logger.count_decisions() == 0

    def test_log_file_with_only_blank_lines(self, tmp_path: "Path") -> None:
        """A log file containing only blank lines yields no results."""
        logger = CDSAuditLogger(storage_dir=str(tmp_path))
        logger.log_file.write_text("\n\n\n")

        assert logger.list_decisions() == []
        assert logger.count_decisions() == 0
        assert logger.get_decision("anything") is None


# ---------------------------------------------------------------------------
# Redis Pub/Sub Integration
# ---------------------------------------------------------------------------


class TestRedisIntegration:
    """Tests for optional Redis pub/sub notifications."""

    def test_publishes_to_redis_on_log(self, tmp_path: "Path") -> None:
        """Redis publish is called with decision_id and risk."""
        mock_redis = MagicMock()
        logger = CDSAuditLogger(storage_dir=str(tmp_path), redis_client=mock_redis)

        decision_id = logger.log_decision(make_mock_decision(risk="high"))

        mock_redis.publish.assert_called_once()
        call_args = mock_redis.publish.call_args
        assert call_args[0][0] == "cds:audit:new_decision"

        payload = json.loads(call_args[0][1])
        assert payload["decision_id"] == decision_id
        assert payload["risk"] == "high"

    def test_redis_failure_does_not_raise(self, tmp_path: "Path") -> None:
        """Redis publish failure is non-fatal; decision is still logged."""
        mock_redis = MagicMock()
        mock_redis.publish.side_effect = ConnectionError("Redis down")

        logger = CDSAuditLogger(storage_dir=str(tmp_path), redis_client=mock_redis)
        decision_id = logger.log_decision(make_mock_decision())

        # Decision was still written to file
        assert decision_id is not None
        entry = logger.get_decision(decision_id)
        assert entry is not None

    def test_no_redis_publish_when_client_is_none(self, tmp_path: "Path") -> None:
        """No Redis operations attempted when client is None."""
        logger = CDSAuditLogger(storage_dir=str(tmp_path))

        # Should not raise
        decision_id = logger.log_decision(make_mock_decision())
        assert decision_id is not None


# ---------------------------------------------------------------------------
# File Write Error Handling
# ---------------------------------------------------------------------------


class TestWriteErrors:
    """Tests for error handling during file writes."""

    def test_os_error_on_write_raises(self, tmp_path: "Path") -> None:
        """OSError during file write is propagated to the caller."""
        logger = CDSAuditLogger(storage_dir=str(tmp_path))

        # Make log_file point to a directory to trigger OSError
        logger.log_file.mkdir(parents=True, exist_ok=True)

        with pytest.raises(OSError):
            logger.log_decision(make_mock_decision())
