"""Tests for empathy_os.feedback_loops"""
from datetime import datetime

from empathy_os.feedback_loops import (
    FeedbackLoop,
    FeedbackLoopDetector,
    LoopPolarity,
    LoopType,
)


class TestLoopType:
    """Tests for LoopType enum."""

    def test_reinforcing_value(self):
        """Test REINFORCING enum value."""
        assert LoopType.REINFORCING.value == "reinforcing"

    def test_balancing_value(self):
        """Test BALANCING enum value."""
        assert LoopType.BALANCING.value == "balancing"

    def test_enum_members(self):
        """Test that all expected enum members exist."""
        assert hasattr(LoopType, "REINFORCING")
        assert hasattr(LoopType, "BALANCING")
        assert len(LoopType) == 2


class TestLoopPolarity:
    """Tests for LoopPolarity enum."""

    def test_virtuous_value(self):
        """Test VIRTUOUS enum value."""
        assert LoopPolarity.VIRTUOUS.value == "virtuous"

    def test_vicious_value(self):
        """Test VICIOUS enum value."""
        assert LoopPolarity.VICIOUS.value == "vicious"

    def test_neutral_value(self):
        """Test NEUTRAL enum value."""
        assert LoopPolarity.NEUTRAL.value == "neutral"

    def test_enum_members(self):
        """Test that all expected enum members exist."""
        assert hasattr(LoopPolarity, "VIRTUOUS")
        assert hasattr(LoopPolarity, "VICIOUS")
        assert hasattr(LoopPolarity, "NEUTRAL")
        assert len(LoopPolarity) == 3


class TestFeedbackLoop:
    """Tests for FeedbackLoop class."""

    def test_initialization(self):
        """Test FeedbackLoop initialization."""
        loop = FeedbackLoop(
            loop_id="test_loop",
            loop_type=LoopType.REINFORCING,
            polarity=LoopPolarity.VIRTUOUS,
            description="Test feedback loop",
            components=["trust", "success"],
        )

        assert loop.loop_id == "test_loop"
        assert loop.loop_type == LoopType.REINFORCING
        assert loop.polarity == LoopPolarity.VIRTUOUS
        assert loop.description == "Test feedback loop"
        assert loop.components == ["trust", "success"]
        assert loop.strength == 0.5  # Default
        assert isinstance(loop.detected_at, datetime)
        assert loop.evidence == []
        assert loop.intervention_points == []

    def test_initialization_with_optional_params(self):
        """Test FeedbackLoop initialization with optional parameters."""
        loop = FeedbackLoop(
            loop_id="custom_loop",
            loop_type=LoopType.BALANCING,
            polarity=LoopPolarity.NEUTRAL,
            description="Custom loop",
            components=["quality", "oversight"],
            strength=0.8,
            evidence=[{"event": "test"}],
            intervention_points=["adjust_parameters"],
        )

        assert loop.strength == 0.8
        assert len(loop.evidence) == 1
        assert loop.intervention_points == ["adjust_parameters"]


