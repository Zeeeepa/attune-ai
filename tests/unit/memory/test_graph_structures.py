"""Tests for memory graph nodes and edges.

Covers Node, Edge, specialized node types, edge types,
and serialization/deserialization.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from datetime import datetime

import pytest

from empathy_os.memory.edges import REVERSE_EDGE_TYPES, WORKFLOW_EDGE_PATTERNS, Edge, EdgeType
from empathy_os.memory.nodes import (
    BugNode,
    Node,
    NodeType,
    PatternNode,
    PerformanceNode,
    VulnerabilityNode,
)


@pytest.mark.unit
class TestNodeType:
    """Tests for NodeType enum."""

    def test_code_entity_types(self):
        """Test code entity node types exist."""
        assert NodeType.FILE.value == "file"
        assert NodeType.FUNCTION.value == "function"
        assert NodeType.CLASS.value == "class"
        assert NodeType.MODULE.value == "module"

    def test_issue_types(self):
        """Test issue node types exist."""
        assert NodeType.BUG.value == "bug"
        assert NodeType.VULNERABILITY.value == "vulnerability"
        assert NodeType.PERFORMANCE_ISSUE.value == "performance_issue"
        assert NodeType.CODE_SMELL.value == "code_smell"
        assert NodeType.TECH_DEBT.value == "tech_debt"

    def test_solution_types(self):
        """Test solution node types exist."""
        assert NodeType.PATTERN.value == "pattern"
        assert NodeType.FIX.value == "fix"
        assert NodeType.REFACTOR.value == "refactor"

    def test_testing_types(self):
        """Test testing node types exist."""
        assert NodeType.TEST.value == "test"
        assert NodeType.TEST_CASE.value == "test_case"
        assert NodeType.COVERAGE_GAP.value == "coverage_gap"


@pytest.mark.unit
class TestNode:
    """Tests for Node dataclass."""

    def test_node_creation_basic(self):
        """Test creating a basic node."""
        node = Node(
            id="node_001",
            type=NodeType.BUG,
            name="Null pointer exception",
        )

        assert node.id == "node_001"
        assert node.type == NodeType.BUG
        assert node.name == "Null pointer exception"
        assert node.description == ""
        assert node.status == "open"

    def test_node_creation_full(self):
        """Test creating a node with all fields."""
        node = Node(
            id="node_002",
            type=NodeType.VULNERABILITY,
            name="SQL Injection",
            description="User input not sanitized",
            source_workflow="security-audit",
            source_file="src/db.py",
            source_line=42,
            severity="critical",
            confidence=0.95,
            metadata={"cwe": "89"},
            tags=["sql", "injection", "input-validation"],
            status="investigating",
        )

        assert node.source_workflow == "security-audit"
        assert node.source_file == "src/db.py"
        assert node.source_line == 42
        assert node.severity == "critical"
        assert node.confidence == 0.95
        assert node.metadata["cwe"] == "89"
        assert "sql" in node.tags

    def test_node_to_dict(self):
        """Test node serialization to dict."""
        node = Node(
            id="node_003",
            type=NodeType.FUNCTION,
            name="process_input",
            description="Processes user input",
            tags=["utility"],
        )

        data = node.to_dict()

        assert data["id"] == "node_003"
        assert data["type"] == "function"
        assert data["name"] == "process_input"
        assert data["tags"] == ["utility"]
        assert "created_at" in data
        assert "updated_at" in data

    def test_node_from_dict(self):
        """Test node deserialization from dict."""
        data = {
            "id": "node_004",
            "type": "file",
            "name": "config.py",
            "description": "Configuration module",
            "severity": "low",
            "confidence": 0.8,
            "tags": ["config"],
            "status": "resolved",
        }

        node = Node.from_dict(data)

        assert node.id == "node_004"
        assert node.type == NodeType.FILE
        assert node.name == "config.py"
        assert node.severity == "low"
        assert node.confidence == 0.8
        assert node.status == "resolved"

    def test_node_roundtrip(self):
        """Test node serialization roundtrip."""
        original = Node(
            id="node_005",
            type=NodeType.PATTERN,
            name="Factory Pattern",
            description="Creates objects",
            source_workflow="code-review",
            severity="info",
            confidence=0.99,
            metadata={"language": "python"},
            tags=["design-pattern", "creational"],
        )

        data = original.to_dict()
        restored = Node.from_dict(data)

        assert restored.id == original.id
        assert restored.type == original.type
        assert restored.name == original.name
        assert restored.description == original.description
        assert restored.severity == original.severity
        assert restored.confidence == original.confidence

    def test_node_default_timestamps(self):
        """Test node has default timestamps."""
        node = Node(id="node_006", type=NodeType.BUG, name="Test")

        assert isinstance(node.created_at, datetime)
        assert isinstance(node.updated_at, datetime)


@pytest.mark.unit
class TestBugNode:
    """Tests for BugNode specialized class."""

    def test_bug_node_creation(self):
        """Test creating a bug node."""
        bug = BugNode(
            id="bug_001",
            type=NodeType.BUG,  # Will be overwritten
            name="Off-by-one error",
            description="Loop iterates one too many times",
            root_cause="Incorrect loop condition",
            fix_suggestion="Use < instead of <=",
            reproduction_steps=["Run test_loop", "Observe index out of bounds"],
        )

        assert bug.type == NodeType.BUG
        assert bug.root_cause == "Incorrect loop condition"
        assert bug.fix_suggestion == "Use < instead of <="
        assert len(bug.reproduction_steps) == 2


@pytest.mark.unit
class TestVulnerabilityNode:
    """Tests for VulnerabilityNode specialized class."""

    def test_vulnerability_node_creation(self):
        """Test creating a vulnerability node."""
        vuln = VulnerabilityNode(
            id="vuln_001",
            type=NodeType.VULNERABILITY,
            name="XSS Attack",
            description="Cross-site scripting vulnerability",
            cwe_id="CWE-79",
            cvss_score=7.5,
            attack_vector="NETWORK",
            remediation="Sanitize user input before rendering",
        )

        assert vuln.type == NodeType.VULNERABILITY
        assert vuln.cwe_id == "CWE-79"
        assert vuln.cvss_score == 7.5
        assert vuln.attack_vector == "NETWORK"


@pytest.mark.unit
class TestPerformanceNode:
    """Tests for PerformanceNode specialized class."""

    def test_performance_node_creation(self):
        """Test creating a performance node."""
        perf = PerformanceNode(
            id="perf_001",
            type=NodeType.PERFORMANCE_ISSUE,
            name="Slow database query",
            description="Query takes > 5s",
            metric="latency",
            current_value=5200.0,
            target_value=100.0,
            optimization_suggestion="Add index on user_id column",
        )

        assert perf.type == NodeType.PERFORMANCE_ISSUE
        assert perf.metric == "latency"
        assert perf.current_value == 5200.0
        assert perf.target_value == 100.0


@pytest.mark.unit
class TestPatternNode:
    """Tests for PatternNode specialized class."""

    def test_pattern_node_creation(self):
        """Test creating a pattern node."""
        pattern = PatternNode(
            id="pat_001",
            type=NodeType.PATTERN,
            name="Singleton Anti-Pattern",
            description="Global state makes testing difficult",
            pattern_type="anti-pattern",
            language="python",
            example_code="class Singleton: _instance = None",
            applies_to=["config", "logging", "database"],
        )

        assert pattern.type == NodeType.PATTERN
        assert pattern.pattern_type == "anti-pattern"
        assert pattern.language == "python"
        assert len(pattern.applies_to) == 3


@pytest.mark.unit
class TestEdgeType:
    """Tests for EdgeType enum."""

    def test_causal_edge_types(self):
        """Test causal relationship edge types."""
        assert EdgeType.CAUSES.value == "causes"
        assert EdgeType.CAUSED_BY.value == "caused_by"
        assert EdgeType.LEADS_TO.value == "leads_to"

    def test_resolution_edge_types(self):
        """Test resolution relationship edge types."""
        assert EdgeType.FIXED_BY.value == "fixed_by"
        assert EdgeType.FIXES.value == "fixes"
        assert EdgeType.MITIGATES.value == "mitigates"

    def test_similarity_edge_types(self):
        """Test similarity relationship edge types."""
        assert EdgeType.SIMILAR_TO.value == "similar_to"
        assert EdgeType.RELATED_TO.value == "related_to"
        assert EdgeType.DUPLICATE_OF.value == "duplicate_of"

    def test_structural_edge_types(self):
        """Test structural relationship edge types."""
        assert EdgeType.CONTAINS.value == "contains"
        assert EdgeType.CONTAINED_IN.value == "contained_in"
        assert EdgeType.DEPENDS_ON.value == "depends_on"


@pytest.mark.unit
class TestEdge:
    """Tests for Edge dataclass."""

    def test_edge_creation_basic(self):
        """Test creating a basic edge."""
        edge = Edge(
            source_id="node_001",
            target_id="node_002",
            type=EdgeType.CAUSES,
        )

        assert edge.source_id == "node_001"
        assert edge.target_id == "node_002"
        assert edge.type == EdgeType.CAUSES
        assert edge.weight == 1.0
        assert edge.confidence == 1.0

    def test_edge_creation_full(self):
        """Test creating an edge with all fields."""
        edge = Edge(
            source_id="bug_001",
            target_id="fix_001",
            type=EdgeType.FIXED_BY,
            weight=0.9,
            confidence=0.85,
            description="Bug fixed by commit abc123",
            source_workflow="bug-predict",
            metadata={"commit": "abc123"},
        )

        assert edge.weight == 0.9
        assert edge.confidence == 0.85
        assert edge.description == "Bug fixed by commit abc123"
        assert edge.source_workflow == "bug-predict"
        assert edge.metadata["commit"] == "abc123"

    def test_edge_id_property(self):
        """Test edge ID generation."""
        edge = Edge(
            source_id="node_001",
            target_id="node_002",
            type=EdgeType.CAUSES,
        )

        assert edge.id == "node_001-causes-node_002"

    def test_edge_to_dict(self):
        """Test edge serialization to dict."""
        edge = Edge(
            source_id="file_001",
            target_id="func_001",
            type=EdgeType.CONTAINS,
            weight=1.0,
            description="File contains function",
        )

        data = edge.to_dict()

        assert data["source_id"] == "file_001"
        assert data["target_id"] == "func_001"
        assert data["type"] == "contains"
        assert data["weight"] == 1.0
        assert "created_at" in data

    def test_edge_from_dict(self):
        """Test edge deserialization from dict."""
        data = {
            "source_id": "test_001",
            "target_id": "func_001",
            "type": "tests",
            "weight": 0.95,
            "confidence": 0.9,
            "description": "Test covers function",
        }

        edge = Edge.from_dict(data)

        assert edge.source_id == "test_001"
        assert edge.target_id == "func_001"
        assert edge.type == EdgeType.TESTS
        assert edge.weight == 0.95
        assert edge.confidence == 0.9

    def test_edge_roundtrip(self):
        """Test edge serialization roundtrip."""
        original = Edge(
            source_id="vuln_001",
            target_id="file_001",
            type=EdgeType.AFFECTS,
            weight=0.8,
            confidence=0.95,
            description="Vulnerability affects file",
            source_workflow="security-audit",
            metadata={"severity": "high"},
        )

        data = original.to_dict()
        restored = Edge.from_dict(data)

        assert restored.source_id == original.source_id
        assert restored.target_id == original.target_id
        assert restored.type == original.type
        assert restored.weight == original.weight
        assert restored.confidence == original.confidence

    def test_edge_default_timestamp(self):
        """Test edge has default timestamp."""
        edge = Edge(
            source_id="a",
            target_id="b",
            type=EdgeType.RELATED_TO,
        )

        assert isinstance(edge.created_at, datetime)


@pytest.mark.unit
class TestReverseEdgeTypes:
    """Tests for REVERSE_EDGE_TYPES mapping."""

    def test_causal_reverses(self):
        """Test causal edge type reverses."""
        assert REVERSE_EDGE_TYPES[EdgeType.CAUSES] == EdgeType.CAUSED_BY
        assert REVERSE_EDGE_TYPES[EdgeType.CAUSED_BY] == EdgeType.CAUSES

    def test_fix_reverses(self):
        """Test fix edge type reverses."""
        assert REVERSE_EDGE_TYPES[EdgeType.FIXED_BY] == EdgeType.FIXES
        assert REVERSE_EDGE_TYPES[EdgeType.FIXES] == EdgeType.FIXED_BY

    def test_structural_reverses(self):
        """Test structural edge type reverses."""
        assert REVERSE_EDGE_TYPES[EdgeType.CONTAINS] == EdgeType.CONTAINED_IN
        assert REVERSE_EDGE_TYPES[EdgeType.CONTAINED_IN] == EdgeType.CONTAINS

    def test_symmetric_types(self):
        """Test symmetric edge types reverse to themselves."""
        assert REVERSE_EDGE_TYPES[EdgeType.SIMILAR_TO] == EdgeType.SIMILAR_TO
        assert REVERSE_EDGE_TYPES[EdgeType.RELATED_TO] == EdgeType.RELATED_TO
        assert REVERSE_EDGE_TYPES[EdgeType.DUPLICATE_OF] == EdgeType.DUPLICATE_OF

    def test_reverse_mappings_are_bidirectional(self):
        """Test that reverse mappings are properly bidirectional.

        For edge types that have reverses defined, verify that:
        - A -> B implies B -> A (bidirectional mapping)
        """
        for edge_type, reverse_type in REVERSE_EDGE_TYPES.items():
            # The reverse of the reverse should be the original
            assert reverse_type in REVERSE_EDGE_TYPES, f"{reverse_type} not in REVERSE_EDGE_TYPES"
            assert REVERSE_EDGE_TYPES[reverse_type] == edge_type or edge_type == reverse_type

    def test_reverse_mapping_count(self):
        """Test that we have a reasonable number of reverse mappings."""
        # At least 15 edge types should have reverses
        assert len(REVERSE_EDGE_TYPES) >= 15

    def test_common_edge_types_have_reverses(self):
        """Test that commonly used edge types have reverse mappings."""
        common_types = [
            EdgeType.CAUSES,
            EdgeType.FIXED_BY,
            EdgeType.CONTAINS,
            EdgeType.TESTS,
            EdgeType.AFFECTS,
        ]

        for edge_type in common_types:
            assert edge_type in REVERSE_EDGE_TYPES, f"{edge_type} should have reverse"


@pytest.mark.unit
class TestWizardEdgePatterns:
    """Tests for WORKFLOW_EDGE_PATTERNS configuration."""

    def test_security_audit_patterns(self):
        """Test security-audit wizard has edge patterns."""
        patterns = WORKFLOW_EDGE_PATTERNS["security-audit"]
        assert len(patterns) > 0

        edge_types = [p[0] for p in patterns]
        assert EdgeType.FIXED_BY in edge_types
        assert EdgeType.AFFECTS in edge_types

    def test_bug_predict_patterns(self):
        """Test bug-predict wizard has edge patterns."""
        patterns = WORKFLOW_EDGE_PATTERNS["bug-predict"]
        assert len(patterns) > 0

        edge_types = [p[0] for p in patterns]
        assert EdgeType.CAUSES in edge_types
        assert EdgeType.SIMILAR_TO in edge_types

    def test_test_gen_patterns(self):
        """Test test-gen wizard has edge patterns."""
        patterns = WORKFLOW_EDGE_PATTERNS["test-gen"]
        assert len(patterns) > 0

        edge_types = [p[0] for p in patterns]
        assert EdgeType.TESTS in edge_types
        assert EdgeType.COVERS in edge_types

    def test_all_wizards_have_patterns(self):
        """Test expected wizards have edge patterns."""
        expected_wizards = [
            "security-audit",
            "bug-predict",
            "perf-audit",
            "code-review",
            "test-gen",
            "dependency-check",
        ]

        for wizard in expected_wizards:
            assert wizard in WORKFLOW_EDGE_PATTERNS, f"{wizard} missing patterns"
