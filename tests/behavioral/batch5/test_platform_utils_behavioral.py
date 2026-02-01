"""Behavioral tests for platform_utils.py - Cross-platform utilities.

Tests Given/When/Then pattern for platform detection and utilities.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

import asyncio
from pathlib import Path
from unittest.mock import patch

from attune.platform_utils import (
    PLATFORM_INFO,
    ensure_dir,
    get_default_cache_dir,
    get_default_config_dir,
    get_default_data_dir,
    get_default_log_dir,
    get_platform_info,
    get_temp_dir,
    is_linux,
    is_macos,
    is_windows,
    normalize_path,
    open_text_file,
    read_text_file,
    safe_run_async,
    setup_asyncio_policy,
    write_text_file,
)


class TestPlatformDetection:
    """Behavioral tests for platform detection functions."""

    def test_is_windows_returns_bool(self):
        """Given: Platform detection function
        When: is_windows called
        Then: Returns boolean."""
        # Given/When
        result = is_windows()

        # Then
        assert isinstance(result, bool)

    def test_is_macos_returns_bool(self):
        """Given: Platform detection function
        When: is_macos called
        Then: Returns boolean."""
        # Given/When
        result = is_macos()

        # Then
        assert isinstance(result, bool)

    def test_is_linux_returns_bool(self):
        """Given: Platform detection function
        When: is_linux called
        Then: Returns boolean."""
        # Given/When
        result = is_linux()

        # Then
        assert isinstance(result, bool)

    def test_exactly_one_platform_is_true(self):
        """Given: All platform detection functions
        When: Checking results
        Then: Exactly one returns True."""
        # Given/When
        platforms = [is_windows(), is_macos(), is_linux()]

        # Then
        assert sum(platforms) == 1, "Exactly one platform should be detected"

    @patch("platform.system", return_value="Windows")
    def test_is_windows_detects_windows(self, mock_system):
        """Given: System platform is Windows
        When: is_windows called
        Then: Returns True."""
        # Given/When
        result = is_windows()

        # Then
        assert result is True

    @patch("platform.system", return_value="Darwin")
    def test_is_macos_detects_darwin(self, mock_system):
        """Given: System platform is Darwin
        When: is_macos called
        Then: Returns True."""
        # Given/When
        result = is_macos()

        # Then
        assert result is True

    @patch("platform.system", return_value="Linux")
    def test_is_linux_detects_linux(self, mock_system):
        """Given: System platform is Linux
        When: is_linux called
        Then: Returns True."""
        # Given/When
        result = is_linux()

        # Then
        assert result is True


class TestDefaultDirectories:
    """Behavioral tests for default directory getters."""

    def test_get_default_log_dir_returns_path(self):
        """Given: Platform-specific config
        When: get_default_log_dir called
        Then: Returns Path object."""
        # Given/When
        result = get_default_log_dir()

        # Then
        assert isinstance(result, Path)

    def test_get_default_data_dir_returns_path(self):
        """Given: Platform-specific config
        When: get_default_data_dir called
        Then: Returns Path object."""
        # Given/When
        result = get_default_data_dir()

        # Then
        assert isinstance(result, Path)

    def test_get_default_config_dir_returns_path(self):
        """Given: Platform-specific config
        When: get_default_config_dir called
        Then: Returns Path object."""
        # Given/When
        result = get_default_config_dir()

        # Then
        assert isinstance(result, Path)

    def test_get_default_cache_dir_returns_path(self):
        """Given: Platform-specific config
        When: get_default_cache_dir called
        Then: Returns Path object."""
        # Given/When
        result = get_default_cache_dir()

        # Then
        assert isinstance(result, Path)

    def test_log_dir_contains_empathy(self):
        """Given: Default log directory
        When: Checking path components
        Then: Contains 'empathy' in path."""
        # Given/When
        log_dir = get_default_log_dir()

        # Then
        assert "empathy" in str(log_dir).lower()

    def test_data_dir_contains_empathy(self):
        """Given: Default data directory
        When: Checking path components
        Then: Contains 'empathy' in path."""
        # Given/When
        data_dir = get_default_data_dir()

        # Then
        assert "empathy" in str(data_dir).lower()


class TestFileOperations:
    """Behavioral tests for file operation utilities."""

    def test_read_text_file_reads_content(self, tmp_path):
        """Given: File with text content
        When: read_text_file called
        Then: Returns file content."""
        # Given
        test_file = tmp_path / "test.txt"
        expected_content = "Hello, World!"
        test_file.write_text(expected_content, encoding="utf-8")

        # When
        result = read_text_file(test_file)

        # Then
        assert result == expected_content

    def test_read_text_file_handles_unicode(self, tmp_path):
        """Given: File with unicode content
        When: read_text_file called
        Then: Correctly reads unicode."""
        # Given
        test_file = tmp_path / "unicode.txt"
        expected_content = "Hello 世界 🌍"
        test_file.write_text(expected_content, encoding="utf-8")

        # When
        result = read_text_file(test_file)

        # Then
        assert result == expected_content

    def test_write_text_file_creates_file(self, tmp_path):
        """Given: Target file path
        When: write_text_file called
        Then: File is created with content."""
        # Given
        test_file = tmp_path / "output.txt"
        content = "Test content"

        # When
        write_text_file(test_file, content)

        # Then
        assert test_file.exists()
        assert test_file.read_text(encoding="utf-8") == content

    def test_write_text_file_returns_char_count(self, tmp_path):
        """Given: Content to write
        When: write_text_file called
        Then: Returns number of characters written."""
        # Given
        test_file = tmp_path / "output.txt"
        content = "Hello"

        # When
        result = write_text_file(test_file, content)

        # Then
        assert result == len(content)

    def test_open_text_file_defaults_to_utf8(self, tmp_path):
        """Given: File to open
        When: open_text_file called without encoding
        Then: Uses UTF-8 encoding."""
        # Given
        test_file = tmp_path / "test.txt"
        test_file.write_text("content", encoding="utf-8")

        # When
        with open_text_file(test_file, "r") as f:
            # Then
            assert f.encoding == "utf-8"


class TestPathUtilities:
    """Behavioral tests for path utility functions."""

    def test_normalize_path_returns_path_object(self):
        """Given: String path
        When: normalize_path called
        Then: Returns Path object."""
        # Given
        path_str = "/some/path"

        # When
        result = normalize_path(path_str)

        # Then
        assert isinstance(result, Path)

    def test_normalize_path_resolves_relative_paths(self):
        """Given: Relative path with '..'
        When: normalize_path called
        Then: Returns absolute resolved path."""
        # Given
        relative_path = "../test"

        # When
        result = normalize_path(relative_path)

        # Then
        assert result.is_absolute()

    def test_get_temp_dir_returns_path(self):
        """Given: System temp directory
        When: get_temp_dir called
        Then: Returns Path object."""
        # Given/When
        result = get_temp_dir()

        # Then
        assert isinstance(result, Path)

    def test_get_temp_dir_exists(self):
        """Given: System temp directory
        When: get_temp_dir called
        Then: Returned path exists."""
        # Given/When
        temp_dir = get_temp_dir()

        # Then
        assert temp_dir.exists()

    def test_ensure_dir_creates_directory(self, tmp_path):
        """Given: Nonexistent directory path
        When: ensure_dir called
        Then: Directory is created."""
        # Given
        new_dir = tmp_path / "new_directory"
        assert not new_dir.exists()

        # When
        result = ensure_dir(new_dir)

        # Then
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_ensure_dir_creates_nested_directories(self, tmp_path):
        """Given: Nested directory path
        When: ensure_dir called
        Then: All parent directories created."""
        # Given
        nested_dir = tmp_path / "a" / "b" / "c"

        # When
        result = ensure_dir(nested_dir)

        # Then
        assert nested_dir.exists()
        assert (tmp_path / "a").exists()
        assert (tmp_path / "a" / "b").exists()

    def test_ensure_dir_is_idempotent(self, tmp_path):
        """Given: Existing directory
        When: ensure_dir called again
        Then: No error, directory still exists."""
        # Given
        test_dir = tmp_path / "existing"
        test_dir.mkdir()

        # When
        result = ensure_dir(test_dir)

        # Then
        assert test_dir.exists()


class TestAsyncioUtilities:
    """Behavioral tests for asyncio utilities."""

    def test_setup_asyncio_policy_runs_without_error(self):
        """Given: Asyncio module
        When: setup_asyncio_policy called
        Then: Completes without error."""
        # Given/When/Then (no assertion needed, just shouldn't raise)
        setup_asyncio_policy()

    def test_safe_run_async_executes_coroutine(self):
        """Given: Simple async coroutine
        When: safe_run_async called
        Then: Coroutine executes and returns result."""

        # Given
        async def test_coro():
            return 42

        # When
        result = safe_run_async(test_coro())

        # Then
        assert result == 42

    def test_safe_run_async_handles_async_sleep(self):
        """Given: Coroutine with async sleep
        When: safe_run_async called
        Then: Sleep completes successfully."""

        # Given
        async def test_coro():
            await asyncio.sleep(0.001)
            return "done"

        # When
        result = safe_run_async(test_coro())

        # Then
        assert result == "done"


class TestPlatformInfo:
    """Behavioral tests for platform information."""

    def test_platform_info_is_dict(self):
        """Given: PLATFORM_INFO constant
        When: Checking type
        Then: It is a dictionary."""
        # Given/When/Then
        assert isinstance(PLATFORM_INFO, dict)

    def test_platform_info_has_system_key(self):
        """Given: PLATFORM_INFO
        When: Checking for 'system' key
        Then: Key exists."""
        # Given/When/Then
        assert "system" in PLATFORM_INFO

    def test_platform_info_has_python_version(self):
        """Given: PLATFORM_INFO
        When: Checking for 'python_version'
        Then: Key exists with version string."""
        # Given/When
        version = PLATFORM_INFO.get("python_version")

        # Then
        assert version is not None
        assert isinstance(version, str)

    def test_get_platform_info_returns_copy(self):
        """Given: PLATFORM_INFO constant
        When: get_platform_info called
        Then: Returns a copy, not original."""
        # Given/When
        info1 = get_platform_info()
        info2 = get_platform_info()

        # Then
        assert info1 is not info2  # Different objects
        assert info1 == info2  # Same content

    def test_platform_info_has_boolean_flags(self):
        """Given: PLATFORM_INFO
        When: Checking platform flags
        Then: All flags are boolean."""
        # Given
        flags = ["is_windows", "is_macos", "is_linux"]

        # When/Then
        for flag in flags:
            assert flag in PLATFORM_INFO
            assert isinstance(PLATFORM_INFO[flag], bool)

    def test_platform_info_has_exactly_one_true_flag(self):
        """Given: Platform boolean flags
        When: Counting True values
        Then: Exactly one is True."""
        # Given
        flags = [PLATFORM_INFO["is_windows"], PLATFORM_INFO["is_macos"], PLATFORM_INFO["is_linux"]]

        # When/Then
        assert sum(flags) == 1
