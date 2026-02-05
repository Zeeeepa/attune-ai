"""Unit tests for DependencyManager.

Tests dependency detection, user prompts, and installation management.
"""

import importlib.util
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from attune.cache.dependency_manager import DependencyManager

# Check if cache dependencies are available
_cache_deps_available = (
    importlib.util.find_spec("sentence_transformers") is not None
    and importlib.util.find_spec("torch") is not None
)


class TestDependencyManager:
    """Test suite for DependencyManager."""

    def test_init_creates_config_path(self):
        """Test initialization with default config path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yml"
            manager = DependencyManager(config_path=config_path)

            assert manager.config_path == config_path

    @pytest.mark.skipif(
        not _cache_deps_available,
        reason="sentence-transformers/torch not installed (optional dependency)",
    )
    def test_is_cache_installed_true(self):
        """Test detection when sentence-transformers is installed."""
        manager = DependencyManager()

        # Should be True when sentence-transformers is installed
        assert manager.is_cache_installed() is True

    @patch("attune.cache.dependency_manager.DependencyManager.is_cache_installed")
    def test_is_cache_installed_false(self, mock_check):
        """Test detection when sentence-transformers is not installed."""
        mock_check.return_value = False
        manager = DependencyManager()

        assert manager.is_cache_installed() is False

    def test_should_prompt_when_not_installed(self):
        """Test that we prompt when cache not installed and not declined."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yml"
            manager = DependencyManager(config_path=config_path)

            # Mock cache not installed
            with patch.object(manager, "is_cache_installed", return_value=False):
                assert manager.should_prompt_cache_install() is True

    @pytest.mark.skipif(
        not _cache_deps_available,
        reason="sentence-transformers/torch not installed (optional dependency)",
    )
    def test_should_not_prompt_when_already_installed(self):
        """Test that we don't prompt when cache already installed."""
        manager = DependencyManager()

        # Cache is installed - should not prompt
        assert manager.should_prompt_cache_install() is False

    def test_should_not_prompt_when_declined(self):
        """Test that we don't prompt when user previously declined."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yml"

            # Create config with declined flag
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, "w") as f:
                yaml.safe_dump({"cache": {"install_declined": True}}, f)

            manager = DependencyManager(config_path=config_path)

            # Mock cache not installed
            with patch.object(manager, "is_cache_installed", return_value=False):
                assert manager.should_prompt_cache_install() is False

    def test_should_not_prompt_when_already_shown(self):
        """Test that we don't prompt when already shown."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yml"

            # Create config with prompt_shown flag
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, "w") as f:
                yaml.safe_dump({"cache": {"prompt_shown": True}}, f)

            manager = DependencyManager(config_path=config_path)

            # Mock cache not installed
            with patch.object(manager, "is_cache_installed", return_value=False):
                assert manager.should_prompt_cache_install() is False

    def test_should_not_prompt_when_disabled(self):
        """Test that we don't prompt when prompts disabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yml"

            # Create config with prompts disabled
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, "w") as f:
                yaml.safe_dump({"cache": {"prompt_enabled": False}}, f)

            manager = DependencyManager(config_path=config_path)

            # Mock cache not installed
            with patch.object(manager, "is_cache_installed", return_value=False):
                assert manager.should_prompt_cache_install() is False

    @patch("builtins.input")
    @patch("subprocess.check_call")
    def test_prompt_cache_install_accept(self, mock_subprocess, mock_input):
        """Test accepting cache installation prompt."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yml"
            manager = DependencyManager(config_path=config_path)

            # User accepts
            mock_input.return_value = "y"

            result = manager.prompt_cache_install()

            assert result is True
            mock_subprocess.assert_called_once()

            # Config should be updated
            assert manager.config["cache"]["enabled"] is True
            assert manager.config["cache"]["install_declined"] is False

    @patch("builtins.input")
    def test_prompt_cache_install_decline(self, mock_input):
        """Test declining cache installation prompt."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yml"
            manager = DependencyManager(config_path=config_path)

            # User declines
            mock_input.return_value = "n"

            result = manager.prompt_cache_install()

            assert result is False

            # Config should be updated
            assert manager.config["cache"]["install_declined"] is True
            assert manager.config["cache"]["prompt_shown"] is True

    @patch("builtins.input")
    def test_prompt_cache_install_keyboard_interrupt(self, mock_input):
        """Test handling keyboard interrupt during prompt."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yml"
            manager = DependencyManager(config_path=config_path)

            # Simulate keyboard interrupt
            mock_input.side_effect = KeyboardInterrupt()

            result = manager.prompt_cache_install()

            assert result is False

    @patch("subprocess.check_call")
    def test_install_cache_dependencies_success(self, mock_subprocess):
        """Test successful dependency installation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yml"
            manager = DependencyManager(config_path=config_path)

            result = manager.install_cache_dependencies()

            assert result is True
            mock_subprocess.assert_called_once()

            # Verify packages were requested
            call_args = mock_subprocess.call_args[0][0]
            assert "sentence-transformers>=2.0.0" in call_args
            assert "torch>=2.0.0" in call_args
            assert "numpy>=1.24.0" in call_args

    @patch("subprocess.check_call")
    def test_install_cache_dependencies_failure(self, mock_subprocess):
        """Test handling installation failure."""
        import subprocess

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yml"
            manager = DependencyManager(config_path=config_path)

            # Simulate installation failure
            mock_subprocess.side_effect = subprocess.CalledProcessError(1, "pip")

            result = manager.install_cache_dependencies()

            assert result is False

    def test_disable_prompts(self):
        """Test disabling cache prompts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yml"
            manager = DependencyManager(config_path=config_path)

            manager.disable_prompts()

            assert manager.config["cache"]["prompt_enabled"] is False

    def test_enable_prompts(self):
        """Test re-enabling cache prompts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yml"
            manager = DependencyManager(config_path=config_path)

            # Disable first
            manager.disable_prompts()
            assert manager.config["cache"]["prompt_enabled"] is False

            # Re-enable
            manager.enable_prompts()
            assert manager.config["cache"]["prompt_enabled"] is True
            assert manager.config["cache"]["prompt_shown"] is False
            assert manager.config["cache"]["install_declined"] is False

    def test_get_config(self):
        """Test getting cache configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yml"

            # Create config
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, "w") as f:
                yaml.safe_dump({"cache": {"enabled": True, "custom": "value"}}, f)

            manager = DependencyManager(config_path=config_path)
            cache_config = manager.get_config()

            assert cache_config["enabled"] is True
            assert cache_config["custom"] == "value"

    def test_set_config(self):
        """Test setting cache configuration values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yml"
            manager = DependencyManager(config_path=config_path)

            manager.set_config("test_key", "test_value")

            assert manager.config["cache"]["test_key"] == "test_value"

            # Verify it's saved to disk
            manager2 = DependencyManager(config_path=config_path)
            assert manager2.config["cache"]["test_key"] == "test_value"
