"""Document Generation Cost Management.

Cost tracking, estimation, and token auto-scaling for doc generation.
Extracted from workflow.py for maintainability.

Contains:
- DocGenCostMixin: Cost estimation, tracking, and auto-scaling methods

Expected attributes on the host class:
    max_cost: float
    cost_warning_threshold: float
    _accumulated_cost: float
    _cost_warning_issued: bool
    _user_max_write_tokens: int | None

Copyright 2025 Smart-AI-Memory
Licensed under the Apache License, Version 2.0
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..base import ModelTier

from .config import TOKEN_COSTS

logger = logging.getLogger(__name__)


class DocGenCostMixin:
    """Mixin providing cost management for document generation."""

    # Class-level defaults for expected attributes
    max_cost: float = 5.0
    cost_warning_threshold: float = 0.8
    _accumulated_cost: float = 0.0
    _cost_warning_issued: bool = False
    _user_max_write_tokens: int | None = None

    def _estimate_cost(self, tier: ModelTier, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for a given tier and token counts."""
        costs = TOKEN_COSTS.get(tier, TOKEN_COSTS.get(list(TOKEN_COSTS.keys())[1]))
        input_cost = (input_tokens / 1000) * costs["input"]
        output_cost = (output_tokens / 1000) * costs["output"]
        return input_cost + output_cost

    def _track_cost(
        self,
        tier: ModelTier,
        input_tokens: int,
        output_tokens: int,
    ) -> tuple[float, bool]:
        """Track accumulated cost and check against limits.

        Returns:
            Tuple of (cost_for_this_call, should_stop)

        """
        cost = self._estimate_cost(tier, input_tokens, output_tokens)
        self._accumulated_cost += cost

        # Check warning threshold
        if (
            self.max_cost > 0
            and not self._cost_warning_issued
            and self._accumulated_cost >= self.max_cost * self.cost_warning_threshold
        ):
            self._cost_warning_issued = True
            logger.warning(
                f"Doc-gen cost approaching limit: ${self._accumulated_cost:.2f} "
                f"of ${self.max_cost:.2f} ({self.cost_warning_threshold * 100:.0f}% threshold)",
            )

        # Check if we should stop
        should_stop = self.max_cost > 0 and self._accumulated_cost >= self.max_cost
        if should_stop:
            logger.warning(
                f"Doc-gen cost limit reached: ${self._accumulated_cost:.2f} >= ${self.max_cost:.2f}",
            )

        return cost, should_stop

    def _auto_scale_tokens(self, section_count: int) -> int:
        """Auto-scale max_write_tokens based on section count.

        Enterprise projects may have 20+ sections requiring more tokens.
        """
        if self._user_max_write_tokens is not None:
            return self._user_max_write_tokens  # User override

        # Base: 2000 tokens per section, minimum 16000, maximum 64000
        scaled = max(16000, min(64000, section_count * 2000))
        logger.info(f"Auto-scaled max_write_tokens to {scaled} for {section_count} sections")
        return scaled