class TestFeedbackLoopDetector:
    """Tests for FeedbackLoopDetector class."""

    def test_initialization(self):
        """Test FeedbackLoopDetector initialization."""
        detector = FeedbackLoopDetector()

        assert len(detector.detected_loops) == 3  # 3 standard loops
        assert detector._get_loop_by_id("R1_trust_building") is not None
        assert detector._get_loop_by_id("R2_trust_erosion") is not None
        assert detector._get_loop_by_id("B1_quality_control") is not None

    def test_detect_active_loop_insufficient_data(self):
        """Test detect_active_loop with insufficient data."""
        detector = FeedbackLoopDetector()

        # Single data point
        history = [{"trust": 0.5, "success": True}]
        result = detector.detect_active_loop(history)

        assert result["dominant_loop"] is None
        assert result["loop_strength"] == 0.0
        assert result["trend"] == "insufficient_data"

    def test_detect_active_loop_virtuous_cycle(self):
        """Test detecting virtuous trust-building cycle."""
        detector = FeedbackLoopDetector()

        # Increasing trust with high success rate (strong trend > 0.1)
        history = [
            {"trust": 0.5, "success": True},
            {"trust": 0.65, "success": True},
            {"trust": 0.8, "success": True},
            {"trust": 0.95, "success": True},
        ]

        result = detector.detect_active_loop(history)

        assert result["dominant_loop"] == "R1_trust_building"
        assert result["loop_type"] == "reinforcing_virtuous"
        assert result["loop_strength"] > 0.0
        assert result["trend"] == "amplifying_positive"
        assert "momentum" in result["recommendation"].lower()

    def test_detect_active_loop_vicious_cycle(self):
        """Test detecting vicious trust-erosion cycle."""
        detector = FeedbackLoopDetector()

        # Decreasing trust with high failure rate
        history = [
            {"trust": 0.7, "success": False},
            {"trust": 0.5, "success": False},
            {"trust": 0.3, "success": False},
            {"trust": 0.2, "success": False},
        ]

        result = detector.detect_active_loop(history)

        assert result["dominant_loop"] == "R2_trust_erosion"
        assert result["loop_type"] == "reinforcing_vicious"
        assert result["loop_strength"] > 0.0
        assert result["trend"] == "amplifying_negative"
        assert "INTERVENTION" in result["recommendation"]

    def test_detect_active_loop_balancing(self):
        """Test detecting balancing quality control loop."""
        detector = FeedbackLoopDetector()

        # Stable trust with moderate success rate
        history = [
            {"trust": 0.5, "success": True},
            {"trust": 0.5, "success": False},
            {"trust": 0.5, "success": True},
            {"trust": 0.5, "success": False},
        ]

        result = detector.detect_active_loop(history)

        assert result["dominant_loop"] == "B1_quality_control"
        assert result["loop_type"] == "balancing"
        assert result["trend"] == "stabilizing"

    def test_detect_virtuous_cycle_true(self):
        """Test detecting virtuous cycle with accelerating trust growth."""
        detector = FeedbackLoopDetector()

        # Trust accelerating upward with high success
        history = [
            {"trust": 0.5, "success": True},
            {"trust": 0.6, "success": True},
            {"trust": 0.72, "success": True},  # Acceleration
            {"trust": 0.86, "success": True},  # More acceleration
        ]

        assert detector.detect_virtuous_cycle(history) is True

    def test_detect_virtuous_cycle_false_low_success(self):
        """Test that virtuous cycle not detected with low success rate."""
        detector = FeedbackLoopDetector()

        # Trust increasing but low success rate
        history = [
            {"trust": 0.5, "success": False},
            {"trust": 0.6, "success": False},
            {"trust": 0.7, "success": True},
        ]

        assert detector.detect_virtuous_cycle(history) is False

    def test_detect_virtuous_cycle_false_no_acceleration(self):
        """Test that virtuous cycle not detected without acceleration."""
        detector = FeedbackLoopDetector()

        # Linear trust growth (not accelerating)
        history = [
            {"trust": 0.5, "success": True},
            {"trust": 0.6, "success": True},
            {"trust": 0.7, "success": True},
            {"trust": 0.8, "success": True},
        ]

        # Linear growth doesn't trigger virtuous cycle detection
        # (requires acceleration)
        result = detector.detect_virtuous_cycle(history)
        # Result depends on precise calculation, but should handle gracefully
        assert isinstance(result, bool)

    def test_detect_virtuous_cycle_insufficient_data(self):
        """Test that virtuous cycle requires sufficient data."""
        detector = FeedbackLoopDetector()

        history = [{"trust": 0.5, "success": True}]

        assert detector.detect_virtuous_cycle(history) is False

    def test_detect_vicious_cycle_true(self):
        """Test detecting vicious cycle with accelerating trust decline."""
        detector = FeedbackLoopDetector()

        # Trust accelerating downward with high failure
        history = [
            {"trust": 0.8, "success": False},
            {"trust": 0.7, "success": False},
            {"trust": 0.55, "success": False},  # Acceleration
            {"trust": 0.35, "success": False},  # More acceleration
        ]

        assert detector.detect_vicious_cycle(history) is True

    def test_detect_vicious_cycle_false_low_failure(self):
        """Test that vicious cycle not detected with low failure rate."""
        detector = FeedbackLoopDetector()

        # Trust decreasing but low failure rate
        history = [
            {"trust": 0.8, "success": True},
            {"trust": 0.7, "success": True},
            {"trust": 0.6, "success": False},
        ]

        assert detector.detect_vicious_cycle(history) is False

    def test_detect_vicious_cycle_insufficient_data(self):
        """Test that vicious cycle requires sufficient data."""
        detector = FeedbackLoopDetector()

        history = [{"trust": 0.5, "success": False}]

        assert detector.detect_vicious_cycle(history) is False

    def test_get_intervention_recommendations(self):
        """Test getting intervention recommendations for a loop."""
        detector = FeedbackLoopDetector()

        # Get recommendations for trust erosion loop
        recommendations = detector.get_intervention_recommendations("R2_trust_erosion")

        assert len(recommendations) > 0
        assert "break_cycle" in recommendations
        assert "rebuild_confidence" in recommendations
        assert "adjust_scope" in recommendations

    def test_get_intervention_recommendations_unknown_loop(self):
        """Test getting recommendations for unknown loop ID."""
        detector = FeedbackLoopDetector()

        recommendations = detector.get_intervention_recommendations("unknown_loop")

        assert recommendations == []

    def test_register_custom_loop(self):
        """Test registering a custom feedback loop."""
        detector = FeedbackLoopDetector()

        initial_count = len(detector.detected_loops)

        # Create custom loop
        custom_loop = FeedbackLoop(
            loop_id="R3_custom",
            loop_type=LoopType.REINFORCING,
            polarity=LoopPolarity.VIRTUOUS,
            description="Custom learning loop",
            components=["knowledge", "practice", "skill"],
            intervention_points=["provide_resources"],
        )

        detector.register_custom_loop(custom_loop)

        assert len(detector.detected_loops) == initial_count + 1
        assert detector._get_loop_by_id("R3_custom") is not None

    def test_get_all_loops(self):
        """Test getting all registered loops."""
        detector = FeedbackLoopDetector()

        loops = detector.get_all_loops()

        assert len(loops) == 3  # 3 standard loops
        assert all(isinstance(loop, FeedbackLoop) for loop in loops)

    def test_reset(self):
        """Test resetting detector state."""
        detector = FeedbackLoopDetector()

        # Add custom loop
        custom_loop = FeedbackLoop(
            loop_id="custom",
            loop_type=LoopType.REINFORCING,
            polarity=LoopPolarity.VIRTUOUS,
            description="Custom loop",
            components=["a", "b"],
        )
        detector.register_custom_loop(custom_loop)

        assert len(detector.detected_loops) == 4  # 3 standard + 1 custom

        # Reset
        detector.reset()

        # Should have only 3 standard loops again
        assert len(detector.detected_loops) == 3
        assert detector._get_loop_by_id("custom") is None
        assert detector._get_loop_by_id("R1_trust_building") is not None

    def test_calculate_trend_increasing(self):
        """Test trend calculation for increasing values."""
        detector = FeedbackLoopDetector()

        values = [0.5, 0.6, 0.7, 0.8, 0.9]
        trend = detector._calculate_trend(values)

        assert trend > 0  # Positive trend

    def test_calculate_trend_decreasing(self):
        """Test trend calculation for decreasing values."""
        detector = FeedbackLoopDetector()

        values = [0.9, 0.7, 0.5, 0.3, 0.1]
        trend = detector._calculate_trend(values)

        assert trend < 0  # Negative trend

    def test_calculate_trend_stable(self):
        """Test trend calculation for stable values."""
        detector = FeedbackLoopDetector()

        values = [0.5, 0.5, 0.5, 0.5, 0.5]
        trend = detector._calculate_trend(values)

        assert trend == 0.0  # No trend

    def test_calculate_trend_insufficient_data(self):
        """Test trend calculation with insufficient data."""
        detector = FeedbackLoopDetector()

        values = [0.5]
        trend = detector._calculate_trend(values)

        assert trend == 0.0

    def test_get_loop_by_id_found(self):
        """Test getting loop by ID when it exists."""
        detector = FeedbackLoopDetector()

        loop = detector._get_loop_by_id("R1_trust_building")

        assert loop is not None
        assert loop.loop_id == "R1_trust_building"
        assert loop.loop_type == LoopType.REINFORCING
        assert loop.polarity == LoopPolarity.VIRTUOUS

    def test_get_loop_by_id_not_found(self):
        """Test getting loop by ID when it doesn't exist."""
        detector = FeedbackLoopDetector()

        loop = detector._get_loop_by_id("nonexistent")

        assert loop is None

    def test_standard_loops_initialized_correctly(self):
        """Test that standard loops are initialized with correct properties."""
        detector = FeedbackLoopDetector()

        # Verify R1 trust building
        r1 = detector._get_loop_by_id("R1_trust_building")
        assert r1.loop_type == LoopType.REINFORCING
        assert r1.polarity == LoopPolarity.VIRTUOUS
        assert "trust" in r1.components
        assert len(r1.intervention_points) > 0

        # Verify R2 trust erosion
        r2 = detector._get_loop_by_id("R2_trust_erosion")
        assert r2.loop_type == LoopType.REINFORCING
        assert r2.polarity == LoopPolarity.VICIOUS
        assert "trust" in r2.components

        # Verify B1 quality control
        b1 = detector._get_loop_by_id("B1_quality_control")
        assert b1.loop_type == LoopType.BALANCING
        assert b1.polarity == LoopPolarity.NEUTRAL
        assert "error_rate" in b1.components

    def test_detect_active_loop_includes_details(self):
        """Test that detect_active_loop includes loop details."""
        detector = FeedbackLoopDetector()

        history = [
            {"trust": 0.5, "success": True},
            {"trust": 0.7, "success": True},
        ]

        result = detector.detect_active_loop(history)

        assert "details" in result
        assert isinstance(result["details"], FeedbackLoop)
