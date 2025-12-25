# Reddit Posts - Ready to Copy/Paste (v3.2.5)

---

## r/ClaudeAI

**Title:** I built persistent memory for Claude that survives across sessions (+ 80% cost savings)

**Body:**

Every Claude conversation starts fresh. I wanted my dev assistant to remember my preferences, so I built [Empathy Framework](https://github.com/Smart-AI-Memory/empathy-framework).

**The core idea:**

```python
from empathy_llm_toolkit import EmpathyLLM

llm = EmpathyLLM(provider="anthropic", memory_enabled=True)

# This preference persists forever
await llm.interact(user_id="me", user_input="I prefer concise Python with type hints")
```

Next session—even days later—Claude remembers.

**Why I actually use it:**

1. **80% cost savings** - Smart routing sends simple tasks to Haiku, complex ones to Opus
   - Before: $4.05/task (all Opus)
   - After: $0.83/task (tiered)

2. **Bug memory** - My debugging wizard remembers every fix. "This looks like bug #247 from 3 months ago—here's what worked."

3. **Provider freedom** - Works with Claude, GPT, Ollama, or hybrid. Switch with one command.

**Quick start:**

```bash
pip install empathy-framework
empathy provider set anthropic
```

Happy to answer questions about the implementation.

---

## r/Python

**Title:** empathy-framework: Persistent LLM memory + smart routing (80% cost savings)

**Body:**

Just released v3.2.5 of [empathy-framework](https://pypi.org/project/empathy-framework/) - adds persistent memory to LLM interactions with smart cost optimization.

**What it does:**

```python
from empathy_llm_toolkit import EmpathyLLM

llm = EmpathyLLM(
    provider="anthropic",  # or "openai", "ollama", "hybrid"
    memory_enabled=True,
    enable_model_routing=True
)

# Memory survives across sessions
await llm.interact(user_id="user123", user_input="I prefer async/await patterns")

# Smart routing picks the right model
await llm.interact(user_id="user123", user_input="Summarize this", task_type="summarize")  # → Haiku
await llm.interact(user_id="user123", user_input="Design the architecture", task_type="coordinate")  # → Opus
```

**Why I built it:**

1. **Cost** - Was spending too much on Opus for simple tasks. Smart routing cut costs 80%.
2. **Context** - Tired of re-explaining my preferences every session.
3. **Flexibility** - Didn't want to be locked into one provider.

**New in v3.2:**

- Unified CLI: `empathy` command with Rich output
- Dev Container: Clone → Open in VS Code → Start coding
- Python 3.10-3.13 support

**CLI:**

```bash
empathy provider status        # See available providers
empathy provider set hybrid    # Use best of each
empathy cheatsheet            # Quick reference
```

GitHub: https://github.com/Smart-AI-Memory/empathy-framework

What use cases would you want persistent memory for?

---

## r/LocalLLaMA

**Title:** Cross-session memory for local LLMs - native Ollama support (v3.2.5)

**Body:**

Built [Empathy Framework](https://github.com/Smart-AI-Memory/empathy-framework) to give LLMs persistent memory. v3.2.5 has native Ollama support.

**Quick example:**

```python
from empathy_llm_toolkit import EmpathyLLM

llm = EmpathyLLM(provider="ollama", memory_enabled=True)

# Preferences persist across sessions
await llm.interact(user_id="user", user_input="I use vim keybindings")
```

**Multi-provider architecture:**

- **Ollama** — Llama 3.2/3.1 (local)
- **Anthropic** — Claude (Haiku/Sonnet/Opus)
- **OpenAI** — GPT (4o-mini/4o/o1)
- **Hybrid** — Best of each provider per tier

Auto-detects running Ollama instance and available API keys.

**CLI:**

```bash
empathy provider status       # Shows what's available
empathy provider set ollama   # Use local only
empathy provider set hybrid   # Mix local + cloud
```

**Smart tier routing for local:**

- Cheap tier: Llama 3.2 (3B)
- Capable tier: Llama 3.1 (8B)
- Premium tier: Llama 3.1 (70B)

Use case: I use Ollama for sensitive code, fall back to Claude for complex architecture decisions.

Feedback welcome from the local LLM community.

---

## r/MachineLearning (if appropriate)

**Title:** [P] Empathy Framework - Persistent memory layer for LLMs with smart model routing

**Body:**

Open source Python framework that adds persistent memory to LLM interactions.

**Problem:** LLM APIs are stateless. Each request starts fresh.

**Solution:** Memory layer that persists user context across sessions, with smart routing to optimize costs.

**Key features:**

1. **Cross-session memory** - Preferences, patterns, and context survive restarts
2. **Smart routing** - Automatically picks Haiku/Sonnet/Opus based on task complexity (80% cost reduction)
3. **Provider-agnostic** - Works with Anthropic, OpenAI, Ollama, or hybrid

**Architecture:**

- Memory stored per-user with isolation
- Pattern detection for proactive suggestions
- Natural language routing ("Fix security in auth.py" → SecurityWizard)

GitHub: https://github.com/Smart-AI-Memory/empathy-framework
PyPI: `pip install empathy-framework`

Looking for feedback on the memory architecture approach.
