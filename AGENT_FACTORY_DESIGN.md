# Agent Factory Feature Design

**Date:** 2026-01-01
**Status:** Design Phase
**Target:** VSCode Extension Integration

---

## Executive Summary

The **Agent Factory** is a guided workflow feature that helps users design, configure, and deploy multi-agent crews for complex development tasks. It combines the power of CrewAI patterns with provider-specific optimizations (Anthropic/OpenAI) while maintaining graceful degradation for all supported LLM providers.

### Key Capabilities

1. **Guided Crew Design** - Socratic questioning to understand user's task and recommend agent configurations
2. **Provider Optimization** - Leverage advanced features (extended thinking, prompt caching, parallel tools)
3. **Cost Transparency** - Real-time cost estimation with tier-based routing
4. **Graceful Fallbacks** - All features work across providers with automatic capability detection
5. **Pattern Learning** - Learn from successful crew configurations to improve recommendations

---

## Core Concepts

### Agent Roles (from CrewAI Research)

```typescript
enum AgentRole {
    COORDINATOR = "coordinator",      // Project management, synthesis
    RESEARCHER = "researcher",         // Information gathering
    WRITER = "writer",                // Content generation
    REVIEWER = "reviewer",            // Quality assurance
    DEBUGGER = "debugger",            // Problem diagnosis
    SECURITY = "security",            // Security analysis
    ARCHITECT = "architect",          // System design
    TESTER = "tester",               // Test creation
    DOCUMENTER = "documenter",        // Documentation
    CUSTOM = "custom"                 // User-defined
}
```

### Crew Modes (Orchestration Patterns)

```typescript
enum CrewMode {
    SEQUENTIAL = "sequential",        // Agent A → B → C
    HIERARCHICAL = "hierarchical",    // Coordinator delegates to specialists
    PARALLEL = "parallel",            // Agents work simultaneously
    CONSENSUS = "consensus"           // Agents vote/debate
}
```

### Model Tiers (Cost Optimization)

```typescript
enum ModelTier {
    CHEAP = "cheap",                  // Haiku/GPT-4o-mini ($0.001/call)
    CAPABLE = "capable",              // Sonnet/GPT-4o ($0.05/call)
    PREMIUM = "premium"               // Opus/o1 ($0.15/call)
}
```

---

## Provider-Specific Features

### Anthropic-Specific Enhancements

Based on research of Anthropic's Messages API, these features can enhance agents when available:

#### 1. Extended Thinking (Reasoning Mode)

**What It Is**: Claude spends additional tokens on internal reasoning before responding.

**Use Cases**:
- Architectural decisions (complex trade-offs)
- Security analysis (multi-step threat modeling)
- Refactoring plans (analyzing dependencies)
- Test design (edge case discovery)

**Implementation**:
```typescript
interface AnthropicExtendedThinking {
    enabled: boolean;
    budget_tokens: number;  // 1024-10000
}

// Agent Factory UI
const architectAgent = {
    role: AgentRole.ARCHITECT,
    tier: ModelTier.PREMIUM,
    anthropicFeatures: {
        extendedThinking: {
            enabled: true,
            budget_tokens: 4096  // Deep reasoning
        }
    }
};
```

**Graceful Fallback**: When using OpenAI/Ollama, skip reasoning mode and use standard completion.

#### 2. Prompt Caching (Cost Optimization)

**What It Is**: Cache static context (system prompts, knowledge bases, code) for 5min-1hour.

**Cost Savings**:
- Cache reads: 90% cheaper than fresh input
- Cache creation: 25% more expensive (one-time)
- **Net savings**: 80%+ for multi-turn agent conversations

**Use Cases**:
- Agents sharing codebase context
- Repeated system prompts across crew
- Knowledge base injection

**Implementation**:
```typescript
interface PromptCacheConfig {
    enabled: boolean;
    ttl: '5m' | '1h';
    cacheSystemPrompt: boolean;
    cacheContextFiles: string[];  // Files to cache
}

// Shared context across crew
const sharedContext = {
    systemPrompt: "You are a code reviewer...",
    codebase: readFiles(['src/**/*.py']),
    cacheControl: {
        type: "ephemeral",
        ttl: "1h"
    }
};
```

