"""Behavioral tests for exceptions.py - Custom exception classes.

Tests Given/When/Then pattern for exception initialization and behavior.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

import pytest

from attune.exceptions import (
    CollaborationStateError,
    ConfidenceThresholdError,
    EmpathyFrameworkError,
    EmpathyLevelError,
    FeedbackLoopError,
    LeveragePointError,
    PatternNotFoundError,
    TrustThresholdError,
    ValidationError,
)


class TestEmpathyFrameworkError:
    """Behavioral tests for base EmpathyFrameworkError exception."""

    def test_base_exception_can_be_raised(self):
        """Given: Base exception class
        When: Exception is raised with message
        Then: Exception is caught with correct message."""
        # Given
        error_message = "Test error message"

        # When/Then
        with pytest.raises(EmpathyFrameworkError, match=error_message):
            raise EmpathyFrameworkError(error_message)

    def test_base_exception_is_exception_subclass(self):
        """Given: Base exception class
        When: Checking inheritance
        Then: It inherits from Python's Exception."""
        # Given/When
        error = EmpathyFrameworkError("test")

        # Then
        assert isinstance(error, Exception)

    def test_base_exception_can_be_caught_broadly(self):
        """Given: Any framework exception
        When: Catching with base class
        Then: All framework exceptions are caught."""
        # Given
        exceptions = [
            ValidationError("test"),
            PatternNotFoundError("test_pattern"),
            TrustThresholdError(0.5, 0.8),
        ]

        # When/Then
        for exc in exceptions:
            with pytest.raises(EmpathyFrameworkError):
                raise exc


class TestValidationError:
    """Behavioral tests for ValidationError exception."""

    def test_validation_error_can_be_raised(self):
        """Given: ValidationError class
        When: Raised with validation message
        Then: Exception carries message."""
        # Given
        message = "Invalid input: expected string, got int"

        # When/Then
        with pytest.raises(ValidationError, match=message):
            raise ValidationError(message)

    def test_validation_error_inherits_from_framework_error(self):
        """Given: ValidationError instance
        When: Checking type
        Then: It is a framework error."""
        # Given/When
        error = ValidationError("test")

        # Then
        assert isinstance(error, EmpathyFrameworkError)


class TestPatternNotFoundError:
    """Behavioral tests for PatternNotFoundError exception."""

    def test_pattern_not_found_stores_pattern_id(self):
        """Given: Pattern ID that doesn't exist
        When: PatternNotFoundError raised
        Then: Pattern ID is accessible."""
        # Given
        pattern_id = "nonexistent_pattern_123"

        # When
        try:
            raise PatternNotFoundError(pattern_id)
        except PatternNotFoundError as e:
            # Then
            assert e.pattern_id == pattern_id

    def test_pattern_not_found_has_default_message(self):
        """Given: Pattern ID
        When: No custom message provided
        Then: Default message includes pattern ID."""
        # Given
        pattern_id = "missing_pattern"

        # When/Then
        with pytest.raises(PatternNotFoundError, match=f"Pattern not found: {pattern_id}"):
            raise PatternNotFoundError(pattern_id)

    def test_pattern_not_found_accepts_custom_message(self):
        """Given: Pattern ID and custom message
        When: Exception raised
        Then: Custom message is used."""
        # Given
        pattern_id = "test_pattern"
        custom_message = "Custom error: pattern lookup failed"

        # When/Then
        with pytest.raises(PatternNotFoundError, match=custom_message):
            raise PatternNotFoundError(pattern_id, custom_message)


class TestTrustThresholdError:
    """Behavioral tests for TrustThresholdError exception."""

    def test_trust_threshold_stores_trust_levels(self):
        """Given: Current and required trust levels
        When: TrustThresholdError raised
        Then: Both levels are accessible."""
        # Given
        current = 0.4
        required = 0.7

        # When
        try:
            raise TrustThresholdError(current, required)
        except TrustThresholdError as e:
            # Then
            assert e.current_trust == current
            assert e.required_trust == required

    def test_trust_threshold_has_default_message(self):
        """Given: Trust levels
        When: No custom message provided
        Then: Default message shows both levels."""
        # Given
        current = 0.3
        required = 0.8

        # When/Then
        with pytest.raises(
            TrustThresholdError, match=f"Trust level {current:.2f} is below required {required:.2f}"
        ):
            raise TrustThresholdError(current, required)

    def test_trust_threshold_accepts_custom_message(self):
        """Given: Trust levels and custom message
        When: Exception raised
        Then: Custom message is used."""
        # Given
        current = 0.5
        required = 0.9
        custom_message = "Trust erosion detected"

        # When/Then
        with pytest.raises(TrustThresholdError, match=custom_message):
            raise TrustThresholdError(current, required, custom_message)

    def test_trust_threshold_handles_edge_values(self):
        """Given: Edge case trust values (0.0, 1.0)
        When: Exception raised
        Then: Values are stored correctly."""
        # Given
        current = 0.0
        required = 1.0

        # When
        try:
            raise TrustThresholdError(current, required)
        except TrustThresholdError as e:
            # Then
            assert e.current_trust == 0.0
            assert e.required_trust == 1.0


