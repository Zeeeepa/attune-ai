---
description: Commands System: Load, parse, and execute markdown-based commands with framework integration.
---

# Commands System

Load, parse, and execute markdown-based commands with framework integration.

## Overview

The commands system provides:

- **Markdown Commands**: Define commands as simple markdown files
- **YAML Frontmatter**: Optional metadata for configuration
- **Registry**: Central management of all commands
- **Hook Integration**: Fire hooks before/after commands
- **Learning Integration**: Apply patterns to command execution

## Command Location

Commands are stored in `.claude/commands/`:

```
.claude/commands/
  commit.md
  test.md
  debug.md
  compact.md    # New in 4.7.0
  patterns.md   # New in 4.7.0
  evaluate.md   # New in 4.7.0
  ...
```

## Command Format

### With YAML Frontmatter (Recommended)

```markdown
---
name: compact
description: Strategic context compaction
category: context
aliases: [comp, save-state]
hooks:
  pre: PreCompact
  post: PostCompact
requires_user_id: true
tags: [context, memory, state]
---

## Overview

This command performs context compaction...

## Execution Steps

1. Save current state
2. Clear context
3. Restore essential info
```

### Without Frontmatter (Legacy)

```markdown
Create a git commit - Follow conventional commit format.

## Execution Steps

1. Check git status
2. Stage files
3. Commit with message
```

The name is inferred from the filename.

## Frontmatter Options

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Command identifier (required with frontmatter) |
| `description` | string | Short description |
| `category` | string | workflow, git, test, docs, security, performance, learning, context, utility |
| `aliases` | list | Alternative names |
| `hooks` | dict | `{pre: EventName, post: EventName}` |
| `requires_user_id` | bool | Needs user context |
| `requires_context` | bool | Needs collaboration state |
| `tags` | list | Searchable tags |
| `version` | string | Command version |

## Loading Commands

### From Directory

```python
from attune_llm.commands import CommandRegistry

registry = CommandRegistry.get_instance()
count = registry.load_from_directory(".claude/commands/")
print(f"Loaded {count} commands")
```

### Default Commands

```python
# Loads from .claude/commands/ in project root
count = registry.load_default_commands()
```

### Single File

```python
config = registry.load_from_file(".claude/commands/custom.md")
```

## Using Commands

### Get by Name or Alias

```python
# By name
commit = registry.get("commit")

# By alias
compact = registry.get("comp")  # Resolves to "compact"

# Required (raises KeyError if not found)
cmd = registry.get_required("test")
```

### List and Search

```python
# All commands
for name in registry.list_commands():
    print(name)

# By category
git_cmds = registry.get_by_category(CommandCategory.GIT)

# By tag
learning_cmds = registry.get_by_tag("learning")

# Search
results = registry.search("test")
```

### Help Text

```python
# Quick list
print(registry.format_help())

# Full command help
cmd = registry.get("compact")
print(cmd.format_full_help())
```

## Command Execution

Commands are executed through Claude Code, but the framework provides context:

```python
from attune_llm.commands import CommandContext, CommandExecutor

# Create context with integrations
ctx = CommandContext(
    user_id="user123",
    hook_registry=hooks,
    context_manager=context_mgr,
    learning_storage=storage,
)

# Execute command
executor = CommandExecutor(ctx)
result = executor.execute(compact_command)

print(f"Success: {result.success}")
print(f"Hooks fired: {result.hooks_fired}")
```

## Hook Integration

Commands can fire hooks before and after execution:

```yaml
---
name: compact
hooks:
  pre: PreCompact   # Fires HookEvent.PRE_COMPACT
  post: PostCompact # Fires HookEvent.POST_COMPACT
---
```

The `CommandExecutor` handles hook firing:

```python
# Automatic hook firing
result = executor.execute(command)
# PreCompact fires -> command body returned -> PostCompact fires
```

## Learning Integration

Commands can access learned patterns:

```python
ctx = CommandContext(
    user_id="user123",
    learning_storage=storage,
)

# Get relevant patterns
patterns_text = ctx.get_patterns_for_context(max_patterns=5)

# Search patterns
relevant = ctx.search_patterns("authentication")

# Include in command context
prepared = executor.prepare_command(command)
# prepared["patterns_context"] contains formatted patterns
```

