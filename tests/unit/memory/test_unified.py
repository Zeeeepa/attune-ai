"""Tests for unified memory interface.

Covers Environment, MemoryConfig, and UnifiedMemory classes.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from empathy_os.memory.redis_bootstrap import RedisStartMethod, RedisStatus
from empathy_os.memory.short_term import AccessTier, TTLStrategy
from empathy_os.memory.unified import (
    Environment,
    MemoryConfig,
    UnifiedMemory,
)


@pytest.mark.unit
class TestEnvironment:
    """Tests for Environment enum."""

    def test_development_environment(self):
        """Test DEVELOPMENT environment value."""
        assert Environment.DEVELOPMENT.value == "development"

    def test_staging_environment(self):
        """Test STAGING environment value."""
        assert Environment.STAGING.value == "staging"

    def test_production_environment(self):
        """Test PRODUCTION environment value."""
        assert Environment.PRODUCTION.value == "production"

    def test_environment_from_string(self):
        """Test creating Environment from string."""
        assert Environment("development") == Environment.DEVELOPMENT
        assert Environment("staging") == Environment.STAGING
        assert Environment("production") == Environment.PRODUCTION

    def test_all_environments_exist(self):
        """Test that expected environments are defined."""
        environments = [e.value for e in Environment]
        assert "development" in environments
        assert "staging" in environments
        assert "production" in environments


@pytest.mark.unit
class TestMemoryConfig:
    """Tests for MemoryConfig dataclass."""

    def test_default_config(self):
        """Test MemoryConfig with default values."""
        config = MemoryConfig()

        assert config.environment == Environment.DEVELOPMENT
        assert config.redis_url is None
        assert config.redis_host == "localhost"
        assert config.redis_port == 6379
        assert config.redis_mock is False
        assert config.redis_auto_start is True
        assert config.default_ttl_seconds == 3600
        assert config.storage_dir == "./memdocs_storage"
        assert config.encryption_enabled is True
        assert config.claude_memory_enabled is True
        assert config.auto_promote_threshold == 0.8

    def test_custom_config(self):
        """Test MemoryConfig with custom values."""
        config = MemoryConfig(
            environment=Environment.PRODUCTION,
            redis_url="redis://custom:6380",
            redis_host="custom-host",
            redis_port=6380,
            redis_mock=True,
            default_ttl_seconds=7200,
            storage_dir="/custom/storage",
            encryption_enabled=False,
            auto_promote_threshold=0.9,
        )

        assert config.environment == Environment.PRODUCTION
        assert config.redis_url == "redis://custom:6380"
        assert config.redis_host == "custom-host"
        assert config.redis_port == 6380
        assert config.redis_mock is True
        assert config.default_ttl_seconds == 7200
        assert config.storage_dir == "/custom/storage"
        assert config.encryption_enabled is False
        assert config.auto_promote_threshold == 0.9

    def test_from_environment_default(self):
        """Test from_environment with no env vars set."""
        with patch.dict(os.environ, {}, clear=True):
            config = MemoryConfig.from_environment()

            assert config.environment == Environment.DEVELOPMENT
            assert config.redis_url is None
            assert config.redis_mock is False

    def test_from_environment_production(self):
        """Test from_environment with production env."""
        env_vars = {
            "EMPATHY_ENV": "production",
            "REDIS_URL": "redis://prod:6379",
            "EMPATHY_REDIS_MOCK": "false",
            "EMPATHY_STORAGE_DIR": "/prod/storage",
            "EMPATHY_ENCRYPTION": "true",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = MemoryConfig.from_environment()

            assert config.environment == Environment.PRODUCTION
            assert config.redis_url == "redis://prod:6379"
            assert config.redis_mock is False
            assert config.storage_dir == "/prod/storage"
            assert config.encryption_enabled is True

    def test_from_environment_mock_mode(self):
        """Test from_environment with mock Redis enabled."""
        env_vars = {
            "EMPATHY_REDIS_MOCK": "true",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = MemoryConfig.from_environment()
            assert config.redis_mock is True

    def test_from_environment_custom_redis_host_port(self):
        """Test from_environment with custom Redis host and port."""
        env_vars = {
            "EMPATHY_REDIS_HOST": "redis-server",
            "EMPATHY_REDIS_PORT": "6380",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = MemoryConfig.from_environment()
            assert config.redis_host == "redis-server"
            assert config.redis_port == 6380

    def test_from_environment_invalid_env_falls_back(self):
        """Test from_environment with invalid EMPATHY_ENV falls back to development."""
        env_vars = {
            "EMPATHY_ENV": "invalid_environment",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = MemoryConfig.from_environment()
            assert config.environment == Environment.DEVELOPMENT

    def test_from_environment_staging(self):
        """Test from_environment with staging env."""
        env_vars = {
            "EMPATHY_ENV": "staging",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = MemoryConfig.from_environment()
            assert config.environment == Environment.STAGING


@pytest.mark.unit
class TestUnifiedMemoryInit:
    """Tests for UnifiedMemory initialization."""

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    @patch("empathy_os.memory.unified.LongTermMemory")
    def test_init_with_mock_redis(self, mock_ltm, mock_secure, mock_redis):
        """Test initialization with mock Redis."""
        config = MemoryConfig(redis_mock=True)

        memory = UnifiedMemory(user_id="test_user", config=config)

        assert memory.user_id == "test_user"
        assert memory._initialized is True
        mock_redis.assert_called_with(use_mock=True)

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    @patch("empathy_os.memory.unified.LongTermMemory")
    def test_init_with_redis_url(self, mock_ltm, mock_secure, mock_redis):
        """Test initialization with Redis URL."""
        config = MemoryConfig(redis_url="redis://localhost:6379")

        with patch("empathy_os.memory.unified.get_redis_memory") as mock_get_redis:
            mock_get_redis.return_value = MagicMock()
            memory = UnifiedMemory(user_id="test_user", config=config)

            mock_get_redis.assert_called_with(url="redis://localhost:6379")
            assert memory._redis_status.method == RedisStartMethod.ALREADY_RUNNING

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    @patch("empathy_os.memory.unified.LongTermMemory")
    @patch("empathy_os.memory.unified.ensure_redis")
    def test_init_with_auto_start(self, mock_ensure, mock_ltm, mock_secure, mock_redis):
        """Test initialization with auto-start Redis."""
        mock_ensure.return_value = RedisStatus(
            available=True,
            method=RedisStartMethod.HOMEBREW,
            message="Started via Homebrew",
        )

        config = MemoryConfig(redis_auto_start=True, redis_mock=False, redis_url=None)
        memory = UnifiedMemory(user_id="test_user", config=config)

        mock_ensure.assert_called_once()
        assert memory._redis_status.available is True

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    @patch("empathy_os.memory.unified.LongTermMemory")
    def test_credentials_property(self, mock_ltm, mock_secure, mock_redis):
        """Test credentials property returns AgentCredentials."""
        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(
            user_id="agent@company.com",
            config=config,
            access_tier=AccessTier.STEWARD,
        )

        creds = memory.credentials

        assert creds.agent_id == "agent@company.com"
        assert creds.tier == AccessTier.STEWARD

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    @patch("empathy_os.memory.unified.LongTermMemory")
    def test_init_long_term_memory_failure(self, mock_ltm, mock_secure, mock_redis):
        """Test graceful handling when long-term memory fails to initialize."""
        mock_secure.side_effect = Exception("Storage unavailable")
        mock_ltm.side_effect = Exception("Storage unavailable")

        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)

        # Should still initialize with short-term memory
        assert memory._initialized is True
        assert memory._long_term is None
        assert memory.has_long_term is False


@pytest.mark.unit
class TestUnifiedMemoryBackendStatus:
    """Tests for get_backend_status method."""

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    @patch("empathy_os.memory.unified.LongTermMemory")
    def test_get_backend_status_with_mock_redis(self, mock_ltm, mock_secure, mock_redis):
        """Test backend status with mock Redis."""
        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)

        status = memory.get_backend_status()

        assert status["environment"] == "development"
        assert status["initialized"] is True
        assert status["short_term"]["mock"] is True
        assert status["short_term"]["method"] == "mock"

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    @patch("empathy_os.memory.unified.LongTermMemory")
    def test_get_backend_status_long_term_info(self, mock_ltm, mock_secure, mock_redis):
        """Test backend status includes long-term memory info."""
        config = MemoryConfig(
            redis_mock=True,
            storage_dir="/custom/storage",
            encryption_enabled=True,
        )
        memory = UnifiedMemory(user_id="test_user", config=config)

        status = memory.get_backend_status()

        assert status["long_term"]["storage_dir"] == "/custom/storage"
        assert status["long_term"]["encryption_enabled"] is True


@pytest.mark.unit
class TestUnifiedMemoryShortTermOps:
    """Tests for short-term memory operations."""

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    @patch("empathy_os.memory.unified.LongTermMemory")
    def test_stash_success(self, mock_ltm, mock_secure, mock_redis_cls):
        """Test stash stores data successfully."""
        mock_redis = MagicMock()
        mock_redis.stash.return_value = True
        mock_redis_cls.return_value = mock_redis

        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)

        result = memory.stash("test_key", {"data": "value"})

        assert result is True
        mock_redis.stash.assert_called_once()

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    @patch("empathy_os.memory.unified.LongTermMemory")
    def test_stash_with_custom_ttl(self, mock_ltm, mock_secure, mock_redis_cls):
        """Test stash with custom TTL selects appropriate strategy."""
        mock_redis = MagicMock()
        mock_redis.stash.return_value = True
        mock_redis_cls.return_value = mock_redis

        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)

        # Use a TTL that maps to SESSION strategy
        memory.stash("key", "value", ttl_seconds=1800)

        # Verify stash was called with SESSION strategy
        call_args = mock_redis.stash.call_args
        assert call_args[0][2].tier == AccessTier.CONTRIBUTOR  # credentials

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    @patch("empathy_os.memory.unified.LongTermMemory")
    def test_stash_no_short_term_memory(self, mock_ltm, mock_secure, mock_redis_cls):
        """Test stash returns False when short-term memory unavailable."""
        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)
        memory._short_term = None

        result = memory.stash("key", "value")

        assert result is False

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    @patch("empathy_os.memory.unified.LongTermMemory")
    def test_retrieve_success(self, mock_ltm, mock_secure, mock_redis_cls):
        """Test retrieve returns stored data."""
        mock_redis = MagicMock()
        mock_redis.retrieve.return_value = {"data": "stored_value"}
        mock_redis_cls.return_value = mock_redis

        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)

        result = memory.retrieve("test_key")

        assert result == {"data": "stored_value"}
        mock_redis.retrieve.assert_called_once()

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    @patch("empathy_os.memory.unified.LongTermMemory")
    def test_retrieve_no_short_term_memory(self, mock_ltm, mock_secure, mock_redis_cls):
        """Test retrieve returns None when short-term memory unavailable."""
        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)
        memory._short_term = None

        result = memory.retrieve("key")

        assert result is None


@pytest.mark.unit
class TestUnifiedMemoryStagedPatterns:
    """Tests for staged pattern operations."""

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    @patch("empathy_os.memory.unified.LongTermMemory")
    def test_stage_pattern_success(self, mock_ltm, mock_secure, mock_redis_cls):
        """Test staging a pattern for validation."""
        mock_redis = MagicMock()
        mock_redis.stage_pattern.return_value = True
        mock_redis_cls.return_value = mock_redis

        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)

        pattern_data = {
            "name": "Test Pattern",
            "description": "A test pattern",
            "content": "Pattern content here",
            "confidence": 0.85,
        }

        result = memory.stage_pattern(pattern_data, pattern_type="algorithm")

        assert result is not None
        assert result.startswith("staged_")
        mock_redis.stage_pattern.assert_called_once()

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    @patch("empathy_os.memory.unified.LongTermMemory")
    def test_stage_pattern_no_short_term(self, mock_ltm, mock_secure, mock_redis_cls):
        """Test stage_pattern returns None when short-term unavailable."""
        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)
        memory._short_term = None

        result = memory.stage_pattern({"name": "Test"})

        assert result is None

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    @patch("empathy_os.memory.unified.LongTermMemory")
    def test_get_staged_patterns(self, mock_ltm, mock_secure, mock_redis_cls):
        """Test retrieving staged patterns."""
        mock_pattern = MagicMock()
        mock_pattern.to_dict.return_value = {
            "pattern_id": "staged_abc123",
            "name": "Test Pattern",
        }

        mock_redis = MagicMock()
        mock_redis.list_staged_patterns.return_value = [mock_pattern]
        mock_redis_cls.return_value = mock_redis

        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)

        result = memory.get_staged_patterns()

        assert len(result) == 1
        assert result[0]["pattern_id"] == "staged_abc123"

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    @patch("empathy_os.memory.unified.LongTermMemory")
    def test_get_staged_patterns_empty(self, mock_ltm, mock_secure, mock_redis_cls):
        """Test get_staged_patterns returns empty list when none staged."""
        mock_redis = MagicMock()
        mock_redis.list_staged_patterns.return_value = []
        mock_redis_cls.return_value = mock_redis

        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)

        result = memory.get_staged_patterns()

        assert result == []


@pytest.mark.unit
class TestUnifiedMemoryLongTermOps:
    """Tests for long-term memory operations."""

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    @patch("empathy_os.memory.unified.LongTermMemory")
    def test_persist_pattern_success(self, mock_ltm, mock_secure_cls, mock_redis):
        """Test persisting a pattern to long-term storage."""
        mock_secure = MagicMock()
        mock_secure.store_pattern.return_value = {
            "pattern_id": "pat_123",
            "classification": "PUBLIC",
        }
        mock_secure_cls.return_value = mock_secure

        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)

        result = memory.persist_pattern(
            content="Pattern content",
            pattern_type="algorithm",
            classification="PUBLIC",
        )

        assert result is not None
        assert result["pattern_id"] == "pat_123"
        mock_secure.store_pattern.assert_called_once()

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    @patch("empathy_os.memory.unified.LongTermMemory")
    def test_persist_pattern_no_long_term(self, mock_ltm, mock_secure_cls, mock_redis):
        """Test persist_pattern returns None when long-term unavailable."""
        mock_secure_cls.side_effect = Exception("Storage unavailable")
        mock_ltm.side_effect = Exception("Storage unavailable")

        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)

        result = memory.persist_pattern("content", "algorithm")

        assert result is None

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    @patch("empathy_os.memory.unified.LongTermMemory")
    def test_recall_pattern_success(self, mock_ltm, mock_secure_cls, mock_redis):
        """Test recalling a pattern from long-term storage."""
        mock_secure = MagicMock()
        mock_secure.retrieve_pattern.return_value = {
            "pattern_id": "pat_123",
            "content": "Pattern content",
        }
        mock_secure_cls.return_value = mock_secure

        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)

        result = memory.recall_pattern("pat_123")

        assert result is not None
        assert result["content"] == "Pattern content"

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    @patch("empathy_os.memory.unified.LongTermMemory")
    def test_recall_pattern_not_found(self, mock_ltm, mock_secure_cls, mock_redis):
        """Test recall_pattern handles not found gracefully."""
        mock_secure = MagicMock()
        mock_secure.retrieve_pattern.side_effect = Exception("Pattern not found")
        mock_secure_cls.return_value = mock_secure

        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)

        result = memory.recall_pattern("nonexistent")

        assert result is None


@pytest.mark.unit
class TestUnifiedMemorySearch:
    """Tests for pattern search operations."""

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    @patch("empathy_os.memory.unified.LongTermMemory")
    def test_search_patterns_no_long_term(self, mock_ltm, mock_secure_cls, mock_redis):
        """Test search_patterns returns empty when long-term unavailable."""
        mock_secure_cls.side_effect = Exception("Storage unavailable")
        mock_ltm.side_effect = Exception("Storage unavailable")

        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)

        result = memory.search_patterns(query="test")

        assert result == []

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    @patch("empathy_os.memory.unified.LongTermMemory")
    def test_search_patterns_with_query(self, mock_ltm, mock_secure_cls, mock_redis):
        """Test search_patterns with text query."""
        mock_secure = MagicMock()
        mock_secure.storage_dir = "./test_storage"
        mock_secure_cls.return_value = mock_secure

        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)

        # Mock _get_all_patterns to return test data
        memory._get_all_patterns = MagicMock(return_value=[
            {"content": "algorithm for sorting", "pattern_type": "algorithm"},
            {"content": "protocol for messaging", "pattern_type": "protocol"},
            {"content": "algorithm for searching", "pattern_type": "algorithm"},
        ])

        result = memory.search_patterns(query="algorithm")

        assert len(result) == 2
        assert all("algorithm" in p["content"] for p in result)

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    @patch("empathy_os.memory.unified.LongTermMemory")
    def test_search_patterns_with_type_filter(self, mock_ltm, mock_secure_cls, mock_redis):
        """Test search_patterns with pattern_type filter."""
        mock_secure = MagicMock()
        mock_secure.storage_dir = "./test_storage"
        mock_secure_cls.return_value = mock_secure

        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)

        memory._get_all_patterns = MagicMock(return_value=[
            {"content": "test content", "pattern_type": "algorithm"},
            {"content": "test content", "pattern_type": "protocol"},
        ])

        result = memory.search_patterns(pattern_type="algorithm")

        assert len(result) == 1
        assert result[0]["pattern_type"] == "algorithm"

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    @patch("empathy_os.memory.unified.LongTermMemory")
    def test_search_patterns_with_limit(self, mock_ltm, mock_secure_cls, mock_redis):
        """Test search_patterns respects limit parameter."""
        mock_secure = MagicMock()
        mock_secure.storage_dir = "./test_storage"
        mock_secure_cls.return_value = mock_secure

        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)

        memory._get_all_patterns = MagicMock(return_value=[
            {"content": "pattern 1"},
            {"content": "pattern 2"},
            {"content": "pattern 3"},
            {"content": "pattern 4"},
            {"content": "pattern 5"},
        ])

        result = memory.search_patterns(limit=3)

        assert len(result) == 3


@pytest.mark.unit
class TestUnifiedMemoryPromotion:
    """Tests for pattern promotion operations."""

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    @patch("empathy_os.memory.unified.LongTermMemory")
    def test_promote_pattern_success(self, mock_ltm, mock_secure_cls, mock_redis_cls):
        """Test promoting a staged pattern to long-term storage."""
        mock_pattern = MagicMock()
        mock_pattern.to_dict.return_value = {
            "pattern_id": "staged_abc123",
            "pattern_type": "algorithm",
            "description": "Test pattern",
            "context": {"content": "Pattern content"},
        }

        mock_redis = MagicMock()
        mock_redis.list_staged_patterns.return_value = [mock_pattern]
        mock_redis.promote_pattern.return_value = True
        mock_redis_cls.return_value = mock_redis

        mock_secure = MagicMock()
        mock_secure.store_pattern.return_value = {
            "pattern_id": "pat_longterm123",
            "classification": "PUBLIC",
        }
        mock_secure_cls.return_value = mock_secure

        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)

        result = memory.promote_pattern("staged_abc123")

        assert result is not None
        assert result["pattern_id"] == "pat_longterm123"

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    @patch("empathy_os.memory.unified.LongTermMemory")
    def test_promote_pattern_not_found(self, mock_ltm, mock_secure_cls, mock_redis_cls):
        """Test promote_pattern when staged pattern doesn't exist."""
        mock_redis = MagicMock()
        mock_redis.list_staged_patterns.return_value = []
        mock_redis_cls.return_value = mock_redis

        mock_secure_cls.return_value = MagicMock()

        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)

        result = memory.promote_pattern("nonexistent_id")

        assert result is None

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    @patch("empathy_os.memory.unified.LongTermMemory")
    def test_promote_pattern_no_backends(self, mock_ltm, mock_secure_cls, mock_redis_cls):
        """Test promote_pattern when backends unavailable."""
        mock_secure_cls.side_effect = Exception("Unavailable")
        mock_ltm.side_effect = Exception("Unavailable")

        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)
        memory._short_term = None

        result = memory.promote_pattern("staged_123")

        assert result is None


