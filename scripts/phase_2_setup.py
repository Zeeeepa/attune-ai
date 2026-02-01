#!/usr/bin/env python
"""Phase 2 Setup - Initialize Pattern Library with Phase 1 Learnings

This script initializes the shared in-memory PatternLibrary with all 10 patterns
discovered during Phase 1 (Files 1-3 refactoring).

No external dependencies required - uses in-memory storage for real-time pattern sharing.
"""

import json

import structlog

from attune.pattern_library import Pattern, PatternLibrary

logger = structlog.get_logger()


def make_pattern(
    id: str,
    type: str,
    name: str,
    desc: str,
    context: dict,
    tags: list,
    code: str,
    conf: float = 1.0,
) -> Pattern:
    """Helper to create Pattern with correct fields."""
    return Pattern(
        id=id,
        agent_id="Phase_1_Learning",
        pattern_type=type,
        name=name,
        description=desc,
        context=context,
        tags=tags,
        code=code.strip(),
        confidence=conf,
    )


def create_phase_1_patterns() -> list[Pattern]:
    """Create 10 patterns discovered during Phase 1 refactoring."""

    patterns = [
        # Pattern 1: String ID Validation
        Pattern(
            id="pattern_1_string_id_validation",
            agent_id="Phase_1_Learning",
            pattern_type="input_validation",
            name="String ID Validation",
            description="Validate string ID parameters are non-empty and non-whitespace",
            context={
                "trigger": "Method with parameter like agent_id: str, user_id: str, pattern_id: str",
                "applicable_to": ["Library", "API", "CLI"],
                "priority": "MEDIUM",
                "discovered_in": "pattern_library.py",
                "auto_fixable": True,
            },
            tags=["validation", "input", "string", "id"],
            code="""
# Check for empty or whitespace-only strings
if not agent_id or not agent_id.strip():
    raise ValueError("agent_id cannot be empty")
            """.strip(),
            confidence=1.0,
        ),
        # Pattern 2: Duplicate Key Prevention
        Pattern(
            id="pattern_2_duplicate_key_prevention",
            agent_id="Phase_1_Learning",
            pattern_type="data_integrity",
            name="Duplicate Key Prevention",
            description="Prevent duplicate keys when adding to dictionaries",
            context={
                "trigger": "Adding to dictionary without checking if key exists",
                "applicable_to": ["Library", "API"],
                "priority": "MEDIUM",
                "discovered_in": "pattern_library.py",
                "auto_fixable": True,
            },
            tags=["dictionary", "duplicate", "data-integrity"],
            code="""
# Check for duplicates before adding
if pattern.id in self.patterns:
    raise ValueError(
        f"Pattern '{pattern.id}' already exists. "
        f"Use a different ID or remove the existing pattern first."
    )
self.patterns[pattern.id] = pattern
            """.strip(),
            confidence=1.0,
        ),
        # Pattern 3: Cycle-Safe Recursion
        Pattern(
            id="pattern_3_cycle_safe_recursion",
            agent_id="Phase_1_Learning",
            pattern_type="algorithm_correctness",
            name="Cycle-Safe Recursion",
            description="Add cycle detection to recursive graph/tree traversal",
            context={
                "trigger": "Recursive method traversing graph structures without cycle detection",
                "applicable_to": ["Library"],
                "priority": "MEDIUM",
                "discovered_in": "pattern_library.py",
                "auto_fixable": False,  # Requires careful analysis
                "risk": "Infinite recursion if cycles exist",
            },
            tags=["recursion", "graph", "cycle-detection", "algorithm"],
            code="""
def get_related_patterns(
    self,
    pattern_id: str,
    depth: int = 1,
    _visited: set[str] | None = None
) -> list[Pattern]:
    # Initialize visited set on first call
    if _visited is None:
        _visited = {pattern_id}

    if depth <= 0 or pattern_id not in self.pattern_graph:
        return []

    related_ids = set(self.pattern_graph[pattern_id])

    if depth > 1:
        for related_id in list(related_ids):
            # Check visited BEFORE recursing
            if related_id not in _visited:
                _visited.add(related_id)
                deeper = self.get_related_patterns(related_id, depth - 1, _visited)
                related_ids.update(p.id for p in deeper)

    return [self.patterns[pid] for pid in related_ids if pid in self.patterns]
            """.strip(),
            confidence=0.9,
        ),
        # Pattern 4: Range Validation
        Pattern(
            id="pattern_4_range_validation",
            agent_id="Phase_1_Learning",
            pattern_type="input_validation",
            name="Range Validation",
            description="Validate float parameters are within expected range (0-1 for probabilities)",
            context={
                "trigger": "Float parameter representing probability, confidence, or percentage",
                "applicable_to": ["Library", "API", "CLI"],
                "priority": "MEDIUM",
                "discovered_in": "pattern_library.py",
                "auto_fixable": True,
            },
            tags=["validation", "range", "probability", "confidence"],
            code="""
# Validate probability/confidence is in [0, 1]
if not 0.0 <= min_confidence <= 1.0:
    raise ValueError(f"min_confidence must be 0-1, got {min_confidence}")
            """.strip(),
            confidence=1.0,
        ),
        # Pattern 5: Type Validation
        Pattern(
            id="pattern_5_type_validation",
            agent_id="Phase_1_Learning",
            pattern_type="input_validation",
            name="Type Validation",
            description="Validate complex type parameters (dict, list, set)",
            context={
                "trigger": "Method accepting dict, list, or complex types without validation",
                "applicable_to": ["Library", "API", "CLI"],
                "priority": "LOW",
                "discovered_in": "pattern_library.py",
                "auto_fixable": True,
            },
            tags=["validation", "type", "isinstance"],
            code="""
# Validate type before using
if not isinstance(context, dict):
    raise TypeError(f"context must be dict, got {type(context).__name__}")
            """.strip(),
            confidence=1.0,
        ),
        # Pattern 6: File Path Validation ⭐ CRITICAL
        Pattern(
            id="pattern_6_file_path_validation",
            agent_id="Phase_1_Learning",
            pattern_type="security_path_traversal",
            name="File Path Validation",
            description="Validate file paths to prevent path traversal attacks",
            context={
                "trigger": "open(path) or Path(path) with user-provided path",
                "applicable_to": ["API", "CLI", "Workflows"],
                "priority": "CRITICAL",
                "discovered_in": "control_panel.py",
                "auto_fixable": True,
                "security_impact": "CRITICAL",
                "prevents": [
                    "Path traversal attacks (../../../etc/passwd)",
                    "Arbitrary file writes",
                    "System directory modifications",
                    "Null byte injection",
                ],
            },
            tags=["security", "path-traversal", "file-io", "validation"],
            code="""
def _validate_file_path(path: str, allowed_dir: str | None = None) -> Path:
    '''Validate file path to prevent path traversal and arbitrary writes.'''
    if not path or not isinstance(path, str):
        raise ValueError("path must be a non-empty string")

    # Check for null bytes
    if "\\x00" in path:
        raise ValueError("path contains null bytes")

    try:
        resolved = Path(path).resolve()
    except (OSError, RuntimeError) as e:
        raise ValueError(f"Invalid path: {e}")

    # Check if within allowed directory
    if allowed_dir:
        try:
            allowed = Path(allowed_dir).resolve()
            resolved.relative_to(allowed)
        except ValueError:
            raise ValueError(f"path must be within {allowed_dir}")

    # Check for dangerous system paths
    dangerous_paths = ["/etc", "/sys", "/proc", "/dev"]
    for dangerous in dangerous_paths:
        if str(resolved).startswith(dangerous):
            raise ValueError(f"Cannot write to system directory: {dangerous}")

    return resolved

# Usage:
validated_path = _validate_file_path(args.output)
with open(validated_path, 'w') as f:
    f.write(data)
            """.strip(),
            confidence=1.0,
        ),
        # Pattern 7: Validation Integration
        Pattern(
            id="pattern_7_validation_integration",
            agent_id="Phase_1_Learning",
            pattern_type="architecture_defensive",
            name="Validation Integration",
            description="Ensure all validation helpers are called at method entry",
            context={
                "trigger": "Public method in API/server code without centralized validation",
                "applicable_to": ["API", "CLI"],
                "priority": "HIGH",
                "discovered_in": "control_panel.py",
                "auto_fixable": False,  # Requires understanding of business logic
            },
            tags=["validation", "architecture", "api", "defensive"],
            code="""
def delete_pattern(self, pattern_id: str, user_id: str) -> bool:
    '''Delete pattern with comprehensive input validation.'''

    # Validate ALL inputs at method entry
    if not _validate_pattern_id(pattern_id):
        raise ValueError(f"Invalid pattern_id format: {pattern_id}")

    if not _validate_agent_id(user_id):
        raise ValueError(f"Invalid user_id format: {user_id}")

    # Business logic here (after validation)
    long_term = self._get_long_term()
    try:
        return long_term.delete_pattern(pattern_id, user_id)
    except Exception as e:
        logger.error("delete_pattern_failed", pattern_id=pattern_id, error=str(e))
        return False  # Graceful degradation
            """.strip(),
            confidence=0.8,
        ),
        # Pattern 8: Stats Error Handling
        Pattern(
            id="pattern_8_stats_error_handling",
            agent_id="Phase_1_Learning",
            pattern_type="reliability_graceful_degradation",
            name="Stats Error Handling",
            description="Gracefully handle errors in stats/metrics collection (best effort)",
            context={
                "trigger": "Operations collecting metrics/stats that may fail",
                "applicable_to": ["API", "Monitoring", "Telemetry"],
                "priority": "MEDIUM",
                "discovered_in": "control_panel.py",
                "auto_fixable": True,
                "pattern": "Log error + return default/False, don't crash",
            },
            tags=["error-handling", "stats", "metrics", "graceful-degradation"],
            code="""
def get_statistics(self) -> MemoryStats | None:
    '''Get statistics with graceful degradation on errors.'''
    try:
        redis_stats = self._redis.info("memory")
        return MemoryStats(
            total_keys=redis_stats.get("keys", 0),
            memory_used_mb=redis_stats.get("used_memory", 0) / (1024 * 1024)
        )
    except Exception as e:
        logger.error("stats_collection_failed", error=str(e))
        return None  # Best effort - don't crash
            """.strip(),
            confidence=1.0,
        ),
        # Pattern 9: CLI Argument Validation
        Pattern(
            id="pattern_9_cli_argument_validation",
            agent_id="Phase_1_Learning",
            pattern_type="security_input_sanitization",
            name="CLI Argument Validation",
            description="Validate CLI arguments from argparse before use in file operations",
            context={
                "trigger": "args.param from argparse used in file operations or system calls",
                "applicable_to": ["CLI"],
                "priority": "HIGH",
                "discovered_in": "cli.py",
                "auto_fixable": True,
                "security_impact": "HIGH",
            },
            tags=["cli", "argparse", "validation", "security"],
            code="""
def cmd_init(args):
    '''Initialize project with validated arguments.

    Raises:
        ValueError: If output path is invalid or unsafe
    '''
    config_format = args.format
    output_path = args.output or f"attune.config.{config_format}"

    # Validate output path to prevent path traversal attacks
    validated_path = _validate_file_path(output_path)

    logger.info(f"Initializing project with format: {config_format}")

    config = EmpathyConfig()
    if config_format == "yaml":
        config.to_yaml(str(validated_path))
    elif config_format == "json":
        config.to_json(str(validated_path))
            """.strip(),
            confidence=1.0,
        ),
        # Pattern 10: Subprocess Safety Audit
        Pattern(
            id="pattern_10_subprocess_safety",
            agent_id="Phase_1_Learning",
            pattern_type="security_command_injection",
            name="Subprocess Safety Audit",
            description="Prevent command injection by using array form with shell=False",
            context={
                "trigger": "subprocess.run(), os.system(), shell=True with user input",
                "applicable_to": ["CLI", "Workflows", "Backend"],
                "priority": "CRITICAL",
                "discovered_in": "cli.py",
                "auto_fixable": False,  # Requires manual security review
                "security_impact": "CRITICAL",
                "prevents": [
                    "Command injection attacks",
                    "Shell escape attacks",
                    "Arbitrary command execution",
                ],
            },
            tags=["security", "subprocess", "command-injection", "shell"],
            code="""
# UNSAFE - DO NOT USE:
import os
user_message = args.message
os.system(f"git commit -m '{user_message}'")  # INJECTION RISK!

# SAFE - Use array form:
import subprocess
user_message = args.message
subprocess.run(
    ["git", "commit", "-m", user_message],  # Array form
    shell=False,  # Never True with user input
    check=True
)
            """.strip(),
            confidence=0.7,  # Lower confidence - requires manual review
        ),
    ]

    return patterns


