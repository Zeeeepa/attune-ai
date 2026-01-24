---
name: utilities
description: Utility tools hub - project init, dependencies, profiling
category: hub
aliases: [util, utils]
tags: [utilities, setup, dependencies, profiling, hub]
version: "1.0"
---

# Utilities

Project setup, dependency management, and profiling tools.

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

## Routing

Based on selection:

| Selection | Command | Description |
|-----------|---------|-------------|
| Initialize project | `/init` | Create config, env template, storage dirs |
| Dependency audit | `/deps` | Security, outdated, license compliance |
| Performance profiling | `/profile` | CPU and memory profiling |

## Quick Access

- `/init` - Initialize new project
- `/deps` - Run dependency audit
- `/profile` - Profile performance

## When to Use Each

**Use `/init` when:**

- Starting a new project
- Adding Empathy Framework to existing project
- Resetting configuration

**Use `/deps` when:**

- Before releases
- After adding dependencies
- Regular security audits
- CI/CD pipeline checks

**Use `/profile` when:**

- Code is running slow
- Optimizing hot paths
- Memory usage is high
- Before/after optimization comparison
