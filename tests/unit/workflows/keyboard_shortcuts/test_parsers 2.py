"""Comprehensive tests for keyboard shortcut parsers.

Tests cover:
- VSCode package.json parsing
- Python pyproject.toml parsing
- YAML manifest parsing
- Composite parser feature discovery
- Error handling and edge cases
"""

import json

import pytest
import yaml

from empathy_os.workflows.keyboard_shortcuts.parsers import (
    CompositeParser,
    LLMFeatureAnalyzer,
    PyProjectParser,
    VSCodeCommandParser,
    YAMLManifestParser,
)
from empathy_os.workflows.keyboard_shortcuts.schema import (
    Feature,
    FrequencyTier,
)


class TestVSCodeCommandParser:
    """Tests for VSCode package.json parser."""

    def test_can_parse_valid_package_json(self, tmp_path):
        """Test parser recognizes valid package.json files."""
        parser = VSCodeCommandParser()
        package_file = tmp_path / "package.json"
        package_file.write_text("{}")

        assert parser.can_parse(package_file) is True

    def test_can_parse_rejects_wrong_filename(self, tmp_path):
        """Test parser rejects non-package.json files."""
        parser = VSCodeCommandParser()
        wrong_file = tmp_path / "other.json"
        wrong_file.write_text("{}")

        assert parser.can_parse(wrong_file) is False

    def test_can_parse_rejects_nonexistent_file(self, tmp_path):
        """Test parser rejects files that don't exist."""
        parser = VSCodeCommandParser()
        missing_file = tmp_path / "package.json"

        assert parser.can_parse(missing_file) is False

    def test_parse_basic_commands(self, tmp_path):
        """Test parsing basic VSCode commands."""
        parser = VSCodeCommandParser()
        package_file = tmp_path / "package.json"

        package_data = {
            "contributes": {
                "commands": [
                    {
                        "command": "empathy.morning",
                        "title": "Empathy: Morning Briefing",
                        "icon": "$(calendar)",
                    },
                    {
                        "command": "empathy.ship",
                        "title": "Empathy: Ship Check",
                        "icon": "$(rocket)",
                    },
                ],
            },
        }
        package_file.write_text(json.dumps(package_data))

        features = parser.parse(package_file)

        assert len(features) == 2
        assert features[0].id == "morning"
        assert features[0].name == "Morning Briefing"
        assert features[0].command == "empathy.morning"
        assert features[0].icon == "$(calendar)"
        assert features[1].id == "ship"
        assert features[1].name == "Ship Check"

    def test_parse_with_category_extraction(self, tmp_path):
        """Test extracting category from title with arrow notation."""
        parser = VSCodeCommandParser()
        package_file = tmp_path / "package.json"

        package_data = {
            "contributes": {
                "commands": [
                    {
                        "command": "empathy.quickMorning",
                        "title": "Empathy: Quick → Morning",
                    },
                ],
            },
        }
        package_file.write_text(json.dumps(package_data))

        features = parser.parse(package_file)

        assert len(features) == 1
        assert features[0].name == "Morning"
        # Category is inferred but not stored in Feature directly

    def test_parse_infers_frequency_tier_from_category(self, tmp_path):
        """Test frequency tier inference based on category."""
        parser = VSCodeCommandParser()
        package_file = tmp_path / "package.json"

        package_data = {
            "contributes": {
                "commands": [
                    {"command": "empathy.quickAction", "title": "Empathy: Quick → Action"},
                    {"command": "empathy.viewDashboard", "title": "Empathy: View → Dashboard"},
                    {"command": "empathy.advancedTool", "title": "Empathy: Advanced Tool"},
                ],
            },
        }
        package_file.write_text(json.dumps(package_data))

        features = parser.parse(package_file)

        assert len(features) == 3
        # Quick category should be DAILY
        assert features[0].frequency == FrequencyTier.DAILY
        # View category should be FREQUENT
        assert features[1].frequency == FrequencyTier.FREQUENT
        # No specific category should be ADVANCED
        assert features[2].frequency == FrequencyTier.ADVANCED

    def test_parse_skips_internal_commands(self, tmp_path):
        """Test that commands starting with _ are skipped."""
        parser = VSCodeCommandParser()
        package_file = tmp_path / "package.json"

        package_data = {
            "contributes": {
                "commands": [
                    {"command": "_empathy.internal", "title": "Internal Command"},
                    {"command": "empathy.public", "title": "Public Command"},
                ],
            },
        }
        package_file.write_text(json.dumps(package_data))

        features = parser.parse(package_file)

        assert len(features) == 1
        assert features[0].command == "empathy.public"

    def test_parse_skips_commands_without_title(self, tmp_path):
        """Test that commands without titles are skipped."""
        parser = VSCodeCommandParser()
        package_file = tmp_path / "package.json"

        package_data = {
            "contributes": {
                "commands": [
                    {"command": "empathy.noTitle"},
                    {"command": "empathy.withTitle", "title": "Has Title"},
                ],
            },
        }
        package_file.write_text(json.dumps(package_data))

        features = parser.parse(package_file)

        assert len(features) == 1
        assert features[0].name == "Has Title"

    def test_parse_handles_invalid_json(self, tmp_path):
        """Test graceful handling of invalid JSON."""
        parser = VSCodeCommandParser()
        package_file = tmp_path / "package.json"
        package_file.write_text("{ invalid json }")

        features = parser.parse(package_file)

        assert features == []

    def test_parse_handles_missing_file(self, tmp_path):
        """Test graceful handling of missing file."""
        parser = VSCodeCommandParser()
        missing_file = tmp_path / "package.json"

        features = parser.parse(missing_file)

        assert features == []

    def test_parse_handles_empty_contributes(self, tmp_path):
        """Test handling of package.json without contributes section."""
        parser = VSCodeCommandParser()
        package_file = tmp_path / "package.json"
        package_file.write_text(json.dumps({"name": "test"}))

        features = parser.parse(package_file)

        assert features == []

    def test_extract_category_with_colon_only(self):
        """Test category extraction from simple colon notation."""
        parser = VSCodeCommandParser()

        category = parser._extract_category("Empathy: Morning")

        assert category == "Empathy"

    def test_extract_category_with_arrow(self):
        """Test category extraction from arrow notation."""
        parser = VSCodeCommandParser()

        category = parser._extract_category("Empathy: Quick → Morning")

        assert category == "Quick"

    def test_extract_category_no_delimiter(self):
        """Test category extraction from plain text."""
        parser = VSCodeCommandParser()

        category = parser._extract_category("Morning Briefing")

        assert category == "General"

    def test_extract_name_with_arrow(self):
        """Test name extraction from arrow notation."""
        parser = VSCodeCommandParser()

        name = parser._extract_name("Empathy: Quick → Morning")

        assert name == "Morning"

    def test_extract_name_with_colon(self):
        """Test name extraction from colon notation."""
        parser = VSCodeCommandParser()

        name = parser._extract_name("Empathy: Morning Briefing")

        assert name == "Morning Briefing"

    def test_extract_name_plain_text(self):
        """Test name extraction from plain text."""
        parser = VSCodeCommandParser()

        name = parser._extract_name("Morning Briefing")

        assert name == "Morning Briefing"

    def test_infer_tier_daily_from_quick(self):
        """Test tier inference for quick category."""
        parser = VSCodeCommandParser()

        tier = parser._infer_tier("Quick Actions")

        assert tier == FrequencyTier.DAILY

    def test_infer_tier_daily_from_daily(self):
        """Test tier inference for daily category."""
        parser = VSCodeCommandParser()

        tier = parser._infer_tier("Daily Tasks")

        assert tier == FrequencyTier.DAILY

    def test_infer_tier_frequent_from_view(self):
        """Test tier inference for view category."""
        parser = VSCodeCommandParser()

        tier = parser._infer_tier("Views")

        assert tier == FrequencyTier.FREQUENT

    def test_infer_tier_frequent_from_workflow(self):
        """Test tier inference for workflow category."""
        parser = VSCodeCommandParser()

        tier = parser._infer_tier("Workflows")

        assert tier == FrequencyTier.FREQUENT

    def test_infer_tier_advanced_default(self):
        """Test tier inference defaults to advanced."""
        parser = VSCodeCommandParser()

        tier = parser._infer_tier("Random Category")

        assert tier == FrequencyTier.ADVANCED


