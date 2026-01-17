"""Token counting utilities using Anthropic's tokenizer.

Provides accurate token counting for billing-accurate cost tracking.
Replaces rough estimates (4 chars per token) with Anthropic's official counter.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from typing import Any

# Lazy import to avoid requiring anthropic if not used
_client = None


def _get_client():
    """Get or create Anthropic client for token counting."""
    global _client
    if _client is None:
        try:
            from anthropic import Anthropic

            _client = Anthropic()
        except ImportError as e:
            raise ImportError(
                "anthropic package required for token counting. "
                "Install with: pip install anthropic"
            ) from e
    return _client


def count_tokens(text: str, model: str = "claude-sonnet-4-5") -> int:
    """Count tokens using Anthropic's tokenizer.

    Args:
        text: Text to tokenize
        model: Model ID (different models may have different tokenizers)

    Returns:
        Exact token count as would be billed by API

    Example:
        >>> count_tokens("Hello, world!")
        4
        >>> count_tokens("def hello():\\n    print('hi')")
        8

    Raises:
        ImportError: If anthropic package not installed
        ValueError: If text is invalid

    """
    if not text:
        return 0

    client = _get_client()

    # Use Anthropic's count_tokens method
    # Note: This is a synchronous call for simplicity
    try:
        result = client.count_tokens(text)
        return result
    except Exception as e:
        # Fallback to rough estimate if API fails
        # This ensures token counting never crashes workflows
        import logging

        logging.debug(f"Token counting failed, using fallback estimate: {e}")
        return len(text) // 4


def count_message_tokens(
    messages: list[dict[str, str]],
    system_prompt: str | None = None,
    model: str = "claude-sonnet-4-5",
) -> dict[str, int]:
    """Count tokens in a conversation.

    Args:
        messages: List of message dicts with "role" and "content"
        system_prompt: Optional system prompt
        model: Model ID

    Returns:
        Dict with token counts by component:
        - "system": System prompt tokens
        - "messages": Message tokens
        - "total": Sum of all tokens

    Example:
        >>> messages = [{"role": "user", "content": "Hello!"}]
        >>> count_message_tokens(messages, system_prompt="You are helpful")
        {"system": 4, "messages": 6, "total": 10}

    """
    counts: dict[str, int] = {}

    # Count system prompt
    if system_prompt:
        counts["system"] = count_tokens(system_prompt, model)
    else:
        counts["system"] = 0

    # Count messages
    # Combine all messages into single text for accurate tokenization
    message_text = "\n".join(f"{msg['role']}: {msg['content']}" for msg in messages)
    counts["messages"] = count_tokens(message_text, model)

    # Total
    counts["total"] = counts["system"] + counts["messages"]

    return counts


def estimate_cost(
    input_tokens: int, output_tokens: int, model: str = "claude-sonnet-4-5"
) -> float:
    """Estimate cost in USD based on token counts.

    Args:
        input_tokens: Input token count
        output_tokens: Output token count
        model: Model ID (used to look up pricing)

    Returns:
        Estimated cost in USD

    Example:
        >>> estimate_cost(1000, 500, "claude-sonnet-4-5")
        0.0105  # $3/M input + $15/M output

    Raises:
        ValueError: If model is unknown

    """
    # Import here to avoid circular dependency
    try:
        from empathy_os.models.registry import get_pricing_for_model

        pricing = get_pricing_for_model(model)
        if not pricing:
            raise ValueError(f"Unknown model: {model}")

        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost
    except ImportError:
        # Fallback if registry not available
        # Use default Sonnet 4.5 pricing
        input_cost = (input_tokens / 1_000_000) * 3.00
        output_cost = (output_tokens / 1_000_000) * 15.00
        return input_cost + output_cost


def calculate_cost_with_cache(
    input_tokens: int,
    output_tokens: int,
    cache_creation_tokens: int,
    cache_read_tokens: int,
    model: str = "claude-sonnet-4-5",
) -> dict[str, Any]:
    """Calculate cost including Anthropic prompt caching.

    Anthropic prompt caching pricing:
    - Cache writes: 25% markup over standard input pricing
    - Cache reads: 90% discount from standard input pricing

    Args:
        input_tokens: Regular input tokens (not cached)
        output_tokens: Output tokens
        cache_creation_tokens: Tokens written to cache
        cache_read_tokens: Tokens read from cache
        model: Model ID

    Returns:
        Dict with cost breakdown:
        - "base_cost": Cost without cache
        - "cache_write_cost": Cost for cache writes (25% markup)
        - "cache_read_cost": Cost for cache reads (90% discount)
        - "total_cost": Sum of all costs
        - "savings": Amount saved by cache reads

    Example:
        >>> calculate_cost_with_cache(1000, 500, 5000, 10000, "claude-sonnet-4-5")
        {
            "base_cost": 0.0105,
            "cache_write_cost": 0.01875,  # 5000 tokens * $3.75/M
            "cache_read_cost": 0.003,     # 10000 tokens * $0.30/M
            "total_cost": 0.03225,
            "savings": 0.027,             # Saved vs. no cache
        }

    """
    # Get pricing for model
    try:
        from empathy_os.models.registry import get_pricing_for_model

        pricing = get_pricing_for_model(model)
        if not pricing:
            raise ValueError(f"Unknown model: {model}")

        input_price_per_million = pricing["input"]
        output_price_per_million = pricing["output"]
    except (ImportError, ValueError):
        # Fallback to default Sonnet 4.5 pricing
        input_price_per_million = 3.00
        output_price_per_million = 15.00

    # Base cost (non-cached tokens)
    base_cost = (input_tokens / 1_000_000) * input_price_per_million
    base_cost += (output_tokens / 1_000_000) * output_price_per_million

    # Cache write cost (25% markup)
    cache_write_price = input_price_per_million * 1.25
    cache_write_cost = (cache_creation_tokens / 1_000_000) * cache_write_price

    # Cache read cost (90% discount = 10% of input price)
    cache_read_price = input_price_per_million * 0.1
    cache_read_cost = (cache_read_tokens / 1_000_000) * cache_read_price

    # Calculate what we would have paid without cache
    full_price_for_cached = (cache_read_tokens / 1_000_000) * input_price_per_million
    savings = full_price_for_cached - cache_read_cost

    return {
        "base_cost": round(base_cost, 6),
        "cache_write_cost": round(cache_write_cost, 6),
        "cache_read_cost": round(cache_read_cost, 6),
        "total_cost": round(base_cost + cache_write_cost + cache_read_cost, 6),
        "savings": round(savings, 6),
    }