**Graceful Fallback**: Skip caching with other providers, accept higher token costs.

#### 3. Multi-Modal Capabilities

**Vision/Document Analysis**:
```typescript
interface MultiModalContent {
    text?: string;
    image?: {
        type: 'base64';
        media_type: 'image/jpeg' | 'image/png';
        data: string;
    };
    document?: {
        type: 'base64';
        media_type: 'application/pdf';
        data: string;
        title: string;
    };
}
```

**Use Cases**:
- Screenshot analysis for UI review
- PDF document analysis
- Diagram/architecture review

**Graceful Fallback**: Extract text from images/PDFs using OCR, pass as text.

#### 4. Parallel Tool Use

**What It Is**: Execute multiple tools simultaneously without sequential wait.

**Example**:
```json
{
  "tool_calls": [
    {"id": "1", "name": "check_tests", "args": {"file": "a.py"}},
    {"id": "2", "name": "check_tests", "args": {"file": "b.py"}},
    {"id": "3", "name": "check_lint", "args": {"file": "a.py"}}
  ]
}
```

**Graceful Fallback**: Execute tools sequentially for OpenAI (which also supports parallel, but different format).

#### 5. Web Search Tool (Server-Side)

**What It Is**: Claude executes web searches without client-side implementation.

**Configuration**:
```typescript
interface WebSearchTool {
    type: 'web_search_20250305';
    max_uses: number;
    allowed_domains?: string[];
    user_location?: {
        country: string;
        region?: string;
        city?: string;
    };
}
```

**Graceful Fallback**: Use external search API (Brave, Bing) for other providers.

---

### OpenAI-Specific Enhancements

Based on codebase analysis and general knowledge:

#### 1. Structured Outputs (JSON Mode)

**What It Is**: Guaranteed JSON responses matching a schema.

**Use Cases**:
- Structured findings (test results, security reports)
- Configuration generation
- Data extraction

**Implementation**:
```typescript
interface OpenAIStructuredOutput {
    response_format: {
        type: 'json_schema';
        json_schema: {
            name: string;
            schema: JSONSchema;
            strict: boolean;
        };
    };
}
```

**Graceful Fallback**: For Anthropic, use XML output parsing or JSON extraction from text.

#### 2. o1 Reasoning Models

**What It Is**: Models (o1, o1-mini) with extended reasoning capabilities.

**Differences from GPT-4**:
- No system messages (reasoning is inherent)
- No streaming
- Higher cost but better accuracy

**Use Cases**:
- Mathematical proofs
- Complex algorithm design
- Multi-step planning

**Graceful Fallback**: Use Anthropic Extended Thinking or standard GPT-4/Claude.

#### 3. Batch API (50% Cost Savings)

**What It Is**: Submit multiple requests as a batch, get results in 24 hours.

**Use Cases**:
- Bulk code analysis
- Test suite generation
- Documentation batch updates

**Implementation**:
```typescript
interface BatchConfig {
    enabled: boolean;
    maxWaitTime: '24h';
    batchSize: number;  // 50,000 max
}
```

**Graceful Fallback**: Process sequentially with rate limiting.

---

## Agent Factory UI Flow

### Step 1: Task Understanding (Socratic Form)

**Prompt**: "What do you want to accomplish?"

**Follow-up Questions** (adaptive based on answer):

