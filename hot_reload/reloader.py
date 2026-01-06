"""Dynamic wizard reloader for hot-reload.

Handles reloading wizard modules without server restart.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import importlib
import logging
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ReloadResult:
    """Result of a wizard reload operation."""

    def __init__(
        self,
        success: bool,
        wizard_id: str,
        message: str,
        error: str | None = None,
    ):
        """Initialize reload result.

        Args:
            success: Whether reload succeeded
            wizard_id: ID of wizard that was reloaded
            message: Status message
            error: Error message if failed

        """
        self.success = success
        self.wizard_id = wizard_id
        self.message = message
        self.error = error

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "wizard_id": self.wizard_id,
            "message": self.message,
            "error": self.error,
        }


class WizardReloader:
    """Handles dynamic reloading of wizard modules.

    Supports hot-reload of wizards without server restart by:
    1. Unloading old module from sys.modules
    2. Reloading module with importlib
    3. Re-registering wizard with wizard API
    4. Notifying clients via callback
    """

    def __init__(
        self,
        register_callback: Callable[[str, type], bool],
        notification_callback: Callable[[dict], None] | None = None,
    ):
        """Initialize reloader.

        Args:
            register_callback: Function to register wizard (wizard_id, wizard_class) -> success
            notification_callback: Optional function to notify clients of reload events

        """
        self.register_callback = register_callback
        self.notification_callback = notification_callback
        self._reload_count = 0

    def reload_wizard(self, wizard_id: str, file_path: str) -> ReloadResult:
        """Reload a wizard module.

        Args:
            wizard_id: Wizard identifier
            file_path: Path to wizard file

        Returns:
            ReloadResult with outcome

        """
        logger.info(f"Attempting to reload wizard: {wizard_id} from {file_path}")

        try:
            # Get module name from file path
            module_name = self._get_module_name(file_path)
            if not module_name:
                error_msg = f"Could not determine module name from {file_path}"
                logger.error(error_msg)
                return ReloadResult(
                    success=False,
                    wizard_id=wizard_id,
                    message="Failed to reload",
                    error=error_msg,
                )

            # Unload old module
            self._unload_module(module_name)

            # Reload module
            try:
                module = importlib.import_module(module_name)
            except ImportError as e:
                error_msg = f"Failed to import module {module_name}: {e}"
                logger.error(error_msg)
                self._notify_reload_failed(wizard_id, error_msg)
                return ReloadResult(
                    success=False,
                    wizard_id=wizard_id,
                    message="Import failed",
                    error=error_msg,
                )

            # Find wizard class in module
            wizard_class = self._find_wizard_class(module)
            if not wizard_class:
                error_msg = f"No wizard class found in {module_name}"
                logger.error(error_msg)
                self._notify_reload_failed(wizard_id, error_msg)
                return ReloadResult(
                    success=False,
                    wizard_id=wizard_id,
                    message="No wizard class found",
                    error=error_msg,
                )

            # Re-register wizard
            success = self.register_callback(wizard_id, wizard_class)

            if success:
                self._reload_count += 1
                logger.info(
                    f"✓ Successfully reloaded {wizard_id} ({self._reload_count} total reloads)"
                )
                self._notify_reload_success(wizard_id)

                return ReloadResult(
                    success=True,
                    wizard_id=wizard_id,
                    message=f"Reloaded successfully (reload #{self._reload_count})",
                )
            else:
                error_msg = "Registration failed"
                logger.error(f"Failed to re-register {wizard_id}")
                self._notify_reload_failed(wizard_id, error_msg)
                return ReloadResult(
                    success=False,
                    wizard_id=wizard_id,
                    message="Registration failed",
                    error=error_msg,
                )

        except Exception as e:
            error_msg = f"Unexpected error reloading {wizard_id}: {e}"
            logger.exception(error_msg)
            self._notify_reload_failed(wizard_id, str(e))
            return ReloadResult(
                success=False,
                wizard_id=wizard_id,
                message="Unexpected error",
                error=str(e),
            )

    def _get_module_name(self, file_path: str) -> str | None:
        """Get Python module name from file path.

        Args:
            file_path: Path to Python file

        Returns:
            Module name or None if cannot determine

        """
        try:
            path = Path(file_path).resolve()

            # Remove .py extension
            if not path.suffix == ".py":
                return None

            # Get parts relative to project root
            # Try to find common patterns: wizards/, coach_wizards/, empathy_software_plugin/wizards/
            parts = path.parts

            # Find wizard directory in path
            wizard_dir_indices = [i for i, part in enumerate(parts) if "wizard" in part.lower()]

            if not wizard_dir_indices:
                return None

            # Take from first wizard directory
            start_idx = wizard_dir_indices[0]

            # Build module name
            module_parts = list(parts[start_idx:])
            module_parts[-1] = module_parts[-1].replace(".py", "")

            module_name = ".".join(module_parts)
            return module_name

        except Exception as e:
            logger.error(f"Error getting module name from {file_path}: {e}")
            return None

    def _unload_module(self, module_name: str) -> None:
        """Unload module from sys.modules.

        Args:
            module_name: Name of module to unload

        """
        # Unload exact module
        if module_name in sys.modules:
            del sys.modules[module_name]
            logger.debug(f"Unloaded module: {module_name}")

        # Also unload any submodules
        submodules = [name for name in sys.modules.keys() if name.startswith(f"{module_name}.")]
        for submodule in submodules:
            del sys.modules[submodule]
            logger.debug(f"Unloaded submodule: {submodule}")

    def _find_wizard_class(self, module: Any) -> type | None:
        """Find wizard class in module.

        Args:
            module: Python module

        Returns:
            Wizard class or None if not found

        """
        # Look for classes ending with "Wizard"
        for name in dir(module):
            if name.endswith("Wizard") and not name.startswith("_"):
                attr = getattr(module, name)
                if isinstance(attr, type):
                    return attr

        return None

    def _notify_reload_success(self, wizard_id: str) -> None:
        """Notify clients of successful reload.

        Args:
            wizard_id: ID of reloaded wizard

        """
        if self.notification_callback:
            try:
                self.notification_callback(
                    {
                        "event": "wizard_reloaded",
                        "wizard_id": wizard_id,
                        "success": True,
                        "reload_count": self._reload_count,
                    }
                )
            except Exception as e:
                logger.error(f"Error sending reload notification: {e}")

    def _notify_reload_failed(self, wizard_id: str, error: str) -> None:
        """Notify clients of failed reload.

        Args:
            wizard_id: ID of wizard that failed to reload
            error: Error message

        """
        if self.notification_callback:
            try:
                self.notification_callback(
                    {
                        "event": "wizard_reload_failed",
                        "wizard_id": wizard_id,
                        "success": False,
                        "error": error,
                    }
                )
            except Exception as e:
                logger.error(f"Error sending failure notification: {e}")

    def get_reload_count(self) -> int:
        """Get total number of successful reloads.

        Returns:
            Reload count

        """
        return self._reload_count
