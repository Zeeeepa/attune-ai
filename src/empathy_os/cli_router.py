"""Hybrid CLI Router - Slash Commands + Natural Language

Supports both structured slash commands and natural language routing:
- Slash commands: empathy /dev commit
- Natural language: empathy "commit my changes"
- Single word: empathy commit (infers /dev commit)

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from empathy_os.routing import SmartRouter


@dataclass
class RoutingPreference:
    """User's learned routing preferences."""

    keyword: str
    slash_command: str
    usage_count: int = 0
    confidence: float = 1.0


class HybridRouter:
    """Routes user input to appropriate commands or workflows.

    Supports three input modes:
    1. Slash commands: /dev commit (direct, structured)
    2. Single words: commit (infers /dev commit from context)
    3. Natural language: "I need to commit" (uses SmartRouter)

    Example:
        router = HybridRouter()

        # Direct slash command
        result = await router.route("/dev commit")
        # → {type: "slash", hub: "dev", command: "commit"}

        # Single word inference
        result = await router.route("commit")
        # → {type: "inferred", hub: "dev", command: "commit", confidence: 0.9}

        # Natural language
        result = await router.route("I want to commit my changes")
        # → {type: "natural", workflow: "commit", slash_equivalent: "/dev commit"}
    """

    def __init__(self, preferences_path: str | None = None):
        """Initialize hybrid router.

        Args:
            preferences_path: Path to user preferences YAML
                Default: .empathy/routing_preferences.yaml
        """
        self.preferences_path = Path(
            preferences_path or Path.home() / ".empathy" / "routing_preferences.yaml"
        )
        self.smart_router = SmartRouter()
        self.preferences: dict[str, RoutingPreference] = {}

        # Command to slash command mapping
        self._command_map = {
            # Dev commands
            "commit": "/dev commit",
            "review": "/dev review-pr",
            "review-pr": "/dev review-pr",
            "refactor": "/dev refactor",
            "perf": "/dev perf-audit",
            "perf-audit": "/dev perf-audit",
            # Testing commands
            "test": "/testing run",
            "tests": "/testing run",
            "coverage": "/testing coverage",
            "generate-tests": "/testing gen",
            "test-gen": "/testing gen",
            # Learning commands
            "evaluate": "/learning evaluate",
            "patterns": "/learning patterns",
            "improve": "/learning improve",
            # Workflow commands
            "security": "/workflows security-audit",
            "security-audit": "/workflows security-audit",
            "bug-predict": "/workflows bug-predict",
            "bugs": "/workflows bug-predict",
            # Context commands
            "status": "/context status",
            "memory": "/context memory",
            "state": "/context state",
            # Doc commands
            "explain": "/docs explain",
            "document": "/docs generate",
            "overview": "/docs overview",
        }

        # Hub descriptions for disambiguation
        self._hub_descriptions = {
            "dev": "Development tools (commits, reviews, refactoring)",
            "testing": "Test generation and coverage analysis",
            "learning": "Session evaluation and pattern learning",
            "workflows": "AI-powered workflows (security, bugs, performance)",
            "context": "Memory and state management",
            "docs": "Documentation generation",
            "plan": "Development planning and architecture",
            "release": "Release preparation and publishing",
            "utilities": "Utility tools (profiling, dependencies)",
        }

        self._load_preferences()

    def _load_preferences(self) -> None:
        """Load user routing preferences from disk."""
        if not self.preferences_path.exists():
            return

        try:
            with open(self.preferences_path) as f:
                data = yaml.safe_load(f) or {}

            for keyword, pref_data in data.get("preferences", {}).items():
                self.preferences[keyword] = RoutingPreference(
                    keyword=keyword,
                    slash_command=pref_data["slash_command"],
                    usage_count=pref_data.get("usage_count", 0),
                    confidence=pref_data.get("confidence", 1.0),
                )
        except Exception as e:
            print(f"Warning: Could not load routing preferences: {e}")

    def _save_preferences(self) -> None:
        """Save user routing preferences to disk."""
        self.preferences_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "preferences": {
                pref.keyword: {
                    "slash_command": pref.slash_command,
                    "usage_count": pref.usage_count,
                    "confidence": pref.confidence,
                }
                for pref in self.preferences.values()
            }
        }

        with open(self.preferences_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False)

    async def route(
        self, user_input: str, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Route user input to appropriate command or workflow.

        Args:
            user_input: User's input (slash command, keyword, or natural language)
            context: Optional context (current file, project info, etc.)

        Returns:
            Routing result with type, command/workflow, and metadata
        """
        user_input = user_input.strip()

        # Level 1: Slash command (direct execution)
        if user_input.startswith("/"):
            return self._route_slash_command(user_input)

        # Level 2: Single word or known command (inference)
        words = user_input.split()
        if len(words) <= 2:
            inferred = self._infer_command(user_input)
            if inferred:
                return inferred

        # Level 3: Natural language (SmartRouter)
        return await self._route_natural_language(user_input, context)

    def _route_slash_command(self, command: str) -> dict[str, Any]:
        """Route slash command directly.

        Args:
            command: Slash command like "/dev commit"

        Returns:
            Routing result
        """
        parts = command[1:].split(maxsplit=1)  # Remove leading /
        hub = parts[0] if parts else "help"
        subcommand = parts[1] if len(parts) > 1 else None

        return {
            "type": "slash",
            "hub": hub,
            "command": subcommand,
            "original": command,
            "confidence": 1.0,
        }

    def _infer_command(self, keyword: str) -> dict[str, Any] | None:
        """Infer slash command from keyword or short phrase.

        Args:
            keyword: Single word or short phrase

        Returns:
            Routing result if inference successful, None otherwise
        """
        keyword_lower = keyword.lower().strip()

        # Check learned preferences first
        if keyword_lower in self.preferences:
            pref = self.preferences[keyword_lower]
            slash_cmd = pref.slash_command

            # Update usage count
            pref.usage_count += 1
            self._save_preferences()

            return self._parse_inferred(slash_cmd, keyword, pref.confidence, "learned")

        # Check built-in command map
        if keyword_lower in self._command_map:
            slash_cmd = self._command_map[keyword_lower]
            return self._parse_inferred(slash_cmd, keyword, 0.9, "builtin")

        # Check for hub names (show hub menu)
        if keyword_lower in self._hub_descriptions:
            return {
                "type": "hub_menu",
                "hub": keyword_lower,
                "original": keyword,
                "confidence": 1.0,
            }

        return None

    def _parse_inferred(
        self, slash_cmd: str, original: str, confidence: float, source: str
    ) -> dict[str, Any]:
        """Parse inferred slash command."""
        parts = slash_cmd[1:].split(maxsplit=1)  # Remove leading /
        hub = parts[0] if parts else "help"
        subcommand = parts[1] if len(parts) > 1 else None

        return {
            "type": "inferred",
            "hub": hub,
            "command": subcommand,
            "original": original,
            "slash_equivalent": slash_cmd,
            "confidence": confidence,
            "source": source,  # learned, builtin
        }

    async def _route_natural_language(
        self, text: str, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Route natural language input using SmartRouter.

        Args:
            text: Natural language input
            context: Optional context

        Returns:
            Routing result with workflow and slash equivalent
        """
        # Use SmartRouter for classification
        decision = await self.smart_router.route(text, context)

        # Map workflow to slash command
        slash_equivalent = self._workflow_to_slash(decision.primary_workflow)

        return {
            "type": "natural",
            "workflow": decision.primary_workflow,
            "secondary_workflows": decision.secondary_workflows,
            "slash_equivalent": slash_equivalent,
            "confidence": decision.confidence,
            "reasoning": decision.reasoning,
            "original": text,
        }

    def _workflow_to_slash(self, workflow: str) -> str:
        """Map workflow name to slash command equivalent.

        Args:
            workflow: Workflow name (e.g., "security-audit")

        Returns:
            Slash command equivalent
        """
        # Workflow to slash command mapping
        workflow_map = {
            "security-audit": "/workflows security-audit",
            "bug-predict": "/workflows bug-predict",
            "code-review": "/dev review",
            "test-gen": "/testing gen",
            "perf-audit": "/dev perf-audit",
            "commit": "/dev commit",
            "refactor": "/dev refactor",
        }

        return workflow_map.get(workflow, f"/workflows {workflow}")

    def learn_preference(self, keyword: str, slash_command: str) -> None:
        """Learn user's routing preference.

        Args:
            keyword: Keyword user typed
            slash_command: Command that was executed
        """
        if keyword in self.preferences:
            pref = self.preferences[keyword]
            pref.usage_count += 1
            # Increase confidence with repeated usage
            pref.confidence = min(1.0, pref.confidence + 0.05)
        else:
            self.preferences[keyword] = RoutingPreference(
                keyword=keyword,
                slash_command=slash_command,
                usage_count=1,
                confidence=0.8,
            )

        self._save_preferences()

    def get_suggestions(self, partial: str) -> list[str]:
        """Get command suggestions based on partial input.

        Args:
            partial: Partial command input

        Returns:
            List of suggested commands
        """
        suggestions = []
        partial_lower = partial.lower()

        # Suggest slash commands
        for cmd in self._command_map.values():
            if partial_lower in cmd.lower():
                suggestions.append(cmd)

        # Suggest learned preferences
        for pref in self.preferences.values():
            if partial_lower in pref.keyword.lower():
                suggestions.append(f"{pref.keyword} → {pref.slash_command}")

        return suggestions[:5]  # Top 5 suggestions


# Convenience functions
async def route_user_input(
    user_input: str, context: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Quick routing helper.

    Args:
        user_input: User's input
        context: Optional context

    Returns:
        Routing result
    """
    router = HybridRouter()
    return await router.route(user_input, context)


def is_slash_command(text: str) -> bool:
    """Check if text is a slash command.

    Args:
        text: Input text

    Returns:
        True if slash command, False otherwise
    """
    return text.strip().startswith("/")