```typescript
interface SocraticQuestion {
    id: string;
    question: string;
    options: Array<{
        label: string;
        value: string;
        description: string;
        leads_to?: string;  // Next question ID
    }>;
    multiSelect?: boolean;
}

const questions: SocraticQuestion[] = [
    {
        id: 'task_type',
        question: 'What type of task is this?',
        options: [
            {
                label: 'Code Review',
                value: 'code_review',
                description: 'Analyze code for issues, patterns, security',
                leads_to: 'code_review_depth'
            },
            {
                label: 'Refactoring',
                value: 'refactor',
                description: 'Improve code structure and quality',
                leads_to: 'refactor_scope'
            },
            {
                label: 'Testing',
                value: 'testing',
                description: 'Generate or review tests',
                leads_to: 'test_type'
            },
            {
                label: 'Documentation',
                value: 'docs',
                description: 'Generate or improve documentation',
                leads_to: 'doc_style'
            },
            {
                label: 'Custom Task',
                value: 'custom',
                description: 'Design a custom agent workflow',
                leads_to: 'custom_design'
            }
        ]
    },
    {
        id: 'code_review_depth',
        question: 'How thorough should the review be?',
        options: [
            {
                label: 'Quick Scan',
                value: 'quick',
                description: '1-2 agents, focused on critical issues (2-3 min)'
            },
            {
                label: 'Standard Review',
                value: 'standard',
                description: '3-4 agents, security + quality + architecture (5-8 min)'
            },
            {
                label: 'Comprehensive Audit',
                value: 'comprehensive',
                description: '5+ agents, all aspects including performance (10-15 min)'
            }
        ]
    },
    // ... more questions
];
```

### Step 2: Crew Recommendation

Based on answers, recommend a crew configuration:

```typescript
interface CrewRecommendation {
    name: string;
    description: string;
    mode: CrewMode;
    agents: AgentConfig[];
    estimatedCost: number;
    estimatedDuration: string;
    reasoning: string;  // Why this crew?
}

// Example output
const recommendation: CrewRecommendation = {
    name: "Code Review Crew (Standard)",
    description: "Comprehensive code review with 4 specialized agents",
    mode: CrewMode.HIERARCHICAL,
    agents: [
        {
            name: "Review Lead",
            role: AgentRole.COORDINATOR,
            tier: ModelTier.PREMIUM,
            capabilities: ['synthesis', 'decision_making'],
            systemPrompt: generateXMLPrompt('review_lead')
        },
        {
            name: "Security Analyst",
            role: AgentRole.SECURITY,
            tier: ModelTier.CAPABLE,
            capabilities: ['vulnerability_detection', 'owasp_analysis'],
            tools: ['dependency_check', 'secrets_scanner'],
            systemPrompt: generateXMLPrompt('security')
        },
        {
            name: "Architecture Reviewer",
            role: AgentRole.ARCHITECT,
            tier: ModelTier.PREMIUM,
            capabilities: ['design_patterns', 'solid_principles'],
            anthropicFeatures: {
                extendedThinking: {
                    enabled: true,
                    budget_tokens: 2048
                }
            },
            systemPrompt: generateXMLPrompt('architect')
        },
        {
            name: "Quality Analyst",
            role: AgentRole.REVIEWER,
            tier: ModelTier.CAPABLE,
            capabilities: ['code_smells', 'best_practices'],
            systemPrompt: generateXMLPrompt('quality')
        }
    ],
    estimatedCost: 0.25,  // $0.25
    estimatedDuration: "5-8 minutes",
    reasoning: "Standard review requires security analysis (capable), architectural decisions (premium with thinking), quality checks (capable), and coordination (premium). Total: 2 premium + 2 capable agents."
};
```

### Step 3: Customization (Optional)

Allow users to modify the recommendation:

```typescript
interface CrewCustomization {
    // Modify individual agents
    modifyAgent(agentName: string, changes: Partial<AgentConfig>): void;

    // Add/remove agents
    addAgent(config: AgentConfig): void;
    removeAgent(agentName: string): void;

    // Change orchestration
    setMode(mode: CrewMode): void;

    // Enable/disable features
    toggleFeature(feature: string, enabled: boolean): void;
}
```

**UI Elements**:
- Agent cards with tier badges
- Drag-and-drop to reorder agents
- Toggle switches for features (caching, thinking, multi-modal)
- Cost meter updating in real-time

### Step 4: Execution with Progress

```typescript
interface CrewExecution {
    status: 'initializing' | 'running' | 'completed' | 'failed';
    currentAgent: string;
    progress: {
        completed: number;
        total: number;
        currentStep: string;
    };
    costs: {
        inputTokens: number;
        outputTokens: number;
        cacheReads: number;
        totalCostUSD: number;
    };
    results: AgentResult[];
}

// Real-time updates via webview messaging
webview.postMessage({
    type: 'crew:progress',
    data: {
        currentAgent: 'Security Analyst',
        step: 'Analyzing dependencies...',
        progress: 25
    }
});
```