class TestPyProjectParser:
    """Tests for pyproject.toml parser."""

    def test_can_parse_valid_pyproject_toml(self, tmp_path):
        """Test parser recognizes valid pyproject.toml files."""
        parser = PyProjectParser()
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text("")

        assert parser.can_parse(pyproject_file) is True

    def test_can_parse_rejects_wrong_filename(self, tmp_path):
        """Test parser rejects non-pyproject.toml files."""
        parser = PyProjectParser()
        wrong_file = tmp_path / "other.toml"
        wrong_file.write_text("")

        assert parser.can_parse(wrong_file) is False

    def test_can_parse_rejects_nonexistent_file(self, tmp_path):
        """Test parser rejects files that don't exist."""
        parser = PyProjectParser()
        missing_file = tmp_path / "pyproject.toml"

        assert parser.can_parse(missing_file) is False

    def test_parse_basic_scripts(self, tmp_path):
        """Test parsing basic CLI scripts."""
        parser = PyProjectParser()
        pyproject_file = tmp_path / "pyproject.toml"

        pyproject_content = """
[project.scripts]
empathy = "empathy_os.cli:main"
empathy-morning = "empathy_os.cli:morning"
"""
        pyproject_file.write_text(pyproject_content)

        features = parser.parse(pyproject_file)

        assert len(features) == 2
        assert features[0].id == "empathy"
        assert features[0].name == "Empathy"
        assert features[0].command == "cli.empathy"
        assert features[0].cli_alias == "empathy"
        assert features[0].frequency == FrequencyTier.FREQUENT

        assert features[1].id == "empathy_morning"
        assert features[1].name == "Empathy Morning"
        assert features[1].cli_alias == "empathy-morning"

    def test_parse_entry_points(self, tmp_path):
        """Test parsing entry points."""
        parser = PyProjectParser()
        pyproject_file = tmp_path / "pyproject.toml"

        pyproject_content = """
[project.entry-points."empathy.workflows"]
morning = "empathy_os.workflows.morning:MorningWorkflow"
ship = "empathy_os.workflows.ship:ShipWorkflow"
"""
        pyproject_file.write_text(pyproject_content)

        features = parser.parse(pyproject_file)

        assert len(features) == 2
        assert features[0].id == "empathy.workflows_morning"
        assert features[0].name == "Morning"
        assert features[0].frequency == FrequencyTier.ADVANCED

    def test_parse_handles_missing_tomllib(self, tmp_path, monkeypatch):
        """Test graceful handling when tomllib is not available."""
        parser = PyProjectParser()
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text("[project]")

        # Mock ImportError for both tomllib and tomli
        import sys

        original_modules = sys.modules.copy()

        # Remove tomllib and tomli from modules
        if "tomllib" in sys.modules:
            del sys.modules["tomllib"]
        if "tomli" in sys.modules:
            del sys.modules["tomli"]

        # Mock import to raise ImportError
        def mock_import(name, *args, **kwargs):
            if name in ("tomllib", "tomli"):
                raise ImportError(f"No module named '{name}'")
            return original_modules.get(name)

        monkeypatch.setattr("builtins.__import__", mock_import)

        features = parser.parse(pyproject_file)

        assert features == []

        # Restore modules
        sys.modules.update(original_modules)

    def test_parse_handles_invalid_toml(self, tmp_path):
        """Test graceful handling of invalid TOML."""
        parser = PyProjectParser()
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text("[ invalid toml")

        features = parser.parse(pyproject_file)

        assert features == []

    def test_parse_handles_missing_file(self, tmp_path):
        """Test graceful handling of missing file."""
        parser = PyProjectParser()
        missing_file = tmp_path / "pyproject.toml"

        features = parser.parse(missing_file)

        assert features == []

    def test_parse_handles_empty_file(self, tmp_path):
        """Test handling of empty pyproject.toml."""
        parser = PyProjectParser()
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text("")

        features = parser.parse(pyproject_file)

        assert features == []