@pytest.mark.unit
class TestUnifiedMemoryProperties:
    """Tests for UnifiedMemory properties."""

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    @patch("empathy_os.memory.unified.LongTermMemory")
    def test_has_short_term_true(self, mock_ltm, mock_secure, mock_redis):
        """Test has_short_term returns True when initialized."""
        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)

        assert memory.has_short_term is True

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    @patch("empathy_os.memory.unified.LongTermMemory")
    def test_has_short_term_false(self, mock_ltm, mock_secure, mock_redis):
        """Test has_short_term returns False when not initialized."""
        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)
        memory._short_term = None

        assert memory.has_short_term is False

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    @patch("empathy_os.memory.unified.LongTermMemory")
    def test_has_long_term_true(self, mock_ltm, mock_secure, mock_redis):
        """Test has_long_term returns True when initialized."""
        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)

        assert memory.has_long_term is True

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    @patch("empathy_os.memory.unified.LongTermMemory")
    def test_using_real_redis_false_when_mock(self, mock_ltm, mock_secure, mock_redis):
        """Test using_real_redis returns False in mock mode."""
        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)

        assert memory.using_real_redis is False

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    @patch("empathy_os.memory.unified.LongTermMemory")
    def test_short_term_property_raises_when_none(self, mock_ltm, mock_secure, mock_redis):
        """Test short_term property raises RuntimeError when not initialized."""
        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)
        memory._short_term = None

        with pytest.raises(RuntimeError, match="Short-term memory not initialized"):
            _ = memory.short_term

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    @patch("empathy_os.memory.unified.LongTermMemory")
    def test_long_term_property_raises_when_none(self, mock_ltm, mock_secure, mock_redis):
        """Test long_term property raises RuntimeError when not initialized."""
        mock_ltm.side_effect = Exception("Unavailable")

        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)

        with pytest.raises(RuntimeError, match="Long-term memory not initialized"):
            _ = memory.long_term


