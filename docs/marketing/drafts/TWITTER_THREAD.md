# Twitter/X Thread - Ready to Post

Copy each numbered item as a separate tweet.

---

**1/7**
What if Claude remembered your preferences across sessions?

I built @empathy_framework to give LLMs persistent memory.

pip install empathy-framework

🧵

---

**2/7**
The problem: Every Claude conversation starts fresh.

Tell it you prefer concise code? Forgotten next session.

Working on a project? Context lost.

---

**3/7**
The fix:

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

**4/7**
It tracks:
→ User preferences
→ Project context
→ Conversation patterns

Each user gets isolated memory. Privacy controls built in.

---

**5/7**
Five empathy levels:

1. Reactive (standard)
2. Informed (uses preferences)
3. Predictive (anticipates needs)
4. Anticipatory (proactive suggestions)
5. Collaborative (full partnership)

---

**6/7**
Now on PyPI:

pip install empathy-framework

GitHub: github.com/Smart-AI-Memory/empathy-framework

Docs: smartaimemory.com/docs

---

**7/7**
Working on getting this into the @AnthropicAI cookbook.

What would you build with an AI that remembers you?

---

# Alt: Shorter 4-tweet version

**1/4**
What if Claude remembered you across sessions?

Built empathy-framework to add persistent memory to LLMs.

pip install empathy-framework

---

**2/4**
```python
llm = EmpathyLLM(provider="anthropic", memory_enabled=True)

await llm.interact(
    user_id="you",
    user_input="I prefer concise answers"
)
```

Next session? Still remembered.

---

**3/4**
Features:
→ Cross-session persistence
→ Per-user isolation
→ Privacy controls
→ Five "empathy levels"

---

**4/4**
GitHub: github.com/Smart-AI-Memory/empathy-framework

What would you build with an AI that remembers?
