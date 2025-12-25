---
title: Give Your AI Persistent Memory (and Cut Costs 80%)
published: false
description: How to make Claude/GPT remember your preferences across sessions using the Empathy Framework v3.2.5
tags: python, ai, claude, openai, llm
cover_image:
---

# Give Your AI Persistent Memory (and Cut Costs 80%)

Every conversation with Claude starts from scratch. Tell it you prefer concise code examples, and next session? Forgotten.

Here's how to fix that—and save 80% on API costs while you're at it.

## The Problem

LLM APIs are stateless. Each request is independent. For simple Q&A, that's fine. But for:

- Development assistants that learn your coding style
- Support bots that remember customer history
- Personal tools that adapt to preferences

...you need memory that persists.

## The Solution: 10 Lines of Python

```python
from empathy_llm_toolkit import EmpathyLLM

llm = EmpathyLLM(
    provider="anthropic",  # or "openai", "ollama", "hybrid"
    memory_enabled=True
)

# This preference survives across sessions
response = await llm.interact(
    user_id="dev_123",
    user_input="I prefer Python with type hints, no docstrings"
)
```

That's it. Next time this user connects—even days later—the AI remembers.

## Why This Actually Matters

### 1. Cost Savings (80%)

Smart routing automatically picks the right model for each task:

| Task | Model | Cost |
|------|-------|------|
| Summarize text | Haiku/GPT-4o-mini | $0.25/M tokens |
| Fix bugs | Sonnet/GPT-4o | $3/M tokens |
| Design architecture | Opus/o1 | $15/M tokens |

**Real numbers:**
- Without routing (all Opus): $4.05/complex task
- With routing (tiered): $0.83/complex task
- **Savings: 80%**

```python
llm = EmpathyLLM(provider="anthropic", enable_model_routing=True)

# Automatically routes to Haiku
await llm.interact(user_id="dev", user_input="Summarize this", task_type="summarize")

# Automatically routes to Opus
await llm.interact(user_id="dev", user_input="Design the system", task_type="coordinate")
```

### 2. Bug Memory

My debugging wizard remembers every fix:

```python
result = await wizard.analyze({
    "error_message": "TypeError: Cannot read property 'map' of undefined",
    "file_path": "src/components/UserList.tsx"
})

print(result["historical_matches"])
# "This looks like bug #247 from 3 months ago"
# "Suggested fix: data?.items ?? []"
```

Without memory, every bug starts from zero. With it, your AI assistant **remembers every fix** and suggests proven solutions.

### 3. Provider Freedom

Not locked into one provider. Switch anytime:

```bash
empathy provider set anthropic  # Use Claude
empathy provider set openai     # Use GPT
empathy provider set ollama     # Use local models
empathy provider set hybrid     # Best of each
```

Use Ollama for sensitive code, Claude for complex reasoning, GPT for specific tasks.

## Smart Router

Natural language routing—no need to know which tool to use:

```python
from empathy_os.routing import SmartRouter

router = SmartRouter()

# Natural language → right wizard
decision = router.route_sync("Fix the security vulnerability in auth.py")
print(f"Primary: {decision.primary_wizard}")  # → security-audit
print(f"Confidence: {decision.confidence}")   # → 0.92
```

Examples:
- "Fix security in auth.py" → SecurityWizard
- "Review this PR" → CodeReviewWizard
- "Why is this slow?" → PerformanceWizard

## Quick Start

```bash
# Install
pip install empathy-framework

# Check available providers (auto-detects API keys)
empathy provider status

# Set your provider
empathy provider set anthropic

# See all commands
empathy cheatsheet
```

## What's in v3.2.5

- **Unified CLI** — One `empathy` command with Rich output
- **Dev Container** — Clone → Open in VS Code → Start coding
- **Python 3.10-3.13** — Full test matrix across all versions
- **Smart Router** — Natural language wizard dispatch
- **Memory Graph** — Cross-wizard knowledge sharing

## Resources

- [GitHub](https://github.com/Smart-AI-Memory/empathy-framework)
- [Documentation](https://smartaimemory.com/framework-docs/)
- [PyPI](https://pypi.org/project/empathy-framework/)

---

*What would you build with an AI that remembers—and costs 80% less?*
