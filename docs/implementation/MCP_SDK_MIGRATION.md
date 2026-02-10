# MCP SDK Migration Evaluation

**Task:** M5 from Anthropic Compliance Plan
**Status:** Evaluated
**Date:** 2026-02-09

---

## Current State

The project uses a custom MCP server (`src/attune/mcp/server.py`, ~614 lines) implementing JSON-RPC 2.0 over stdio transport manually. It registers tools, resources, and prompts with hand-built schemas and handles the protocol loop directly.

## Official MCP Python SDK

The official `mcp` package (`pip install mcp`) provides:

- Correct JSON-RPC 2.0 protocol handling
- Built-in tool/resource/prompt registration with decorators
- SSE and stdio transports out of the box
- Type-safe request/response handling via Pydantic models
- Automatic schema generation from type hints

## Migration Assessment

### Effort Estimate

- **1-2 days** for core migration
- **0.5 day** for testing and validation
- Total: **~2-3 days**

### What Changes

| Component | Current | After Migration |
|-----------|---------|----------------|
| Protocol handling | Custom JSON-RPC loop (~150 lines) | SDK handles automatically |
| Tool registration | Dict-based schemas (~200 lines) | Decorator-based with type hints |
| Transport | Custom stdio reader | `mcp.server.stdio` |
| Error handling | Manual JSON-RPC error codes | SDK error types |

### What Stays the Same

- Tool implementation logic (workflow calls)
- Resource content (project structure, config)
- Prompt definitions (content unchanged)

### Breaking Changes

- None for end users (MCP protocol is the same)
- Internal: tool handler signatures change to use SDK types
- Config: `.mcp.json` / `.claude/mcp.json` unchanged

### Pros

1. **Reduced maintenance** - ~200 lines of protocol code eliminated
2. **Protocol correctness** - SDK handles edge cases (cancellation, progress)
3. **Future-proof** - Automatic support for new MCP features
4. **Type safety** - Pydantic models for all request/response types

### Cons

1. **New dependency** - Adds `mcp` package (and its transitive deps)
2. **Migration risk** - Could break existing tool integrations if done incorrectly
3. **Learning curve** - Team needs to learn SDK patterns

## Recommendation

**Proceed as a separate PR** after the current compliance work is complete. The custom implementation works but requires manual updates for any MCP protocol changes. Migration is straightforward but should not be bundled with other changes.

### Migration Path

1. Add `mcp>=1.0.0` to optional dependencies
2. Create `src/attune/mcp/server_v2.py` alongside existing server
3. Migrate tools one at a time, testing each
4. Swap entry point when all tools pass
5. Remove old server code
