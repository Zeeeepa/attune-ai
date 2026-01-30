"""Autonomous Test Generation with Dashboard Integration - Enhanced Edition.

Generates behavioral tests with real-time monitoring via Agent Coordination Dashboard.

ENHANCEMENTS (Phase 1):
- Extended thinking mode for better test planning
- Prompt caching for 90% cost reduction
- Full source code (no truncation)
- Workflow-specific prompts with mocking templates
- Few-shot learning with examples

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

import json
import logging
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from empathy_os.memory.short_term import RedisShortTermMemory
from empathy_os.telemetry.agent_tracking import HeartbeatCoordinator
from empathy_os.telemetry.event_streaming import EventStreamer
from empathy_os.telemetry.feedback_loop import FeedbackLoop

logger = logging.getLogger(__name__)


class AutonomousTestGenerator:
    """Generate tests autonomously with dashboard monitoring and Anthropic best practices."""

    def __init__(self, agent_id: str, batch_num: int, modules: list[dict[str, Any]]):
        """Initialize generator.

        Args:
            agent_id: Unique agent identifier
            batch_num: Batch number (1-18)
            modules: List of modules to generate tests for
        """
        self.agent_id = agent_id
        self.batch_num = batch_num
        self.modules = modules

        # Initialize memory backend for dashboard integration
        try:
            self.memory = RedisShortTermMemory()
            self.coordinator = HeartbeatCoordinator(memory=self.memory, enable_streaming=True)
            self.event_streamer = EventStreamer(memory=self.memory)
            self.feedback_loop = FeedbackLoop(memory=self.memory)
        except Exception as e:
            logger.warning(f"Failed to initialize memory backend: {e}")
            self.coordinator = HeartbeatCoordinator()
            self.event_streamer = None
            self.feedback_loop = None

        self.output_dir = Path(f"tests/behavioral/generated/batch{batch_num}")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_all(self) -> dict[str, Any]:
        """Generate tests for all modules with progress tracking.

        Returns:
            Summary of generation results
        """
        # Start tracking
        self.coordinator.start_heartbeat(
            agent_id=self.agent_id,
            metadata={
                "batch": self.batch_num,
                "total_modules": len(self.modules),
                "workflow": "autonomous_test_generation",
            }
        )

        try:
            results = {
                "batch": self.batch_num,
                "total_modules": len(self.modules),
                "completed": 0,
                "failed": 0,
                "tests_generated": 0,
                "files_created": [],
            }

            for i, module in enumerate(self.modules):
                progress = (i + 1) / len(self.modules)
                module_name = module["file"].replace("src/empathy_os/", "")

                # Update dashboard
                self.coordinator.beat(
                    status="running",
                    progress=progress,
                    current_task=f"Generating tests for {module_name}"
                )

                try:
                    # Generate tests for this module
                    test_file = self._generate_module_tests(module)
                    if test_file:
                        results["completed"] += 1
                        results["files_created"].append(str(test_file))
                        logger.info(f"✅ Generated tests for {module_name}")

                        # Send event to dashboard
                        if self.event_streamer:
                            self.event_streamer.publish_event(
                                event_type="test_file_created",
                                data={
                                    "agent_id": self.agent_id,
                                    "module": module_name,
                                    "test_file": str(test_file),
                                    "batch": self.batch_num
                                }
                            )

                        # Record quality feedback
                        if self.feedback_loop:
                            self.feedback_loop.record_feedback(
                                workflow_name="test-generation",
                                stage_name="generation",
                                tier="capable",
                                quality_score=1.0,  # Success
                                metadata={"module": module_name, "status": "success", "batch": self.batch_num}
                            )
                    else:
                        results["failed"] += 1
                        logger.warning(f"⚠️ Skipped {module_name} (validation failed)")

                        # Record failure feedback
                        if self.feedback_loop:
                            self.feedback_loop.record_feedback(
                                workflow_name="test-generation",
                                stage_name="validation",
                                tier="capable",
                                quality_score=0.0,  # Failure
                                metadata={"module": module_name, "status": "validation_failed", "batch": self.batch_num}
                            )

                except Exception as e:
                    results["failed"] += 1
                    logger.error(f"❌ Error generating tests for {module_name}: {e}")

                    # Send error event
                    if self.event_streamer:
                        self.event_streamer.publish_event(
                            event_type="test_generation_error",
                            data={
                                "agent_id": self.agent_id,
                                "module": module_name,
                                "error": str(e),
                                "batch": self.batch_num
                            }
                        )

            # Count total tests
            results["tests_generated"] = self._count_tests()

            # Final update
            self.coordinator.beat(
                status="completed",
                progress=1.0,
                current_task=f"Completed: {results['completed']}/{results['total_modules']} modules"
            )

            return results

        except Exception as e:
            # Error tracking
            self.coordinator.beat(
                status="failed",
                progress=0.0,
                current_task=f"Failed: {str(e)}"
            )
            raise

        finally:
            # Stop heartbeat
            self.coordinator.stop_heartbeat(
                final_status="completed" if results["completed"] > 0 else "failed"
            )

    def _generate_module_tests(self, module: dict[str, Any]) -> Path | None:
        """Generate tests for a single module using LLM agent.

        Args:
            module: Module info dict with 'file', 'total', 'missing', etc.

        Returns:
            Path to generated test file, or None if skipped
        """
        source_file = Path(module["file"])
        module_name = source_file.stem

        # Skip if module doesn't exist
        if not source_file.exists():
            logger.warning(f"Source file not found: {source_file}")
            return None

        # Read source to understand what needs testing
        try:
            source_code = source_file.read_text()
        except Exception as e:
            logger.error(f"Cannot read {source_file}: {e}")
            return None

        # Generate test file path
        test_file = self.output_dir / f"test_{module_name}_behavioral.py"

        # Extract module path for imports
        module_path = str(source_file).replace("src/", "").replace(".py", "").replace("/", ".")

        # Generate tests using LLM agent with Anthropic best practices
        test_content = self._generate_with_llm(module_name, module_path, source_file, source_code)

        if not test_content:
            logger.warning(f"LLM generation failed for {module_name}")
            return None

        logger.info(f"LLM generated {len(test_content)} bytes for {module_name}")

        # Write test file
        test_file.write_text(test_content)
        logger.info(f"Wrote test file: {test_file}")

        # Validate it can be imported
        if not self._validate_test_file(test_file):
            test_file.unlink()
            return None

        return test_file

    def _is_workflow_module(self, source_code: str, module_path: str) -> bool:
        """Detect if module is a workflow requiring special handling.

        Args:
            source_code: Source code content
            module_path: Python import path

        Returns:
            True if this is a workflow module needing LLM mocking
        """
        # Check for workflow indicators
        indicators = [
            r"class\s+\w+Workflow",
            r"async\s+def\s+execute",
            r"tier_routing",
            r"LLMProvider",
            r"TelemetryCollector",
            r"from\s+anthropic\s+import",
            r"messages\.create",
            r"client\.messages"
        ]

        return any(re.search(pattern, source_code) for pattern in indicators)

    def _get_example_tests(self) -> str:
        """Get few-shot examples of excellent tests for prompt learning."""
        return """EXAMPLE 1: Testing a utility function with mocking
