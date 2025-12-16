---
title: Give Claude Persistent Memory in 10 Lines of Python
published: false
description: How to make Claude remember your preferences across sessions using the Empathy Framework
tags: python, ai, claude, anthropic
cover_image:
---

# Give Claude Persistent Memory in 10 Lines of Python

Every conversation with Claude starts from scratch. Tell it you prefer concise code examples, and next session? It's forgotten.

Here's how to fix that.

## The Problem

Claude's API is stateless. Each request is independent. For simple Q&A, that's fine. But for:

- Development assistants that learn your coding style
- Customer support that remembers history
- Personal tools that adapt to preferences

...you need memory that persists.

## The Solution

```python
from empathy_llm_toolkit import EmpathyLLM

llm = EmpathyLLM(
    provider="anthropic",
    api_key="your-key",
    memory_enabled=True
)

# This preference survives across sessions
response = await llm.interact(
    user_id="dev_123",
    user_input="I prefer Python with type hints, no docstrings"
)
```

That's it. Next time this user connects—even days later—Claude remembers.

## How It Works

The [Empathy Framework](https://github.com/Smart-AI-Memory/empathy-framework) stores user context in a memory layer that:

1. **Persists across sessions** - Preferences survive restarts
2. **Scopes by user** - Each user has isolated memory
3. **Supports projects** - Different contexts for different work
4. **Includes privacy controls** - Clear memory, forget specific info

## Five Levels of Empathy

The framework implements five collaboration levels:

| Level | Behavior |
|-------|----------|
| 1 - Reactive | Standard request-response |
| 2 - Informed | Uses stored preferences |
| 3 - Predictive | Anticipates based on patterns |
| 4 - Anticipatory | Proactively suggests |
| 5 - Collaborative | Full partnership |

```python
# Level 3: Claude anticipates your needs
response = await llm.interact(
    user_id="dev_123",
    user_input="Starting a new FastAPI project",
    empathy_level=3
)
# Might proactively suggest your preferred patterns
```

## Privacy Built In

```python
# Clear all memory
await llm.clear_memory(user_id="dev_123")

# Forget specific information
await llm.forget(user_id="dev_123", pattern="email")
```

## Get Started

```bash
pip install empathy-framework
```

**Resources:**
- [GitHub](https://github.com/Smart-AI-Memory/empathy-framework)
- [Documentation](https://www.smartaimemory.com/docs)
- [Anthropic Cookbook Example](https://github.com/anthropics/anthropic-cookbook/tree/main/third_party/Empathy-framework)

---

*What would you build with an AI that remembers? Drop a comment below.*
