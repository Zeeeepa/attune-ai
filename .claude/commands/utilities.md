---
name: utilities
description: Utility tools hub - project init, dependencies, profiling
category: hub
aliases: [util, utils]
tags: [utilities, setup, dependencies, profiling, hub]
version: "2.0"
---

# Utilities

**Aliases:** `/util`, `/utils`

Project setup, dependency management, and profiling tools.

## Quick Examples

```bash
/utilities                # Interactive menu
/utilities "init"         # Initialize project
/utilities "check deps"   # Audit dependencies
```

## Discovery

```yaml
Question:
  header: "Task"
  question: "What utility do you need?"
  options:
    - label: "Initialize project"
      description: "Set up Empathy Framework configuration for a project"
    - label: "Dependency audit"
      description: "Check for security vulnerabilities and outdated packages"
    - label: "Performance profiling"
      description: "Profile code to find bottlenecks"
```

---

## Initialize Project

Set up Empathy Framework configuration for a project.

**I will:**

1. Create `.claude/` directory structure:
   - `commands/` - Custom commands
   - `rules/` - Project rules
2. Generate configuration files:
   - `empathy.config.yml`
   - `.env.example`
3. Set up storage directories
4. Initialize pattern storage
5. Create starter templates

**Created structure:**

```text
.claude/
├── commands/      # Custom slash commands
├── rules/         # Project-specific rules
├── CLAUDE.md      # Project instructions
└── compact-state.md
```

---

## Dependency Audit

Check for security vulnerabilities and outdated packages.

**I will:**

1. Scan for security vulnerabilities:
   - `pip-audit` / `safety` for Python
   - `npm audit` for JavaScript
2. Check for outdated packages
3. Review license compliance
4. Report findings with:
   - Severity level
   - Affected package
   - Fix recommendation

**Output includes:**

| Category       | Tool        |
| -------------- | ----------- |
| Vulnerabilities| pip-audit   |
| Outdated       | pip list -o |
| Licenses       | pip-licenses|

---

## Performance Profiling

Profile code to find bottlenecks.

**Tell me:**

- What to profile (script, function, endpoint)
- Concern (CPU, memory, or both)

**I will:**

1. Set up profiling:
   - `cProfile` for CPU time
   - `memory_profiler` for memory
2. Run the target code
3. Analyze results:
   - Identify hot spots
   - Find memory leaks
   - Measure timing
4. Suggest optimizations

**Profiling output:**

```text
Top 10 by cumulative time:
  function_name    calls    tottime    cumtime
  slow_func        1000     5.23s      8.45s
  ...
```

---

## When NOT to Use This Hub

| If you need...    | Use instead |
| ----------------- | ----------- |
| Run tests         | `/testing`  |
| Debug issues      | `/dev`      |
| Security scan     | `/release`  |
| Manage context    | `/context`  |

## Related Hubs

- `/release` - Security scanning for releases
- `/testing` - Run benchmarks
- `/dev` - Development tasks
