"""Tests for empathy_llm_toolkit wizards module.

Comprehensive test coverage for wizard base class and configuration.

Created: 2026-01-20
Coverage target: 80%+
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from empathy_llm_toolkit.wizards.base_wizard import BaseWizard, WizardConfig

# =============================================================================
# WizardConfig Tests
# =============================================================================


class TestWizardConfig:
    """Tests for WizardConfig dataclass."""

    def test_default_values(self):
        """Test default configuration values."""
        config = WizardConfig(
            name="test_wizard",
            description="A test wizard",
            domain="general",
        )

        assert config.name == "test_wizard"
        assert config.description == "A test wizard"
        assert config.domain == "general"
        assert config.default_empathy_level == 2
        assert config.enable_security is False
        assert config.pii_patterns == []
        assert config.enable_secrets_detection is False
        assert config.block_on_secrets is True
        assert config.audit_all_access is False
        assert config.retention_days == 180
        assert config.default_classification == "INTERNAL"
        assert config.auto_classify is True
        assert config.enable_memory is False
        assert config.memory_config is None
        assert config.xml_prompts_enabled is True
        assert config.xml_schema_version == "1.0"
        assert config.enforce_xml_response is False

    def test_custom_values(self):
        """Test custom configuration values."""
        config = WizardConfig(
            name="healthcare_wizard",
            description="A healthcare assistant",
            domain="healthcare",
            default_empathy_level=3,
            enable_security=True,
            pii_patterns=["ssn", "mrn"],
            enable_secrets_detection=True,
            block_on_secrets=False,
            audit_all_access=True,
            retention_days=365,
            default_classification="SENSITIVE",
            auto_classify=False,
            enable_memory=True,
            xml_prompts_enabled=False,
            xml_schema_version="2.0",
            enforce_xml_response=True,
        )

        assert config.name == "healthcare_wizard"
        assert config.domain == "healthcare"
        assert config.default_empathy_level == 3
        assert config.enable_security is True
        assert len(config.pii_patterns) == 2
        assert config.block_on_secrets is False
        assert config.audit_all_access is True
        assert config.retention_days == 365
        assert config.default_classification == "SENSITIVE"
        assert config.auto_classify is False
        assert config.enable_memory is True
        assert config.xml_prompts_enabled is False
        assert config.xml_schema_version == "2.0"
        assert config.enforce_xml_response is True


# =============================================================================
# BaseWizard Tests
# =============================================================================


class TestBaseWizard:
    """Tests for BaseWizard class."""

    @pytest.fixture
    def mock_llm(self):
        """Create a mock EmpathyLLM."""
        llm = MagicMock()
        llm.interact = AsyncMock(
            return_value={
                "response": "Test response",
                "empathy_level": 2,
                "metadata": {},
            }
        )
        return llm

    @pytest.fixture
    def valid_config(self):
        """Create a valid wizard configuration."""
        return WizardConfig(
            name="test_wizard",
            description="A test wizard for testing",
            domain="testing",
        )

    def test_init_valid(self, mock_llm, valid_config):
        """Test successful initialization."""
        wizard = BaseWizard(llm=mock_llm, config=valid_config)

        assert wizard.llm == mock_llm
        assert wizard.config == valid_config
        assert wizard.logger is not None

    def test_init_invalid_empathy_level(self, mock_llm):
        """Test initialization with invalid empathy level."""
        config = WizardConfig(
            name="test",
            description="test",
            domain="test",
            default_empathy_level=10,  # Invalid
        )

        with pytest.raises(ValueError, match="Empathy level must be 0-4"):
            BaseWizard(llm=mock_llm, config=config)

    def test_init_invalid_classification(self, mock_llm):
        """Test initialization with invalid classification."""
        config = WizardConfig(
            name="test",
            description="test",
            domain="test",
            default_classification="TOP_SECRET",  # Invalid
        )

        with pytest.raises(ValueError, match="Invalid classification"):
            BaseWizard(llm=mock_llm, config=config)

    @pytest.mark.asyncio
    async def test_process_basic(self, mock_llm, valid_config):
        """Test basic request processing."""
        wizard = BaseWizard(llm=mock_llm, config=valid_config)

        result = await wizard.process(
            user_input="Hello, help me with something",
            user_id="user123",
        )

        assert "response" in result
        assert "wizard" in result
        assert result["wizard"]["name"] == "test_wizard"
        assert result["wizard"]["domain"] == "testing"
        assert result["wizard"]["empathy_level"] == 2  # Default level

        # Verify LLM was called
        mock_llm.interact.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_with_empathy_override(self, mock_llm, valid_config):
        """Test processing with empathy level override."""
        wizard = BaseWizard(llm=mock_llm, config=valid_config)

        result = await wizard.process(
            user_input="Help me",
            user_id="user123",
            empathy_level=4,
        )

        assert result["wizard"]["empathy_level"] == 4

        # Verify LLM was called with force_level=4
        call_kwargs = mock_llm.interact.call_args[1]
        assert call_kwargs["force_level"] == 4

    @pytest.mark.asyncio
    async def test_process_with_session_context(self, mock_llm, valid_config):
        """Test processing with session context."""
        wizard = BaseWizard(llm=mock_llm, config=valid_config)

        session_context = {
            "previous_topic": "debugging",
            "language": "Python",
        }

        await wizard.process(
            user_input="Continue helping me",
            user_id="user123",
            session_context=session_context,
        )

        # Verify context was passed to LLM
        call_kwargs = mock_llm.interact.call_args[1]
        assert "context" in call_kwargs
        assert call_kwargs["context"]["previous_topic"] == "debugging"

    def test_build_system_prompt(self, mock_llm, valid_config):
        """Test system prompt building."""
        wizard = BaseWizard(llm=mock_llm, config=valid_config)

        prompt = wizard._build_system_prompt()

        assert "testing" in prompt  # Domain
        assert "A test wizard for testing" in prompt  # Description
        assert "accurate" in prompt.lower()
        assert "empathetic" in prompt.lower()

    def test_format_context(self, mock_llm, valid_config):
        """Test context formatting."""
        wizard = BaseWizard(llm=mock_llm, config=valid_config)

        context = {"topic": "debugging", "file": "test.py"}
        formatted = wizard._format_context(context)

        assert "Context:" in formatted
        assert "topic: debugging" in formatted
        assert "file: test.py" in formatted

    def test_is_xml_enabled(self, mock_llm, valid_config):
        """Test XML enabled check."""
        wizard = BaseWizard(llm=mock_llm, config=valid_config)

        # Default is enabled
        assert wizard._is_xml_enabled() is True

        # With disabled
        config_disabled = WizardConfig(
            name="test",
            description="test",
            domain="test",
            xml_prompts_enabled=False,
        )
        wizard_disabled = BaseWizard(llm=mock_llm, config=config_disabled)
        assert wizard_disabled._is_xml_enabled() is False

    def test_render_xml_prompt(self, mock_llm, valid_config):
        """Test XML prompt rendering."""
        wizard = BaseWizard(llm=mock_llm, config=valid_config)

        prompt = wizard._render_xml_prompt(
            role="code reviewer",
            goal="Review the code for issues",
            instructions=["Check for bugs", "Verify style"],
            constraints=["Be constructive", "Follow PEP 8"],
            input_type="code",
            input_payload="def foo(): pass",
        )

        assert '<task role="code reviewer"' in prompt
        assert "<goal>Review the code for issues</goal>" in prompt
        assert "<instructions>" in prompt
        assert "1. Check for bugs" in prompt
        assert "2. Verify style" in prompt
        assert "<constraints>" in prompt
        assert "- Be constructive" in prompt
        assert '<input type="code">' in prompt
        assert "def foo(): pass" in prompt
        assert "</task>" in prompt

    def test_render_xml_prompt_with_extra_context(self, mock_llm, valid_config):
        """Test XML prompt rendering with extra context."""
        wizard = BaseWizard(llm=mock_llm, config=valid_config)

        prompt = wizard._render_xml_prompt(
            role="assistant",
            goal="Help user",
            instructions=["Step 1"],
            constraints=["Be helpful"],
            input_type="query",
            input_payload="Test query",
            extra={"language": "Python", "framework": "Django"},
        )

        assert "<context>" in prompt
        assert "<language>Python</language>" in prompt
        assert "<framework>Django</framework>" in prompt

    def test_render_xml_prompt_disabled(self, mock_llm):
        """Test XML prompt falls back to plain text when disabled."""
        config = WizardConfig(
            name="test",
            description="test",
            domain="test",
            xml_prompts_enabled=False,
        )
        wizard = BaseWizard(llm=mock_llm, config=config)

        prompt = wizard._render_xml_prompt(
            role="assistant",
            goal="Help user",
            instructions=["Step 1"],
            constraints=["Be helpful"],
            input_type="query",
            input_payload="Test query",
        )

        # Should be plain text, not XML
        assert "<task" not in prompt
        assert "Role: assistant" in prompt
        assert "Goal: Help user" in prompt

    def test_render_plain_prompt(self, mock_llm, valid_config):
        """Test plain text prompt rendering."""
        wizard = BaseWizard(llm=mock_llm, config=valid_config)

        prompt = wizard._render_plain_prompt(
            role="code reviewer",
            goal="Review the code",
            instructions=["Check bugs", "Check style"],
            constraints=["Be constructive"],
            input_payload="def foo(): pass",
        )

        assert "Role: code reviewer" in prompt
        assert "Goal: Review the code" in prompt
        assert "Instructions:" in prompt
        assert "1. Check bugs" in prompt
        assert "Guidelines:" in prompt
        assert "- Be constructive" in prompt
        assert "Input:" in prompt
        assert "def foo(): pass" in prompt

    def test_parse_xml_response_disabled(self, mock_llm, valid_config):
        """Test XML response parsing when enforcement is disabled."""
        wizard = BaseWizard(llm=mock_llm, config=valid_config)

        response = "<summary>Test summary</summary>"
        result = wizard._parse_xml_response(response)

        assert result["xml_parsed"] is False
        assert result["content"] == response

    def test_parse_xml_response_enabled(self, mock_llm):
        """Test XML response parsing when enforcement is enabled."""
        config = WizardConfig(
            name="test",
            description="test",
            domain="test",
            enforce_xml_response=True,
        )
        wizard = BaseWizard(llm=mock_llm, config=config)

        response = """
        <summary>This is a test summary</summary>
        <recommendation>Do this first</recommendation>
        <recommendation>Then do this</recommendation>
        <finding>Found issue A</finding>
        <finding>Found issue B</finding>
        """

        result = wizard._parse_xml_response(response)

        assert result["xml_parsed"] is True
        assert result["summary"] == "This is a test summary"
        assert len(result["recommendations"]) == 2
        assert "Do this first" in result["recommendations"]
        assert len(result["findings"]) == 2
        assert "Found issue A" in result["findings"]
        assert result["content"] == response

    def test_parse_xml_response_partial(self, mock_llm):
        """Test XML response parsing with partial tags."""
        config = WizardConfig(
            name="test",
            description="test",
            domain="test",
            enforce_xml_response=True,
        )
        wizard = BaseWizard(llm=mock_llm, config=config)

        # Only has summary, no recommendations
        response = "<summary>Just a summary</summary>"
        result = wizard._parse_xml_response(response)

        assert result["xml_parsed"] is True
        assert result["summary"] == "Just a summary"
        assert "recommendations" not in result
        assert "findings" not in result

    def test_get_config(self, mock_llm, valid_config):
        """Test getting wizard configuration."""
        wizard = BaseWizard(llm=mock_llm, config=valid_config)

        retrieved_config = wizard.get_config()
        assert retrieved_config == valid_config

    def test_get_name(self, mock_llm, valid_config):
        """Test getting wizard name."""
        wizard = BaseWizard(llm=mock_llm, config=valid_config)

        assert wizard.get_name() == "test_wizard"


# =============================================================================
# Import Tests
# =============================================================================


class TestWizardImports:
    """Tests for wizard module imports."""

    def test_base_imports(self):
        """Test that base classes are importable."""
        from empathy_llm_toolkit.wizards import BaseWizard, WizardConfig

        assert BaseWizard is not None
        assert WizardConfig is not None

    def test_customer_support_wizard_import(self):
        """Test that CustomerSupportWizard is importable."""
        from empathy_llm_toolkit.wizards import CustomerSupportWizard

        assert CustomerSupportWizard is not None

    def test_deprecated_wizards_import(self):
        """Test that deprecated wizards are still importable."""
        # These should work but may show deprecation warnings
        from empathy_llm_toolkit.wizards import HealthcareWizard, TechnologyWizard

        assert HealthcareWizard is not None
        assert TechnologyWizard is not None


# =============================================================================
# Edge Cases
# =============================================================================


class TestBaseWizardEdgeCases:
    """Edge case tests for BaseWizard."""

    @pytest.fixture
    def mock_llm(self):
        """Create a mock EmpathyLLM."""
        llm = MagicMock()
        llm.interact = AsyncMock(return_value={"response": "test", "metadata": {}})
        return llm

    def test_empathy_level_boundary_zero(self, mock_llm):
        """Test empathy level at boundary (0)."""
        config = WizardConfig(
            name="test",
            description="test",
            domain="test",
            default_empathy_level=0,  # Minimum valid
        )

        wizard = BaseWizard(llm=mock_llm, config=config)
        assert wizard.config.default_empathy_level == 0

    def test_empathy_level_boundary_four(self, mock_llm):
        """Test empathy level at boundary (4)."""
        config = WizardConfig(
            name="test",
            description="test",
            domain="test",
            default_empathy_level=4,  # Maximum valid
        )

        wizard = BaseWizard(llm=mock_llm, config=config)
        assert wizard.config.default_empathy_level == 4

    def test_all_valid_classifications(self, mock_llm):
        """Test all valid classification values."""
        for classification in ["PUBLIC", "INTERNAL", "SENSITIVE"]:
            config = WizardConfig(
                name="test",
                description="test",
                domain="test",
                default_classification=classification,
            )

            wizard = BaseWizard(llm=mock_llm, config=config)
            assert wizard.config.default_classification == classification

    def test_empty_context_formatting(self, mock_llm):
        """Test formatting empty context."""
        config = WizardConfig(name="test", description="test", domain="test")
        wizard = BaseWizard(llm=mock_llm, config=config)

        formatted = wizard._format_context({})
        assert "Context:" in formatted

    def test_render_xml_prompt_empty_lists(self, mock_llm):
        """Test XML prompt with empty instructions and constraints."""
        config = WizardConfig(name="test", description="test", domain="test")
        wizard = BaseWizard(llm=mock_llm, config=config)

        prompt = wizard._render_xml_prompt(
            role="assistant",
            goal="Help",
            instructions=[],
            constraints=[],
            input_type="text",
            input_payload="test",
        )

        # Should still be valid XML
        assert "<task" in prompt
        assert "<goal>Help</goal>" in prompt
        assert "<instructions>" not in prompt  # Empty list should be skipped
        assert "<constraints>" not in prompt

    @pytest.mark.asyncio
    async def test_process_none_session_context(self, mock_llm):
        """Test processing with None session context."""
        config = WizardConfig(name="test", description="test", domain="test")
        wizard = BaseWizard(llm=mock_llm, config=config)

        # Should not raise error
        result = await wizard.process(
            user_input="test",
            user_id="user123",
            session_context=None,
        )

        assert result is not None
