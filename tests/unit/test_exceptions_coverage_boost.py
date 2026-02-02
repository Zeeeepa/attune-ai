"""Tests for custom exceptions module.

Module: exceptions.py (123 lines)
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

# ============================================================================
# Base Exception Tests
# ============================================================================


@pytest.mark.unit
class TestEmpathyFrameworkError:
    """Test suite for EmpathyFrameworkError base exception."""

    def test_create_base_exception(self):
        """Test creating base exception with message."""
        # When
        exc = EmpathyFrameworkError("Test error")

        # Then
        assert str(exc) == "Test error"
        assert isinstance(exc, Exception)

    def test_base_exception_is_exception(self):
        """Test that base exception inherits from Exception."""
        assert issubclass(EmpathyFrameworkError, Exception)


# ============================================================================
# ValidationError Tests
# ============================================================================


@pytest.mark.unit
class TestValidationError:
    """Test suite for ValidationError exception."""

    def test_create_validation_error(self):
        """Test creating ValidationError with message."""
        # When
        exc = ValidationError("Invalid input")

        # Then
        assert str(exc) == "Invalid input"
        assert isinstance(exc, EmpathyFrameworkError)

    def test_validation_error_inherits_base(self):
        """Test that ValidationError inherits from EmpathyFrameworkError."""
        assert issubclass(ValidationError, EmpathyFrameworkError)


# ============================================================================
# PatternNotFoundError Tests
# ============================================================================


@pytest.mark.unit
class TestPatternNotFoundError:
    """Test suite for PatternNotFoundError exception."""

    def test_create_with_pattern_id_only(self):
        """Test creating PatternNotFoundError with pattern_id only."""
        # When
        exc = PatternNotFoundError("pattern_123")

        # Then
        assert "pattern_123" in str(exc)
        assert exc.pattern_id == "pattern_123"

    def test_create_with_custom_message(self):
        """Test creating PatternNotFoundError with custom message."""
        # When
        exc = PatternNotFoundError("pattern_456", "Custom error message")

        # Then
        assert str(exc) == "Custom error message"
        assert exc.pattern_id == "pattern_456"

    def test_pattern_not_found_inherits_base(self):
        """Test that PatternNotFoundError inherits from EmpathyFrameworkError."""
        assert issubclass(PatternNotFoundError, EmpathyFrameworkError)


# ============================================================================
# TrustThresholdError Tests
# ============================================================================


@pytest.mark.unit
class TestTrustThresholdError:
    """Test suite for TrustThresholdError exception."""

    def test_create_with_trust_values(self):
        """Test creating TrustThresholdError with trust values."""
        # When
        exc = TrustThresholdError(current_trust=0.5, required_trust=0.8)

        # Then
        assert exc.current_trust == 0.5
        assert exc.required_trust == 0.8
        assert "0.50" in str(exc)
        assert "0.80" in str(exc)

    def test_create_with_custom_message(self):
        """Test creating TrustThresholdError with custom message."""
        # When
        exc = TrustThresholdError(0.3, 0.7, "Custom trust error")

        # Then
        assert str(exc) == "Custom trust error"
        assert exc.current_trust == 0.3
        assert exc.required_trust == 0.7

    def test_trust_threshold_inherits_base(self):
        """Test that TrustThresholdError inherits from EmpathyFrameworkError."""
        assert issubclass(TrustThresholdError, EmpathyFrameworkError)


# ============================================================================
# ConfidenceThresholdError Tests
# ============================================================================


@pytest.mark.unit
class TestConfidenceThresholdError:
    """Test suite for ConfidenceThresholdError exception."""

    def test_create_with_confidence_values(self):
        """Test creating ConfidenceThresholdError with confidence values."""
        # When
        exc = ConfidenceThresholdError(confidence=0.6, threshold=0.85)

        # Then
        assert exc.confidence == 0.6
        assert exc.threshold == 0.85
        assert "0.60" in str(exc)
        assert "0.85" in str(exc)

    def test_create_with_custom_message(self):
        """Test creating ConfidenceThresholdError with custom message."""
        # When
        exc = ConfidenceThresholdError(0.4, 0.9, "Custom confidence error")

        # Then
        assert str(exc) == "Custom confidence error"
        assert exc.confidence == 0.4
        assert exc.threshold == 0.9

    def test_confidence_threshold_inherits_base(self):
        """Test that ConfidenceThresholdError inherits from EmpathyFrameworkError."""
        assert issubclass(ConfidenceThresholdError, EmpathyFrameworkError)


# ============================================================================
# EmpathyLevelError Tests
# ============================================================================


@pytest.mark.unit
class TestEmpathyLevelError:
    """Test suite for EmpathyLevelError exception."""

    def test_create_with_level(self):
        """Test creating EmpathyLevelError with level."""
        # When
        exc = EmpathyLevelError(level=5)

        # Then
        assert exc.level == 5
        assert "5" in str(exc)

    def test_create_with_custom_message(self):
        """Test creating EmpathyLevelError with custom message."""
        # When
        exc = EmpathyLevelError(3, "Custom level error")

        # Then
        assert str(exc) == "Custom level error"
        assert exc.level == 3

    def test_empathy_level_inherits_base(self):
        """Test that EmpathyLevelError inherits from EmpathyFrameworkError."""
        assert issubclass(EmpathyLevelError, EmpathyFrameworkError)


# ============================================================================
# LeveragePointError Tests
# ============================================================================


@pytest.mark.unit
class TestLeveragePointError:
    """Test suite for LeveragePointError exception."""

    def test_create_leverage_point_error(self):
        """Test creating LeveragePointError with message."""
        # When
        exc = LeveragePointError("No leverage points found")

        # Then
        assert str(exc) == "No leverage points found"
        assert isinstance(exc, EmpathyFrameworkError)

    def test_leverage_point_inherits_base(self):
        """Test that LeveragePointError inherits from EmpathyFrameworkError."""
        assert issubclass(LeveragePointError, EmpathyFrameworkError)


# ============================================================================
# FeedbackLoopError Tests
# ============================================================================


@pytest.mark.unit
class TestFeedbackLoopError:
    """Test suite for FeedbackLoopError exception."""

    def test_create_feedback_loop_error(self):
        """Test creating FeedbackLoopError with message."""
        # When
        exc = FeedbackLoopError("Vicious cycle detected")

        # Then
        assert str(exc) == "Vicious cycle detected"
        assert isinstance(exc, EmpathyFrameworkError)

    def test_feedback_loop_inherits_base(self):
        """Test that FeedbackLoopError inherits from EmpathyFrameworkError."""
        assert issubclass(FeedbackLoopError, EmpathyFrameworkError)


# ============================================================================
# CollaborationStateError Tests
# ============================================================================


@pytest.mark.unit
class TestCollaborationStateError:
    """Test suite for CollaborationStateError exception."""

    def test_create_collaboration_state_error(self):
        """Test creating CollaborationStateError with message."""
        # When
        exc = CollaborationStateError("Invalid state transition")

        # Then
        assert str(exc) == "Invalid state transition"
        assert isinstance(exc, EmpathyFrameworkError)

    def test_collaboration_state_inherits_base(self):
        """Test that CollaborationStateError inherits from EmpathyFrameworkError."""
        assert issubclass(CollaborationStateError, EmpathyFrameworkError)


# ============================================================================
# Exception Hierarchy Tests
# ============================================================================


@pytest.mark.unit
class TestExceptionHierarchy:
    """Test suite for exception inheritance hierarchy."""

    def test_all_exceptions_inherit_from_base(self):
        """Test that all custom exceptions inherit from EmpathyFrameworkError."""
        # Given
        exceptions = [
            ValidationError,
            PatternNotFoundError,
            TrustThresholdError,
            ConfidenceThresholdError,
            EmpathyLevelError,
            LeveragePointError,
            FeedbackLoopError,
            CollaborationStateError,
        ]

        # Then
        for exc_class in exceptions:
            assert issubclass(exc_class, EmpathyFrameworkError)
            assert issubclass(exc_class, Exception)

    def test_can_catch_all_with_base_exception(self):
        """Test that all custom exceptions can be caught with base exception."""

        # Given
        def raise_validation():
            raise ValidationError("test")

        def raise_pattern_not_found():
            raise PatternNotFoundError("test")

        # Then
        with pytest.raises(EmpathyFrameworkError):
            raise_validation()

        with pytest.raises(EmpathyFrameworkError):
            raise_pattern_not_found()
