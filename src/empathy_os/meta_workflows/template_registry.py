"""Template registry for meta-workflows.

Handles loading, saving, and discovering meta-workflow templates.

Created: 2026-01-17
Purpose: Manage reusable workflow templates
"""

import importlib.util
import logging
from pathlib import Path

from empathy_os.meta_workflows.models import MetaWorkflowTemplate

logger = logging.getLogger(__name__)

# Import _validate_file_path from parent config.py (not config package)
_config_py_path = Path(__file__).parent.parent / "config.py"
_spec = importlib.util.spec_from_file_location("_config_module", _config_py_path)
if _spec and _spec.loader:
    _config_module = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_config_module)
    _validate_file_path = _config_module._validate_file_path
else:
    # Fallback: simple validation if import fails
    def _validate_file_path(path: str, allowed_dir: str | None = None) -> Path:
        if not path:
            raise ValueError("path must be non-empty")
        return Path(path).resolve()


class TemplateRegistry:
    """Registry for meta-workflow templates.

    Manages template storage, loading, and discovery.
    Templates are stored as JSON files in a directory.

    Attributes:
        storage_dir: Directory where templates are stored
    """

    def __init__(self, storage_dir: str | None = None):
        """Initialize template registry.

        Args:
            storage_dir: Directory for template storage
                        (default: .empathy/meta_workflows/templates/)

        Raises:
            ValueError: If storage_dir is invalid
        """
        if storage_dir is None:
            storage_dir = str(Path.home() / ".empathy" / "meta_workflows" / "templates")

        # Validate and create storage directory
        self.storage_dir = Path(_validate_file_path(storage_dir))
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Template registry initialized at: {self.storage_dir}")

    def load_template(self, template_id: str) -> MetaWorkflowTemplate | None:
        """Load a template by ID.

        Args:
            template_id: ID of template to load

        Returns:
            MetaWorkflowTemplate if found, None otherwise

        Raises:
            ValueError: If template file is invalid or corrupted
        """
        template_path = self.storage_dir / f"{template_id}.json"

        if not template_path.exists():
            logger.warning(f"Template not found: {template_id}")
            return None

        try:
            json_str = template_path.read_text(encoding="utf-8")
            template = MetaWorkflowTemplate.from_json(json_str)
            logger.info(f"Loaded template: {template_id}")
            return template

        except (ValueError, KeyError) as e:
            logger.error(f"Failed to load template {template_id}: {e}")
            raise ValueError(f"Invalid template file {template_id}: {e}") from e

    def save_template(self, template: MetaWorkflowTemplate) -> Path:
        """Save a template to disk.

        Args:
            template: Template to save

        Returns:
            Path where template was saved

        Raises:
            ValueError: If template is invalid or path is unsafe
            OSError: If write operation fails
        """
        template_path = self.storage_dir / f"{template.template_id}.json"

        # Validate path (prevent path traversal)
        validated_path = _validate_file_path(str(template_path))

        try:
            json_str = template.to_json()
            validated_path.write_text(json_str, encoding="utf-8")
            logger.info(f"Saved template: {template.template_id} → {validated_path}")
            return validated_path

        except OSError as e:
            logger.error(f"Failed to save template {template.template_id}: {e}")
            raise

    def list_templates(self) -> list[str]:
        """List all available template IDs.

        Returns:
            List of template IDs (sorted)
        """
        template_files = self.storage_dir.glob("*.json")
        template_ids = [f.stem for f in template_files]
        template_ids.sort()

        logger.debug(f"Found {len(template_ids)} templates")
        return template_ids

    def get_template_info(self, template_id: str) -> dict | None:
        """Get basic info about a template without loading it fully.

        Args:
            template_id: ID of template

        Returns:
            Dictionary with basic template info, or None if not found
        """
        template = self.load_template(template_id)
        if template is None:
            return None

        return {
            "template_id": template.template_id,
            "name": template.name,
            "description": template.description,
            "version": template.version,
            "tags": template.tags,
            "author": template.author,
            "estimated_cost_range": template.estimated_cost_range,
            "estimated_duration_minutes": template.estimated_duration_minutes,
            "question_count": len(template.form_schema.questions),
            "agent_rule_count": len(template.agent_composition_rules),
        }

    def delete_template(self, template_id: str) -> bool:
        """Delete a template.

        Args:
            template_id: ID of template to delete

        Returns:
            True if deleted, False if not found

        Raises:
            OSError: If delete operation fails
        """
        template_path = self.storage_dir / f"{template_id}.json"

        if not template_path.exists():
            logger.warning(f"Template not found for deletion: {template_id}")
            return False

        try:
            template_path.unlink()
            logger.info(f"Deleted template: {template_id}")
            return True

        except OSError as e:
            logger.error(f"Failed to delete template {template_id}: {e}")
            raise


# =============================================================================
# Module-level helpers
# =============================================================================


def get_default_registry() -> TemplateRegistry:
    """Get default template registry instance.

    Returns:
        TemplateRegistry using default storage location
    """
    return TemplateRegistry()
