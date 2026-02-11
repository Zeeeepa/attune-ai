# Routing Accuracy Report — attune-ai Plugin

**Date:** 2026-02-10
**Plugin Version:** 5.3.0
**Evaluator:** Automated skill analysis

---

## Methodology

Each scenario represents a natural language input from a user invoking `/attune` or interacting with the plugin. The "Expected Route" is derived from PLUGIN_DEVELOPMENT_PLAN.md Task 3.1. The "Actual Route" is determined by matching against:

1. `/attune` command shortcut table and execution instructions
2. Natural language routing patterns in `commands/attune.md`
3. Skill trigger lists in `memory-and-context/SKILL.md` and `workflow-orchestration/SKILL.md`
4. Setup-guide agent detection steps

---

## Results

### Memory Scenarios

| # | User Input | Expected Route | Actual Route | Match | Notes |
|---|-----------|----------------|--------------|-------|-------|
| 1 | "Store timezone preference" | `memory_store` | `memory_store` via memory-and-context skill (trigger: "store") | PASS | "store" is both a shortcut and a skill trigger |
| 2 | "What context about this project?" | `memory_search` | `memory_search` via memory-and-context skill (trigger: "context") | PASS | "context" trigger routes to skill, which documents `memory_search` for queries |
| 3 | "Reset all memory" | `memory_forget` | `memory_forget` via natural language pattern "delete memory" -> memory_forget | PASS | "memory" + "reset" matches NL pattern; shortcut "forget" also matches |

### Agent/Team Scenarios

| # | User Input | Expected Route | Actual Route | Match | Notes |
|---|-----------|----------------|--------------|-------|-------|
| 4 | "Team to review PR" | `agent_team_create` | workflow-orchestration skill (trigger: "team") -> Agent Team Composition section | PASS | Skill documents SDKAgentTeam pattern; "team" is a trigger |
| 5 | "Set up monitoring" | `agent_team_create` | Ambiguous -- "setup" matches setup-guide agent; no "monitoring" trigger in attune-ai plugin | PARTIAL | Without healthcare context, "monitoring" has no routing target in the base plugin. Routes to setup-guide via "setup" keyword. Correct if intent is agent monitoring, but "set up" is ambiguous |

### Workflow Scenarios

| # | User Input | Expected Route | Actual Route | Match | Notes |
|---|-----------|----------------|--------------|-------|-------|
| 6 | "Prepare for release" | `release_prep` | `release_prep` via NL pattern "release" -> release_prep | PASS | Direct match on "release" keyword |
| 7 | "Generate docs" | `document-gen` | CLI-only workflow via workflow-orchestration skill | PASS | Skill lists "Document Generation" under CLI-Only Workflows; "run" trigger activates skill |
| 8 | "Run dependency check" | `dependency-check` | CLI-only workflow via workflow-orchestration skill (trigger: "run") | PASS | Listed under CLI-Only Workflows section |

### Tier Routing Scenarios

| # | User Input | Expected Route | Actual Route | Match | Notes |
|---|-----------|----------------|--------------|-------|-------|
| 9 | "Classify this error" | Haiku (triage) | workflow-orchestration skill -> Progressive Tier Routing: Haiku for classification | PASS | Tier routing table explicitly lists "Classification, triage" under Haiku |
| 10 | "Analyze 12 modules" | Sonnet -> Opus | workflow-orchestration skill -> Sonnet for structured analysis, escalate to Opus if architectural reasoning needed | PASS | Tier escalation table: multi-file analysis -> Sonnet, complex coordination -> Opus |

### Meta Scenarios

| # | User Input | Expected Route | Actual Route | Match | Notes |
|---|-----------|----------------|--------------|-------|-------|
| 11 | "Configure Redis" | setup-guide agent | setup-guide agent via NL pattern "redis" -> setup-guide agent | PASS | Direct keyword match in attune.md routing table |
| 12 | "What version?" | version check | version check via NL pattern "version" -> version check | PASS | Direct keyword match in attune.md routing table |

### Additional Scenarios

| # | User Input | Expected Route | Actual Route | Match | Notes |
|---|-----------|----------------|--------------|-------|-------|
| 13 | "Remember my code style" | CLAUDE.md (native) | memory-and-context skill -> Layer Positioning table recommends CLAUDE.md | PASS | Skill explicitly documents this in the "When to Use" decision table |
| 14 | "Set empathy to maximum" | `empathy_set_level(5)` | `empathy_set_level` via NL pattern "empathy" + "level" | PASS | Skill documents levels 1-5 correctly; shortcut `/attune empathy` also matches |

---

## Summary

| Category | Scenarios | Passed | Partial | Failed |
|----------|-----------|--------|---------|--------|
| Memory | 3 | 3 | 0 | 0 |
| Agent/Team | 2 | 1 | 1 | 0 |
| Workflow | 3 | 3 | 0 | 0 |
| Tier Routing | 2 | 2 | 0 | 0 |
| Meta | 2 | 2 | 0 | 0 |
| Additional | 2 | 2 | 0 | 0 |
| **Total** | **14** | **13** | **1** | **0** |

**Accuracy: 93% (13/14 full pass, 1 partial)**

Target was 80%. Result exceeds target.

---

## Partial Match Analysis

### Scenario 5: "Set up monitoring"

**Issue:** "Set up monitoring" is ambiguous in the base attune-ai plugin. The word "setup" routes to the setup-guide agent, but "monitoring" has no routing target in the base plugin (monitoring is a healthcare-cds concept). A user in the base plugin context asking to "set up monitoring" would be routed to the setup-guide, which is a reasonable fallback but not the intended agent_team_create route.

**Proposed Improvement:** Add "monitoring" as a trigger for the workflow-orchestration skill, routing to the Agent Team Composition section. This would make the skill ask: "What kind of monitoring? (Agent dashboard status / Custom agent team / Healthcare patient monitoring)". The first two options stay in the base plugin; the third redirects to healthcare-cds.

---

## Routing Coverage Gaps

1. **No "monitoring" keyword in base plugin** -- Addressed above.
2. **CLI-only workflows have no MCP tool** -- Document Generation, Refactor Planning, Research Synthesis, Dependency Check, PR Review, and SEO Optimization are CLI-only. The skill correctly identifies them as CLI-only and provides the command, but users expecting MCP tool execution will need the CLI.
3. **Ambiguous "run" keyword** -- "run" is a workflow-orchestration trigger but also appears in common developer speech ("run tests", "run the build"). The Socratic discovery step mitigates this by asking what the user wants to run.