@pytest.mark.unit
class TestUnifiedMemoryHealthCheck:
    """Tests for health_check method."""

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    @patch("empathy_os.memory.unified.LongTermMemory")
    def test_health_check_structure(self, mock_ltm, mock_secure, mock_redis):
        """Test health_check returns expected structure."""
        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)

        health = memory.health_check()

        assert "short_term" in health
        assert "long_term" in health
        assert "environment" in health
        assert health["short_term"]["available"] is True
        assert health["short_term"]["mock_mode"] is True

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    @patch("empathy_os.memory.unified.LongTermMemory")
    def test_health_check_long_term_info(self, mock_ltm, mock_secure, mock_redis):
        """Test health_check includes long-term memory info."""
        config = MemoryConfig(
            redis_mock=True,
            storage_dir="/test/storage",
            encryption_enabled=True,
        )
        memory = UnifiedMemory(user_id="test_user", config=config)

        health = memory.health_check()

        assert health["long_term"]["available"] is True
        assert health["long_term"]["storage_dir"] == "/test/storage"
        assert health["long_term"]["encryption"] is True

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    @patch("empathy_os.memory.unified.LongTermMemory")
    def test_health_check_environment(self, mock_ltm, mock_secure, mock_redis):
        """Test health_check reflects environment setting."""
        config = MemoryConfig(
            environment=Environment.PRODUCTION,
            redis_mock=True,
        )
        memory = UnifiedMemory(user_id="test_user", config=config)

        health = memory.health_check()

        assert health["environment"] == "production"


