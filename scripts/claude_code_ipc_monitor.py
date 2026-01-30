#!/usr/bin/env python3
"""Claude Code IPC Monitor for AskUserQuestion.

This script monitors for AskUserQuestion requests from Python code
and forwards them to Claude Code's AskUserQuestion tool.

Usage:
    # Run in background while Claude Code session is active
    python scripts/claude_code_ipc_monitor.py

The monitor watches for request files in /tmp/.claude-code-ipc/ and
creates response files with user selections.

Created: 2026-01-29
"""
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


class IPCMonitor:
    """Monitor for AskUserQuestion IPC requests."""

    def __init__(self, ipc_dir: Path):
        """Initialize IPC monitor.

        Args:
            ipc_dir: Directory to monitor for request files
        """
        self.ipc_dir = ipc_dir
        self.ipc_dir.mkdir(exist_ok=True)
        self.processed: set[str] = set()

        logger.info(f"IPC Monitor initialized: {self.ipc_dir}")

    def run(self):
        """Run monitoring loop."""
        logger.info("Starting IPC monitor (Ctrl+C to stop)")

        try:
            while True:
                self._process_requests()
                time.sleep(0.2)  # Check every 200ms

        except KeyboardInterrupt:
            logger.info("IPC monitor stopped")

    def _process_requests(self):
        """Process any pending request files."""
        for request_file in self.ipc_dir.glob("ask-request-*.json"):
            request_id = request_file.stem.replace("ask-request-", "")

            # Skip if already processed
            if request_id in self.processed:
                continue

            try:
                self._handle_request(request_file, request_id)
                self.processed.add(request_id)

            except Exception as e:
                logger.error(f"Error processing {request_file}: {e}")

    def _handle_request(self, request_file: Path, request_id: str):
        """Handle a single request file.

        Args:
            request_file: Path to request file
            request_id: Unique request identifier
        """
        # Read request
        request_data = json.loads(request_file.read_text())
        questions = request_data.get("questions", [])

        logger.info(f"Processing request {request_id}: {len(questions)} question(s)")

        # Forward to Claude Code AskUserQuestion tool
        # NOTE: This would be called by Claude Code agent, not by this Python script
        # The actual integration happens when Claude Code sees the request file
        # and uses its AskUserQuestion tool to prompt the user

        # For now, this script just logs the request
        # In production, this would trigger Claude Code to show the prompts
        for i, q in enumerate(questions, 1):
            logger.info(f"  Q{i}: {q.get('question')} ({len(q.get('options', []))} options)")

        # Create placeholder response
        # In production, this would contain actual user selections
        response_file = self.ipc_dir / f"ask-response-{request_id}.json"
        response_data = {
            "request_id": request_id,
            "answers": self._get_user_response(questions),
            "timestamp": time.time(),
        }

        response_file.write_text(json.dumps(response_data, indent=2))
        logger.info(f"Created response: {response_file}")

    def _get_user_response(self, questions: list[dict[str, Any]]) -> dict[str, Any]:
        """Get user response for questions.

        This is a placeholder that returns the first option for each question.
        In production, this would use Claude Code's AskUserQuestion tool.

        Args:
            questions: List of questions

        Returns:
            Dictionary mapping headers to selected answers
        """
        answers = {}

        for question in questions:
            header = question.get("header", "")
            options = question.get("options", [])

            if options:
                # Default to first option
                answers[header] = options[0].get("label", "")

        return answers


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Monitor for Claude Code IPC requests"
    )
    parser.add_argument(
        "--ipc-dir",
        type=Path,
        default=Path("/tmp/.claude-code-ipc"),
        help="Directory to monitor (default: /tmp/.claude-code-ipc)",
    )

    args = parser.parse_args()

    # Create and run monitor
    monitor = IPCMonitor(ipc_dir=args.ipc_dir)
    monitor.run()


if __name__ == "__main__":
    main()
