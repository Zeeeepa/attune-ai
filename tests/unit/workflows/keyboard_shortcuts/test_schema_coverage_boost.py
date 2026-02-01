"""Unit tests for keyboard shortcuts schema module.

This test suite provides comprehensive coverage for the schema definitions
used in keyboard shortcut generation, including enums, dataclasses, and
validation logic.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import pytest

from attune.workflows.keyboard_shortcuts.schema import (
    KEYBOARD_LAYOUTS,
    RESERVED_KEYS,
    Category,
    Feature,
    FeatureManifest,
    FingerPosition,
    FrequencyTier,
    GeneratedShortcuts,
    HandPosition,
    KeyboardLayout,
    LayoutConfig,
    LayoutShortcuts,
    RowPosition,
    ScaleAssignments,
    ShortcutAssignment,
)


@pytest.mark.unit
class TestFrequencyTier:
    """Test suite for FrequencyTier enum."""

    def test_enum_values_exist(self):
        """Test that all frequency tier values are defined."""
        assert FrequencyTier.DAILY == "daily"
        assert FrequencyTier.FREQUENT == "frequent"
        assert FrequencyTier.ADVANCED == "advanced"

    def test_enum_is_string_enum(self):
        """Test that FrequencyTier is a string enum."""
        assert isinstance(FrequencyTier.DAILY, str)
        assert isinstance(FrequencyTier.FREQUENT, str)

    def test_enum_can_be_compared_to_string(self):
        """Test that enum values can be compared to strings."""
        assert FrequencyTier.DAILY == "daily"
        assert FrequencyTier.FREQUENT != "daily"


@pytest.mark.unit
class TestKeyboardLayout:
    """Test suite for KeyboardLayout enum."""

    def test_enum_values_exist(self):
        """Test that all keyboard layout values are defined."""
        assert KeyboardLayout.QWERTY == "qwerty"
        assert KeyboardLayout.DVORAK == "dvorak"
        assert KeyboardLayout.COLEMAK == "colemak"

    def test_enum_is_string_enum(self):
        """Test that KeyboardLayout is a string enum."""
        assert isinstance(KeyboardLayout.QWERTY, str)

    def test_all_layouts_in_keyboard_layouts_constant(self):
        """Test that all enum values have entries in KEYBOARD_LAYOUTS."""
        for layout in KeyboardLayout:
            assert layout in KEYBOARD_LAYOUTS


@pytest.mark.unit
class TestHandPosition:
    """Test suite for HandPosition enum."""

    def test_enum_values_exist(self):
        """Test that hand position values are defined."""
        assert HandPosition.LEFT == "left"
        assert HandPosition.RIGHT == "right"

    def test_enum_is_string_enum(self):
        """Test that HandPosition is a string enum."""
        assert isinstance(HandPosition.LEFT, str)


@pytest.mark.unit
class TestFingerPosition:
    """Test suite for FingerPosition enum."""

    def test_enum_values_exist(self):
        """Test that all finger position values are defined."""
        assert FingerPosition.PINKY == "pinky"
        assert FingerPosition.RING == "ring"
        assert FingerPosition.MIDDLE == "middle"
        assert FingerPosition.INDEX == "index"
        assert FingerPosition.THUMB == "thumb"

    def test_enum_is_string_enum(self):
        """Test that FingerPosition is a string enum."""
        assert isinstance(FingerPosition.INDEX, str)


@pytest.mark.unit
class TestRowPosition:
    """Test suite for RowPosition enum."""

    def test_enum_values_exist(self):
        """Test that all row position values are defined."""
        assert RowPosition.TOP == "top"
        assert RowPosition.HOME == "home"
        assert RowPosition.BOTTOM == "bottom"

    def test_enum_is_string_enum(self):
        """Test that RowPosition is a string enum."""
        assert isinstance(RowPosition.HOME, str)


@pytest.mark.unit
class TestFeature:
    """Test suite for Feature dataclass."""

    def test_create_feature_with_required_fields(self):
        """Test creating feature with only required fields."""
        feature = Feature(id="test", name="Test Feature")

        assert feature.id == "test"
        assert feature.name == "Test Feature"
        assert feature.description == ""
        assert feature.command == ""
        assert feature.cli_alias == ""
        assert feature.frequency == FrequencyTier.FREQUENT
        assert feature.context == "global"
        assert feature.icon == "$(symbol-misc)"

    def test_create_feature_with_all_fields(self):
        """Test creating feature with all fields specified."""
        feature = Feature(
            id="morning",
            name="Morning Briefing",
            description="Start your day with an AI briefing",
            command="empathy.morning",
            cli_alias="empathy morning",
            frequency=FrequencyTier.DAILY,
            context="global",
            icon="$(sun)",
        )

        assert feature.id == "morning"
        assert feature.name == "Morning Briefing"
        assert feature.description == "Start your day with an AI briefing"
        assert feature.command == "empathy.morning"
        assert feature.cli_alias == "empathy morning"
        assert feature.frequency == FrequencyTier.DAILY
        assert feature.context == "global"
        assert feature.icon == "$(sun)"

    def test_feature_context_can_be_editor(self):
        """Test that feature context can be set to editor."""
        feature = Feature(id="format", name="Format Code", context="editor")
        assert feature.context == "editor"

    def test_feature_context_can_be_explorer(self):
        """Test that feature context can be set to explorer."""
        feature = Feature(id="reveal", name="Reveal in Explorer", context="explorer")
        assert feature.context == "explorer"


@pytest.mark.unit
class TestCategory:
    """Test suite for Category dataclass."""

    def test_create_category_with_required_fields(self):
        """Test creating category with only required fields."""
        category = Category(name="Development")

        assert category.name == "Development"
        assert category.icon == "$(folder)"
        assert category.tier == FrequencyTier.FREQUENT
        assert category.features == []

    def test_create_category_with_features(self):
        """Test creating category with features list."""
        features = [
            Feature(id="test1", name="Test 1"),
            Feature(id="test2", name="Test 2"),
        ]
        category = Category(name="Testing", features=features)

        assert category.name == "Testing"
        assert len(category.features) == 2
        assert category.features[0].id == "test1"

    def test_create_category_with_custom_icon_and_tier(self):
        """Test creating category with custom icon and tier."""
        category = Category(
            name="Daily Tasks",
            icon="$(calendar)",
            tier=FrequencyTier.DAILY,
        )

        assert category.icon == "$(calendar)"
        assert category.tier == FrequencyTier.DAILY


@pytest.mark.unit
class TestLayoutConfig:
    """Test suite for LayoutConfig dataclass."""

    def test_create_qwerty_layout_sets_defaults(self):
        """Test that QWERTY layout sets home row and mnemonic."""
        config = LayoutConfig(layout=KeyboardLayout.QWERTY)

        assert config.layout == KeyboardLayout.QWERTY
        assert config.home_row == ["a", "s", "d", "f"]
        assert config.mnemonic_base == "natural English letters"

    def test_create_dvorak_layout_sets_defaults(self):
        """Test that DVORAK layout sets home row and mnemonic."""
        config = LayoutConfig(layout=KeyboardLayout.DVORAK)

        assert config.layout == KeyboardLayout.DVORAK
        assert config.home_row == ["a", "o", "e", "u"]
        assert config.mnemonic_base == "vowel-centric patterns"

    def test_create_colemak_layout_sets_defaults(self):
        """Test that COLEMAK layout sets home row and mnemonic."""
        config = LayoutConfig(layout=KeyboardLayout.COLEMAK)

        assert config.layout == KeyboardLayout.COLEMAK
        assert config.home_row == ["a", "r", "s", "t"]
        assert config.mnemonic_base == "ARST patterns"

    def test_create_layout_with_explicit_home_row(self):
        """Test that explicit home row overrides defaults."""
        config = LayoutConfig(
            layout=KeyboardLayout.QWERTY,
            home_row=["x", "y", "z"],
        )

        assert config.home_row == ["x", "y", "z"]
        # mnemonic_base should not be set when home_row is provided
        assert config.mnemonic_base == ""

    def test_create_layout_with_explicit_home_row_and_mnemonic(self):
        """Test that explicit home row and mnemonic are both preserved."""
        config = LayoutConfig(
            layout=KeyboardLayout.QWERTY,
            home_row=["x", "y", "z"],
            mnemonic_base="custom mnemonics",
        )

        assert config.home_row == ["x", "y", "z"]
        assert config.mnemonic_base == "custom mnemonics"


@pytest.mark.unit
class TestShortcutAssignment:
    """Test suite for ShortcutAssignment dataclass."""

    def test_create_assignment_with_required_fields(self):
        """Test creating shortcut assignment with required fields."""
        assignment = ShortcutAssignment(
            feature_id="morning",
            key="m",
            mnemonic="M = Morning",
        )

        assert assignment.feature_id == "morning"
        assert assignment.key == "m"
        assert assignment.mnemonic == "M = Morning"
        assert assignment.hand == HandPosition.LEFT
        assert assignment.finger == FingerPosition.INDEX
        assert assignment.row == RowPosition.HOME
        assert assignment.layout == KeyboardLayout.QWERTY

    def test_create_assignment_with_all_fields(self):
        """Test creating shortcut assignment with all fields."""
        assignment = ShortcutAssignment(
            feature_id="ship",
            key="s",
            mnemonic="S = Ship",
            hand=HandPosition.LEFT,
            finger=FingerPosition.RING,
            row=RowPosition.HOME,
            layout=KeyboardLayout.DVORAK,
        )

        assert assignment.feature_id == "ship"
        assert assignment.key == "s"
        assert assignment.hand == HandPosition.LEFT
        assert assignment.finger == FingerPosition.RING
        assert assignment.row == RowPosition.HOME
        assert assignment.layout == KeyboardLayout.DVORAK


@pytest.mark.unit
class TestScaleAssignments:
    """Test suite for ScaleAssignments dataclass."""

    def test_create_scale_assignments_with_defaults(self):
        """Test creating scale assignments with default empty lists."""
        scale = ScaleAssignments()

        assert scale.daily == []
        assert scale.frequent == []
        assert scale.advanced == []

    def test_create_scale_assignments_with_keys(self):
        """Test creating scale assignments with key lists."""
        scale = ScaleAssignments(
            daily=["m", "s", "f", "d"],
            frequent=["c", "r", "t", "p"],
            advanced=["b", "w", "l", "n"],
        )

        assert scale.daily == ["m", "s", "f", "d"]
        assert scale.frequent == ["c", "r", "t", "p"]
        assert scale.advanced == ["b", "w", "l", "n"]


@pytest.mark.unit
class TestLayoutShortcuts:
    """Test suite for LayoutShortcuts dataclass."""

    def test_create_layout_shortcuts_with_defaults(self):
        """Test creating layout shortcuts with default values."""
        layout = LayoutShortcuts(layout=KeyboardLayout.QWERTY)

        assert layout.layout == KeyboardLayout.QWERTY
        assert layout.shortcuts == []
        assert isinstance(layout.scale_assignments, ScaleAssignments)
        assert layout.phrase_mnemonic == ""

    def test_create_layout_shortcuts_with_all_fields(self):
        """Test creating layout shortcuts with all fields."""
        shortcuts = [
            ShortcutAssignment(feature_id="morning", key="m", mnemonic="M = Morning"),
            ShortcutAssignment(feature_id="ship", key="s", mnemonic="S = Ship"),
        ]
        scale = ScaleAssignments(daily=["m", "s"])

        layout = LayoutShortcuts(
            layout=KeyboardLayout.QWERTY,
            shortcuts=shortcuts,
            scale_assignments=scale,
            phrase_mnemonic="My Ship",
        )

        assert len(layout.shortcuts) == 2
        assert layout.scale_assignments.daily == ["m", "s"]
        assert layout.phrase_mnemonic == "My Ship"


@pytest.mark.unit
class TestFeatureManifest:
    """Test suite for FeatureManifest dataclass."""

    def test_create_manifest_with_required_fields(self):
        """Test creating manifest with only required fields."""
        manifest = FeatureManifest(project_name="Test Project")

        assert manifest.project_name == "Test Project"
        assert manifest.project_type == "custom"
        assert manifest.prefix == "ctrl+shift+e"
        assert manifest.categories == []
        # __post_init__ should create default layouts
        assert len(manifest.layouts) == 3
        assert any(l.layout == KeyboardLayout.QWERTY for l in manifest.layouts)
        assert any(l.layout == KeyboardLayout.DVORAK for l in manifest.layouts)
        assert any(l.layout == KeyboardLayout.COLEMAK for l in manifest.layouts)

    def test_create_manifest_with_vscode_project_type(self):
        """Test creating manifest for VSCode extension."""
        manifest = FeatureManifest(
            project_name="My Extension",
            project_type="vscode-extension",
        )

        assert manifest.project_type == "vscode-extension"

    def test_create_manifest_with_python_cli_project_type(self):
        """Test creating manifest for Python CLI."""
        manifest = FeatureManifest(
            project_name="My CLI",
            project_type="python-cli",
        )

        assert manifest.project_type == "python-cli"

    def test_create_manifest_with_custom_prefix(self):
        """Test creating manifest with custom prefix."""
        manifest = FeatureManifest(
            project_name="Test",
            prefix="ctrl+alt+k",
        )

        assert manifest.prefix == "ctrl+alt+k"

    def test_create_manifest_with_explicit_layouts(self):
        """Test that explicit layouts override defaults."""
        layouts = [LayoutConfig(layout=KeyboardLayout.QWERTY)]
        manifest = FeatureManifest(
            project_name="Test",
            layouts=layouts,
        )

        # Should NOT create default layouts since layouts were provided
        assert len(manifest.layouts) == 1
        assert manifest.layouts[0].layout == KeyboardLayout.QWERTY

    def test_all_features_returns_empty_for_no_categories(self):
        """Test all_features returns empty list when no categories."""
        manifest = FeatureManifest(project_name="Test")

        assert manifest.all_features() == []

    def test_all_features_returns_all_features_across_categories(self):
        """Test all_features aggregates features from all categories."""
        categories = [
            Category(
                name="Cat1",
                features=[
                    Feature(id="f1", name="Feature 1"),
                    Feature(id="f2", name="Feature 2"),
                ],
            ),
            Category(
                name="Cat2",
                features=[
                    Feature(id="f3", name="Feature 3"),
                ],
            ),
        ]
        manifest = FeatureManifest(project_name="Test", categories=categories)

        all_features = manifest.all_features()
        assert len(all_features) == 3
        assert all_features[0].id == "f1"
        assert all_features[1].id == "f2"
        assert all_features[2].id == "f3"

    def test_features_by_tier_filters_daily(self):
        """Test features_by_tier filters for DAILY tier."""
        categories = [
            Category(
                name="Cat1",
                features=[
                    Feature(id="f1", name="F1", frequency=FrequencyTier.DAILY),
                    Feature(id="f2", name="F2", frequency=FrequencyTier.FREQUENT),
                    Feature(id="f3", name="F3", frequency=FrequencyTier.DAILY),
                ],
            ),
        ]
        manifest = FeatureManifest(project_name="Test", categories=categories)

        daily = manifest.features_by_tier(FrequencyTier.DAILY)
        assert len(daily) == 2
        assert all(f.frequency == FrequencyTier.DAILY for f in daily)

    def test_features_by_tier_filters_frequent(self):
        """Test features_by_tier filters for FREQUENT tier."""
        categories = [
            Category(
                name="Cat1",
                features=[
                    Feature(id="f1", name="F1", frequency=FrequencyTier.DAILY),
                    Feature(id="f2", name="F2", frequency=FrequencyTier.FREQUENT),
                    Feature(id="f3", name="F3", frequency=FrequencyTier.ADVANCED),
                ],
            ),
        ]
        manifest = FeatureManifest(project_name="Test", categories=categories)

        frequent = manifest.features_by_tier(FrequencyTier.FREQUENT)
        assert len(frequent) == 1
        assert frequent[0].id == "f2"

    def test_features_by_tier_filters_advanced(self):
        """Test features_by_tier filters for ADVANCED tier."""
        categories = [
            Category(
                name="Cat1",
                features=[
                    Feature(id="f1", name="F1", frequency=FrequencyTier.ADVANCED),
                    Feature(id="f2", name="F2", frequency=FrequencyTier.FREQUENT),
                ],
            ),
        ]
        manifest = FeatureManifest(project_name="Test", categories=categories)

        advanced = manifest.features_by_tier(FrequencyTier.ADVANCED)
        assert len(advanced) == 1
        assert advanced[0].id == "f1"

    def test_features_by_tier_returns_empty_for_no_matches(self):
        """Test features_by_tier returns empty list when no matches."""
        categories = [
            Category(
                name="Cat1",
                features=[
                    Feature(id="f1", name="F1", frequency=FrequencyTier.FREQUENT),
                ],
            ),
        ]
        manifest = FeatureManifest(project_name="Test", categories=categories)

        daily = manifest.features_by_tier(FrequencyTier.DAILY)
        assert daily == []


@pytest.mark.unit
class TestGeneratedShortcuts:
    """Test suite for GeneratedShortcuts dataclass."""

    def test_create_generated_shortcuts_with_defaults(self):
        """Test creating generated shortcuts with default values."""
        manifest = FeatureManifest(project_name="Test")
        result = GeneratedShortcuts(manifest=manifest)

        assert result.manifest == manifest
        assert result.layouts == {}
        assert result.validation_passed is True
        assert result.conflicts == []
        assert result.warnings == []

    def test_create_generated_shortcuts_with_layouts(self):
        """Test creating generated shortcuts with layout data."""
        manifest = FeatureManifest(project_name="Test")
        qwerty_shortcuts = LayoutShortcuts(layout=KeyboardLayout.QWERTY)
        layouts = {KeyboardLayout.QWERTY: qwerty_shortcuts}

        result = GeneratedShortcuts(manifest=manifest, layouts=layouts)

        assert KeyboardLayout.QWERTY in result.layouts
        assert result.layouts[KeyboardLayout.QWERTY] == qwerty_shortcuts

    def test_create_generated_shortcuts_with_validation_failure(self):
        """Test creating generated shortcuts with validation failure."""
        manifest = FeatureManifest(project_name="Test")
        result = GeneratedShortcuts(
            manifest=manifest,
            validation_passed=False,
            conflicts=["Duplicate key: m"],
            warnings=["Reserved key used: w"],
        )

        assert result.validation_passed is False
        assert len(result.conflicts) == 1
        assert len(result.warnings) == 1
        assert "Duplicate key: m" in result.conflicts
        assert "Reserved key used: w" in result.warnings


@pytest.mark.unit
class TestKeyboardLayoutsConstant:
    """Test suite for KEYBOARD_LAYOUTS constant."""

    def test_keyboard_layouts_has_all_enum_values(self):
        """Test that KEYBOARD_LAYOUTS has entries for all layouts."""
        for layout in KeyboardLayout:
            assert layout in KEYBOARD_LAYOUTS

    def test_keyboard_layouts_has_required_keys(self):
        """Test that each layout has top_row, home_row, bottom_row."""
        for layout_data in KEYBOARD_LAYOUTS.values():
            assert "top_row" in layout_data
            assert "home_row" in layout_data
            assert "bottom_row" in layout_data

    def test_qwerty_layout_has_correct_keys(self):
        """Test that QWERTY layout has expected keys."""
        qwerty = KEYBOARD_LAYOUTS[KeyboardLayout.QWERTY]
        assert qwerty["home_row"] == list("asdfghjkl")
        assert "q" in qwerty["top_row"]
        assert "z" in qwerty["bottom_row"]

    def test_dvorak_layout_has_correct_keys(self):
        """Test that DVORAK layout has expected keys."""
        dvorak = KEYBOARD_LAYOUTS[KeyboardLayout.DVORAK]
        assert "a" in dvorak["home_row"]
        assert "o" in dvorak["home_row"]
        assert "e" in dvorak["home_row"]

    def test_colemak_layout_has_correct_keys(self):
        """Test that COLEMAK layout has expected keys."""
        colemak = KEYBOARD_LAYOUTS[KeyboardLayout.COLEMAK]
        assert "a" in colemak["home_row"]
        assert "r" in colemak["home_row"]
        assert "s" in colemak["home_row"]
        assert "t" in colemak["home_row"]


@pytest.mark.unit
class TestReservedKeysConstant:
    """Test suite for RESERVED_KEYS constant."""

    def test_reserved_keys_has_global_and_ide(self):
        """Test that RESERVED_KEYS has global and ide entries."""
        assert "global" in RESERVED_KEYS
        assert "ide" in RESERVED_KEYS

    def test_reserved_keys_global_contains_os_keys(self):
        """Test that global reserved keys include common OS shortcuts."""
        global_keys = RESERVED_KEYS["global"]
        assert "q" in global_keys  # Quit
        assert "w" in global_keys  # Close window

    def test_reserved_keys_ide_contains_editor_keys(self):
        """Test that IDE reserved keys include common editor shortcuts."""
        ide_keys = RESERVED_KEYS["ide"]
        assert "n" in ide_keys  # New
        assert "o" in ide_keys  # Open
        assert "s" in ide_keys  # Save
        assert "z" in ide_keys  # Undo