## New Commands in 4.7.0

### /compact

Strategic context compaction:

```
/compact
```

- Preserves trust level and empathy calibration
- Saves detected patterns
- Creates SBAR handoff for work continuity
- Auto-restores in next session

### /patterns

View and manage learned patterns:

```
/patterns                    # Summary
/patterns search async       # Search
/patterns category preference # By category
```

### /evaluate

Evaluate session for learning:

```
/evaluate           # Extract patterns
/evaluate --dry-run # Preview only
/evaluate --force   # Force extraction
```

## Command Categories

| Category | Description | Examples |
|----------|-------------|----------|
| `workflow` | Multi-step workflows | debug, release-prep |
| `git` | Git operations | commit, pr, review-pr |
| `test` | Testing | test, test-coverage |
| `docs` | Documentation | manage-docs, explain |
| `security` | Security analysis | security-scan |
| `performance` | Performance tools | benchmark, profile |
| `learning` | Pattern learning | patterns, evaluate |
| `context` | Context management | compact |
| `utility` | General utilities | status, init |

## Validation

Validate command files:

```python
from attune_llm.commands import CommandLoader

loader = CommandLoader()
errors = loader.validate_directory(".claude/commands/")

for file_path, file_errors in errors.items():
    print(f"{file_path}:")
    for error in file_errors:
        print(f"  - {error}")
```

## Creating Custom Commands

1. Create markdown file in `.claude/commands/`:

```markdown
---
name: my-command
description: Does something useful
category: utility
aliases: [mc]
---

## Overview

Describe what this command does.

## Execution Steps

### Step 1: First Action

Instructions for Claude...

### Step 2: Second Action

More instructions...

## Related Commands

- `/other-command` - Related functionality
```

2. Reload registry:

```python
registry.reload()
```

## API Reference

### CommandRegistry

```python
class CommandRegistry:
    @classmethod
    def get_instance() -> CommandRegistry
    @classmethod
    def reset_instance() -> None

    def register(config, overwrite=False) -> None
    def unregister(name) -> bool
    def get(name) -> CommandConfig | None
    def get_required(name) -> CommandConfig
    def has(name) -> bool
    def resolve_alias(name) -> str

    def list_commands() -> list[str]
    def list_aliases() -> dict[str, str]
    def iter_commands() -> Iterator[CommandConfig]

    def load_from_directory(directory, recursive=False, overwrite=False) -> int
    def load_from_file(file_path, overwrite=False) -> CommandConfig
    def load_default_commands(overwrite=False) -> int
    def reload() -> int

    def get_by_category(category) -> list[CommandConfig]
    def get_by_tag(tag) -> list[CommandConfig]
    def search(query) -> list[CommandConfig]

    def format_help() -> str
    def get_summary() -> dict
```

### CommandContext

```python
class CommandContext:
    user_id: str
    hook_registry: HookRegistry | None
    context_manager: ContextManager | None
    learning_storage: LearnedSkillsStorage | None

    def fire_hook(event, context=None) -> list[dict]
    def save_context_state() -> Path | None
    def restore_context_state() -> bool
    def get_patterns_for_context(max_patterns=5) -> str
    def search_patterns(query) -> list
```

### CommandExecutor

```python
class CommandExecutor:
    def __init__(context: CommandContext)

    def execute(command, args=None) -> CommandResult
    def prepare_command(command, args=None) -> dict
```

### CommandConfig

```python
@dataclass
class CommandConfig:
    name: str
    description: str
    body: str
    metadata: CommandMetadata
    source_file: Path | None

    @property
    def aliases() -> list[str]
    @property
    def category() -> CommandCategory
    @property
    def hooks() -> dict[str, str]

    def get_all_names() -> list[str]
    def format_for_display() -> str
    def format_full_help() -> str
```

## See Also

- [Hooks](hooks.md) - Hook system for command events
- [Context Management](context-management.md) - State preservation
- [Continuous Learning](continuous-learning.md) - Pattern extraction
- [Markdown Agents](markdown-agents.md) - Agent definitions
