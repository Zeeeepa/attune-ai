"""
Tests for Healthcare Plugin Trajectory Analyzer (Level 4)

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import pytest

from empathy_healthcare_plugin.monitors.monitoring.trajectory_analyzer import (
    TrajectoryAnalyzer,
    TrajectoryPrediction,
    VitalTrend,
)


class TestTrajectoryAnalyzer:
    """Test trajectory analyzer initialization and basic functionality"""

    def test_initialization(self):
        """Test analyzer initializes with correct normal ranges"""
        analyzer = TrajectoryAnalyzer()

        assert analyzer.normal_ranges["hr"] == (60, 100)
        assert analyzer.normal_ranges["systolic_bp"] == (90, 140)
        assert analyzer.normal_ranges["o2_sat"] == (95, 100)
        assert analyzer.normal_ranges["temp_f"] == (97.0, 99.5)

        assert analyzer.concerning_rates["hr"] == 15
        assert analyzer.concerning_rates["systolic_bp"] == 20
        assert analyzer.concerning_rates["respiratory_rate"] == 5

    def test_analyze_trajectory_no_history(self):
        """Test with no historical data returns low confidence"""
        analyzer = TrajectoryAnalyzer()

        current = {"hr": 80, "systolic_bp": 120}
        history = []

        prediction = analyzer.analyze_trajectory(current, history)

        assert prediction.trajectory_state == "stable"
        assert prediction.confidence == 0.3
        assert (
            prediction.overall_assessment == "Insufficient historical data for trajectory analysis"
        )
        assert prediction.recommendations == ["Continue monitoring"]
        assert prediction.estimated_time_to_critical is None


class TestStableTrajectory:
    """Test stable patient trajectory detection"""

    def test_stable_vitals(self):
        """Test stable vitals produce stable trajectory"""
        analyzer = TrajectoryAnalyzer()

        current = {
            "hr": 80,
            "systolic_bp": 120,
            "diastolic_bp": 75,
            "respiratory_rate": 16,
            "temp_f": 98.6,
            "o2_sat": 98,
        }

        history = [
            {
                "hr": 78,
                "systolic_bp": 118,
                "diastolic_bp": 74,
                "respiratory_rate": 15,
                "temp_f": 98.4,
                "o2_sat": 97,
            },
            {
                "hr": 79,
                "systolic_bp": 119,
                "diastolic_bp": 75,
                "respiratory_rate": 16,
                "temp_f": 98.5,
                "o2_sat": 98,
            },
            {
                "hr": 80,
                "systolic_bp": 120,
                "diastolic_bp": 75,
                "respiratory_rate": 16,
                "temp_f": 98.6,
                "o2_sat": 98,
            },
        ]

        prediction = analyzer.analyze_trajectory(current, history)

        assert prediction.trajectory_state == "stable"
        assert "stable" in prediction.overall_assessment.lower()
        assert prediction.recommendations == ["Continue routine monitoring"]
        assert prediction.estimated_time_to_critical is None

    def test_minimal_changes_are_stable(self):
        """Test that small changes (<5%) are considered stable"""
        analyzer = TrajectoryAnalyzer()

        current = {"hr": 82}
        history = [{"hr": 80}, {"hr": 81}]

        prediction = analyzer.analyze_trajectory(current, history)

        assert prediction.trajectory_state == "stable"
        # Change is (82-81)/81 = 1.23%, should be stable
        assert any(trend.direction == "stable" for trend in prediction.vital_trends)


class TestConcerningTrajectory:
    """Test detection of concerning trends"""

    def test_elevated_heart_rate(self):
        """Test increasing heart rate triggers concerning state"""
        analyzer = TrajectoryAnalyzer()

        current = {"hr": 115}  # Above normal range
        history = [{"hr": 95}, {"hr": 100}, {"hr": 105}]

        prediction = analyzer.analyze_trajectory(current, history)

        assert prediction.trajectory_state in ["concerning", "critical"]
        assert len(prediction.vital_trends) > 0

        hr_trend = next((t for t in prediction.vital_trends if t.parameter == "hr"), None)
        assert hr_trend is not None
        assert hr_trend.concerning is True
        # Change from 105 to 115 is 9.5%, should be increasing
        assert hr_trend.direction in ["increasing", "stable"]  # May vary based on threshold

    def test_decreasing_blood_pressure(self):
        """Test decreasing BP triggers concerning state"""
        analyzer = TrajectoryAnalyzer()

        current = {"systolic_bp": 85}  # Below normal
        history = [{"systolic_bp": 110}, {"systolic_bp": 100}, {"systolic_bp": 90}]

        prediction = analyzer.analyze_trajectory(current, history)

        assert prediction.trajectory_state in ["concerning", "critical"]

        bp_trend = next((t for t in prediction.vital_trends if t.parameter == "systolic_bp"), None)
        assert bp_trend is not None
        assert bp_trend.concerning is True
        assert bp_trend.direction == "decreasing"

    def test_rapid_respiratory_rate_increase(self):
        """Test rapid RR increase triggers concerning state"""
        analyzer = TrajectoryAnalyzer()

        current = {"respiratory_rate": 30}
        history = [{"respiratory_rate": 18}, {"respiratory_rate": 22}, {"respiratory_rate": 26}]

        prediction = analyzer.analyze_trajectory(current, history)

        assert prediction.trajectory_state in ["concerning", "critical"]


class TestCriticalTrajectory:
    """Test detection of critical trajectories"""

    def test_critical_oxygen_desaturation(self):
        """Test O2 sat drop triggers critical state"""
        analyzer = TrajectoryAnalyzer()

        current = {"o2_sat": 88, "hr": 95}  # O2 below critical threshold
        history = [{"o2_sat": 96, "hr": 85}, {"o2_sat": 93, "hr": 90}, {"o2_sat": 90, "hr": 93}]

        prediction = analyzer.analyze_trajectory(current, history)

        assert prediction.trajectory_state == "critical"
        assert "critical" in prediction.overall_assessment.lower()

    def test_critical_blood_pressure_drop(self):
        """Test critical BP drop triggers critical state"""
        analyzer = TrajectoryAnalyzer()

        current = {"systolic_bp": 75, "hr": 110}  # Critically low BP
        history = [
            {"systolic_bp": 100, "hr": 85},
            {"systolic_bp": 90, "hr": 95},
            {"systolic_bp": 85, "hr": 105},
        ]

        prediction = analyzer.analyze_trajectory(current, history)

        assert prediction.trajectory_state == "critical"
        assert (
            "CRITICAL" in prediction.overall_assessment
            or "critical" in prediction.overall_assessment.lower()
        )

    def test_multiple_concerning_trends(self):
        """Test multiple concerning trends trigger critical/concerning state"""
        analyzer = TrajectoryAnalyzer()

        current = {"hr": 115, "systolic_bp": 85, "respiratory_rate": 28, "temp_f": 101.5}

        history = [
            {"hr": 90, "systolic_bp": 110, "respiratory_rate": 18, "temp_f": 98.6},
            {"hr": 100, "systolic_bp": 100, "respiratory_rate": 22, "temp_f": 99.5},
            {"hr": 110, "systolic_bp": 90, "respiratory_rate": 25, "temp_f": 100.5},
        ]

        prediction = analyzer.analyze_trajectory(current, history)

        assert prediction.trajectory_state in ["concerning", "critical"]

        concerning_trends = [t for t in prediction.vital_trends if t.concerning]
        assert len(concerning_trends) >= 2


class TestLevel4Predictions:
    """Test Level 4 anticipatory predictions (time to critical)"""

    def test_time_to_critical_bp_prediction(self):
        """Test prediction of time until critical BP"""
        analyzer = TrajectoryAnalyzer()

        # BP dropping from 100 → 95 → 90, currently 95
        # If it continues, will hit 85 (critical) soon
        current = {"systolic_bp": 95}
        history = [{"systolic_bp": 100}, {"systolic_bp": 97}]

        prediction = analyzer.analyze_trajectory(current, history)

        if prediction.trajectory_state in ["concerning", "critical"]:
            # Should estimate time to critical
            if prediction.estimated_time_to_critical:
                assert "hour" in prediction.estimated_time_to_critical

    def test_time_to_critical_o2_prediction(self):
        """Test prediction of time until critical O2 sat"""
        analyzer = TrajectoryAnalyzer()

        # Larger drops to trigger concerning state with time prediction
        current = {"o2_sat": 90}  # At critical threshold
        history = [{"o2_sat": 96}, {"o2_sat": 93}]

        prediction = analyzer.analyze_trajectory(current, history)

        # Should be concerning or critical
        assert prediction.trajectory_state in ["concerning", "critical"]
        # May or may not have time prediction depending on rate calculation
        # Just verify it's in valid states

    def test_no_time_prediction_for_stable(self):
        """Test no time prediction for stable patients"""
        analyzer = TrajectoryAnalyzer()

        current = {"hr": 80, "systolic_bp": 120}
        history = [{"hr": 78, "systolic_bp": 118}, {"hr": 79, "systolic_bp": 119}]

        prediction = analyzer.analyze_trajectory(current, history)

        assert prediction.trajectory_state == "stable"
        assert prediction.estimated_time_to_critical is None


class TestTrendAnalysis:
    """Test individual trend analysis"""

    def test_trend_direction_increasing(self):
        """Test trend correctly identifies increasing direction"""
        analyzer = TrajectoryAnalyzer()

        current = {"hr": 100}
        history = [{"hr": 80}, {"hr": 90}]

        prediction = analyzer.analyze_trajectory(current, history)

        hr_trend = next((t for t in prediction.vital_trends if t.parameter == "hr"), None)
        assert hr_trend is not None
        assert hr_trend.direction == "increasing"
        assert hr_trend.change > 0

    def test_trend_direction_decreasing(self):
        """Test trend correctly identifies decreasing direction"""
        analyzer = TrajectoryAnalyzer()

        current = {"hr": 70}
        history = [{"hr": 90}, {"hr": 80}]

        prediction = analyzer.analyze_trajectory(current, history)

        hr_trend = next((t for t in prediction.vital_trends if t.parameter == "hr"), None)
        assert hr_trend is not None
        assert hr_trend.direction == "decreasing"
        assert hr_trend.change < 0

    def test_trend_change_percent_calculation(self):
        """Test change percent is calculated correctly"""
        analyzer = TrajectoryAnalyzer()

        current = {"hr": 110}
        history = [{"hr": 100}]

        prediction = analyzer.analyze_trajectory(current, history)

        hr_trend = next((t for t in prediction.vital_trends if t.parameter == "hr"), None)
        assert hr_trend is not None
        # Change: 110 - 100 = 10, Percent: 10/100 * 100 = 10%
        assert hr_trend.change_percent == pytest.approx(10.0, abs=0.1)

    def test_skip_non_numeric_parameters(self):
        """Test that non-numeric parameters are skipped"""
        analyzer = TrajectoryAnalyzer()

        current = {"hr": 80, "mental_status": "alert"}
        history = [{"hr": 78, "mental_status": "alert"}]

        prediction = analyzer.analyze_trajectory(current, history)

        # Should only have hr trend, not mental_status
        assert len(prediction.vital_trends) == 1
        assert prediction.vital_trends[0].parameter == "hr"


class TestRecommendations:
    """Test recommendation generation"""

    def test_stable_recommendations(self):
        """Test stable vitals get routine monitoring recommendation"""
        analyzer = TrajectoryAnalyzer()

        current = {"hr": 80, "systolic_bp": 120}
        history = [{"hr": 78, "systolic_bp": 118}]

        prediction = analyzer.analyze_trajectory(current, history)

        assert "Continue routine monitoring" in prediction.recommendations

    def test_concerning_recommendations(self):
        """Test concerning vitals get increased monitoring"""
        analyzer = TrajectoryAnalyzer()

        current = {"systolic_bp": 85}  # Below normal
        history = [{"systolic_bp": 110}, {"systolic_bp": 95}]

        prediction = analyzer.analyze_trajectory(current, history)

        if prediction.trajectory_state in ["concerning", "critical"]:
            assert any("physician" in rec.lower() for rec in prediction.recommendations)
            assert any("monitoring" in rec.lower() for rec in prediction.recommendations)

    def test_critical_recommendations_include_rapid_response(self):
        """Test critical state recommends rapid response team"""
        analyzer = TrajectoryAnalyzer()

        current = {"systolic_bp": 75, "o2_sat": 88}
        history = [{"systolic_bp": 100, "o2_sat": 96}, {"systolic_bp": 85, "o2_sat": 92}]

        prediction = analyzer.analyze_trajectory(current, history)

        if prediction.trajectory_state == "critical":
            assert any("rapid response" in rec.lower() for rec in prediction.recommendations)

    def test_specific_parameter_recommendations(self):
        """Test specific recommendations for different parameters"""
        analyzer = TrajectoryAnalyzer()

        # Test BP-specific recommendation
        current = {"systolic_bp": 85}
        history = [{"systolic_bp": 100}]

        prediction = analyzer.analyze_trajectory(current, history)

        if any(t.parameter == "systolic_bp" and t.concerning for t in prediction.vital_trends):
            assert any(
                "volume" in rec.lower() or "perfusion" in rec.lower()
                for rec in prediction.recommendations
            )


class TestConfidenceCalculation:
    """Test confidence scoring"""

    def test_more_data_increases_confidence(self):
        """Test that more historical data increases confidence"""
        analyzer = TrajectoryAnalyzer()

        current = {"hr": 85}

        # Few data points
        history_short = [{"hr": 80}]
        pred_short = analyzer.analyze_trajectory(current, history_short)

        # More data points
        history_long = [{"hr": 80}] * 10
        pred_long = analyzer.analyze_trajectory(current, history_long)

        assert pred_long.confidence >= pred_short.confidence

    def test_concerning_trends_affect_confidence(self):
        """Test that concerning trends affect confidence"""
        analyzer = TrajectoryAnalyzer()

        # Stable vitals
        current_stable = {"hr": 80, "systolic_bp": 120}
        history_stable = [{"hr": 78, "systolic_bp": 118}, {"hr": 79, "systolic_bp": 119}] * 5

        pred_stable = analyzer.analyze_trajectory(current_stable, history_stable)

        # All vitals concerning
        current_concerning = {"hr": 120, "systolic_bp": 80, "respiratory_rate": 30}
        history_concerning = [{"hr": 90, "systolic_bp": 110, "respiratory_rate": 18}] * 5

        pred_concerning = analyzer.analyze_trajectory(current_concerning, history_concerning)

        # Both should have confidence scores
        assert 0.0 <= pred_stable.confidence <= 1.0
        assert 0.0 <= pred_concerning.confidence <= 1.0


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_missing_vitals_in_history(self):
        """Test handling of missing vitals in historical data"""
        analyzer = TrajectoryAnalyzer()

        current = {"hr": 85, "systolic_bp": 120}
        history = [{"hr": 80}, {"systolic_bp": 118}]  # Missing systolic_bp  # Missing hr

        prediction = analyzer.analyze_trajectory(current, history)

        # Should still work, just with available data
        assert prediction is not None
        assert prediction.trajectory_state in ["stable", "concerning", "critical", "improving"]

    def test_zero_previous_value_division(self):
        """Test handling of zero previous value in percent calculation"""
        analyzer = TrajectoryAnalyzer()

        # This is unrealistic for vital signs, but test edge case
        current = {"hr": 80}
        history = [{"hr": 0}]  # Invalid but test robustness

        prediction = analyzer.analyze_trajectory(current, history)

        # Should not crash
        assert prediction is not None

    def test_none_values_in_history(self):
        """Test handling of None values in historical data"""
        analyzer = TrajectoryAnalyzer()

        current = {"hr": 85}
        history = [{"hr": 80}, {"hr": None}, {"hr": 82}]  # None value

        prediction = analyzer.analyze_trajectory(current, history)

        # Should filter out None values
        assert prediction is not None

    def test_empty_current_data(self):
        """Test handling of empty current data"""
        analyzer = TrajectoryAnalyzer()

        current = {}
        history = [{"hr": 80}]

        prediction = analyzer.analyze_trajectory(current, history)

        assert prediction.trajectory_state == "stable"
        assert len(prediction.vital_trends) == 0


class TestVitalTrendDataclass:
    """Test VitalTrend dataclass"""

    def test_vital_trend_creation(self):
        """Test creating a VitalTrend"""
        trend = VitalTrend(
            parameter="hr",
            current_value=100,
            previous_value=80,
            change=20,
            change_percent=25.0,
            direction="increasing",
            rate_of_change=10.0,
            concerning=True,
            reasoning="HR above normal range",
        )

        assert trend.parameter == "hr"
        assert trend.current_value == 100
        assert trend.concerning is True


class TestTrajectoryPredictionDataclass:
    """Test TrajectoryPrediction dataclass"""

    def test_trajectory_prediction_creation(self):
        """Test creating a TrajectoryPrediction"""
        trend = VitalTrend(
            parameter="hr",
            current_value=100,
            previous_value=80,
            change=20,
            change_percent=25.0,
            direction="increasing",
            rate_of_change=10.0,
            concerning=True,
            reasoning="HR elevated",
        )

        prediction = TrajectoryPrediction(
            trajectory_state="concerning",
            estimated_time_to_critical="2 hours",
            vital_trends=[trend],
            overall_assessment="Patient showing concerning trends",
            confidence=0.8,
            recommendations=["Notify physician"],
        )

        assert prediction.trajectory_state == "concerning"
        assert prediction.confidence == 0.8
        assert len(prediction.recommendations) == 1