### Step 5: Results Display

Interactive report with:
- **Executive Summary** (from coordinator)
- **Findings by Agent** (expandable sections)
- **Actions** (Fix buttons, navigate to code)
- **Cost Breakdown** (per-agent costs)
- **Save Configuration** (reuse this crew)

---

## Graceful Degradation Strategy

### Feature Detection

```typescript
interface ProviderCapabilities {
    provider: 'anthropic' | 'openai' | 'google' | 'ollama';
    features: {
        streaming: boolean;
        toolUse: boolean;
        parallelTools: boolean;
        extendedThinking: boolean;
        promptCaching: boolean;
        multiModal: boolean;
        structuredOutputs: boolean;
        webSearch: boolean;
        batchAPI: boolean;
    };
}

async function detectCapabilities(provider: string): Promise<ProviderCapabilities> {
    const apiKey = getApiKey(provider);
    if (!apiKey) {
        return getDefaultCapabilities(provider);
    }

    // Test API with minimal request
    try {
        const response = await testProviderFeatures(provider, apiKey);
        return parseCapabilities(response);
    } catch (error) {
        return getDefaultCapabilities(provider);
    }
}
```

### Feature Fallback Matrix

| Feature | Anthropic | OpenAI | Ollama | Fallback |
|---------|-----------|--------|--------|----------|
| **Streaming** | ✅ | ✅ | ✅ | Full response |
| **Tool Use** | ✅ | ✅ | ❌ | Client-side execution |
| **Parallel Tools** | ✅ | ✅ | ❌ | Sequential execution |
| **Extended Thinking** | ✅ | ❌ (o1 only) | ❌ | Standard completion |
| **Prompt Caching** | ✅ | ❌ | ❌ | No caching |
| **Multi-Modal** | ✅ | ✅ | ❌ | OCR preprocessing |
| **Structured JSON** | ❌ | ✅ | ❌ | XML parsing |
| **Web Search** | ✅ | ❌ | ❌ | External API |
| **Batch API** | ❌ | ✅ | ❌ | Sequential |

### Implementation Pattern

```typescript
class AgentFactory {
    private capabilities: ProviderCapabilities;

    async createAgent(config: AgentConfig): Promise<BaseAgent> {
        // Apply provider-specific optimizations
        const optimizedConfig = this.applyOptimizations(config);

        // Create agent with fallbacks
        return new BaseAgent(optimizedConfig, this.capabilities);
    }

    private applyOptimizations(config: AgentConfig): AgentConfig {
        const optimized = { ...config };

        // Extended thinking
        if (config.anthropicFeatures?.extendedThinking?.enabled) {
            if (this.capabilities.features.extendedThinking) {
                // Use Claude extended thinking
                optimized.thinkingMode = 'extended';
            } else if (this.isOpenAI() && config.tier === ModelTier.PREMIUM) {
                // Use o1 model instead
                optimized.model_override = 'o1';
            } else {
                // Standard completion
                optimized.thinkingMode = 'standard';
                this.warnUser('Extended thinking not available, using standard mode');
            }
        }

        // Prompt caching
        if (config.caching?.enabled) {
            if (!this.capabilities.features.promptCaching) {
                optimized.caching = { enabled: false };
                this.warnUser('Prompt caching not available for this provider');
            }
        }

        // Multi-modal
        if (config.multiModal?.enabled) {
            if (!this.capabilities.features.multiModal) {
                optimized.preprocessImages = true;  // Use OCR
                this.warnUser('Multi-modal not natively supported, using OCR preprocessing');
            }
        }

        return optimized;
    }
}
```

---

## Cost Optimization Features

### 1. Tier-Based Routing

```typescript
interface TierRouter {
    // Route tasks to appropriate tier
    route(task: Task): ModelTier;
}

const router: TierRouter = {
    route(task: Task): ModelTier {
        // Simple tasks → cheap
        if (task.type === 'summarization' || task.tokenCount < 500) {
            return ModelTier.CHEAP;
        }

        // Complex reasoning → premium
        if (task.requiresReasoning || task.type === 'architecture') {
            return ModelTier.PREMIUM;
        }

        // Default → capable
        return ModelTier.CAPABLE;
    }
};
```