```python
import pytest
from unittest.mock import Mock, patch
from mymodule import process_data

class TestProcessData:
    def test_processes_valid_data_successfully(self):
        \"\"\"Given valid input data, when processing, then returns expected result.\"\"\"
        # Given
        input_data = {"key": "value", "count": 42}

        # When
        result = process_data(input_data)

        # Then
        assert result is not None
        assert result["status"] == "success"
        assert result["processed"] is True

    def test_handles_invalid_data_with_error(self):
        \"\"\"Given invalid input, when processing, then raises ValueError.\"\"\"
        # Given
        invalid_data = {"missing": "key"}

        # When/Then
        with pytest.raises(ValueError, match="Required key 'key' not found"):
            process_data(invalid_data)
```

EXAMPLE 2: Testing a workflow with LLM mocking
```python
import pytest
from unittest.mock import Mock, AsyncMock, patch
from mymodule import MyWorkflow

@pytest.fixture
def mock_llm_client(mocker):
    \"\"\"Mock Anthropic LLM client.\"\"\"
    mock = mocker.patch('anthropic.Anthropic')
    mock_response = Mock()
    mock_response.content = [Mock(text="mock LLM response")]
    mock_response.usage = Mock(input_tokens=100, output_tokens=50)
    mock_response.stop_reason = "end_turn"
    mock.return_value.messages.create = AsyncMock(return_value=mock_response)
    return mock

class TestMyWorkflow:
    @pytest.mark.asyncio
    async def test_executes_successfully_with_mocked_llm(self, mock_llm_client):
        \"\"\"Given valid input, when executing workflow, then completes successfully.\"\"\"
        # Given
        workflow = MyWorkflow()
        input_data = {"prompt": "test prompt"}

        # When
        result = await workflow.execute(input_data)

        # Then
        assert result is not None
        assert "response" in result
        mock_llm_client.return_value.messages.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_handles_api_error_gracefully(self, mock_llm_client):
        \"\"\"Given API failure, when executing, then handles error appropriately.\"\"\"
        # Given
        workflow = MyWorkflow()
        mock_llm_client.return_value.messages.create.side_effect = Exception("API Error")

        # When/Then
        with pytest.raises(Exception, match="API Error"):
            await workflow.execute({"prompt": "test"})
```
"""

    def _get_workflow_specific_prompt(self, module_name: str, module_path: str, source_code: str) -> str:
        """Get workflow-specific test generation prompt with comprehensive mocking guidance."""
        return f"""Generate comprehensive tests for this WORKFLOW module.

