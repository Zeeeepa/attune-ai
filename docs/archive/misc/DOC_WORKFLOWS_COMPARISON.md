---
description: Documentation Workflows Comparison: ## Current Situation: 3 Doc Workflows ### 1.
---

# Documentation Workflows Comparison

## Current Situation: 3 Doc Workflows

### 1. Generate Docs (doc-gen)
**Button**: "Generate Docs"
**Type**: Simple 3-stage pipeline
**Purpose**: Cost-optimized doc generation for specific code
**Stages**:
- outline (cheap - Gemini)
- write (capable - Sonnet)
- polish (premium - Opus)

**Use Case**: "I need docs for this specific file/function"

---

### 2. Manage Docs (doc-orchestrator)
**Button**: "Manage Docs"
**Type**: End-to-end orchestration workflow
**Purpose**: Full documentation management system
**Phases**:
1. SCOUT - Find documentation gaps
2. PRIORITIZE - Rank by severity/impact
3. GENERATE - Create/update docs for priority items
4. UPDATE - Update ProjectIndex

**Use Case**: "Audit my entire codebase for missing/stale docs and fix the worst ones"

---

### 3. Sync Docs (manage-docs)
**Button**: "Sync Docs"
**Type**: ManageDocumentationCrew (CrewAI)
**Purpose**: Ensure program files are documented and docs stay updated when code changes
**Agents**:
- Analyst: Scans for documentation gaps
- Reviewer: Validates accuracy

**Use Case**: "Make sure my docs are in sync with recent code changes"

---

## The Problem: Overlap & Confusion

**doc-orchestrator** and **manage-docs** do very similar things:
- Both find documentation gaps ✓
- Both identify stale docs ✓
- Both can generate/update docs ✓

**Differences**:
- doc-orchestrator: More comprehensive, prioritization, cost management
- manage-docs: Focused on keeping existing docs synchronized

---

## Recommendations

### Option 1: Remove manage-docs ✅ RECOMMENDED
Keep only:
- **doc-gen**: Quick doc generation for specific code
- **doc-orchestrator**: Full doc management (includes gap detection + sync)

**Pros**:
- Clearer UX (2 buttons instead of 3)
- Less duplication
- doc-orchestrator already does everything manage-docs does

**Cons**:
- Lose the ManageDocumentationCrew implementation

---

### Option 2: Rename for Clarity
- **Generate Docs** (doc-gen) → Keep as-is
- **Manage Docs** (doc-orchestrator) → Rename to "Doc Audit & Fix"
- **Sync Docs** (manage-docs) → Rename to "Keep Docs Current"

**Pros**: Clearer differentiation
**Cons**: Still 3 workflows with overlap

---

### Option 3: Consolidate into 2 Workflows
- **Generate Docs**: Simple generation (doc-gen)
- **Manage Docs**: Full management (merge doc-orchestrator + manage-docs)

**Pros**: Best of both implementations
**Cons**: More work to merge

---

## Decision Needed

**Question for User**: Which option do you prefer?

1. **Remove "Sync Docs" button** (manage-docs workflow)
2. **Rename all three** for better clarity
3. **Merge** doc-orchestrator + manage-docs

My recommendation: **Option 1** - Remove manage-docs, keep doc-gen and doc-orchestrator.
