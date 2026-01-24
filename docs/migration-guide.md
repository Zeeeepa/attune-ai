# Migration Guide: Empathy Framework 4.7.0

> **Attribution**: Version 4.7.0 adds architectural patterns inspired by [everything-claude-code](https://github.com/affaan-m/everything-claude-code) by Affaan Mustafa (MIT License). These complement the Empathy Framework's existing learning capabilities.

## What's New in 4.7.0

| Feature | Description | Source |
|---------|-------------|--------|
| Hook System | Event-driven automation | everything-claude-code |
| Markdown Agents | Portable agent definitions | everything-claude-code |
| Context Management | State preservation through compaction | everything-claude-code |
| Session Learning | Pattern extraction from interactions | everything-claude-code |

**Existing features enhanced** (not replaced): Code inspection learning, memory system, empathy levels.

## Quick Start

### 1. Update

```bash
pip install --upgrade empathy-llm-toolkit>=4.7.0
```

### 2. Configuration (Optional Additions)

```yaml
# empathy.config.yaml - add to existing config
hooks:
  enabled: true

learning:
  enabled: true
  auto_evaluate: true
```

### 3. Verify

```python
from empathy_llm_toolkit.hooks import HookRegistry
from empathy_llm_toolkit.agents_md import AgentRegistry
from empathy_llm_toolkit.context import ContextManager
from empathy_llm_toolkit.learning import SessionEvaluator

print("Migration successful!")
```

## Learning Systems

### Code Inspection Learning (Existing)
- Extracts patterns from code analysis
- Storage: `patterns/inspection/`
- Unchanged in 4.7.0

### Session Learning (New)
- Extracts patterns from user interactions
- Storage: `.empathy/learned_skills/`
- Complements existing system

## New Imports

```python
# Hooks
from empathy_llm_toolkit.hooks import HookRegistry
from empathy_llm_toolkit.hooks.config import HookEvent

# Markdown Agents
from empathy_llm_toolkit.agents_md import AgentRegistry

# Context Management
from empathy_llm_toolkit.context import ContextManager, CompactState

# Session Learning
from empathy_llm_toolkit.learning import SessionEvaluator, PatternExtractor
```

## Directory Structure

```
project/
├── .claude/commands/       # NEW: Slash commands
├── .empathy/
│   ├── compact_states/     # NEW: Context preservation
│   └── learned_skills/     # NEW: Session patterns
├── agents_md/              # NEW: Markdown agents
├── patterns/inspection/    # EXISTING: Code patterns
└── empathy.config.yaml
```

## Backward Compatibility

All existing features continue to work unchanged. New features are additive.

## Full Documentation

- [Hooks](hooks.md)
- [Markdown Agents](markdown-agents.md)
- [Context Management](context-management.md)
- [Continuous Learning](continuous-learning.md)