### 2. Real-Time Cost Tracking

```typescript
interface CostTracker {
    inputTokens: number;
    outputTokens: number;
    cacheCreationTokens: number;
    cacheReadTokens: number;

    calculateCost(): number;
    getBreakdown(): CostBreakdown;
}

// Display in UI
const costDisplay = {
    current: '$0.23',
    estimate: '$0.50',
    breakdown: {
        'Review Lead (Premium)': '$0.12',
        'Security (Capable)': '$0.04',
        'Architect (Premium + Thinking)': '$0.15',
        'Quality (Capable)': '$0.04',
        'Cache savings': '-$0.12'
    }
};
```

### 3. Budget Limits

```typescript
interface BudgetControl {
    maxCostPerCrew: number;
    warningThreshold: number;

    checkBudget(estimatedCost: number): {
        allowed: boolean;
        message?: string;
    };
}

// Example
if (estimatedCost > budget.maxCostPerCrew) {
    showWarning(`This crew will cost $${estimatedCost}, which exceeds your budget of $${budget.maxCostPerCrew}. Consider using fewer premium-tier agents or enabling prompt caching.`);
}
```

---

## Pattern Learning

### Learning from Successful Crews

```typescript
interface CrewPattern {
    taskType: string;
    crewConfig: CrewRecommendation;
    success: boolean;
    userFeedback?: number;  // 1-5 rating
    executionTime: number;
    cost: number;
}

class PatternLearner {
    async recordCrewExecution(pattern: CrewPattern): Promise<void> {
        // Store in workspace state
        const patterns = await this.loadPatterns();
        patterns.push(pattern);
        await this.savePatterns(patterns);

        // Update recommendations
        this.updateRecommendations(pattern);
    }

    async suggestCrew(taskDescription: string): Promise<CrewRecommendation> {
        // Find similar past crews
        const similar = await this.findSimilarPatterns(taskDescription);

        // Return most successful configuration
        return similar
            .filter(p => p.success && p.userFeedback >= 4)
            .sort((a, b) => b.userFeedback - a.userFeedback)[0]
            ?.crewConfig;
    }
}
```

---

## Implementation Checklist

### Phase 1: Core Infrastructure (Backend)
- [ ] Extend `AgentFactory` with provider capability detection
- [ ] Add `ExtendedThinkingConfig` to agent config schema
- [ ] Implement `PromptCacheConfig` for Anthropic
- [ ] Add graceful fallback wrappers for all features
- [ ] Create `CrewRecommendationEngine` class

### Phase 2: Socratic UI (Frontend)
- [ ] Create `AgentFactoryPanelProvider.ts`
- [ ] Build Socratic question flow with adaptive branching
- [ ] Design agent configuration cards (drag-drop)
- [ ] Implement real-time cost calculator
- [ ] Add progress tracking with agent status

### Phase 3: Integration
- [ ] Add "Agent Factory" button to Guided Panel
- [ ] Wire factory to workflow execution system
- [ ] Integrate with Pattern Learner service
- [ ] Add crew configuration export/import

### Phase 4: Testing & Documentation
- [ ] Test with all providers (Anthropic, OpenAI, Ollama)
- [ ] Verify graceful degradation for missing features
- [ ] Document crew configuration examples
- [ ] Create video tutorial

---

## Success Metrics

- ✅ Users can design custom crews in <5 minutes
- ✅ Cost estimates accurate within ±15%
- ✅ Features gracefully degrade across all providers
- ✅ 80%+ of users save crew configurations for reuse
- ✅ Pattern learning improves recommendations over time

---

## Next Steps

1. **Add Agent Factory button** to [GuidedPanelProvider.ts](vscode-extension/src/panels/GuidedPanelProvider.ts)
2. **Create AgentFactoryPanelProvider.ts** with Socratic form flow
3. **Extend backend** with capability detection and fallbacks
4. **Test with real workflows** (code review, refactoring, testing)

**Ready to implement!** 🚀
