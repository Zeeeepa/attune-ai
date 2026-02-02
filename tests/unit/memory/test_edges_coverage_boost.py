"""Unit tests for memory graph Edge and EdgeType.

This test suite provides comprehensive coverage for the memory graph edge
implementation, including EdgeType enum, Edge dataclass, serialization,
and edge pattern mappings.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from datetime import datetime

import pytest

from attune.memory.edges import (
    REVERSE_EDGE_TYPES,
    WORKFLOW_EDGE_PATTERNS,
    Edge,
    EdgeType,
)


@pytest.mark.unit
class TestEdgeTypeEnum:
    """Test suite for EdgeType enum."""

    def test_edge_type_enum_has_causal_relationships(self):
        """Test that EdgeType enum includes causal relationship types."""
        assert EdgeType.CAUSES.value == "causes"
        assert EdgeType.CAUSED_BY.value == "caused_by"
        assert EdgeType.LEADS_TO.value == "leads_to"

    def test_edge_type_enum_has_resolution_relationships(self):
        """Test that EdgeType enum includes resolution relationship types."""
        assert EdgeType.FIXED_BY.value == "fixed_by"
        assert EdgeType.FIXES.value == "fixes"
        assert EdgeType.MITIGATES.value == "mitigates"

    def test_edge_type_enum_has_similarity_relationships(self):
        """Test that EdgeType enum includes similarity relationship types."""
        assert EdgeType.SIMILAR_TO.value == "similar_to"
        assert EdgeType.RELATED_TO.value == "related_to"
        assert EdgeType.DUPLICATE_OF.value == "duplicate_of"

    def test_edge_type_enum_has_structural_relationships(self):
        """Test that EdgeType enum includes structural relationship types."""
        assert EdgeType.CONTAINS.value == "contains"
        assert EdgeType.CONTAINED_IN.value == "contained_in"
        assert EdgeType.DEPENDS_ON.value == "depends_on"
        assert EdgeType.IMPORTED_BY.value == "imported_by"
        assert EdgeType.AFFECTS.value == "affects"
        assert EdgeType.AFFECTED_BY.value == "affected_by"

    def test_edge_type_enum_has_testing_relationships(self):
        """Test that EdgeType enum includes testing relationship types."""
        assert EdgeType.TESTED_BY.value == "tested_by"
        assert EdgeType.TESTS.value == "tests"
        assert EdgeType.COVERS.value == "covers"

    def test_edge_type_enum_has_documentation_relationships(self):
        """Test that EdgeType enum includes documentation relationship types."""
        assert EdgeType.DOCUMENTS.value == "documents"
        assert EdgeType.DOCUMENTED_BY.value == "documented_by"

    def test_edge_type_enum_has_sequence_relationships(self):
        """Test that EdgeType enum includes sequence relationship types."""
        assert EdgeType.PRECEDED_BY.value == "preceded_by"
        assert EdgeType.FOLLOWED_BY.value == "followed_by"

    def test_edge_type_enum_has_derivation_relationships(self):
        """Test that EdgeType enum includes derivation relationship types."""
        assert EdgeType.DERIVED_FROM.value == "derived_from"
        assert EdgeType.REFACTORED_TO.value == "refactored_to"

    def test_edge_type_can_be_created_from_string_value(self):
        """Test that EdgeType can be created from string value."""
        edge_type = EdgeType("causes")
        assert edge_type == EdgeType.CAUSES


@pytest.mark.unit
class TestEdgeDataclass:
    """Test suite for Edge dataclass."""

    def test_edge_creation_with_required_fields(self):
        """Test creating edge with only required fields."""
        edge = Edge(
            source_id="node-1",
            target_id="node-2",
            type=EdgeType.CAUSES,
        )

        assert edge.source_id == "node-1"
        assert edge.target_id == "node-2"
        assert edge.type == EdgeType.CAUSES

    def test_edge_creation_with_default_values(self):
        """Test that edge uses correct default values."""
        edge = Edge(
            source_id="node-1",
            target_id="node-2",
            type=EdgeType.CAUSES,
        )

        assert edge.weight == 1.0
        assert edge.confidence == 1.0
        assert edge.description == ""
        assert edge.source_workflow == ""
        assert edge.metadata == {}
        assert isinstance(edge.created_at, datetime)

    def test_edge_creation_with_custom_values(self):
        """Test creating edge with custom values."""
        custom_time = datetime(2025, 1, 15, 12, 0, 0)
        edge = Edge(
            source_id="node-1",
            target_id="node-2",
            type=EdgeType.CAUSES,
            weight=0.75,
            confidence=0.85,
            description="Bug A causes Bug B",
            source_workflow="bug-predict",
            metadata={"severity": "high"},
            created_at=custom_time,
        )

        assert edge.weight == 0.75
        assert edge.confidence == 0.85
        assert edge.description == "Bug A causes Bug B"
        assert edge.source_workflow == "bug-predict"
        assert edge.metadata == {"severity": "high"}
        assert edge.created_at == custom_time

    def test_edge_id_property_generates_unique_id(self):
        """Test that edge.id generates unique identifier."""
        edge = Edge(
            source_id="node-1",
            target_id="node-2",
            type=EdgeType.CAUSES,
        )

        assert edge.id == "node-1-causes-node-2"

    def test_edge_id_is_unique_for_different_types(self):
        """Test that edge ID is unique for different edge types."""
        edge1 = Edge(source_id="A", target_id="B", type=EdgeType.CAUSES)
        edge2 = Edge(source_id="A", target_id="B", type=EdgeType.FIXED_BY)

        assert edge1.id != edge2.id
        assert edge1.id == "A-causes-B"
        assert edge2.id == "A-fixed_by-B"

    def test_edge_weight_range(self):
        """Test that edge weight can be set to different values."""
        edge_low = Edge(source_id="A", target_id="B", type=EdgeType.CAUSES, weight=0.1)
        edge_high = Edge(source_id="A", target_id="B", type=EdgeType.CAUSES, weight=1.0)

        assert edge_low.weight == 0.1
        assert edge_high.weight == 1.0

    def test_edge_confidence_range(self):
        """Test that edge confidence can be set to different values."""
        edge_low = Edge(source_id="A", target_id="B", type=EdgeType.CAUSES, confidence=0.5)
        edge_high = Edge(source_id="A", target_id="B", type=EdgeType.CAUSES, confidence=1.0)

        assert edge_low.confidence == 0.5
        assert edge_high.confidence == 1.0


@pytest.mark.unit
class TestEdgeSerialization:
    """Test suite for Edge serialization and deserialization."""

    def test_to_dict_includes_all_fields(self):
        """Test that to_dict includes all edge fields."""
        custom_time = datetime(2025, 1, 15, 12, 0, 0)
        edge = Edge(
            source_id="node-1",
            target_id="node-2",
            type=EdgeType.CAUSES,
            weight=0.75,
            confidence=0.85,
            description="Test description",
            source_workflow="test-workflow",
            metadata={"key": "value"},
            created_at=custom_time,
        )

        edge_dict = edge.to_dict()

        assert edge_dict["source_id"] == "node-1"
        assert edge_dict["target_id"] == "node-2"
        assert edge_dict["type"] == "causes"
        assert edge_dict["weight"] == 0.75
        assert edge_dict["confidence"] == 0.85
        assert edge_dict["description"] == "Test description"
        assert edge_dict["source_workflow"] == "test-workflow"
        assert edge_dict["metadata"] == {"key": "value"}
        assert edge_dict["created_at"] == "2025-01-15T12:00:00"

    def test_to_dict_converts_enum_to_string(self):
        """Test that to_dict converts EdgeType enum to string value."""
        edge = Edge(source_id="A", target_id="B", type=EdgeType.FIXES)
        edge_dict = edge.to_dict()

        assert edge_dict["type"] == "fixes"
        assert isinstance(edge_dict["type"], str)

    def test_to_dict_converts_datetime_to_isoformat(self):
        """Test that to_dict converts datetime to ISO format string."""
        custom_time = datetime(2025, 1, 15, 12, 30, 45)
        edge = Edge(source_id="A", target_id="B", type=EdgeType.CAUSES, created_at=custom_time)
        edge_dict = edge.to_dict()

        assert edge_dict["created_at"] == "2025-01-15T12:30:45"
        assert isinstance(edge_dict["created_at"], str)

    def test_from_dict_creates_edge_with_all_fields(self):
        """Test that from_dict creates edge from dictionary."""
        edge_dict = {
            "source_id": "node-1",
            "target_id": "node-2",
            "type": "causes",
            "weight": 0.75,
            "confidence": 0.85,
            "description": "Test description",
            "source_workflow": "test-workflow",
            "metadata": {"key": "value"},
            "created_at": "2025-01-15T12:00:00",
        }

        edge = Edge.from_dict(edge_dict)

        assert edge.source_id == "node-1"
        assert edge.target_id == "node-2"
        assert edge.type == EdgeType.CAUSES
        assert edge.weight == 0.75
        assert edge.confidence == 0.85
        assert edge.description == "Test description"
        assert edge.source_workflow == "test-workflow"
        assert edge.metadata == {"key": "value"}
        assert edge.created_at == datetime(2025, 1, 15, 12, 0, 0)

    def test_from_dict_uses_defaults_for_missing_optional_fields(self):
        """Test that from_dict uses defaults for missing optional fields."""
        edge_dict = {
            "source_id": "node-1",
            "target_id": "node-2",
            "type": "causes",
        }

        edge = Edge.from_dict(edge_dict)

        assert edge.weight == 1.0
        assert edge.confidence == 1.0
        assert edge.description == ""
        assert edge.source_workflow == ""
        assert edge.metadata == {}
        assert isinstance(edge.created_at, datetime)

    def test_from_dict_handles_legacy_source_wizard_field(self):
        """Test that from_dict handles legacy 'source_wizard' field."""
        edge_dict = {
            "source_id": "node-1",
            "target_id": "node-2",
            "type": "causes",
            "source_wizard": "legacy-wizard",  # Old field name
        }

        edge = Edge.from_dict(edge_dict)

        # Should use source_wizard as fallback for source_workflow
        assert edge.source_workflow == "legacy-wizard"

    def test_from_dict_prefers_source_workflow_over_source_wizard(self):
        """Test that from_dict prefers source_workflow when both present."""
        edge_dict = {
            "source_id": "node-1",
            "target_id": "node-2",
            "type": "causes",
            "source_workflow": "new-workflow",
            "source_wizard": "old-wizard",
        }

        edge = Edge.from_dict(edge_dict)

        assert edge.source_workflow == "new-workflow"

    def test_roundtrip_serialization(self):
        """Test that edge survives to_dict -> from_dict round trip."""
        original = Edge(
            source_id="node-1",
            target_id="node-2",
            type=EdgeType.FIXED_BY,
            weight=0.9,
            confidence=0.95,
            description="Original edge",
            source_workflow="test-workflow",
            metadata={"priority": "high", "count": 42},
            created_at=datetime(2025, 1, 15, 10, 30, 0),
        )

        # Round trip
        edge_dict = original.to_dict()
        restored = Edge.from_dict(edge_dict)

        assert restored.source_id == original.source_id
        assert restored.target_id == original.target_id
        assert restored.type == original.type
        assert restored.weight == original.weight
        assert restored.confidence == original.confidence
        assert restored.description == original.description
        assert restored.source_workflow == original.source_workflow
        assert restored.metadata == original.metadata
        assert restored.created_at == original.created_at

    def test_roundtrip_preserves_complex_metadata(self):
        """Test that round-trip preserves complex metadata structures."""
        original = Edge(
            source_id="A",
            target_id="B",
            type=EdgeType.CONTAINS,
            metadata={
                "nested": {"key": "value"},
                "list": [1, 2, 3],
                "mixed": {"numbers": [1, 2], "strings": ["a", "b"]},
            },
        )

        edge_dict = original.to_dict()
        restored = Edge.from_dict(edge_dict)

        assert restored.metadata == original.metadata


@pytest.mark.unit
class TestWorkflowEdgePatterns:
    """Test suite for workflow edge patterns."""

    def test_workflow_edge_patterns_includes_security_audit(self):
        """Test that workflow patterns include security-audit patterns."""
        patterns = WORKFLOW_EDGE_PATTERNS["security-audit"]

        assert (EdgeType.CAUSES, "vulnerability → vulnerability") in patterns
        assert (EdgeType.FIXED_BY, "vulnerability → fix") in patterns
        assert (EdgeType.AFFECTS, "vulnerability → file") in patterns

    def test_workflow_edge_patterns_includes_bug_predict(self):
        """Test that workflow patterns include bug-predict patterns."""
        patterns = WORKFLOW_EDGE_PATTERNS["bug-predict"]

        assert (EdgeType.CAUSES, "bug → bug") in patterns
        assert (EdgeType.SIMILAR_TO, "bug → bug") in patterns
        assert (EdgeType.FIXED_BY, "bug → fix") in patterns

    def test_workflow_edge_patterns_includes_perf_audit(self):
        """Test that workflow patterns include perf-audit patterns."""
        patterns = WORKFLOW_EDGE_PATTERNS["perf-audit"]

        assert (EdgeType.CAUSES, "performance_issue → performance_issue") in patterns
        assert (EdgeType.LEADS_TO, "code_smell → performance_issue") in patterns
        assert (EdgeType.MITIGATES, "refactor → performance_issue") in patterns

    def test_workflow_edge_patterns_includes_code_review(self):
        """Test that workflow patterns include code-review patterns."""
        patterns = WORKFLOW_EDGE_PATTERNS["code-review"]

        assert (EdgeType.CONTAINS, "file → function") in patterns
        assert (EdgeType.RELATED_TO, "code_smell → pattern") in patterns
        assert (EdgeType.REFACTORED_TO, "function → function") in patterns

    def test_workflow_edge_patterns_includes_test_gen(self):
        """Test that workflow patterns include test-gen patterns."""
        patterns = WORKFLOW_EDGE_PATTERNS["test-gen"]

        assert (EdgeType.TESTS, "test → function") in patterns
        assert (EdgeType.COVERS, "test → file") in patterns
        assert (EdgeType.TESTS, "test_case → bug") in patterns

    def test_workflow_edge_patterns_includes_dependency_check(self):
        """Test that workflow patterns include dependency-check patterns."""
        patterns = WORKFLOW_EDGE_PATTERNS["dependency-check"]

        assert (EdgeType.DEPENDS_ON, "file → dependency") in patterns
        assert (EdgeType.CAUSES, "dependency → vulnerability") in patterns

    def test_all_workflow_patterns_use_valid_edge_types(self):
        """Test that all workflow patterns use valid EdgeType values."""
        for _workflow, patterns in WORKFLOW_EDGE_PATTERNS.items():
            for edge_type, description in patterns:
                # Should be valid EdgeType enum
                assert isinstance(edge_type, EdgeType)
                # Description should be non-empty string
                assert isinstance(description, str)
                assert len(description) > 0


@pytest.mark.unit
class TestReverseEdgeTypes:
    """Test suite for reverse edge type mappings."""

    def test_reverse_edge_types_for_causal_relationships(self):
        """Test reverse mappings for causal relationships."""
        assert REVERSE_EDGE_TYPES[EdgeType.CAUSES] == EdgeType.CAUSED_BY
        assert REVERSE_EDGE_TYPES[EdgeType.CAUSED_BY] == EdgeType.CAUSES

    def test_reverse_edge_types_for_resolution_relationships(self):
        """Test reverse mappings for resolution relationships."""
        assert REVERSE_EDGE_TYPES[EdgeType.FIXED_BY] == EdgeType.FIXES
        assert REVERSE_EDGE_TYPES[EdgeType.FIXES] == EdgeType.FIXED_BY

    def test_reverse_edge_types_for_structural_relationships(self):
        """Test reverse mappings for structural relationships."""
        assert REVERSE_EDGE_TYPES[EdgeType.CONTAINS] == EdgeType.CONTAINED_IN
        assert REVERSE_EDGE_TYPES[EdgeType.CONTAINED_IN] == EdgeType.CONTAINS
        assert REVERSE_EDGE_TYPES[EdgeType.DEPENDS_ON] == EdgeType.IMPORTED_BY
        assert REVERSE_EDGE_TYPES[EdgeType.IMPORTED_BY] == EdgeType.DEPENDS_ON
        assert REVERSE_EDGE_TYPES[EdgeType.AFFECTS] == EdgeType.AFFECTED_BY
        assert REVERSE_EDGE_TYPES[EdgeType.AFFECTED_BY] == EdgeType.AFFECTS

    def test_reverse_edge_types_for_testing_relationships(self):
        """Test reverse mappings for testing relationships."""
        assert REVERSE_EDGE_TYPES[EdgeType.TESTED_BY] == EdgeType.TESTS
        assert REVERSE_EDGE_TYPES[EdgeType.TESTS] == EdgeType.TESTED_BY

    def test_reverse_edge_types_for_documentation_relationships(self):
        """Test reverse mappings for documentation relationships."""
        assert REVERSE_EDGE_TYPES[EdgeType.DOCUMENTS] == EdgeType.DOCUMENTED_BY
        assert REVERSE_EDGE_TYPES[EdgeType.DOCUMENTED_BY] == EdgeType.DOCUMENTS

    def test_reverse_edge_types_for_sequence_relationships(self):
        """Test reverse mappings for sequence relationships."""
        assert REVERSE_EDGE_TYPES[EdgeType.PRECEDED_BY] == EdgeType.FOLLOWED_BY
        assert REVERSE_EDGE_TYPES[EdgeType.FOLLOWED_BY] == EdgeType.PRECEDED_BY

    def test_reverse_edge_types_for_symmetric_relationships(self):
        """Test that symmetric relationships map to themselves."""
        assert REVERSE_EDGE_TYPES[EdgeType.SIMILAR_TO] == EdgeType.SIMILAR_TO
        assert REVERSE_EDGE_TYPES[EdgeType.RELATED_TO] == EdgeType.RELATED_TO
        assert REVERSE_EDGE_TYPES[EdgeType.DUPLICATE_OF] == EdgeType.DUPLICATE_OF

    def test_reverse_mapping_is_bidirectional(self):
        """Test that reverse mapping is bidirectional for asymmetric edges."""
        # For asymmetric relationships, reverse of reverse should be original
        asymmetric_types = [
            EdgeType.CAUSES,
            EdgeType.FIXED_BY,
            EdgeType.CONTAINS,
            EdgeType.DEPENDS_ON,
            EdgeType.TESTED_BY,
            EdgeType.DOCUMENTS,
            EdgeType.PRECEDED_BY,
            EdgeType.AFFECTS,
        ]

        for edge_type in asymmetric_types:
            reverse_type = REVERSE_EDGE_TYPES[edge_type]
            double_reverse = REVERSE_EDGE_TYPES[reverse_type]
            assert double_reverse == edge_type

    def test_reverse_mapping_is_reflexive_for_symmetric_edges(self):
        """Test that symmetric edges map to themselves."""
        symmetric_types = [
            EdgeType.SIMILAR_TO,
            EdgeType.RELATED_TO,
            EdgeType.DUPLICATE_OF,
        ]

        for edge_type in symmetric_types:
            assert REVERSE_EDGE_TYPES[edge_type] == edge_type


@pytest.mark.unit
class TestEdgeEdgeCases:
    """Test suite for Edge edge cases."""

    def test_edge_with_same_source_and_target(self):
        """Test creating edge where source equals target (self-loop)."""
        edge = Edge(
            source_id="node-1",
            target_id="node-1",
            type=EdgeType.SIMILAR_TO,
        )

        assert edge.source_id == edge.target_id
        assert edge.id == "node-1-similar_to-node-1"

    def test_edge_with_empty_metadata(self):
        """Test that edge handles empty metadata dictionary."""
        edge = Edge(source_id="A", target_id="B", type=EdgeType.CAUSES, metadata={})

        assert edge.metadata == {}
        edge_dict = edge.to_dict()
        assert edge_dict["metadata"] == {}

    def test_edge_with_none_values_in_metadata(self):
        """Test that edge handles None values in metadata."""
        edge = Edge(
            source_id="A",
            target_id="B",
            type=EdgeType.CAUSES,
            metadata={"optional_field": None},
        )

        edge_dict = edge.to_dict()
        restored = Edge.from_dict(edge_dict)
        assert restored.metadata["optional_field"] is None

    def test_edge_with_zero_weight(self):
        """Test that edge accepts zero weight."""
        edge = Edge(source_id="A", target_id="B", type=EdgeType.CAUSES, weight=0.0)

        assert edge.weight == 0.0

    def test_edge_with_zero_confidence(self):
        """Test that edge accepts zero confidence."""
        edge = Edge(source_id="A", target_id="B", type=EdgeType.CAUSES, confidence=0.0)

        assert edge.confidence == 0.0

    def test_edge_with_very_long_description(self):
        """Test that edge handles very long description strings."""
        long_desc = "x" * 10000
        edge = Edge(source_id="A", target_id="B", type=EdgeType.CAUSES, description=long_desc)

        assert edge.description == long_desc
        assert len(edge.description) == 10000

    def test_edge_with_special_characters_in_ids(self):
        """Test that edge handles special characters in node IDs."""
        edge = Edge(
            source_id="node:with:colons",
            target_id="node-with-dashes",
            type=EdgeType.CAUSES,
        )

        assert edge.id == "node:with:colons-causes-node-with-dashes"