class TestConfidenceThresholdError:
    """Behavioral tests for ConfidenceThresholdError exception."""

    def test_confidence_threshold_stores_values(self):
        """Given: Confidence and threshold values
        When: ConfidenceThresholdError raised
        Then: Both values are accessible."""
        # Given
        confidence = 0.6
        threshold = 0.85

        # When
        try:
            raise ConfidenceThresholdError(confidence, threshold)
        except ConfidenceThresholdError as e:
            # Then
            assert e.confidence == confidence
            assert e.threshold == threshold

    def test_confidence_threshold_has_default_message(self):
        """Given: Confidence values
        When: No custom message provided
        Then: Default message shows both values."""
        # Given
        confidence = 0.5
        threshold = 0.75

        # When/Then
        with pytest.raises(
            ConfidenceThresholdError,
            match=f"Confidence {confidence:.2f} is below threshold {threshold:.2f}",
        ):
            raise ConfidenceThresholdError(confidence, threshold)

    def test_confidence_threshold_accepts_custom_message(self):
        """Given: Confidence values and custom message
        When: Exception raised
        Then: Custom message is used."""
        # Given
        confidence = 0.4
        threshold = 0.8
        custom_message = "Prediction uncertainty too high"

        # When/Then
        with pytest.raises(ConfidenceThresholdError, match=custom_message):
            raise ConfidenceThresholdError(confidence, threshold, custom_message)


class TestEmpathyLevelError:
    """Behavioral tests for EmpathyLevelError exception."""

    def test_empathy_level_error_stores_level(self):
        """Given: Invalid empathy level
        When: EmpathyLevelError raised
        Then: Level is accessible."""
        # Given
        level = 99

        # When
        try:
            raise EmpathyLevelError(level)
        except EmpathyLevelError as e:
            # Then
            assert e.level == level

    def test_empathy_level_error_has_default_message(self):
        """Given: Invalid level
        When: No custom message provided
        Then: Default message includes level."""
        # Given
        level = -1

        # When/Then
        with pytest.raises(EmpathyLevelError, match=f"Invalid empathy level: {level}"):
            raise EmpathyLevelError(level)

    def test_empathy_level_error_accepts_custom_message(self):
        """Given: Level and custom message
        When: Exception raised
        Then: Custom message is used."""
        # Given
        level = 5
        custom_message = "Cannot regress to lower level"

        # When/Then
        with pytest.raises(EmpathyLevelError, match=custom_message):
            raise EmpathyLevelError(level, custom_message)


class TestLeveragePointError:
    """Behavioral tests for LeveragePointError exception."""

    def test_leverage_point_error_can_be_raised(self):
        """Given: LeveragePointError class
        When: Raised with message
        Then: Exception carries message."""
        # Given
        message = "No leverage points found in system"

        # When/Then
        with pytest.raises(LeveragePointError, match=message):
            raise LeveragePointError(message)

    def test_leverage_point_error_inherits_from_framework_error(self):
        """Given: LeveragePointError instance
        When: Checking inheritance
        Then: It is a framework error."""
        # Given/When
        error = LeveragePointError("test")

        # Then
        assert isinstance(error, EmpathyFrameworkError)


class TestFeedbackLoopError:
    """Behavioral tests for FeedbackLoopError exception."""

    def test_feedback_loop_error_can_be_raised(self):
        """Given: FeedbackLoopError class
        When: Raised with message
        Then: Exception carries message."""
        # Given
        message = "Vicious cycle detected but cannot break"

        # When/Then
        with pytest.raises(FeedbackLoopError, match=message):
            raise FeedbackLoopError(message)

    def test_feedback_loop_error_inherits_from_framework_error(self):
        """Given: FeedbackLoopError instance
        When: Checking inheritance
        Then: It is a framework error."""
        # Given/When
        error = FeedbackLoopError("test")

        # Then
        assert isinstance(error, EmpathyFrameworkError)


class TestCollaborationStateError:
    """Behavioral tests for CollaborationStateError exception."""

    def test_collaboration_state_error_can_be_raised(self):
        """Given: CollaborationStateError class
        When: Raised with message
        Then: Exception carries message."""
        # Given
        message = "Invalid state transition: active -> terminated"

        # When/Then
        with pytest.raises(CollaborationStateError, match=message):
            raise CollaborationStateError(message)

    def test_collaboration_state_error_inherits_from_framework_error(self):
        """Given: CollaborationStateError instance
        When: Checking inheritance
        Then: It is a framework error."""
        # Given/When
        error = CollaborationStateError("test")

        # Then
        assert isinstance(error, EmpathyFrameworkError)
