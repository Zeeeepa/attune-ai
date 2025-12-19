# Twitter/X Thread - Ready to Post

Copy each numbered item as a separate tweet.

---

**1/8**
What if Claude remembered your preferences across sessions—and cost 80% less?

Just shipped empathy-framework v2.3 with smart model routing.

pip install empathy-framework

🧵

---

**2/8**
The problem: Every Claude conversation starts fresh.

Tell it you prefer concise code? Forgotten next session.

And you're paying Opus prices for simple tasks.

---

**3/8**
The fix - persistent memory:

```python
from empathy_llm_toolkit import EmpathyLLM

llm = EmpathyLLM(
    provider="anthropic",
    memory_enabled=True
)

await llm.interact(
    user_id="dev_123",
    user_input="I prefer Python with type hints"
)
```

That preference now survives.

---

**4/8**
NEW in v2.3 - ModelRouter:

```python
llm = EmpathyLLM(
    provider="anthropic",
    enable_model_routing=True
)

# Summarize → Haiku ($0.25/M)
# Code gen → Sonnet ($3/M)
# Architecture → Opus ($15/M)
```

Real savings: $4.05 → $0.83 per task (80%)

---

**5/8**
It tracks:
→ User preferences
→ Project context
→ Conversation patterns

Each user gets isolated memory. Privacy controls built in.

---

**6/8**
Five empathy levels:

1. Reactive (standard)
2. Informed (uses preferences)
3. Predictive (anticipates needs)
4. Anticipatory (proactive suggestions)
5. Collaborative (full partnership)

---

**7/8**
Now on PyPI:

pip install empathy-framework

GitHub: github.com/Smart-AI-Memory/empathy-framework

Docs: smartaimemory.com/docs

---

**8/8**
What would you build with an AI that remembers you—and costs 80% less?

---

# Alt: Shorter 4-tweet version

**1/4**
What if Claude remembered you across sessions—and cost 80% less?

Just shipped empathy-framework v2.3 with smart model routing.

pip install empathy-framework

---

**2/4**
```python
llm = EmpathyLLM(
    provider="anthropic",
    memory_enabled=True,
    enable_model_routing=True  # NEW!
)
```

Memory persists. Costs drop 80%.

---

**3/4**
Features:
→ Cross-session persistence
→ Per-user isolation
→ Privacy controls
→ Five "empathy levels"
→ NEW: Smart model routing (Haiku/Sonnet/Opus auto-selection)

---

**4/4**
GitHub: github.com/Smart-AI-Memory/empathy-framework

What would you build with an AI that remembers—and costs 80% less?
