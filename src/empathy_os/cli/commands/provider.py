"""Provider configuration commands.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from pathlib import Path

from empathy_os.config import _validate_file_path
from empathy_os.logging_config import get_logger

logger = get_logger(__name__)


def cmd_provider_hybrid(args):
    """Configure hybrid mode - pick best models for each tier.

    Args:
        args: Namespace object from argparse (no additional attributes used).

    Returns:
        None: Launches interactive tier configuration.
    """
    from empathy_os.models.provider_config import configure_hybrid_interactive

    configure_hybrid_interactive()


def cmd_provider_show(args):
    """Show current provider configuration.

    Args:
        args: Namespace object from argparse (no additional attributes used).

    Returns:
        None: Prints provider configuration and model mappings.
    """
    from empathy_os.models import MODEL_REGISTRY
    from empathy_os.models.provider_config import ProviderConfig
    from empathy_os.workflows.config import WorkflowConfig

    print("\n" + "=" * 60)
    print("Provider Configuration")
    print("=" * 60)

    # Detect available providers
    config = ProviderConfig.auto_detect()
    print(
        f"\nDetected API keys for: {', '.join(config.available_providers) if config.available_providers else 'None'}",
    )

    # Load workflow config
    wf_config = WorkflowConfig.load()
    print(f"\nDefault provider: {wf_config.default_provider}")

    # Show effective models
    print("\nEffective model mapping:")
    if wf_config.custom_models and "hybrid" in wf_config.custom_models:
        hybrid = wf_config.custom_models["hybrid"]
        for tier in ["cheap", "capable", "premium"]:
            model = hybrid.get(tier, "not configured")
            print(f"  {tier:8} → {model}")
    else:
        provider = wf_config.default_provider
        if provider in MODEL_REGISTRY:
            for tier in ["cheap", "capable", "premium"]:
                model_info = MODEL_REGISTRY[provider].get(tier)
                if model_info:
                    print(f"  {tier:8} → {model_info.id} ({provider})")

    print()


def cmd_provider_set(args):
    """Set default provider.

    Args:
        args: Namespace object from argparse with attributes:
            - name (str): Provider name to set as default.

    Returns:
        None: Saves provider to .empathy/workflows.yaml.
    """
    import yaml

    provider = args.name
    workflows_path = Path(".empathy/workflows.yaml")

    # Load existing config or create new
    if workflows_path.exists():
        with open(workflows_path) as f:
            config = yaml.safe_load(f) or {}
    else:
        config = {}
        workflows_path.parent.mkdir(parents=True, exist_ok=True)

    config["default_provider"] = provider

    validated_workflows_path = _validate_file_path(str(workflows_path))
    with open(validated_workflows_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    print(f"✓ Default provider set to: {provider}")
    print(f"  Saved to: {validated_workflows_path}")

    if provider == "hybrid":
        print("\n  Tip: Run 'empathy provider hybrid' to customize tier models")
