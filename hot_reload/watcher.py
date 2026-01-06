"""File system watcher for wizard hot-reload.

Monitors wizard directories for changes and triggers reloads.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import logging
from collections.abc import Callable
from pathlib import Path

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger(__name__)


class WizardFileHandler(FileSystemEventHandler):
    """Handles file system events for wizard files."""

    def __init__(self, reload_callback: Callable[[str], None]):
        """Initialize handler.

        Args:
            reload_callback: Function to call when wizard file changes

        """
        super().__init__()
        self.reload_callback = reload_callback
        self._processing = set()  # Prevent duplicate events

    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification events.

        Args:
            event: File system event

        """
        if event.is_directory:
            return

        file_path = event.src_path

        # Only process Python files
        if not file_path.endswith(".py"):
            return

        # Skip __pycache__ and test files
        if "__pycache__" in file_path or "test_" in file_path:
            return

        # Prevent duplicate processing
        if file_path in self._processing:
            return

        try:
            self._processing.add(file_path)

            wizard_id = self._extract_wizard_id(file_path)
            if wizard_id:
                logger.info(f"Detected change in {wizard_id} ({file_path})")
                self.reload_callback(wizard_id, file_path)

        except Exception as e:
            logger.error(f"Error processing file change {file_path}: {e}")
        finally:
            self._processing.discard(file_path)

    def _extract_wizard_id(self, file_path: str) -> str | None:
        """Extract wizard ID from file path.

        Args:
            file_path: Path to wizard file

        Returns:
            Wizard ID or None if cannot extract

        """
        path = Path(file_path)

        # Get filename without extension
        filename = path.stem

        # Remove common suffixes
        wizard_id = filename.replace("_wizard", "").replace("wizard_", "")

        # Convert to wizard ID format (snake_case)
        wizard_id = wizard_id.lower()

        return wizard_id if wizard_id else None


class WizardFileWatcher:
    """Watches wizard directories for file changes.

    Monitors specified directories and triggers reload callbacks
    when wizard files are modified.
    """

    def __init__(self, wizard_dirs: list[Path], reload_callback: Callable[[str, str], None]):
        """Initialize watcher.

        Args:
            wizard_dirs: List of directories to watch
            reload_callback: Function to call on file changes (wizard_id, file_path)

        """
        self.wizard_dirs = [Path(d) for d in wizard_dirs]
        self.reload_callback = reload_callback
        self.observer = Observer()
        self.event_handler = WizardFileHandler(reload_callback)
        self._running = False

    def start(self) -> None:
        """Start watching wizard directories."""
        if self._running:
            logger.warning("Watcher already running")
            return

        valid_dirs = []
        for directory in self.wizard_dirs:
            if not directory.exists():
                logger.warning(f"Directory does not exist: {directory}")
                continue

            if not directory.is_dir():
                logger.warning(f"Not a directory: {directory}")
                continue

            # Schedule watching
            self.observer.schedule(
                self.event_handler,
                str(directory),
                recursive=True,
            )
            valid_dirs.append(directory)
            logger.info(f"Watching directory: {directory}")

        if not valid_dirs:
            logger.error("No valid directories to watch")
            return

        self.observer.start()
        self._running = True

        logger.info(
            f"Hot-reload enabled for {len(valid_dirs)} "
            f"{'directory' if len(valid_dirs) == 1 else 'directories'}"
        )

    def stop(self) -> None:
        """Stop watching wizard directories."""
        if not self._running:
            return

        self.observer.stop()
        self.observer.join(timeout=5.0)
        self._running = False

        logger.info("Hot-reload watcher stopped")

    def is_running(self) -> bool:
        """Check if watcher is running.

        Returns:
            True if watching, False otherwise

        """
        return self._running

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
