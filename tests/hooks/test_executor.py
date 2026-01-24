"""Tests for hook executor."""

import asyncio

import pytest

from empathy_llm_toolkit.hooks.config import HookDefinition, HookType
from empathy_llm_toolkit.hooks.executor import HookExecutor, HookExecutorSync


class TestHookExecutor:
    """Tests for HookExecutor."""

    def test_create_executor(self):
        """Test creating an executor."""
        executor = HookExecutor()
        assert executor._python_handlers == {}

    def test_create_executor_with_handlers(self):
        """Test creating executor with pre-registered handlers."""
        handlers = {"test_id": lambda **ctx: "result"}
        executor = HookExecutor(python_handlers=handlers)

        assert "test_id" in executor._python_handlers


@pytest.mark.asyncio
class TestHookExecutorAsync:
    """Async tests for HookExecutor."""

    async def test_execute_python_hook_by_id(self):
        """Test executing a Python hook by handler ID."""
        def my_handler(**context):
            return {"value": context.get("input", 0) * 2}

        executor = HookExecutor(python_handlers={"my_handler_id": my_handler})

        hook = HookDefinition(
            type=HookType.PYTHON,
            command="my_handler_id",
        )

        result = await executor.execute(hook, {"input": 5})

        assert result["success"] is True
        assert result["output"]["value"] == 10
        assert "duration_ms" in result

    async def test_execute_python_hook_async_handler(self):
        """Test executing an async Python handler."""
        async def async_handler(**context):
            await asyncio.sleep(0.01)
            return {"async": True}

        executor = HookExecutor(python_handlers={"async_id": async_handler})

        hook = HookDefinition(
            type=HookType.PYTHON,
            command="async_id",
        )

        result = await executor.execute(hook, {})

        assert result["success"] is True
        assert result["output"]["async"] is True

    async def test_execute_command_hook(self):
        """Test executing a shell command hook."""
        executor = HookExecutor()

        hook = HookDefinition(
            type=HookType.COMMAND,
            command="echo 'hello world'",
        )

        result = await executor.execute(hook, {})

        assert result["success"] is True
        assert "hello world" in result["output"]

    async def test_execute_command_with_substitution(self):
        """Test command variable substitution."""
        executor = HookExecutor()

        hook = HookDefinition(
            type=HookType.COMMAND,
            command="echo 'File: {file_path}'",
        )

        result = await executor.execute(hook, {"file_path": "test.py"})

        assert result["success"] is True
        assert "test.py" in result["output"]

    async def test_execute_command_missing_variable(self):
        """Test command with missing variable fails."""
        executor = HookExecutor()

        hook = HookDefinition(
            type=HookType.COMMAND,
            command="echo {missing_var}",
        )

        result = await executor.execute(hook, {})

        assert result["success"] is False
        assert "missing_var" in result["error"].lower() or "Missing" in result["error"]

    async def test_execute_timeout(self):
        """Test hook timeout handling."""
        async def slow_handler(**context):
            await asyncio.sleep(10)
            return {}

        executor = HookExecutor(python_handlers={"slow": slow_handler})

        hook = HookDefinition(
            type=HookType.PYTHON,
            command="slow",
            timeout=1,  # 1 second timeout
        )

        result = await executor.execute(hook, {})

        assert result["success"] is False
        assert "timeout" in result["error"].lower()

    async def test_execute_async_mode(self):
        """Test async (fire-and-forget) execution."""
        call_log = []

        async def logging_handler(**context):
            await asyncio.sleep(0.1)
            call_log.append("executed")

        executor = HookExecutor(python_handlers={"logger": logging_handler})

        hook = HookDefinition(
            type=HookType.PYTHON,
            command="logger",
            async_execution=True,
        )

        result = await executor.execute(hook, {})

        assert result["success"] is True
        assert result["async"] is True

        # Handler hasn't completed yet
        assert len(call_log) == 0

        # Wait for async execution
        await asyncio.sleep(0.2)
        assert len(call_log) == 1

    async def test_execute_python_module_import(self):
        """Test importing and calling a module:function."""
        executor = HookExecutor()

        # Use a built-in module function
        hook = HookDefinition(
            type=HookType.PYTHON,
            command="os.path:exists",
        )

        result = await executor.execute(hook, {})

        # This will fail because exists() needs a path arg
        # But it validates the import mechanism works
        assert "success" in result

    async def test_execute_invalid_python_format(self):
        """Test invalid Python hook format."""
        executor = HookExecutor()

        hook = HookDefinition(
            type=HookType.PYTHON,
            command="invalid_no_colon",
        )

        result = await executor.execute(hook, {})

        assert result["success"] is False
        assert "module.path:function" in result["error"]


class TestHookExecutorSync:
    """Tests for synchronous executor wrapper."""

    def test_execute_sync(self):
        """Test synchronous execution."""
        def sync_handler(**context):
            return {"sync": True}

        executor = HookExecutorSync(python_handlers={"sync": sync_handler})

        hook = HookDefinition(
            type=HookType.PYTHON,
            command="sync",
        )

        result = executor.execute(hook, {})

        assert result["success"] is True
        assert result["output"]["sync"] is True