⚠️ CRITICAL: This module makes LLM API calls and requires proper mocking.

MODULE: {module_name}
IMPORT PATH: {module_path}

SOURCE CODE (COMPLETE - NO TRUNCATION):
```python
{source_code}
```

WORKFLOW TESTING REQUIREMENTS:

1. **Mock LLM API calls** - NEVER make real API calls in tests
   ```python
   @pytest.fixture
   def mock_llm_client(mocker):
       mock = mocker.patch('anthropic.Anthropic')
       mock_response = Mock()
       mock_response.content = [Mock(text="mock response")]
       mock_response.usage = Mock(input_tokens=100, output_tokens=50)
       mock_response.stop_reason = "end_turn"
       mock.return_value.messages.create = AsyncMock(return_value=mock_response)
       return mock
   ```

2. **Test tier routing** - Verify correct model selection (cheap/capable/premium)
3. **Test telemetry** - Mock and verify telemetry recording
4. **Test cost calculation** - Verify token usage and cost tracking
5. **Test error handling** - Mock API failures, timeouts, rate limits
6. **Test caching** - Mock cache hits/misses if applicable

TARGET COVERAGE: 40-50% (realistic for workflow classes with proper mocking)

Generate a complete test file with:
- Copyright header: "Generated by enhanced autonomous test generation system."
- Proper imports (from {module_path})
- Mock fixtures for ALL external dependencies (LLM, databases, APIs, file I/O)
- Given/When/Then structure in docstrings
- Both success and failure test cases
- Edge case handling
- Docstrings for all tests describing behavior

Return ONLY the complete Python test file, no explanations."""

    def _generate_with_llm(self, module_name: str, module_path: str, source_file: Path, source_code: str) -> str | None:
        """Generate comprehensive tests using LLM with Anthropic best practices.

        ENHANCEMENTS (Phase 1):
        - Extended thinking for better test planning
        - Prompt caching for 90% cost reduction
        - Full source code (NO TRUNCATION)
        - Workflow-specific prompts when detected

        Args:
            module_name: Name of module being tested
            module_path: Python import path (e.g., empathy_os.config)
            source_file: Path to source file
            source_code: Source code content (FULL, not truncated)

        Returns:
            Test file content with comprehensive tests, or None if generation failed
        """
        import os

        try:
            import anthropic
        except ImportError:
            logger.error("anthropic package not installed")
            return None

        # Get API key
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.error("ANTHROPIC_API_KEY not set")
            return None

        # Detect if this is a workflow module
        is_workflow = self._is_workflow_module(source_code, module_path)
        logger.info(f"Module {module_name}: workflow={is_workflow}, size={len(source_code)} bytes (FULL)")

        # Build appropriate prompt based on module type
        if is_workflow:
            generation_prompt = self._get_workflow_specific_prompt(module_name, module_path, source_code)
        else:
            generation_prompt = f"""Generate comprehensive behavioral tests for this Python module.

SOURCE FILE: {source_file}
MODULE PATH: {module_path}

SOURCE CODE (COMPLETE):
```python
{source_code}
```

Generate a complete test file that:
1. Uses Given/When/Then behavioral test structure
2. Tests all public functions and classes
3. Includes edge cases and error handling
4. Uses proper mocking for external dependencies
5. Targets 80%+ code coverage for this module
6. Follows pytest conventions

Requirements:
- Import from {module_path} (not from src/)
- Use pytest fixtures where appropriate
- Mock external dependencies (APIs, databases, file I/O)
- Test both success and failure paths
- Include docstrings for all tests
- Use descriptive test names
- Start with copyright header:
\"\"\"Behavioral tests for {module_name}.

Generated by enhanced autonomous test generation system.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
\"\"\"

