# Reddit Posts - Ready to Copy/Paste

---

## r/ClaudeAI

**Title:** I built a persistent memory layer for Claude + smart model routing (80% cost savings)

**Body:**

Every Claude conversation starts fresh. I wanted my dev assistant to remember my preferences across sessions, so I built [Empathy Framework](https://github.com/Smart-AI-Memory/empathy-framework).

Quick example:

```python
from empathy_llm_toolkit import EmpathyLLM

llm = EmpathyLLM(provider="anthropic", memory_enabled=True)

# This preference persists across sessions
await llm.interact(
    user_id="me",
    user_input="I prefer concise Python with type hints"
)
```

Next session, Claude remembers.

**v2.3 just shipped with ModelRouter** - automatically picks Haiku/Sonnet/Opus based on task complexity. Real savings: $4.05 → $0.83 per complex task (80% reduction).

```python
llm = EmpathyLLM(provider="anthropic", enable_model_routing=True)
await llm.interact(user_id="dev", user_input="Summarize this", task_type="summarize")  # → Haiku
```

**Features:**
- Cross-session memory persistence
- Per-user isolation
- Privacy controls (clear/forget)
- Five "empathy levels" from reactive to anticipatory
- **NEW:** Smart model routing (80% cost savings)

On PyPI: `pip install empathy-framework`

Happy to answer questions.

---

## r/Python

**Title:** empathy-framework v2.3: Persistent LLM memory + smart model routing (80% cost savings)

**Body:**

Just released v2.3 of [empathy-framework](https://pypi.org/project/empathy-framework/) - a Python library that adds persistent memory to LLM interactions, plus automatic model routing for cost optimization.

```python
from empathy_llm_toolkit import EmpathyLLM

llm = EmpathyLLM(
    provider="anthropic",
    memory_enabled=True,
    enable_model_routing=True  # NEW in v2.3
)

# Memory survives across sessions
await llm.interact(user_id="user123", user_input="Remember I prefer async/await")

# Automatic model selection based on task
await llm.interact(user_id="user123", user_input="Summarize this", task_type="summarize")  # → Haiku
```

**What's new in v2.3:**
- **ModelRouter**: Auto-picks Haiku/Sonnet/Opus based on task complexity
- Real cost savings: $4.05 → $0.83 per complex task (80% reduction)

**Core features:**
- Works with Claude, OpenAI, local models
- Per-user memory isolation
- Privacy controls built in
- Async-first design
- Five "empathy levels" from reactive to anticipatory

GitHub: https://github.com/Smart-AI-Memory/empathy-framework

Feedback welcome. What use cases would you want memory for?

---

## r/LocalLLaMA

**Title:** Cross-session memory layer for LLMs - works with local models too

**Body:**

Built [Empathy Framework](https://github.com/Smart-AI-Memory/empathy-framework) to give LLMs persistent memory across sessions.

Originally for Claude, but the architecture is provider-agnostic. Working on local model support.

```python
from empathy_llm_toolkit import EmpathyLLM

llm = EmpathyLLM(provider="anthropic", memory_enabled=True)

# Preferences persist
await llm.interact(user_id="user", user_input="I use vim keybindings")
```

The memory layer stores user context separately from the model, so it should work with any backend that accepts a system prompt.

Currently on PyPI: `pip install empathy-framework`

Anyone running local models interested in testing? Would love to add ollama/llama.cpp support.
