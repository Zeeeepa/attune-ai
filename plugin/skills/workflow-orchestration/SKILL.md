---
name: workflow-orchestration
description: "Multi-agent workflow composition, execution, and progressive tier routing"
triggers:
  - workflow
  - run
  - execute
  - agent
  - team
  - orchestrate
  - automate
  - pipeline
  - release
  - security
  - review
  - test
---

## Socratic Routing

Do NOT present a menu of 32+ workflows. Instead, use progressive discovery:

1. **Ask**: "What are you trying to accomplish?"
2. **Narrow**: Based on response, ask about specific aspects
3. **Execute**: Route to the appropriate MCP tool or CLI command

This approach avoids overwhelming the user while ensuring they reach the right workflow.

## Workflow Categories

### Security and Quality

| Workflow | MCP Tool | Description |
|----------|----------|-------------|
| Security Audit | security_audit | Vulnerability scanning, dangerous patterns, security issues |
| Bug Prediction | bug_predict | Pattern analysis and potential bug detection |
| Code Review | code_review | Comprehensive code quality analysis |

### Testing

| Workflow | MCP Tool | Description |
|----------|----------|-------------|
| Test Generation | test_generation | Generate behavioral tests with Given/When/Then structure |

### Performance

| Workflow | MCP Tool | Description |
|----------|----------|-------------|
| Performance Audit | performance_audit | Bottleneck detection, memory leaks, optimization opportunities |

### Release

| Workflow | MCP Tool | Description |
|----------|----------|-------------|
| Release Preparation | release_prep | Health checks, security, changelog, release recommendation |

### Utility

| Workflow | MCP Tool | Description |
|----------|----------|-------------|
| Auth Status | auth_status | Authentication strategy status and tier info |
| Auth Recommend | auth_recommend | Per-file authentication mode recommendation |
| Telemetry Stats | telemetry_stats | Cost savings, cache hit rates, performance metrics |
| Dashboard Status | dashboard_status | Active agents, pending approvals, recent signals |

### CLI-Only Workflows

These workflows are available through the attune CLI but not yet exposed as MCP tools:

- **Document Generation** -- `attune workflow run document-gen`
- **Refactor Planning** -- `attune workflow run refactor-plan`
- **Research Synthesis** -- `attune workflow run research-synthesis`
- **Dependency Check** -- `attune workflow run dependency-check`
- **PR Review** -- `attune workflow run pr-review`
- **SEO Optimization** -- `attune workflow run seo-optimization`

## Progressive Tier Routing

Start at the cheapest appropriate tier and escalate based on complexity:

| Start Tier | Escalate To | When |
|------------|-------------|------|
| Haiku | Sonnet | Error classification unclear, multi-file analysis needed |
| Sonnet | Opus | Architectural reasoning required, complex agent coordination |

**Decision framework:**

- **Haiku**: Classification, triage, high-volume routing, simple threshold checks
- **Sonnet**: Structured analysis, coding tasks, daily development work
- **Opus**: Deep reasoning, complex multi-agent coordination, enterprise research

## Agent Team Composition

For complex tasks requiring multiple perspectives, compose agent teams:

1. **Define roles**: Each agent has a specific responsibility (security, testing, docs, versioning)
2. **Assign tools**: Each agent accesses relevant MCP tools
3. **Set coordination**: Agents share findings through memory_store/memory_retrieve
4. **Run sequentially or parallel**: Based on dependency graph

**Reference pattern -- Release Prep Team:**

- Security Agent: Runs security_audit, reports vulnerabilities
- Testing Agent: Runs test_generation, checks coverage
- Docs Agent: Verifies changelog and documentation
- Version Agent: Validates version bumps and compatibility

## Custom Workflow Creation

Compose new workflows from existing building blocks:

1. Identify the workflow category and pattern
2. Use workflow mixins (execution, cost tracking, state management, telemetry)
3. Register with the plugin system
4. Expose via MCP tool if needed

## Routing Examples

| User Says | Route To |
|-----------|----------|
| "Prepare a release" | Ask about scope, then release_prep |
| "Review this code for security" | security_audit (start Haiku for triage) |
| "Generate tests for this module" | test_generation |
| "Check performance" | performance_audit |
| "What's my cost usage?" | telemetry_stats |
| "Build me an agent team" | Guide through team composition |
| "Run all quality checks" | Compose: security_audit + code_review + bug_predict |