def initialize_pattern_library() -> PatternLibrary:
    """Initialize shared in-memory PatternLibrary with Phase 1 patterns.

    Returns:
        PatternLibrary instance ready for agent use
    """
    logger.info("Initializing Pattern Library for Phase 2")

    # Create in-memory library (no Redis needed!)
    library = PatternLibrary()

    # Load Phase 1 patterns
    patterns = create_phase_1_patterns()

    # Contribute each pattern
    for pattern in patterns:
        library.contribute_pattern("Phase_1_Learning", pattern)
        logger.info(
            "Pattern loaded",
            pattern_id=pattern.id,
            priority=pattern.context.get("priority"),
            auto_fixable=pattern.context.get("auto_fixable"),
        )

    # Get statistics
    stats = library.get_library_stats()
    logger.info(
        "Pattern Library initialized",
        total_patterns=stats["total_patterns"],
        patterns_by_type=stats["patterns_by_type"],
        backend="in-memory",
    )

    return library


def export_patterns_for_reference(
    library: PatternLibrary, output_path: str = "phase_1_patterns_export.json"
):
    """Export patterns to JSON for reference/documentation.

    Args:
        library: PatternLibrary to export
        output_path: Output file path
    """

    export_data = {
        "version": "1.0.0",
        "phase": "Phase 1 Complete - Ready for Phase 2",
        "patterns": [
            {
                "id": p.id,
                "type": p.pattern_type,
                "name": p.name,
                "description": p.description,
                "context": p.context,
                "tags": p.tags,
                "code": p.code,
                "confidence": p.confidence,
                "success_rate": p.success_rate,
            }
            for p in library.patterns.values()
        ],
        "stats": library.get_library_stats(),
    }

    with open(output_path, "w") as f:
        json.dump(export_data, f, indent=2)

    logger.info(f"Patterns exported to {output_path}")


if __name__ == "__main__":
    # Initialize library
    library = initialize_pattern_library()

    # Export for reference
    export_patterns_for_reference(library)

    print("\n" + "=" * 80)
    print("✅ Pattern Library Initialized Successfully")
    print("=" * 80)
    print(f"\nTotal Patterns: {len(library.patterns)}")
    print("\nPatterns by Priority:")
    priorities = {}
    for p in library.patterns.values():
        priority = p.context.get("priority", "UNKNOWN")
        priorities[priority] = priorities.get(priority, 0) + 1

    for priority in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        if priority in priorities:
            print(f"  {priority}: {priorities[priority]}")

    print("\nReady for Phase 2 parallel refactoring!")
    print("=" * 80)
