# Reddit Posts - Ready to Copy/Paste

---

## r/ClaudeAI

**Title:** I built a persistent memory layer for Claude - open source

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

**Features:**
- Cross-session memory persistence
- Per-user isolation
- Privacy controls (clear/forget)
- Five "empathy levels" from reactive to anticipatory

Just hit PyPI: `pip install empathy-framework`

Working on getting it into the Anthropic Cookbook. Happy to answer questions.

---

## r/Python

**Title:** empathy-framework: Add persistent memory to LLMs in Python

**Body:**

Released v2.2.7 of [empathy-framework](https://pypi.org/project/empathy-framework/) - a Python library that adds persistent, cross-session memory to LLM interactions.

```python
from empathy_llm_toolkit import EmpathyLLM

llm = EmpathyLLM(provider="anthropic", memory_enabled=True)

# Memory survives across sessions
await llm.interact(user_id="user123", user_input="Remember I prefer async/await")
```

**Why I built it:**

Most LLM APIs are stateless. Great for simple queries, but if you're building:
- Dev assistants that learn your style
- Customer support with history
- Personal tools that adapt

...you need persistent context.

**Features:**
- Works with Claude, OpenAI, local models
- Per-user memory isolation
- Privacy controls built in
- Async-first design

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
