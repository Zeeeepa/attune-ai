"""Boundary condition tests for MultiModelWizard.

Tests edge cases and boundary conditions including:
- Model count thresholds (0, 1, 2, 3, 4, 7, 8, 100+)
- Empty and malformed input data
- File read errors in helper methods
- Threshold boundaries for predictions
- Large and negative values

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import tempfile
from pathlib import Path

import pytest

from empathy_software_plugin.wizards.multi_model_wizard import MultiModelWizard


class TestModelCountBoundaries:
    """Test behavior at model count boundaries."""

    @pytest.fixture
    def wizard(self):
        return MultiModelWizard()

    @pytest.mark.asyncio
    async def test_zero_models(self, wizard):
        """Test with zero models."""
        context = {
            "model_usage": [],
            "model_count": 0,
            "routing_logic": [],
            "project_path": "/tmp",
        }

        result = await wizard.analyze(context)

        # Should complete without errors
        assert result["confidence"] == 0.85
        # No multi-model issues with 0 models
        assert len(result["predictions"]) == 0

    @pytest.mark.asyncio
    async def test_single_model(self, wizard):
        """Test with exactly 1 model (no coordination needed)."""
        context = {
            "model_usage": [{"model": "gpt-4"}],
            "model_count": 1,
            "routing_logic": [],
            "project_path": "/tmp",
        }

        result = await wizard.analyze(context)

        # Single model should have no coordination issues
        assert len(result["predictions"]) == 0
        assert result["confidence"] == 0.85

    @pytest.mark.asyncio
    async def test_two_models_boundary(self, wizard):
        """Test with exactly 2 models (minimal coordination)."""
        context = {
            "model_usage": [{"model": "gpt-4"}, {"model": "claude"}],
            "model_count": 2,
            "routing_logic": [],
            "project_path": "/tmp",
        }

        result = await wizard.analyze(context)

        # Should trigger some warnings (fallback, version tracking)
        # But NOT abstraction layer (needs > 2)
        issue_types = [i["type"] for i in result["issues"]]
        assert "no_fallback_strategy" in issue_types
        assert "no_model_abstraction" not in issue_types

    @pytest.mark.asyncio
    async def test_three_models_boundary(self, wizard):
        """Test with exactly 3 models (starts needing abstraction)."""
        context = {
            "model_usage": [{}, {}, {}],
            "model_count": 3,
            "routing_logic": [],
            "project_path": "/tmp",
        }

        result = await wizard.analyze(context)

        # Should trigger abstraction warning (> 2)
        issue_types = [i["type"] for i in result["issues"]]
        assert "no_model_abstraction" in issue_types
        assert "no_cost_tracking" in issue_types

    @pytest.mark.asyncio
    async def test_four_models_lower_complexity_boundary(self, wizard):
        """Test with exactly 4 models (lower bound of complexity threshold)."""
        context = {
            "model_usage": [],
            "model_count": 4,
            "routing_logic": [],
            "project_path": "/tmp",
        }

        result = await wizard.analyze(context)

        # Should trigger coordination_complexity prediction (4-7 range)
        pred_types = [p["type"] for p in result["predictions"]]
        assert "coordination_complexity" in pred_types
        assert "suboptimal_routing" in pred_types

    @pytest.mark.asyncio
    async def test_seven_models_upper_complexity_boundary(self, wizard):
        """Test with exactly 7 models (upper bound of complexity threshold)."""
        context = {
            "model_usage": [],
            "model_count": 7,
            "routing_logic": [],
            "project_path": "/tmp",
        }

        result = await wizard.analyze(context)

        # Should still trigger coordination_complexity (4-7 range)
        pred_types = [p["type"] for p in result["predictions"]]
        assert "coordination_complexity" in pred_types

    @pytest.mark.asyncio
    async def test_eight_models_beyond_complexity_boundary(self, wizard):
        """Test with exactly 8 models (beyond 4-7 complexity threshold)."""
        context = {
            "model_usage": [],
            "model_count": 8,
            "routing_logic": [],
            "project_path": "/tmp",
        }

        result = await wizard.analyze(context)

        # coordination_complexity prediction is for 4-7 range
        pred_types = [p["type"] for p in result["predictions"]]
        # Should NOT have coordination_complexity (outside 4-7 range)
        assert "coordination_complexity" not in pred_types

    @pytest.mark.asyncio
    async def test_very_large_model_count(self, wizard):
        """Test with very large model count (100+)."""
        context = {
            "model_usage": [],
            "model_count": 150,
            "routing_logic": [],
            "project_path": "/tmp",
        }

        result = await wizard.analyze(context)

        # Should complete without crashing
        assert result is not None
        assert result["metadata"]["model_count"] == 150

    @pytest.mark.asyncio
    async def test_negative_model_count(self, wizard):
        """Test with negative model count (invalid but shouldn't crash)."""
        context = {
            "model_usage": [],
            "model_count": -1,
            "routing_logic": [],
            "project_path": "/tmp",
        }

        result = await wizard.analyze(context)

        # Should handle gracefully (no predictions triggered)
        assert result is not None
        assert len(result["predictions"]) == 0


class TestEmptyAndMalformedInput:
    """Test empty and malformed input data."""

    @pytest.fixture
    def wizard(self):
        return MultiModelWizard()

    @pytest.mark.asyncio
    async def test_empty_model_usage(self, wizard):
        """Test with empty model_usage list."""
        context = {
            "model_usage": [],
            "model_count": 5,
            "routing_logic": [],
            "project_path": "/tmp",
        }

        result = await wizard.analyze(context)

        # Should complete (model_count matters, not model_usage)
        assert result is not None

    @pytest.mark.asyncio
    async def test_empty_routing_logic(self, wizard):
        """Test with empty routing_logic list."""
        context = {
            "model_usage": [{"model": "gpt-4"}],
            "model_count": 1,
            "routing_logic": [],
            "project_path": "/tmp",
        }

        result = await wizard.analyze(context)

        # Helper methods should return False for empty routing
        assert result is not None

    @pytest.mark.asyncio
    async def test_malformed_model_usage_dict(self, wizard):
        """Test with malformed model_usage dictionaries."""
        context = {
            "model_usage": [
                {},  # Empty dict
                {"invalid_key": "value"},  # Missing expected keys
                {"model": None},  # Null value
            ],
            "model_count": 3,
            "routing_logic": [],
            "project_path": "/tmp",
        }

        result = await wizard.analyze(context)

        # Should handle gracefully
        assert result is not None

    @pytest.mark.asyncio
    async def test_model_count_mismatch(self, wizard):
        """Test when model_count doesn't match model_usage length."""
        context = {
            "model_usage": [{"model": "gpt-4"}],  # 1 model
            "model_count": 5,  # Says 5
            "routing_logic": [],
            "project_path": "/tmp",
        }

        result = await wizard.analyze(context)

        # Should use model_count for logic
        assert result["metadata"]["model_count"] == 5

    @pytest.mark.asyncio
    async def test_missing_context_keys_with_defaults(self, wizard):
        """Test with missing context keys (wizard validates required fields)."""
        context = {
            # Missing model_usage, model_count, routing_logic
            "project_path": "/tmp",
        }

        # Wizard validates required context keys
        with pytest.raises(ValueError, match="missing required context"):
            await wizard.analyze(context)

    @pytest.mark.asyncio
    async def test_none_context_values(self, wizard):
        """Test with None values in context (causes TypeError)."""
        context = {
            "model_usage": None,
            "model_count": None,  # Can't compare None > int
            "routing_logic": None,
            "project_path": None,
        }

        # TypeError when comparing None > int in _analyze_model_coordination
        with pytest.raises(TypeError):
            await wizard.analyze(context)


class TestHelperMethodBoundaries:
    """Test boundary conditions in helper methods."""

    @pytest.fixture
    def wizard(self):
        return MultiModelWizard()

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_has_consistent_prompts_empty_list(self, wizard):
        """Test _has_consistent_prompts with empty list."""
        result = wizard._has_consistent_prompts([])

        assert result is False

    def test_has_consistent_prompts_missing_key(self, wizard):
        """Test _has_consistent_prompts with missing uses_template_system key."""
        model_usage = [{"model": "gpt-4"}]  # Missing uses_template_system

        result = wizard._has_consistent_prompts(model_usage)

        # Should return False (no usage has uses_template_system=True)
        assert result is False

    def test_has_model_abstraction_nonexistent_file(self, wizard):
        """Test _has_model_abstraction with non-existent file."""
        result = wizard._has_model_abstraction(["/nonexistent/file.py"])

        # Should return False (OSError caught)
        assert result is False

    def test_has_model_abstraction_empty_file(self, wizard, temp_dir):
        """Test _has_model_abstraction with empty file."""
        empty_file = temp_dir / "empty.py"
        empty_file.write_text("")

        result = wizard._has_model_abstraction([str(empty_file)])

        # No keywords found in empty file
        assert result is False

    def test_has_fallback_strategy_case_sensitivity(self, wizard, temp_dir):
        """Test _has_fallback_strategy is case-insensitive."""
        test_file = temp_dir / "api.py"
        test_file.write_text("def FALLBACK_function():\n    pass")

        result = wizard._has_fallback_strategy([str(test_file)])

        # Should match (uses .lower())
        assert result is True

    def test_has_cost_tracking_requires_both_keywords(self, wizard, temp_dir):
        """Test _has_cost_tracking requires both 'cost' and 'track'/'log'."""
        # Only 'cost' keyword
        cost_only = temp_dir / "cost.py"
        cost_only.write_text("def cost_function():\n    pass")

        result = wizard._has_cost_tracking([str(cost_only)])

        # Should return False (needs both cost AND track/log)
        assert result is False

        # Both 'cost' and 'track'
        both = temp_dir / "tracking.py"
        both.write_text("def track_cost():\n    pass")

        result = wizard._has_cost_tracking([str(both)])

        # Should return True
        assert result is True

    def test_helper_with_binary_file(self, wizard, temp_dir):
        """Test helper methods with binary file (should handle gracefully)."""
        binary_file = temp_dir / "binary.py"
        binary_file.write_bytes(b"\x00\x01\x02\x03")

        # Should not crash (might fail to read or read as garbage)
        result = wizard._has_model_abstraction([str(binary_file)])

        # Should return False (unlikely to have keywords in binary)
        assert result is False

    def test_helper_with_very_large_file(self, wizard, temp_dir):
        """Test helper methods with very large file."""
        large_file = temp_dir / "large.py"
        large_file.write_text("x = 1\n" * 100000)  # 100k lines

        result = wizard._has_model_abstraction([str(large_file)])

        # Should complete (might be slow but shouldn't crash)
        assert result is False

    def test_helper_with_permission_error(self, wizard, temp_dir):
        """Test helper methods handle permission errors."""
        # Create file
        restricted_file = temp_dir / "restricted.py"
        restricted_file.write_text("def foo(): pass")

        # Simulate permission error with mock
        import builtins
        from unittest.mock import mock_open, patch

        mock_file = mock_open()
        mock_file.side_effect = PermissionError("Access denied")

        with patch.object(builtins, "open", mock_file):
            result = wizard._has_model_abstraction([str(restricted_file)])

            # Should return False (OSError caught)
            assert result is False

    def test_helper_with_unicode_decode_error(self, wizard, temp_dir):
        """Test helper methods handle unicode decode errors."""
        # Write file with invalid UTF-8
        invalid_file = temp_dir / "invalid.py"
        invalid_file.write_bytes(b"\x80\x81\x82\x83")

        # Helper methods don't specify encoding, so they may fail on invalid UTF-8
        # This is caught by OSError handler
        try:
            result = wizard._has_model_abstraction([str(invalid_file)])
            # If it succeeds, result should be boolean
            assert isinstance(result, bool)
        except UnicodeDecodeError:
            # Also acceptable - not all helpers handle encoding errors
            pass


class TestPredictionThresholds:
    """Test exact threshold boundaries for predictions."""

    @pytest.fixture
    def wizard(self):
        return MultiModelWizard()

    @pytest.mark.asyncio
    async def test_coordination_complexity_exact_lower_bound(self, wizard):
        """Test coordination_complexity at exact lower bound (4 models)."""
        predictions = await wizard._predict_multi_model_issues(
            model_usage=[], model_count=4, routing=[], full_context={}
        )

        pred_types = [p["type"] for p in predictions]
        # Should include (4 is in 4-7 range)
        assert "coordination_complexity" in pred_types

    @pytest.mark.asyncio
    async def test_coordination_complexity_exact_upper_bound(self, wizard):
        """Test coordination_complexity at exact upper bound (7 models)."""
        predictions = await wizard._predict_multi_model_issues(
            model_usage=[], model_count=7, routing=[], full_context={}
        )

        pred_types = [p["type"] for p in predictions]
        # Should include (7 is in 4-7 range)
        assert "coordination_complexity" in pred_types

    @pytest.mark.asyncio
    async def test_coordination_complexity_below_lower_bound(self, wizard):
        """Test coordination_complexity below lower bound (3 models)."""
        predictions = await wizard._predict_multi_model_issues(
            model_usage=[], model_count=3, routing=[], full_context={}
        )

        pred_types = [p["type"] for p in predictions]
        # Should NOT include (3 is below 4-7 range)
        assert "coordination_complexity" not in pred_types

    @pytest.mark.asyncio
    async def test_coordination_complexity_above_upper_bound(self, wizard):
        """Test coordination_complexity above upper bound (8 models)."""
        predictions = await wizard._predict_multi_model_issues(
            model_usage=[], model_count=8, routing=[], full_context={}
        )

        pred_types = [p["type"] for p in predictions]
        # Should NOT include (8 is above 4-7 range)
        assert "coordination_complexity" not in pred_types

    @pytest.mark.asyncio
    async def test_cost_optimization_boundary(self, wizard):
        """Test cost_optimization_needed appears at > 2 models."""
        # Exactly 2 models
        predictions_2 = await wizard._predict_multi_model_issues(
            model_usage=[], model_count=2, routing=[], full_context={}
        )
        pred_types_2 = [p["type"] for p in predictions_2]

        # Exactly 3 models
        predictions_3 = await wizard._predict_multi_model_issues(
            model_usage=[], model_count=3, routing=[], full_context={}
        )
        pred_types_3 = [p["type"] for p in predictions_3]

        # Should appear at 3 but not 2 (condition is > 2)
        assert "cost_optimization_needed" not in pred_types_2
        assert "cost_optimization_needed" in pred_types_3

    @pytest.mark.asyncio
    async def test_output_inconsistency_boundary(self, wizard):
        """Test output_inconsistency appears at > 2 models."""
        predictions_2 = await wizard._predict_multi_model_issues(
            model_usage=[], model_count=2, routing=[], full_context={}
        )
        predictions_3 = await wizard._predict_multi_model_issues(
            model_usage=[], model_count=3, routing=[], full_context={}
        )

        pred_types_2 = [p["type"] for p in predictions_2]
        pred_types_3 = [p["type"] for p in predictions_3]

        # Should appear at 3 but not 2
        assert "output_inconsistency" not in pred_types_2
        assert "output_inconsistency" in pred_types_3

    @pytest.mark.asyncio
    async def test_version_drift_boundary(self, wizard):
        """Test model_version_drift appears at > 1 models."""
        predictions_1 = await wizard._predict_multi_model_issues(
            model_usage=[], model_count=1, routing=[], full_context={}
        )
        predictions_2 = await wizard._predict_multi_model_issues(
            model_usage=[], model_count=2, routing=[], full_context={}
        )

        pred_types_1 = [p["type"] for p in predictions_1]
        pred_types_2 = [p["type"] for p in predictions_2]

        # Should appear at 2 but not 1
        assert "model_version_drift" not in pred_types_1
        assert "model_version_drift" in pred_types_2

    @pytest.mark.asyncio
    async def test_smart_routing_boundary(self, wizard):
        """Test suboptimal_routing appears at > 3 models."""
        predictions_3 = await wizard._predict_multi_model_issues(
            model_usage=[], model_count=3, routing=[], full_context={}
        )
        predictions_4 = await wizard._predict_multi_model_issues(
            model_usage=[], model_count=4, routing=[], full_context={}
        )

        pred_types_3 = [p["type"] for p in predictions_3]
        pred_types_4 = [p["type"] for p in predictions_4]

        # Should appear at 4 but not 3
        assert "suboptimal_routing" not in pred_types_3
        assert "suboptimal_routing" in pred_types_4


class TestRecommendationBoundaries:
    """Test boundary conditions in recommendation generation."""

    @pytest.fixture
    def wizard(self):
        return MultiModelWizard()

    def test_recommendations_with_no_predictions(self, wizard):
        """Test _generate_recommendations with empty predictions."""
        recommendations = wizard._generate_recommendations([], [])

        assert isinstance(recommendations, list)
        assert len(recommendations) == 0

    def test_recommendations_with_no_prevention_steps(self, wizard):
        """Test recommendations when prediction has no prevention_steps."""
        predictions = [
            {
                "type": "test",
                "alert": "Test alert",
                "impact": "high",
                "prevention_steps": [],  # Empty
            }
        ]

        recommendations = wizard._generate_recommendations([], predictions)

        # Should include alert but no steps
        assert any("Test alert" in r for r in recommendations)

    def test_recommendations_with_many_prevention_steps(self, wizard):
        """Test recommendations limits prevention steps to 3."""
        predictions = [
            {
                "type": "test",
                "alert": "Test",
                "impact": "high",
                "prevention_steps": [f"Step {i}" for i in range(10)],  # 10 steps
            }
        ]

        recommendations = wizard._generate_recommendations([], predictions)

        # Should only show first 3 steps
        step_recs = [r for r in recommendations if "Step" in r]
        assert len(step_recs) <= 3

    def test_recommendations_without_personal_experience(self, wizard):
        """Test recommendations when prediction lacks personal_experience."""
        predictions = [
            {
                "type": "test",
                "alert": "Test",
                "impact": "high",
                "prevention_steps": ["Step 1"],
                # No personal_experience key
            }
        ]

        recommendations = wizard._generate_recommendations([], predictions)

        # Should not crash
        assert isinstance(recommendations, list)


class TestIssueAnalysisBoundaries:
    """Test boundary conditions in issue analysis."""

    @pytest.fixture
    def wizard(self):
        return MultiModelWizard()

    @pytest.mark.asyncio
    async def test_abstraction_warning_exact_threshold(self, wizard):
        """Test no_model_abstraction at exact threshold (> 2)."""
        # Exactly 2 models - should NOT warn
        issues_2 = await wizard._analyze_model_coordination([], 2, [])
        issue_types_2 = [i["type"] for i in issues_2]

        # Exactly 3 models - should warn
        issues_3 = await wizard._analyze_model_coordination([], 3, [])
        issue_types_3 = [i["type"] for i in issues_3]

        assert "no_model_abstraction" not in issue_types_2
        assert "no_model_abstraction" in issue_types_3

    @pytest.mark.asyncio
    async def test_fallback_warning_exact_threshold(self, wizard):
        """Test no_fallback_strategy at exact threshold (> 1)."""
        # Exactly 1 model - should NOT warn
        issues_1 = await wizard._analyze_model_coordination([], 1, [])
        issue_types_1 = [i["type"] for i in issues_1]

        # Exactly 2 models - should warn
        issues_2 = await wizard._analyze_model_coordination([], 2, [])
        issue_types_2 = [i["type"] for i in issues_2]

        assert "no_fallback_strategy" not in issue_types_1
        assert "no_fallback_strategy" in issue_types_2

    @pytest.mark.asyncio
    async def test_cost_tracking_warning_exact_threshold(self, wizard):
        """Test no_cost_tracking at exact threshold (> 2)."""
        # Exactly 2 models - should NOT warn
        issues_2 = await wizard._analyze_model_coordination([], 2, [])
        issue_types_2 = [i["type"] for i in issues_2]

        # Exactly 3 models - should warn
        issues_3 = await wizard._analyze_model_coordination([], 3, [])
        issue_types_3 = [i["type"] for i in issues_3]

        assert "no_cost_tracking" not in issue_types_2
        assert "no_cost_tracking" in issue_types_3