Return ONLY the complete Python test file content, no explanations."""

        # Build messages with prompt caching (90% cost reduction on retries)
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "You are an expert Python test engineer. Here are examples of excellent tests:",
                        "cache_control": {"type": "ephemeral"}
                    },
                    {
                        "type": "text",
                        "text": self._get_example_tests(),
                        "cache_control": {"type": "ephemeral"}
                    },
                    {
                        "type": "text",
                        "text": generation_prompt
                    }
                ]
            }
        ]

        try:
            # Call Anthropic API with extended thinking and caching
            logger.info(f"Calling LLM with extended thinking for {module_name} (workflow={is_workflow})")
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-sonnet-4-5",  # capable tier
                max_tokens=16000,  # Output tokens
                thinking={
                    "type": "enabled",
                    "budget_tokens": 4000  # Thinking budget for test planning
                },
                messages=messages,
            )

            if not response.content:
                logger.warning(f"Empty LLM response for {module_name}")
                return None

            # Extract test content (thinking comes first, then text)
            test_content = None
            for block in response.content:
                if block.type == "text":
                    test_content = block.text.strip()
                    break

            if not test_content:
                logger.warning(f"No text content in LLM response for {module_name}")
                return None

            logger.info(f"LLM returned {len(test_content)} bytes for {module_name}")

            if len(test_content) < 100:
                logger.warning(f"LLM response too short for {module_name}: {test_content[:200]}")
                return None

            # Clean up response (remove markdown fences if present)
            if test_content.startswith("```python"):
                test_content = test_content[len("```python"):].strip()
            if test_content.endswith("```"):
                test_content = test_content[:-3].strip()

            # Check for truncation indicators
            if response.stop_reason == "max_tokens":
                logger.warning(f"⚠️  LLM response truncated for {module_name} (hit max_tokens)")
                # Response might be incomplete but let validation catch it

            # Quick syntax pre-check before returning
            try:
                import ast
                ast.parse(test_content)
                logger.info(f"✓ Quick syntax check passed for {module_name}")
            except SyntaxError as e:
                logger.error(f"❌ LLM generated invalid syntax for {module_name}: {e.msg} at line {e.lineno}")
                return None

            logger.info(f"Test content cleaned, final size: {len(test_content)} bytes")
            return test_content

        except Exception as e:
            logger.error(f"LLM generation error for {module_name}: {e}", exc_info=True)
            return None

    def _validate_test_file(self, test_file: Path) -> bool:
        """Validate test file can be imported and has valid syntax.

        Args:
            test_file: Path to test file

        Returns:
            True if valid, False otherwise
        """
        # Step 1: Check for syntax errors with ast.parse (fast)
        try:
            import ast
            content = test_file.read_text()
            ast.parse(content)
            logger.info(f"✓ Syntax check passed for {test_file.name}")
        except SyntaxError as e:
            logger.error(f"❌ Syntax error in {test_file.name} at line {e.lineno}: {e.msg}")
            return False
        except Exception as e:
            logger.error(f"❌ Cannot parse {test_file.name}: {e}")
            return False

        # Step 2: Check if pytest can collect the tests
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "--collect-only", str(test_file)],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                logger.error(f"❌ Pytest collection failed for {test_file.name}")
                logger.error(f"   Error: {result.stderr[:500]}")
                return False

            logger.info(f"✓ Pytest collection passed for {test_file.name}")
            return True

        except subprocess.TimeoutExpired:
            logger.error(f"❌ Validation timeout for {test_file.name}")
            return False
        except Exception as e:
            logger.error(f"❌ Validation exception for {test_file}: {e}")
            return False

    def _count_tests(self) -> int:
        """Count total tests in generated files.

        Returns:
            Number of tests
        """
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "--collect-only", "-q", str(self.output_dir)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            # Parse output like "123 tests collected"
            for line in result.stdout.split("\n"):
                if "tests collected" in line:
                    return int(line.split()[0])
            return 0
        except Exception:
            return 0


def run_batch_generation(batch_num: int, modules_json: str) -> None:
    """Run test generation for a batch.

    Args:
        batch_num: Batch number
        modules_json: JSON string of modules to process
    """
    # Parse modules
    modules = json.loads(modules_json)

    # Create agent
    agent_id = f"test-gen-batch{batch_num}"
    generator = AutonomousTestGenerator(agent_id, batch_num, modules)

    # Generate tests
    print(f"Starting autonomous test generation for batch {batch_num}")
    print(f"Modules to process: {len(modules)}")
    print(f"Agent ID: {agent_id}")
    print(f"ENHANCEMENTS: Extended thinking + Prompt caching + Workflow detection")
    print("Monitor at: http://localhost:8000\n")

    results = generator.generate_all()

    # Report results
    print(f"\n{'='*60}")
    print(f"Batch {batch_num} Complete!")
    print(f"{'='*60}")
    print(f"Modules processed: {results['completed']}/{results['total_modules']}")
    print(f"Tests generated: {results['tests_generated']}")
    print(f"Files created: {len(results['files_created'])}")
    print(f"Failed: {results['failed']}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python -m empathy_os.workflows.autonomous_test_gen <batch_num> <modules_json>")
        sys.exit(1)

    batch_num = int(sys.argv[1])
    modules_json = sys.argv[2]

    run_batch_generation(batch_num, modules_json)
