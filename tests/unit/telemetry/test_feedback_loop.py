"""Unit tests for Feedback Loop (Pattern 6).

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from datetime import datetime
from unittest.mock import Mock

from attune.telemetry.feedback_loop import (
    FeedbackEntry,
    FeedbackLoop,
    ModelTier,
    QualityStats,
    TierRecommendation,
)


class TestFeedbackEntry:
    """Test FeedbackEntry dataclass."""

    def test_feedback_entry_creation(self):
        """Test creating a FeedbackEntry."""
        entry = FeedbackEntry(
            feedback_id="feedback_abc123",
            workflow_name="code-review",
            stage_name="analysis",
            tier="cheap",
            quality_score=0.85,
            timestamp=datetime(2026, 1, 27, 12, 0, 0),
            metadata={"tokens": 150, "latency_ms": 1200},
        )

        assert entry.feedback_id == "feedback_abc123"
        assert entry.workflow_name == "code-review"
        assert entry.stage_name == "analysis"
        assert entry.tier == "cheap"
        assert entry.quality_score == 0.85
        assert entry.metadata["tokens"] == 150

    def test_to_dict(self):
        """Test converting FeedbackEntry to dict."""
        entry = FeedbackEntry(
            feedback_id="feedback_abc123",
            workflow_name="code-review",
            stage_name="analysis",
            tier="cheap",
            quality_score=0.85,
            timestamp=datetime(2026, 1, 27, 12, 0, 0),
            metadata={"tokens": 150},
        )

        entry_dict = entry.to_dict()

        assert entry_dict["feedback_id"] == "feedback_abc123"
        assert entry_dict["workflow_name"] == "code-review"
        assert entry_dict["quality_score"] == 0.85
        assert entry_dict["timestamp"] == "2026-01-27T12:00:00"

    def test_from_dict(self):
        """Test creating FeedbackEntry from dict."""
        data = {
            "feedback_id": "feedback_xyz789",
            "workflow_name": "test-generation",
            "stage_name": "analysis",
            "tier": "capable",
            "quality_score": 0.92,
            "timestamp": "2026-01-27T12:00:00",
            "metadata": {"tokens": 250},
        }

        entry = FeedbackEntry.from_dict(data)

        assert entry.feedback_id == "feedback_xyz789"
        assert entry.workflow_name == "test-generation"
        assert entry.quality_score == 0.92


class TestQualityStats:
    """Test QualityStats dataclass."""

    def test_quality_stats_creation(self):
        """Test creating QualityStats."""
        stats = QualityStats(
            workflow_name="code-review",
            stage_name="analysis",
            tier="cheap",
            avg_quality=0.82,
            min_quality=0.65,
            max_quality=0.95,
            sample_count=25,
            recent_trend=0.15,
        )

        assert stats.workflow_name == "code-review"
        assert stats.avg_quality == 0.82
        assert stats.sample_count == 25
        assert stats.recent_trend == 0.15


class TestTierRecommendation:
    """Test TierRecommendation dataclass."""

    def test_tier_recommendation_creation(self):
        """Test creating TierRecommendation."""
        recommendation = TierRecommendation(
            current_tier="cheap",
            recommended_tier="capable",
            confidence=0.85,
            reason="Low quality (0.62) - upgrade for better results",
            stats={
                "cheap": QualityStats(
                    workflow_name="test",
                    stage_name="analysis",
                    tier="cheap",
                    avg_quality=0.62,
                    min_quality=0.50,
                    max_quality=0.75,
                    sample_count=15,
                    recent_trend=-0.1,
                )
            },
        )

        assert recommendation.current_tier == "cheap"
        assert recommendation.recommended_tier == "capable"
        assert recommendation.confidence == 0.85
        assert "upgrade" in recommendation.reason


class TestFeedbackLoop:
    """Test FeedbackLoop class."""

    def test_init_without_memory(self):
        """Test FeedbackLoop initialization without memory backend."""
        loop = FeedbackLoop()

        assert loop.memory is None

    def test_init_with_memory(self):
        """Test FeedbackLoop initialization with memory backend."""
        mock_memory = Mock()
        loop = FeedbackLoop(memory=mock_memory)

        assert loop.memory == mock_memory

    def test_record_feedback_without_memory(self):
        """Test record_feedback returns empty string when no memory."""
        loop = FeedbackLoop()

        feedback_id = loop.record_feedback(
            workflow_name="test",
            stage_name="analysis",
            tier=ModelTier.CHEAP,
            quality_score=0.85,
        )

        assert feedback_id == ""

    def test_record_feedback_validates_quality_score(self):
        """Test record_feedback validates quality score range."""
        mock_client = Mock()
        mock_memory = Mock(spec=["_client"])
        mock_memory._client = mock_client

        loop = FeedbackLoop(memory=mock_memory)

        # Test invalid scores
        result = loop.record_feedback(
            workflow_name="test", stage_name="analysis", tier="cheap", quality_score=1.5
        )
        assert result == ""

        result = loop.record_feedback(
            workflow_name="test", stage_name="analysis", tier="cheap", quality_score=-0.1
        )
        assert result == ""

    def test_record_feedback_stores_entry(self):
        """Test that record_feedback stores feedback in memory."""
        mock_client = Mock()
        mock_memory = Mock(spec=["_client"])
        mock_memory._client = mock_client

        loop = FeedbackLoop(memory=mock_memory)

        feedback_id = loop.record_feedback(
            workflow_name="code-review",
            stage_name="analysis",
            tier=ModelTier.CHEAP,
            quality_score=0.85,
            metadata={"tokens": 150},
        )

        # Should have stored feedback
        assert mock_client.setex.called
        assert feedback_id.startswith("feedback_")

        # Verify key format
        call_args = mock_client.setex.call_args[0]
        assert call_args[0].startswith("feedback:code-review:analysis:cheap:")
        assert call_args[1] == loop.FEEDBACK_TTL  # 7 days

    def test_record_feedback_converts_model_tier_enum(self):
        """Test that record_feedback converts ModelTier enum to string."""
        mock_client = Mock()
        mock_memory = Mock(spec=["_client"])
        mock_memory._client = mock_client

        loop = FeedbackLoop(memory=mock_memory)

        # Use enum
        feedback_id = loop.record_feedback(
            workflow_name="test",
            stage_name="analysis",
            tier=ModelTier.CAPABLE,
            quality_score=0.88,
        )

        assert feedback_id != ""

        # Verify tier stored as string
        call_args = mock_client.setex.call_args[0]
        assert "capable" in call_args[0]

    def test_get_feedback_history_empty(self):
        """Test get_feedback_history returns empty list when no data."""
        mock_client = Mock()
        mock_client.scan_iter.return_value = []

        mock_memory = Mock(spec=["_client"])
        mock_memory._client = mock_client

        loop = FeedbackLoop(memory=mock_memory)

        history = loop.get_feedback_history("test-workflow", "analysis")

        assert history == []

    def test_get_feedback_history_filters_by_tier(self):
        """Test get_feedback_history filters by tier."""
        mock_client = Mock()

        all_keys = [
            b"feedback:test:analysis:cheap:abc123",
            b"feedback:test:analysis:capable:xyz789",
        ]

        # Mock keys() to filter based on pattern
        def mock_scan_iter(match="", count=100):
            if "cheap" in match:
                return [k for k in all_keys if b"cheap" in k]
            elif "capable" in match:
                return [k for k in all_keys if b"capable" in k]
            else:
                return all_keys

        mock_client.scan_iter.side_effect = mock_scan_iter

        import json

        cheap_data = {
            "feedback_id": "feedback_abc123",
            "workflow_name": "test",
            "stage_name": "analysis",
            "tier": "cheap",
            "quality_score": 0.75,
            "timestamp": "2026-01-27T12:00:00",
            "metadata": {},
        }

        capable_data = {
            "feedback_id": "feedback_xyz789",
            "workflow_name": "test",
            "stage_name": "analysis",
            "tier": "capable",
            "quality_score": 0.88,
            "timestamp": "2026-01-27T12:05:00",
            "metadata": {},
        }

        def mock_get(key):
            if isinstance(key, bytes):
                key = key.decode()

            if "cheap" in key:
                return json.dumps(cheap_data).encode()
            elif "capable" in key:
                return json.dumps(capable_data).encode()
            return None

        mock_client.get.side_effect = mock_get

        mock_memory = Mock(spec=["_client"])
        mock_memory._client = mock_client

        loop = FeedbackLoop(memory=mock_memory)

        # Get only cheap tier feedback
        history = loop.get_feedback_history("test", "analysis", tier="cheap")

        # Should filter to only cheap tier
        assert len(history) == 1
        assert history[0].tier == "cheap"

    def test_get_quality_stats_no_data(self):
        """Test get_quality_stats returns None when no data."""
        mock_client = Mock()
        mock_client.scan_iter.return_value = []

        mock_memory = Mock(spec=["_client"])
        mock_memory._client = mock_client

        loop = FeedbackLoop(memory=mock_memory)

        stats = loop.get_quality_stats("test", "analysis")

        assert stats is None

    def test_get_quality_stats_calculates_correctly(self):
        """Test get_quality_stats calculates statistics correctly."""
        mock_client = Mock()

        # Create 10 feedback entries
        all_keys = [f"feedback:test:analysis:cheap:id{i}".encode() for i in range(10)]

        # Mock keys() to return all_keys when pattern matches
        def mock_scan_iter(match="", count=100):
            if "cheap" in match:
                return all_keys
            return []

        mock_client.scan_iter.side_effect = mock_scan_iter

        import json

        def mock_get(key):
            # Quality scores: 0.5, 0.6, 0.7, 0.8, 0.9, 0.6, 0.7, 0.8, 0.9, 1.0
            key_str = key.decode() if isinstance(key, bytes) else key
            idx = int(key_str.split("id")[1])
            score = 0.5 + (idx * 0.1) if idx < 5 else 0.5 + ((idx - 5) * 0.1) + 0.1

            data = {
                "feedback_id": f"feedback_id{idx}",
                "workflow_name": "test",
                "stage_name": "analysis",
                "tier": "cheap",
                "quality_score": score,
                "timestamp": f"2026-01-27T12:{idx:02d}:00",
                "metadata": {},
            }
            return json.dumps(data).encode()

        mock_client.get.side_effect = mock_get

        mock_memory = Mock(spec=["_client"])
        mock_memory._client = mock_client

        loop = FeedbackLoop(memory=mock_memory)

        stats = loop.get_quality_stats("test", "analysis", tier="cheap")

        assert stats is not None
        assert stats.sample_count == 10
        assert stats.min_quality == 0.5
        assert stats.max_quality == 1.0
        # Average: (0.5+0.6+0.7+0.8+0.9 + 0.6+0.7+0.8+0.9+1.0) / 10 = 0.75
        assert abs(stats.avg_quality - 0.75) < 0.01

    def test_recommend_tier_no_data(self):
        """Test recommend_tier with no feedback data."""
        mock_client = Mock()
        mock_client.scan_iter.return_value = []

        mock_memory = Mock(spec=["_client"])
        mock_memory._client = mock_client

        loop = FeedbackLoop(memory=mock_memory)

        recommendation = loop.recommend_tier("test", "analysis", current_tier="cheap")

        assert recommendation.current_tier == "cheap"
        assert recommendation.recommended_tier == "cheap"
        assert recommendation.confidence == 0.0
        assert "No feedback data" in recommendation.reason

    def test_recommend_tier_insufficient_samples(self):
        """Test recommend_tier with insufficient samples."""
        mock_client = Mock()

        # Create 5 feedback entries (less than MIN_SAMPLES=10)
        all_keys = [f"feedback:test:analysis:cheap:id{i}".encode() for i in range(5)]

        # Mock keys() to return based on pattern
        def mock_scan_iter(match="", count=100):
            if "cheap" in match:
                return all_keys
            return []

        mock_client.scan_iter.side_effect = mock_scan_iter

        import json

        def mock_get(key):
            key_str = key.decode() if isinstance(key, bytes) else key
            idx = int(key_str.split("id")[1])
            data = {
                "feedback_id": f"feedback_id{idx}",
                "workflow_name": "test",
                "stage_name": "analysis",
                "tier": "cheap",
                "quality_score": 0.8,
                "timestamp": f"2026-01-27T12:{idx:02d}:00",
                "metadata": {},
            }
            return json.dumps(data).encode()

        mock_client.get.side_effect = mock_get

        mock_memory = Mock(spec=["_client"])
        mock_memory._client = mock_client

        loop = FeedbackLoop(memory=mock_memory)

        recommendation = loop.recommend_tier("test", "analysis", current_tier="cheap")

        assert recommendation.current_tier == "cheap"
        assert recommendation.recommended_tier == "cheap"
        assert recommendation.confidence == 0.0
        assert "Insufficient data" in recommendation.reason

    def test_recommend_tier_upgrade_on_low_quality(self):
        """Test recommend_tier suggests upgrade when quality is low."""
        mock_client = Mock()

        # Create 15 feedback entries with low quality (0.6)
        all_keys = [f"feedback:test:analysis:cheap:id{i}".encode() for i in range(15)]

        # Mock keys() to return based on pattern
        def mock_scan_iter(match="", count=100):
            if "cheap" in match:
                return all_keys
            return []

        mock_client.scan_iter.side_effect = mock_scan_iter

        import json

        def mock_get(key):
            key_str = key.decode() if isinstance(key, bytes) else key
            idx = int(key_str.split("id")[1])
            data = {
                "feedback_id": f"feedback_id{idx}",
                "workflow_name": "test",
                "stage_name": "analysis",
                "tier": "cheap",
                "quality_score": 0.6,  # Below QUALITY_THRESHOLD (0.7)
                "timestamp": f"2026-01-27T12:{idx:02d}:00",
                "metadata": {},
            }
            return json.dumps(data).encode()

        mock_client.get.side_effect = mock_get

        mock_memory = Mock(spec=["_client"])
        mock_memory._client = mock_client

        loop = FeedbackLoop(memory=mock_memory)

        recommendation = loop.recommend_tier("test", "analysis", current_tier="cheap")

        assert recommendation.current_tier == "cheap"
        assert recommendation.recommended_tier == "capable"
        assert "upgrade" in recommendation.reason.lower()

    def test_recommend_tier_maintain_on_acceptable_quality(self):
        """Test recommend_tier maintains tier when quality is acceptable."""
        mock_client = Mock()

        # Create 15 feedback entries with acceptable quality (0.8)
        all_keys = [f"feedback:test:analysis:cheap:id{i}".encode() for i in range(15)]

        # Mock keys() to return based on pattern
        def mock_scan_iter(match="", count=100):
            if "cheap" in match:
                return all_keys
            return []

        mock_client.scan_iter.side_effect = mock_scan_iter

        import json

        def mock_get(key):
            key_str = key.decode() if isinstance(key, bytes) else key
            idx = int(key_str.split("id")[1])
            data = {
                "feedback_id": f"feedback_id{idx}",
                "workflow_name": "test",
                "stage_name": "analysis",
                "tier": "cheap",
                "quality_score": 0.8,  # Above QUALITY_THRESHOLD (0.7), below 0.9
                "timestamp": f"2026-01-27T12:{idx:02d}:00",
                "metadata": {},
            }
            return json.dumps(data).encode()

        mock_client.get.side_effect = mock_get

        mock_memory = Mock(spec=["_client"])
        mock_memory._client = mock_client

        loop = FeedbackLoop(memory=mock_memory)

        recommendation = loop.recommend_tier("test", "analysis", current_tier="cheap")

        assert recommendation.current_tier == "cheap"
        assert recommendation.recommended_tier == "cheap"
        assert "maintain" in recommendation.reason.lower()

    def test_recommend_tier_already_premium(self):
        """Test recommend_tier when already using premium tier."""
        mock_client = Mock()

        # Create 15 feedback entries with low quality on premium tier
        all_keys = [f"feedback:test:analysis:premium:id{i}".encode() for i in range(15)]

        # Mock keys() to return based on pattern
        def mock_scan_iter(match="", count=100):
            if "premium" in match:
                return all_keys
            return []

        mock_client.scan_iter.side_effect = mock_scan_iter

        import json

        def mock_get(key):
            key_str = key.decode() if isinstance(key, bytes) else key
            idx = int(key_str.split("id")[1])
            data = {
                "feedback_id": f"feedback_id{idx}",
                "workflow_name": "test",
                "stage_name": "analysis",
                "tier": "premium",
                "quality_score": 0.6,  # Low quality even on premium
                "timestamp": f"2026-01-27T12:{idx:02d}:00",
                "metadata": {},
            }
            return json.dumps(data).encode()

        mock_client.get.side_effect = mock_get

        mock_memory = Mock(spec=["_client"])
        mock_memory._client = mock_client

        loop = FeedbackLoop(memory=mock_memory)

        recommendation = loop.recommend_tier("test", "analysis", current_tier="premium")

        assert recommendation.current_tier == "premium"
        assert recommendation.recommended_tier == "premium"
        assert "already using premium" in recommendation.reason.lower()

    def test_get_underperforming_stages_no_stages(self):
        """Test get_underperforming_stages returns empty when no stages."""
        mock_client = Mock()
        mock_client.scan_iter.return_value = []

        mock_memory = Mock(spec=["_client"])
        mock_memory._client = mock_client

        loop = FeedbackLoop(memory=mock_memory)

        underperforming = loop.get_underperforming_stages("test-workflow")

        assert underperforming == []

    def test_get_underperforming_stages_filters_by_threshold(self):
        """Test get_underperforming_stages filters by quality threshold."""
        mock_client = Mock()

        # Create feedback for 2 stages: one good, one bad
        all_keys = [
            b"feedback:test:stage1:cheap:id1",
            b"feedback:test:stage1:cheap:id2",
            b"feedback:test:stage2:cheap:id3",
            b"feedback:test:stage2:cheap:id4",
        ]

        # Mock keys() to return all keys for workflow pattern, or specific stage keys
        def mock_scan_iter(match="", count=100):
            if match == "feedback:test:*":
                return all_keys
            elif "stage1" in match:
                return [k for k in all_keys if b"stage1" in k]
            elif "stage2" in match:
                return [k for k in all_keys if b"stage2" in k]
            return []

        mock_client.scan_iter.side_effect = mock_scan_iter

        import json

        def mock_get(key):
            key_str = key.decode() if isinstance(key, bytes) else key

            if "stage1" in key_str:
                # Good quality stage
                data = {
                    "feedback_id": "id1",
                    "workflow_name": "test",
                    "stage_name": "stage1",
                    "tier": "cheap",
                    "quality_score": 0.85,
                    "timestamp": "2026-01-27T12:00:00",
                    "metadata": {},
                }
            else:
                # Poor quality stage
                data = {
                    "feedback_id": "id3",
                    "workflow_name": "test",
                    "stage_name": "stage2",
                    "tier": "cheap",
                    "quality_score": 0.55,
                    "timestamp": "2026-01-27T12:00:00",
                    "metadata": {},
                }
            return json.dumps(data).encode()

        mock_client.get.side_effect = mock_get

        mock_memory = Mock(spec=["_client"])
        mock_memory._client = mock_client

        loop = FeedbackLoop(memory=mock_memory)

        underperforming = loop.get_underperforming_stages("test", quality_threshold=0.7)

        # Should only return stage2 (quality 0.55 < 0.7)
        assert len(underperforming) == 1
        assert underperforming[0][0] == "stage2/cheap"  # Stage name includes tier
        assert underperforming[0][1].avg_quality < 0.7

    def test_clear_feedback_no_stage(self):
        """Test clear_feedback clears all stages for workflow."""
        mock_client = Mock()
        mock_client.scan_iter.return_value = [
            b"feedback:test:stage1:cheap:id1",
            b"feedback:test:stage2:cheap:id2",
        ]
        mock_client.delete.return_value = 2

        mock_memory = Mock(spec=["_client"])
        mock_memory._client = mock_client

        loop = FeedbackLoop(memory=mock_memory)

        cleared = loop.clear_feedback("test")

        assert cleared == 2
        assert mock_client.delete.called

    def test_clear_feedback_specific_stage(self):
        """Test clear_feedback clears only specified stage."""
        mock_client = Mock()
        mock_client.scan_iter.return_value = [b"feedback:test:stage1:cheap:id1"]
        mock_client.delete.return_value = 1

        mock_memory = Mock(spec=["_client"])
        mock_memory._client = mock_client

        loop = FeedbackLoop(memory=mock_memory)

        cleared = loop.clear_feedback("test", stage_name="stage1")

        assert cleared == 1

        # Verify pattern includes stage name
        mock_client.scan_iter.assert_called_with(match="feedback:test:stage1:*", count=100)