class TestYAMLManifestParser:
    """Tests for features.yaml parser."""

    def test_can_parse_features_yaml(self, tmp_path):
        """Test parser recognizes features.yaml files."""
        parser = YAMLManifestParser()
        yaml_file = tmp_path / "features.yaml"
        yaml_file.write_text("")

        assert parser.can_parse(yaml_file) is True

    def test_can_parse_features_yml(self, tmp_path):
        """Test parser recognizes features.yml files."""
        parser = YAMLManifestParser()
        yml_file = tmp_path / "features.yml"
        yml_file.write_text("")

        assert parser.can_parse(yml_file) is True

    def test_can_parse_rejects_wrong_filename(self, tmp_path):
        """Test parser rejects non-features files."""
        parser = YAMLManifestParser()
        wrong_file = tmp_path / "other.yaml"
        wrong_file.write_text("")

        assert parser.can_parse(wrong_file) is False

    def test_parse_basic_features(self, tmp_path):
        """Test parsing basic feature manifest."""
        parser = YAMLManifestParser()
        yaml_file = tmp_path / "features.yaml"

        manifest_data = {
            "categories": [
                {
                    "name": "Quick Actions",
                    "tier": "daily",
                    "features": [
                        {
                            "id": "morning",
                            "name": "Morning Briefing",
                            "description": "Daily morning status",
                            "command": "empathy.morning",
                            "cli_alias": "empathy morning",
                            "frequency": "daily",
                        },
                    ],
                },
            ],
        }
        yaml_file.write_text(yaml.dump(manifest_data))

        features = parser.parse(yaml_file)

        assert len(features) == 1
        assert features[0].id == "morning"
        assert features[0].name == "Morning Briefing"
        assert features[0].command == "empathy.morning"
        assert features[0].cli_alias == "empathy morning"
        assert features[0].frequency == FrequencyTier.DAILY

    def test_parse_infers_tier_from_category(self, tmp_path):
        """Test that feature inherits tier from category."""
        parser = YAMLManifestParser()
        yaml_file = tmp_path / "features.yaml"

        manifest_data = {
            "categories": [
                {
                    "name": "Views",
                    "tier": "frequent",
                    "features": [
                        {
                            "id": "dashboard",
                            "name": "Dashboard",
                            "command": "empathy.dashboard",
                        },
                    ],
                },
            ],
        }
        yaml_file.write_text(yaml.dump(manifest_data))

        features = parser.parse(yaml_file)

        assert len(features) == 1
        assert features[0].frequency == FrequencyTier.FREQUENT

    def test_parse_feature_overrides_category_tier(self, tmp_path):
        """Test that feature-level frequency overrides category tier."""
        parser = YAMLManifestParser()
        yaml_file = tmp_path / "features.yaml"

        manifest_data = {
            "categories": [
                {
                    "name": "Actions",
                    "tier": "frequent",
                    "features": [
                        {
                            "id": "critical",
                            "name": "Critical Action",
                            "command": "empathy.critical",
                            "frequency": "daily",
                        },
                    ],
                },
            ],
        }
        yaml_file.write_text(yaml.dump(manifest_data))

        features = parser.parse(yaml_file)

        assert len(features) == 1
        assert features[0].frequency == FrequencyTier.DAILY

    def test_parse_handles_invalid_tier(self, tmp_path):
        """Test handling of invalid tier values."""
        parser = YAMLManifestParser()
        yaml_file = tmp_path / "features.yaml"

        manifest_data = {
            "categories": [
                {
                    "name": "Actions",
                    "tier": "invalid_tier",
                    "features": [
                        {
                            "id": "action",
                            "name": "Action",
                            "command": "empathy.action",
                        },
                    ],
                },
            ],
        }
        yaml_file.write_text(yaml.dump(manifest_data))

        features = parser.parse(yaml_file)

        assert len(features) == 1
        # Should default to FREQUENT
        assert features[0].frequency == FrequencyTier.FREQUENT

    def test_parse_generates_id_from_name(self, tmp_path):
        """Test that ID is generated from name if missing."""
        parser = YAMLManifestParser()
        yaml_file = tmp_path / "features.yaml"

        manifest_data = {
            "categories": [
                {
                    "name": "Actions",
                    "features": [
                        {
                            "name": "Morning Briefing",
                            "command": "empathy.morning",
                        },
                    ],
                },
            ],
        }
        yaml_file.write_text(yaml.dump(manifest_data))

        features = parser.parse(yaml_file)

        assert len(features) == 1
        assert features[0].id == "morning_briefing"

    def test_parse_handles_invalid_yaml(self, tmp_path):
        """Test graceful handling of invalid YAML."""
        parser = YAMLManifestParser()
        yaml_file = tmp_path / "features.yaml"
        yaml_file.write_text("{ invalid: yaml: structure:")

        features = parser.parse(yaml_file)

        assert features == []

    def test_parse_handles_missing_file(self, tmp_path):
        """Test graceful handling of missing file."""
        parser = YAMLManifestParser()
        missing_file = tmp_path / "features.yaml"

        features = parser.parse(missing_file)

        assert features == []

    def test_parse_full_manifest(self, tmp_path):
        """Test parsing complete manifest with project metadata."""
        parser = YAMLManifestParser()
        yaml_file = tmp_path / "features.yaml"

        manifest_data = {
            "project": {
                "name": "empathy-framework",
                "type": "vscode-extension",
                "prefix": "ctrl+shift+e",
            },
            "categories": [
                {
                    "name": "Quick Actions",
                    "icon": "$(zap)",
                    "tier": "daily",
                    "features": [
                        {
                            "id": "morning",
                            "name": "Morning",
                            "description": "Morning briefing",
                            "command": "empathy.morning",
                        },
                    ],
                },
            ],
        }
        yaml_file.write_text(yaml.dump(manifest_data))

        manifest = parser.parse_full_manifest(yaml_file)

        assert manifest is not None
        assert manifest.project_name == "empathy-framework"
        assert manifest.project_type == "vscode-extension"
        assert manifest.prefix == "ctrl+shift+e"
        assert len(manifest.categories) == 1
        assert manifest.categories[0].name == "Quick Actions"
        assert manifest.categories[0].icon == "$(zap)"

    def test_parse_full_manifest_handles_missing_file(self, tmp_path):
        """Test full manifest parsing with missing file."""
        parser = YAMLManifestParser()
        missing_file = tmp_path / "features.yaml"

        manifest = parser.parse_full_manifest(missing_file)

        assert manifest is None

    def test_parse_full_manifest_handles_invalid_yaml(self, tmp_path):
        """Test full manifest parsing with invalid YAML."""
        parser = YAMLManifestParser()
        yaml_file = tmp_path / "features.yaml"
        yaml_file.write_text("{ invalid yaml")

        manifest = parser.parse_full_manifest(yaml_file)

        assert manifest is None


