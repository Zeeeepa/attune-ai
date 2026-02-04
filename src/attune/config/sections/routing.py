"""Model routing configuration section.

Copyright 2026 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from dataclasses import dataclass
from typing import Literal


@dataclass
class RoutingConfig:
    """Model routing and tier selection configuration.

    Controls how requests are routed to different model tiers
    (cheap/capable/premium) and cost optimization settings.

    Attributes:
        default_tier: Default model tier for requests.
        cheap_model: Model ID for cheap/fast tier (Haiku).
        capable_model: Model ID for capable/balanced tier (Sonnet).
        premium_model: Model ID for premium/powerful tier (Opus).
        auto_tier_selection: Automatically select tier based on task complexity.
        cost_optimization: Enable cost-saving optimizations.
        max_tokens_cheap: Max output tokens for cheap tier.
        max_tokens_capable: Max output tokens for capable tier.
        max_tokens_premium: Max output tokens for premium tier.
        temperature_default: Default temperature for completions.
        retry_on_rate_limit: Retry requests on rate limit errors.
        max_retries: Maximum retry attempts.
    """

    default_tier: Literal["cheap", "capable", "premium"] = "capable"
    cheap_model: str = "claude-3-haiku-20240307"
    capable_model: str = "claude-3-5-sonnet-20241022"
    premium_model: str = "claude-3-opus-20240229"
    auto_tier_selection: bool = True
    cost_optimization: bool = True
    max_tokens_cheap: int = 4096
    max_tokens_capable: int = 8192
    max_tokens_premium: int = 16384
    temperature_default: float = 0.7
    retry_on_rate_limit: bool = True
    max_retries: int = 3

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "default_tier": self.default_tier,
            "cheap_model": self.cheap_model,
            "capable_model": self.capable_model,
            "premium_model": self.premium_model,
            "auto_tier_selection": self.auto_tier_selection,
            "cost_optimization": self.cost_optimization,
            "max_tokens_cheap": self.max_tokens_cheap,
            "max_tokens_capable": self.max_tokens_capable,
            "max_tokens_premium": self.max_tokens_premium,
            "temperature_default": self.temperature_default,
            "retry_on_rate_limit": self.retry_on_rate_limit,
            "max_retries": self.max_retries,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RoutingConfig":
        """Create from dictionary."""
        return cls(
            default_tier=data.get("default_tier", "capable"),
            cheap_model=data.get("cheap_model", "claude-3-haiku-20240307"),
            capable_model=data.get("capable_model", "claude-3-5-sonnet-20241022"),
            premium_model=data.get("premium_model", "claude-3-opus-20240229"),
            auto_tier_selection=data.get("auto_tier_selection", True),
            cost_optimization=data.get("cost_optimization", True),
            max_tokens_cheap=data.get("max_tokens_cheap", 4096),
            max_tokens_capable=data.get("max_tokens_capable", 8192),
            max_tokens_premium=data.get("max_tokens_premium", 16384),
            temperature_default=data.get("temperature_default", 0.7),
            retry_on_rate_limit=data.get("retry_on_rate_limit", True),
            max_retries=data.get("max_retries", 3),
        )