@pytest.mark.unit
class TestUnifiedMemoryTTLStrategy:
    """Tests for TTL strategy mapping in stash."""

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    @patch("empathy_os.memory.unified.LongTermMemory")
    def test_ttl_maps_to_coordination(self, mock_ltm, mock_secure, mock_redis_cls):
        """Test short TTL maps to COORDINATION strategy."""
        mock_redis = MagicMock()
        mock_redis.stash.return_value = True
        mock_redis_cls.return_value = mock_redis

        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)

        memory.stash("key", "value", ttl_seconds=60)

        call_args = mock_redis.stash.call_args
        ttl_strategy = call_args[0][3]  # 4th arg is TTLStrategy
        assert ttl_strategy == TTLStrategy.COORDINATION

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    @patch("empathy_os.memory.unified.LongTermMemory")
    def test_ttl_maps_to_session(self, mock_ltm, mock_secure, mock_redis_cls):
        """Test medium TTL maps to SESSION strategy."""
        mock_redis = MagicMock()
        mock_redis.stash.return_value = True
        mock_redis_cls.return_value = mock_redis

        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)

        memory.stash("key", "value", ttl_seconds=1800)

        call_args = mock_redis.stash.call_args
        ttl_strategy = call_args[0][3]
        assert ttl_strategy == TTLStrategy.SESSION

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    @patch("empathy_os.memory.unified.LongTermMemory")
    def test_ttl_maps_to_conflict_context(self, mock_ltm, mock_secure, mock_redis_cls):
        """Test very long TTL maps to CONFLICT_CONTEXT strategy."""
        mock_redis = MagicMock()
        mock_redis.stash.return_value = True
        mock_redis_cls.return_value = mock_redis

        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)

        memory.stash("key", "value", ttl_seconds=1000000)

        call_args = mock_redis.stash.call_args
        ttl_strategy = call_args[0][3]
        assert ttl_strategy == TTLStrategy.CONFLICT_CONTEXT