class TestLLMFeatureAnalyzer:
    """Tests for LLM-based feature analyzer."""

    @pytest.mark.asyncio
    async def test_analyze_codebase_returns_empty_list(self, tmp_path):
        """Test that analyze_codebase returns empty list (placeholder)."""
        analyzer = LLMFeatureAnalyzer()

        features = await analyzer.analyze_codebase(tmp_path)

        assert features == []

    @pytest.mark.asyncio
    async def test_analyze_codebase_with_client(self, tmp_path):
        """Test analyzer with LLM client (placeholder)."""
        mock_client = object()
        analyzer = LLMFeatureAnalyzer(llm_client=mock_client)

        features = await analyzer.analyze_codebase(tmp_path)

        assert features == []
        assert analyzer.llm_client is mock_client


class TestCompositeParser:
    """Tests for composite parser that combines all parsers."""

    def test_initialization(self):
        """Test composite parser initializes all parsers."""
        parser = CompositeParser()

        assert len(parser.parsers) == 3
        assert isinstance(parser.parsers[0], VSCodeCommandParser)
        assert isinstance(parser.parsers[1], PyProjectParser)
        assert isinstance(parser.parsers[2], YAMLManifestParser)
        assert isinstance(parser.llm_analyzer, LLMFeatureAnalyzer)

    def test_discover_features_from_package_json(self, tmp_path):
        """Test discovering features from VSCode package.json."""
        parser = CompositeParser()

        package_file = tmp_path / "package.json"
        package_data = {
            "contributes": {
                "commands": [
                    {"command": "test.command", "title": "Test Command"},
                ],
            },
        }
        package_file.write_text(json.dumps(package_data))

        manifest = parser.discover_features(tmp_path)

        assert len(manifest.all_features()) == 1
        assert manifest.all_features()[0].id == "command"

    def test_discover_features_from_pyproject_toml(self, tmp_path):
        """Test discovering features from pyproject.toml."""
        parser = CompositeParser()

        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_content = """
[project.scripts]
test-cli = "test.cli:main"
"""
        pyproject_file.write_text(pyproject_content)

        manifest = parser.discover_features(tmp_path)

        assert len(manifest.all_features()) == 1
        assert manifest.all_features()[0].id == "test_cli"

    def test_discover_features_prefers_full_manifest(self, tmp_path):
        """Test that full YAML manifest takes precedence."""
        parser = CompositeParser()

        # Create both package.json and features.yaml
        package_file = tmp_path / "package.json"
        package_data = {
            "contributes": {
                "commands": [
                    {"command": "test.command", "title": "Test Command"},
                ],
            },
        }
        package_file.write_text(json.dumps(package_data))

        yaml_file = tmp_path / "features.yaml"
        manifest_data = {
            "project": {
                "name": "custom-project",
                "type": "custom",
            },
            "categories": [
                {
                    "name": "Custom",
                    "features": [
                        {"id": "custom", "name": "Custom Feature", "command": "custom.command"},
                    ],
                },
            ],
        }
        yaml_file.write_text(yaml.dump(manifest_data))

        manifest = parser.discover_features(tmp_path)

        # Should use YAML manifest, not package.json
        assert manifest.project_name == "custom-project"
        assert len(manifest.all_features()) == 1
        assert manifest.all_features()[0].id == "custom"

    def test_discover_features_combines_multiple_sources(self, tmp_path):
        """Test combining features from multiple sources."""
        parser = CompositeParser()

        # Create both package.json and pyproject.toml (no features.yaml)
        package_file = tmp_path / "package.json"
        package_data = {
            "contributes": {
                "commands": [
                    {"command": "test.vscode", "title": "VSCode Command"},
                ],
            },
        }
        package_file.write_text(json.dumps(package_data))

        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_content = """
[project.scripts]
test-cli = "test.cli:main"
"""
        pyproject_file.write_text(pyproject_content)

        manifest = parser.discover_features(tmp_path)

        # Should combine both sources
        assert len(manifest.all_features()) == 2

    def test_discover_features_infers_project_type_vscode(self, tmp_path):
        """Test project type inference for VSCode extension."""
        parser = CompositeParser()

        package_file = tmp_path / "package.json"
        package_file.write_text(json.dumps({}))

        manifest = parser.discover_features(tmp_path)

        assert manifest.project_type == "vscode-extension"

    def test_discover_features_infers_project_type_python(self, tmp_path):
        """Test project type inference for Python CLI."""
        parser = CompositeParser()

        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text("")

        manifest = parser.discover_features(tmp_path)

        assert manifest.project_type == "python-cli"

    def test_discover_features_categorizes_by_frequency(self, tmp_path):
        """Test automatic categorization by frequency tier."""
        parser = CompositeParser()

        package_file = tmp_path / "package.json"
        package_data = {
            "contributes": {
                "commands": [
                    {"command": "test.quick", "title": "Quick: Action"},
                    {"command": "test.view", "title": "View: Dashboard"},
                    {"command": "test.other", "title": "Other Command"},
                ],
            },
        }
        package_file.write_text(json.dumps(package_data))

        manifest = parser.discover_features(tmp_path)

        features_by_tier = {
            FrequencyTier.DAILY: manifest.features_by_tier(FrequencyTier.DAILY),
            FrequencyTier.FREQUENT: manifest.features_by_tier(FrequencyTier.FREQUENT),
            FrequencyTier.ADVANCED: manifest.features_by_tier(FrequencyTier.ADVANCED),
        }

        assert len(features_by_tier[FrequencyTier.DAILY]) == 1
        assert len(features_by_tier[FrequencyTier.FREQUENT]) == 1
        assert len(features_by_tier[FrequencyTier.ADVANCED]) == 1

    def test_get_patterns_vscode(self):
        """Test file pattern retrieval for VSCode parser."""
        parser = CompositeParser()
        vscode_parser = VSCodeCommandParser()

        patterns = parser._get_patterns(vscode_parser)

        assert patterns == ["package.json"]

    def test_get_patterns_pyproject(self):
        """Test file pattern retrieval for PyProject parser."""
        parser = CompositeParser()
        pyproject_parser = PyProjectParser()

        patterns = parser._get_patterns(pyproject_parser)

        assert patterns == ["pyproject.toml"]

    def test_get_patterns_yaml(self):
        """Test file pattern retrieval for YAML parser."""
        parser = CompositeParser()
        yaml_parser = YAMLManifestParser()

        patterns = parser._get_patterns(yaml_parser)

        assert patterns == ["features.yaml", "features.yml"]

    def test_create_manifest_from_features_groups_by_category(self, tmp_path):
        """Test manifest creation groups features into categories."""
        parser = CompositeParser()

        features = [
            Feature(
                id="quick_action",
                name="Quick Action",
                command="test.quick",
                frequency=FrequencyTier.DAILY,
            ),
            Feature(
                id="view_dashboard",
                name="Dashboard",
                command="test.view",
                frequency=FrequencyTier.FREQUENT,
            ),
        ]

        manifest = parser._create_manifest_from_features(tmp_path, features)

        assert len(manifest.categories) >= 1
        assert manifest.project_name == tmp_path.name

    def test_create_manifest_from_features_infers_tier_from_frequency(self, tmp_path):
        """Test category tier inference from feature frequencies."""
        parser = CompositeParser()

        features = [
            Feature(id="a", name="A", command="a", frequency=FrequencyTier.DAILY),
            Feature(id="b", name="B", command="b", frequency=FrequencyTier.DAILY),
            Feature(id="c", name="C", command="c", frequency=FrequencyTier.FREQUENT),
        ]

        manifest = parser._create_manifest_from_features(tmp_path, features)

        # Find the category with most features
        largest_category = max(manifest.categories, key=lambda c: len(c.features))
        # Tier should be the most common tier among features
        assert largest_category.tier in [FrequencyTier.DAILY, FrequencyTier.FREQUENT]
