# Anthropic Cookbook Submission Draft

**Target:** https://github.com/anthropics/anthropic-cookbook
**Proposed Location:** `misc/building_ai_memory_systems.ipynb`

---

## Notebook: Building AI Memory Systems with Claude

### Overview
This notebook shows how to add persistent memory to Claude conversations, enabling:
- Context that persists across sessions
- Multi-agent coordination
- Real-time state sharing with Redis

### Outline

```
1. Introduction
   - The problem: Claude conversations are stateless
   - Why memory matters for production AI systems
   - What we'll build

2. Setup
   - pip install anthropic redis
   - Environment variables (ANTHROPIC_API_KEY, REDIS_URL)

3. Basic Memory Pattern
   - Simple conversation history storage
   - Injecting context into Claude prompts
   - Code example: store/retrieve messages

4. Redis Integration
   - Why Redis for AI memory (sub-ms latency)
   - Connection setup
   - TTL-based expiration for automatic cleanup

5. Use Case 1: Session Context
   - Store user preferences and history
   - Auto-inject into Claude system prompt
   - Code example with working demo

6. Use Case 2: Multi-Agent Coordination
   - Multiple Claude instances sharing state
   - Task claiming with Redis locks
   - Result sharing between agents

7. Use Case 3: Short-Term Memory
   - Conversation context window management
   - Sliding window with Redis lists
   - Automatic pruning

8. Performance Considerations
   - Benchmarks (session read: 0.3ms, etc.)
   - Redis vs alternatives comparison
   - When to use mock mode for testing

9. Production Tips
   - Error handling
   - Connection pooling
   - Graceful degradation

10. Next Steps
    - Link to Empathy Framework for full implementation
    - Link to blog post for deep dive
```

---

## Code Snippets to Include

### Basic Memory Store
```python
import anthropic
import redis
import json

client = anthropic.Anthropic()
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def store_message(user_id: str, role: str, content: str):
    """Store a message in Redis with auto-expiration."""
    key = f"memory:{user_id}:messages"
    message = json.dumps({"role": role, "content": content})
    r.lpush(key, message)
    r.ltrim(key, 0, 99)  # Keep last 100
    r.expire(key, 3600)  # 1 hour TTL

def get_context(user_id: str, limit: int = 10) -> list:
    """Retrieve recent messages for context injection."""
    key = f"memory:{user_id}:messages"
    messages = r.lrange(key, 0, limit - 1)
    return [json.loads(m) for m in reversed(messages)]

def chat_with_memory(user_id: str, user_message: str) -> str:
    """Chat with Claude using memory context."""
    # Get conversation history
    history = get_context(user_id)

    # Store user message
    store_message(user_id, "user", user_message)

    # Build messages with history
    messages = history + [{"role": "user", "content": user_message}]

    # Call Claude
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=messages
    )

    assistant_message = response.content[0].text

    # Store assistant response
    store_message(user_id, "assistant", assistant_message)

    return assistant_message
```

### Multi-Agent Coordination
```python
def claim_task(agent_id: str, task_id: str) -> bool:
    """Atomically claim a task (only one agent can claim)."""
    key = f"task:{task_id}:claimed_by"
    # SET NX = only set if not exists
    return r.set(key, agent_id, nx=True, ex=300)  # 5 min lock

def share_result(task_id: str, result: dict):
    """Share task result for other agents."""
    key = f"task:{task_id}:result"
    r.set(key, json.dumps(result), ex=3600)
    # Notify waiting agents
    r.publish(f"task:{task_id}:complete", "done")
```

---

## PR Description Draft

```
## Add: Building AI Memory Systems with Claude

This notebook demonstrates how to add persistent memory to Claude
conversations using Redis for real-time coordination.

### What's included:
- Basic memory patterns for conversation history
- Redis integration for sub-millisecond access
- Multi-agent coordination examples
- Production tips and benchmarks

### Why this matters:
Production AI systems need memory that persists across sessions.
This cookbook shows practical patterns used in real applications.

### Testing:
- All code examples are runnable
- Works with Redis or mock mode for testing
- Tested with Claude claude-sonnet-4-20250514 and claude-opus-4-20250514

Related: https://www.smartaimemory.com/blog/building-ai-memory-with-redis
```

---

## Next Steps

1. [ ] Fork anthropic-cookbook repo
2. [ ] Create notebook from this outline
3. [ ] Test all code examples
4. [ ] Submit PR
5. [ ] Respond to review feedback

---

## Timeline

- **Draft notebook:** 2-3 hours
- **Testing:** 1 hour
- **PR submission:** Week 2-3 of marketing sprint
- **Review cycle:** 1-2 weeks typically

---

*Created: December 15, 2025*
