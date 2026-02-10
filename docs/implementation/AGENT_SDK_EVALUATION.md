# Anthropic Agent SDK Evaluation

**Task:** M7 from Anthropic Compliance Plan
**Status:** Evaluated
**Date:** 2026-02-09

---

## Current State

The project has a custom multi-agent orchestration layer in `src/attune/orchestration/` with:

- Agent creation and lifecycle management
- 6 coordination patterns (heartbeats, signals, events, approvals, quality feedback, demo mode)
- Tier-based model selection (cheap/capable/premium)
- Quality gates with confidence thresholds
- Pattern learning and memory integration

Additionally, `src/attune/agents/healthcare/` implements domain-specific agents:

- ECG Analyzer Agent
- Clinical Reasoning Agent
- CDSTeam orchestration (gather → reason two-phase execution)

## Anthropic Agent SDK

The `claude-agent-sdk` package provides:

- Standardized agent creation with tool use
- Built-in conversation management
- Guardrails and safety patterns
- Multi-agent handoff protocols
- Streaming support

## Compatibility Assessment

| Feature | Current Implementation | Agent SDK |
|---------|----------------------|-----------|
| Agent creation | Custom `AgentFactory` | SDK `Agent` class |
| Tool registration | Manual dict schemas | SDK tool decorators |
| Multi-agent coordination | Custom 6-pattern system | SDK handoff protocol |
| Model selection | Tier routing (cheap/capable/premium) | Per-agent model config |
| Quality gates | Custom confidence thresholds | SDK guardrails |
| Memory/learning | Custom pattern library | Not built-in |
| Healthcare domain | Custom CDS agents | Generic agent base |

## Analysis

### Where the SDK Helps

1. **Simpler agent creation** - Reduces boilerplate for basic agents
2. **Standardized tool use** - Better interop with Claude Code
3. **Built-in safety** - Guardrails out of the box

### Where the SDK Doesn't Fit

1. **Custom coordination patterns** - The 6 patterns (heartbeats, signals, events, approvals, quality feedback, demo mode) are domain-specific and not available in the SDK
2. **Tier-based routing** - The SDK doesn't provide automatic cost-based model selection
3. **Pattern learning** - Memory integration and pattern library are project-specific
4. **Healthcare agents** - CDS team orchestration has domain-specific two-phase execution that doesn't map to SDK patterns

### Migration Effort

- **High effort** (1-2 weeks) for full migration
- **Medium risk** of regressions in coordination patterns
- **Partial adoption** possible - use SDK for new simple agents while keeping custom orchestration

## Recommendation

**Partial adoption for new agents; keep custom orchestration.**

The project's multi-agent system is significantly more sophisticated than what the Agent SDK provides out of the box. The 6 coordination patterns, tier-based routing, and healthcare-specific orchestration are core differentiators that would be lost or require significant workarounds with the SDK.

### Recommended Path

1. Use Agent SDK for **new, simple agents** that don't need custom coordination
2. Keep `src/attune/orchestration/` for complex multi-agent workflows
3. Consider wrapping Agent SDK agents in the existing tier-routing system
4. Revisit when the Agent SDK adds more orchestration primitives
